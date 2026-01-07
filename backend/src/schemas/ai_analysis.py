"""Pydantic schemas for AI-powered job analysis."""

from enum import Enum
from pydantic import BaseModel, Field

from src.schemas.job import RoleType


class AssessmentType(str, Enum):
    """How AI-forward the company/role is."""

    BUILDING_AI = "building_ai"  # Company builds AI products
    USING_AI = "using_ai"  # Company uses AI tools/platforms
    AI_CURIOUS = "ai_curious"  # Mentions AI but not core focus
    TRADITIONAL = "traditional"  # No AI focus


class SeniorityMatch(str, Enum):
    """How well candidate seniority matches the role."""

    OVER_QUALIFIED = "over_qualified"
    WELL_MATCHED = "well_matched"
    SLIGHTLY_UNDER = "slightly_under"
    SIGNIFICANTLY_UNDER = "significantly_under"


class Recommendation(str, Enum):
    """Recommendation for how to proceed with the job."""

    STRONG_APPLY = "strong_apply"  # Excellent fit, apply immediately
    APPLY = "apply"  # Good fit, worth applying
    RESEARCH_MORE = "research_more"  # Potential fit, needs more info
    SKIP = "skip"  # Poor fit, don't waste time


class RoleClassification(BaseModel):
    """AI's classification of what role type this job is."""

    suggested_role: RoleType = Field(..., description="Best matching role type")
    confidence: float = Field(..., ge=0, le=1, description="Confidence in this classification")
    reasoning: str = Field(..., description="Why this role was selected")


class RoleScoreDetail(BaseModel):
    """Detailed score for a specific role type."""

    role: RoleType = Field(..., description="The role type")
    score: int = Field(..., ge=0, le=100, description="Fit score 0-100")
    explanation: str = Field(..., description="Why this score was given")


class AIForwardAssessment(BaseModel):
    """Assessment of how AI-forward the company/role is."""

    is_ai_forward: bool = Field(..., description="Whether this is AI-forward")
    confidence: float = Field(..., ge=0, le=1, description="Confidence in assessment")
    evidence: list[str] = Field(default_factory=list, description="Evidence supporting assessment")
    assessment_type: AssessmentType = Field(..., description="Type of AI involvement")


class SkillsAlignment(BaseModel):
    """How well candidate skills match job requirements."""

    strong_matches: list[str] = Field(default_factory=list, description="Skills that match well")
    partial_matches: list[str] = Field(default_factory=list, description="Skills with partial overlap")
    gaps: list[str] = Field(default_factory=list, description="Required skills candidate lacks")


class ExperienceFit(BaseModel):
    """How well candidate experience matches requirements."""

    years_required: int | None = Field(None, description="Years of experience required")
    seniority_match: SeniorityMatch = Field(..., description="How seniority compares")
    notes: str | None = Field(None, description="Additional context about experience fit")


class CulturalSignals(BaseModel):
    """Cultural signals detected in the job posting."""

    positive: list[str] = Field(default_factory=list, description="Positive cultural signals")
    concerns: list[str] = Field(default_factory=list, description="Potential cultural concerns")


class LocationAssessment(BaseModel):
    """Assessment of location compatibility."""

    is_compatible: bool = Field(..., description="Whether location works for candidate")
    work_type_detected: str | None = Field(None, description="Remote/hybrid/onsite detected")
    location_restrictions: list[str] = Field(default_factory=list, description="Any location restrictions found")
    notes: str | None = Field(None, description="Explanation of location assessment")


class OverallAssessment(BaseModel):
    """Overall assessment and recommendation."""

    priority_score: int = Field(..., ge=0, le=100, description="Overall priority/fit score")
    recommendation: Recommendation = Field(..., description="What to do with this job")
    summary: str = Field(..., description="2-3 sentence summary of fit")
    key_strengths: list[str] = Field(default_factory=list, description="Top reasons this is a good fit")
    key_concerns: list[str] = Field(default_factory=list, description="Top reasons for concern")


class AIJobAnalysisResult(BaseModel):
    """Complete AI analysis result for a job posting."""

    role_classification: RoleClassification = Field(..., description="Role type classification")
    role_scores: list[RoleScoreDetail] = Field(..., description="Fit score for each role type")
    ai_forward_assessment: AIForwardAssessment = Field(..., description="AI-forward assessment")
    skills_alignment: SkillsAlignment = Field(..., description="Skills match analysis")
    experience_fit: ExperienceFit = Field(..., description="Experience match analysis")
    cultural_signals: CulturalSignals = Field(..., description="Cultural analysis")
    location_assessment: LocationAssessment = Field(..., description="Location compatibility")
    overall_assessment: OverallAssessment = Field(..., description="Overall recommendation")

    # Metadata
    analysis_version: str = Field(default="1.0", description="Version of analysis schema")
    model_used: str = Field(default="claude-sonnet-4-20250514", description="Model used for analysis")
