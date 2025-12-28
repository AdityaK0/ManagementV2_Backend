from fastapi import APIRouter, HTTPException,Response
from services.portfolio_service import get_vendor_portfolio
import os
from services.utils import get_meta

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

    path = os.path.join(
        os.environ.get("SQLITE_CACHE_DIR", "../sqlite_cache"),
        f"{business_name}.version"
    )

    try:
        with open(path, "r") as f:
            version = f.read().strip()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Meta not available")

    return {"version": version}



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
