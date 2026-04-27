import structlog
import dramatiq

from cuantocuestave_workers.broker import broker  # noqa: F401 — registers broker

logger = structlog.get_logger(__name__)


@dramatiq.actor(queue_name="scraping", max_retries=3)
def scrape_supermarket(supermarket_slug: str) -> None:
    logger.info("scrape_started", supermarket=supermarket_slug)
    # TODO: resolve ScraperPort impl from DI, run scrape, persist results
    logger.info("scrape_finished", supermarket=supermarket_slug)
