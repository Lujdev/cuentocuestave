"""Tests for SqlSupermarketRepository.

Unit tests use a mock session to verify query construction logic.
Integration tests (pg_session) verify real Postgres round-trips.
"""
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from cuantocuestave_infra.db.repositories.supermarket import SqlSupermarketRepository


# ---------------------------------------------------------------------------
# Unit tests — mock session
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_by_slug_executes_select(mock_session: AsyncMock) -> None:
    """get_by_slug calls execute and returns scalar_one_or_none result."""
    expected = MagicMock()
    expected.slug = "plazas"
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected
    mock_session.execute = AsyncMock(return_value=mock_result)

    repo = SqlSupermarketRepository(mock_session)
    result = await repo.get_by_slug("plazas")

    assert result is expected
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_slug_returns_none_when_missing(mock_session: AsyncMock) -> None:
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    repo = SqlSupermarketRepository(mock_session)
    result = await repo.get_by_slug("nonexistent")

    assert result is None


@pytest.mark.asyncio
async def test_upsert_adds_new_row_when_not_found(mock_session: AsyncMock) -> None:
    """upsert calls session.add when the slug doesn't exist yet."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    repo = SqlSupermarketRepository(mock_session)
    row = await repo.upsert("plazas", "Plaza's", "https://plazas.com.ve", "USD")

    mock_session.add.assert_called_once()
    mock_session.flush.assert_awaited_once()
    assert row.slug == "plazas"


@pytest.mark.asyncio
async def test_upsert_updates_existing_row(mock_session: AsyncMock) -> None:
    """upsert mutates the existing row and flushes without calling session.add."""
    existing = MagicMock()
    existing.display_name = "Old Name"
    existing.base_url = "https://old.com"
    existing.currency = "USD"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing
    mock_session.execute = AsyncMock(return_value=mock_result)

    repo = SqlSupermarketRepository(mock_session)
    row = await repo.upsert("plazas", "Plaza's New", "https://new.com", "VES")

    mock_session.add.assert_not_called()
    mock_session.flush.assert_awaited_once()
    assert row.display_name == "Plaza's New"
    assert row.base_url == "https://new.com"
    assert row.currency == "VES"


# ---------------------------------------------------------------------------
# Integration tests — real Postgres
# ---------------------------------------------------------------------------

@pytest.mark.integration
@pytest.mark.asyncio
async def test_upsert_and_get_by_slug_roundtrip(pg_session: AsyncMock) -> None:
    repo = SqlSupermarketRepository(pg_session)
    slug = f"test-plazas-{uuid4().hex[:8]}"

    row = await repo.upsert(slug, "Plaza's Test", "https://plazas.com.ve", "USD")
    assert row.id is not None

    fetched = await repo.get_by_slug(slug)
    assert fetched is not None
    assert fetched.display_name == "Plaza's Test"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_upsert_idempotent(pg_session: AsyncMock) -> None:
    repo = SqlSupermarketRepository(pg_session)
    slug = f"test-plazas-{uuid4().hex[:8]}"

    r1 = await repo.upsert(slug, "Name V1", "https://plazas.com.ve", "USD")
    r2 = await repo.upsert(slug, "Name V2", "https://plazas.com.ve", "USD")

    assert r1.id == r2.id
    assert r2.display_name == "Name V2"
