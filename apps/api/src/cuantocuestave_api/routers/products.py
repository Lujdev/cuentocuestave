from fastapi import APIRouter, Query

from cuantocuestave_api.deps import DbSession

router = APIRouter(tags=["products"])


@router.get("/products")
async def list_products(
    db: DbSession,
    category: str | None = None,
    search: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict:
    # TODO: use application use case
    return {"items": [], "page": page, "page_size": page_size, "total": 0}


@router.get("/products/{slug}")
async def get_product(slug: str, db: DbSession) -> dict:
    # TODO: use application use case
    return {"slug": slug}
