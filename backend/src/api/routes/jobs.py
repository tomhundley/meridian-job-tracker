"""Job CRUD endpoints."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, case, nulls_last
from sqlalchemy.orm import selectinload

from src.api.deps import DbSession, require_permissions
from src.models import Job, CoverLetter, JobContact, JobStatus as ModelJobStatus, RoleType as ModelRoleType, WorkLocationType as ModelWorkLocationType, EmploymentType as ModelEmploymentType
from src.schemas import (
    JobCreate,
    JobIngestRequest,
    JobBulkIngestRequest,
    JobBulkIngestResponse,
    JobBulkStatusUpdate,
    JobBulkStatusResponse,
    JobListResponse,
    JobResponse,
    JobStatusUpdate,
    JobUpdate,
    JobStatus,
    RoleType,
    WorkLocationType,
    CoverLetterCreate,
    CoverLetterResponse,
)
from src.services import job_scraper, JobScrapeError

router = APIRouter()


@router.get(
    "",
    response_model=JobListResponse,
    summary="List jobs",
    description="List all jobs with optional filters and pagination.",
    dependencies=[Depends(require_permissions(["jobs:read"]))],
)
async def list_jobs(
    db: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    status: JobStatus | None = None,
    company: str | None = None,
    target_role: RoleType | None = None,
    work_location_type: WorkLocationType | None = None,
    min_priority: Annotated[int | None, Query(ge=0, le=100)] = None,
    min_salary: Annotated[int | None, Query(ge=0, description="Minimum salary filter")] = None,
    max_salary: Annotated[int | None, Query(ge=0, description="Maximum salary filter")] = None,
    search: str | None = None,
    sort_by: Annotated[str | None, Query(description="Sort field: updated_at, created_at, priority, salary")] = "updated_at",
    sort_order: Annotated[str | None, Query(description="Sort order: asc or desc")] = "desc",
) -> JobListResponse:
    """List all jobs with optional filters and pagination."""
    # Base query - exclude deleted
    query = select(Job).where(Job.deleted_at.is_(None))

    # Apply filters
    if status:
        query = query.where(Job.status == ModelJobStatus(status.value))
    if company:
        query = query.where(Job.company.ilike(f"%{company}%"))
    if target_role:
        query = query.where(Job.target_role == ModelRoleType(target_role.value))
    if work_location_type:
        query = query.where(Job.work_location_type == ModelWorkLocationType(work_location_type.value))
    if min_priority is not None:
        query = query.where(Job.priority >= min_priority)
    if min_salary is not None:
        # Filter jobs where max salary is at least min_salary (or min salary if max is null)
        query = query.where(
            (Job.salary_max >= min_salary) | ((Job.salary_max.is_(None)) & (Job.salary_min >= min_salary))
        )
    if max_salary is not None:
        # Filter jobs where min salary is at most max_salary (or max salary if min is null)
        query = query.where(
            (Job.salary_min <= max_salary) | ((Job.salary_min.is_(None)) & (Job.salary_max <= max_salary))
        )
    if search:
        # Simple search on title, company, description
        search_filter = (
            Job.title.ilike(f"%{search}%")
            | Job.company.ilike(f"%{search}%")
            | Job.description_raw.ilike(f"%{search}%")
        )
        query = query.where(search_filter)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    # Determine sort column
    # For salary, use COALESCE to pick best available value, with nulls always last
    salary_sort_col = func.coalesce(Job.salary_max, Job.salary_min)

    sort_column_map = {
        "updated_at": Job.updated_at,
        "created_at": Job.created_at,
        "priority": Job.priority,
        "salary": salary_sort_col,
        "title": Job.title,
        "company": Job.company,
    }
    sort_column = sort_column_map.get(sort_by or "updated_at", Job.updated_at)

    # Apply sort order, with nulls last for salary
    if sort_order == "asc":
        if sort_by == "salary":
            order_clause = nulls_last(sort_column.asc())
        else:
            order_clause = sort_column.asc()
    else:
        if sort_by == "salary":
            order_clause = nulls_last(sort_column.desc())
        else:
            order_clause = sort_column.desc()

    # Apply pagination and ordering
    query = (
        query.order_by(order_clause, Job.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(query)
    jobs = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return JobListResponse(
        items=[JobResponse.model_validate(job) for job in jobs],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post(
    "/ingest",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest job from URL",
    description=(
        "Automatically scrape and parse job details from supported job board URLs.\n\n"
        "**Supported Sources:**\n"
        "- LinkedIn: `linkedin.com/jobs/view/*`\n"
        "- Indeed: `indeed.com/viewjob*`\n"
        "- Greenhouse: `boards.greenhouse.io/*`\n"
        "- Lever: `jobs.lever.co/*`\n"
        "- Workday: `*.myworkdayjobs.com/*`\n"
    ),
    responses={
        201: {"description": "Job created successfully"},
        400: {"description": "Unsupported URL or parsing failed"},
        409: {"description": "Job already exists (duplicate URL)"},
    },
    dependencies=[Depends(require_permissions(["jobs:ingest"]))],
)
async def ingest_job(
    db: DbSession,
    request: JobIngestRequest,
) -> Job:
    """Ingest a job from a URL."""
    url = str(request.url)
    try:
        scraped = await job_scraper.scrape(url, request.source)
    except JobScrapeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    if scraped.source_id:
        query = select(Job).where(
            Job.job_board == scraped.source,
            Job.job_board_id == scraped.source_id,
            Job.deleted_at.is_(None),
        )
    else:
        query = select(Job).where(
            Job.url == url,
            Job.deleted_at.is_(None),
        )
    existing = (await db.execute(query)).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Job already exists",
        )

    job = Job(
        title=scraped.title,
        company=scraped.company,
        location=scraped.location,
        url=url,
        job_board=request.source or scraped.source,
        job_board_id=scraped.source_id,
        description_raw=scraped.description,
        source_html=scraped.raw_html,
        notes=request.notes,
    )
    db.add(job)
    await db.flush()
    await db.refresh(job)
    return job


@router.post(
    "/bulk",
    response_model=JobBulkIngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Bulk ingest jobs from URLs",
    description="Create multiple jobs by scraping their URLs.",
    dependencies=[Depends(require_permissions(["jobs:ingest"]))],
)
async def bulk_ingest_jobs(
    db: DbSession,
    request: JobBulkIngestRequest,
) -> JobBulkIngestResponse:
    """Bulk ingest jobs from a list of URLs."""
    created: list[Job] = []
    failed: list[dict[str, str]] = []

    for job_request in request.jobs:
        url = str(job_request.url)
        try:
            scraped = await job_scraper.scrape(url, job_request.source)
        except JobScrapeError as exc:
            failed.append({"url": url, "error": str(exc)})
            continue

        if scraped.source_id:
            query = select(Job).where(
                Job.job_board == scraped.source,
                Job.job_board_id == scraped.source_id,
                Job.deleted_at.is_(None),
            )
        else:
            query = select(Job).where(
                Job.url == url,
                Job.deleted_at.is_(None),
            )
        existing = (await db.execute(query)).scalar_one_or_none()
        if existing:
            failed.append({"url": url, "error": "Job already exists"})
            continue

        job = Job(
            title=scraped.title,
            company=scraped.company,
            location=scraped.location,
            url=url,
            job_board=job_request.source or scraped.source,
            job_board_id=scraped.source_id,
            description_raw=scraped.description,
            source_html=scraped.raw_html,
            notes=job_request.notes,
        )
        db.add(job)
        await db.flush()
        created.append(job)

    return JobBulkIngestResponse(
        created=[JobResponse.model_validate(job) for job in created],
        failed=failed,
    )


@router.patch(
    "/bulk/status",
    response_model=JobBulkStatusResponse,
    summary="Bulk update job status",
    description="Update status for multiple jobs in a single request.",
    dependencies=[Depends(require_permissions(["jobs:update_status"]))],
)
async def bulk_update_job_status(
    db: DbSession,
    status_update: JobBulkStatusUpdate,
) -> JobBulkStatusResponse:
    """Update status for multiple jobs."""
    query = select(Job).where(
        Job.id.in_(status_update.job_ids),
        Job.deleted_at.is_(None),
    )
    result = await db.execute(query)
    jobs = list(result.scalars().all())
    found_ids = {job.id for job in jobs}
    missing = [job_id for job_id in status_update.job_ids if job_id not in found_ids]

    now = datetime.utcnow()
    for job in jobs:
        job.status = ModelJobStatus(status_update.status.value)
        job.status_changed_at = now
        if status_update.closed_reason:
            job.closed_reason = status_update.closed_reason
        if status_update.status == JobStatus.APPLIED and job.applied_at is None:
            job.applied_at = now

    await db.flush()

    return JobBulkStatusResponse(
        updated=[JobResponse.model_validate(job) for job in jobs],
        missing=missing,
    )


@router.post(
    "",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create job",
    description="Create a new job record.",
    dependencies=[Depends(require_permissions(["jobs:write"]))],
)
async def create_job(
    db: DbSession,
    job_in: JobCreate,
) -> Job:
    """Create a new job."""
    job = Job(
        title=job_in.title,
        company=job_in.company,
        location=job_in.location,
        work_location_type=ModelWorkLocationType(job_in.work_location_type.value) if job_in.work_location_type else None,
        url=job_in.url,
        description_raw=job_in.description_raw,
        salary_min=job_in.salary_min,
        salary_max=job_in.salary_max,
        salary_currency=job_in.salary_currency,
        employment_type=ModelEmploymentType(job_in.employment_type.value) if job_in.employment_type else None,
        target_role=ModelRoleType(job_in.target_role.value) if job_in.target_role else None,
        priority=job_in.priority,
        notes=job_in.notes,
        tags=job_in.tags,
        job_board=job_in.job_board,
        job_board_id=job_in.job_board_id,
    )
    db.add(job)
    await db.flush()
    await db.refresh(job)
    return job


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    summary="Get job",
    description="Retrieve a job by ID.",
    dependencies=[Depends(require_permissions(["jobs:read"]))],
)
async def get_job(
    db: DbSession,
    job_id: UUID,
) -> Job:
    """Get a job by ID."""
    query = (
        select(Job)
        .where(Job.id == job_id, Job.deleted_at.is_(None))
        .options(
            selectinload(Job.cover_letters),
            selectinload(Job.emails),
        )
    )
    result = await db.execute(query)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found",
        )

    return job


@router.patch(
    "/{job_id}",
    response_model=JobResponse,
    summary="Update job",
    description="Update job details.",
    dependencies=[Depends(require_permissions(["jobs:write"]))],
)
async def update_job(
    db: DbSession,
    job_id: UUID,
    job_in: JobUpdate,
) -> Job:
    """Update a job."""
    query = select(Job).where(Job.id == job_id, Job.deleted_at.is_(None))
    result = await db.execute(query)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found",
        )

    # Update fields
    update_data = job_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            if field == "target_role":
                value = ModelRoleType(value.value)
            elif field == "employment_type":
                value = ModelEmploymentType(value.value)
            elif field == "work_location_type":
                value = ModelWorkLocationType(value.value)
        setattr(job, field, value)

    await db.flush()
    await db.refresh(job)
    return job


@router.patch(
    "/{job_id}/status",
    response_model=JobResponse,
    summary="Update job status",
    description="Update the status for a job.",
    dependencies=[Depends(require_permissions(["jobs:update_status"]))],
)
async def update_job_status(
    db: DbSession,
    job_id: UUID,
    status_update: JobStatusUpdate,
) -> Job:
    """Update a job's status."""
    query = select(Job).where(Job.id == job_id, Job.deleted_at.is_(None))
    result = await db.execute(query)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found",
        )

    job.status = ModelJobStatus(status_update.status.value)
    job.status_changed_at = datetime.utcnow()
    if status_update.closed_reason:
        job.closed_reason = status_update.closed_reason

    # Set applied_at if transitioning to applied
    if status_update.status == JobStatus.APPLIED and job.applied_at is None:
        job.applied_at = datetime.utcnow()

    # Handle decline reasons
    if status_update.user_decline_reasons is not None:
        job.user_decline_reasons = status_update.user_decline_reasons
    if status_update.company_decline_reasons is not None:
        job.company_decline_reasons = status_update.company_decline_reasons
    if status_update.decline_notes is not None:
        job.decline_notes = status_update.decline_notes

    await db.flush()
    await db.refresh(job)
    return job


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete job",
    description="Soft delete a job.",
    dependencies=[Depends(require_permissions(["jobs:delete"]))],
)
async def delete_job(
    db: DbSession,
    job_id: UUID,
) -> None:
    """Soft delete a job."""
    query = select(Job).where(Job.id == job_id, Job.deleted_at.is_(None))
    result = await db.execute(query)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found",
        )

    job.deleted_at = datetime.utcnow()
    await db.flush()


