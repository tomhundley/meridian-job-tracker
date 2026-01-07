"""Job CRUD endpoints."""

from datetime import datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import cast, func, select, case, nulls_last, String
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
    JobAnalysisResponse,
    RoleType,
    WorkLocationType,
    CoverLetterCreate,
    CoverLetterResponse,
)
from src.schemas.job_note import JobNoteCreate, JobNoteEntry, NoteSource, NoteType
from src.services import (
    job_scraper,
    JobScrapeError,
    analyze_job,
    analyze_job_with_ai,
    sparkles_client,
    generate_typed_notes,
    description_fetcher,
)

router = APIRouter()


def build_job_response(job: Job, contacts: list | None = None) -> JobResponse:
    """Build JobResponse without triggering lazy loads.

    For newly created jobs, pass contacts=[] to avoid lazy loading.
    For jobs with pre-loaded contacts, pass contacts=job.contacts.
    """
    contact_list = contacts if contacts is not None else []
    return JobResponse(
        id=job.id,
        created_at=job.created_at,
        updated_at=job.updated_at,
        title=job.title,
        company=job.company,
        location=job.location,
        work_location_type=job.work_location_type,
        url=job.url,
        description_raw=job.description_raw,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        salary_currency=job.salary_currency,
        employment_type=job.employment_type,
        posted_at=job.posted_at,
        target_role=job.target_role,
        priority=job.priority,
        notes=job.notes,
        tags=job.tags,
        is_easy_apply=job.is_easy_apply,
        is_favorite=job.is_favorite,
        is_perfect_fit=job.is_perfect_fit,
        is_ai_forward=job.is_ai_forward,
        is_location_compatible=job.is_location_compatible,
        status=job.status,
        status_changed_at=job.status_changed_at,
        closed_reason=job.closed_reason,
        job_board=job.job_board,
        job_board_id=job.job_board_id,
        application_method=job.application_method,
        applied_at=job.applied_at,
        user_decline_reasons=job.user_decline_reasons,
        company_decline_reasons=job.company_decline_reasons,
        decline_notes=job.decline_notes,
        contacts=contact_list,
        contact_count=len(contact_list),
    )


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
    status: Annotated[str | None, Query(description="Comma-separated list of statuses to filter by")] = None,
    company: str | None = None,
    target_role: RoleType | None = None,
    work_location_type: WorkLocationType | None = None,
    is_easy_apply: Annotated[bool | None, Query(description="Filter by Easy Apply status")] = None,
    is_favorite: Annotated[bool | None, Query(description="Filter by favorite status")] = None,
    is_perfect_fit: Annotated[bool | None, Query(description="Filter by perfect fit status")] = None,
    is_ai_forward: Annotated[bool | None, Query(description="Filter by AI-forward status")] = None,
    is_location_compatible: Annotated[bool | None, Query(description="Filter by location compatibility")] = None,
    min_priority: Annotated[int | None, Query(ge=0, le=100)] = None,
    min_salary: Annotated[int | None, Query(ge=0, description="Minimum salary filter")] = None,
    max_salary: Annotated[int | None, Query(ge=0, description="Maximum salary filter")] = None,
    search: str | None = None,
    sort_by: Annotated[str | None, Query(description="Sort field: updated_at, created_at, priority, salary")] = "updated_at",
    sort_order: Annotated[str | None, Query(description="Sort order: asc or desc")] = "desc",
    max_age_days: Annotated[int | None, Query(ge=1, description="Maximum posting age in days")] = None,
) -> JobListResponse:
    """List all jobs with optional filters and pagination."""
    # Base query - exclude deleted
    query = select(Job).where(Job.deleted_at.is_(None))

    # Apply filters
    if status:
        # Support comma-separated list of statuses
        status_list = [s.strip() for s in status.split(",") if s.strip()]
        if status_list:
            status_enums = [ModelJobStatus(s) for s in status_list if s in [e.value for e in ModelJobStatus]]
            if status_enums:
                query = query.where(Job.status.in_(status_enums))
    if company:
        query = query.where(Job.company.ilike(f"%{company}%"))
    if target_role:
        query = query.where(Job.target_role == ModelRoleType(target_role.value))
    if work_location_type:
        query = query.where(Job.work_location_type == ModelWorkLocationType(work_location_type.value))
    if is_easy_apply is not None:
        query = query.where(Job.is_easy_apply == is_easy_apply)
    if is_favorite is not None:
        query = query.where(Job.is_favorite == is_favorite)
    if is_perfect_fit is not None:
        query = query.where(Job.is_perfect_fit == is_perfect_fit)
    if is_ai_forward is not None:
        query = query.where(Job.is_ai_forward == is_ai_forward)
    if is_location_compatible is not None:
        query = query.where(Job.is_location_compatible == is_location_compatible)
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
        # Search on title, company, description, and job ID
        search_filter = (
            Job.title.ilike(f"%{search}%")
            | Job.company.ilike(f"%{search}%")
            | Job.description_raw.ilike(f"%{search}%")
            | cast(Job.id, String).ilike(f"%{search}%")
        )
        query = query.where(search_filter)
    if max_age_days is not None:
        # Filter by posting age - include jobs with NULL posted_at (they pass the filter)
        cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
        query = query.where((Job.posted_at.is_(None)) | (Job.posted_at >= cutoff_date))

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
        .options(selectinload(Job.contacts))
    )

    result = await db.execute(query)
    jobs = list(result.scalars().all())

    total_pages = (total + page_size - 1) // page_size

    # Build response with contacts (already loaded via selectinload)
    items = [build_job_response(job, contacts=list(job.contacts)) for job in jobs]

    return JobListResponse(
        items=items,
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
        "Automatically scrape, parse, and analyze job details from supported URLs.\n\n"
        "**Supported Sources:**\n"
        "- LinkedIn: `linkedin.com/jobs/view/*`\n"
        "- Indeed: `indeed.com/viewjob*`\n"
        "- Greenhouse: `boards.greenhouse.io/*`\n"
        "- Lever: `jobs.lever.co/*`\n"
        "- Workday: `*.myworkdayjobs.com/*`\n\n"
        "**Auto-Extracted Data:**\n"
        "- Title, company, location, description\n"
        "- Salary range (if available)\n"
        "- Employment type (full-time, contract, etc.)\n"
        "- Work location type (remote, hybrid, on-site)\n"
        "- Posted date\n"
        "- Easy Apply status (LinkedIn)\n\n"
        "**Auto-Analysis:**\n"
        "- Priority/fit score (0-100)\n"
        "- AI-forward company detection\n"
        "- Target role suggestion (CTO, VP, Director, etc.)\n"
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
) -> JobResponse:
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

    # Parse posted_at date if available
    posted_at = None
    if scraped.posted_at:
        try:
            from datetime import datetime
            posted_at = datetime.fromisoformat(scraped.posted_at.replace("Z", "+00:00"))
        except ValueError:
            pass

    # Map employment type string to enum
    employment_type = None
    if scraped.employment_type:
        try:
            employment_type = ModelEmploymentType(scraped.employment_type)
        except ValueError:
            pass

    # Map work location type string to enum
    work_location_type = None
    if scraped.work_location_type:
        try:
            work_location_type = ModelWorkLocationType(scraped.work_location_type)
        except ValueError:
            pass

    job = Job(
        title=scraped.title,
        company=scraped.company,
        location=scraped.location,
        url=url,
        job_board=request.source or scraped.source,
        job_board_id=scraped.source_id,
        description_raw=scraped.description,
        source_html=scraped.raw_html,
        is_easy_apply=scraped.is_easy_apply,
        salary_min=scraped.salary_min,
        salary_max=scraped.salary_max,
        salary_currency=scraped.salary_currency or "USD",
        employment_type=employment_type,
        work_location_type=work_location_type,
        posted_at=posted_at,
        notes=[{"text": request.notes, "timestamp": datetime.utcnow().isoformat() + "Z", "source": "user"}] if request.notes else None,
    )

    # Run job analysis to set priority, is_ai_forward, and target_role
    if scraped.description:
        try:
            analysis = analyze_job(
                description=scraped.description,
                title=scraped.title,
                company=scraped.company,
            )
            job.priority = analysis.suggested_priority
            job.is_ai_forward = analysis.is_ai_forward
            if analysis.suggested_role:
                job.target_role = analysis.suggested_role
        except Exception:
            pass  # Don't fail ingestion if analysis fails

    db.add(job)
    await db.flush()
    await db.refresh(job)

    # Build response (new jobs have no contacts)
    return build_job_response(job, contacts=[])


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

        # Parse posted_at date if available
        posted_at = None
        if scraped.posted_at:
            try:
                posted_at = datetime.fromisoformat(scraped.posted_at.replace("Z", "+00:00"))
            except ValueError:
                pass

        # Map employment type string to enum
        employment_type = None
        if scraped.employment_type:
            try:
                employment_type = ModelEmploymentType(scraped.employment_type)
            except ValueError:
                pass

        # Map work location type string to enum
        work_location_type = None
        if scraped.work_location_type:
            try:
                work_location_type = ModelWorkLocationType(scraped.work_location_type)
            except ValueError:
                pass

        job = Job(
            title=scraped.title,
            company=scraped.company,
            location=scraped.location,
            url=url,
            job_board=job_request.source or scraped.source,
            job_board_id=scraped.source_id,
            description_raw=scraped.description,
            source_html=scraped.raw_html,
            is_easy_apply=scraped.is_easy_apply,
            salary_min=scraped.salary_min,
            salary_max=scraped.salary_max,
            salary_currency=scraped.salary_currency or "USD",
            employment_type=employment_type,
            work_location_type=work_location_type,
            posted_at=posted_at,
            notes=[{"text": job_request.notes, "timestamp": datetime.utcnow().isoformat() + "Z", "source": "user"}] if job_request.notes else None,
        )

        # Run job analysis to set priority, is_ai_forward, and target_role
        if scraped.description:
            try:
                analysis = analyze_job(
                    description=scraped.description,
                    title=scraped.title,
                    company=scraped.company,
                )
                job.priority = analysis.suggested_priority
                job.is_ai_forward = analysis.is_ai_forward
                if analysis.suggested_role:
                    job.target_role = analysis.suggested_role
            except Exception:
                pass  # Don't fail ingestion if analysis fails

        db.add(job)
        await db.flush()
        created.append(job)

    return JobBulkIngestResponse(
        created=[build_job_response(job, contacts=[]) for job in created],
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
    query = (
        select(Job)
        .where(
            Job.id.in_(status_update.job_ids),
            Job.deleted_at.is_(None),
        )
        .options(selectinload(Job.contacts))
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

    # Build responses with contacts (already loaded via selectinload)
    updated_responses = [build_job_response(job, contacts=list(job.contacts)) for job in jobs]

    return JobBulkStatusResponse(
        updated=updated_responses,
        missing=missing,
    )


@router.get(
    "/descriptions/stats",
    summary="Get description statistics",
    description="Get statistics about job description completeness.",
    dependencies=[Depends(require_permissions(["jobs:read"]))],
)
async def get_description_stats(
    db: DbSession,
) -> dict:
    """Get statistics about job descriptions."""
    return await description_fetcher.get_stats(db)


@router.get(
    "/descriptions/incomplete",
    summary="List jobs with incomplete descriptions",
    description=(
        "Get jobs that need full descriptions fetched via browser automation.\n\n"
        "Jobs with descriptions < 500 chars are considered incomplete.\n"
        "Use browser automation to fetch full descriptions from the returned URLs."
    ),
    dependencies=[Depends(require_permissions(["jobs:read"]))],
)
async def list_incomplete_descriptions(
    db: DbSession,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    min_chars: Annotated[int | None, Query(description="Override minimum character threshold")] = None,
) -> list[dict]:
    """List jobs needing full descriptions."""
    incomplete = await description_fetcher.get_incomplete_jobs(db, limit=limit, min_chars=min_chars)

    return [
        {
            "id": str(job.id),
            "title": job.title,
            "company": job.company,
            "url": description_fetcher.build_fetch_url(job),
            "job_board": job.job_board,
            "job_board_id": job.job_board_id,
            "description_length": job.description_length,
            "needs_fetch": job.needs_fetch,
        }
        for job in incomplete
    ]


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
) -> JobResponse:
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

    # Build response manually to avoid lazy loading contacts on new job
    return JobResponse(
        id=job.id,
        created_at=job.created_at,
        updated_at=job.updated_at,
        title=job.title,
        company=job.company,
        location=job.location,
        work_location_type=job.work_location_type,
        url=job.url,
        description_raw=job.description_raw,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        salary_currency=job.salary_currency,
        employment_type=job.employment_type,
        posted_at=job.posted_at,
        target_role=job.target_role,
        priority=job.priority,
        notes=job.notes,
        tags=job.tags,
        status=job.status,
        status_changed_at=job.status_changed_at,
        closed_reason=job.closed_reason,
        job_board=job.job_board,
        job_board_id=job.job_board_id,
        application_method=job.application_method,
        applied_at=job.applied_at,
        user_decline_reasons=job.user_decline_reasons,
        company_decline_reasons=job.company_decline_reasons,
        decline_notes=job.decline_notes,
        contacts=[],
        contact_count=0,
    )


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
) -> JobResponse:
    """Get a job by ID."""
    query = (
        select(Job)
        .where(Job.id == job_id, Job.deleted_at.is_(None))
        .options(
            selectinload(Job.cover_letters),
            selectinload(Job.emails),
            selectinload(Job.contacts),
        )
    )
    result = await db.execute(query)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found",
        )

    # Build response with contacts (already loaded via selectinload)
    return build_job_response(job, contacts=list(job.contacts))


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
) -> JobResponse:
    """Update a job."""
    query = (
        select(Job)
        .where(Job.id == job_id, Job.deleted_at.is_(None))
        .options(selectinload(Job.contacts))
    )
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
    await db.refresh(job, ["contacts"])

    # Build response with contacts (contacts are eagerly loaded)
    return build_job_response(job, contacts=list(job.contacts))


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
) -> JobResponse:
    """Update a job's status."""
    query = (
        select(Job)
        .where(Job.id == job_id, Job.deleted_at.is_(None))
        .options(selectinload(Job.contacts))
    )
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
    await db.refresh(job, ["contacts"])

    # Build response with contacts (contacts are eagerly loaded)
    return build_job_response(job, contacts=list(job.contacts))


