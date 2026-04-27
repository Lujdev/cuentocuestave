"""cuantocuestave_workers — Dramatiq actors + APScheduler cron jobs.

This package is the wiring layer: no business logic lives here.
On import, logging is configured so all workers emit structured JSON.
"""

from cuantocuestave_infra.observability.logging import configure_logging
from cuantocuestave_infra.settings import Settings

_settings = Settings()
configure_logging(log_level=_settings.log_level)
