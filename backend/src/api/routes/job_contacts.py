"""Job contact endpoints for tracking hiring team members."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from src.api.deps import DbSession, require_permissions
from src.models import Job, JobContact
from src.schemas import JobContactCreate, JobContactUpdate, JobContactResponse

router = APIRouter()


async def get_job_or_404(db: DbSession, job_id: UUID) -> Job:
    """Get a job by ID or raise 404."""
    query = select(Job).where(Job.id == job_id, Job.deleted_at.is_(None))
    result = await db.execute(query)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found",
        )
    return job


async def get_contact_or_404(db: DbSession, job_id: UUID, contact_id: UUID) -> JobContact:
    """Get a contact by ID for a specific job or raise 404."""
    query = select(JobContact).where(
        JobContact.id == contact_id,
        JobContact.job_id == job_id,
    )
    result = await db.execute(query)
    contact = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with id {contact_id} not found for job {job_id}",
        )
    return contact


@router.get(
    "",
    response_model=list[JobContactResponse],
    summary="List job contacts",
    description="Retrieve all contacts for a job (hiring team, recruiters, etc.).",
    dependencies=[Depends(require_permissions(["jobs:read"]))],
)
async def list_job_contacts(
    db: DbSession,
    job_id: UUID,
) -> list[JobContact]:
    """List all contacts for a job."""
    # Verify job exists
    await get_job_or_404(db, job_id)

    query = select(JobContact).where(JobContact.job_id == job_id).order_by(JobContact.created_at)
    result = await db.execute(query)
    return list(result.scalars().all())


@router.post(
    "",
    response_model=JobContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add job contact",
    description="Add a new contact to a job (recruiter, hiring manager, etc.).",
    dependencies=[Depends(require_permissions(["jobs:write"]))],
)
async def create_job_contact(
    db: DbSession,
    job_id: UUID,
    contact_data: JobContactCreate,
) -> JobContact:
    """Add a new contact to a job."""
    # Verify job exists
    await get_job_or_404(db, job_id)

    # Check for duplicate linkedin_url if provided
    if contact_data.linkedin_url:
        existing_query = select(JobContact).where(
            JobContact.job_id == job_id,
            JobContact.linkedin_url == contact_data.linkedin_url,
        )
        existing = await db.execute(existing_query)
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Contact with LinkedIn URL {contact_data.linkedin_url} already exists for this job",
            )

    contact = JobContact(
        job_id=job_id,
        name=contact_data.name,
        title=contact_data.title,
        linkedin_url=contact_data.linkedin_url,
        linkedin_member_id=contact_data.linkedin_member_id,
        email=contact_data.email,
        contact_type=contact_data.contact_type.value,
        is_job_poster=contact_data.is_job_poster,
        notes=contact_data.notes,
    )

    db.add(contact)
    await db.flush()
    await db.refresh(contact)
    return contact


@router.get(
    "/{contact_id}",
    response_model=JobContactResponse,
    summary="Get job contact",
    description="Retrieve a specific contact for a job.",
    dependencies=[Depends(require_permissions(["jobs:read"]))],
)
async def get_job_contact(
    db: DbSession,
    job_id: UUID,
    contact_id: UUID,
) -> JobContact:
    """Get a specific contact for a job."""
    return await get_contact_or_404(db, job_id, contact_id)


@router.patch(
    "/{contact_id}",
    response_model=JobContactResponse,
    summary="Update job contact",
    description="Update a contact's information (notes, contacted status, etc.).",
    dependencies=[Depends(require_permissions(["jobs:write"]))],
)
async def update_job_contact(
    db: DbSession,
    job_id: UUID,
    contact_id: UUID,
    contact_data: JobContactUpdate,
) -> JobContact:
    """Update a contact's information."""
    contact = await get_contact_or_404(db, job_id, contact_id)

    # Update only provided fields
    update_data = contact_data.model_dump(exclude_unset=True)

    # Handle contact_type enum conversion
    if "contact_type" in update_data and update_data["contact_type"] is not None:
        update_data["contact_type"] = update_data["contact_type"].value

    for field, value in update_data.items():
        setattr(contact, field, value)

    await db.flush()
    await db.refresh(contact)
    return contact


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete job contact",
    description="Remove a contact from a job.",
    dependencies=[Depends(require_permissions(["jobs:write"]))],
)
async def delete_job_contact(
    db: DbSession,
    job_id: UUID,
    contact_id: UUID,
) -> None:
    """Delete a contact from a job."""
    contact = await get_contact_or_404(db, job_id, contact_id)
    await db.delete(contact)
    await db.flush()
