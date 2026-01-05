"""Pydantic schemas for API request/response validation."""

from .job import (
    JobCreate,
    JobUpdate,
    JobResponse,
    JobListResponse,
    JobStatusUpdate,
    JobStatus,
    RoleType,
    ApplicationMethod,
)
from .cover_letter import (
    CoverLetterCreate,
    CoverLetterResponse,
    CoverLetterApprove,
)
from .email import (
    EmailCreate,
    EmailResponse,
)

__all__ = [
    # Job schemas
    "JobCreate",
    "JobUpdate",
    "JobResponse",
    "JobListResponse",
    "JobStatusUpdate",
    "JobStatus",
    "RoleType",
    "ApplicationMethod",
    # Cover letter schemas
    "CoverLetterCreate",
    "CoverLetterResponse",
    "CoverLetterApprove",
    # Email schemas
    "EmailCreate",
    "EmailResponse",
]
