import structlog
import dramatiq

from cuantocuestave_workers.broker import broker  # noqa: F401

logger = structlog.get_logger(__name__)


@dramatiq.actor(queue_name="default", max_retries=5)
def fetch_exchange_rates() -> None:
    logger.info("exchange_rates_fetch_started")
    # TODO: BCV + monitor_dolar_ve scrapers
    logger.info("exchange_rates_fetch_finished")
