"""Plaza's supermarket scraper — Scrapling DynamicFetcher (Playwright-based)."""
import structlog

from cuantocuestave_domain.ports.scraper import RawListing
from cuantocuestave_infra.scrapers.base import BaseScrapler

logger = structlog.get_logger(__name__)

BASE_URL = "https://www.plazas.com.ve"


class PlazasScraper(BaseScrapler):
    supermarket_slug = "plazas"

    async def _fetch_listings(self) -> list[RawListing]:
        # TODO Fase 1: implement with Scrapling DynamicFetcher
        # from scrapling import DynamicFetcher
        # page = await DynamicFetcher.fetch(url, ...)
        # parse listings from page DOM
        logger.info("plazas_scraper_stub")
        return []
