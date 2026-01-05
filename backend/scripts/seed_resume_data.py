#!/usr/bin/env python3
"""
Script to export resume data from Meridian TypeScript files to JSON cache.

This script parses the TypeScript data files and creates a JSON cache
that the resume service can use without parsing TypeScript at runtime.

Usage:
    python -m scripts.seed_resume_data
"""

import json
import re
from pathlib import Path


# Default path to Meridian resume data
MERIDIAN_RESUME_PATH = Path("/Users/tomhundley/projects/trh/meridian/src/lib/resume")
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "resume_cache" / "resume_data.json"


def parse_personal_info(content: str) -> dict:
    """Extract personalInfo from TypeScript content."""
    match = re.search(
        r'export const personalInfo = \{([^}]+)\}',
        content,
        re.DOTALL
    )
    if not match:
        return {}

    obj_str = match.group(1)
    result = {}
    pattern = r'(\w+):\s*["\']([^"\']+)["\']'
    for m in re.finditer(pattern, obj_str):
        result[m.group(1)] = m.group(2)
    return result


def parse_roles(content: str) -> dict:
    """Extract role definitions from TypeScript content."""
    # This is a simplified parser - for complex data, manual JSON is preferred
    roles = {}

    role_types = ["cto", "vp", "director", "architect", "developer"]

    for role in role_types:
        # Find the role block
        pattern = rf'{role}:\s*\{{([^}}]+(?:\{{[^}}]*\}}[^}}]*)*)\}}'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            role_block = match.group(1)

            # Extract fields
            title_match = re.search(r'title:\s*["\']([^"\']+)["\']', role_block)
            headline_match = re.search(r'headline:\s*["\']([^"\']+)["\']', role_block)
            summary_match = re.search(r'summary:\s*["`]([^"`]+)["`]', role_block)

            roles[role] = {
                "id": role,
                "title": title_match.group(1) if title_match else role.upper(),
                "headline": headline_match.group(1) if headline_match else "",
                "summary": summary_match.group(1) if summary_match else "",
            }

    return roles


