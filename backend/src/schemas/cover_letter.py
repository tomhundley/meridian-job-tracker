"""Pydantic schemas for Cover Letter API."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .job import RoleType


class CoverLetterBase(BaseModel):
    """Base schema for CoverLetter."""

    target_role: RoleType
    custom_instructions: str | None = None


class CoverLetterCreate(CoverLetterBase):
    """Schema for generating a new cover letter."""

    tone: Literal["professional", "conversational"] = Field(
        default="professional",
        description="Tone of the cover letter: professional or conversational",
    )


class RAGEvidenceItem(BaseModel):
    """Evidence item from RAG used in cover letter generation."""

    requirement: str = Field(..., description="The job requirement being matched")
    match_strength: Literal["strong", "moderate", "weak", "none"] = Field(
        ..., description="Strength of the match"
    )
    evidence_snippet: str = Field(..., description="Evidence snippet from career documents")
    source_document: str | None = Field(None, description="Source document name")


class CoverLetterUpdate(BaseModel):
    """Schema for updating a cover letter."""

    content: str = Field(..., min_length=1)


class CoverLetterApprove(BaseModel):
    """Schema for approving a cover letter."""

    is_approved: bool = True


class CoverLetterResponse(BaseModel):
    """Schema for cover letter response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    created_at: datetime
    updated_at: datetime
    content: str
    target_role: RoleType
    generation_prompt: str | None = None
    model_used: str | None = None
    version: int
    is_current: bool
    is_approved: bool
    approved_at: datetime | None = None
    rag_evidence: list[RAGEvidenceItem] | None = Field(
        default=None, description="RAG evidence used in generation (if use_rag=true)"
    )
    rag_context_used: bool = Field(
        default=False, description="Whether RAG context was used in generation"
    )
