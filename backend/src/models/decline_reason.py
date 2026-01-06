"""Decline reason lookup models."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.config.database import Base


class UserDeclineReason(Base):
    """Lookup table for reasons user passes on a job."""

    __tablename__ = "user_decline_reasons"

    code: Mapped[str] = mapped_column(String(50), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )

    def __repr__(self) -> str:
        return f"<UserDeclineReason {self.code}>"


class CompanyDeclineReason(Base):
    """Lookup table for reasons company rejects user."""

    __tablename__ = "company_decline_reasons"

    code: Mapped[str] = mapped_column(String(50), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )

    def __repr__(self) -> str:
        return f"<CompanyDeclineReason {self.code}>"


# Category display names for UI grouping
USER_DECLINE_CATEGORIES = {
    "compensation": "Compensation",
    "location": "Location & Remote",
    "role_fit": "Role Fit",
    "company": "Company Concerns",
    "process": "Process Issues",
    "personal": "Personal",
}

COMPANY_DECLINE_CATEGORIES = {
    "selection": "Candidate Selection",
    "experience": "Experience & Skills",
    "fit": "Fit & Expectations",
    "verification": "Verification",
    "interview": "Interview",
    "other": "Other",
}
