from fastapi import APIRouter, HTTPException,Response
from services.portfolio_service import get_vendor_portfolio,get_meta_data


router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


@router.get("/public/{business_name}/")
async def public_vendor_portfolio(business_name: str,response: Response):
    data = await get_vendor_portfolio(business_name)
    if not data:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    response.headers["Cache-Control"] = (
        "public, max-age=300, s-maxage=300, stale-while-revalidate=60"
        # "public, max-age=0, s-maxage=300"
    )

    return data




@router.get("/public/{business_name}/meta/")
async def portfolio_meta_data(business_name: str, response: Response):
    response.headers["Cache-Control"] = "no-store"
    return await get_meta_data(business_name)


# @router.get("/public/{business_name}/meta/") # accessing from RAM Based files
# async def portfolio_meta_data(business_name: str, response: Response):
#     response.headers["Cache-Control"] = "no-store"
#     version = get_meta(business_name)
#     return {"version": version}





# @router.get("/public/{business_name}/meta/")
# async def portfolio_meta_data(business_name: str,response: Response):
#     data = await get_meta_data(business_name)
#     if not data:
#         raise HTTPException(status_code=404, detail="Portfolio not found")

#     response.headers["Cache-Control"] = "no-store"

#     return data
