from fastapi import APIRouter, HTTPException
from services.collection_service import get_vendor_collections, get_vendor_collection_details

router = APIRouter(prefix="/api/portfolio", tags=["collections"])


@router.get("/public/{business_name}/collections/")
async def public_collections(business_name: str):
    collections = await get_vendor_collections(business_name)

    if not collections:
        raise HTTPException(status_code=404, detail="No collections found")

    return collections

@router.get("/public/{business_name}/collections/{id}")
async def public_collectio_details(business_name: str, id: int):
    collection = await get_vendor_collection_details(business_name, id)

    if not collection:
        raise HTTPException(status_code=404, detail="No collection found")

    return collection