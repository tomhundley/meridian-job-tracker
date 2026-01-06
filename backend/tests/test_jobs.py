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
async def test_create_job_with_salary(client, api_key_header):
    """Test creating a job with salary information."""
    payload = {
        "title": "Senior Engineer",
        "company": "TechCo",
        "salary_min": 150000,
        "salary_max": 200000,
        "salary_currency": "USD",
        "employment_type": "full_time",
    }
    response = await client.post("/api/v1/jobs", json=payload, headers=api_key_header)
    assert response.status_code == 201
    data = response.json()
    assert data["salary_min"] == 150000
    assert data["salary_max"] == 200000
    assert data["salary_currency"] == "USD"
    assert data["employment_type"] == "full_time"


@pytest.mark.asyncio
async def test_create_job_with_work_location_type(client, api_key_header):
    """Test creating a job with work location type."""
    payload = {
        "title": "Remote Developer",
        "company": "DistributedCo",
        "work_location_type": "remote",
    }
    response = await client.post("/api/v1/jobs", json=payload, headers=api_key_header)
    assert response.status_code == 201
    data = response.json()
    assert data["work_location_type"] == "remote"


@pytest.mark.asyncio
async def test_create_job_with_priority(client, api_key_header):
    """Test creating a job with custom priority."""
    payload = {
        "title": "High Priority Role",
        "company": "ImportantCo",
        "priority": 90,
    }
    response = await client.post("/api/v1/jobs", json=payload, headers=api_key_header)
    assert response.status_code == 201
    data = response.json()
    assert data["priority"] == 90


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


@pytest.mark.asyncio
async def test_filter_jobs_by_salary_min(client, api_key_header):
    """Test filtering jobs by minimum salary."""
    # Create jobs with different salary ranges
    jobs = [
        {"title": "Junior Dev", "company": "Co1", "salary_min": 50000, "salary_max": 70000},
        {"title": "Senior Dev", "company": "Co2", "salary_min": 120000, "salary_max": 150000},
        {"title": "Lead Dev", "company": "Co3", "salary_min": 180000, "salary_max": 220000},
        {"title": "No Salary", "company": "Co4"},  # No salary info
    ]
    for job in jobs:
        response = await client.post("/api/v1/jobs", json=job, headers=api_key_header)
        assert response.status_code == 201

    # Filter for jobs paying at least $100k
    response = await client.get("/api/v1/jobs?min_salary=100000", headers=api_key_header)
    assert response.status_code == 200
    data = response.json()
    # Should include Senior Dev and Lead Dev (max salary >= 100k)
    titles = [job["title"] for job in data["items"]]
    assert "Senior Dev" in titles
    assert "Lead Dev" in titles
    assert "Junior Dev" not in titles


@pytest.mark.asyncio
async def test_filter_jobs_by_salary_max(client, api_key_header):
    """Test filtering jobs by maximum salary."""
    # Create jobs with different salary ranges
    jobs = [
        {"title": "Entry Level", "company": "Startup", "salary_min": 40000, "salary_max": 60000},
        {"title": "Mid Level", "company": "MidCo", "salary_min": 80000, "salary_max": 100000},
        {"title": "Executive", "company": "BigCorp", "salary_min": 300000, "salary_max": 500000},
    ]
    for job in jobs:
        response = await client.post("/api/v1/jobs", json=job, headers=api_key_header)
        assert response.status_code == 201

    # Filter for jobs with min salary under $90k
    response = await client.get("/api/v1/jobs?max_salary=90000", headers=api_key_header)
    assert response.status_code == 200
    data = response.json()
    titles = [job["title"] for job in data["items"]]
    assert "Entry Level" in titles
    assert "Mid Level" in titles
    assert "Executive" not in titles


