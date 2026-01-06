"""Pytest fixtures for backend tests.

Tests use transaction isolation - each test runs in a transaction that is
rolled back at the end, so no test data persists to the database.
"""

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


# Use production database URL - tests run in transactions that rollback
TEST_DB_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://meridian:meridian@localhost:5434/meridian_jobs"
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    """Create database engine for tests.

    Uses the production database with transaction isolation.
    Each test runs in a transaction that is rolled back.
    """
    engine = create_async_engine(TEST_DB_URL, poolclass=NullPool)

    # Verify connection works
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))

    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(engine):
    """Provide a transactional database session for tests.

    Each test gets a session wrapped in a transaction that is rolled back
    at the end, ensuring test isolation without affecting production data.
    """
    connection = await engine.connect()
    transaction = await connection.begin()

    session_factory = async_sessionmaker(
        bind=connection,
        expire_on_commit=False,
        class_=AsyncSession
    )

    async with session_factory() as session:
        yield session

    await transaction.rollback()
    await connection.close()


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


@pytest.fixture
def unique_job_board_id():
    """Generate a unique job_board_id for test jobs.

    Since the database has a unique constraint on (job_board, job_board_id),
    tests need unique values to avoid conflicts with production data.
    """
    import uuid
    counter = [0]

    def _generate():
        counter[0] += 1
        return f"test-{uuid.uuid4().hex[:8]}-{counter[0]}"

    return _generate


@pytest.fixture
def test_job_payload(unique_job_board_id):
    """Create a test job payload with unique identifiers.

    Returns a function that generates job payloads with unique job_board_id
    to avoid conflicts with production data.
    """
    def _create(title="Test Engineer", company="Test Company", **kwargs):
        return {
            "title": title,
            "company": company,
            "job_board": "test",
            "job_board_id": unique_job_board_id(),
            **kwargs
        }

    return _create
