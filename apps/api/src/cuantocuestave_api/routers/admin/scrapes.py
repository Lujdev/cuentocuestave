from typing import Annotated

from fastapi import APIRouter, Depends

from cuantocuestave_api.auth.neon_auth import require_admin
from cuantocuestave_api.deps import DbSession

router = APIRouter(tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/scrapes")
async def list_scrape_runs(db: DbSession) -> dict:
    return {"runs": []}


@router.post("/scrapes/trigger/{supermarket_slug}")
async def trigger_scrape(supermarket_slug: str) -> dict:
    # TODO: enqueue Dramatiq actor
    return {"queued": supermarket_slug}
