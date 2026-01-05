"""Email model for correspondence tracking."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config.database import Base

if TYPE_CHECKING:
    from .job import Job


class Email(Base):
    """Email correspondence related to job applications."""

    __tablename__ = "emails"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign key to job (nullable - email might not be linked yet)
    job_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="SET NULL"),
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

    # Email metadata
    from_email: Mapped[str] = mapped_column(String(255), nullable=False)
    to_email: Mapped[str | None] = mapped_column(String(255))
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str | None] = mapped_column(Text)

    # Timestamp of the actual email
    email_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Direction tracking
    is_inbound: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationship
    job: Mapped["Job | None"] = relationship("Job", back_populates="emails")

    def __repr__(self) -> str:
        return f"<Email '{self.subject}' from {self.from_email}>"
