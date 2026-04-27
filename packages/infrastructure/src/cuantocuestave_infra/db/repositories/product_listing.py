"""SQL adapter for the ProductListingRepository port (scraping side)."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cuantocuestave_domain.ports.scraper import RawListing
from cuantocuestave_infra.db.models import ProductListing


class SqlProductListingRepository:
    """SQLAlchemy 2.0 adapter for persisting scraped product listings.

    Uses (supermarket_id, external_id) as the natural upsert key.
    Returns (orm_row, is_new) so callers can track new vs updated counts.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert_by_external_id(
        self,
        raw: RawListing,
        supermarket_id: UUID,
    ) -> tuple[Any, bool]:
        """Upsert a product listing from a scraped :class:`RawListing`.

        Returns:
            (orm_row, is_new) — is_new=True when the row was just inserted.
        """
        result = await self._session.execute(
            select(ProductListing).where(
                ProductListing.supermarket_id == supermarket_id,
                ProductListing.external_id == raw.external_id,
            )
        )
        row = result.scalar_one_or_none()
        is_new = row is None

        if is_new:
            row = ProductListing(
                supermarket_id=supermarket_id,
                external_id=raw.external_id,
                raw_name=raw.raw_name,
                raw_brand=raw.raw_brand,
                raw_unit=raw.raw_unit,
                raw_category=raw.raw_category,
                image_url=raw.image_url,
                product_url=raw.product_url,
                match_status="pending",
            )
            self._session.add(row)
        else:
            row.raw_name = raw.raw_name
            row.raw_brand = raw.raw_brand
            row.raw_unit = raw.raw_unit
            row.raw_category = raw.raw_category
            row.image_url = raw.image_url
            row.product_url = raw.product_url
            row.last_seen_at = datetime.now(UTC)

        await self._session.flush()
        return row, is_new
