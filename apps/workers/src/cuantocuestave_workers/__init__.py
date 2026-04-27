"""cuantocuestave_workers — Dramatiq actors + APScheduler cron jobs.

This package is the wiring layer: no business logic lives here.
On import, logging is configured so all workers emit structured JSON.
"""

import structlog

from cuantocuestave_infra.observability.logging import configure_logging
from cuantocuestave_infra.settings import Settings

_settings = Settings()
configure_logging(log_level=_settings.log_level)

if _settings.sentry_dsn:
    try:
        import sentry_sdk

        sentry_sdk.init(
            dsn=_settings.sentry_dsn,
            environment=_settings.environment,
            traces_sample_rate=0.1,
        )
        structlog.get_logger(__name__).info("sentry_enabled", dsn_prefix=_settings.sentry_dsn[:30])
    except Exception as _sentry_err:
        structlog.get_logger(__name__).warning("sentry_init_failed", error=str(_sentry_err))
