from fastapi import APIRouter, Query,Response,Depends
from typing import Union
from services.product_service import get_vendor_products,get_vendor_product_detail,get_vendor_product_categories
from db.connection import get_db
from psycopg2.extensions import connection

router = APIRouter(prefix="/api/portfolio", tags=["products"])


@router.get("/public/{business_name}/products/")
def public_products(
    business_name: str,
    response: Response,
    page: int = 1,
    page_size: int = 10,
    search: str = "",
    min_price: Union[float, None, str] = Query(None),
    max_price: Union[float, None, str] = Query(None),
    category: Union[str, None, str] = Query(None),
    v: str | None = None,
    db: connection = Depends(get_db),
):
    min_price = None if min_price in ("", None) else float(min_price)
    max_price = None if max_price in ("", None) else float(max_price)
    category = None if category in ("", None) else category

    if (
        page == 1
        and page_size == 10
        and not search
        and not min_price
        and not max_price
        and not category
        #and not v
    ):
        response.headers["Cache-Control"] = (
            "public, max-age=300, s-maxage=300, stale-while-revalidate=60"
        )
    else:
        response.headers["Cache-Control"] = "no-store"

    return get_vendor_products(
        db,
        business_name,
        page,
        page_size,
        search,
        min_price,
        max_price,
        category,
        v,
    )



@router.get("/public/{business_name}/products/{product_id}/")
def public_product_detail(
    business_name: str,
    product_id: int,
    response: Response,
    v: str | None = None,
    db: connection = Depends(get_db),
):
    response.headers["Cache-Control"] = "no-store"

    data = get_vendor_product_detail(
        db,
        business_name,
        product_id,
        version=v,
    )

    if not data:
        raise HTTPException(status_code=404, detail="Product not found")

    return data
 

@router.get("/public/{business_name}/categories/")
def get_vendor_categories(
    business_name: str,
    response: Response,
    v: str | None = None,
    db: connection = Depends(get_db),
):
    response.headers["Cache-Control"] = (
        "public, max-age=300, s-maxage=300, stale-while-revalidate=60"
    )

    return get_vendor_product_categories(
        db,
        business_name,
        version=v,
    )
    
