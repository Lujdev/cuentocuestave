import structlog
import dramatiq

from cuantocuestave_workers.broker import broker  # noqa: F401

logger = structlog.get_logger(__name__)


@dramatiq.actor(queue_name="ml", max_retries=1)
def run_forecasts() -> None:
    logger.info("forecast_started")
    # TODO: ProphetRunner + ArimaRunner per product
    logger.info("forecast_finished")
