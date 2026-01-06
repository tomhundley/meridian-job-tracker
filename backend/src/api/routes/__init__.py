"""API routes."""

from fastapi import APIRouter

from .jobs import router as jobs_router
from .cover_letters import router as cover_letters_router
from .emails import router as emails_router
from .agents import router as agents_router
from .webhooks import router as webhooks_router
from .health import router as health_router
from .discovery import router as discovery_router
from .decline_reasons import router as decline_reasons_router
from .job_contacts import router as job_contacts_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["health"])
api_router.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
api_router.include_router(cover_letters_router, prefix="/cover-letters", tags=["cover-letters"])
api_router.include_router(emails_router, prefix="/emails", tags=["emails"])
api_router.include_router(agents_router, prefix="/agents", tags=["agents"])
api_router.include_router(webhooks_router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(discovery_router)
api_router.include_router(decline_reasons_router, prefix="/decline-reasons", tags=["decline-reasons"])
api_router.include_router(job_contacts_router, prefix="/jobs/{job_id}/contacts", tags=["job-contacts"])
