"""Job model for tracking job applications."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config.database import Base

if TYPE_CHECKING:
    from .application_attempt import ApplicationAttempt
    from .cover_letter import CoverLetter
    from .email import Email
    from .job_contact import JobContact


class JobStatus(str, enum.Enum):
    """Status of a job application."""

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


class RoleType(str, enum.Enum):
    """Target role types matching resume data."""

    CTO = "cto"
    VP = "vp"
    DIRECTOR = "director"
    ARCHITECT = "architect"
    DEVELOPER = "developer"


class ApplicationMethod(str, enum.Enum):
    """Method used to apply for a job."""

    LINKEDIN_QUICK_APPLY = "linkedin_quick_apply"
    LINKEDIN_FULL_APPLY = "linkedin_full_apply"
    COMPANY_WEBSITE = "company_website"
    EMAIL = "email"
    REFERRAL = "referral"
    RECRUITER = "recruiter"
    MANUAL = "manual"


class WorkLocationType(str, enum.Enum):
    """Work location type for the job."""

    REMOTE = "remote"
    HYBRID = "hybrid"
    ON_SITE = "on_site"


class EmploymentType(str, enum.Enum):
    """Employment type for the job."""

    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    CONTRACT_TO_HIRE = "contract_to_hire"
    TEMPORARY = "temporary"
    INTERNSHIP = "internship"


class Job(Base):
    """Job posting being tracked for applications."""

    __tablename__ = "jobs"

    __table_args__ = (
        UniqueConstraint("job_board", "job_board_id", name="uq_job_board_id"),
        CheckConstraint("priority >= 0 AND priority <= 100", name="check_priority_range"),
    )

    # Primary key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Core job info
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str | None] = mapped_column(String(255))
    work_location_type: Mapped[WorkLocationType | None] = mapped_column(
        Enum(WorkLocationType, name="work_location_type", create_type=False, values_callable=lambda x: [e.value for e in x]),
    )
    url: Mapped[str | None] = mapped_column(Text)
    job_board: Mapped[str | None] = mapped_column(String(50))
    job_board_id: Mapped[str | None] = mapped_column(String(255))

    # Job description
    description_raw: Mapped[str | None] = mapped_column(Text)
    source_html: Mapped[str | None] = mapped_column(Text)

    # Compensation (all optional)
    salary_min: Mapped[int | None] = mapped_column(Integer)
    salary_max: Mapped[int | None] = mapped_column(Integer)
    salary_currency: Mapped[str | None] = mapped_column(String(3), default="USD")
    employment_type: Mapped[EmploymentType | None] = mapped_column(
        Enum(EmploymentType, name="employment_type", create_type=False, values_callable=lambda x: [e.value for e in x]),
    )

    # Status tracking
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status", create_type=False, values_callable=lambda x: [e.value for e in x]),
        default=JobStatus.SAVED,
        nullable=False,
    )
    status_changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    closed_reason: Mapped[str | None] = mapped_column(String(100))

    # Role matching
    target_role: Mapped[RoleType | None] = mapped_column(
        Enum(RoleType, name="role_type", create_type=False, values_callable=lambda x: [e.value for e in x]),
    )

    # Priority and organization
    priority: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(Text))

    # Job posting date (when posted on job board)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # LinkedIn Easy Apply flag
    is_easy_apply: Mapped[bool] = mapped_column(default=False, nullable=False)

    # User preference flags
    is_favorite: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_perfect_fit: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_ai_forward: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Application details
    application_method: Mapped[ApplicationMethod | None] = mapped_column(
        Enum(ApplicationMethod, name="application_method", create_type=False, values_callable=lambda x: [e.value for e in x]),
    )
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Decline tracking (arrays for multiple reasons)
    user_decline_reasons: Mapped[list[str] | None] = mapped_column(ARRAY(String(50)))
    company_decline_reasons: Mapped[list[str] | None] = mapped_column(ARRAY(String(50)))
    decline_notes: Mapped[str | None] = mapped_column(Text)

    # Soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    cover_letters: Mapped[list["CoverLetter"]] = relationship(
        "CoverLetter",
        back_populates="job",
        cascade="all, delete-orphan",
    )
    emails: Mapped[list["Email"]] = relationship(
        "Email",
        back_populates="job",
    )
    application_attempts: Mapped[list["ApplicationAttempt"]] = relationship(
        "ApplicationAttempt",
        back_populates="job",
        cascade="all, delete-orphan",
    )
    contacts: Mapped[list["JobContact"]] = relationship(
        "JobContact",
        back_populates="job",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Job {self.title} at {self.company}>"
