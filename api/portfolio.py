from fastapi import APIRouter, HTTPException,Response
from services.portfolio_service import get_vendor_portfolio

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


@router.get("/public/{business_name}/")
async def public_vendor_portfolio(business_name: str,response: Response):
    data = await get_vendor_portfolio(business_name)
    if not data:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    response.headers["Cache-Control"] = (
        "public, max-age=300, stale-while-revalidate=600"
    )

    return data

