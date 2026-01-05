"""Application attempt model for tracking automation."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config.database import Base

from .job import ApplicationMethod

if TYPE_CHECKING:
    from .job import Job


class ApplicationAttempt(Base):
    """Automation attempt for a job application."""

    __tablename__ = "application_attempts"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign key to job
    job_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    # Attempt details
    method: Mapped[ApplicationMethod] = mapped_column(
        Enum(ApplicationMethod, name="application_method", create_type=False),
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Status
    success: Mapped[bool | None] = mapped_column(Boolean)
    error_message: Mapped[str | None] = mapped_column(Text)

    # Automation details
    screenshot_path: Mapped[str | None] = mapped_column(Text)
    form_data: Mapped[dict | None] = mapped_column(JSONB)

    # Human confirmation
    requires_confirmation: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    confirmed_by: Mapped[str | None] = mapped_column(String(100))

    # Relationship
    job: Mapped["Job"] = relationship("Job", back_populates="application_attempts")

    def __repr__(self) -> str:
        status = "success" if self.success else "failed" if self.success is False else "pending"
        return f"<ApplicationAttempt {self.method.value} - {status}>"
