"""SQLAlchemy models for the Meridian Job Tracker."""

from .job import Job, JobStatus, RoleType, ApplicationMethod, WorkLocationType, EmploymentType
from .cover_letter import CoverLetter
from .email import Email
from .application_attempt import ApplicationAttempt
from .agent import Agent
from .webhook import Webhook
from .job_contact import JobContact
from .decline_reason import (
    UserDeclineReason,
    CompanyDeclineReason,
    USER_DECLINE_CATEGORIES,
    COMPANY_DECLINE_CATEGORIES,
)

__all__ = [
    "Job",
    "JobStatus",
    "RoleType",
    "ApplicationMethod",
    "WorkLocationType",
    "EmploymentType",
    "CoverLetter",
    "Email",
    "ApplicationAttempt",
    "Agent",
    "Webhook",
    "JobContact",
    "UserDeclineReason",
    "CompanyDeclineReason",
    "USER_DECLINE_CATEGORIES",
    "COMPANY_DECLINE_CATEGORIES",
]