@router.post(
    "/{job_id}/analyze",
    response_model=JobAnalysisResponse,
    summary="Analyze job fit",
    description=(
        "Analyze a job to determine AI-forward status, fit score, and role suggestions.\n\n"
        "**AI Analysis:** When `use_ai=true` (default), uses Claude for semantic analysis.\n"
        "Falls back to rule-based analysis if AI unavailable.\n\n"
        "**RAG Enhancement:** When `use_rag=true` (default), fetches context from Sparkles\n"
        "career documents to provide personalized coaching insights.\n\n"
        "Returns:\n"
        "- **is_ai_forward**: Whether this is an AI-forward company/role\n"
        "- **ai_confidence**: Confidence score (0-1) for AI-forward detection\n"
        "- **suggested_priority**: Fit score (0-100) based on skills match\n"
        "- **suggested_role**: Recommended target role (CTO, VP, Director, etc.)\n"
        "- **technologies_matched/missing**: Tech requirements vs resume skills\n"
    ),
    dependencies=[Depends(require_permissions(["jobs:read"]))],
)
async def analyze_job_fit(
    db: DbSession,
    job_id: UUID,
    apply_suggestions: Annotated[bool, Query(description="Apply suggested priority and is_ai_forward to job")] = False,
    use_ai: Annotated[bool, Query(description="Use AI (Claude) for semantic analysis")] = True,
    use_rag: Annotated[bool, Query(description="Use RAG from Sparkles for coaching insights")] = True,
) -> JobAnalysisResponse:
    """Analyze a job for fit and AI-forward status."""
    query = select(Job).where(Job.id == job_id, Job.deleted_at.is_(None))
    result = await db.execute(query)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found",
        )

    if not job.description_raw:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job has no description to analyze",
        )

    # Run analysis - use AI by default
    analysis, ai_result = analyze_job_with_ai(job, use_ai=use_ai)

    # Optionally apply suggestions to the job
    if apply_suggestions:
        job.priority = analysis.suggested_priority
        job.is_ai_forward = analysis.is_ai_forward
        job.is_location_compatible = analysis.is_location_compatible
        if analysis.suggested_role:
            job.target_role = ModelRoleType(analysis.suggested_role.value)

        # Auto-reject if location is incompatible
        if not analysis.is_location_compatible:
            job.status = ModelJobStatus.ARCHIVED
            # Add 'location' to user_decline_reasons
            existing_reasons = job.user_decline_reasons or []
            if "location" not in existing_reasons:
                job.user_decline_reasons = existing_reasons + ["location"]
            # Add location note to decline_notes
            if analysis.location_notes:
                existing_notes = job.decline_notes or ""
                if existing_notes:
                    job.decline_notes = f"{existing_notes}\n{analysis.location_notes}"
                else:
                    job.decline_notes = analysis.location_notes

        # Generate typed notes from AI analysis
        if ai_result:
            # Try to get RAG context for enhanced coaching
            coaching_insights = None
            requirement_matches = None

            if use_rag and sparkles_client.is_configured:
                try:
                    # Extract requirements from job for RAG matching
                    from src.services.jd_analyzer import detect_and_parse_jd
                    jd_result = detect_and_parse_jd(job.description_raw)
                    requirements = (
                        jd_result.requirements.must_have[:10] +
                        jd_result.requirements.nice_to_have[:5]
                    )

                    if requirements:
                        # Get JD requirement matches from RAG
                        requirement_matches = await sparkles_client.match_jd_requirements(
                            requirements=requirements,
                            threshold=0.40,
                            limit_per_req=3,
                        )

                        # Convert to RAGEvidence for coaching
                        from src.schemas.ai_analysis_coach import CoachingInsights, RAGEvidence
                        evidence_list = []
                        for match in requirement_matches:
                            for top_match in match.top_matches[:1]:  # Top match only
                                evidence_list.append(top_match)

                        coaching_insights = CoachingInsights(
                            talking_points=[],
                            strengths_to_highlight=[],
                            gaps_to_address=[],
                            study_recommendations=[],
                            watch_outs=[],
                            evidence_from_resume=evidence_list,
                        )
                except Exception as e:
                    import structlog
                    logger = structlog.get_logger(__name__)
                    logger.warning(
                        "rag_context_failed",
                        job_id=str(job.id),
                        error=str(e),
                    )

            # Generate multiple typed notes
            typed_notes = generate_typed_notes(
                ai_result=ai_result,
                coaching=coaching_insights,
                requirement_matches=requirement_matches,
            )

            # Convert notes to dict format and append to job
            existing_notes = job.notes or []
            new_notes_dicts = [note.model_dump(mode="json") for note in typed_notes]
            job.notes = existing_notes + new_notes_dicts

        await db.flush()

    # Convert role_scores to response format
    role_scores_response = None
    if analysis.role_scores:
        from src.schemas.job import RoleScoreResponse
        role_scores_response = [
            RoleScoreResponse(
                role=RoleType(rs.role.value),
                score=rs.score,
                label=rs.label,
            )
            for rs in analysis.role_scores
        ]

    return JobAnalysisResponse(
        is_ai_forward=analysis.is_ai_forward,
        ai_confidence=analysis.ai_confidence,
        suggested_priority=analysis.suggested_priority,
        suggested_role=RoleType(analysis.suggested_role.value) if analysis.suggested_role else None,
        technologies_matched=analysis.technologies_matched,
        technologies_missing=analysis.technologies_missing,
        years_experience_required=analysis.years_experience_required,
        seniority_level=analysis.seniority_level,
        analysis_notes=analysis.analysis_notes,
        role_scores=role_scores_response,
        is_location_compatible=analysis.is_location_compatible,
        location_notes=analysis.location_notes,
    )


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


