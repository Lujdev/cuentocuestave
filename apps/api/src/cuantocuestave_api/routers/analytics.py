from fastapi import APIRouter

from cuantocuestave_api.deps import DbSession

router = APIRouter(tags=["analytics"])


@router.get("/analytics/clusters")
async def product_clusters(db: DbSession) -> dict:
    # TODO: return latest cluster assignments
    return {"clusters": []}


@router.get("/analytics/anomalies")
async def recent_anomalies(db: DbSession) -> dict:
    # TODO: return recent unreviewed anomalies
    return {"anomalies": []}
