"""Pydantic schemas for Job API."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class JobStatus(str, Enum):
    """Job application status."""

    SAVED = "saved"
    RESEARCHING = "researching"
    READY_TO_APPLY = "ready_to_apply"
    APPLYING = "applying"
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    ARCHIVED = "archived"


class RoleType(str, Enum):
    """Target role type."""

    CTO = "cto"
    VP = "vp"
    DIRECTOR = "director"
    ARCHITECT = "architect"
    DEVELOPER = "developer"


class ApplicationMethod(str, Enum):
    """Application method."""

    LINKEDIN_QUICK_APPLY = "linkedin_quick_apply"
    LINKEDIN_FULL_APPLY = "linkedin_full_apply"
    COMPANY_WEBSITE = "company_website"
    EMAIL = "email"
    REFERRAL = "referral"
    RECRUITER = "recruiter"
    MANUAL = "manual"


class JobBase(BaseModel):
    """Base schema for Job."""

    title: str = Field(..., min_length=1, max_length=255)
    company: str = Field(..., min_length=1, max_length=255)
    location: str | None = Field(None, max_length=255)
    url: str | None = None
    description_raw: str | None = None
    target_role: RoleType | None = None
    priority: int = Field(50, ge=0, le=100)
    notes: str | None = None
    tags: list[str] | None = None


class JobCreate(JobBase):
    """Schema for creating a new job."""

    job_board: str | None = Field(None, max_length=50)
    job_board_id: str | None = Field(None, max_length=255)


class JobIngestRequest(BaseModel):
    """Schema for ingesting a job from a URL."""

    url: HttpUrl
    source: str | None = Field(None, max_length=50)
    notes: str | None = None


class JobUpdate(BaseModel):
    """Schema for updating a job."""

    title: str | None = Field(None, min_length=1, max_length=255)
    company: str | None = Field(None, min_length=1, max_length=255)
    location: str | None = Field(None, max_length=255)
    url: str | None = None
    description_raw: str | None = None
    target_role: RoleType | None = None
    priority: int | None = Field(None, ge=0, le=100)
    notes: str | None = None
    tags: list[str] | None = None
    closed_reason: str | None = Field(None, max_length=100)


class JobStatusUpdate(BaseModel):
    """Schema for updating job status."""

    status: JobStatus
    closed_reason: str | None = Field(None, max_length=100)


class JobBulkStatusUpdate(BaseModel):
    """Schema for updating status on multiple jobs."""

    job_ids: list[UUID] = Field(..., min_length=1)
    status: JobStatus
    closed_reason: str | None = Field(None, max_length=100)


class JobResponse(JobBase):
    """Schema for job response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
    status: JobStatus
    status_changed_at: datetime
    closed_reason: str | None = None
    job_board: str | None = None
    job_board_id: str | None = None
    application_method: ApplicationMethod | None = None
    applied_at: datetime | None = None


class JobBulkIngestRequest(BaseModel):
    """Schema for ingesting multiple jobs from URLs."""

    jobs: list[JobIngestRequest] = Field(..., min_length=1)


class JobBulkIngestError(BaseModel):
    """Schema for failed bulk ingest items."""

    url: str
    error: str


class JobBulkIngestResponse(BaseModel):
    """Schema for bulk ingest response."""

    created: list[JobResponse]
    failed: list[JobBulkIngestError]


class JobBulkStatusResponse(BaseModel):
    """Schema for bulk status update response."""

    updated: list[JobResponse]
    missing: list[UUID]


class JobListResponse(BaseModel):
    """Schema for paginated job list response."""

    items: list[JobResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
