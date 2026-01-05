"""FastAPI application entry point."""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import api_router
from src.config import settings

app = FastAPI(
    title="Meridian Job Tracker",
    description="Job tracking and application automation API",
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://localhost:3000",
        # Add Vercel deployment URL when ready
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


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
