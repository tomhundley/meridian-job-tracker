"""Pydantic schemas for Job Contact API."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ContactType(str, Enum):
    """Type of contact in the hiring process."""

    RECRUITER = "recruiter"
    HIRING_MANAGER = "hiring_manager"
    TEAM_MEMBER = "team_member"
    JOB_POSTER = "job_poster"
    HR_CONTACT = "hr_contact"


class JobContactBase(BaseModel):
    """Base schema for JobContact."""

    name: str = Field(..., min_length=1, max_length=255)
    title: str | None = Field(None, max_length=255)
    linkedin_url: str | None = None
    linkedin_member_id: str | None = Field(None, max_length=100)
    email: str | None = Field(None, max_length=255)
    contact_type: ContactType = ContactType.RECRUITER
    is_job_poster: bool = False
    notes: str | None = None


class JobContactCreate(JobContactBase):
    """Schema for creating a new job contact."""

    pass


class JobContactUpdate(BaseModel):
    """Schema for updating a job contact."""

    name: str | None = Field(None, min_length=1, max_length=255)
    title: str | None = Field(None, max_length=255)
    linkedin_url: str | None = None
    linkedin_member_id: str | None = Field(None, max_length=100)
    email: str | None = Field(None, max_length=255)
    contact_type: ContactType | None = None
    is_job_poster: bool | None = None
    notes: str | None = None
    contacted_at: datetime | None = None
    response_received_at: datetime | None = None


class JobContactResponse(BaseModel):
    """Schema for job contact response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    created_at: datetime
    updated_at: datetime
    name: str
    title: str | None = None
    linkedin_url: str | None = None
    linkedin_member_id: str | None = None
    email: str | None = None
    contact_type: str
    is_job_poster: bool
    notes: str | None = None
    contacted_at: datetime | None = None
    response_received_at: datetime | None = None
