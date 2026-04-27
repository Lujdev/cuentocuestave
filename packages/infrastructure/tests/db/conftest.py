"""Pytest fixtures for infrastructure database tests.

Unit tests use a mock AsyncSession (no real DB needed).
Integration tests (marked @pytest.mark.integration) use a real Postgres session
obtained from the cuantocuestave_infra settings.
"""
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio


@pytest.fixture
def mock_session() -> AsyncMock:
    """Return a pre-configured mock AsyncSession for unit tests."""
    session = AsyncMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.add = MagicMock()
    return session


@pytest_asyncio.fixture
async def pg_session():  # type: ignore[no-untyped-def]
    """Real async Postgres session for integration tests.

    Requires DATABASE_URL to be set and the schema to be up to date.
    Each test runs in a transaction that is rolled back on teardown.
    """
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    from cuantocuestave_infra.settings import Settings

    settings = Settings()
    engine = create_async_engine(settings.database_url, echo=False)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as session:
        async with session.begin():
            yield session
            await session.rollback()

    await engine.dispose()