@pytest.mark.asyncio
async def test_filter_jobs_by_salary_range(client, api_key_header):
    """Test filtering jobs by salary range (both min and max)."""
    jobs = [
        {"title": "Low Pay", "company": "Co1", "salary_min": 30000, "salary_max": 50000},
        {"title": "Mid Pay", "company": "Co2", "salary_min": 80000, "salary_max": 120000},
        {"title": "High Pay", "company": "Co3", "salary_min": 200000, "salary_max": 300000},
    ]
    for job in jobs:
        response = await client.post("/api/v1/jobs", json=job, headers=api_key_header)
        assert response.status_code == 201

    # Filter for jobs in $70k-$150k range
    response = await client.get("/api/v1/jobs?min_salary=70000&max_salary=150000", headers=api_key_header)
    assert response.status_code == 200
    data = response.json()
    titles = [job["title"] for job in data["items"]]
    assert "Mid Pay" in titles
    assert "Low Pay" not in titles
    assert "High Pay" not in titles


@pytest.mark.asyncio
async def test_filter_jobs_by_priority(client, api_key_header):
    """Test filtering jobs by minimum priority."""
    jobs = [
        {"title": "Low Priority", "company": "Co1", "priority": 20},
        {"title": "Medium Priority", "company": "Co2", "priority": 50},
        {"title": "High Priority", "company": "Co3", "priority": 85},
    ]
    for job in jobs:
        response = await client.post("/api/v1/jobs", json=job, headers=api_key_header)
        assert response.status_code == 201

    # Filter for priority >= 50
    response = await client.get("/api/v1/jobs?min_priority=50", headers=api_key_header)
    assert response.status_code == 200
    data = response.json()
    titles = [job["title"] for job in data["items"]]
    assert "Medium Priority" in titles
    assert "High Priority" in titles
    assert "Low Priority" not in titles


@pytest.mark.asyncio
async def test_filter_jobs_by_work_location_type(client, api_key_header):
    """Test filtering jobs by work location type."""
    jobs = [
        {"title": "Remote Job", "company": "Co1", "work_location_type": "remote"},
        {"title": "Hybrid Job", "company": "Co2", "work_location_type": "hybrid"},
        {"title": "Onsite Job", "company": "Co3", "work_location_type": "on_site"},
    ]
    for job in jobs:
        response = await client.post("/api/v1/jobs", json=job, headers=api_key_header)
        assert response.status_code == 201

    # Filter for remote only
    response = await client.get("/api/v1/jobs?work_location_type=remote", headers=api_key_header)
    assert response.status_code == 200
    data = response.json()
    titles = [job["title"] for job in data["items"]]
    assert "Remote Job" in titles
    assert "Hybrid Job" not in titles
    assert "Onsite Job" not in titles


@pytest.mark.asyncio
async def test_update_job_with_salary(client, api_key_header):
    """Test updating a job with salary information."""
    # Create job without salary
    response = await client.post(
        "/api/v1/jobs",
        json={"title": "Developer", "company": "TechCo"},
        headers=api_key_header,
    )
    job_id = response.json()["id"]

    # Update with salary info
    update_response = await client.patch(
        f"/api/v1/jobs/{job_id}",
        json={
            "salary_min": 100000,
            "salary_max": 130000,
            "salary_currency": "USD",
            "employment_type": "full_time",
        },
        headers=api_key_header,
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["salary_min"] == 100000
    assert data["salary_max"] == 130000
    assert data["employment_type"] == "full_time"


@pytest.mark.asyncio
async def test_update_job_work_location_type(client, api_key_header):
    """Test updating a job's work location type."""
    # Create job
    response = await client.post(
        "/api/v1/jobs",
        json={"title": "Developer", "company": "TechCo"},
        headers=api_key_header,
    )
    job_id = response.json()["id"]

    # Update work location type
    update_response = await client.patch(
        f"/api/v1/jobs/{job_id}",
        json={"work_location_type": "hybrid"},
        headers=api_key_header,
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["work_location_type"] == "hybrid"
