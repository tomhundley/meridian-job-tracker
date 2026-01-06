"""Tests for job endpoints."""

import pytest

from src.services.job_scraper import ScrapedJob
from src.services import job_scraper


@pytest.mark.asyncio
async def test_create_job(client, api_key_header):
    payload = {"title": "Engineer", "company": "Acme"}
    response = await client.post("/api/v1/jobs", json=payload, headers=api_key_header)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Engineer"
    assert data["company"] == "Acme"


@pytest.mark.asyncio
async def test_ingest_job(monkeypatch, client, api_key_header):
    async def fake_scrape(url: str, source: str | None = None):
        return ScrapedJob(
            title="Platform Engineer",
            company="Acme Corp",
            location="Remote",
            description="Build infrastructure.",
            source=source or "linkedin",
            source_id="123",
            raw_html="<html></html>",
        )

    monkeypatch.setattr(job_scraper, "scrape", fake_scrape)

    payload = {"url": "https://linkedin.com/jobs/view/123", "source": "linkedin"}
    response = await client.post("/api/v1/jobs/ingest", json=payload, headers=api_key_header)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Platform Engineer"
    assert data["company"] == "Acme Corp"


@pytest.mark.asyncio
async def test_bulk_status_update(client, api_key_header):
    job_ids = []
    for idx in range(2):
        payload = {"title": f"Engineer {idx}", "company": "Acme"}
        response = await client.post("/api/v1/jobs", json=payload, headers=api_key_header)
        assert response.status_code == 201
        job_ids.append(response.json()["id"])

    response = await client.patch(
        "/api/v1/jobs/bulk/status",
        json={"job_ids": job_ids, "status": "applied"},
        headers=api_key_header,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["updated"]) == 2
    assert data["updated"][0]["status"] == "applied"


@pytest.mark.asyncio
async def test_delete_job(client, api_key_header):
    response = await client.post(
        "/api/v1/jobs",
        json={"title": "Engineer", "company": "Acme"},
        headers=api_key_header,
    )
    job_id = response.json()["id"]

    delete_response = await client.delete(f"/api/v1/jobs/{job_id}", headers=api_key_header)
    assert delete_response.status_code == 204

    get_response = await client.get(f"/api/v1/jobs/{job_id}", headers=api_key_header)
    assert get_response.status_code == 404
