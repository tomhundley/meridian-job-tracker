"""
Description Fetcher Service for incomplete job descriptions.

This service identifies jobs with truncated/incomplete descriptions and
provides utilities for batch processing. Actual fetching is performed
by browser automation (Chrome DevTools MCP or Playwright) through
Claude Code agents.

The issue: LinkedIn and other job boards require JavaScript to render
full descriptions. The httpx-based scraper only gets ~150 chars from
meta tags. This service helps identify and track jobs needing updates.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

import structlog
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Job

logger = structlog.get_logger(__name__)

# Minimum description length to consider "complete"
MIN_DESCRIPTION_LENGTH = 500
# Target description length for good analysis
TARGET_DESCRIPTION_LENGTH = 2000


@dataclass
class IncompleteJobInfo:
    """Information about a job with incomplete description."""

    id: UUID
    title: str
    company: str
    url: str | None
    job_board: str | None
    job_board_id: str | None
    description_length: int
    needs_fetch: bool


@dataclass
class FetchResult:
    """Result of a description fetch operation."""

    job_id: UUID
    success: bool
    old_length: int
    new_length: int
    error: str | None = None


class DescriptionFetcherService:
    """
    Service for identifying and managing incomplete job descriptions.

    This service helps identify jobs that need full descriptions fetched
    via browser automation. It provides:

    1. Detection of incomplete descriptions (<500 chars)
    2. Job URL building for LinkedIn and other sources
    3. Batch processing utilities
    4. Description update tracking

    Note: Actual browser automation is performed by Claude Code agents
    using Chrome DevTools MCP or Playwright MCP tools.
    """

    def __init__(self):
        self.min_length = MIN_DESCRIPTION_LENGTH
        self.target_length = TARGET_DESCRIPTION_LENGTH

    async def get_incomplete_jobs(
        self,
        db: AsyncSession,
        limit: int = 20,
        min_chars: int | None = None,
    ) -> list[IncompleteJobInfo]:
        """
        Get jobs with incomplete descriptions.

        Args:
            db: Database session
            limit: Maximum number of jobs to return
            min_chars: Override minimum description length

        Returns:
            List of jobs needing description updates
        """
        min_length = min_chars or self.min_length

        # Query for jobs with short descriptions
        query = (
            select(Job)
            .where(
                Job.deleted_at.is_(None),
                Job.description_raw.isnot(None),
                func.length(Job.description_raw) < min_length,
            )
            .order_by(Job.created_at.desc())
            .limit(limit)
        )

        result = await db.execute(query)
        jobs = list(result.scalars().all())

        incomplete_jobs = []
        for job in jobs:
            desc_len = len(job.description_raw) if job.description_raw else 0
            incomplete_jobs.append(
                IncompleteJobInfo(
                    id=job.id,
                    title=job.title,
                    company=job.company,
                    url=job.url,
                    job_board=job.job_board,
                    job_board_id=job.job_board_id,
                    description_length=desc_len,
                    needs_fetch=desc_len < min_length,
                )
            )

        logger.info(
            "incomplete_jobs_found",
            count=len(incomplete_jobs),
            min_length=min_length,
        )

        return incomplete_jobs

    async def get_jobs_without_descriptions(
        self,
        db: AsyncSession,
        limit: int = 20,
    ) -> list[IncompleteJobInfo]:
        """
        Get jobs with no description at all.

        Args:
            db: Database session
            limit: Maximum number of jobs to return

        Returns:
            List of jobs with empty/null descriptions
        """
        query = (
            select(Job)
            .where(
                Job.deleted_at.is_(None),
                (Job.description_raw.is_(None)) | (Job.description_raw == ""),
            )
            .order_by(Job.created_at.desc())
            .limit(limit)
        )

        result = await db.execute(query)
        jobs = list(result.scalars().all())

        return [
            IncompleteJobInfo(
                id=job.id,
                title=job.title,
                company=job.company,
                url=job.url,
                job_board=job.job_board,
                job_board_id=job.job_board_id,
                description_length=0,
                needs_fetch=True,
            )
            for job in jobs
        ]

    def build_fetch_url(self, job_info: IncompleteJobInfo) -> str | None:
        """
        Build the URL to fetch the full description from.

        Handles LinkedIn and other job boards specifically.

        Args:
            job_info: Job information including URL and job_board

        Returns:
            URL to navigate to for fetching, or None if no URL available
        """
        # If we have a direct URL, use it
        if job_info.url:
            return job_info.url

        # Try to build URL from job_board and job_board_id
        if job_info.job_board and job_info.job_board_id:
            if job_info.job_board.lower() == "linkedin":
                return f"https://www.linkedin.com/jobs/view/{job_info.job_board_id}/"
            elif job_info.job_board.lower() == "indeed":
                return f"https://www.indeed.com/viewjob?jk={job_info.job_board_id}"
            # Add more job boards as needed

        return None

    async def update_description(
        self,
        db: AsyncSession,
        job_id: UUID,
        new_description: str,
    ) -> FetchResult:
        """
        Update a job's description after fetching.

        Args:
            db: Database session
            job_id: Job ID to update
            new_description: The new full description

        Returns:
            FetchResult with success/failure info
        """
        query = select(Job).where(Job.id == job_id, Job.deleted_at.is_(None))
        result = await db.execute(query)
        job = result.scalar_one_or_none()

        if not job:
            return FetchResult(
                job_id=job_id,
                success=False,
                old_length=0,
                new_length=0,
                error=f"Job {job_id} not found",
            )

        old_length = len(job.description_raw) if job.description_raw else 0
        new_length = len(new_description)

        # Only update if new description is longer
        if new_length <= old_length:
            return FetchResult(
                job_id=job_id,
                success=False,
                old_length=old_length,
                new_length=new_length,
                error=f"New description ({new_length} chars) not longer than existing ({old_length} chars)",
            )

        job.description_raw = new_description
        job.updated_at = datetime.now(timezone.utc)

        await db.flush()

        logger.info(
            "description_updated",
            job_id=str(job_id),
            old_length=old_length,
            new_length=new_length,
        )

        return FetchResult(
            job_id=job_id,
            success=True,
            old_length=old_length,
            new_length=new_length,
        )

    async def get_stats(self, db: AsyncSession) -> dict:
        """
        Get statistics about job descriptions.

        Returns:
            Dict with counts of complete, incomplete, and missing descriptions
        """
        # Total jobs
        total_query = select(func.count()).select_from(Job).where(Job.deleted_at.is_(None))
        total = await db.scalar(total_query) or 0

        # Jobs with descriptions
        with_desc_query = (
            select(func.count())
            .select_from(Job)
            .where(
                Job.deleted_at.is_(None),
                Job.description_raw.isnot(None),
                Job.description_raw != "",
            )
        )
        with_desc = await db.scalar(with_desc_query) or 0

        # Jobs with complete descriptions (>= target length)
        complete_query = (
            select(func.count())
            .select_from(Job)
            .where(
                Job.deleted_at.is_(None),
                Job.description_raw.isnot(None),
                func.length(Job.description_raw) >= self.target_length,
            )
        )
        complete = await db.scalar(complete_query) or 0

        # Jobs with incomplete descriptions (< min length but not empty)
        incomplete_query = (
            select(func.count())
            .select_from(Job)
            .where(
                Job.deleted_at.is_(None),
                Job.description_raw.isnot(None),
                Job.description_raw != "",
                func.length(Job.description_raw) < self.min_length,
            )
        )
        incomplete = await db.scalar(incomplete_query) or 0

        # Jobs without descriptions
        missing = total - with_desc

        return {
            "total_jobs": total,
            "with_descriptions": with_desc,
            "complete_descriptions": complete,
            "incomplete_descriptions": incomplete,
            "missing_descriptions": missing,
            "needs_fetch": incomplete + missing,
            "min_length_threshold": self.min_length,
            "target_length": self.target_length,
        }


# Singleton instance
description_fetcher = DescriptionFetcherService()
