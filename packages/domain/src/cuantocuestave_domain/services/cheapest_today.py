from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from cuantocuestave_domain.entities.price import Price


@dataclass(frozen=True)
class CheapestResult:
    product_id: UUID
    supermarket_id: UUID
    supermarket_slug: str
    price_usd: Decimal
    unit_price_usd: Decimal


class CheapestTodayService:
    def find_cheapest(self, prices: list[Price], supermarket_slugs: dict[UUID, str]) -> CheapestResult | None:
        available = [p for p in prices if p.available]
        if not available:
            return None
        cheapest = min(available, key=lambda p: p.unit_price_usd)
        listing_id = cheapest.product_listing_id
        # supermarket_id resolved by caller from listing
        return CheapestResult(
            product_id=listing_id,  # placeholder — caller resolves product_id
            supermarket_id=listing_id,  # placeholder
            supermarket_slug=supermarket_slugs.get(listing_id, "unknown"),
            price_usd=cheapest.price_usd,
            unit_price_usd=cheapest.unit_price_usd,
        )
