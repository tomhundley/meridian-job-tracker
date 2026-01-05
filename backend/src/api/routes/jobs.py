"""Job CRUD endpoints."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from src.api.deps import ApiKey, DbSession
from src.models import Job, JobStatus as ModelJobStatus, RoleType as ModelRoleType
from src.schemas import (
    JobCreate,
    JobListResponse,
    JobResponse,
    JobStatusUpdate,
    JobUpdate,
    JobStatus,
    RoleType,
    CoverLetterCreate,
    CoverLetterResponse,
)

router = APIRouter()


@router.get("", response_model=JobListResponse)
async def list_jobs(
    db: DbSession,
    _api_key: ApiKey,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    status: JobStatus | None = None,
    company: str | None = None,
    target_role: RoleType | None = None,
    search: str | None = None,
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

    # Apply pagination and ordering
    query = (
        query.order_by(Job.priority.desc(), Job.created_at.desc())
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


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    db: DbSession,
    _api_key: ApiKey,
    job_in: JobCreate,
) -> Job:
    """Create a new job."""
    job = Job(
        title=job_in.title,
        company=job_in.company,
        location=job_in.location,
        url=job_in.url,
        description_raw=job_in.description_raw,
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


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    db: DbSession,
    _api_key: ApiKey,
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


@router.patch("/{job_id}", response_model=JobResponse)
async def update_job(
    db: DbSession,
    _api_key: ApiKey,
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
        if field == "target_role" and value is not None:
            value = ModelRoleType(value.value)
        setattr(job, field, value)

    await db.flush()
    await db.refresh(job)
    return job


@router.patch("/{job_id}/status", response_model=JobResponse)
async def update_job_status(
    db: DbSession,
    _api_key: ApiKey,
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
    if status_update.closed_reason:
        job.closed_reason = status_update.closed_reason

    # Set applied_at if transitioning to applied
    if status_update.status == JobStatus.APPLIED and job.applied_at is None:
        job.applied_at = datetime.utcnow()

    await db.flush()
    await db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    db: DbSession,
    _api_key: ApiKey,
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
@router.post("/{job_id}/cover-letter", response_model=CoverLetterResponse, status_code=status.HTTP_201_CREATED)
async def generate_cover_letter(
    db: DbSession,
    _api_key: ApiKey,
    job_id: UUID,
    request: CoverLetterCreate,
) -> CoverLetterModel:
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


@router.get("/{job_id}/cover-letters", response_model=list[CoverLetterResponse])
async def list_job_cover_letters(
    db: DbSession,
    _api_key: ApiKey,
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
