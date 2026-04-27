"""Base class for Scrapling-based scrapers implementing ScraperPort."""
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from cuantocuestave_domain.ports.scraper import RawListing, ScrapeResult, ScraperPort

logger = structlog.get_logger(__name__)


class BaseScrapler(ScraperPort):
    """Abstract Scrapling-based scraper. Subclasses implement _fetch_listings."""

    max_retries: int = 3
    rate_limit_seconds: float = 1.0

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=5, max=60),
        reraise=True,
    )
    async def scrape(self) -> ScrapeResult:
        log = logger.bind(supermarket=self.supermarket_slug)
        log.info("scrape_start")
        errors: list[str] = []
        listings: list[RawListing] = []
        try:
            listings = await self._fetch_listings()
            log.info("scrape_done", items=len(listings))
        except Exception as exc:
            errors.append(str(exc))
            log.error("scrape_error", error=str(exc))
        return ScrapeResult(
            supermarket_slug=self.supermarket_slug,
            listings=listings,
            errors=errors,
        )

    async def _fetch_listings(self) -> list[RawListing]:
        raise NotImplementedError
