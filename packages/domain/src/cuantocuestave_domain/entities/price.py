from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class Price:
    id: int
    product_listing_id: UUID
    price_local: Decimal
    currency: str
    price_usd: Decimal
    price_ves_bcv: Decimal | None
    price_ves_paralelo: Decimal | None
    unit_price_usd: Decimal
    available: bool
    observed_at: datetime
    scrape_run_id: UUID


@dataclass(frozen=True)
class ExchangeRate:
    id: int
    source: str  # "bcv" | "paralelo" | "monitor_dolar_ve"
    rate_ves_per_usd: Decimal
    observed_at: datetime
