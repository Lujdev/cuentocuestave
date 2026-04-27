"""SQL adapter for exchange rate persistence."""

from datetime import UTC, timedelta
from typing import Any

import structlog
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from cuantocuestave_infra.db.models import ExchangeRate
from cuantocuestave_infra.exchange.types import ExchangeRateReading

logger = structlog.get_logger(__name__)


class SqlExchangeRateRepository:
    """Append-only exchange rate storage with idempotent per-minute deduplication."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def append(self, reading: ExchangeRateReading) -> None:
        """Insert *reading* unless a row for the same source+minute already exists.

        Deduplication window: same UTC minute (truncated to minute boundary).
        This avoids duplicate rows when the actor fires rapidly or retries.
        """
        minute_start = reading.observed_at.replace(second=0, microsecond=0, tzinfo=UTC)
        minute_end = minute_start + timedelta(minutes=1)

        existing = await self._session.execute(
            select(ExchangeRate).where(
                and_(
                    ExchangeRate.source == reading.source,
                    ExchangeRate.observed_at >= minute_start,
                    ExchangeRate.observed_at < minute_end,
                )
            )
        )
        if existing.scalar_one_or_none() is not None:
            logger.info("exchange_rate_already_present", source=reading.source)
            return

        row = ExchangeRate(
            source=reading.source,
            rate_ves_per_usd=reading.rate_ves_per_usd,
            observed_at=reading.observed_at,
            raw_payload=reading.raw_payload or None,
        )
        self._session.add(row)
        await self._session.flush()

    async def get_latest(self, source: str) -> Any | None:
        """Return the most recent ExchangeRate ORM row for *source*, or None."""
        result = await self._session.execute(
            select(ExchangeRate)
            .where(ExchangeRate.source == source)
            .order_by(ExchangeRate.observed_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
