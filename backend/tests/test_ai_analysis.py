"""Tests for AI-powered job analysis."""

import json
import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from src.models import Job
from src.models.job import RoleType, WorkLocationType
from src.schemas.ai_analysis import (
    AIJobAnalysisResult,
    AssessmentType,
    Recommendation,
    SeniorityMatch,
)
from src.services.ai_analysis_service import AIAnalysisService, _build_user_prompt
from src.services.analysis_cache import AnalysisCache
from src.services.job_analysis_service import analyze_job_with_ai, _convert_ai_to_legacy


# Sample AI response for mocking
SAMPLE_AI_RESPONSE = {
    "role_classification": {
        "suggested_role": "director",
        "confidence": 0.85,
        "reasoning": "Title contains 'Director' and responsibilities align with director-level work",
    },
    "role_scores": [
        {"role": "cto", "score": 55, "explanation": "Some strategic overlap but not C-level"},
        {"role": "vp", "score": 65, "explanation": "Good leadership scope"},
        {"role": "director", "score": 80, "explanation": "Best match for title and responsibilities"},
        {"role": "architect", "score": 50, "explanation": "Less technical depth required"},
        {"role": "developer", "score": 35, "explanation": "Too senior for IC role"},
    ],
    "ai_forward_assessment": {
        "is_ai_forward": True,
        "confidence": 0.9,
        "evidence": ["Building AI products", "LLM integration mentioned", "ML platform work"],
        "assessment_type": "building_ai",
    },
    "skills_alignment": {
        "strong_matches": ["Python", "TypeScript", "Azure", "Team leadership"],
        "partial_matches": ["React", "Node.js"],
        "gaps": ["Kubernetes", "Go"],
    },
    "experience_fit": {
        "years_required": 10,
        "seniority_match": "well_matched",
        "notes": "10+ years required, candidate exceeds with 25+ years",
    },
    "cultural_signals": {
        "positive": ["Collaborative environment", "Growth mindset", "Innovation focus"],
        "concerns": ["Fast-paced startup culture may be demanding"],
    },
    "location_assessment": {
        "is_compatible": True,
        "work_type_detected": "hybrid",
        "location_restrictions": [],
        "notes": "Hybrid role in Atlanta metro area - compatible with Alpharetta, GA",
    },
    "overall_assessment": {
        "priority_score": 78,
        "recommendation": "apply",
        "summary": "Strong fit for a Director-level AI role. Good technology overlap and leadership experience alignment. Hybrid location works well.",
        "key_strengths": [
            "AI-forward company building products",
            "Director-level leadership scope",
            "Strong tech stack match",
        ],
        "key_concerns": ["May require Kubernetes experience", "Startup pace"],
    },
}


@pytest.fixture
def sample_job():
    """Create a sample job for testing."""
    job = Job(
        id=uuid4(),
        title="Director of Engineering - AI Platform",
        company="AI Startup Inc",
        location="Atlanta, GA",
        work_location_type=WorkLocationType.HYBRID,
        description_raw="""
        We are looking for a Director of Engineering to lead our AI Platform team.

        About the Role:
        - Lead a team of 10+ engineers building our ML platform
        - Drive technical strategy for LLM integration
        - Collaborate with product on AI product roadmap
        - Build and scale our AI infrastructure

        Requirements:
        - 10+ years of software engineering experience
        - 5+ years of leadership experience
        - Strong Python and TypeScript skills
        - Experience with Azure cloud services
        - Passion for AI and machine learning

        Nice to have:
        - Kubernetes experience
        - Go programming language
        """,
    )
    return job


@pytest.fixture
def mock_ai_response():
    """Return the mock AI response."""
    return SAMPLE_AI_RESPONSE


