from fastapi import APIRouter, HTTPException,Response,Depends
from services.collection_service import get_vendor_collections, get_vendor_collection_details
from db.connection import get_db
from psycopg2.extensions import connection

router = APIRouter(prefix="/api/portfolio", tags=["collections"])


@router.get("/public/{business_name}/collections/")
def public_collections(
    business_name: str,
    response: Response,
    v: str | None = None,
    db: connection = Depends(get_db),
):
    collections = get_vendor_collections(
        db,
        business_name,
        version=v,
    )

    if collections is None:
        raise HTTPException(status_code=404, detail="Vendor not found")

    response.headers["Cache-Control"] = "no-store"
    return collections


@router.get("/public/{business_name}/collections/{id}/")
def public_collection_details(
    business_name: str,
    id: int,
    response: Response,
    v: str | None = None,
    db: connection = Depends(get_db),
):
    collection = get_vendor_collection_details(
        db,
        business_name,
        collection_id=id,
        version=v,
    )

    response.headers["Cache-Control"] = "no-store"

    if not collection:
        raise HTTPException(status_code=404, detail="No collection found")

    return collection