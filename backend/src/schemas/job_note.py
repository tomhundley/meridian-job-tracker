"""Pydantic schemas for Job Notes."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class NoteSource(str, Enum):
    """Source of a note."""

    USER = "user"
    AGENT = "agent"


class NoteType(str, Enum):
    """Type of note for categorization."""

    GENERAL = "general"  # Default, backward compatible
    AI_ANALYSIS_SUMMARY = "ai_analysis_summary"  # Overall fit assessment
    COACHING_NOTES = "coaching_notes"  # What to emphasize in applications
    TALKING_POINTS = "talking_points"  # Interview preparation points
    STUDY_RECOMMENDATIONS = "study_recommendations"  # Skills/topics to study
    STRENGTHS = "strengths"  # Key strengths to highlight
    WATCH_OUTS = "watch_outs"  # Red flags or concerns
    RAG_EVIDENCE = "rag_evidence"  # Evidence from career documents


class JobNoteEntry(BaseModel):
    """Single note entry in the notes array."""

    text: str = Field(..., min_length=1, description="Note content")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="When note was created"
    )
    source: NoteSource = Field(
        default=NoteSource.USER, description="Who created the note"
    )
    note_type: NoteType = Field(
        default=NoteType.GENERAL, description="Category of note"
    )
    metadata: dict[str, Any] | None = Field(
        default=None, description="Additional structured data (scores, evidence, etc.)"
    )


class JobNoteCreate(BaseModel):
    """Schema for adding a new note."""

    text: str = Field(..., min_length=1, description="Note content")
    source: NoteSource = Field(default=NoteSource.USER, description="Note source")
    note_type: NoteType = Field(default=NoteType.GENERAL, description="Category of note")
    metadata: dict[str, Any] | None = Field(default=None, description="Additional data")
