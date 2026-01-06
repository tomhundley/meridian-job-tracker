"""Pydantic schemas for Agent API."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AgentCreate(BaseModel):
    """Schema for creating an agent."""

    name: str = Field(..., min_length=1, max_length=200)
    permissions: list[str] = Field(default_factory=list)


class AgentResponse(BaseModel):
    """Schema for agent response (includes API key on creation)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    permissions: list[str]
    api_key: str
    is_active: bool
    created_at: datetime
