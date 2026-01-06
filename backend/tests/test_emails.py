"""Tests for email endpoints."""

import datetime

import pytest


@pytest.mark.asyncio
async def test_create_and_link_email(client, api_key_header):
    job_response = await client.post(
        "/api/v1/jobs",
        json={"title": "Engineer", "company": "Acme"},
        headers=api_key_header,
    )
    job_id = job_response.json()["id"]

    payload = {
        "from_email": "recruiter@example.com",
        "to_email": "candidate@example.com",
        "subject": "Interview",
        "body": "Let's schedule time.",
        "email_timestamp": datetime.datetime.utcnow().isoformat(),
        "is_inbound": True,
    }
    response = await client.post("/api/v1/emails", json=payload, headers=api_key_header)
    assert response.status_code == 201
    email_id = response.json()["id"]

    link_response = await client.patch(
        f"/api/v1/emails/{email_id}/link/{job_id}",
        headers=api_key_header,
    )
    assert link_response.status_code == 200
    assert link_response.json()["job_id"] == job_id


@pytest.mark.asyncio
async def test_delete_email(client, api_key_header):
    payload = {
        "from_email": "recruiter@example.com",
        "to_email": "candidate@example.com",
        "subject": "Interview",
        "body": "Let's schedule time.",
        "email_timestamp": datetime.datetime.utcnow().isoformat(),
        "is_inbound": True,
    }
    response = await client.post("/api/v1/emails", json=payload, headers=api_key_header)
    email_id = response.json()["id"]

    delete_response = await client.delete(f"/api/v1/emails/{email_id}", headers=api_key_header)
    assert delete_response.status_code == 204

    get_response = await client.get(f"/api/v1/emails/{email_id}", headers=api_key_header)
    assert get_response.status_code == 404
