"""Agent model for API access."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.config.database import Base


class Agent(Base):
    """API agent with scoped permissions."""

    __tablename__ = "agents"
    __table_args__ = (
        UniqueConstraint("name", name="uq_agent_name"),
        UniqueConstraint("api_key", name="uq_agent_api_key"),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

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

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    api_key: Mapped[str] = mapped_column(String(255), nullable=False)
    permissions: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<Agent {self.name}>"
