from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
import logging
from lambda_sqlite_builder.local_runner import build_local

router = APIRouter()
logger = logging.getLogger("internal_api")

class BuildRequest(BaseModel):
    vendor_slug: str

@router.post("/build")
async def trigger_local_build(payload: BuildRequest, background_tasks: BackgroundTasks):
    """
    Trigger a local SQLite build for a vendor.
    Useful for development environment.
    """
    logger.info(f"Received build request for {payload.vendor_slug}")
    
    # Validating slug could go here
    
    # Run build in background
    background_tasks.add_task(build_local, payload.vendor_slug)
    
    return {
        "status": "accepted", 
        "message": f"Local build triggered for {payload.vendor_slug}",
        "mode": "background_task"
    }
