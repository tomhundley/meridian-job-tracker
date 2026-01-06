"""Job Analysis Service - AI detection and fit scoring."""

from dataclasses import dataclass

from src.models.job import RoleType
from src.services.jd_analyzer import (
    detect_and_parse_jd,
    extract_technologies,
    JDAnalysisResult,
)
from src.services.resume_service import resume_service


# AI/ML technologies that indicate an AI-forward company
AI_FORWARD_KEYWORDS = {
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "tensorflow", "pytorch", "scikit-learn", "openai",
    "langchain", "llm", "gpt", "claude", "anthropic", "rag", "retrieval augmented",
    "ai", "artificial intelligence", "ml", "generative ai", "gen ai", "genai",
    "vector database", "embeddings", "transformer", "neural network",
    "hugging face", "huggingface", "fine-tuning", "prompt engineering",
}

# Keywords that strongly indicate AI-forward culture (not just using AI tools)
AI_CULTURE_INDICATORS = {
    "ai-first", "ai first", "ai-native", "ai native", "ai-forward", "ai forward",
    "building ai", "developing ai", "ai product", "ai platform", "ai startup",
    "llm product", "ai company", "ml platform", "ai infrastructure",
}


@dataclass
class JobAnalysisResult:
    """Result of analyzing a job posting."""

    is_ai_forward: bool
    ai_confidence: float  # 0-1 how confident we are it's AI-forward
    suggested_priority: int  # 0-100 fit score
    suggested_role: RoleType | None
    technologies_matched: list[str]
    technologies_missing: list[str]
    years_experience_required: int | None
    seniority_level: str | None
    analysis_notes: list[str]


def analyze_job(
    description: str,
    title: str | None = None,
    company: str | None = None,
) -> JobAnalysisResult:
    """
    Analyze a job posting to determine AI-forward status and fit.

    Args:
        description: The job description text
        title: Optional job title for additional context
        company: Optional company name for additional context

    Returns:
        JobAnalysisResult with AI detection, fit scoring, and suggestions
    """
    # Combine all text for analysis
    full_text = " ".join(filter(None, [title, company, description]))
    lower_text = full_text.lower()

    # Parse the job description
    jd_result = detect_and_parse_jd(description)

    # Detect AI-forward status
    is_ai_forward, ai_confidence = _detect_ai_forward(lower_text, jd_result)

    # Get technologies from job
    job_technologies = set(t.lower() for t in jd_result.requirements.technologies)

    # Match against resume skills
    my_skills = _get_my_skills()
    matched = [t for t in jd_result.requirements.technologies if t.lower() in my_skills]
    missing = [t for t in jd_result.requirements.technologies if t.lower() not in my_skills]

    # Suggest role based on title and requirements
    suggested_role = _suggest_role(title, jd_result)

    # Calculate priority/fit score
    priority, notes = _calculate_fit_score(
        jd_result,
        title,
        matched,
        missing,
        is_ai_forward,
        suggested_role,
    )

    return JobAnalysisResult(
        is_ai_forward=is_ai_forward,
        ai_confidence=ai_confidence,
        suggested_priority=priority,
        suggested_role=suggested_role,
        technologies_matched=matched,
        technologies_missing=missing,
        years_experience_required=jd_result.requirements.years_experience,
        seniority_level=jd_result.requirements.seniority_level,
        analysis_notes=notes,
    )


def _detect_ai_forward(lower_text: str, jd_result: JDAnalysisResult) -> tuple[bool, float]:
    """Detect if the job is at an AI-forward company."""
    # Check for AI culture indicators (strongest signal)
    culture_matches = sum(1 for kw in AI_CULTURE_INDICATORS if kw in lower_text)
    if culture_matches > 0:
        return True, min(0.9 + culture_matches * 0.05, 1.0)

    # Check for AI/ML technologies in requirements
    job_tech_lower = {t.lower() for t in jd_result.requirements.technologies}
    ai_tech_matches = len(job_tech_lower & AI_FORWARD_KEYWORDS)

    # Check for AI keywords in general text
    ai_keyword_matches = sum(1 for kw in AI_FORWARD_KEYWORDS if kw in lower_text)

    # Calculate confidence
    if ai_tech_matches >= 3:
        return True, min(0.7 + ai_tech_matches * 0.05, 0.95)
    elif ai_tech_matches >= 1 or ai_keyword_matches >= 3:
        confidence = min(0.4 + ai_tech_matches * 0.15 + ai_keyword_matches * 0.05, 0.8)
        return confidence > 0.5, confidence

    return False, 0.1


