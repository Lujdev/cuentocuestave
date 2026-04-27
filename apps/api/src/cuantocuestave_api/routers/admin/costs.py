from fastapi import APIRouter, Depends

from cuantocuestave_api.auth.neon_auth import require_admin
from cuantocuestave_api.deps import DbSession

router = APIRouter(tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/costs")
async def cost_summary(db: DbSession = Depends()) -> dict:
    """LLM cost, scrape run stats, Redis memory."""
    return {"llm_today_usd": 0.0, "scrapes_today": 0, "redis_mb": 0}
