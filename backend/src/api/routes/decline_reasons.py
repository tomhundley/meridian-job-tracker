"""Decline reasons API endpoints."""

from collections import defaultdict

from fastapi import APIRouter
from sqlalchemy import select

from src.api.deps import DbSession
from src.models.decline_reason import (
    CompanyDeclineReason,
    UserDeclineReason,
    COMPANY_DECLINE_CATEGORIES,
    USER_DECLINE_CATEGORIES,
)
from src.schemas.decline_reason import (
    CategoryWithReasons,
    DeclineReasonResponse,
    DeclineReasonsListResponse,
)

router = APIRouter()


@router.get(
    "/user",
    response_model=DeclineReasonsListResponse,
    summary="List user decline reasons",
    description="Get all active user decline reasons grouped by category.",
)
async def list_user_decline_reasons(db: DbSession) -> DeclineReasonsListResponse:
    """List all active user decline reasons grouped by category."""
    result = await db.execute(
        select(UserDeclineReason)
        .where(UserDeclineReason.is_active == True)
        .order_by(UserDeclineReason.category, UserDeclineReason.sort_order)
    )
    reasons = result.scalars().all()

    # Group by category
    by_category: dict[str, list[DeclineReasonResponse]] = defaultdict(list)
    for reason in reasons:
        by_category[reason.category].append(
            DeclineReasonResponse(
                code=reason.code,
                display_name=reason.display_name,
                category=reason.category,
                description=reason.description,
            )
        )

    # Build response with category display names
    categories = []
    for cat_name, cat_display in USER_DECLINE_CATEGORIES.items():
        if cat_name in by_category:
            categories.append(
                CategoryWithReasons(
                    name=cat_name,
                    display_name=cat_display,
                    reasons=by_category[cat_name],
                )
            )

    return DeclineReasonsListResponse(categories=categories)


@router.get(
    "/company",
    response_model=DeclineReasonsListResponse,
    summary="List company decline reasons",
    description="Get all active company decline reasons grouped by category.",
)
async def list_company_decline_reasons(db: DbSession) -> DeclineReasonsListResponse:
    """List all active company decline reasons grouped by category."""
    result = await db.execute(
        select(CompanyDeclineReason)
        .where(CompanyDeclineReason.is_active == True)
        .order_by(CompanyDeclineReason.category, CompanyDeclineReason.sort_order)
    )
    reasons = result.scalars().all()

    # Group by category
    by_category: dict[str, list[DeclineReasonResponse]] = defaultdict(list)
    for reason in reasons:
        by_category[reason.category].append(
            DeclineReasonResponse(
                code=reason.code,
                display_name=reason.display_name,
                category=reason.category,
                description=reason.description,
            )
        )

    # Build response with category display names
    categories = []
    for cat_name, cat_display in COMPANY_DECLINE_CATEGORIES.items():
        if cat_name in by_category:
            categories.append(
                CategoryWithReasons(
                    name=cat_name,
                    display_name=cat_display,
                    reasons=by_category[cat_name],
                )
            )

    return DeclineReasonsListResponse(categories=categories)
