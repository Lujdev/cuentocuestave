"""SQL adapter for append-only price persistence."""

from sqlalchemy.ext.asyncio import AsyncSession

from cuantocuestave_infra.db.models import Price


class SqlPriceRepository:
    """Append-only price storage — never updates an existing price row."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def append(self, price_data: dict) -> None:
        """Insert a new price row.

        *price_data* keys must match the :class:`Price` model columns:
        product_listing_id, price_local, currency, price_usd, price_ves_bcv,
        price_ves_paralelo, unit_price_usd, available, observed_at, scrape_run_id.
        """
        row = Price(**price_data)
        self._session.add(row)
        await self._session.flush()
