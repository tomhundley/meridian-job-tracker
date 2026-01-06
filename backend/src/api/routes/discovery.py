"""Job discovery routes for finding and importing jobs from LinkedIn."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import ApiKey, DbSession, require_permissions
from src.models import Job, JobStatus
from src.schemas.discovery import (
    BulkDiscoveryRequest,
    BulkDiscoveryResponse,
    JobDiscoveryItem,
    LinkedInSearchRequest,
    LinkedInSearchResponse,
)
from src.services.linkedin_discovery import LinkedInJobDiscovery, DiscoveredJob

router = APIRouter(prefix="/discovery", tags=["discovery"])


@router.post(
    "/linkedin/search-url",
    response_model=LinkedInSearchResponse,
    summary="Generate LinkedIn search URL",
    description="Generate a LinkedIn job search URL with the specified filters. Use this URL with Playwright to search for jobs.",
)
async def generate_linkedin_search_url(
    request: LinkedInSearchRequest,
    _auth: ApiKey,
) -> LinkedInSearchResponse:
    """Generate a LinkedIn search URL for use with browser automation."""
    search_url = LinkedInJobDiscovery.build_search_url(
        keywords=request.keywords,
        location=request.location,
        experience_level=request.experience_level,
        date_posted=request.date_posted,
        remote=request.remote,
        easy_apply=request.easy_apply_only,
    )

    return LinkedInSearchResponse(
        search_url=search_url,
        message="Use this URL with Playwright browser automation to search LinkedIn",
        instructions=(
            "1. Navigate to this URL using Playwright\n"
            "2. Take a snapshot of the job listings\n"
            "3. Use the /discovery/linkedin/save endpoint to save discovered jobs"
        ),
    )


@router.post(
    "/linkedin/save",
    response_model=BulkDiscoveryResponse,
    summary="Save discovered LinkedIn jobs",
    description="Save multiple jobs discovered from LinkedIn search results to the database.",
    dependencies=[Depends(require_permissions(["jobs:write"]))],
)
async def save_discovered_jobs(
    request: BulkDiscoveryRequest,
    db: DbSession,
    _auth: ApiKey,
) -> BulkDiscoveryResponse:
    """Save discovered jobs to the database."""
    saved = 0
    skipped = 0
    errors: list[str] = []

    for job_item in request.jobs:
        try:
            # Check for existing job by LinkedIn ID if provided
            if request.auto_dedupe and job_item.linkedin_job_id:
                existing = await db.execute(
                    select(Job).where(
                        Job.job_board == "linkedin",
                        Job.job_board_id == job_item.linkedin_job_id,
                    )
                )
                if existing.scalar_one_or_none():
                    skipped += 1
                    continue

            # Create new job - use enum value for PostgreSQL compatibility
            from src.models.job import JobStatus as ModelJobStatus
            job = Job(
                title=job_item.title,
                company=job_item.company,
                location=job_item.location,
                url=job_item.url,
                job_board="linkedin",
                job_board_id=job_item.linkedin_job_id,
                status=ModelJobStatus.SAVED,
                notes=_build_notes(job_item),
                tags=_build_tags(job_item),
            )
            db.add(job)
            saved += 1

        except Exception as e:
            errors.append(f"Failed to save {job_item.title} at {job_item.company}: {str(e)}")

    await db.commit()

    return BulkDiscoveryResponse(
        saved=saved,
        skipped_duplicates=skipped,
        errors=errors,
    )


def _build_notes(job: JobDiscoveryItem) -> str | None:
    """Build notes string from job discovery data."""
    parts = []
    if job.posted_date:
        parts.append(f"Posted: {job.posted_date}")
    if job.salary_info:
        parts.append(f"Salary: {job.salary_info}")
    return " | ".join(parts) if parts else None


def _build_tags(job: JobDiscoveryItem) -> list[str]:
    """Build tags list from job discovery data."""
    tags = ["linkedin-discovered"]
    if job.is_easy_apply:
        tags.append("easy-apply")
    return tags


@router.get(
    "/stats",
    summary="Get discovery statistics",
    description="Get statistics about discovered jobs and application status.",
)
async def get_discovery_stats(
    db: DbSession,
    _auth: ApiKey,
) -> dict:
    """Get job discovery and application statistics."""
    from sqlalchemy import func

    # Total jobs by status
    status_counts = await db.execute(
        select(Job.status, func.count(Job.id))
        .where(Job.deleted_at.is_(None))
        .group_by(Job.status)
    )
    status_dict = {str(row[0].value): row[1] for row in status_counts.fetchall()}

    # Jobs discovered from LinkedIn
    linkedin_count = await db.execute(
        select(func.count(Job.id))
        .where(Job.job_board == "linkedin", Job.deleted_at.is_(None))
    )
    linkedin_total = linkedin_count.scalar() or 0

    # Applied jobs
    applied_count = await db.execute(
        select(func.count(Job.id))
        .where(
            Job.status.in_([JobStatus.APPLIED, JobStatus.INTERVIEWING, JobStatus.OFFER]),
            Job.deleted_at.is_(None),
        )
    )
    applied_total = applied_count.scalar() or 0

    # Jobs with easy-apply tag
    easy_apply_count = await db.execute(
        select(func.count(Job.id))
        .where(Job.tags.contains(["easy-apply"]), Job.deleted_at.is_(None))
    )
    easy_apply_total = easy_apply_count.scalar() or 0

    return {
        "total_jobs": sum(status_dict.values()),
        "by_status": status_dict,
        "linkedin_jobs": linkedin_total,
        "applied_jobs": applied_total,
        "easy_apply_jobs": easy_apply_total,
        "application_rate": f"{(applied_total / linkedin_total * 100):.1f}%" if linkedin_total > 0 else "0%",
    }
