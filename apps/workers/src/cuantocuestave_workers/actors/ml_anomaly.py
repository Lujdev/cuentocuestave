import structlog
import dramatiq

from cuantocuestave_workers.broker import broker  # noqa: F401

logger = structlog.get_logger(__name__)


@dramatiq.actor(queue_name="ml", max_retries=1)
def detect_anomalies() -> None:
    logger.info("anomaly_detection_started")
    # TODO: IsolationForestRunner
    logger.info("anomaly_detection_finished")
