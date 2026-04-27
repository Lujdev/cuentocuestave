"""Unit tests for ExchangeRateReading and ExchangeRateFetchError."""
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from cuantocuestave_infra.exchange.types import ExchangeRateFetchError, ExchangeRateReading


def test_exchange_rate_reading_is_frozen() -> None:
    reading = ExchangeRateReading(
        source="bcv",
        rate_ves_per_usd=Decimal("36.50"),
        observed_at=datetime(2026, 4, 26, 12, 0, tzinfo=UTC),
    )
    with pytest.raises((AttributeError, TypeError)):
        reading.source = "other"  # type: ignore[misc]


def test_exchange_rate_reading_default_payload() -> None:
    reading = ExchangeRateReading(
        source="monitor_dolar_ve",
        rate_ves_per_usd=Decimal("95.12"),
        observed_at=datetime(2026, 4, 26, 12, 0, tzinfo=UTC),
    )
    assert reading.raw_payload == {}


def test_exchange_rate_reading_with_payload() -> None:
    payload = {"promedio": 95.12, "nombre": "Paralelo"}
    reading = ExchangeRateReading(
        source="monitor_dolar_ve",
        rate_ves_per_usd=Decimal("95.12"),
        observed_at=datetime(2026, 4, 26, 12, 0, tzinfo=UTC),
        raw_payload=payload,
    )
    assert reading.raw_payload["nombre"] == "Paralelo"


def test_exchange_rate_fetch_error_is_exception() -> None:
    exc = ExchangeRateFetchError("connection refused")
    assert isinstance(exc, Exception)
    assert "connection refused" in str(exc)
