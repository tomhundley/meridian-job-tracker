"""Job Description Analyzer - Ported from Meridian TypeScript."""

import re
from dataclasses import dataclass, field
from typing import Literal


# Keywords that strongly indicate a job description
JD_INDICATORS = {
    "strong": [
        "job description",
        "position summary",
        "role overview",
        "responsibilities",
        "qualifications",
        "requirements",
        "we are looking for",
        "we are seeking",
        "the ideal candidate",
        "you will",
        "you will be responsible",
        "what you'll do",
        "what we're looking for",
        "about the role",
        "about the position",
        "job responsibilities",
        "key responsibilities",
        "core responsibilities",
        "essential duties",
        "required skills",
        "required experience",
        "preferred qualifications",
        "nice to have",
        "must have",
        "minimum qualifications",
        "basic qualifications",
    ],
    "moderate": [
        "experience with",
        "experience in",
        "years of experience",
        "proficiency in",
        "knowledge of",
        "familiar with",
        "background in",
        "degree in",
        "bachelor",
        "master",
        "salary",
        "compensation",
        "benefits",
        "remote",
        "hybrid",
        "on-site",
        "full-time",
        "part-time",
        "contract",
        "apply now",
        "apply here",
        "equal opportunity",
        "eeo",
    ],
}

# Technology patterns to extract
TECH_PATTERNS = [
    # Languages
    r"\b(javascript|typescript|python|java|c\+\+|c#|ruby|go|golang|rust|kotlin|swift|scala|php|perl)\b",
    # Frontend
    r"\b(react|angular|vue|svelte|next\.?js|nuxt|gatsby|remix|astro|tailwind|css|sass|scss|html5?|webpack|vite)\b",
    # Backend
    r"\b(node\.?js|express|fastify|nest\.?js|django|flask|fastapi|spring|\.net|rails|laravel|asp\.net|graphql|rest|grpc)\b",
    # Cloud/Infra
    r"\b(aws|azure|gcp|google cloud|kubernetes|k8s|docker|terraform|ansible|jenkins|ci/cd|github actions|gitlab|vercel|netlify)\b",
    # Databases
    r"\b(postgresql|postgres|mysql|mongodb|redis|elasticsearch|dynamodb|cosmos ?db|supabase|firebase|sql server|oracle|cassandra)\b",
    # AI/ML
    r"\b(machine learning|deep learning|nlp|computer vision|tensorflow|pytorch|scikit-learn|openai|langchain|llm|gpt|claude|anthropic|rag)\b",
    # Tools/Concepts
    r"\b(git|agile|scrum|jira|confluence|figma|microservices|serverless|api|sdk|saas|devops|sre|mlops)\b",
]

# Experience extraction patterns
EXPERIENCE_PATTERNS = [
    r"(\d+)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp)",
    r"(?:minimum|at least|required)\s+(\d+)\s*(?:years?|yrs?)",
    r"(\d+)\s*-\s*(\d+)\s*(?:years?|yrs?)",
]

# Seniority level patterns
SENIORITY_PATTERNS = [
    (r"\b(principal|staff|distinguished|fellow)\b", "staff+"),
    (r"\b(senior|sr\.?|lead|team lead)\b", "senior"),
    (r"\b(mid[- ]?level|intermediate)\b", "mid"),
    (r"\b(junior|jr\.?|entry[- ]?level|associate|early career)\b", "junior"),
    (r"\b(intern|internship)\b", "intern"),
]

SeniorityLevel = Literal["intern", "junior", "mid", "senior", "staff+"]


@dataclass
class ExtractedRequirements:
    """Structured requirements extracted from a job description."""

    must_have: list[str] = field(default_factory=list)
    nice_to_have: list[str] = field(default_factory=list)
    technologies: list[str] = field(default_factory=list)
    years_experience: int | None = None
    seniority_level: SeniorityLevel | None = None
    education: list[str] = field(default_factory=list)
    responsibilities: list[str] = field(default_factory=list)


@dataclass
class JDSummary:
    """Summary information extracted from a job description."""

    job_title: str | None = None
    company: str | None = None
    location: str | None = None
    employment_type: str | None = None


@dataclass
class JDAnalysisResult:
    """Result of analyzing text for job description content."""

    is_jd: bool
    confidence: float
    requirements: ExtractedRequirements
    summary: JDSummary
    raw_text: str


def extract_technologies(text: str) -> list[str]:
    """Extract technology keywords from text."""
    technologies = set()
    for pattern in TECH_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # Normalize the technology name
            tech = match.lower().strip()
            # Handle variations
            if tech in ("golang", "go"):
                tech = "Go"
            elif tech in ("node.js", "nodejs"):
                tech = "Node.js"
            elif tech in ("next.js", "nextjs"):
                tech = "Next.js"
            elif tech in ("nest.js", "nestjs"):
                tech = "NestJS"
            elif tech == "typescript":
                tech = "TypeScript"
            elif tech == "javascript":
                tech = "JavaScript"
            elif tech == "python":
                tech = "Python"
            elif tech == "postgresql" or tech == "postgres":
                tech = "PostgreSQL"
            elif tech in ("cosmosdb", "cosmos db"):
                tech = "Cosmos DB"
            else:
                tech = match  # Keep original casing for others
            technologies.add(tech)
    return sorted(list(technologies))


def extract_years_experience(text: str) -> int | None:
    """Extract years of experience requirement."""
    for pattern in EXPERIENCE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Get the first match
            match = matches[0]
            if isinstance(match, tuple):
                # Range pattern - take the minimum
                return int(match[0])
            return int(match)
    return None


