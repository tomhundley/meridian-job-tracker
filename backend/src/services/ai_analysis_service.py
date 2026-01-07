"""AI-powered job analysis service using Claude."""

import json
import re
from datetime import datetime, timezone

import structlog
from anthropic import Anthropic

from src.config import settings
from src.models import Job
from src.models.job import RoleType
from src.schemas.ai_analysis import (
    AIJobAnalysisResult,
    RoleClassification,
    RoleScoreDetail,
    AIForwardAssessment,
    SkillsAlignment,
    ExperienceFit,
    CulturalSignals,
    LocationAssessment,
    OverallAssessment,
    AssessmentType,
    SeniorityMatch,
    Recommendation,
)
from src.schemas.ai_analysis_coach import (
    CoachingInsights,
    EnhancedAnalysisResult,
    JDMatchResult,
    RAGEvidence,
)
from src.schemas.job_note import JobNoteEntry, NoteSource, NoteType

logger = structlog.get_logger(__name__)

# System prompt with candidate profile
SYSTEM_PROMPT = """You are a job analysis assistant for Tom Hundley, an experienced technology executive seeking AI-focused roles.

## Candidate Profile

**Experience:** 25+ years in enterprise software development, from QA tester to CTO/business owner
**Location:** Alpharetta, GA (willing to travel anywhere in US for hybrid/on-site roles)
**Core Drive:** Seeking AI-focused positions where title is secondary to being immersed in AI at scale

### Target Roles (priority order)
1. CTO - Technology strategy, AI transformation, enterprise architecture
2. VP Engineering - Organization building, P&L management, team development
3. Director - Delivery excellence, Agile/Scrum, process improvement
4. Solutions Architect - System design, enterprise integration, cloud-native
5. Developer - Hands-on coding, AI-assisted development, technical depth

### Core Competencies
- AI/ML: Azure OpenAI, RAG systems, LLM integration, prompt engineering, agentic systems, Claude Code
- Cloud: Azure (primary), AWS, GCP - Functions, Service Bus, Cosmos DB, DevOps
- Languages: C#/.NET 8, TypeScript, React/Next.js, Python, Node.js
- Integration: REST APIs, GraphQL, tRPC, Azure Service Bus, Event-driven architecture
- Leadership: P&L management ($1-5M), vendor management, team building (15+ engineers)

### Key Differentiators
- 19-year partnership with MDSi as de facto CTO building enterprise telecom software
- 3M+ lines of AI-generated production code using Claude Code
- Enterprise integration experience (Comcast, AT&T, Verizon, Cox, Charter)
- Strong preference for AI-forward companies BUILDING AI products (not just using them)

### Deal Breakers (should result in skip recommendation)
- Remote roles restricted to states other than GA (he lives in Alpharetta, GA)
- Roles focused solely on legacy tech with no AI roadmap
- Very junior positions (<5 years experience required)

You must analyze job postings and return structured JSON. Be direct and honest about fit - don't oversell poor matches."""


def _build_user_prompt(job: Job) -> str:
    """Build the user prompt with job details and output format."""
    return f"""Analyze this job posting and return a JSON response:

## Job Details
- **Title:** {job.title}
- **Company:** {job.company}
- **Location:** {job.location or "Not specified"}
- **Work Type:** {job.work_location_type.value if job.work_location_type else "Not specified"}
- **Employment Type:** {job.employment_type.value if job.employment_type else "Not specified"}

## Job Description
{job.description_raw or "No description provided"}

## Required JSON Response Format
Return ONLY valid JSON matching this exact structure (no markdown, no explanation):

{{
  "role_classification": {{
    "suggested_role": "cto|vp|director|architect|developer",
    "confidence": 0.0-1.0,
    "reasoning": "Why this role type fits"
  }},
  "role_scores": [
    {{"role": "cto", "score": 0-100, "explanation": "Why this score"}},
    {{"role": "vp", "score": 0-100, "explanation": "Why this score"}},
    {{"role": "director", "score": 0-100, "explanation": "Why this score"}},
    {{"role": "architect", "score": 0-100, "explanation": "Why this score"}},
    {{"role": "developer", "score": 0-100, "explanation": "Why this score"}}
  ],
  "ai_forward_assessment": {{
    "is_ai_forward": true|false,
    "confidence": 0.0-1.0,
    "evidence": ["Evidence 1", "Evidence 2"],
    "assessment_type": "building_ai|using_ai|ai_curious|traditional"
  }},
  "skills_alignment": {{
    "strong_matches": ["Skill 1", "Skill 2"],
    "partial_matches": ["Skill 3"],
    "gaps": ["Missing skill 1"]
  }},
  "experience_fit": {{
    "years_required": null or number,
    "seniority_match": "over_qualified|well_matched|slightly_under|significantly_under",
    "notes": "Additional context"
  }},
  "cultural_signals": {{
    "positive": ["Good signal 1"],
    "concerns": ["Concern 1"]
  }},
  "location_assessment": {{
    "is_compatible": true|false,
    "work_type_detected": "remote|hybrid|onsite|null",
    "location_restrictions": ["State1", "State2"],
    "notes": "Explanation of location compatibility"
  }},
  "overall_assessment": {{
    "priority_score": 0-100,
    "recommendation": "strong_apply|apply|research_more|skip",
    "summary": "2-3 sentence summary of fit",
    "key_strengths": ["Strength 1", "Strength 2"],
    "key_concerns": ["Concern 1"]
  }}
}}

Important scoring guidelines:
- priority_score 80-100: Excellent fit, apply immediately
- priority_score 60-79: Good fit, worth applying
- priority_score 40-59: Moderate fit, research more
- priority_score 0-39: Poor fit, likely skip

Location rules:
- Remote roles restricted to specific states that DON'T include GA = skip
- Remote roles open to all US or including GA = compatible
- Hybrid/onsite in Atlanta metro = compatible
- Hybrid/onsite requiring relocation = check if reasonable"""


