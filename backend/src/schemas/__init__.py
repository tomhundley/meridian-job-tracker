"""Pydantic schemas for API request/response validation."""

from .job import (
    JobCreate,
    JobUpdate,
    JobResponse,
    JobListResponse,
    JobStatusUpdate,
    JobIngestRequest,
    JobBulkIngestRequest,
    JobBulkIngestResponse,
    JobBulkStatusUpdate,
    JobBulkStatusResponse,
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
from .agent import AgentCreate, AgentResponse
from .webhook import WebhookCreate, WebhookResponse

__all__ = [
    # Job schemas
    "JobCreate",
    "JobUpdate",
    "JobResponse",
    "JobListResponse",
    "JobStatusUpdate",
    "JobIngestRequest",
    "JobBulkIngestRequest",
    "JobBulkIngestResponse",
    "JobBulkStatusUpdate",
    "JobBulkStatusResponse",
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
    # Agent schemas
    "AgentCreate",
    "AgentResponse",
    # Webhook schemas
    "WebhookCreate",
    "WebhookResponse",
]
