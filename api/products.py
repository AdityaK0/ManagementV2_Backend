from fastapi import APIRouter, Query
from typing import Union
from services.product_service import get_vendor_products,get_vendor_product_detail

router = APIRouter(prefix="/api/portfolio", tags=["products"])


@router.get("/public/{business_name}/products/")
async def public_products(
    business_name: str,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
    min_price: Union[float, None, str] = Query(None),
    max_price: Union[float, None, str] = Query(None),
):
    # convert empty strings to None
    min_price = None if min_price in ("", None) else float(min_price)
    max_price = None if max_price in ("", None) else float(max_price)

    return await get_vendor_products(
        business_name,
        page,
        page_size,
        search,
        min_price,
        max_price,
    )







@router.get("/public/{business_name}/products/{product_id}/")
async def public_product_detail(business_name: str, product_id: int):
    """
    Fetch a single product detail by vendor slug (business_name) and product_id.
    """
    
    return await get_vendor_product_detail(
        business_name,
        product_id
    )
    