class AIAnalysisService:
    """Service for AI-powered job analysis using Claude."""

    def __init__(self):
        self.client = Anthropic(api_key=settings.anthropic_api_key) if settings.anthropic_api_key else None
        self.model = "claude-sonnet-4-20250514"

    def analyze(self, job: Job) -> AIJobAnalysisResult:
        """
        Analyze a job using Claude AI.

        Args:
            job: The job to analyze

        Returns:
            AIJobAnalysisResult with comprehensive analysis

        Raises:
            ValueError: If Anthropic API key not configured
            Exception: If API call fails
        """
        if not self.client:
            raise ValueError("Anthropic API key not configured")

        logger.info(
            "ai_analysis_start",
            job_id=str(job.id),
            company=job.company,
            title=job.title,
        )

        user_prompt = _build_user_prompt(job)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )

            content = response.content[0].text
            result = self._parse_response(content, job)

            logger.info(
                "ai_analysis_success",
                job_id=str(job.id),
                priority=result.overall_assessment.priority_score,
                recommendation=result.overall_assessment.recommendation.value,
            )

            return result

        except Exception as e:
            logger.error(
                "ai_analysis_error",
                job_id=str(job.id),
                error=str(e),
            )
            raise

    def _parse_response(self, content: str, job: Job) -> AIJobAnalysisResult:
        """Parse Claude's JSON response into AIJobAnalysisResult."""
        # Try to extract JSON from response (handle potential markdown wrapping)
        json_match = re.search(r'\{[\s\S]*\}', content)
        if not json_match:
            raise ValueError(f"No JSON found in response: {content[:200]}")

        json_str = json_match.group()
        data = json.loads(json_str)

        # Parse role classification
        role_data = data.get("role_classification", {})
        role_classification = RoleClassification(
            suggested_role=RoleType(role_data.get("suggested_role", "developer")),
            confidence=float(role_data.get("confidence", 0.5)),
            reasoning=role_data.get("reasoning", ""),
        )

        # Parse role scores
        role_scores = []
        for score_data in data.get("role_scores", []):
            role_scores.append(RoleScoreDetail(
                role=RoleType(score_data.get("role", "developer")),
                score=int(score_data.get("score", 50)),
                explanation=score_data.get("explanation", ""),
            ))

        # Ensure all roles have scores
        existing_roles = {rs.role for rs in role_scores}
        for role in RoleType:
            if role not in existing_roles:
                role_scores.append(RoleScoreDetail(
                    role=role,
                    score=50,
                    explanation="No specific analysis",
                ))

        # Parse AI forward assessment
        ai_data = data.get("ai_forward_assessment", {})
        ai_forward_assessment = AIForwardAssessment(
            is_ai_forward=bool(ai_data.get("is_ai_forward", False)),
            confidence=float(ai_data.get("confidence", 0.5)),
            evidence=ai_data.get("evidence", []),
            assessment_type=AssessmentType(ai_data.get("assessment_type", "traditional")),
        )

        # Parse skills alignment
        skills_data = data.get("skills_alignment", {})
        skills_alignment = SkillsAlignment(
            strong_matches=skills_data.get("strong_matches", []),
            partial_matches=skills_data.get("partial_matches", []),
            gaps=skills_data.get("gaps", []),
        )

        # Parse experience fit
        exp_data = data.get("experience_fit", {})
        experience_fit = ExperienceFit(
            years_required=exp_data.get("years_required"),
            seniority_match=SeniorityMatch(exp_data.get("seniority_match", "well_matched")),
            notes=exp_data.get("notes"),
        )

        # Parse cultural signals
        culture_data = data.get("cultural_signals", {})
        cultural_signals = CulturalSignals(
            positive=culture_data.get("positive", []),
            concerns=culture_data.get("concerns", []),
        )

        # Parse location assessment
        loc_data = data.get("location_assessment", {})
        location_assessment = LocationAssessment(
            is_compatible=bool(loc_data.get("is_compatible", True)),
            work_type_detected=loc_data.get("work_type_detected"),
            location_restrictions=loc_data.get("location_restrictions", []),
            notes=loc_data.get("notes"),
        )

        # Parse overall assessment
        overall_data = data.get("overall_assessment", {})
        overall_assessment = OverallAssessment(
            priority_score=int(overall_data.get("priority_score", 50)),
            recommendation=Recommendation(overall_data.get("recommendation", "research_more")),
            summary=overall_data.get("summary", ""),
            key_strengths=overall_data.get("key_strengths", []),
            key_concerns=overall_data.get("key_concerns", []),
        )

        return AIJobAnalysisResult(
            role_classification=role_classification,
            role_scores=role_scores,
            ai_forward_assessment=ai_forward_assessment,
            skills_alignment=skills_alignment,
            experience_fit=experience_fit,
            cultural_signals=cultural_signals,
            location_assessment=location_assessment,
            overall_assessment=overall_assessment,
            model_used=self.model,
        )

    def _fallback_result(self, job: Job) -> AIJobAnalysisResult:
        """Return a default result when AI analysis fails."""
        return AIJobAnalysisResult(
            role_classification=RoleClassification(
                suggested_role=RoleType.DEVELOPER,
                confidence=0.3,
                reasoning="Fallback: AI analysis unavailable",
            ),
            role_scores=[
                RoleScoreDetail(role=role, score=50, explanation="Fallback score")
                for role in RoleType
            ],
            ai_forward_assessment=AIForwardAssessment(
                is_ai_forward=False,
                confidence=0.3,
                evidence=[],
                assessment_type=AssessmentType.TRADITIONAL,
            ),
            skills_alignment=SkillsAlignment(),
            experience_fit=ExperienceFit(
                seniority_match=SeniorityMatch.WELL_MATCHED,
            ),
            cultural_signals=CulturalSignals(),
            location_assessment=LocationAssessment(
                is_compatible=True,
            ),
            overall_assessment=OverallAssessment(
                priority_score=50,
                recommendation=Recommendation.RESEARCH_MORE,
                summary="AI analysis unavailable - manual review recommended",
                key_strengths=[],
                key_concerns=["AI analysis failed - needs manual review"],
            ),
            model_used="fallback",
        )


