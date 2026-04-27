from dataclasses import dataclass
from uuid import UUID

from cuantocuestave_domain.errors import ProductNotFound
from cuantocuestave_domain.ports.repositories import PriceRepository, ProductRepository
from cuantocuestave_domain.services.cheapest_today import CheapestResult, CheapestTodayService


@dataclass
class ComputeCheapestUseCase:
    product_repo: ProductRepository
    price_repo: PriceRepository
    service: CheapestTodayService = CheapestTodayService()

    async def execute(self, product_slug: str) -> CheapestResult | None:
        product = await self.product_repo.get_by_slug(product_slug)
        if not product:
            raise ProductNotFound(product_slug)
        prices = await self.price_repo.get_latest_by_product(product.id)
        return self.service.find_cheapest(prices, {})
