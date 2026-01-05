"""Pydantic schemas for Cover Letter API."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .job import RoleType


class CoverLetterBase(BaseModel):
    """Base schema for CoverLetter."""

    target_role: RoleType
    custom_instructions: str | None = None


class CoverLetterCreate(CoverLetterBase):
    """Schema for generating a new cover letter."""

    pass


class CoverLetterUpdate(BaseModel):
    """Schema for updating a cover letter."""

    content: str = Field(..., min_length=1)


class CoverLetterApprove(BaseModel):
    """Schema for approving a cover letter."""

    is_approved: bool = True


class CoverLetterResponse(BaseModel):
    """Schema for cover letter response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    created_at: datetime
    updated_at: datetime
    content: str
    target_role: RoleType
    generation_prompt: str | None = None
    model_used: str | None = None
    version: int
    is_current: bool
    is_approved: bool
    approved_at: datetime | None = None