# Enhanced coaching prompt section
COACHING_PROMPT_SECTION = """

## COACHING ANALYSIS REQUEST

In addition to the standard analysis, provide detailed coaching insights based on the candidate's background:

{rag_context}

Provide coaching insights in this additional JSON section:

"coaching_insights": {{
  "talking_points": [
    "Specific points to make in interviews with evidence from past projects..."
  ],
  "strengths_to_highlight": [
    "Key strengths to emphasize with concrete examples..."
  ],
  "gaps_to_address": [
    "Skills gaps and strategies to address them..."
  ],
  "study_recommendations": [
    "Technologies or skills to brush up on before interviewing..."
  ],
  "watch_outs": [
    "Red flags or concerns about the role that need attention..."
  ]
}}

Be specific and reference the candidate's actual experience when providing coaching advice.
"""


class AIAnalysisServiceEnhanced(AIAnalysisService):
    """Enhanced AI analysis service with RAG context and coaching insights."""

    async def analyze_with_coaching(
        self,
        job: Job,
        rag_context: str = "",
    ) -> tuple[AIJobAnalysisResult, CoachingInsights, list[JDMatchResult]]:
        """
        Enhanced analysis with RAG context and coaching insights.

        Args:
            job: The job to analyze
            rag_context: Pre-built RAG context from SparklesClient

        Returns:
            Tuple of (AIJobAnalysisResult, CoachingInsights, JDMatchResults)
        """
        if not self.client:
            raise ValueError("Anthropic API key not configured")

        logger.info(
            "enhanced_ai_analysis_start",
            job_id=str(job.id),
            company=job.company,
            title=job.title,
            has_rag_context=bool(rag_context),
        )

        # Build enhanced prompt with coaching section
        user_prompt = _build_user_prompt(job)
        if rag_context:
            user_prompt += COACHING_PROMPT_SECTION.format(rag_context=rag_context)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=6000,  # Increased for coaching insights
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )

            content = response.content[0].text
            result, coaching = self._parse_enhanced_response(content, job)

            logger.info(
                "enhanced_ai_analysis_success",
                job_id=str(job.id),
                priority=result.overall_assessment.priority_score,
                recommendation=result.overall_assessment.recommendation.value,
                has_coaching=bool(coaching.talking_points),
            )

            return result, coaching, []

        except Exception as e:
            logger.error(
                "enhanced_ai_analysis_error",
                job_id=str(job.id),
                error=str(e),
            )
            raise

    def _parse_enhanced_response(
        self, content: str, job: Job
    ) -> tuple[AIJobAnalysisResult, CoachingInsights]:
        """Parse Claude's JSON response including coaching insights."""
        # Try to extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', content)
        if not json_match:
            raise ValueError(f"No JSON found in response: {content[:200]}")

        json_str = json_match.group()
        data = json.loads(json_str)

        # Parse standard analysis (reuse parent logic)
        result = self._parse_response(content, job)

        # Parse coaching insights
        coaching_data = data.get("coaching_insights", {})
        coaching = CoachingInsights(
            talking_points=coaching_data.get("talking_points", []),
            strengths_to_highlight=coaching_data.get("strengths_to_highlight", []),
            gaps_to_address=coaching_data.get("gaps_to_address", []),
            study_recommendations=coaching_data.get("study_recommendations", []),
            watch_outs=coaching_data.get("watch_outs", []),
            evidence_from_resume=[],  # Populated from RAG matches
        )

        return result, coaching


