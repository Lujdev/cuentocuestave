"""Dramatiq actor: scrape_supermarket — orchestrates one full scrape cycle."""

import asyncio
from datetime import UTC, datetime

import dramatiq
import structlog

from cuantocuestave_infra.db.repositories import (
    SqlExchangeRateRepository,
    SqlPriceRepository,
    SqlProductListingRepository,
    SqlScrapeRunRepository,
    SqlSupermarketRepository,
)
from cuantocuestave_infra.db.session import async_session_factory
from cuantocuestave_infra.scrapers import SCRAPERS
from cuantocuestave_workers.broker import broker  # noqa: F401 — registers broker

logger = structlog.get_logger(__name__)

_WORKER_VERSION = "0.1.0"


async def _scrape_async(supermarket_slug: str) -> None:
    """Full async scrape pipeline for a single supermarket."""

    log = logger.bind(supermarket=supermarket_slug)

    scraper_cls = SCRAPERS.get(supermarket_slug)
    if scraper_cls is None:
        log.error("scraper_not_found", known=list(SCRAPERS.keys()))
        return

    async with async_session_factory() as session:
        supermarket_repo = SqlSupermarketRepository(session)
        scrape_run_repo = SqlScrapeRunRepository(session)
        listing_repo = SqlProductListingRepository(session)
        price_repo = SqlPriceRepository(session)
        exchange_repo = SqlExchangeRateRepository(session)

        # Ensure the supermarket row exists in the DB
        supermarket = await supermarket_repo.get_by_slug(supermarket_slug)
        if supermarket is None:
            log.error("supermarket_not_in_db", hint="run seed or upsert first")
            return

        # Guard: exchange rate MUST exist before scraping prices
        monitor_rate = await exchange_repo.get_latest("monitor_dolar_ve")
        if monitor_rate is None:
            run = await scrape_run_repo.start(supermarket.id, _WORKER_VERSION)
            await scrape_run_repo.finish(
                run_id=run.id,
                status="skipped",
                items_seen=0,
                items_new=0,
                items_updated=0,
                errors_count=0,
                error_summary={"reason": "exchange_rate_missing", "source": "monitor_dolar_ve"},
            )
            await session.commit()
            log.warning("exchange_rate_missing", source="monitor_dolar_ve")
            return

        bcv_rate = await exchange_repo.get_latest("bcv")

        # Open scrape run
        run = await scrape_run_repo.start(supermarket.id, _WORKER_VERSION)
        await session.commit()  # persist run id before scraping (crash safety)

        scraper = scraper_cls()
        scrape_result = await scraper.scrape()

        observed_at = datetime.now(UTC)
        items_seen = len(scrape_result.listings)
        items_new = 0
        items_updated = 0
        errors_count = len(scrape_result.errors)
        error_summary: dict | None = (
            {"errors": scrape_result.errors[:20]} if scrape_result.errors else None
        )

        for raw in scrape_result.listings:
            try:
                listing, is_new = await listing_repo.upsert_by_external_id(raw, supermarket.id)

                if is_new:
                    items_new += 1
                else:
                    items_updated += 1

                # Convert to USD
                if raw.currency == "USD":
                    price_usd = raw.price_local
                else:
                    # Assume VES — divide by paralelo rate
                    price_usd = raw.price_local / monitor_rate.rate_ves_per_usd

                # unit_price_usd: placeholder — Fase 2 will normalise by pack size
                unit_price_usd = price_usd

                price_ves_bcv = (
                    price_usd * bcv_rate.rate_ves_per_usd if bcv_rate is not None else None
                )
                price_ves_paralelo = price_usd * monitor_rate.rate_ves_per_usd

                await price_repo.append(
                    {
                        "product_listing_id": listing.id,
                        "price_local": raw.price_local,
                        "currency": raw.currency,
                        "price_usd": price_usd,
                        "price_ves_bcv": price_ves_bcv,
                        "price_ves_paralelo": price_ves_paralelo,
                        "unit_price_usd": unit_price_usd,
                        "available": raw.available,
                        "observed_at": observed_at,
                        "scrape_run_id": run.id,
                    }
                )
            except Exception as exc:
                errors_count += 1
                log.error("listing_persist_error", external_id=raw.external_id, error=str(exc))
                if error_summary is None:
                    error_summary = {"errors": []}
                error_summary["errors"].append(f"{raw.external_id}: {exc}")

        status = "success" if errors_count == 0 else ("partial" if items_seen > 0 else "failed")

        await scrape_run_repo.finish(
            run_id=run.id,
            status=status,
            items_seen=items_seen,
            items_new=items_new,
            items_updated=items_updated,
            errors_count=errors_count,
            error_summary=error_summary,
        )
        await session.commit()

    log.info(
        "scrape_finished",
        status=status,
        items_seen=items_seen,
        items_new=items_new,
        items_updated=items_updated,
        errors_count=errors_count,
    )


@dramatiq.actor(queue_name="scraping", max_retries=3)
def scrape_supermarket(supermarket_slug: str) -> None:
    """Dramatiq entry point — bridges sync Dramatiq with the async pipeline."""
    logger.info("scrape_started", supermarket=supermarket_slug)
    asyncio.run(_scrape_async(supermarket_slug))
    logger.info("scrape_actor_done", supermarket=supermarket_slug)
