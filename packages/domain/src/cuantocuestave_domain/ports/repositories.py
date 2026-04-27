from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from cuantocuestave_domain.entities.price import ExchangeRate, Price
from cuantocuestave_domain.entities.product import Product, ProductListing


class ProductRepository(ABC):
    @abstractmethod
    async def get_by_slug(self, slug: str) -> Product | None: ...

    @abstractmethod
    async def list_published(
        self,
        category: str | None,
        search: str | None,
        offset: int,
        limit: int,
    ) -> tuple[list[Product], int]: ...


class ProductListingRepository(ABC):
    @abstractmethod
    async def get_pending_match(self, limit: int = 50) -> list[ProductListing]: ...

    @abstractmethod
    async def update_match(
        self,
        listing_id: UUID,
        canonical_product_id: UUID,
        confidence: float,
        method: str,
    ) -> None: ...


class PriceRepository(ABC):
    @abstractmethod
    async def get_latest_by_product(self, product_id: UUID) -> list[Price]: ...

    @abstractmethod
    async def get_history(
        self,
        product_id: UUID,
        days: int,
    ) -> list[Price]: ...


class ExchangeRateRepository(ABC):
    @abstractmethod
    async def get_latest(self, source: str) -> ExchangeRate | None: ...


class SupermarketRepository(ABC):
    """Port for persisting and retrieving supermarket records."""

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Any | None: ...

    @abstractmethod
    async def upsert(
        self,
        slug: str,
        display_name: str,
        base_url: str,
        currency: str,
    ) -> Any: ...


class ScrapeRunRepository(ABC):
    """Port for recording scrape run lifecycle events."""

    @abstractmethod
    async def start(self, supermarket_id: UUID, worker_version: str) -> Any: ...

    @abstractmethod
    async def finish(
        self,
        run_id: UUID,
        status: str,
        items_seen: int,
        items_new: int,
        items_updated: int,
        errors_count: int,
        error_summary: dict | None,
    ) -> None: ...
