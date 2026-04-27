"""Repository adapters — SQLAlchemy 2.0 implementations of domain ports."""

from cuantocuestave_infra.db.repositories.exchange_rate import SqlExchangeRateRepository
from cuantocuestave_infra.db.repositories.price import SqlPriceRepository
from cuantocuestave_infra.db.repositories.product_listing import SqlProductListingRepository
from cuantocuestave_infra.db.repositories.scrape_run import SqlScrapeRunRepository
from cuantocuestave_infra.db.repositories.supermarket import SqlSupermarketRepository
from cuantocuestave_infra.db.repositories.types import PriceCreate, ScrapeRunResult

__all__ = [
    "PriceCreate",
    "ScrapeRunResult",
    "SqlExchangeRateRepository",
    "SqlPriceRepository",
    "SqlProductListingRepository",
    "SqlScrapeRunRepository",
    "SqlSupermarketRepository",
]
