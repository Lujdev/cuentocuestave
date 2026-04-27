from fastapi import APIRouter, Depends

from cuantocuestave_api.auth.neon_auth import require_admin
from cuantocuestave_api.deps import DbSession

router = APIRouter(tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/matching/queue")
async def matching_queue(db: DbSession) -> dict:
    """Listings with match_status=ambiguous pending manual review."""
    return {"items": [], "total": 0}


@router.post("/matching/{listing_id}/decide")
async def decide_match(listing_id: str, canonical_product_id: str, db: DbSession) -> dict:
    # TODO: write matching_decision, update listing
    return {"listing_id": listing_id, "canonical_product_id": canonical_product_id}
