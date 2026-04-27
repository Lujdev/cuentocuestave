from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass
class RawListing:
    external_id: str
    raw_name: str
    raw_brand: str | None
    raw_unit: str | None
    raw_category: str | None
    price_local: Decimal
    currency: str
    available: bool
    image_url: str | None
    product_url: str | None


@dataclass
class ScrapeResult:
    supermarket_slug: str
    listings: list[RawListing]
    errors: list[str]


class ScraperPort(ABC):
    """Implemented by infrastructure scrapers (Scrapling-based)."""

    @abstractmethod
    async def scrape(self) -> ScrapeResult:
        ...

    @property
    @abstractmethod
    def supermarket_slug(self) -> str:
        ...
