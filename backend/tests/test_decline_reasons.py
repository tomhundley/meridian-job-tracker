"""Tests for decline reasons API endpoints and job decline functionality."""

import pytest


@pytest.mark.asyncio
async def test_list_user_decline_reasons(client, api_key_header):
    """Test listing user decline reasons grouped by category."""
    response = await client.get("/api/v1/decline-reasons/user", headers=api_key_header)
    assert response.status_code == 200
    data = response.json()

    assert "categories" in data
    categories = data["categories"]
    assert len(categories) > 0

    # Check structure of a category
    category = categories[0]
    assert "name" in category
    assert "display_name" in category
    assert "reasons" in category
    assert len(category["reasons"]) > 0

    # Check structure of a reason
    reason = category["reasons"][0]
    assert "code" in reason
    assert "display_name" in reason


@pytest.mark.asyncio
async def test_list_company_decline_reasons(client, api_key_header):
    """Test listing company decline reasons grouped by category."""
    response = await client.get("/api/v1/decline-reasons/company", headers=api_key_header)
    assert response.status_code == 200
    data = response.json()

    assert "categories" in data
    categories = data["categories"]
    assert len(categories) > 0


@pytest.mark.asyncio
async def test_update_job_with_user_decline_reasons(client, api_key_header, test_job_payload):
    """Test updating a job with user decline reasons."""
    # Create a job
    job_response = await client.post(
        "/api/v1/jobs",
        json=test_job_payload(title="Engineer", company="Test Co"),
        headers=api_key_header,
    )
    assert job_response.status_code == 201
    job_id = job_response.json()["id"]

    # Update job status to withdrawn and add decline reasons via status endpoint
    update_response = await client.patch(
        f"/api/v1/jobs/{job_id}/status",
        json={
            "status": "withdrawn",
            "user_decline_reasons": ["salary_too_low", "not_remote"],
            "decline_notes": "Compensation was below market rate",
        },
        headers=api_key_header,
    )
    assert update_response.status_code == 200
    data = update_response.json()

    assert data["status"] == "withdrawn"
    assert data["user_decline_reasons"] == ["salary_too_low", "not_remote"]
    assert data["decline_notes"] == "Compensation was below market rate"


@pytest.mark.asyncio
async def test_update_job_with_company_decline_reasons(client, api_key_header, test_job_payload):
    """Test updating a job with company decline reasons."""
    # Create a job
    job_response = await client.post(
        "/api/v1/jobs",
        json=test_job_payload(title="Engineer", company="Test Co"),
        headers=api_key_header,
    )
    assert job_response.status_code == 201
    job_id = job_response.json()["id"]

    # Update job status to rejected and add company decline reasons via status endpoint
    update_response = await client.patch(
        f"/api/v1/jobs/{job_id}/status",
        json={
            "status": "rejected",
            "company_decline_reasons": ["selected_other", "insufficient_experience"],
            "decline_notes": "They went with an internal candidate",
        },
        headers=api_key_header,
    )
    assert update_response.status_code == 200
    data = update_response.json()

    assert data["status"] == "rejected"
    assert data["company_decline_reasons"] == ["selected_other", "insufficient_experience"]
    assert data["decline_notes"] == "They went with an internal candidate"


@pytest.mark.asyncio
async def test_clear_decline_reasons(client, api_key_header, test_job_payload):
    """Test clearing decline reasons from a job."""
    # Create a job with decline reasons
    job_response = await client.post(
        "/api/v1/jobs",
        json=test_job_payload(title="Engineer", company="Test Co"),
        headers=api_key_header,
    )
    job_id = job_response.json()["id"]

    # Add decline reasons via status endpoint
    await client.patch(
        f"/api/v1/jobs/{job_id}/status",
        json={
            "status": "withdrawn",
            "user_decline_reasons": ["salary_too_low"],
        },
        headers=api_key_header,
    )

    # Clear decline reasons via general update
    update_response = await client.patch(
        f"/api/v1/jobs/{job_id}",
        json={
            "user_decline_reasons": None,
            "decline_notes": None,
        },
        headers=api_key_header,
    )
    assert update_response.status_code == 200
    data = update_response.json()

    assert data["user_decline_reasons"] is None
    assert data["decline_notes"] is None


@pytest.mark.asyncio
async def test_job_response_includes_decline_fields(client, api_key_header, test_job_payload):
    """Test that job GET response includes decline reason fields."""
    # Create a job
    job_response = await client.post(
        "/api/v1/jobs",
        json=test_job_payload(title="Engineer", company="Test Co"),
        headers=api_key_header,
    )
    job_id = job_response.json()["id"]

    # Fetch the job
    get_response = await client.get(f"/api/v1/jobs/{job_id}", headers=api_key_header)
    assert get_response.status_code == 200
    data = get_response.json()

    # Verify decline fields are present (even if null)
    assert "user_decline_reasons" in data
    assert "company_decline_reasons" in data
    assert "decline_notes" in data
