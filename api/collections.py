from fastapi import APIRouter, HTTPException,Response
from services.collection_service import get_vendor_collections, get_vendor_collection_details

router = APIRouter(prefix="/api/portfolio", tags=["collections"])


@router.get("/public/{business_name}/collections/")
async def public_collections(
    business_name: str,
    response: Response,
    v: str | None = None,
):
    collections = await get_vendor_collections(
        business_name,
        version=v
    )

    if collections is None:
        raise HTTPException(status_code=404, detail="Vendor not found")

    response.headers["Cache-Control"] = "no-store"
    return collections


@router.get("/public/{business_name}/collections/{id}/")
async def public_collection_details(
    business_name: str,
    id: int,
    response: Response,
    v: str | None = None,
):
    collection = await get_vendor_collection_details(
        business_name,
        collection_id=id,
        version=v,
    )

    response.headers["Cache-Control"] = "no-store"

    if not collection:
        raise HTTPException(status_code=404, detail="No collection found")

    return collection
