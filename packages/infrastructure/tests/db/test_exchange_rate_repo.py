"""Tests for SqlExchangeRateRepository.

Unit tests use a mock session to verify deduplication logic and query structure.
Integration tests (pg_session) verify real Postgres round-trips.
"""
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from cuantocuestave_infra.db.repositories.exchange_rate import SqlExchangeRateRepository
from cuantocuestave_infra.exchange.types import ExchangeRateReading


def _reading(
    source: str = "bcv",
    rate: str = "36.50",
    minute: int = 0,
) -> ExchangeRateReading:
    ts = datetime(2026, 4, 26, 12, minute, 0, tzinfo=UTC)
    return ExchangeRateReading(
        source=source,
        rate_ves_per_usd=Decimal(rate),
        observed_at=ts,
        raw_payload={"rate_raw": rate},
    )


# ---------------------------------------------------------------------------
# Unit tests — mock session
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_latest_returns_none_when_empty(mock_session: AsyncMock) -> None:
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    repo = SqlExchangeRateRepository(mock_session)
    result = await repo.get_latest("bcv")

    assert result is None
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_latest_returns_orm_row(mock_session: AsyncMock) -> None:
    expected = MagicMock()
    expected.source = "bcv"
    expected.rate_ves_per_usd = Decimal("36.50")

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected
    mock_session.execute = AsyncMock(return_value=mock_result)

    repo = SqlExchangeRateRepository(mock_session)
    result = await repo.get_latest("bcv")

    assert result is expected


@pytest.mark.asyncio
async def test_append_skips_when_duplicate_within_minute(mock_session: AsyncMock) -> None:
    """append() should NOT add a new row when a row for the same source+minute exists."""
    existing = MagicMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing  # duplicate found
    mock_session.execute = AsyncMock(return_value=mock_result)

    repo = SqlExchangeRateRepository(mock_session)
    await repo.append(_reading("bcv", "36.50", minute=0))

    mock_session.add.assert_not_called()
    mock_session.flush.assert_not_awaited()


@pytest.mark.asyncio
async def test_append_inserts_when_no_duplicate(mock_session: AsyncMock) -> None:
    """append() should session.add when no row for this source+minute exists."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None  # no duplicate
    mock_session.execute = AsyncMock(return_value=mock_result)

    repo = SqlExchangeRateRepository(mock_session)
    await repo.append(_reading("bcv", "36.50", minute=0))

    mock_session.add.assert_called_once()
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_append_empty_payload_stored_as_none(mock_session: AsyncMock) -> None:
    """An ExchangeRateReading with empty raw_payload should store None in DB."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    reading = ExchangeRateReading(
        source="monitor_dolar_ve",
        rate_ves_per_usd=Decimal("95.12"),
        observed_at=datetime(2026, 4, 26, 12, 0, tzinfo=UTC),
        # raw_payload defaults to {}
    )

    repo = SqlExchangeRateRepository(mock_session)
    await repo.append(reading)

    added_row = mock_session.add.call_args[0][0]
    # Empty dict should be stored as None (falsy check in implementation)
    assert added_row.raw_payload is None


# ---------------------------------------------------------------------------
# Integration tests — real Postgres
# ---------------------------------------------------------------------------

@pytest.mark.integration
@pytest.mark.asyncio
async def test_append_and_get_latest_roundtrip(pg_session: AsyncMock) -> None:
    repo = SqlExchangeRateRepository(pg_session)
    # Use a unique minute offset to avoid conflicts with other test runs
    unique_minute = datetime.now(UTC).minute
    reading = _reading("bcv", "36.50", minute=unique_minute)

    await repo.append(reading)
    latest = await repo.get_latest("bcv")

    assert latest is not None
    assert latest.rate_ves_per_usd == Decimal("36.50")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_append_deduplication_integration(pg_session: AsyncMock) -> None:
    from sqlalchemy import func, select

    from cuantocuestave_infra.db.models import ExchangeRate

    repo = SqlExchangeRateRepository(pg_session)
    unique_minute = datetime.now(UTC).minute
    r1 = _reading("monitor_dolar_ve", "95.00", minute=unique_minute)
    r2 = _reading("monitor_dolar_ve", "99.99", minute=unique_minute)  # same minute

    await repo.append(r1)
    await repo.append(r2)  # should be skipped

    # Count rows for this source at this exact minute
    minute_start = r1.observed_at.replace(second=0, microsecond=0)
    minute_end = minute_start + timedelta(minutes=1)
    result = await pg_session.execute(
        select(func.count()).where(
            ExchangeRate.source == "monitor_dolar_ve",
            ExchangeRate.observed_at >= minute_start,
            ExchangeRate.observed_at < minute_end,
        )
    )
    count = result.scalar()
    assert count == 1
