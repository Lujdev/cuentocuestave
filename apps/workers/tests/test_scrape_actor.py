"""Unit tests for the scrape_supermarket actor logic."""
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cuantocuestave_domain.ports.scraper import RawListing


def _make_raw_listing(external_id: str = "sku-001", currency: str = "USD") -> RawListing:
    return RawListing(
        external_id=external_id,
        raw_name="Harina PAN 1kg",
        raw_brand="P.A.N.",
        raw_unit="kg",
        raw_category="cereales",
        price_local=Decimal("3.50"),
        currency=currency,
        available=True,
        image_url=None,
        product_url=None,
    )


def _make_session_cm(session: AsyncMock) -> MagicMock:
    """Return a mock that acts as an async context manager yielding *session*."""
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=session)
    cm.__aexit__ = AsyncMock(return_value=False)
    return cm


@pytest.mark.asyncio
async def test_scrape_async_skips_when_exchange_rate_missing() -> None:
    """Actor should finish with status='skipped' when monitor rate is absent."""
    from cuantocuestave_workers.actors.scrape import _scrape_async

    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()

    mock_supermarket = MagicMock()
    mock_supermarket.id = "00000000-0000-0000-0000-000000000001"

    mock_supermarket_repo = AsyncMock()
    mock_supermarket_repo.get_by_slug = AsyncMock(return_value=mock_supermarket)

    mock_run = MagicMock()
    mock_run.id = "00000000-0000-0000-0000-000000000002"

    mock_scrape_run_repo = AsyncMock()
    mock_scrape_run_repo.start = AsyncMock(return_value=mock_run)
    mock_scrape_run_repo.finish = AsyncMock()

    mock_exchange_repo = AsyncMock()
    mock_exchange_repo.get_latest = AsyncMock(return_value=None)  # no rate

    with (
        patch(
            "cuantocuestave_workers.actors.scrape.async_session_factory",
            return_value=_make_session_cm(mock_session),
        ),
        patch(
            "cuantocuestave_workers.actors.scrape.SqlSupermarketRepository",
            return_value=mock_supermarket_repo,
        ),
        patch(
            "cuantocuestave_workers.actors.scrape.SqlScrapeRunRepository",
            return_value=mock_scrape_run_repo,
        ),
        patch(
            "cuantocuestave_workers.actors.scrape.SqlProductListingRepository",
            return_value=AsyncMock(),
        ),
        patch(
            "cuantocuestave_workers.actors.scrape.SqlPriceRepository",
            return_value=AsyncMock(),
        ),
        patch(
            "cuantocuestave_workers.actors.scrape.SqlExchangeRateRepository",
            return_value=mock_exchange_repo,
        ),
        patch(
            "cuantocuestave_workers.actors.scrape.SCRAPERS",
            {"plazas": MagicMock()},
        ),
    ):
        await _scrape_async("plazas")

    mock_scrape_run_repo.finish.assert_awaited_once()
    call_kwargs = mock_scrape_run_repo.finish.call_args.kwargs
    assert call_kwargs["status"] == "skipped"


@pytest.mark.asyncio
async def test_scrape_async_unknown_slug_returns_early() -> None:
    """Actor should return immediately if the slug has no registered scraper."""
    from cuantocuestave_workers.actors.scrape import _scrape_async

    mock_session = AsyncMock()

    with (
        patch(
            "cuantocuestave_workers.actors.scrape.async_session_factory",
            return_value=_make_session_cm(mock_session),
        ),
        patch("cuantocuestave_workers.actors.scrape.SCRAPERS", {}),
    ):
        # Should not raise and should not open a DB session
        await _scrape_async("unknown-slug")

    # session.__aenter__ never called because we return before entering context
    mock_session.commit.assert_not_awaited()
