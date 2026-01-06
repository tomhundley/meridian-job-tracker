"""Pydantic schemas for Webhook API."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class WebhookCreate(BaseModel):
    """Schema for creating a webhook subscription."""

    url: HttpUrl
    events: list[str] = Field(default_factory=list)
    secret: str | None = Field(None, max_length=255)
    is_active: bool = True


class WebhookResponse(BaseModel):
    """Schema for webhook response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    url: str
    events: list[str]
    secret: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
