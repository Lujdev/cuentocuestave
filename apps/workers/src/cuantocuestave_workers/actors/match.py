import structlog
import dramatiq

from cuantocuestave_workers.broker import broker  # noqa: F401

logger = structlog.get_logger(__name__)


@dramatiq.actor(queue_name="matching", max_retries=2)
def match_pending_listings(supermarket_slug: str) -> None:
    logger.info("matching_started", supermarket=supermarket_slug)
    # TODO: MatchListingUseCase
    logger.info("matching_finished", supermarket=supermarket_slug)
