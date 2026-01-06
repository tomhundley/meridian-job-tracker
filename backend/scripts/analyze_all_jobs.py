#!/usr/bin/env python3
"""Run analysis on all jobs and update their fit scores."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from src.config.database import AsyncSessionLocal
from src.models.job import Job, RoleType
from src.services import analyze_job


async def analyze_all_jobs():
    """Analyze all jobs and update their priority, is_ai_forward, and target_role."""
    async with AsyncSessionLocal() as session:
        # Get all jobs with descriptions
        result = await session.execute(
            select(Job).where(
                Job.deleted_at.is_(None),
                Job.description_raw.isnot(None),
            ).order_by(Job.created_at.desc())
        )
        jobs = list(result.scalars().all())

        print("=" * 70)
        print(f"ANALYZING {len(jobs)} JOBS")
        print("=" * 70)

        updated = 0
        ai_forward_count = 0
        errors = 0

        for job in jobs:
            try:
                analysis = analyze_job(
                    description=job.description_raw,
                    title=job.title,
                    company=job.company,
                )

                # Track changes
                changes = []

                if job.priority != analysis.suggested_priority:
                    changes.append(f"priority: {job.priority} → {analysis.suggested_priority}")
                    job.priority = analysis.suggested_priority

                if job.is_ai_forward != analysis.is_ai_forward:
                    changes.append(f"ai_forward: {job.is_ai_forward} → {analysis.is_ai_forward}")
                    job.is_ai_forward = analysis.is_ai_forward

                if analysis.suggested_role and job.target_role != analysis.suggested_role:
                    old_role = job.target_role.value if job.target_role else "None"
                    changes.append(f"role: {old_role} → {analysis.suggested_role.value}")
                    job.target_role = analysis.suggested_role

                if analysis.is_ai_forward:
                    ai_forward_count += 1

                if changes:
                    updated += 1
                    print(f"\n{job.title} @ {job.company}")
                    print(f"  Changes: {', '.join(changes)}")
                    if analysis.analysis_notes:
                        print(f"  Notes: {', '.join(analysis.analysis_notes)}")
                else:
                    print(f"✓ {job.title} @ {job.company} (no changes)")

            except Exception as e:
                print(f"✗ {job.title} @ {job.company}: ERROR - {e}")
                errors += 1

        await session.commit()

        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Total analyzed: {len(jobs)}")
        print(f"Jobs updated: {updated}")
        print(f"AI-forward jobs: {ai_forward_count}")
        print(f"Errors: {errors}")


if __name__ == "__main__":
    asyncio.run(analyze_all_jobs())