def _get_my_skills() -> set[str]:
    """Get my skills from resume service."""
    skills = resume_service.get_skills_for_role(RoleType.CTO)
    skill_set = set()
    for skill in skills:
        name = skill.get("name", "").lower()
        skill_set.add(name)
        # Also add common variations
        if "." in name:
            skill_set.add(name.replace(".", ""))
        if " " in name:
            skill_set.add(name.replace(" ", ""))

    # Add common aliases
    aliases = {
        "python": {"python3", "py"},
        "javascript": {"js", "es6", "ecmascript"},
        "typescript": {"ts"},
        "postgresql": {"postgres", "psql"},
        "node.js": {"nodejs", "node"},
        "react": {"reactjs", "react.js"},
        "aws": {"amazon web services"},
        "gcp": {"google cloud", "google cloud platform"},
    }
    expanded_skills = set(skill_set)
    for skill in skill_set:
        if skill in aliases:
            expanded_skills.update(aliases[skill])
    for main, alts in aliases.items():
        if any(alt in skill_set for alt in alts):
            expanded_skills.add(main)

    return expanded_skills


def _suggest_role(title: str | None, jd_result: JDAnalysisResult) -> RoleType | None:
    """Suggest the best role type based on job title and requirements."""
    if not title:
        return None

    title_lower = title.lower()

    # Check for explicit role matches
    if any(kw in title_lower for kw in ["cto", "chief technology", "chief technical"]):
        return RoleType.CTO
    if any(kw in title_lower for kw in ["vp ", "vice president", "svp ", "evp "]):
        return RoleType.VP
    if any(kw in title_lower for kw in ["director", "head of"]):
        return RoleType.DIRECTOR
    if any(kw in title_lower for kw in ["architect", "principal"]):
        return RoleType.ARCHITECT

    # Check seniority from JD analysis
    seniority = jd_result.requirements.seniority_level
    if seniority == "staff+":
        return RoleType.ARCHITECT
    elif seniority == "senior":
        return RoleType.DIRECTOR

    return None


def _calculate_fit_score(
    jd_result: JDAnalysisResult,
    title: str | None,
    matched_tech: list[str],
    missing_tech: list[str],
    is_ai_forward: bool,
    suggested_role: RoleType | None,
) -> tuple[int, list[str]]:
    """Calculate a fit score (0-100) and generate analysis notes."""
    score = 50  # Start at middle
    notes = []

    # Role alignment (major factor)
    if suggested_role:
        if suggested_role in [RoleType.CTO, RoleType.VP]:
            score += 20
            notes.append(f"Executive role alignment: {suggested_role.value}")
        elif suggested_role == RoleType.DIRECTOR:
            score += 15
            notes.append("Director-level role")
        elif suggested_role == RoleType.ARCHITECT:
            score += 10
            notes.append("Architecture/Principal role")

    # Technology match (important factor)
    total_tech = len(matched_tech) + len(missing_tech)
    if total_tech > 0:
        match_ratio = len(matched_tech) / total_tech
        tech_score = int(match_ratio * 20)
        score += tech_score
        if match_ratio >= 0.8:
            notes.append(f"Strong tech match: {len(matched_tech)}/{total_tech}")
        elif match_ratio >= 0.5:
            notes.append(f"Good tech match: {len(matched_tech)}/{total_tech}")
        elif match_ratio < 0.3 and total_tech > 3:
            notes.append(f"Tech gap: missing {', '.join(missing_tech[:3])}")
            score -= 10

    # AI-forward bonus (for interest alignment)
    if is_ai_forward:
        score += 10
        notes.append("AI-forward company")

    # Experience level check
    years_req = jd_result.requirements.years_experience
    if years_req:
        if years_req <= 15:  # Assuming 15+ years experience
            score += 5
            notes.append(f"Experience requirement: {years_req}+ years (match)")
        elif years_req > 20:
            notes.append(f"High experience requirement: {years_req}+ years")

    # Title relevance
    if title:
        title_lower = title.lower()
        if any(kw in title_lower for kw in ["software", "engineering", "technology", "technical"]):
            score += 5
            notes.append("Technology-focused role")
        if any(kw in title_lower for kw in ["remote", "distributed"]):
            score += 3
            notes.append("Remote-friendly")

    # Clamp score to 0-100
    score = max(0, min(100, score))

    return score, notes


# Singleton instance
job_analysis_service = analyze_job
