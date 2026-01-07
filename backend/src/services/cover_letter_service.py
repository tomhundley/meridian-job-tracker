"""Cover letter generation service using Claude API."""

from typing import Literal

from anthropic import Anthropic
import structlog

from src.config import settings
from src.models import CoverLetter, Job
from src.models.job import RoleType
from src.schemas.ai_analysis_coach import JDMatchResult

from .jd_analyzer import JDAnalysisResult, detect_and_parse_jd
from .resume_service import resume_service
from .sparkles_client import sparkles_client


class CoverLetterService:
    """Service for generating tailored cover letters."""

    def __init__(self):
        self.client = Anthropic(api_key=settings.anthropic_api_key) if settings.anthropic_api_key else None
        self.resume = resume_service
        self.sparkles = sparkles_client

    def analyze_job(self, job: Job) -> JDAnalysisResult:
        """Analyze a job description."""
        if not job.description_raw:
            # Return empty analysis for jobs without descriptions
            from .jd_analyzer import ExtractedRequirements, JDSummary
            return JDAnalysisResult(
                is_jd=False,
                confidence=0.0,
                requirements=ExtractedRequirements(),
                summary=JDSummary(job_title=job.title, company=job.company),
                raw_text="",
            )
        return detect_and_parse_jd(job.description_raw)

    def _build_prompt(
        self,
        job: Job,
        jd_analysis: JDAnalysisResult,
        target_role: RoleType,
        custom_instructions: str | None = None,
        tone: Literal["professional", "conversational"] = "professional",
        rag_context: str = "",
    ) -> str:
        """Build the cover letter generation prompt."""
        # Get resume data for the target role
        resume_data = self.resume.get_resume_for_role(target_role)
        personal = resume_data["personal_info"]
        experiences = resume_data["experiences"][:3]  # Top 3 experiences
        skills = resume_data["skills"][:5]  # Top 5 skill categories

        # Format experience bullets
        experience_text = ""
        for exp in experiences:
            titles = exp.get("titles", [])
            if titles:
                title = titles[0].get("title", "")
                period = titles[0].get("period", "")
                experience_text += f"\n### {title} at {exp['company']} ({period})\n"
                for desc in exp.get("descriptions", [])[:3]:
                    experience_text += f"- {desc}\n"

        # Format skills
        skills_text = ", ".join([
            item
            for skill in skills
            for item in skill.get("items", [])[:3]
        ])

        # Format requirements
        requirements = jd_analysis.requirements
        must_have_text = "\n".join(f"- {req}" for req in requirements.must_have[:10])
        tech_text = ", ".join(requirements.technologies[:15])

        # Tone instructions
        tone_instructions = {
            "professional": """
- Use formal, executive-level language
- Maintain confident but respectful tone
- Focus on strategic impact and leadership
- Keep a polished, business-appropriate style""",
            "conversational": """
- Use warm, approachable language
- Show personality while remaining professional
- Balance confidence with humility
- Write as if speaking to a colleague""",
        }

        # RAG context section
        rag_section = ""
        if rag_context:
            rag_section = f"""
## Evidence from Career Documents (USE THESE!)

The following are specific examples and achievements from my career
that directly match this job's requirements. Incorporate these:

{rag_context}
"""

        prompt = f"""Generate a professional cover letter for this position.

## Position
- Title: {job.title}
- Company: {job.company}
- Location: {job.location or "Not specified"}

## Job Requirements
### Must Have:
{must_have_text or "Not specified"}

### Technologies:
{tech_text or "Not specified"}

### Experience Required:
{requirements.years_experience or "Not specified"} years

## Candidate Profile ({resume_data['role_title']})
### Contact:
- Name: {personal['name']}
- Email: {personal['email']}
- Phone: {personal['phone']}
- LinkedIn: {personal['linkedin']}

### Summary:
{resume_data.get('summary', '')}

### Relevant Experience:
{experience_text}

### Key Skills:
{skills_text}
{rag_section}
## Tone Guidelines
{tone_instructions.get(tone, tone_instructions["professional"])}

## Instructions
1. Open with a strong hook connecting my experience to their needs
2. Highlight 2-3 specific achievements relevant to their requirements
3. If career evidence is provided above, reference those specific examples
4. Demonstrate knowledge of their technology stack
5. Show enthusiasm for the specific opportunity
6. Keep to 3-4 paragraphs
7. Be confident but not arrogant
8. Use specific metrics where available
9. Close with a call to action

{f"Additional instructions: {custom_instructions}" if custom_instructions else ""}

Generate the cover letter now. Do not include any preamble or explanation - just output the cover letter text starting with "Dear Hiring Manager," or similar greeting."""

        return prompt

    async def _get_rag_context(
        self,
        job: Job,
        jd_analysis: JDAnalysisResult,
        target_role: RoleType,
    ) -> tuple[str, list[dict]]:
        """
        Fetch RAG context for cover letter generation.

        Returns:
            Tuple of (formatted context string, list of evidence dicts for storage)
        """
        logger = structlog.get_logger(__name__)

        if not self.sparkles.is_configured:
            logger.warning("sparkles_not_configured_for_cover_letter")
            return "", []

        try:
            # Get job requirements to match
            requirements = (
                jd_analysis.requirements.must_have[:8] +
                jd_analysis.requirements.nice_to_have[:4]
            )

            if not requirements:
                return "", []

            # Match requirements against career documents
            matches = await self.sparkles.match_jd_requirements(
                requirements=requirements,
                threshold=0.45,
                limit_per_req=2,
            )

            if not matches:
                return "", []

            # Filter to strong and moderate matches
            relevant_matches = [m for m in matches if m.match_strength in ("strong", "moderate")]

            if not relevant_matches:
                return "", []

            # Build formatted context
            context_parts = []
            evidence_list = []

            for match in relevant_matches[:6]:  # Limit to 6 best matches
                if match.evidence:
                    context_parts.append(f"**{match.requirement}**")
                    context_parts.append(f"Evidence: {match.evidence[0]}")
                    context_parts.append("")

                    # Build evidence dict for storage
                    for top_match in match.top_matches[:1]:
                        evidence_list.append({
                            "requirement": match.requirement,
                            "match_strength": match.match_strength,
                            "evidence_snippet": top_match.evidence_snippet,
                            "source_document": top_match.source_document,
                        })

            logger.info(
                "rag_context_retrieved_for_cover_letter",
                job_id=str(job.id),
                matches_found=len(relevant_matches),
                evidence_items=len(evidence_list),
            )

            return "\n".join(context_parts), evidence_list

        except Exception as e:
            logger.error("rag_context_error_for_cover_letter", error=str(e))
            return "", []

    async def generate(
        self,
        job: Job,
        target_role: RoleType,
        custom_instructions: str | None = None,
        tone: Literal["professional", "conversational"] = "professional",
        use_rag: bool = True,
    ) -> dict:
        """
        Generate a tailored cover letter for a job.

        Args:
            job: The job to generate a cover letter for
            target_role: The role type to tailor the letter to
            custom_instructions: Optional custom instructions
            tone: Tone of the letter (professional or conversational)
            use_rag: Whether to use RAG for enhanced context (default: True)

        Returns dict with content and metadata, ready for creating CoverLetter model.
        """
        logger = structlog.get_logger(__name__)

        if not self.client:
            raise ValueError("Anthropic API key not configured")

        logger.info(
            "cover_letter_generation_start",
            job_id=str(job.id),
            company=job.company,
            title=job.title,
            target_role=target_role.value,
            use_rag=use_rag,
            tone=tone,
        )

        # Analyze job description
        jd_analysis = self.analyze_job(job)

        # Get RAG context if enabled
        rag_context = ""
        rag_evidence: list[dict] = []
        if use_rag:
            rag_context, rag_evidence = await self._get_rag_context(
                job=job,
                jd_analysis=jd_analysis,
                target_role=target_role,
            )

        # Build prompt with optional RAG context
        prompt = self._build_prompt(
            job=job,
            jd_analysis=jd_analysis,
            target_role=target_role,
            custom_instructions=custom_instructions,
            tone=tone,
            rag_context=rag_context,
        )

        # Generate with Claude
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        content = response.content[0].text

        result = {
            "content": content,
            "target_role": target_role,
            "generation_prompt": prompt,
            "model_used": "claude-sonnet-4-20250514",
            "rag_evidence": rag_evidence if rag_evidence else None,
            "rag_context_used": bool(rag_context),
        }

        logger.info(
            "cover_letter_generation_success",
            job_id=str(job.id),
            target_role=target_role.value,
            rag_context_used=bool(rag_context),
        )

        return result

    def generate_sync(
        self,
        job: Job,
        target_role: RoleType,
        custom_instructions: str | None = None,
        tone: Literal["professional", "conversational"] = "professional",
        use_rag: bool = True,
    ) -> dict:
        """
        Synchronous version of generate for non-async contexts.
        """
        import asyncio
        return asyncio.run(self.generate(job, target_role, custom_instructions, tone, use_rag))


# Singleton instance
cover_letter_service = CoverLetterService()
