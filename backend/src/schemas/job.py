"""Pydantic schemas for Job API."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from src.schemas.job_contact import JobContactResponse
from src.schemas.job_note import JobNoteEntry


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


class WorkLocationType(str, Enum):
    """Work location type."""

    REMOTE = "remote"
    HYBRID = "hybrid"
    ON_SITE = "on_site"


class EmploymentType(str, Enum):
    """Employment type."""

    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    CONTRACT_TO_HIRE = "contract_to_hire"
    TEMPORARY = "temporary"
    INTERNSHIP = "internship"


class JobBase(BaseModel):
    """Base schema for Job."""

    title: str = Field(..., min_length=1, max_length=255)
    company: str = Field(..., min_length=1, max_length=255)
    location: str | None = Field(None, max_length=255)
    work_location_type: WorkLocationType | None = None
    url: str | None = None
    description_raw: str | None = None
    salary_min: int | None = Field(None, ge=0, description="Minimum annual salary")
    salary_max: int | None = Field(None, ge=0, description="Maximum annual salary")
    salary_currency: str | None = Field("USD", max_length=3, description="ISO 4217 currency code")
    employment_type: EmploymentType | None = None
    posted_at: datetime | None = Field(None, description="When the job was posted on the job board")
    target_role: RoleType | None = None
    priority: int = Field(50, ge=0, le=100)
    notes: list[JobNoteEntry] | None = Field(None, description="Structured notes array")
    tags: list[str] | None = None
    is_easy_apply: bool = Field(False, description="LinkedIn Easy Apply job")
    is_favorite: bool = Field(False, description="User marked as favorite")
    is_perfect_fit: bool = Field(False, description="User marked as perfect fit")
    is_ai_forward: bool = Field(False, description="AI-forward company/role")
    is_location_compatible: bool = Field(True, description="Location compatible with user")


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
    work_location_type: WorkLocationType | None = None
    url: str | None = None
    description_raw: str | None = None
    salary_min: int | None = Field(None, ge=0)
    salary_max: int | None = Field(None, ge=0)
    salary_currency: str | None = Field(None, max_length=3)
    employment_type: EmploymentType | None = None
    posted_at: datetime | None = None
    target_role: RoleType | None = None
    priority: int | None = Field(None, ge=0, le=100)
    notes: list[JobNoteEntry] | None = Field(None, description="Structured notes array")
    tags: list[str] | None = None
    is_easy_apply: bool | None = None
    is_favorite: bool | None = None
    is_perfect_fit: bool | None = None
    is_ai_forward: bool | None = None
    is_location_compatible: bool | None = None
    closed_reason: str | None = Field(None, max_length=100)
    user_decline_reasons: list[str] | None = None
    company_decline_reasons: list[str] | None = None
    decline_notes: str | None = None


class JobStatusUpdate(BaseModel):
    """Schema for updating job status."""

    status: JobStatus
    closed_reason: str | None = Field(None, max_length=100)
    user_decline_reasons: list[str] | None = None
    company_decline_reasons: list[str] | None = None
    decline_notes: str | None = None


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
    posted_at: datetime | None = None
    user_decline_reasons: list[str] | None = None
    company_decline_reasons: list[str] | None = None
    decline_notes: str | None = None
    contacts: list[JobContactResponse] = []
    contact_count: int = 0


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


class RoleScoreResponse(BaseModel):
    """Schema for a role-specific score."""

    role: RoleType = Field(..., description="The role type")
    score: int = Field(..., ge=0, le=100, description="Fit score for this role")
    label: str = Field(..., description="Human readable role label")


class JobAnalysisResponse(BaseModel):
    """Schema for job analysis result."""

    is_ai_forward: bool = Field(..., description="Whether this is an AI-forward company/role")
    ai_confidence: float = Field(..., ge=0, le=1, description="Confidence score for AI-forward detection")
    suggested_priority: int = Field(..., ge=0, le=100, description="Suggested priority/fit score")
    suggested_role: RoleType | None = Field(None, description="Suggested target role based on job")
    technologies_matched: list[str] = Field(default_factory=list, description="Technologies that match resume")
    technologies_missing: list[str] = Field(default_factory=list, description="Required technologies not in resume")
    years_experience_required: int | None = Field(None, description="Years of experience required")
    seniority_level: str | None = Field(None, description="Detected seniority level")
    analysis_notes: list[str] = Field(default_factory=list, description="Analysis notes and observations")
    role_scores: list[RoleScoreResponse] | None = Field(None, description="Fit scores for each target role")
    is_location_compatible: bool = Field(True, description="Whether job location is compatible with user")
    location_notes: str | None = Field(None, description="Explanation of location compatibility")
