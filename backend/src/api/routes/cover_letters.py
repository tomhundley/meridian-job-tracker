"""Cover letter endpoints."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from src.api.deps import DbSession, require_permissions
from src.models import CoverLetter, Job
from src.models.job import RoleType as ModelRoleType
from src.schemas import CoverLetterApprove, CoverLetterResponse

router = APIRouter()


@router.get(
    "/{cover_letter_id}",
    response_model=CoverLetterResponse,
    summary="Get cover letter",
    description="Retrieve a cover letter by ID.",
    dependencies=[Depends(require_permissions(["cover_letters:read"]))],
)
async def get_cover_letter(
    db: DbSession,
    cover_letter_id: UUID,
) -> CoverLetter:
    """Get a cover letter by ID."""
    query = select(CoverLetter).where(
        CoverLetter.id == cover_letter_id,
        CoverLetter.deleted_at.is_(None),
    )
    result = await db.execute(query)
    cover_letter = result.scalar_one_or_none()

    if not cover_letter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cover letter with id {cover_letter_id} not found",
        )

    return cover_letter


@router.patch(
    "/{cover_letter_id}/approve",
    response_model=CoverLetterResponse,
    summary="Approve cover letter",
    description="Approve or unapprove a cover letter.",
    dependencies=[Depends(require_permissions(["cover_letters:approve"]))],
)
async def approve_cover_letter(
    db: DbSession,
    cover_letter_id: UUID,
    approval: CoverLetterApprove,
) -> CoverLetter:
    """Approve or unapprove a cover letter."""
    query = select(CoverLetter).where(
        CoverLetter.id == cover_letter_id,
        CoverLetter.deleted_at.is_(None),
    )
    result = await db.execute(query)
    cover_letter = result.scalar_one_or_none()

    if not cover_letter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cover letter with id {cover_letter_id} not found",
        )

    cover_letter.is_approved = approval.is_approved
    cover_letter.approved_at = datetime.utcnow() if approval.is_approved else None

    await db.flush()
    await db.refresh(cover_letter)
    return cover_letter


@router.delete(
    "/{cover_letter_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete cover letter",
    description="Soft delete a cover letter.",
    dependencies=[Depends(require_permissions(["cover_letters:delete"]))],
)
async def delete_cover_letter(
    db: DbSession,
    cover_letter_id: UUID,
) -> None:
    """Soft delete a cover letter."""
    query = select(CoverLetter).where(
        CoverLetter.id == cover_letter_id,
        CoverLetter.deleted_at.is_(None),
    )
    result = await db.execute(query)
    cover_letter = result.scalar_one_or_none()

    if not cover_letter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cover letter with id {cover_letter_id} not found",
        )

    cover_letter.deleted_at = datetime.utcnow()
    await db.flush()
