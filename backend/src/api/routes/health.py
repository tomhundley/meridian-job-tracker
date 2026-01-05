"""Health check endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "service": "meridian-job-tracker"}


@router.get("/ready")
async def readiness_check() -> dict:
    """Readiness check endpoint."""
    # TODO: Add database connectivity check
    return {"status": "ready"}
