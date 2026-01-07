"""Tests for cover letter endpoints."""

import pytest

from src.services import cover_letter_service
from src.models.job import RoleType


@pytest.mark.asyncio
async def test_generate_cover_letter(monkeypatch, client, api_key_header, test_job_payload):
    async def fake_generate(*_args, **_kwargs):
        return {
            "content": "Dear Hiring Manager, ...",
            "target_role": RoleType.CTO,
            "generation_prompt": "prompt",
            "model_used": "test-model",
            "rag_evidence": None,
            "rag_context_used": False,
        }

    monkeypatch.setattr(cover_letter_service, "generate", fake_generate)

    job_response = await client.post(
        "/api/v1/jobs",
        json=test_job_payload(title="Engineer", company="Acme"),
        headers=api_key_header,
    )
    job_id = job_response.json()["id"]

    response = await client.post(
        f"/api/v1/jobs/{job_id}/cover-letter",
        json={"target_role": "cto"},
        headers=api_key_header,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["content"].startswith("Dear Hiring Manager")


@pytest.mark.asyncio
async def test_approve_cover_letter(monkeypatch, client, api_key_header, test_job_payload):
    async def fake_generate(*_args, **_kwargs):
        return {
            "content": "Cover letter",
            "target_role": RoleType.CTO,
            "generation_prompt": "prompt",
            "model_used": "test-model",
            "rag_evidence": None,
            "rag_context_used": False,
        }

    monkeypatch.setattr(cover_letter_service, "generate", fake_generate)

    job_response = await client.post(
        "/api/v1/jobs",
        json=test_job_payload(title="Engineer", company="Acme"),
        headers=api_key_header,
    )
    job_id = job_response.json()["id"]

    cover_response = await client.post(
        f"/api/v1/jobs/{job_id}/cover-letter",
        json={"target_role": "cto"},
        headers=api_key_header,
    )
    cover_id = cover_response.json()["id"]

    response = await client.patch(
        f"/api/v1/cover-letters/{cover_id}/approve",
        json={"is_approved": True},
        headers=api_key_header,
    )
    assert response.status_code == 200
    assert response.json()["is_approved"] is True


@pytest.mark.asyncio
async def test_delete_cover_letter(monkeypatch, client, api_key_header, test_job_payload):
    async def fake_generate(*_args, **_kwargs):
        return {
            "content": "Cover letter",
            "target_role": RoleType.CTO,
            "generation_prompt": "prompt",
            "model_used": "test-model",
            "rag_evidence": None,
            "rag_context_used": False,
        }

    monkeypatch.setattr(cover_letter_service, "generate", fake_generate)

    job_response = await client.post(
        "/api/v1/jobs",
        json=test_job_payload(title="Engineer", company="Acme"),
        headers=api_key_header,
    )
    job_id = job_response.json()["id"]

    cover_response = await client.post(
        f"/api/v1/jobs/{job_id}/cover-letter",
        json={"target_role": "cto"},
        headers=api_key_header,
    )
    cover_id = cover_response.json()["id"]

    delete_response = await client.delete(
        f"/api/v1/cover-letters/{cover_id}",
        headers=api_key_header,
    )
    assert delete_response.status_code == 204

    get_response = await client.get(
        f"/api/v1/cover-letters/{cover_id}",
        headers=api_key_header,
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_generate_cover_letter_with_tone(monkeypatch, client, api_key_header, test_job_payload):
    """Test cover letter generation with tone parameter."""
    received_tone = None

    async def fake_generate(*_args, **kwargs):
        nonlocal received_tone
        received_tone = kwargs.get("tone", "professional")
        return {
            "content": "Dear Hiring Manager, ...",
            "target_role": RoleType.VP,
            "generation_prompt": "prompt",
            "model_used": "test-model",
            "rag_evidence": None,
            "rag_context_used": False,
        }

    monkeypatch.setattr(cover_letter_service, "generate", fake_generate)

    job_response = await client.post(
        "/api/v1/jobs",
        json=test_job_payload(title="VP Engineering", company="Tech Corp"),
        headers=api_key_header,
    )
    job_id = job_response.json()["id"]

    response = await client.post(
        f"/api/v1/jobs/{job_id}/cover-letter",
        json={"target_role": "vp", "tone": "conversational"},
        headers=api_key_header,
    )
    assert response.status_code == 201
    assert received_tone == "conversational"


@pytest.mark.asyncio
async def test_generate_cover_letter_with_rag_evidence(monkeypatch, client, api_key_header, test_job_payload):
    """Test cover letter generation returns RAG evidence when available."""
    async def fake_generate(*_args, **_kwargs):
        return {
            "content": "Dear Hiring Manager, ...",
            "target_role": RoleType.DIRECTOR,
            "generation_prompt": "prompt",
            "model_used": "test-model",
            "rag_evidence": [
                {
                    "requirement": "Python experience",
                    "match_strength": "strong",
                    "evidence_snippet": "10 years leading Python teams",
                    "source_document": "resume.md",
                }
            ],
            "rag_context_used": True,
        }

    monkeypatch.setattr(cover_letter_service, "generate", fake_generate)

    job_response = await client.post(
        "/api/v1/jobs",
        json=test_job_payload(title="Director", company="Acme"),
        headers=api_key_header,
    )
    job_id = job_response.json()["id"]

    response = await client.post(
        f"/api/v1/jobs/{job_id}/cover-letter",
        json={"target_role": "director"},
        headers=api_key_header,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["rag_context_used"] is True
    assert len(data["rag_evidence"]) == 1
    assert data["rag_evidence"][0]["requirement"] == "Python experience"
    assert data["rag_evidence"][0]["match_strength"] == "strong"
