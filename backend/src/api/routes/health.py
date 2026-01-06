"""Health check endpoints."""

from datetime import datetime

from fastapi import APIRouter
from sqlalchemy import text

from src.api.deps import DbSession

router = APIRouter()


@router.get(
    "/health",
    summary="Health check",
    description="Basic service health check.",
)
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "service": "meridian-job-tracker"}


async def _build_readiness_payload(db: DbSession) -> dict:
    await db.execute(text("SELECT 1"))
    return {
        "status": "ready",
        "database": "connected",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get(
    "/health/ready",
    summary="Readiness check",
    description="Readiness check including database connectivity.",
)
async def readiness_check(db: DbSession) -> dict:
    """Readiness check endpoint."""
    return await _build_readiness_payload(db)


@router.get(
    "/ready",
    summary="Readiness check (legacy)",
    description="Legacy readiness check including database connectivity.",
)
async def readiness_check_legacy(db: DbSession) -> dict:
    """Legacy readiness check endpoint."""
    return await _build_readiness_payload(db)
