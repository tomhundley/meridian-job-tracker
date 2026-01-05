"""Application settings using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str = "postgresql+asyncpg://meridian:meridian@localhost:5432/meridian_jobs"

    # API Authentication
    api_key: str = "change-me-in-production"

    # Anthropic API
    anthropic_api_key: str = ""

    # LinkedIn Credentials (for browser automation)
    linkedin_email: str = ""
    linkedin_password: str = ""

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # Environment
    environment: Literal["development", "staging", "production"] = "development"

    # Paths
    resume_data_path: str = "/Users/tomhundley/projects/trh/meridian/src/lib/resume"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