def create_default_resume_data() -> dict:
    """Create default resume data structure."""
    return {
        "personal_info": {
            "name": "Tom Hundley",
            "location": "Alpharetta, GA",
            "email": "tom@thomashundley.com",
            "phone": "404.822.8810",
            "linkedin": "https://www.linkedin.com/in/tomhundley/",
            "website": "https://thomashundley.com",
            "github": "https://github.com/tomhundley",
        },
        "roles": {
            "cto": {
                "id": "cto",
                "title": "Chief Technology Officer",
                "headline": "Technology Executive & AI Innovation Leader",
                "summary": "25+ year technology executive with deep expertise in AI transformation, platform architecture, and enterprise software development. Acting CTO for MDSi since 2017. Pioneer in agentic AI development where agents analyze, fix, and deploy code autonomously.",
            },
            "vp": {
                "id": "vp",
                "title": "VP of Software Development",
                "headline": "Software Development Executive",
                "summary": "Technology executive with 25+ years delivering enterprise solutions. Full P&L responsibility managing $500K-2M annual delivery. Built and scaled teams to 15 engineers with high retention through mentorship and career development.",
            },
            "director": {
                "id": "director",
                "title": "Director of Software Engineering",
                "headline": "Engineering Leader & Delivery Expert",
                "summary": "Engineering leader with 25+ years delivering complex enterprise systems. Expert in Agile methodologies, team leadership, and predictable delivery. Track record of clearing backlogs and improving delivery quality.",
            },
            "architect": {
                "id": "architect",
                "title": "Principal Solutions Architect",
                "headline": "Enterprise Architect & Platform Strategist",
                "summary": "Principal architect with 25+ years designing enterprise platforms. Expert in microservices, cloud-native architectures, and integration patterns. Designed systems for telecom, retail, healthcare, and manufacturing.",
            },
            "developer": {
                "id": "developer",
                "title": "Senior Software Engineer",
                "headline": "Full-Stack Engineer & Technical Lead",
                "summary": "Senior engineer with 25+ years hands-on development experience. Expert in C#, .NET, Azure, React, and Next.js. Passionate about clean code, mentorship, and continuous learning.",
            },
        },
        "experiences": [
            {
                "slug": "elegant-software-solutions",
                "company": "Elegant Software Solutions, Inc.",
                "location": "Alpharetta, GA",
                "period": "04/07 – Present",
                "available_roles": ["cto", "vp", "director", "architect", "developer"],
                "role_titles": {
                    "cto": [
                        {"title": "Chief Technology Officer", "period": "01/17 – Present"},
                    ],
                    "vp": [
                        {"title": "VP of Software Development", "period": "01/15 – Present"},
                    ],
                    "director": [
                        {"title": "Director of Software Development", "period": "04/07 – Present"},
                    ],
                    "architect": [
                        {"title": "Principal Architect", "period": "04/07 – Present"},
                    ],
                    "developer": [
                        {"title": "Lead Software Engineer", "period": "04/07 – Present"},
                    ],
                },
                "descriptions": {
                    "cto": [
                        "Defined technology strategy and AI governance across a multi-client portfolio",
                        "Pioneered agentic AI development with autonomous bug analysis and deployment",
                        "Directed 19-year MDSi relationship as acting CTO",
                        "Built platform standards across 540+ repos",
                    ],
                    "vp": [
                        "Full P&L responsibility for ESS operations, managing $500K-2M in annual delivery",
                        "Scaled teams to 15 engineers with high retention",
                        "Built hiring, onboarding, and career development programs",
                    ],
                    "director": [
                        "Cleared backlogs and improved delivery predictability through Agile/Scrum",
                        "Managed delivery across concurrent enterprise engagements",
                        "Led resource planning and roadmap execution across teams",
                    ],
                    "architect": [
                        "Designed enterprise architectures for telecom, AI platforms, and regulated industries",
                        "Built microservices platforms including Acuity v4 and Climb Analytics",
                        "Architected carrier integrations for Comcast, AT&T, Verizon, Cox",
                    ],
                    "developer": [
                        "Hands-on development across C#, .NET 8, Azure Functions, React, and Next.js",
                        "Built integration services, data pipelines, and automation",
                        "Created reusable frameworks and code generators",
                    ],
                },
            },
            {
                "slug": "mdsi",
                "company": "MDSi, Inc.",
                "location": "Alpharetta, GA",
                "period": "05/06 – Present",
                "available_roles": ["cto", "vp", "director", "architect", "developer"],
                "role_titles": {
                    "cto": [
                        {"title": "Acting CTO & Technology Partner", "period": "01/17 – Present"},
                    ],
                    "vp": [
                        {"title": "VP of Software Development", "period": "01/15 – Present"},
                    ],
                    "director": [
                        {"title": "Director of Software Development", "period": "01/15 – Present"},
                    ],
                    "architect": [
                        {"title": "Principal Architect", "period": "01/15 – Present"},
                    ],
                    "developer": [
                        {"title": "Lead Software Engineer", "period": "05/06 – Present"},
                    ],
                },
                "descriptions": {
                    "cto": [
                        "Assumed fractional CTO role in 2017 with full technology authority",
                        "Lead technology committee and set strategic direction",
                        "Led $1.5M AX09 to D365 F&O migration program",
                    ],
                    "vp": [
                        "MDSi gave all software development to ESS to run in 2015",
                        "Own technology budget, staffing levels, and vendor management",
                        "Established SDLC, ALM, and code review processes",
                    ],
                    "director": [
                        "Led consolidated development team after MDSi outsourcing",
                        "Implemented Agile methodologies and improved delivery predictability",
                        "Manage cross-functional teams across multiple product lines",
                    ],
                    "architect": [
                        "Unified enterprise platform merging legacy systems into modern stack",
                        "Designed microservices architecture for Acuity platform",
                        "Built carrier integration framework for major telecom providers",
                    ],
                    "developer": [
                        "Built and maintained 540+ repositories across enterprise systems",
                        "Developed carrier integrations, logistics automation, and reporting",
                        "Mentored team through code reviews and pair programming",
                    ],
                },
            },
        ],
        "skills": [
            {
                "category": "AI & Machine Learning",
                "items": ["Azure OpenAI", "RAG Systems", "Semantic Search", "Embeddings", "MCP", "Agentic AI"],
                "role_emphasis": {"cto": 5, "vp": 4, "director": 3, "architect": 5, "developer": 5},
                "proficiency": 5,
            },
            {
                "category": "Cloud & Infrastructure",
                "items": ["Azure", "Azure Functions", "App Service", "Service Bus", "Cosmos DB", "SQL Server"],
                "role_emphasis": {"cto": 4, "vp": 3, "director": 3, "architect": 5, "developer": 5},
                "proficiency": 5,
            },
            {
                "category": "Languages & Frameworks",
                "items": ["C#", ".NET 8", "TypeScript", "React", "Next.js", "Python"],
                "role_emphasis": {"cto": 3, "vp": 2, "director": 3, "architect": 4, "developer": 5},
                "proficiency": 5,
            },
            {
                "category": "Leadership",
                "items": ["Team Building", "Mentorship", "Strategic Planning", "P&L Management", "Vendor Management"],
                "role_emphasis": {"cto": 5, "vp": 5, "director": 5, "architect": 3, "developer": 2},
                "proficiency": 5,
            },
        ],
        "projects": [
            {
                "slug": "acuity-v4",
                "name": "Acuity v4 Platform",
                "client": "MDSi",
                "period": "2020 – Present",
                "summary": "Cloud-native microservices platform for telecom logistics",
                "technologies": ["C#", ".NET 8", "Azure Functions", "Cosmos DB", "React"],
                "role_relevance": {"cto": 5, "vp": 4, "director": 4, "architect": 5, "developer": 5},
            },
            {
                "slug": "climb-analytics",
                "name": "Climb Analytics",
                "client": "MDSi",
                "period": "2023 – Present",
                "summary": "AI-powered analytics platform with RAG and semantic search",
                "technologies": ["Azure OpenAI", "RAG", "Embeddings", "Next.js", "Cosmos DB"],
                "role_relevance": {"cto": 5, "vp": 4, "director": 3, "architect": 5, "developer": 5},
            },
        ],
        "education": {
            "degree": "Bachelor of Science",
            "field": "Hospitality Management",
            "school": "University of Central Florida",
            "year": "1999",
        },
        "certifications": [
            {"name": "Microsoft Certified Professional (MCP)", "issuer": "Microsoft"},
            {"name": "Brain Bench C# Master", "issuer": "Brain Bench"},
        ],
    }


def main():
    """Main entry point."""
    print("Seeding resume data...")

    # Try to parse from Meridian files, fall back to defaults
    data = create_default_resume_data()

    if MERIDIAN_RESUME_PATH.exists():
        data_file = MERIDIAN_RESUME_PATH / "data.ts"
        if data_file.exists():
            content = data_file.read_text()

            # Update personal info from source
            personal = parse_personal_info(content)
            if personal:
                data["personal_info"].update(personal)
                print(f"  Loaded personal info: {personal.get('name', 'Unknown')}")

    # Ensure output directory exists
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Write JSON cache
    with open(OUTPUT_PATH, "w") as f:
        json.dump(data, f, indent=2)

    print(f"  Wrote resume data to {OUTPUT_PATH}")
    print("Done!")


if __name__ == "__main__":
    main()
