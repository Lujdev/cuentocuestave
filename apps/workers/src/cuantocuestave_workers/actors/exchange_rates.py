"""Dramatiq actor: fetch_exchange_rates — fetches BCV + paralelo rates and persists them."""

import asyncio

import dramatiq
import structlog

from cuantocuestave_infra.db.repositories import SqlExchangeRateRepository
from cuantocuestave_infra.db.session import async_session_factory
from cuantocuestave_infra.exchange import (
    ExchangeRateFetchError,
    fetch_bcv_rate,
    fetch_monitor_dolar_rate,
)
from cuantocuestave_workers.broker import broker  # noqa: F401

logger = structlog.get_logger(__name__)


async def _fetch_and_persist() -> None:
    """Async pipeline: fetch both exchange rates and append to the DB."""

    async with async_session_factory() as session:
        repo = SqlExchangeRateRepository(session)

        # BCV — official rate
        try:
            bcv_reading = await fetch_bcv_rate()
            await repo.append(bcv_reading)
            logger.info(
                "exchange_rate_persisted",
                source="bcv",
                rate=str(bcv_reading.rate_ves_per_usd),
            )
        except ExchangeRateFetchError as exc:
            logger.error("exchange_rate_fetch_failed", source="bcv", error=str(exc))

        # Monitor Dólar Venezuela — parallel market rate
        try:
            monitor_reading = await fetch_monitor_dolar_rate()
            await repo.append(monitor_reading)
            logger.info(
                "exchange_rate_persisted",
                source="monitor_dolar_ve",
                rate=str(monitor_reading.rate_ves_per_usd),
            )
        except ExchangeRateFetchError as exc:
            logger.error("exchange_rate_fetch_failed", source="monitor_dolar_ve", error=str(exc))

        await session.commit()


@dramatiq.actor(queue_name="default", max_retries=5)
def fetch_exchange_rates() -> None:
    """Dramatiq entry point — bridges sync Dramatiq with the async pipeline."""
    logger.info("exchange_rates_fetch_started")
    asyncio.run(_fetch_and_persist())
    logger.info("exchange_rates_fetch_finished")
