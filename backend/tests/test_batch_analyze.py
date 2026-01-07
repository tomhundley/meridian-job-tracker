"""Tests for batch analyze endpoint."""

import pytest
from unittest.mock import patch, MagicMock

from src.models.job import RoleType
from src.services.ai_analysis_service import AIAnalysisResult


@pytest.mark.asyncio
async def test_batch_analyze_empty_when_no_eligible_jobs(client, api_key_header):
    """Test batch analyze returns empty when no jobs need analysis."""
    response = await client.post(
        "/api/v1/jobs/analyze-all",
        json={"limit": 10},
        headers=api_key_header,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_eligible"] == 0
    assert data["processed"] == 0
    assert data["successful"] == 0
    assert data["failed"] == 0


@pytest.mark.asyncio
async def test_batch_analyze_filters_short_descriptions(client, api_key_header, test_job_payload):
    """Test batch analyze filters out jobs with short descriptions."""
    # Create job with short description
    await client.post(
        "/api/v1/jobs",
        json=test_job_payload(
            title="Short Job",
            company="Test Co",
            description_raw="Too short",  # Less than 500 chars
        ),
        headers=api_key_header,
    )

    response = await client.post(
        "/api/v1/jobs/analyze-all",
        json={"limit": 10, "min_description_length": 500},
        headers=api_key_header,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_eligible"] == 0


@pytest.mark.asyncio
async def test_batch_analyze_processes_eligible_jobs(monkeypatch, client, api_key_header, test_job_payload):
    """Test batch analyze processes jobs without existing analysis."""
    # Mock the AI analysis to avoid actual API calls
    mock_result = MagicMock()
    mock_result.suggested_priority = 85
    mock_result.is_ai_forward = True
    mock_result.is_location_compatible = True
    mock_result.suggested_role = RoleType.VP
    mock_result.technologies_matched = ["Python"]
    mock_result.technologies_missing = []
    mock_result.location_notes = None

    mock_ai_result = MagicMock(spec=AIAnalysisResult)
    mock_ai_result.overall_assessment.priority_score = 85
    mock_ai_result.overall_assessment.recommendation.value = "apply"
    mock_ai_result.overall_assessment.summary = "Good fit"
    mock_ai_result.overall_assessment.key_strengths = ["Python"]
    mock_ai_result.overall_assessment.key_concerns = []
    mock_ai_result.skills_alignment.strong_matches = ["Python"]
    mock_ai_result.skills_alignment.partial_matches = []
    mock_ai_result.skills_alignment.gaps = []

    def mock_analyze(*_args, **_kwargs):
        return mock_result, mock_ai_result

    monkeypatch.setattr("src.api.routes.jobs.analyze_job_with_ai", mock_analyze)

    # Create job with long enough description
    long_description = "A" * 600  # More than 500 chars
    job_response = await client.post(
        "/api/v1/jobs",
        json=test_job_payload(
            title="Eligible Job",
            company="Test Co",
            description_raw=long_description,
        ),
        headers=api_key_header,
    )
    job_id = job_response.json()["id"]

    response = await client.post(
        "/api/v1/jobs/analyze-all",
        json={"limit": 10, "min_description_length": 500, "delay_seconds": 0.1},
        headers=api_key_header,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_eligible"] >= 1
    assert data["processed"] >= 1
    assert data["successful"] >= 1

    # Find our job in results
    job_result = next((r for r in data["results"] if r["job_id"] == job_id), None)
    assert job_result is not None
    assert job_result["success"] is True
    assert job_result["priority"] == 85


@pytest.mark.asyncio
async def test_batch_analyze_skips_already_analyzed_jobs(monkeypatch, client, api_key_header, test_job_payload):
    """Test batch analyze skips jobs that already have ai_analysis_summary notes."""
    # Mock the AI analysis
    mock_result = MagicMock()
    mock_result.suggested_priority = 75
    mock_result.is_ai_forward = False
    mock_result.is_location_compatible = True
    mock_result.suggested_role = RoleType.DIRECTOR
    mock_result.technologies_matched = []
    mock_result.technologies_missing = []
    mock_result.location_notes = None

    mock_ai_result = MagicMock(spec=AIAnalysisResult)
    mock_ai_result.overall_assessment.priority_score = 75
    mock_ai_result.overall_assessment.recommendation.value = "apply"
    mock_ai_result.overall_assessment.summary = "Decent fit"
    mock_ai_result.overall_assessment.key_strengths = []
    mock_ai_result.overall_assessment.key_concerns = []
    mock_ai_result.skills_alignment.strong_matches = []
    mock_ai_result.skills_alignment.partial_matches = []
    mock_ai_result.skills_alignment.gaps = []

    def mock_analyze(*_args, **_kwargs):
        return mock_result, mock_ai_result

    monkeypatch.setattr("src.api.routes.jobs.analyze_job_with_ai", mock_analyze)

    # Create job with long enough description
    long_description = "B" * 600
    job_response = await client.post(
        "/api/v1/jobs",
        json=test_job_payload(
            title="Will Be Analyzed",
            company="Test Co",
            description_raw=long_description,
        ),
        headers=api_key_header,
    )
    job_id = job_response.json()["id"]

    # Run first batch analysis
    response1 = await client.post(
        "/api/v1/jobs/analyze-all",
        json={"limit": 10, "min_description_length": 500, "delay_seconds": 0.1},
        headers=api_key_header,
    )
    assert response1.status_code == 200
    data1 = response1.json()

    # Job should be in first batch results
    job_result1 = next((r for r in data1["results"] if r["job_id"] == job_id), None)
    assert job_result1 is not None

    # Run second batch analysis - job should be skipped
    response2 = await client.post(
        "/api/v1/jobs/analyze-all",
        json={"limit": 10, "min_description_length": 500, "delay_seconds": 0.1},
        headers=api_key_header,
    )
    assert response2.status_code == 200
    data2 = response2.json()

    # Job should NOT be in second batch results (already analyzed)
    job_result2 = next((r for r in data2["results"] if r["job_id"] == job_id), None)
    assert job_result2 is None


@pytest.mark.asyncio
async def test_batch_analyze_respects_limit(monkeypatch, client, api_key_header, test_job_payload):
    """Test batch analyze respects the limit parameter."""
    # Mock the AI analysis
    mock_result = MagicMock()
    mock_result.suggested_priority = 80
    mock_result.is_ai_forward = True
    mock_result.is_location_compatible = True
    mock_result.suggested_role = RoleType.VP
    mock_result.technologies_matched = []
    mock_result.technologies_missing = []
    mock_result.location_notes = None

    mock_ai_result = MagicMock(spec=AIAnalysisResult)
    mock_ai_result.overall_assessment.priority_score = 80
    mock_ai_result.overall_assessment.recommendation.value = "apply"
    mock_ai_result.overall_assessment.summary = "Good"
    mock_ai_result.overall_assessment.key_strengths = []
    mock_ai_result.overall_assessment.key_concerns = []
    mock_ai_result.skills_alignment.strong_matches = []
    mock_ai_result.skills_alignment.partial_matches = []
    mock_ai_result.skills_alignment.gaps = []

    def mock_analyze(*_args, **_kwargs):
        return mock_result, mock_ai_result

    monkeypatch.setattr("src.api.routes.jobs.analyze_job_with_ai", mock_analyze)

    # Create multiple jobs
    long_description = "C" * 600
    for i in range(5):
        await client.post(
            "/api/v1/jobs",
            json=test_job_payload(
                title=f"Job {i}",
                company="Test Co",
                description_raw=long_description,
            ),
            headers=api_key_header,
        )

    # Request only 2
    response = await client.post(
        "/api/v1/jobs/analyze-all",
        json={"limit": 2, "min_description_length": 500, "delay_seconds": 0.1},
        headers=api_key_header,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["processed"] == 2
    assert len(data["results"]) == 2


@pytest.mark.asyncio
async def test_batch_analyze_request_validation(client, api_key_header):
    """Test batch analyze validates request parameters."""
    # Test limit too high
    response = await client.post(
        "/api/v1/jobs/analyze-all",
        json={"limit": 200},  # Max is 100
        headers=api_key_header,
    )
    assert response.status_code == 422

    # Test negative limit
    response = await client.post(
        "/api/v1/jobs/analyze-all",
        json={"limit": -1},
        headers=api_key_header,
    )
    assert response.status_code == 422

    # Test delay too high
    response = await client.post(
        "/api/v1/jobs/analyze-all",
        json={"delay_seconds": 100},  # Max is 10
        headers=api_key_header,
    )
    assert response.status_code == 422
