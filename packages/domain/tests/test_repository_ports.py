"""Unit tests for the new SupermarketRepository and ScrapeRunRepository ABCs."""
from abc import ABC
from uuid import UUID

import pytest

from cuantocuestave_domain.ports.repositories import (
    ScrapeRunRepository,
    SupermarketRepository,
)


def test_supermarket_repository_is_abstract() -> None:
    assert issubclass(SupermarketRepository, ABC)
    with pytest.raises(TypeError):
        SupermarketRepository()  # type: ignore[abstract]


def test_scrape_run_repository_is_abstract() -> None:
    assert issubclass(ScrapeRunRepository, ABC)
    with pytest.raises(TypeError):
        ScrapeRunRepository()  # type: ignore[abstract]


def test_supermarket_repository_concrete_subclass() -> None:
    """A minimal concrete impl satisfies the ABC contract."""

    class FakeSupermarketRepo(SupermarketRepository):
        async def get_by_slug(self, slug: str) -> None:
            return None

        async def upsert(self, slug: str, display_name: str, base_url: str, currency: str) -> None:
            return None

    repo = FakeSupermarketRepo()
    assert repo is not None


def test_scrape_run_repository_concrete_subclass() -> None:
    """A minimal concrete impl satisfies the ABC contract."""
    from uuid import uuid4

    class FakeScrapeRunRepo(ScrapeRunRepository):
        async def start(self, supermarket_id: UUID, worker_version: str) -> None:
            return None

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
            return None

    repo = FakeScrapeRunRepo()
    assert repo is not None
