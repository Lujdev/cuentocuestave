from fastapi import APIRouter, Query

from cuantocuestave_api.deps import DbSession

router = APIRouter(tags=["prices"])


@router.get("/products/{slug}/history")
async def price_history(
    slug: str,
    db: DbSession,
    days: int = Query(90, ge=1, le=365),
) -> dict:
    # TODO: use application use case
    return {"slug": slug, "days": days, "prices": []}


@router.get("/products/{slug}/forecast")
async def price_forecast(
    slug: str,
    db: DbSession,
    horizon: int = Query(14, ge=1, le=90),
) -> dict:
    # TODO: use ML forecast
    return {"slug": slug, "horizon": horizon, "forecast": []}


@router.get("/exchange-rates/latest")
async def latest_exchange_rates(db: DbSession) -> dict:
    # TODO: use repository
    return {"bcv": None, "paralelo": None}
