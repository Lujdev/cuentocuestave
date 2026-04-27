FROM python:3.12-slim AS base
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

# Playwright deps for Scrapling DynamicFetcher
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

FROM base AS builder
RUN pip install uv
COPY pyproject.toml .
COPY packages packages
COPY apps/workers apps/workers
RUN uv sync --package cuantocuestave-workers --no-dev

FROM base AS runtime
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/packages packages
COPY --from=builder /app/apps/workers apps/workers
ENV PATH="/app/.venv/bin:$PATH"
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/bin

# Default: run Dramatiq workers
CMD ["dramatiq", "cuantocuestave_workers.actors.scrape", \
     "cuantocuestave_workers.actors.match", \
     "cuantocuestave_workers.actors.exchange_rates", \
     "cuantocuestave_workers.actors.ml_anomaly", \
     "cuantocuestave_workers.actors.ml_forecast", \
     "cuantocuestave_workers.actors.ml_cluster", \
     "cuantocuestave_workers.actors.refresh_views", \
     "--processes", "2", "--threads", "4"]
