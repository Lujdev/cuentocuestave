"""Unit tests for the fetch_exchange_rates actor logic."""
from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cuantocuestave_infra.exchange.types import ExchangeRateFetchError, ExchangeRateReading


def _reading(source: str, rate: str = "36.50") -> ExchangeRateReading:
    return ExchangeRateReading(
        source=source,
        rate_ves_per_usd=Decimal(rate),
        observed_at=datetime(2026, 4, 26, 12, 0, tzinfo=UTC),
    )


def _make_session_cm(session: AsyncMock) -> MagicMock:
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=session)
    cm.__aexit__ = AsyncMock(return_value=False)
    return cm


@pytest.mark.asyncio
async def test_fetch_and_persist_both_sources() -> None:
    from cuantocuestave_workers.actors.exchange_rates import _fetch_and_persist

    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()

    mock_repo = AsyncMock()
    mock_repo.append = AsyncMock()

    with (
        patch(
            "cuantocuestave_workers.actors.exchange_rates.async_session_factory",
            return_value=_make_session_cm(mock_session),
        ),
        patch(
            "cuantocuestave_workers.actors.exchange_rates.SqlExchangeRateRepository",
            return_value=mock_repo,
        ),
        patch(
            "cuantocuestave_workers.actors.exchange_rates.fetch_bcv_rate",
            AsyncMock(return_value=_reading("bcv", "36.50")),
        ),
        patch(
            "cuantocuestave_workers.actors.exchange_rates.fetch_monitor_dolar_rate",
            AsyncMock(return_value=_reading("monitor_dolar_ve", "95.12")),
        ),
    ):
        await _fetch_and_persist()

    assert mock_repo.append.await_count == 2
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_fetch_and_persist_continues_when_bcv_fails() -> None:
    """A BCV fetch failure should not prevent persisting the monitor rate."""
    from cuantocuestave_workers.actors.exchange_rates import _fetch_and_persist

    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()

    mock_repo = AsyncMock()
    mock_repo.append = AsyncMock()

    with (
        patch(
            "cuantocuestave_workers.actors.exchange_rates.async_session_factory",
            return_value=_make_session_cm(mock_session),
        ),
        patch(
            "cuantocuestave_workers.actors.exchange_rates.SqlExchangeRateRepository",
            return_value=mock_repo,
        ),
        patch(
            "cuantocuestave_workers.actors.exchange_rates.fetch_bcv_rate",
            AsyncMock(side_effect=ExchangeRateFetchError("timeout")),
        ),
        patch(
            "cuantocuestave_workers.actors.exchange_rates.fetch_monitor_dolar_rate",
            AsyncMock(return_value=_reading("monitor_dolar_ve", "95.12")),
        ),
    ):
        await _fetch_and_persist()

    # Only the monitor rate was successfully appended
    assert mock_repo.append.await_count == 1
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_fetch_and_persist_continues_when_monitor_fails() -> None:
    """A monitor fetch failure should not prevent persisting the BCV rate."""
    from cuantocuestave_workers.actors.exchange_rates import _fetch_and_persist

    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()

    mock_repo = AsyncMock()
    mock_repo.append = AsyncMock()

    with (
        patch(
            "cuantocuestave_workers.actors.exchange_rates.async_session_factory",
            return_value=_make_session_cm(mock_session),
        ),
        patch(
            "cuantocuestave_workers.actors.exchange_rates.SqlExchangeRateRepository",
            return_value=mock_repo,
        ),
        patch(
            "cuantocuestave_workers.actors.exchange_rates.fetch_bcv_rate",
            AsyncMock(return_value=_reading("bcv", "36.50")),
        ),
        patch(
            "cuantocuestave_workers.actors.exchange_rates.fetch_monitor_dolar_rate",
            AsyncMock(side_effect=ExchangeRateFetchError("timeout")),
        ),
    ):
        await _fetch_and_persist()

    # Only the BCV rate was successfully appended
    assert mock_repo.append.await_count == 1
    mock_session.commit.assert_awaited_once()
