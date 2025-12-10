from fastapi import APIRouter, HTTPException
from services.portfolio_service import get_vendor_portfolio
from serializers.portfolio_serializer import PortfolioSchema  # ✅ Pydantic schema

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


# @router.get("/public/{business_name}/", response_model=PortfolioSchema)
# async def public_vendor_portfolio(business_name: str):
#     """
#     Get public vendor portfolio summary (from Elasticsearch)
#     """
#     data = await get_vendor_portfolio(business_name)

#     if not data:
#         raise HTTPException(status_code=404, detail="Portfolio not found")

#     return data 


@router.get("/public/{business_name}/", response_model=PortfolioSchema)
async def public_vendor_portfolio(business_name: str):
    data = await get_vendor_portfolio(business_name)
    if not data:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    return data 

