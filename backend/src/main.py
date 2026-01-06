"""FastAPI application entry point."""

import time
import uvicorn
import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import api_router
from src.config import settings
from src.config.logging import setup_logging
from src.middleware import add_request_id_middleware, init_rate_limiting, register_error_handlers

setup_logging()
logger = structlog.get_logger("api")

app = FastAPI(
    title="Meridian Job Tracker",
    description="Job tracking and application automation API",
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

add_request_id_middleware(app)
register_error_handlers(app)
init_rate_limiting(app)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3005",
        "https://localhost:3005",
        # Add Vercel deployment URL when ready
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log request/response details."""
    start_time = time.monotonic()
    response = await call_next(request)
    duration_ms = (time.monotonic() - start_time) * 1000
    logger.info(
        "request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round(duration_ms, 2),
        request_id=getattr(request.state, "request_id", None),
    )
    return response


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "name": "Meridian Job Tracker",
        "version": "0.1.0",
        "docs": "/docs" if settings.debug else None,
    }


def run_server() -> None:
    """Run the FastAPI server."""
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    run_server()
