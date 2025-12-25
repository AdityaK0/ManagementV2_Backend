from fastapi import APIRouter, HTTPException
from services.portfolio_service import get_vendor_portfolio
from utils.cache_headers import public_cache

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


@router.get("/public/{business_name}/")
@public_cache(max_age=300, stale_while_revalidate=600)
async def public_vendor_portfolio(business_name: str):
    data = await get_vendor_portfolio(business_name)
    if not data:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    return data