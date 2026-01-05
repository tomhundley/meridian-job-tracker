"""Cover letter generation service using Claude API."""

from anthropic import Anthropic

from src.config import settings
from src.models import CoverLetter, Job
from src.models.job import RoleType

from .jd_analyzer import JDAnalysisResult, detect_and_parse_jd
from .resume_service import resume_service


class CoverLetterService:
    """Service for generating tailored cover letters."""

    def __init__(self):
        self.client = Anthropic(api_key=settings.anthropic_api_key) if settings.anthropic_api_key else None
        self.resume = resume_service

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

## Instructions
1. Open with a strong hook connecting my experience to their needs
2. Highlight 2-3 specific achievements relevant to their requirements
3. Demonstrate knowledge of their technology stack
4. Show enthusiasm for the specific opportunity
5. Keep to 3-4 paragraphs
6. Be confident but not arrogant
7. Use specific metrics where available
8. Close with a call to action

{f"Additional instructions: {custom_instructions}" if custom_instructions else ""}

Generate the cover letter now. Do not include any preamble or explanation - just output the cover letter text starting with "Dear Hiring Manager," or similar greeting."""

        return prompt

    async def generate(
        self,
        job: Job,
        target_role: RoleType,
        custom_instructions: str | None = None,
    ) -> dict:
        """
        Generate a tailored cover letter for a job.

        Returns dict with content and metadata, ready for creating CoverLetter model.
        """
        if not self.client:
            raise ValueError("Anthropic API key not configured")

        # Analyze job description
        jd_analysis = self.analyze_job(job)

        # Build prompt
        prompt = self._build_prompt(
            job=job,
            jd_analysis=jd_analysis,
            target_role=target_role,
            custom_instructions=custom_instructions,
        )

        # Generate with Claude
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        content = response.content[0].text

        return {
            "content": content,
            "target_role": target_role,
            "generation_prompt": prompt,
            "model_used": "claude-sonnet-4-20250514",
        }

    def generate_sync(
        self,
        job: Job,
        target_role: RoleType,
        custom_instructions: str | None = None,
    ) -> dict:
        """
        Synchronous version of generate for non-async contexts.
        """
        import asyncio
        return asyncio.run(self.generate(job, target_role, custom_instructions))


# Singleton instance
cover_letter_service = CoverLetterService()
