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
    """Async pipeline: fetch both exchange rates concurrently and append to the DB."""

    results = await asyncio.gather(
        fetch_bcv_rate(),
        fetch_monitor_dolar_rate(),
        return_exceptions=True,
    )

    async with async_session_factory() as session:
        repo = SqlExchangeRateRepository(session)

        sources = ("bcv", "monitor_dolar_ve")
        for source, result in zip(sources, results, strict=True):
            if isinstance(result, ExchangeRateFetchError):
                logger.warning("exchange_rate_fetch_failed", source=source, error=str(result))
            elif isinstance(result, BaseException):
                logger.error("exchange_rate_unexpected_error", source=source, error=str(result))
            else:
                await repo.append(result)
                logger.info(
                    "exchange_rate_persisted",
                    source=source,
                    rate=str(result.rate_ves_per_usd),
                )

        await session.commit()


@dramatiq.actor(queue_name="default", max_retries=5)
def fetch_exchange_rates() -> None:
    """Dramatiq entry point — bridges sync Dramatiq with the async pipeline."""
    logger.info("exchange_rates_fetch_started")
    asyncio.run(_fetch_and_persist())
    logger.info("exchange_rates_fetch_finished")
