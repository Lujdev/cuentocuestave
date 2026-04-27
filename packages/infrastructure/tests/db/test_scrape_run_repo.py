"""Tests for SqlScrapeRunRepository.

Unit tests use a mock session.
Integration tests (pg_session) verify real Postgres round-trips.
"""
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from cuantocuestave_infra.db.repositories.scrape_run import SqlScrapeRunRepository


# ---------------------------------------------------------------------------
# Unit tests — mock session
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_start_adds_new_run(mock_session: AsyncMock) -> None:
    """start() should session.add a ScrapeRun with status='running'."""
    repo = SqlScrapeRunRepository(mock_session)
    supermarket_id = uuid4()

    run = await repo.start(supermarket_id, worker_version="0.1.0")

    mock_session.add.assert_called_once()
    mock_session.flush.assert_awaited_once()
    assert run.status == "running"
    assert run.supermarket_id == supermarket_id
    assert run.worker_version == "0.1.0"
    assert run.started_at is not None


@pytest.mark.asyncio
async def test_finish_updates_run_fields(mock_session: AsyncMock) -> None:
    """finish() should set all result fields on the existing ORM row."""
    existing_run = MagicMock()
    existing_run.id = uuid4()
    existing_run.status = "running"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_run
    mock_session.execute = AsyncMock(return_value=mock_result)

    repo = SqlScrapeRunRepository(mock_session)
    await repo.finish(
        run_id=existing_run.id,
        status="success",
        items_seen=50,
        items_new=5,
        items_updated=45,
        errors_count=0,
        error_summary=None,
    )

    assert existing_run.status == "success"
    assert existing_run.items_seen == 50
    assert existing_run.items_new == 5
    assert existing_run.items_updated == 45
    assert existing_run.errors_count == 0
    assert existing_run.error_summary is None
    assert existing_run.finished_at is not None
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_finish_with_missing_run_is_noop(mock_session: AsyncMock) -> None:
    """finish() should silently return when the run_id doesn't exist."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    repo = SqlScrapeRunRepository(mock_session)
    # Should not raise
    await repo.finish(
        run_id=uuid4(),
        status="success",
        items_seen=0,
        items_new=0,
        items_updated=0,
        errors_count=0,
        error_summary=None,
    )
    mock_session.flush.assert_not_awaited()


@pytest.mark.asyncio
async def test_finish_skipped_stores_error_summary(mock_session: AsyncMock) -> None:
    existing_run = MagicMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_run
    mock_session.execute = AsyncMock(return_value=mock_result)

    repo = SqlScrapeRunRepository(mock_session)
    summary = {"reason": "exchange_rate_missing", "source": "monitor_dolar_ve"}
    await repo.finish(
        run_id=uuid4(),
        status="skipped",
        items_seen=0,
        items_new=0,
        items_updated=0,
        errors_count=0,
        error_summary=summary,
    )

    assert existing_run.status == "skipped"
    assert existing_run.error_summary == summary


# ---------------------------------------------------------------------------
# Integration tests — real Postgres
# ---------------------------------------------------------------------------

@pytest.mark.integration
@pytest.mark.asyncio
async def test_start_and_finish_roundtrip(pg_session: AsyncMock) -> None:
    from cuantocuestave_infra.db.repositories.supermarket import SqlSupermarketRepository

    sm_repo = SqlSupermarketRepository(pg_session)
    slug = f"test-sm-{uuid4().hex[:8]}"
    supermarket = await sm_repo.upsert(slug, "Test SM", "https://test.com", "USD")

    run_repo = SqlScrapeRunRepository(pg_session)
    run = await run_repo.start(supermarket.id, worker_version="0.1.0")
    assert run.id is not None
    assert run.status == "running"

    await run_repo.finish(
        run_id=run.id,
        status="success",
        items_seen=10,
        items_new=2,
        items_updated=8,
        errors_count=0,
        error_summary=None,
    )
    assert run.status == "success"
    assert run.finished_at is not None
