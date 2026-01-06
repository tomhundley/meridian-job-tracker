"""LinkedIn job discovery service using Playwright browser automation."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from urllib.parse import quote_plus, urlencode

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class DiscoveredJob:
    """A job discovered from LinkedIn search results."""

    title: str
    company: str
    location: str | None = None
    url: str | None = None
    linkedin_job_id: str | None = None
    posted_date: str | None = None
    is_easy_apply: bool = False
    salary_info: str | None = None
    raw_data: dict[str, Any] = field(default_factory=dict)

    def to_job_create_dict(self) -> dict[str, Any]:
        """Convert to dict for JobCreate schema."""
        return {
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "url": self.url,
            "job_board": "linkedin",
            "job_board_id": self.linkedin_job_id,
            "notes": self._build_notes(),
            "tags": self._build_tags(),
        }

    def _build_notes(self) -> str | None:
        parts = []
        if self.posted_date:
            parts.append(f"Posted: {self.posted_date}")
        if self.salary_info:
            parts.append(f"Salary: {self.salary_info}")
        return " | ".join(parts) if parts else None

    def _build_tags(self) -> list[str]:
        tags = ["linkedin-discovered"]
        if self.is_easy_apply:
            tags.append("easy-apply")
        return tags


@dataclass
class LinkedInSearchParams:
    """Parameters for LinkedIn job search."""

    keywords: str
    location: str | None = None
    distance_miles: int | None = None
    job_type: list[str] | None = None  # F=Full-time, P=Part-time, C=Contract, T=Temporary, I=Internship
    experience_level: list[str] | None = None  # 1=Internship, 2=Entry, 3=Associate, 4=Mid-Senior, 5=Director, 6=Executive
    date_posted: str | None = None  # r86400=24h, r604800=week, r2592000=month
    remote: list[str] | None = None  # 1=On-site, 2=Remote, 3=Hybrid
    easy_apply: bool = False
    salary_range: str | None = None

    def build_url(self) -> str:
        """Build LinkedIn job search URL."""
        base_url = "https://www.linkedin.com/jobs/search/"
        params: dict[str, str] = {"keywords": self.keywords}

        if self.location:
            params["location"] = self.location
        if self.distance_miles:
            params["distance"] = str(self.distance_miles)
        if self.date_posted:
            params["f_TPR"] = self.date_posted
        if self.easy_apply:
            params["f_AL"] = "true"

        # Multi-value filters
        if self.job_type:
            params["f_JT"] = ",".join(self.job_type)
        if self.experience_level:
            params["f_E"] = ",".join(self.experience_level)
        if self.remote:
            params["f_WT"] = ",".join(self.remote)
        if self.salary_range:
            params["f_SB2"] = self.salary_range

        return f"{base_url}?{urlencode(params)}"


class LinkedInJobDiscovery:
    """
    LinkedIn job discovery using Playwright browser automation.

    This service is designed to work with external Playwright sessions
    (e.g., via MCP) rather than managing its own browser.
    """

    @staticmethod
    def build_search_url(
        keywords: str,
        location: str | None = None,
        experience_level: list[str] | None = None,
        date_posted: str | None = None,
        remote: list[str] | None = None,
        easy_apply: bool = False,
    ) -> str:
        """Build a LinkedIn job search URL with filters."""
        params = LinkedInSearchParams(
            keywords=keywords,
            location=location,
            experience_level=experience_level,
            date_posted=date_posted,
            remote=remote,
            easy_apply=easy_apply,
        )
        return params.build_url()

    @staticmethod
    def parse_job_card(card_text: str) -> DiscoveredJob | None:
        """
        Parse a job card from LinkedIn search results.

        Expected format from accessibility tree:
        - link "Job Title Company Location Posted Date"
        - May include "Easy Apply" indicator
        """
        if not card_text or len(card_text) < 10:
            return None

        # Extract LinkedIn job ID from URL if present
        job_id_match = re.search(r"/jobs/view/(\d+)", card_text)
        linkedin_job_id = job_id_match.group(1) if job_id_match else None

        # Try to extract URL
        url_match = re.search(r'(https://www\.linkedin\.com/jobs/view/\d+[^\s"]*)', card_text)
        url = url_match.group(1) if url_match else None
        if linkedin_job_id and not url:
            url = f"https://www.linkedin.com/jobs/view/{linkedin_job_id}/"

        # Check for Easy Apply
        is_easy_apply = "easy apply" in card_text.lower()

        # Try to parse the structured parts
        # Common patterns:
        # "Title\nCompany\nLocation\nPosted X days ago"
        # "Title at Company · Location · Posted"
        lines = [line.strip() for line in card_text.split("\n") if line.strip()]

        title = lines[0] if lines else "Unknown Title"
        company = lines[1] if len(lines) > 1 else "Unknown Company"
        location = None
        posted_date = None

        # Try to identify location and posted date from remaining lines
        for line in lines[2:]:
            lower_line = line.lower()
            if any(x in lower_line for x in ["ago", "posted", "hour", "day", "week", "month"]):
                posted_date = line
            elif any(x in lower_line for x in ["remote", "hybrid", "on-site", ","]):
                if not location:
                    location = line
            elif len(line) < 100:  # Likely location or metadata
                if not location:
                    location = line

        return DiscoveredJob(
            title=title,
            company=company,
            location=location,
            url=url,
            linkedin_job_id=linkedin_job_id,
            posted_date=posted_date,
            is_easy_apply=is_easy_apply,
            raw_data={"original_text": card_text},
        )

    @staticmethod
    def parse_search_results(snapshot_text: str) -> list[DiscoveredJob]:
        """
        Parse multiple job listings from a LinkedIn search results page snapshot.

        This parses the accessibility tree output from Playwright's snapshot.
        """
        jobs: list[DiscoveredJob] = []

        # Split by job card boundaries
        # LinkedIn job cards often start with link elements to job details
        job_pattern = re.compile(
            r'link\s+"([^"]+)".*?href.*?/jobs/view/(\d+)',
            re.IGNORECASE | re.DOTALL
        )

        for match in job_pattern.finditer(snapshot_text):
            title_text = match.group(1)
            job_id = match.group(2)

            # Try to extract more context around this match
            start = max(0, match.start() - 50)
            end = min(len(snapshot_text), match.end() + 200)
            context = snapshot_text[start:end]

            job = LinkedInJobDiscovery.parse_job_card(context)
            if job:
                job.linkedin_job_id = job_id
                job.url = f"https://www.linkedin.com/jobs/view/{job_id}/"
                # Use title from link text if we got a good one
                if title_text and len(title_text) > 3:
                    job.title = title_text.split("\n")[0].strip()
                jobs.append(job)

        # Deduplicate by job ID
        seen_ids: set[str | None] = set()
        unique_jobs: list[DiscoveredJob] = []
        for job in jobs:
            if job.linkedin_job_id not in seen_ids:
                seen_ids.add(job.linkedin_job_id)
                unique_jobs.append(job)

        logger.info(
            "linkedin_search_parsed",
            total_found=len(jobs),
            unique_jobs=len(unique_jobs),
        )
        return unique_jobs

    @staticmethod
    def parse_job_list_items(items: list[dict[str, Any]]) -> list[DiscoveredJob]:
        """
        Parse job listings from structured data (e.g., from scraping).

        Expected item format:
        {
            "title": "Job Title",
            "company": "Company Name",
            "location": "Location",
            "url": "https://linkedin.com/jobs/view/123",
            "posted": "2 days ago",
            "easy_apply": True
        }
        """
        jobs: list[DiscoveredJob] = []

        for item in items:
            job_id = None
            url = item.get("url", "")
            if url:
                id_match = re.search(r"/jobs/view/(\d+)", url)
                if id_match:
                    job_id = id_match.group(1)

            job = DiscoveredJob(
                title=item.get("title", "Unknown"),
                company=item.get("company", "Unknown"),
                location=item.get("location"),
                url=url,
                linkedin_job_id=job_id,
                posted_date=item.get("posted"),
                is_easy_apply=item.get("easy_apply", False),
                salary_info=item.get("salary"),
                raw_data=item,
            )
            jobs.append(job)

        return jobs


# Convenience instance
linkedin_discovery = LinkedInJobDiscovery()