def generate_typed_notes(
    ai_result: AIJobAnalysisResult,
    coaching: CoachingInsights | None = None,
    requirement_matches: list[JDMatchResult] | None = None,
) -> list[JobNoteEntry]:
    """
    Generate multiple typed notes from AI analysis and coaching insights.

    Args:
        ai_result: The AI job analysis result
        coaching: Optional coaching insights from RAG-enhanced analysis
        requirement_matches: Optional JD requirement match results

    Returns:
        List of typed notes to add to the job
    """
    notes: list[JobNoteEntry] = []
    now = datetime.now(timezone.utc)

    # 1. AI Analysis Summary note
    recommendation = ai_result.overall_assessment.recommendation.value.upper()
    score = ai_result.overall_assessment.priority_score
    summary = ai_result.overall_assessment.summary

    summary_text = f"**{recommendation}** ({score}/100)\n\n{summary}"
    if ai_result.ai_forward_assessment.is_ai_forward:
        ai_type = ai_result.ai_forward_assessment.assessment_type.value.replace("_", " ").title()
        summary_text += f"\n\n**AI Assessment:** {ai_type} ({ai_result.ai_forward_assessment.confidence:.0%} confidence)"

    notes.append(JobNoteEntry(
        text=summary_text,
        timestamp=now,
        source=NoteSource.AGENT,
        note_type=NoteType.AI_ANALYSIS_SUMMARY,
        metadata={
            "priority_score": score,
            "recommendation": recommendation,
            "ai_forward": ai_result.ai_forward_assessment.is_ai_forward,
            "suggested_role": ai_result.role_classification.suggested_role.value,
        },
    ))

    # 2. Strengths note (if any identified)
    if ai_result.overall_assessment.key_strengths:
        strengths_text = "**Key Strengths:**\n" + "\n".join(
            f"• {s}" for s in ai_result.overall_assessment.key_strengths
        )
        notes.append(JobNoteEntry(
            text=strengths_text,
            timestamp=now,
            source=NoteSource.AGENT,
            note_type=NoteType.STRENGTHS,
        ))

    # 3. Watch-outs note (if concerns identified)
    if ai_result.overall_assessment.key_concerns:
        concerns_text = "**Concerns to Address:**\n" + "\n".join(
            f"• {c}" for c in ai_result.overall_assessment.key_concerns
        )
        notes.append(JobNoteEntry(
            text=concerns_text,
            timestamp=now,
            source=NoteSource.AGENT,
            note_type=NoteType.WATCH_OUTS,
        ))

    # 4. Location note (if incompatible)
    if not ai_result.location_assessment.is_compatible:
        loc_text = f"**Location Issue:** {ai_result.location_assessment.notes or 'Not compatible'}"
        if ai_result.location_assessment.location_restrictions:
            loc_text += f"\n\nRestricted to: {', '.join(ai_result.location_assessment.location_restrictions)}"
        notes.append(JobNoteEntry(
            text=loc_text,
            timestamp=now,
            source=NoteSource.AGENT,
            note_type=NoteType.WATCH_OUTS,
            metadata={"location_incompatible": True},
        ))

    # If we have coaching insights, add those notes
    if coaching:
        # 5. Talking Points note
        if coaching.talking_points:
            tp_text = "**Interview Talking Points:**\n" + "\n".join(
                f"• {tp}" for tp in coaching.talking_points
            )
            notes.append(JobNoteEntry(
                text=tp_text,
                timestamp=now,
                source=NoteSource.AGENT,
                note_type=NoteType.TALKING_POINTS,
            ))

        # 6. Coaching notes (strengths to highlight)
        if coaching.strengths_to_highlight:
            highlight_text = "**Strengths to Emphasize:**\n" + "\n".join(
                f"• {s}" for s in coaching.strengths_to_highlight
            )
            notes.append(JobNoteEntry(
                text=highlight_text,
                timestamp=now,
                source=NoteSource.AGENT,
                note_type=NoteType.COACHING_NOTES,
            ))

        # 7. Study Recommendations note
        if coaching.study_recommendations:
            study_text = "**Study Before Interviewing:**\n" + "\n".join(
                f"• {s}" for s in coaching.study_recommendations
            )
            notes.append(JobNoteEntry(
                text=study_text,
                timestamp=now,
                source=NoteSource.AGENT,
                note_type=NoteType.STUDY_RECOMMENDATIONS,
            ))

        # 8. Gaps to Address note
        if coaching.gaps_to_address:
            gaps_text = "**Skills Gaps to Address:**\n" + "\n".join(
                f"• {g}" for g in coaching.gaps_to_address
            )
            notes.append(JobNoteEntry(
                text=gaps_text,
                timestamp=now,
                source=NoteSource.AGENT,
                note_type=NoteType.COACHING_NOTES,
            ))

        # 9. Additional watch-outs from coaching
        if coaching.watch_outs:
            wo_text = "**Additional Watch-Outs:**\n" + "\n".join(
                f"• {w}" for w in coaching.watch_outs
            )
            notes.append(JobNoteEntry(
                text=wo_text,
                timestamp=now,
                source=NoteSource.AGENT,
                note_type=NoteType.WATCH_OUTS,
            ))

        # 10. RAG Evidence note (if any strong matches)
        if coaching.evidence_from_resume:
            strong_evidence = [e for e in coaching.evidence_from_resume if e.match_strength == "strong"]
            if strong_evidence:
                rag_text = "**Evidence from Career Documents:**\n"
                for ev in strong_evidence[:5]:  # Limit to 5
                    rag_text += f"\n**{ev.requirement}** (from {ev.source_document}):\n{ev.evidence_snippet}\n"
                notes.append(JobNoteEntry(
                    text=rag_text,
                    timestamp=now,
                    source=NoteSource.AGENT,
                    note_type=NoteType.RAG_EVIDENCE,
                    metadata={"evidence_count": len(strong_evidence)},
                ))

    # If we have requirement matches from RAG
    if requirement_matches:
        strong_matches = [m for m in requirement_matches if m.match_strength == "strong"]
        gaps = [m for m in requirement_matches if m.match_strength == "none"]

        if strong_matches or gaps:
            rag_summary = "**JD Requirements Analysis:**\n"
            if strong_matches:
                rag_summary += f"\n✅ **Strong Matches ({len(strong_matches)}):**\n"
                for m in strong_matches[:5]:
                    rag_summary += f"• {m.requirement}\n"
            if gaps:
                rag_summary += f"\n⚠️ **Potential Gaps ({len(gaps)}):**\n"
                for m in gaps[:5]:
                    rag_summary += f"• {m.requirement}\n"

            notes.append(JobNoteEntry(
                text=rag_summary,
                timestamp=now,
                source=NoteSource.AGENT,
                note_type=NoteType.RAG_EVIDENCE,
                metadata={
                    "strong_count": len(strong_matches),
                    "gap_count": len(gaps),
                },
            ))

    return notes


# Singleton instances
ai_analysis_service = AIAnalysisService()
ai_analysis_service_enhanced = AIAnalysisServiceEnhanced()
