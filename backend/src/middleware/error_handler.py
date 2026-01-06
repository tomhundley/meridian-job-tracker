"""Global error handling middleware."""

from uuid import uuid4

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.config import settings

logger = structlog.get_logger(__name__)


def add_request_id_middleware(app: FastAPI) -> None:
    """Attach request ID middleware."""

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


def register_error_handlers(app: FastAPI) -> None:
    """Register global exception handlers."""

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", None)
        logger.exception(
            "unhandled_exception",
            request_id=request_id,
            path=str(request.url),
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": str(exc) if settings.debug else "An error occurred",
                "request_id": request_id,
            },
        )
