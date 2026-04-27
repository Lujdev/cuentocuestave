"""SQL adapter for the SupermarketRepository port."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cuantocuestave_infra.db.models import Supermarket


class SqlSupermarketRepository:
    """SQLAlchemy 2.0 implementation of the SupermarketRepository port."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_slug(self, slug: str) -> Any | None:
        """Return the Supermarket ORM row for *slug*, or None if not found."""
        result = await self._session.execute(select(Supermarket).where(Supermarket.slug == slug))
        return result.scalar_one_or_none()

    async def upsert(
        self,
        slug: str,
        display_name: str,
        base_url: str,
        currency: str,
    ) -> Any:
        """Insert a new supermarket or update display_name, base_url, and currency.

        Returns the (possibly freshly created) ORM row.
        """
        row = await self.get_by_slug(slug)
        if row is None:
            row = Supermarket(
                slug=slug,
                display_name=display_name,
                base_url=base_url,
                currency=currency,
            )
            self._session.add(row)
        else:
            row.display_name = display_name
            row.base_url = base_url
            row.currency = currency

        await self._session.flush()
        return row
