#!/usr/bin/env python3
"""Reprocess all jobs to detect and set Easy Apply status."""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, update
from src.config.database import AsyncSessionLocal
from src.models.job import Job
from src.services.job_scraper import JobScraper, detect_source


async def reprocess_jobs():
    """Re-scrape all LinkedIn jobs and update Easy Apply status."""
    scraper = JobScraper()

    async with AsyncSessionLocal() as session:
        # Get all jobs with URLs
        result = await session.execute(
            select(Job).where(Job.url.isnot(None))
        )
        jobs = result.scalars().all()

        print(f"Found {len(jobs)} jobs with URLs")

        linkedin_count = 0
        updated_count = 0
        easy_apply_count = 0
        errors = []

        for job in jobs:
            source = detect_source(job.url)
            if source != "linkedin":
                continue

            linkedin_count += 1
            print(f"\nProcessing: {job.title} at {job.company}")
            print(f"  URL: {job.url}")

            try:
                scraped = await scraper.scrape(job.url)

                if scraped.is_easy_apply != job.is_easy_apply:
                    print(f"  Updating is_easy_apply: {job.is_easy_apply} -> {scraped.is_easy_apply}")
                    await session.execute(
                        update(Job)
                        .where(Job.id == job.id)
                        .values(is_easy_apply=scraped.is_easy_apply)
                    )
                    updated_count += 1
                else:
                    print(f"  is_easy_apply unchanged: {job.is_easy_apply}")

                if scraped.is_easy_apply:
                    easy_apply_count += 1

            except Exception as e:
                print(f"  ERROR: {e}")
                errors.append((job.title, job.company, str(e)))

        await session.commit()

        print("\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)
        print(f"Total jobs with URLs: {len(jobs)}")
        print(f"LinkedIn jobs processed: {linkedin_count}")
        print(f"Jobs updated: {updated_count}")
        print(f"Easy Apply jobs found: {easy_apply_count}")

        if errors:
            print(f"\nErrors ({len(errors)}):")
            for title, company, error in errors:
                print(f"  - {title} at {company}: {error}")


if __name__ == "__main__":
    asyncio.run(reprocess_jobs())
