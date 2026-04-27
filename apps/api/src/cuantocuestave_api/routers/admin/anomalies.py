from fastapi import APIRouter, Depends

from cuantocuestave_api.auth.neon_auth import require_admin
from cuantocuestave_api.deps import DbSession

router = APIRouter(tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/anomalies")
async def list_anomalies(reviewed: bool = False, db: DbSession = Depends()) -> dict:
    return {"anomalies": []}


@router.post("/anomalies/{anomaly_id}/review")
async def review_anomaly(anomaly_id: str, db: DbSession = Depends()) -> dict:
    return {"anomaly_id": anomaly_id, "reviewed": True}
