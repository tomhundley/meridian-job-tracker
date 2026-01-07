"""Business logic services."""

from .resume_service import resume_service, ResumeService
from .jd_analyzer import detect_and_parse_jd, JDAnalysisResult, ExtractedRequirements
from .cover_letter_service import cover_letter_service, CoverLetterService
from .job_scraper import job_scraper, JobScraper, ScrapedJob, JobScrapeError
from .job_analysis_service import analyze_job, analyze_job_with_ai, JobAnalysisResult as JobFitAnalysis
from .ai_analysis_service import (
    ai_analysis_service,
    AIAnalysisService,
    ai_analysis_service_enhanced,
    AIAnalysisServiceEnhanced,
    generate_typed_notes,
)
from .analysis_cache import analysis_cache, AnalysisCache
from .sparkles_client import sparkles_client, SparklesClient
from .description_fetcher import description_fetcher, DescriptionFetcherService

__all__ = [
    "resume_service",
    "ResumeService",
    "detect_and_parse_jd",
    "JDAnalysisResult",
    "ExtractedRequirements",
    "cover_letter_service",
    "CoverLetterService",
    "job_scraper",
    "JobScraper",
    "ScrapedJob",
    "JobScrapeError",
    "analyze_job",
    "analyze_job_with_ai",
    "JobFitAnalysis",
    "ai_analysis_service",
    "AIAnalysisService",
    "ai_analysis_service_enhanced",
    "AIAnalysisServiceEnhanced",
    "generate_typed_notes",
    "analysis_cache",
    "AnalysisCache",
    "sparkles_client",
    "SparklesClient",
    "description_fetcher",
    "DescriptionFetcherService",
]
