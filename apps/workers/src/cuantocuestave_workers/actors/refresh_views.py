import structlog
import dramatiq

from cuantocuestave_workers.broker import broker  # noqa: F401

logger = structlog.get_logger(__name__)


@dramatiq.actor(queue_name="default", max_retries=3)
def refresh_materialized_views() -> None:
    logger.info("refresh_views_started")
    # TODO: REFRESH MATERIALIZED VIEW CONCURRENTLY mv_latest_prices
    logger.info("refresh_views_finished")
