"""APScheduler cron jobs — persisted in Postgres via SQLAlchemyJobStore."""
import structlog
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.blocking import BlockingScheduler

from cuantocuestave_infra.settings import Settings

from .actors.exchange_rates import fetch_exchange_rates
from .actors.ml_anomaly import detect_anomalies
from .actors.ml_cluster import run_clustering
from .actors.ml_forecast import run_forecasts
from .actors.refresh_views import refresh_materialized_views
from .actors.scrape import scrape_supermarket

logger = structlog.get_logger(__name__)
settings = Settings()

jobstores = {
    "default": SQLAlchemyJobStore(url=settings.database_url_sync),
}
executors = {"default": ThreadPoolExecutor(4)}

scheduler = BlockingScheduler(jobstores=jobstores, executors=executors)


def register_jobs() -> None:
    # Scraping: every 6h per supermarket
    for slug in ["plazas", "excelsior-gama"]:
        scheduler.add_job(
            scrape_supermarket.send,
            "cron",
            args=[slug],
            hour="0,6,12,18",
            id=f"scrape_{slug}",
            replace_existing=True,
        )

    # Exchange rates: every 2h
    scheduler.add_job(
        fetch_exchange_rates.send,
        "cron",
        hour="*/2",
        id="exchange_rates",
        replace_existing=True,
    )

    # Materialized view refresh: 15 min after each scrape slot
    scheduler.add_job(
        refresh_materialized_views.send,
        "cron",
        hour="0,6,12,18",
        minute="15",
        id="refresh_views",
        replace_existing=True,
    )

    # Anomaly detection: daily at 02:00 VET (UTC-4 = 06:00 UTC)
    scheduler.add_job(
        detect_anomalies.send,
        "cron",
        hour="6",
        id="detect_anomalies",
        replace_existing=True,
    )

    # Forecasting: weekly on Monday 03:00 VET (07:00 UTC)
    scheduler.add_job(
        run_forecasts.send,
        "cron",
        day_of_week="mon",
        hour="7",
        id="run_forecasts",
        replace_existing=True,
    )

    # Clustering: weekly on Monday 04:00 VET (08:00 UTC)
    scheduler.add_job(
        run_clustering.send,
        "cron",
        day_of_week="mon",
        hour="8",
        id="run_clustering",
        replace_existing=True,
    )

    logger.info("scheduler_jobs_registered")


if __name__ == "__main__":
    register_jobs()
    logger.info("scheduler_starting")
    scheduler.start()
