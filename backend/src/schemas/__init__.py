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
    WorkLocationType,
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
from .discovery import (
    LinkedInSearchRequest,
    LinkedInSearchResponse,
    JobDiscoveryItem,
    BulkDiscoveryRequest,
    BulkDiscoveryResponse,
)
from .decline_reason import (
    DeclineReasonResponse,
    CategoryWithReasons,
    DeclineReasonsListResponse,
    DeclineUpdate,
)
from .job_contact import (
    JobContactCreate,
    JobContactUpdate,
    JobContactResponse,
    ContactType,
)

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
    "WorkLocationType",
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
    # Discovery schemas
    "LinkedInSearchRequest",
    "LinkedInSearchResponse",
    "JobDiscoveryItem",
    "BulkDiscoveryRequest",
    "BulkDiscoveryResponse",
    # Decline reason schemas
    "DeclineReasonResponse",
    "CategoryWithReasons",
    "DeclineReasonsListResponse",
    "DeclineUpdate",
    # Job contact schemas
    "JobContactCreate",
    "JobContactUpdate",
    "JobContactResponse",
    "ContactType",
]
