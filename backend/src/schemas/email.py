"""Pydantic schemas for Email API."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EmailBase(BaseModel):
    """Base schema for Email."""

    from_email: EmailStr
    to_email: EmailStr | None = None
    subject: str = Field(..., min_length=1, max_length=500)
    body: str | None = None
    email_timestamp: datetime
    is_inbound: bool = True


class EmailCreate(EmailBase):
    """Schema for creating a new email record."""

    job_id: UUID | None = None


class EmailUpdate(BaseModel):
    """Schema for updating an email record."""

    job_id: UUID | None = None
    subject: str | None = Field(None, min_length=1, max_length=500)
    body: str | None = None


class EmailResponse(EmailBase):
    """Schema for email response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID | None = None
    created_at: datetime
    updated_at: datetime
