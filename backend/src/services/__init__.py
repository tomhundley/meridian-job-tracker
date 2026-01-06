"""Business logic services."""

from .resume_service import resume_service, ResumeService
from .jd_analyzer import detect_and_parse_jd, JDAnalysisResult, ExtractedRequirements
from .cover_letter_service import cover_letter_service, CoverLetterService
from .job_scraper import job_scraper, JobScraper, ScrapedJob, JobScrapeError
from .job_analysis_service import analyze_job, JobAnalysisResult as JobFitAnalysis

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
    "JobFitAnalysis",
]
