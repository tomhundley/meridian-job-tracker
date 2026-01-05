"""Cover letter model for generated application letters."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config.database import Base

from .job import RoleType

if TYPE_CHECKING:
    from .job import Job


class CoverLetter(Base):
    """Generated cover letter for a job application."""

    __tablename__ = "cover_letters"

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

    # Content
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Generation metadata
    target_role: Mapped[RoleType] = mapped_column(
        Enum(RoleType, name="role_type", create_type=False),
        nullable=False,
    )
    generation_prompt: Mapped[str | None] = mapped_column(Text)
    model_used: Mapped[str | None] = mapped_column(String(100))

    # Versioning
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Approval status
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationship
    job: Mapped["Job"] = relationship("Job", back_populates="cover_letters")

    def __repr__(self) -> str:
        return f"<CoverLetter v{self.version} for job {self.job_id}>"
