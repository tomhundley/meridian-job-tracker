"""Tests for job scraping/parsing."""

import pytest

from src.services.job_scraper import JobScraper, JobScrapeError


def test_parse_json_ld_job_posting():
    html = """
    <html>
      <head>
        <script type="application/ld+json">
          {
            "@context": "http://schema.org",
            "@type": "JobPosting",
            "title": "Senior Engineer",
            "description": "<p>Build reliable systems.</p>",
            "hiringOrganization": {"name": "Acme Corp"},
            "jobLocation": {"address": {"addressLocality": "Austin", "addressRegion": "TX", "addressCountry": "US"}}
          }
        </script>
      </head>
      <body></body>
    </html>
    """
    scraper = JobScraper()
    result = scraper.parse("https://linkedin.com/jobs/view/123", html, source="linkedin")
    assert result.title == "Senior Engineer"
    assert result.company == "Acme Corp"
    assert result.location == "Austin, TX, US"
    assert "Build reliable systems." in (result.description or "")


def test_parse_requires_title_and_company():
    html = "<html><head><meta property='og:title' content='Role'></head><body></body></html>"
    scraper = JobScraper()
    with pytest.raises(JobScrapeError):
        scraper.parse("https://indeed.com/viewjob?jk=abc", html, source="indeed")