# Cover letter generation endpoint
@router.post(
    "/{job_id}/cover-letter",
    response_model=CoverLetterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate cover letter",
    description="Generate a new cover letter for a job.",
    dependencies=[Depends(require_permissions(["cover_letters:write"]))],
)
async def generate_cover_letter(
    db: DbSession,
    job_id: UUID,
    request: CoverLetterCreate,
) -> CoverLetter:
    """Generate a cover letter for a job."""
    from src.models import CoverLetter as CoverLetterModel
    from src.services import cover_letter_service

    # Get the job
    query = select(Job).where(Job.id == job_id, Job.deleted_at.is_(None))
    result = await db.execute(query)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found",
        )

    # Generate cover letter
    try:
        generation_result = await cover_letter_service.generate(
            job=job,
            target_role=ModelRoleType(request.target_role.value),
            custom_instructions=request.custom_instructions,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Get current version number
    from sqlalchemy import func as sqlfunc
    version_query = select(sqlfunc.coalesce(sqlfunc.max(CoverLetterModel.version), 0)).where(
        CoverLetterModel.job_id == job_id,
        CoverLetterModel.deleted_at.is_(None),
    )
    current_version = await db.scalar(version_query) or 0

    # Mark existing cover letters as not current
    from sqlalchemy import update
    await db.execute(
        update(CoverLetterModel)
        .where(CoverLetterModel.job_id == job_id, CoverLetterModel.is_current == True)
        .values(is_current=False)
    )

    # Create new cover letter
    cover_letter = CoverLetterModel(
        job_id=job_id,
        content=generation_result["content"],
        target_role=generation_result["target_role"],
        generation_prompt=generation_result["generation_prompt"],
        model_used=generation_result["model_used"],
        version=current_version + 1,
        is_current=True,
    )
    db.add(cover_letter)
    await db.flush()
    await db.refresh(cover_letter)

    return cover_letter


@router.get(
    "/{job_id}/cover-letters",
    response_model=list[CoverLetterResponse],
    summary="List cover letters for job",
    description="List all cover letters for a job.",
    dependencies=[Depends(require_permissions(["cover_letters:read"]))],
)
async def list_job_cover_letters(
    db: DbSession,
    job_id: UUID,
) -> list:
    """List all cover letters for a job."""
    from src.models import CoverLetter as CoverLetterModel

    query = (
        select(CoverLetterModel)
        .where(CoverLetterModel.job_id == job_id, CoverLetterModel.deleted_at.is_(None))
        .order_by(CoverLetterModel.version.desc())
    )
    result = await db.execute(query)
    return list(result.scalars().all())