class TestAIAnalysisService:
    """Tests for AIAnalysisService."""

    def test_build_user_prompt(self, sample_job):
        """Test that user prompt is built correctly."""
        prompt = _build_user_prompt(sample_job)

        assert "Director of Engineering - AI Platform" in prompt
        assert "AI Startup Inc" in prompt
        assert "Atlanta, GA" in prompt
        assert "ML platform" in prompt
        assert "JSON" in prompt

    @patch("src.services.ai_analysis_service.Anthropic")
    def test_analyze_success(self, mock_anthropic, sample_job, mock_ai_response):
        """Test successful AI analysis."""
        # Setup mock
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(mock_ai_response))]
        mock_client.messages.create.return_value = mock_response

        # Create service and run analysis
        service = AIAnalysisService()
        service.client = mock_client  # Override to avoid None
        result = service.analyze(sample_job)

        # Verify result
        assert isinstance(result, AIJobAnalysisResult)
        assert result.role_classification.suggested_role == RoleType.DIRECTOR
        assert result.role_classification.confidence == 0.85
        assert result.ai_forward_assessment.is_ai_forward is True
        assert result.ai_forward_assessment.assessment_type == AssessmentType.BUILDING_AI
        assert result.overall_assessment.priority_score == 78
        assert result.overall_assessment.recommendation == Recommendation.APPLY
        assert result.location_assessment.is_compatible is True

    @patch("src.services.ai_analysis_service.Anthropic")
    def test_analyze_parses_all_roles(self, mock_anthropic, sample_job, mock_ai_response):
        """Test that all role scores are parsed."""
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(mock_ai_response))]
        mock_client.messages.create.return_value = mock_response

        service = AIAnalysisService()
        service.client = mock_client
        result = service.analyze(sample_job)

        # Should have all 5 roles
        assert len(result.role_scores) == 5
        roles = {rs.role for rs in result.role_scores}
        assert roles == {RoleType.CTO, RoleType.VP, RoleType.DIRECTOR, RoleType.ARCHITECT, RoleType.DEVELOPER}

        # Check director score
        director_score = next(rs for rs in result.role_scores if rs.role == RoleType.DIRECTOR)
        assert director_score.score == 80

    def test_fallback_result(self, sample_job):
        """Test fallback result generation."""
        service = AIAnalysisService()
        result = service._fallback_result(sample_job)

        assert isinstance(result, AIJobAnalysisResult)
        assert result.overall_assessment.recommendation == Recommendation.RESEARCH_MORE
        assert result.model_used == "fallback"
        assert "AI analysis unavailable" in result.overall_assessment.summary


class TestConvertAIToLegacy:
    """Tests for converting AI results to legacy format."""

    @patch("src.services.ai_analysis_service.Anthropic")
    def test_convert_ai_to_legacy(self, mock_anthropic, sample_job, mock_ai_response):
        """Test conversion from AI result to legacy format."""
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(mock_ai_response))]
        mock_client.messages.create.return_value = mock_response

        service = AIAnalysisService()
        service.client = mock_client
        ai_result = service.analyze(sample_job)

        # Convert to legacy
        legacy = _convert_ai_to_legacy(ai_result)

        # Check legacy fields
        assert legacy.is_ai_forward is True
        assert legacy.ai_confidence == 0.9
        assert legacy.suggested_priority == 78
        assert legacy.suggested_role == RoleType.DIRECTOR
        assert legacy.is_location_compatible is True
        assert "Python" in legacy.technologies_matched
        assert "Kubernetes" in legacy.technologies_missing
        assert len(legacy.role_scores) == 5


