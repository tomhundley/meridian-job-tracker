#!/usr/bin/env python3
"""Bulk add Easy Apply jobs from LinkedIn."""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, update
from src.config.database import AsyncSessionLocal
from src.models.job import Job, EmploymentType, WorkLocationType
from src.services.job_scraper import JobScraper
from src.services import analyze_job

# Easy Apply job IDs from LinkedIn search (last 30 days, exec roles)
EASY_APPLY_JOB_IDS = [
    # Page 1
    "4342261730",  # VP Software Engineering - Alined Consulting Group - Milwaukee
    "4342978977",  # Director of Engineering - BrightHire Search Partners - Nashville
    "3750102461",  # CTO (Co-Founder) - Parkspot.ai - Remote
    "4342824379",  # Head of Solution Consulting - Engage PSG Search - Remote
    "4348867132",  # VP Software Engineering - 2X - Remote
    "4344017550",  # Director of Technology - Walker Glass Company Ltd
    "4328625350",  # VP Software Private Equity - Confidential - Atlanta
    # Additional exec roles
    "4346969467",  # VP Technical Operations - Undisclosed - Remote
    "4345697983",  # Managing Director Head of Technology - Selby Jennings
    "4327234052",  # SVP Technology & Innovation - Confidential
    "4346271377",  # VP Information Systems - Franklin Fitch - Atlanta
    "4330029605",  # Fractional CTO - Nest Navigate - Remote
]


async def bulk_add_jobs():
    """Add jobs and mark them as Easy Apply."""
    scraper = JobScraper()

    async with AsyncSessionLocal() as session:
        added = 0
        skipped = 0
        failed = 0

        for job_id in EASY_APPLY_JOB_IDS:
            url = f"https://www.linkedin.com/jobs/view/{job_id}"

            # Check if already exists
            existing = await session.execute(
                select(Job).where(
                    Job.job_board == "linkedin",
                    Job.job_board_id == job_id,
                    Job.deleted_at.is_(None),
                )
            )
            if existing.scalar_one_or_none():
                print(f"SKIP (exists): {job_id}")
                skipped += 1
                continue

            try:
                print(f"Scraping: {url}")
                scraped = await scraper.scrape(url)

                # Clean up title (remove "Company hiring ... | LinkedIn" format)
                title = scraped.title
                if " hiring " in title and " | LinkedIn" in title:
                    title = title.split(" hiring ")[1].split(" in ")[0]
                elif " | LinkedIn" in title:
                    title = title.replace(" | LinkedIn", "")

                # Parse posted_at date if available
                posted_at = None
                if scraped.posted_at:
                    try:
                        posted_at = datetime.fromisoformat(scraped.posted_at.replace("Z", "+00:00"))
                    except ValueError:
                        pass

                # Map employment type string to enum
                employment_type = None
                if scraped.employment_type:
                    try:
                        employment_type = EmploymentType(scraped.employment_type)
                    except ValueError:
                        pass

                # Map work location type string to enum
                work_location_type = None
                if scraped.work_location_type:
                    try:
                        work_location_type = WorkLocationType(scraped.work_location_type)
                    except ValueError:
                        pass

                job = Job(
                    title=title,
                    company=scraped.company,
                    location=scraped.location,
                    url=url,
                    job_board="linkedin",
                    job_board_id=job_id,
                    description_raw=scraped.description,
                    source_html=scraped.raw_html,
                    is_easy_apply=True,  # Force True since we found these in Easy Apply search
                    salary_min=scraped.salary_min,
                    salary_max=scraped.salary_max,
                    salary_currency=scraped.salary_currency or "USD",
                    employment_type=employment_type,
                    work_location_type=work_location_type,
                    posted_at=posted_at,
                )

                # Run job analysis to set priority, is_ai_forward, and target_role
                if scraped.description:
                    try:
                        analysis = analyze_job(
                            description=scraped.description,
                            title=title,
                            company=scraped.company,
                        )
                        job.priority = analysis.suggested_priority
                        job.is_ai_forward = analysis.is_ai_forward
                        if analysis.suggested_role:
                            job.target_role = analysis.suggested_role
                    except Exception as analysis_error:
                        print(f"  Analysis warning: {analysis_error}")

                session.add(job)
                await session.flush()

                # Log what we captured
                details = []
                if scraped.salary_min or scraped.salary_max:
                    details.append(f"${scraped.salary_min or '?'}-${scraped.salary_max or '?'}")
                if work_location_type:
                    details.append(work_location_type.value)
                if employment_type:
                    details.append(employment_type.value)
                details.append(f"priority={job.priority}")
                if job.is_ai_forward:
                    details.append("AI-forward")
                if job.target_role:
                    details.append(f"role={job.target_role.value}")

                details_str = f" ({', '.join(details)})" if details else ""
                print(f"  ADDED: {title} at {scraped.company}{details_str}")
                added += 1

            except Exception as e:
                print(f"  FAILED: {e}")
                failed += 1

        await session.commit()

        print("\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)
        print(f"Added: {added}")
        print(f"Skipped (already exist): {skipped}")
        print(f"Failed: {failed}")


if __name__ == "__main__":
    asyncio.run(bulk_add_jobs())
