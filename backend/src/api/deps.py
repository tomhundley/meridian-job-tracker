"""API dependencies for dependency injection."""

from dataclasses import dataclass
from typing import Annotated, Iterable
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_db, settings
from src.models import Agent


@dataclass(frozen=True)
class AuthContext:
    """Authenticated request context."""

    api_key: str
    is_admin: bool
    permissions: set[str]
    agent_id: UUID | None = None
    agent_name: str | None = None


# Type aliases for dependencies
DbSession = Annotated[AsyncSession, Depends(get_db)]


def _permission_allowed(granted: set[str], required: str) -> bool:
    if "*" in granted:
        return True
    if required in granted:
        return True
    prefix = f"{required.split(':', 1)[0]}:*"
    return prefix in granted


async def verify_api_key(
    db: DbSession,
    x_api_key: Annotated[str | None, Header()] = None,
) -> AuthContext:
    """Verify API key from request header."""
    if settings.debug and settings.local_dev_bypass:
        return AuthContext(
            api_key=x_api_key or "local-dev",
            is_admin=True,
            permissions={"*"},
        )

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )

    if x_api_key == settings.api_key:
        return AuthContext(api_key=x_api_key, is_admin=True, permissions={"*"})

    result = await db.execute(
        select(Agent).where(
            Agent.api_key == x_api_key,
            Agent.is_active.is_(True),
        )
    )
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    return AuthContext(
        api_key=x_api_key,
        is_admin=False,
        permissions=set(agent.permissions or []),
        agent_id=agent.id,
        agent_name=agent.name,
    )


def require_permissions(required: Iterable[str]):
    """Dependency factory for permission checks."""

    required_list = tuple(required)

    async def checker(auth: AuthContext = Depends(verify_api_key)) -> AuthContext:
        if auth.is_admin:
            return auth
        missing = [
            permission
            for permission in required_list
            if not _permission_allowed(auth.permissions, permission)
        ]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permissions: {', '.join(missing)}",
            )
        return auth

    return checker


ApiKey = Annotated[AuthContext, Depends(verify_api_key)]
