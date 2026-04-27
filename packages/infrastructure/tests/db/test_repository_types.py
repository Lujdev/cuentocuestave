"""Unit tests for PriceCreate and ScrapeRunResult pydantic models."""
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from cuantocuestave_infra.db.repositories.types import PriceCreate, ScrapeRunResult


def _price_create_payload() -> dict:
    return {
        "product_listing_id": uuid4(),
        "price_local": Decimal("4.99"),
        "currency": "USD",
        "price_usd": Decimal("4.99"),
        "price_ves_bcv": Decimal("182.13"),
        "price_ves_paralelo": Decimal("474.95"),
        "unit_price_usd": Decimal("4.99"),
        "available": True,
        "observed_at": datetime(2026, 4, 26, 12, 0, tzinfo=UTC),
        "scrape_run_id": uuid4(),
    }


def test_price_create_valid() -> None:
    p = PriceCreate(**_price_create_payload())
    assert p.currency == "USD"
    assert p.available is True


def test_price_create_nullable_ves_fields() -> None:
    payload = _price_create_payload()
    payload["price_ves_bcv"] = None
    payload["price_ves_paralelo"] = None
    p = PriceCreate(**payload)
    assert p.price_ves_bcv is None
    assert p.price_ves_paralelo is None


def test_price_create_is_frozen() -> None:
    p = PriceCreate(**_price_create_payload())
    with pytest.raises((AttributeError, ValidationError, TypeError)):
        p.currency = "VES"  # type: ignore[misc]


def test_scrape_run_result_defaults() -> None:
    r = ScrapeRunResult(run_id=uuid4(), status="success")
    assert r.items_seen == 0
    assert r.errors_count == 0
    assert r.error_summary is None


def test_scrape_run_result_is_frozen() -> None:
    r = ScrapeRunResult(run_id=uuid4(), status="success")
    with pytest.raises((AttributeError, ValidationError, TypeError)):
        r.status = "failed"  # type: ignore[misc]
