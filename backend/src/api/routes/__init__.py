"""API routes."""

from fastapi import APIRouter

from .jobs import router as jobs_router
from .cover_letters import router as cover_letters_router
from .emails import router as emails_router
from .health import router as health_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["health"])
api_router.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
api_router.include_router(cover_letters_router, prefix="/cover-letters", tags=["cover-letters"])
api_router.include_router(emails_router, prefix="/emails", tags=["emails"])