# Notes endpoints
@router.post(
    "/{job_id}/notes",
    response_model=JobNoteEntry,
    status_code=status.HTTP_201_CREATED,
    summary="Add note to job",
    description="Add a new note to a job with optional type and metadata.",
    dependencies=[Depends(require_permissions(["jobs:write"]))],
)
async def add_job_note(
    db: DbSession,
    job_id: UUID,
    note_in: JobNoteCreate,
) -> JobNoteEntry:
    """Add a note to a job."""
    query = select(Job).where(Job.id == job_id, Job.deleted_at.is_(None))
    result = await db.execute(query)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found",
        )

    # Create new note entry with type and metadata
    new_note = JobNoteEntry(
        text=note_in.text,
        timestamp=datetime.utcnow(),
        source=note_in.source,
        note_type=note_in.note_type,
        metadata=note_in.metadata,
    )

    # Append to existing notes array (or create new array)
    existing_notes = job.notes or []
    job.notes = existing_notes + [new_note.model_dump(mode="json")]

    await db.flush()

    return new_note


@router.get(
    "/{job_id}/notes",
    response_model=list[JobNoteEntry],
    summary="List notes for job",
    description="List all notes for a job with optional type filter.",
    dependencies=[Depends(require_permissions(["jobs:read"]))],
)
async def list_job_notes(
    db: DbSession,
    job_id: UUID,
    note_type: Annotated[NoteType | None, Query(description="Filter by note type")] = None,
    source: Annotated[NoteSource | None, Query(description="Filter by source (user/agent)")] = None,
) -> list[JobNoteEntry]:
    """List all notes for a job with optional filters."""
    query = select(Job).where(Job.id == job_id, Job.deleted_at.is_(None))
    result = await db.execute(query)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found",
        )

    if not job.notes:
        return []

    notes = [JobNoteEntry(**note) for note in job.notes]

    # Apply filters
    if note_type:
        notes = [n for n in notes if n.note_type == note_type]
    if source:
        notes = [n for n in notes if n.source == source]

    return notes


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
