"""Job scraping and parsing utilities."""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Any
from urllib.parse import parse_qs, urlparse

import httpx
from bs4 import BeautifulSoup
import structlog


class JobScrapeError(ValueError):
    """Raised when a job cannot be scraped or parsed."""


@dataclass(frozen=True)
class ScrapedJob:
    """Parsed job details from a URL."""

    title: str
    company: str
    location: str | None
    description: str | None
    source: str
    source_id: str | None
    raw_html: str


SUPPORTED_SOURCES = {"linkedin", "indeed", "greenhouse", "lever", "workday"}


def _clean_text(value: str | None) -> str | None:
    if not value:
        return None
    return re.sub(r"\s+", " ", value).strip()


def _select_text(soup: BeautifulSoup, selectors: list[str]) -> str | None:
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            text = _clean_text(element.get_text(" ", strip=True))
            if text:
                return text
    return None


def _meta_content(soup: BeautifulSoup, selectors: list[str]) -> str | None:
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            content = element.get("content")
            if content:
                return _clean_text(content)
    return None


def _iter_json_ld(data: Any) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    if isinstance(data, list):
        for item in data:
            items.extend(_iter_json_ld(item))
    elif isinstance(data, dict):
        if "@graph" in data:
            items.extend(_iter_json_ld(data["@graph"]))
        else:
            items.append(data)
    return items


def _extract_job_posting(soup: BeautifulSoup) -> dict[str, Any] | None:
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        if not script.string:
            continue
        try:
            data = json.loads(script.string)
        except json.JSONDecodeError:
            continue
        for item in _iter_json_ld(data):
            item_type = item.get("@type")
            if item_type == "JobPosting" or (
                isinstance(item_type, list) and "JobPosting" in item_type
            ):
                return item
    return None


def _extract_location(job_posting: dict[str, Any]) -> str | None:
    location = job_posting.get("jobLocation")
    if isinstance(location, list) and location:
        location = location[0]
    if isinstance(location, dict):
        address = location.get("address")
        if isinstance(address, dict):
            parts = [
                address.get("addressLocality"),
                address.get("addressRegion"),
                address.get("addressCountry"),
            ]
            return _clean_text(", ".join([part for part in parts if part]))
        if isinstance(address, str):
            return _clean_text(address)
    return None


def detect_source(url: str) -> str | None:
    host = urlparse(url).netloc.lower()
    if "linkedin.com" in host:
        return "linkedin"
    if "indeed.com" in host:
        return "indeed"
    if "greenhouse.io" in host:
        return "greenhouse"
    if "lever.co" in host:
        return "lever"
    if "workday" in host:
        return "workday"
    return None


def extract_source_id(url: str, source: str) -> str | None:
    parsed = urlparse(url)
    if source == "linkedin":
        match = re.search(r"/jobs/view/(\d+)", parsed.path)
        if match:
            return match.group(1)
        query = parse_qs(parsed.query)
        if "currentJobId" in query:
            return query["currentJobId"][0]
    if source == "indeed":
        query = parse_qs(parsed.query)
        if "jk" in query:
            return query["jk"][0]
        match = re.search(r"jk=([a-zA-Z0-9]+)", url)
        if match:
            return match.group(1)
    if source == "greenhouse":
        match = re.search(r"/jobs/(\d+)", parsed.path)
        if match:
            return match.group(1)
    if source == "lever":
        segments = [segment for segment in parsed.path.split("/") if segment]
        if len(segments) >= 2:
            return segments[-1]
    if source == "workday":
        query = parse_qs(parsed.query)
        for key in ("jobId", "jobid", "job_id"):
            if key in query:
                return query[key][0]
        match = re.search(r"_([A-Za-z0-9-]+)$", parsed.path)
        if match:
            return match.group(1)
    return None


