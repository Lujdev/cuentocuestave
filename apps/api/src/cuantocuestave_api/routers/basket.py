from fastapi import APIRouter

from cuantocuestave_api.deps import DbSession

router = APIRouter(tags=["basket"])


@router.get("/basket/index")
async def basket_index(db: DbSession) -> dict:
    """Canasta básica vs salario mínimo + tipo de cambio."""
    # TODO: BasketIndexService
    return {"basket_usd": None, "min_wage_usd": None, "ratio": None, "history": []}
