"""Pydantic schemas for AI coaching insights from RAG-enhanced analysis."""

from typing import Literal

from pydantic import BaseModel, Field


class RAGEvidence(BaseModel):
    """Evidence from RAG search supporting an insight."""

    requirement: str = Field(..., description="The job requirement being matched")
    match_strength: Literal["strong", "moderate", "weak", "none"] = Field(
        ..., description="How well the candidate matches this requirement"
    )
    evidence_snippet: str = Field(..., description="Quote from career documents")
    source_document: str = Field(..., description="Source document name/path")
    similarity_score: float = Field(..., ge=0, le=1, description="Semantic similarity")


class JDMatchResult(BaseModel):
    """Result of matching a single job requirement against resume."""

    requirement: str = Field(..., description="The job requirement")
    match_strength: Literal["strong", "moderate", "weak", "none"] = Field(
        ..., description="Overall match strength"
    )
    evidence: list[str] = Field(default_factory=list, description="Evidence snippets")
    top_matches: list[RAGEvidence] = Field(
        default_factory=list, description="Top matching documents"
    )
    avg_similarity: float = Field(0.0, description="Average similarity score")


class ResumeSearchResult(BaseModel):
    """Result from semantic search over career documents."""

    id: str = Field(..., description="Document chunk ID")
    content: str = Field(..., description="The chunk text")
    source: str = Field(..., description="Source document")
    category: str = Field(..., description="Document category")
    similarity: float = Field(..., ge=0, le=1, description="Similarity score")
    section: str | None = Field(None, description="Section header if available")


class CoachingInsights(BaseModel):
    """Coaching insights generated from RAG-enhanced analysis."""

    talking_points: list[str] = Field(
        default_factory=list,
        description="Specific points to make in interviews with evidence",
    )
    strengths_to_highlight: list[str] = Field(
        default_factory=list,
        description="Key strengths to emphasize with concrete examples",
    )
    gaps_to_address: list[str] = Field(
        default_factory=list,
        description="Skill gaps and strategies to address them",
    )
    study_recommendations: list[str] = Field(
        default_factory=list,
        description="Technologies or skills to brush up on",
    )
    watch_outs: list[str] = Field(
        default_factory=list,
        description="Red flags or concerns about the role",
    )
    evidence_from_resume: list[RAGEvidence] = Field(
        default_factory=list,
        description="Supporting evidence from career documents",
    )


class EnhancedAnalysisResult(BaseModel):
    """Complete result from RAG-enhanced AI analysis."""

    # Standard analysis fields (from AIJobAnalysisResult)
    priority_score: int = Field(..., ge=0, le=100)
    recommendation: Literal["strong_apply", "apply", "research_more", "skip"]
    summary: str
    is_ai_forward: bool
    ai_forward_type: Literal["building_ai", "using_ai", "ai_curious", "traditional"]
    suggested_role: str
    is_location_compatible: bool
    location_notes: str | None

    # RAG-enhanced coaching
    coaching: CoachingInsights = Field(
        default_factory=CoachingInsights,
        description="Coaching insights from RAG analysis",
    )

    # Match details
    requirement_matches: list[JDMatchResult] = Field(
        default_factory=list,
        description="How each job requirement matches resume",
    )