def _fallback_parse(soup: BeautifulSoup, source: str) -> tuple[str | None, str | None, str | None, str | None]:
    if source == "linkedin":
        title = _select_text(
            soup,
            [
                "h1.top-card-layout__title",
                "h1.topcard__title",
                "h1",
            ],
        )
        company = _select_text(
            soup,
            [
                "a.topcard__org-name-link",
                "span.topcard__flavor",
                "a.top-card-layout__company-name",
            ],
        )
        location = _select_text(
            soup,
            [
                "span.topcard__flavor--bullet",
                "span.top-card-layout__first-subline",
            ],
        )
        description = _select_text(
            soup,
            [
                "div.show-more-less-html__markup",
                "div.description__text",
            ],
        )
        return title, company, location, description

    if source == "indeed":
        title = _select_text(soup, ["h1.jobsearch-JobInfoHeader-title", "h1"])
        company = _select_text(
            soup,
            ["div[data-testid='inlineHeader-companyName']", "span.companyName"],
        )
        location = _select_text(
            soup,
            ["div[data-testid='inlineHeader-companyLocation']", "div.companyLocation"],
        )
        description = _select_text(soup, ["div#jobDescriptionText"])
        return title, company, location, description

    if source == "greenhouse":
        title = _select_text(soup, ["h1.app-title", "h1"])
        company = _select_text(soup, ["div.company-name"])
        if not company:
            company = _meta_content(soup, ["meta[property='og:site_name']"])
        location = _select_text(soup, ["div.location", "div.location span"])
        description = _select_text(soup, ["div#content", "div.section-wrapper"])
        return title, company, location, description

    if source == "lever":
        title = _select_text(soup, ["h2.posting-headline", "h1.posting-headline", "h1"])
        company = _meta_content(soup, ["meta[property='og:site_name']"])
        location = _select_text(soup, ["div.posting-categories", "div.location"])
        description = _select_text(soup, ["div.posting-section", "div.section-wrapper"])
        return title, company, location, description

    if source == "workday":
        title = _select_text(soup, ["h2", "h1"])
        company = _meta_content(soup, ["meta[property='og:site_name']"])
        location = _select_text(soup, ["div[data-automation-id='location']", "span.location"])
        description = _select_text(soup, ["div[data-automation-id='jobDescription']", "div.jobDescription"])
        return title, company, location, description

    return None, None, None, None


logger = structlog.get_logger(__name__)


class JobScraper:
    """Scrape and parse job postings."""

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client

    async def fetch_html(self, url: str) -> str:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; MeridianJobTracker/1.0)",
        }
        timeout = httpx.Timeout(20.0, connect=10.0)
        if self._client:
            response = await self._client.get(url, headers=headers, follow_redirects=True, timeout=timeout)
        else:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, follow_redirects=True, timeout=timeout)
        response.raise_for_status()
        return response.text

    def parse(self, url: str, html: str, source: str | None = None) -> ScrapedJob:
        resolved_source = (source or detect_source(url) or "").lower()
        if resolved_source not in SUPPORTED_SOURCES:
            raise JobScrapeError("Unsupported job board URL")

        soup = BeautifulSoup(html, "html.parser")
        job_posting = _extract_job_posting(soup)

        title = None
        company = None
        location = None
        description = None

        if job_posting:
            title = _clean_text(job_posting.get("title"))
            description_value = job_posting.get("description")
            if isinstance(description_value, str):
                description = _clean_text(
                    BeautifulSoup(description_value, "html.parser").get_text(" ", strip=True)
                )
            org = job_posting.get("hiringOrganization")
            if isinstance(org, dict):
                company = _clean_text(org.get("name"))
            location = _extract_location(job_posting)

        if not title:
            title = _meta_content(soup, ["meta[property='og:title']", "meta[name='twitter:title']"])
        if not description:
            description = _meta_content(soup, ["meta[property='og:description']", "meta[name='description']"])

        if not any([title, company, location, description]):
            title, company, location, description = _fallback_parse(soup, resolved_source)
        else:
            fallback_title, fallback_company, fallback_location, fallback_description = _fallback_parse(
                soup,
                resolved_source,
            )
            title = title or fallback_title
            company = company or fallback_company
            location = location or fallback_location
            description = description or fallback_description

        title = _clean_text(title) or ""
        company = _clean_text(company) or ""
        location = _clean_text(location)
        description = _clean_text(description)

        if not title or not company:
            raise JobScrapeError("Failed to parse job title or company")

        return ScrapedJob(
            title=title,
            company=company,
            location=location,
            description=description,
            source=resolved_source,
            source_id=extract_source_id(url, resolved_source),
            raw_html=html,
        )

    async def scrape(self, url: str, source: str | None = None) -> ScrapedJob:
        logger.info("job_scrape_start", url=url, source=source)
        html = await self.fetch_html(url)
        scraped = self.parse(url, html, source)
        logger.info(
            "job_scrape_success",
            url=url,
            source=scraped.source,
            source_id=scraped.source_id,
        )
        return scraped


job_scraper = JobScraper()
