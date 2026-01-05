"""API dependencies for dependency injection."""

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_db, settings


async def verify_api_key(x_api_key: Annotated[str, Header()]) -> str:
    """Verify API key from request header."""
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )
    return x_api_key


# Type aliases for dependencies
DbSession = Annotated[AsyncSession, Depends(get_db)]
ApiKey = Annotated[str, Depends(verify_api_key)]
