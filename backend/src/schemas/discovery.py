"""Pydantic schemas for job discovery."""

from pydantic import BaseModel, Field


class LinkedInSearchRequest(BaseModel):
    """Request to search LinkedIn for jobs."""

    keywords: str = Field(..., min_length=1, description="Search keywords (e.g., 'CTO', 'VP Engineering')")
    location: str | None = Field(None, description="Location filter (e.g., 'San Francisco, CA')")
    experience_level: list[str] | None = Field(
        None,
        description="Experience levels: 1=Internship, 2=Entry, 3=Associate, 4=Mid-Senior, 5=Director, 6=Executive",
    )
    date_posted: str | None = Field(
        None,
        description="Date filter: r86400=24h, r604800=week, r2592000=month",
    )
    remote: list[str] | None = Field(
        None,
        description="Work type: 1=On-site, 2=Remote, 3=Hybrid",
    )
    easy_apply_only: bool = Field(False, description="Filter to Easy Apply jobs only")


class LinkedInSearchResponse(BaseModel):
    """Response from LinkedIn job search."""

    search_url: str
    message: str
    instructions: str


class JobDiscoveryItem(BaseModel):
    """A discovered job from search results."""

    title: str
    company: str
    location: str | None = None
    url: str | None = None
    linkedin_job_id: str | None = None
    posted_date: str | None = None
    is_easy_apply: bool = False
    salary_info: str | None = None


class BulkDiscoveryRequest(BaseModel):
    """Request to save multiple discovered jobs."""

    jobs: list[JobDiscoveryItem] = Field(..., min_length=1)
    auto_dedupe: bool = Field(True, description="Skip jobs already in database")


class BulkDiscoveryResponse(BaseModel):
    """Response from bulk job discovery save."""

    saved: int
    skipped_duplicates: int
    errors: list[str]
