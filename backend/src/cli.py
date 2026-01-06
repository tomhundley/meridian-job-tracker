"""CLI commands for Meridian Job Tracker."""

import asyncio
from uuid import UUID

import typer
from rich.console import Console
from sqlalchemy import select, update, func

from src.automation.linkedin_apply import LinkedInApply
from src.config.database import AsyncSessionLocal
from src.models import Job, JobStatus, RoleType, CoverLetter
from src.services import job_scraper, cover_letter_service

app = typer.Typer()
console = Console()


def _parse_role(role: str | None) -> RoleType | None:
    if not role:
        return None
    normalized = role.lower()
    for value in RoleType:
        if value.value == normalized:
            return value
    raise typer.BadParameter(f"Unknown role: {role}")


def _parse_status(status: str | None) -> JobStatus | None:
    if not status:
        return None
    normalized = status.lower()
    for value in JobStatus:
        if value.value == normalized:
            return value
    raise typer.BadParameter(f"Unknown status: {status}")


@app.command()
def add_job(url: str, role: str | None = None, source: str | None = None, notes: str | None = None):
    """Add a job from URL."""
    target_role = _parse_role(role)

    async def _run() -> None:
        async with AsyncSessionLocal() as session:
            scraped = await job_scraper.scrape(url, source)
            if scraped.source_id:
                query = select(Job).where(
                    Job.job_board == scraped.source,
                    Job.job_board_id == scraped.source_id,
                    Job.deleted_at.is_(None),
                )
            else:
                query = select(Job).where(Job.url == url, Job.deleted_at.is_(None))
            existing = (await session.execute(query)).scalar_one_or_none()
            if existing:
                console.print("[yellow]Job already exists.[/yellow]")
                return

            job = Job(
                title=scraped.title,
                company=scraped.company,
                location=scraped.location,
                url=url,
                job_board=source or scraped.source,
                job_board_id=scraped.source_id,
                description_raw=scraped.description,
                source_html=scraped.raw_html,
                target_role=target_role,
                notes=notes,
            )
            session.add(job)
            await session.commit()
            await session.refresh(job)

            console.print(f"[green]Created job {job.id}[/green] {job.title} at {job.company}")

    asyncio.run(_run())


@app.command()
def list_jobs(status: str | None = None, limit: int = 10):
    """List jobs with optional status filter."""
    status_value = _parse_status(status)

    async def _run() -> None:
        async with AsyncSessionLocal() as session:
            query = select(Job).where(Job.deleted_at.is_(None)).order_by(Job.created_at.desc()).limit(limit)
            if status_value:
                query = query.where(Job.status == status_value)
            result = await session.execute(query)
            jobs = result.scalars().all()
            if not jobs:
                console.print("[yellow]No jobs found.[/yellow]")
                return
            for job in jobs:
                console.print(f"{job.id} | {job.title} | {job.company} | {job.status.value}")

    asyncio.run(_run())


@app.command()
def generate_cover_letter(job_id: str, role: str):
    """Generate cover letter for a job."""
    target_role = _parse_role(role)
    if not target_role:
        raise typer.BadParameter("Role is required for cover letter generation.")

    async def _run() -> None:
        async with AsyncSessionLocal() as session:
            job = await session.get(Job, UUID(job_id))
            if not job or job.deleted_at is not None:
                console.print("[red]Job not found.[/red]")
                return

            generation_result = await cover_letter_service.generate(
                job=job,
                target_role=target_role,
            )

            version_query = select(func.coalesce(func.max(CoverLetter.version), 0)).where(
                CoverLetter.job_id == job.id,
                CoverLetter.deleted_at.is_(None),
            )
            current_version = await session.scalar(version_query) or 0

            await session.execute(
                update(CoverLetter)
                .where(CoverLetter.job_id == job.id, CoverLetter.is_current == True)
                .values(is_current=False)
            )

            cover_letter = CoverLetter(
                job_id=job.id,
                content=generation_result["content"],
                target_role=generation_result["target_role"],
                generation_prompt=generation_result["generation_prompt"],
                model_used=generation_result["model_used"],
                version=current_version + 1,
                is_current=True,
            )
            session.add(cover_letter)
            await session.commit()
            await session.refresh(cover_letter)

            console.print(f"[green]Generated cover letter {cover_letter.id}[/green]")

    asyncio.run(_run())


@app.command()
def apply(job_id: str, dry_run: bool = True):
    """Start LinkedIn Easy Apply automation."""

    async def _run() -> None:
        async with AsyncSessionLocal() as session:
            job = await session.get(Job, UUID(job_id))
            if not job or job.deleted_at is not None:
                console.print("[red]Job not found.[/red]")
                return
            if not job.url:
                console.print("[red]Job URL missing; cannot apply.[/red]")
                return

        apply_service = LinkedInApply()
        result = await apply_service.apply(job.url, auto_submit=not dry_run)

        if result.success:
            console.print(f"[green]Application completed for {result.job_title or job.url}[/green]")
        else:
            console.print(f"[red]Application failed[/red] {result.error_message}")

    asyncio.run(_run())


if __name__ == "__main__":
    app()
