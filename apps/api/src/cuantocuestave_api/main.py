from contextlib import asynccontextmanager
from typing import AsyncGenerator

import sentry_sdk
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from cuantocuestave_api.routers import analytics, basket, prices, products
from cuantocuestave_api.routers.admin import anomalies, costs, matching, scrapes
from cuantocuestave_infra.db.session import engine
from cuantocuestave_infra.observability.logging import configure_logging
from cuantocuestave_infra.settings import Settings

logger = structlog.get_logger(__name__)
settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    configure_logging(settings.log_level)
    if settings.sentry_dsn:
        sentry_sdk.init(dsn=settings.sentry_dsn, environment=settings.environment)
    logger.info("startup", environment=settings.environment)
    yield
    await engine.dispose()
    logger.info("shutdown")


app = FastAPI(
    title="cuantocuestave API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.environment != "production" else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

app.include_router(products.router, prefix="/api")
app.include_router(prices.router, prefix="/api")
app.include_router(basket.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(scrapes.router, prefix="/api/admin")
app.include_router(matching.router, prefix="/api/admin")
app.include_router(anomalies.router, prefix="/api/admin")
app.include_router(costs.router, prefix="/api/admin")


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
