from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SupermarketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    slug: str
    display_name: str


class LatestPriceOut(BaseModel):
    supermarket: SupermarketOut
    price_usd: Decimal
    price_ves_bcv: Decimal | None
    price_ves_paralelo: Decimal | None
    unit_price_usd: Decimal
    available: bool
    observed_at: datetime


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    slug: str
    display_name: str
    brand: str | None
    canonical_unit: str
    canonical_pack_size: Decimal
    category: str
    is_basic_basket: bool
    image_url: str | None
    latest_prices: list[LatestPriceOut] = []


class ProductListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    slug: str
    display_name: str
    brand: str | None
    category: str
    is_basic_basket: bool
    cheapest_price_usd: Decimal | None
    cheapest_supermarket: str | None


class PaginatedProducts(BaseModel):
    items: list[ProductListItem]
    page: int
    page_size: int
    total: int
