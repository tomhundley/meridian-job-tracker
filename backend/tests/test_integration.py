"""Integration tests for end-to-end flow."""

import datetime

import pytest

from src.services import cover_letter_service
from src.models.job import RoleType


@pytest.mark.asyncio
async def test_full_job_flow(monkeypatch, client, api_key_header, test_job_payload):
    async def fake_generate(*_args, **_kwargs):
        return {
            "content": "Cover letter",
            "target_role": RoleType.CTO,
            "generation_prompt": "prompt",
            "model_used": "test-model",
        }

    monkeypatch.setattr(cover_letter_service, "generate", fake_generate)

    job_response = await client.post(
        "/api/v1/jobs",
        json=test_job_payload(title="Engineer", company="Acme"),
        headers=api_key_header,
    )
    job_id = job_response.json()["id"]

    email_payload = {
        "from_email": "recruiter@example.com",
        "to_email": "candidate@example.com",
        "subject": "Interview",
        "body": "Let's schedule time.",
        "email_timestamp": datetime.datetime.utcnow().isoformat(),
        "is_inbound": True,
        "job_id": job_id,
    }
    email_response = await client.post("/api/v1/emails", json=email_payload, headers=api_key_header)
    assert email_response.status_code == 201

    cover_response = await client.post(
        f"/api/v1/jobs/{job_id}/cover-letter",
        json={"target_role": "cto"},
        headers=api_key_header,
    )
    assert cover_response.status_code == 201

    status_response = await client.patch(
        f"/api/v1/jobs/{job_id}/status",
        json={"status": "applied"},
        headers=api_key_header,
    )
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "applied"
