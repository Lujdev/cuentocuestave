"""SQL adapter for the ScrapeRunRepository port."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cuantocuestave_infra.db.models import ScrapeRun

# Version injected at import time — can be overridden for tests.
_WORKER_VERSION = "0.1.0"


class SqlScrapeRunRepository:
    """SQLAlchemy 2.0 implementation of the ScrapeRunRepository port."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def start(self, supermarket_id: UUID, worker_version: str = _WORKER_VERSION) -> Any:
        """Open a new scrape run and return the ORM row with its generated id."""
        row = ScrapeRun(
            supermarket_id=supermarket_id,
            started_at=datetime.now(UTC),
            status="running",
            worker_version=worker_version,
        )
        self._session.add(row)
        await self._session.flush()
        return row

    async def finish(
        self,
        run_id: UUID,
        status: str,
        items_seen: int,
        items_new: int,
        items_updated: int,
        errors_count: int,
        error_summary: dict | None,
    ) -> None:
        """Close the scrape run identified by *run_id*, recording final stats."""
        result = await self._session.execute(select(ScrapeRun).where(ScrapeRun.id == run_id))
        row = result.scalar_one_or_none()
        if row is None:
            return  # silently ignore missing runs (idempotent)

        row.finished_at = datetime.now(UTC)
        row.status = status
        row.items_seen = items_seen
        row.items_new = items_new
        row.items_updated = items_updated
        row.errors_count = errors_count
        row.error_summary = error_summary
        await self._session.flush()