class TestAnalysisCache:
    """Tests for analysis caching."""

    def test_cache_set_and_get(self, mock_ai_response):
        """Test basic cache operations."""
        cache = AnalysisCache(max_size=10)
        job_id = str(uuid4())
        description = "Test job description"

        # Create a mock AI result
        from src.schemas.ai_analysis import (
            RoleClassification,
            RoleScoreDetail,
            AIForwardAssessment,
            SkillsAlignment,
            ExperienceFit,
            CulturalSignals,
            LocationAssessment,
            OverallAssessment,
        )

        result = AIJobAnalysisResult(
            role_classification=RoleClassification(
                suggested_role=RoleType.DIRECTOR,
                confidence=0.85,
                reasoning="Test",
            ),
            role_scores=[
                RoleScoreDetail(role=role, score=50, explanation="Test")
                for role in RoleType
            ],
            ai_forward_assessment=AIForwardAssessment(
                is_ai_forward=True,
                confidence=0.9,
                evidence=["Test"],
                assessment_type=AssessmentType.BUILDING_AI,
            ),
            skills_alignment=SkillsAlignment(),
            experience_fit=ExperienceFit(seniority_match=SeniorityMatch.WELL_MATCHED),
            cultural_signals=CulturalSignals(),
            location_assessment=LocationAssessment(is_compatible=True),
            overall_assessment=OverallAssessment(
                priority_score=78,
                recommendation=Recommendation.APPLY,
                summary="Test summary",
            ),
        )

        # Set in cache
        cache.set(job_id, description, result)

        # Get from cache
        cached = cache.get(job_id, description)
        assert cached is not None
        assert cached.overall_assessment.priority_score == 78

    def test_cache_miss_different_description(self, mock_ai_response):
        """Test cache miss when description changes."""
        cache = AnalysisCache(max_size=10)
        job_id = str(uuid4())

        # Create a simple mock result
        from src.schemas.ai_analysis import (
            RoleClassification,
            RoleScoreDetail,
            AIForwardAssessment,
            SkillsAlignment,
            ExperienceFit,
            CulturalSignals,
            LocationAssessment,
            OverallAssessment,
        )

        result = AIJobAnalysisResult(
            role_classification=RoleClassification(
                suggested_role=RoleType.DIRECTOR,
                confidence=0.85,
                reasoning="Test",
            ),
            role_scores=[
                RoleScoreDetail(role=role, score=50, explanation="Test")
                for role in RoleType
            ],
            ai_forward_assessment=AIForwardAssessment(
                is_ai_forward=True,
                confidence=0.9,
                evidence=["Test"],
                assessment_type=AssessmentType.BUILDING_AI,
            ),
            skills_alignment=SkillsAlignment(),
            experience_fit=ExperienceFit(seniority_match=SeniorityMatch.WELL_MATCHED),
            cultural_signals=CulturalSignals(),
            location_assessment=LocationAssessment(is_compatible=True),
            overall_assessment=OverallAssessment(
                priority_score=78,
                recommendation=Recommendation.APPLY,
                summary="Test summary",
            ),
        )

        # Set with one description
        cache.set(job_id, "Description A", result)

        # Try to get with different description
        cached = cache.get(job_id, "Description B")
        assert cached is None  # Should miss

    def test_cache_invalidate(self):
        """Test cache invalidation."""
        cache = AnalysisCache(max_size=10)
        job_id = str(uuid4())

        from src.schemas.ai_analysis import (
            RoleClassification,
            RoleScoreDetail,
            AIForwardAssessment,
            SkillsAlignment,
            ExperienceFit,
            CulturalSignals,
            LocationAssessment,
            OverallAssessment,
        )

        result = AIJobAnalysisResult(
            role_classification=RoleClassification(
                suggested_role=RoleType.DIRECTOR,
                confidence=0.85,
                reasoning="Test",
            ),
            role_scores=[
                RoleScoreDetail(role=role, score=50, explanation="Test")
                for role in RoleType
            ],
            ai_forward_assessment=AIForwardAssessment(
                is_ai_forward=True,
                confidence=0.9,
                evidence=["Test"],
                assessment_type=AssessmentType.BUILDING_AI,
            ),
            skills_alignment=SkillsAlignment(),
            experience_fit=ExperienceFit(seniority_match=SeniorityMatch.WELL_MATCHED),
            cultural_signals=CulturalSignals(),
            location_assessment=LocationAssessment(is_compatible=True),
            overall_assessment=OverallAssessment(
                priority_score=78,
                recommendation=Recommendation.APPLY,
                summary="Test summary",
            ),
        )

        cache.set(job_id, "Description", result)
        assert cache.get(job_id, "Description") is not None

        cache.invalidate(job_id)
        assert cache.get(job_id, "Description") is None

    def test_cache_eviction(self):
        """Test LRU eviction when cache is full."""
        cache = AnalysisCache(max_size=2)

        from src.schemas.ai_analysis import (
            RoleClassification,
            RoleScoreDetail,
            AIForwardAssessment,
            SkillsAlignment,
            ExperienceFit,
            CulturalSignals,
            LocationAssessment,
            OverallAssessment,
        )

        def make_result(score):
            return AIJobAnalysisResult(
                role_classification=RoleClassification(
                    suggested_role=RoleType.DIRECTOR,
                    confidence=0.85,
                    reasoning="Test",
                ),
                role_scores=[
                    RoleScoreDetail(role=role, score=50, explanation="Test")
                    for role in RoleType
                ],
                ai_forward_assessment=AIForwardAssessment(
                    is_ai_forward=True,
                    confidence=0.9,
                    evidence=["Test"],
                    assessment_type=AssessmentType.BUILDING_AI,
                ),
                skills_alignment=SkillsAlignment(),
                experience_fit=ExperienceFit(seniority_match=SeniorityMatch.WELL_MATCHED),
                cultural_signals=CulturalSignals(),
                location_assessment=LocationAssessment(is_compatible=True),
                overall_assessment=OverallAssessment(
                    priority_score=score,
                    recommendation=Recommendation.APPLY,
                    summary="Test summary",
                ),
            )

        # Add 3 items to cache with max_size=2
        cache.set("job1", "desc", make_result(10))
        cache.set("job2", "desc", make_result(20))
        cache.set("job3", "desc", make_result(30))

        # First item should be evicted
        assert cache.get("job1", "desc") is None
        assert cache.get("job2", "desc") is not None
        assert cache.get("job3", "desc") is not None


class TestAnalyzeJobWithAI:
    """Tests for the integrated analyze_job_with_ai function."""

    @patch("src.services.job_analysis_service.settings")
    def test_fallback_to_rules_when_no_api_key(self, mock_settings, sample_job):
        """Test fallback to rule-based analysis when API key not set."""
        mock_settings.anthropic_api_key = None

        result, ai_result = analyze_job_with_ai(sample_job, use_ai=True)

        # Should have used rule-based analysis
        assert ai_result is None
        assert result is not None
        assert result.suggested_priority >= 0

    @patch("src.services.job_analysis_service.settings")
    def test_rules_only_mode(self, mock_settings, sample_job):
        """Test forcing rule-based analysis."""
        mock_settings.anthropic_api_key = "test-key"

        result, ai_result = analyze_job_with_ai(sample_job, use_ai=False)

        # Should have used rule-based analysis
        assert ai_result is None
        assert result is not None
