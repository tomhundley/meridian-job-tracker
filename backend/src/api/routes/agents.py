"""Agent management endpoints."""

import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from src.api.deps import DbSession, require_permissions
from src.models import Agent
from src.schemas import AgentCreate, AgentResponse

router = APIRouter()


def _generate_api_key() -> str:
    return f"agent_{secrets.token_urlsafe(32)}"


@router.post(
    "",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create agent",
    description="Create a new agent API key with scoped permissions.",
    dependencies=[Depends(require_permissions(["agents:write"]))],
)
async def create_agent(
    db: DbSession,
    agent_in: AgentCreate,
) -> Agent:
    """Create a new agent."""
    existing = (await db.execute(select(Agent).where(Agent.name == agent_in.name))).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Agent name already exists",
        )

    api_key = _generate_api_key()
    agent = Agent(
        name=agent_in.name,
        api_key=api_key,
        permissions=agent_in.permissions,
    )
    db.add(agent)
    await db.flush()
    await db.refresh(agent)
    return agent
