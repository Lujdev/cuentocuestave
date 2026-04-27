"""Pydantic v2 models for repository write operations."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PriceCreate(BaseModel):
    """Validated payload for inserting a new price row (append-only)."""

    model_config = ConfigDict(frozen=True)

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


class ScrapeRunResult(BaseModel):
    """Validated payload for finishing a scrape run."""

    model_config = ConfigDict(frozen=True)

    run_id: UUID
    status: str  # "success" | "partial" | "failed" | "skipped"
    items_seen: int = 0
    items_new: int = 0
    items_updated: int = 0
    errors_count: int = 0
    error_summary: dict | None = None
