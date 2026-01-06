"""Webhook registration endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy import select

from src.api.deps import DbSession, require_permissions
from src.models import Webhook
from src.schemas import WebhookCreate, WebhookResponse

router = APIRouter()


@router.get(
    "",
    response_model=list[WebhookResponse],
    summary="List webhooks",
    description="List registered webhooks.",
    dependencies=[Depends(require_permissions(["webhooks:read"]))],
)
async def list_webhooks(db: DbSession) -> list[Webhook]:
    """List all webhooks."""
    result = await db.execute(select(Webhook).order_by(Webhook.created_at.desc()))
    return list(result.scalars().all())


@router.post(
    "",
    response_model=WebhookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register webhook",
    description="Register a webhook for event notifications.",
    dependencies=[Depends(require_permissions(["webhooks:write"]))],
)
async def create_webhook(
    db: DbSession,
    webhook_in: WebhookCreate,
) -> Webhook:
    """Register a webhook."""
    webhook = Webhook(
        url=str(webhook_in.url),
        events=webhook_in.events,
        secret=webhook_in.secret,
        is_active=webhook_in.is_active,
    )
    db.add(webhook)
    await db.flush()
    await db.refresh(webhook)
    return webhook
