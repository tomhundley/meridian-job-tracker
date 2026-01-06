"""Pytest fixtures for backend tests."""

import asyncio
import os

import pytest
import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.config import settings
from src.config.database import Base, get_db
from src.main import app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    db_url = os.getenv("TEST_DATABASE_URL")
    if not db_url:
        pytest.skip("Set TEST_DATABASE_URL to run database-backed tests.")

    engine = create_async_engine(db_url, poolclass=NullPool)

    async with engine.begin() as conn:
        await conn.execute(
            text(
                """
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'job_status') THEN
                        CREATE TYPE job_status AS ENUM (
                            'saved',
                            'researching',
                            'ready_to_apply',
                            'applying',
                            'applied',
                            'interviewing',
                            'offer',
                            'rejected',
                            'withdrawn',
                            'archived'
                        );
                    END IF;

                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'role_type') THEN
                        CREATE TYPE role_type AS ENUM (
                            'cto',
                            'vp',
                            'director',
                            'architect',
                            'developer'
                        );
                    END IF;

                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'application_method') THEN
                        CREATE TYPE application_method AS ENUM (
                            'linkedin_quick_apply',
                            'linkedin_full_apply',
                            'company_website',
                            'email',
                            'referral',
                            'recruiter',
                            'manual'
                        );
                    END IF;
                END $$;
                """
            )
        )
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        # Seed decline reason lookup tables (separate statements for asyncpg)
        await conn.execute(
            text(
                """
                INSERT INTO user_decline_reasons (code, display_name, category, sort_order, is_active, created_at)
                VALUES
                    ('salary_too_low', 'Salary below expectations', 'compensation', 1, true, NOW()),
                    ('not_remote', 'Not fully remote', 'location', 1, true, NOW()),
                    ('wrong_tech_stack', 'Technology stack not preferred', 'role_fit', 1, true, NOW()),
                    ('found_better', 'Found better opportunity', 'personal', 1, true, NOW()),
                    ('other', 'Other reason', 'personal', 99, true, NOW())
                ON CONFLICT (code) DO NOTHING
                """
            )
        )
        await conn.execute(
            text(
                """
                INSERT INTO company_decline_reasons (code, display_name, category, sort_order, is_active, created_at)
                VALUES
                    ('selected_other', 'Selected another candidate', 'candidate_selection', 1, true, NOW()),
                    ('insufficient_experience', 'Not enough experience', 'experience_skills', 1, true, NOW()),
                    ('failed_technical', 'Did not pass technical assessment', 'experience_skills', 2, true, NOW()),
                    ('ghosted', 'No response / ghosted', 'other', 1, true, NOW()),
                    ('other', 'Other reason', 'other', 99, true, NOW())
                ON CONFLICT (code) DO NOTHING
                """
            )
        )

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(engine):
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def api_key_header():
    return {"X-API-Key": settings.api_key}
