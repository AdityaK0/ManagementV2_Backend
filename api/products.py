from fastapi import APIRouter, Query,Response
from typing import Union
from services.product_service import get_vendor_products,get_vendor_product_detail,get_vendor_product_categories

router = APIRouter(prefix="/api/portfolio", tags=["products"])


@router.get("/public/{business_name}/products/")
async def public_products(
    business_name: str,
    response: Response,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
    min_price: Union[float, None, str] = Query(None),
    max_price: Union[float, None, str] = Query(None),
    category: Union[str, None, str] = Query(None),
    
):
    # convert empty strings to None
    min_price = None if min_price in ("", None) else float(min_price)
    max_price = None if max_price in ("", None) else float(max_price)
    category = None if category in ("", None) else category


    if page == 1 and page_size == 10:
        response.headers["Cache-Control"] = (
             "public, max-age=30, s-maxage=300, stale-while-revalidate=60"
            # "public, max-age=0, s-maxage=300"
        )


    return await get_vendor_products(
        business_name,
        page,
        page_size,
        search,
        min_price,
        max_price,
        category,
    )







@router.get("/public/{business_name}/products/{product_id}/")
async def public_product_detail(business_name: str, product_id: int,response: Response):
    """
    Fetch a single product detail by vendor slug (business_name) and product_id.
    """
    response.headers["Cache-Control"] = "no-store"
    return await get_vendor_product_detail(
        business_name,
        product_id
    )
    

@router.get("/public/{business_name}/categories/")
async def get_vendor_categories(business_name: str,response: Response):
    response.headers["Cache-Control"] = (
         "public, max-age=30, s-maxage=300, stale-while-revalidate=60"
    #    "public, max-age=30, s-maxage=300, stale-while-revalidate=60"
    )
    return await get_vendor_product_categories(
        business_name
    )
    
