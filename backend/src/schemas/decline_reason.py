"""Pydantic schemas for decline reasons API."""

from pydantic import BaseModel, ConfigDict


class DeclineReasonResponse(BaseModel):
    """A single decline reason."""

    model_config = ConfigDict(from_attributes=True)

    code: str
    display_name: str
    category: str
    description: str | None = None


class CategoryWithReasons(BaseModel):
    """A category containing multiple decline reasons."""

    name: str
    display_name: str
    reasons: list[DeclineReasonResponse]


class DeclineReasonsListResponse(BaseModel):
    """Response containing all decline reasons grouped by category."""

    categories: list[CategoryWithReasons]


class DeclineUpdate(BaseModel):
    """Schema for updating decline reasons on a job."""

    user_decline_reasons: list[str] | None = None
    company_decline_reasons: list[str] | None = None
    decline_notes: str | None = None
