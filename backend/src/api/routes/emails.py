"""Email endpoints."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select

from src.api.deps import ApiKey, DbSession
from src.models import Email
from src.schemas import EmailCreate, EmailResponse

router = APIRouter()


@router.get("", response_model=list[EmailResponse])
async def list_emails(
    db: DbSession,
    _api_key: ApiKey,
    job_id: UUID | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Email]:
    """List emails with optional job filter."""
    query = select(Email).where(Email.deleted_at.is_(None))

    if job_id:
        query = query.where(Email.job_id == job_id)

    query = query.order_by(Email.email_timestamp.desc()).offset(offset).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


@router.post("", response_model=EmailResponse, status_code=status.HTTP_201_CREATED)
async def create_email(
    db: DbSession,
    _api_key: ApiKey,
    email_in: EmailCreate,
) -> Email:
    """Create a new email record (typically from email agent)."""
    email = Email(
        job_id=email_in.job_id,
        from_email=email_in.from_email,
        to_email=email_in.to_email,
        subject=email_in.subject,
        body=email_in.body,
        email_timestamp=email_in.email_timestamp,
        is_inbound=email_in.is_inbound,
    )
    db.add(email)
    await db.flush()
    await db.refresh(email)
    return email


@router.get("/{email_id}", response_model=EmailResponse)
async def get_email(
    db: DbSession,
    _api_key: ApiKey,
    email_id: UUID,
) -> Email:
    """Get an email by ID."""
    query = select(Email).where(Email.id == email_id, Email.deleted_at.is_(None))
    result = await db.execute(query)
    email = result.scalar_one_or_none()

    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Email with id {email_id} not found",
        )

    return email


@router.patch("/{email_id}/link/{job_id}", response_model=EmailResponse)
async def link_email_to_job(
    db: DbSession,
    _api_key: ApiKey,
    email_id: UUID,
    job_id: UUID,
) -> Email:
    """Link an email to a job."""
    query = select(Email).where(Email.id == email_id, Email.deleted_at.is_(None))
    result = await db.execute(query)
    email = result.scalar_one_or_none()

    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Email with id {email_id} not found",
        )

    email.job_id = job_id
    await db.flush()
    await db.refresh(email)
    return email


@router.delete("/{email_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_email(
    db: DbSession,
    _api_key: ApiKey,
    email_id: UUID,
) -> None:
    """Soft delete an email."""
    query = select(Email).where(Email.id == email_id, Email.deleted_at.is_(None))
    result = await db.execute(query)
    email = result.scalar_one_or_none()

    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Email with id {email_id} not found",
        )

    email.deleted_at = datetime.utcnow()
    await db.flush()
