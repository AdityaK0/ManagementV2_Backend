from fastapi import APIRouter, HTTPException
from services.collection_service import get_vendor_collections

router = APIRouter(prefix="/api/portfolio", tags=["collections"])


@router.get("/public/{business_name}/collections/")
async def public_collections(business_name: str):
    collections = await get_vendor_collections(business_name)

    if not collections:
        raise HTTPException(status_code=404, detail="No collections found")

    return collections