def extract_seniority_level(text: str) -> SeniorityLevel | None:
    """Extract seniority level from text."""
    for pattern, level in SENIORITY_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return level  # type: ignore
    return None


def extract_requirements(text: str) -> ExtractedRequirements:
    """Extract structured requirements from job description text."""
    requirements = ExtractedRequirements()

    # Extract technologies
    requirements.technologies = extract_technologies(text)

    # Extract years of experience
    requirements.years_experience = extract_years_experience(text)

    # Extract seniority level
    requirements.seniority_level = extract_seniority_level(text)

    # Extract education requirements
    education_patterns = [
        r"(?:bachelor'?s?|b\.?s\.?|b\.?a\.?)(?:\s+degree)?(?:\s+in\s+([^,\n]+))?",
        r"(?:master'?s?|m\.?s\.?|m\.?a\.?|mba)(?:\s+degree)?(?:\s+in\s+([^,\n]+))?",
        r"(?:ph\.?d\.?|doctorate)(?:\s+in\s+([^,\n]+))?",
    ]
    for pattern in education_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            requirements.education.append(pattern.split("(?:")[1].split("|")[0].replace("'?s?", "'s"))

    # Extract bullet points that look like requirements
    lines = text.split("\n")
    in_requirements_section = False
    in_nice_to_have_section = False

    for line in lines:
        line = line.strip()
        lower_line = line.lower()

        # Detect section headers
        if any(kw in lower_line for kw in ["requirements", "qualifications", "must have", "required"]):
            in_requirements_section = True
            in_nice_to_have_section = False
            continue
        elif any(kw in lower_line for kw in ["nice to have", "preferred", "bonus"]):
            in_nice_to_have_section = True
            in_requirements_section = False
            continue
        elif any(kw in lower_line for kw in ["responsibilities", "you will", "what you'll do"]):
            in_requirements_section = False
            in_nice_to_have_section = False
            continue

        # Extract bullet points
        if line.startswith(("-", "•", "*", "·")) or re.match(r"^\d+\.", line):
            bullet_text = re.sub(r"^[-•*·]\s*|\d+\.\s*", "", line).strip()
            if bullet_text:
                if in_nice_to_have_section:
                    requirements.nice_to_have.append(bullet_text)
                elif in_requirements_section:
                    requirements.must_have.append(bullet_text)

    return requirements


def extract_summary(text: str) -> JDSummary:
    """Extract summary information from job description."""
    summary = JDSummary()

    # Try to extract job title (usually in the first few lines or after "Job Title:")
    title_patterns = [
        r"(?:job title|position|role):\s*(.+?)(?:\n|$)",
        r"^#?\s*(.+?(?:engineer|developer|manager|director|lead|architect|analyst|designer)[^\n]*)",
    ]
    for pattern in title_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            summary.job_title = match.group(1).strip()
            break

    # Try to extract company
    company_patterns = [
        r"(?:company|employer|at|about):\s*(.+?)(?:\n|$)",
        r"(?:join|about)\s+([A-Z][A-Za-z0-9\s]+?)(?:\s+(?:is|as|team|we))",
    ]
    for pattern in company_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            summary.company = match.group(1).strip()
            break

    # Try to extract location
    location_patterns = [
        r"(?:location|based in|office):\s*(.+?)(?:\n|$)",
        r"\b(remote|hybrid|on-?site)\b",
    ]
    for pattern in location_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            summary.location = match.group(1).strip()
            break

    # Employment type
    type_patterns = [
        r"\b(full[- ]?time|part[- ]?time|contract|freelance|internship)\b",
    ]
    for pattern in type_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            summary.employment_type = match.group(1).strip()
            break

    return summary


def detect_and_parse_jd(text: str) -> JDAnalysisResult:
    """
    Detect if text is a job description and extract its structure.

    Returns an analysis result with confidence score and extracted information.
    """
    lower_text = text.lower()

    # Calculate confidence score based on indicator matches
    strong_matches = sum(1 for ind in JD_INDICATORS["strong"] if ind in lower_text)
    moderate_matches = sum(1 for ind in JD_INDICATORS["moderate"] if ind in lower_text)

    # Calculate confidence (0-1)
    max_strong_score = min(strong_matches * 0.15, 0.6)
    max_moderate_score = min(moderate_matches * 0.05, 0.3)
    confidence = min(max_strong_score + max_moderate_score + 0.1, 1.0)

    # Consider it a JD if confidence > 0.3 OR has at least 2 strong matches
    is_jd = confidence > 0.3 or strong_matches >= 2

    # Extract information
    requirements = extract_requirements(text)
    summary = extract_summary(text)

    return JDAnalysisResult(
        is_jd=is_jd,
        confidence=confidence,
        requirements=requirements,
        summary=summary,
        raw_text=text,
    )


def summarize_requirements(requirements: ExtractedRequirements) -> str:
    """Create a human-readable summary of extracted requirements."""
    parts = []

    if requirements.seniority_level:
        parts.append(f"Seniority: {requirements.seniority_level}")

    if requirements.years_experience:
        parts.append(f"Experience: {requirements.years_experience}+ years")

    if requirements.technologies:
        top_tech = requirements.technologies[:10]
        parts.append(f"Technologies: {', '.join(top_tech)}")

    if requirements.must_have:
        parts.append(f"Key requirements: {len(requirements.must_have)} items")

    return " | ".join(parts) if parts else "No specific requirements extracted"
