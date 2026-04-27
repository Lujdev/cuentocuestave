"""Excelsior Gama scraper — Scrapling StealthyFetcher (curl_cffi-based)."""
import structlog

from cuantocuestave_domain.ports.scraper import RawListing
from cuantocuestave_infra.scrapers.base import BaseScrapler

logger = structlog.get_logger(__name__)

BASE_URL = "https://www.excelsior-gama.com"


class ExcelsiorGamaScraper(BaseScrapler):
    supermarket_slug = "excelsior-gama"

    async def _fetch_listings(self) -> list[RawListing]:
        # TODO Fase 2: implement with Scrapling StealthyFetcher or DynamicFetcher
        logger.info("excelsior_gama_scraper_stub")
        return []
