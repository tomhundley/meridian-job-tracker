"""Rate limiting utilities."""

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from slowapi.extension import _rate_limit_exceeded_handler

from fastapi import FastAPI

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


def init_rate_limiting(app: FastAPI) -> None:
    """Attach rate limiting middleware and handlers."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
