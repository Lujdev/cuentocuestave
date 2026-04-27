FROM python:3.12-slim AS base
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

FROM base AS builder
RUN pip install uv
COPY pyproject.toml .
COPY packages/domain packages/domain
COPY packages/application packages/application
COPY packages/infrastructure packages/infrastructure
COPY apps/api apps/api
RUN uv sync --package cuantocuestave-api --no-dev

FROM base AS runtime
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/packages packages
COPY --from=builder /app/apps/api apps/api
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "cuantocuestave_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
