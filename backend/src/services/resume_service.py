"""Resume service for accessing Meridian resume data."""

import json
import re
from pathlib import Path
from typing import Any

from src.config import settings
from src.models.job import RoleType


class ResumeService:
    """Service for accessing resume data from Meridian project."""

    def __init__(self, data_path: Path | None = None):
        self.data_path = data_path or Path(settings.resume_data_path)
        self._cache: dict[str, Any] = {}
        self._loaded = False

    def _load_data(self) -> None:
        """Load and parse resume data from TypeScript files."""
        if self._loaded:
            return

        # Try to load from JSON cache first
        cache_path = Path(__file__).parent.parent.parent / "data" / "resume_cache" / "resume_data.json"
        if cache_path.exists():
            with open(cache_path) as f:
                self._cache = json.load(f)
                self._loaded = True
                return

        # Parse TypeScript files if no cache exists
        data_file = self.data_path / "data.ts"
        if data_file.exists():
            self._parse_typescript_data(data_file)
            self._loaded = True

    def _parse_typescript_data(self, file_path: Path) -> None:
        """Parse TypeScript data file to extract resume information."""
        content = file_path.read_text()

        # Extract personalInfo
        personal_match = re.search(
            r'export const personalInfo = \{([^}]+)\}',
            content,
            re.DOTALL
        )
        if personal_match:
            personal_str = personal_match.group(1)
            self._cache["personal_info"] = self._parse_object(personal_str)

        # For complex nested structures, we'll use the JSON cache
        # This parser handles simple cases; complex cases use the seed script

    def _parse_object(self, obj_str: str) -> dict[str, str]:
        """Parse a simple TypeScript object literal."""
        result = {}
        # Match key: "value" or key: 'value' patterns
        pattern = r'(\w+):\s*["\']([^"\']+)["\']'
        for match in re.finditer(pattern, obj_str):
            key = match.group(1)
            value = match.group(2)
            result[key] = value
        return result

    @property
    def personal_info(self) -> dict[str, str]:
        """Get personal contact information."""
        self._load_data()
        return self._cache.get("personal_info", {
            "name": "Tom Hundley",
            "location": "Alpharetta, GA",
            "email": "tom@thomashundley.com",
            "phone": "404.822.8810",
            "linkedin": "https://www.linkedin.com/in/tomhundley/",
            "website": "https://thomashundley.com",
            "github": "https://github.com/tomhundley",
        })

    def get_role_definition(self, role: RoleType) -> dict[str, Any]:
        """Get role definition including title, headline, summary."""
        self._load_data()
        roles = self._cache.get("roles", {})
        return roles.get(role.value, {})

    def get_experiences_for_role(self, role: RoleType) -> list[dict[str, Any]]:
        """Get experiences filtered and formatted for a specific role."""
        self._load_data()
        experiences = self._cache.get("experiences", [])

        result = []
        for exp in experiences:
            if role.value not in exp.get("available_roles", []):
                continue

            # Get role-specific titles and descriptions
            role_titles = exp.get("role_titles", {}).get(role.value, [])
            descriptions = exp.get("descriptions", {}).get(role.value, [])

            result.append({
                "company": exp.get("company"),
                "location": exp.get("location"),
                "period": exp.get("period"),
                "titles": role_titles,
                "descriptions": descriptions,
            })

        return result

    def get_skills_for_role(self, role: RoleType) -> list[dict[str, Any]]:
        """Get skills prioritized for a specific role."""
        self._load_data()
        skills = self._cache.get("skills", [])

        # Sort by role emphasis
        def get_emphasis(skill: dict) -> int:
            return skill.get("role_emphasis", {}).get(role.value, 3)

        sorted_skills = sorted(skills, key=get_emphasis, reverse=True)
        return sorted_skills

    def get_projects_for_role(self, role: RoleType, limit: int = 10) -> list[dict[str, Any]]:
        """Get top projects for a specific role."""
        self._load_data()
        projects = self._cache.get("projects", [])

        # Filter and sort by role relevance
        def get_relevance(project: dict) -> int:
            return project.get("role_relevance", {}).get(role.value, 3)

        sorted_projects = sorted(projects, key=get_relevance, reverse=True)
        return sorted_projects[:limit]

    def get_resume_for_role(self, role: RoleType) -> dict[str, Any]:
        """Get complete resume data formatted for a specific role."""
        role_def = self.get_role_definition(role)

        return {
            "personal_info": self.personal_info,
            "role": role.value,
            "role_title": role_def.get("title", role.value.upper()),
            "headline": role_def.get("headline", ""),
            "summary": role_def.get("summary", ""),
            "experiences": self.get_experiences_for_role(role),
            "skills": self.get_skills_for_role(role),
            "projects": self.get_projects_for_role(role),
        }


# Singleton instance
resume_service = ResumeService()
