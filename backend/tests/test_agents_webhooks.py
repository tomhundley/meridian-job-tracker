"""Tests for agent and webhook endpoints."""

import pytest


@pytest.mark.asyncio
async def test_create_agent_and_use_permissions(client, api_key_header, test_job_payload):
    job_response = await client.post(
        "/api/v1/jobs",
        json=test_job_payload(title="Engineer", company="Acme"),
        headers=api_key_header,
    )
    assert job_response.status_code == 201

    agent_response = await client.post(
        "/api/v1/agents",
        json={"name": "test-agent", "permissions": ["jobs:read"]},
        headers=api_key_header,
    )
    assert agent_response.status_code == 201
    agent_key = agent_response.json()["api_key"]

    list_response = await client.get("/api/v1/jobs", headers={"X-API-Key": agent_key})
    assert list_response.status_code == 200


@pytest.mark.asyncio
async def test_create_and_list_webhooks(client, api_key_header):
    create_response = await client.post(
        "/api/v1/webhooks",
        json={
            "url": "https://agent.example.com/callback",
            "events": ["job.status_changed"],
            "secret": "test-secret",
        },
        headers=api_key_header,
    )
    assert create_response.status_code == 201

    list_response = await client.get("/api/v1/webhooks", headers=api_key_header)
    assert list_response.status_code == 200
    assert any(webhook["url"] == "https://agent.example.com/callback" for webhook in list_response.json())
