import asyncio
import os
from fastapi import HTTPException

META_DIR = os.environ.get("META_DIR")
SQLITE_CACHE_DIR = os.environ.get("SQLITE_CACHE_DIR", "../sqlite_cache")






def get_meta(business_name: str) -> str:
    """
    Reads vendor version from META_DIR (RAM/tmpfs) if configured,
    otherwise falls back to disk.
    """

    if META_DIR:
        print("read from ram based file")
        path = os.path.join(META_DIR, f"{business_name}.version")
    else:
        print("read from disk")
        path = os.path.join(SQLITE_CACHE_DIR, f"{business_name}.version")

    try:
        with open(path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Meta not available")



def read_version_from_disk(business_name: str) -> str:
    path = os.path.join(
        os.environ.get("SQLITE_CACHE_DIR", "../sqlite_cache"),
        f"{business_name}.version"
    )

    try:
        with open(path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Meta not available")

    
async def run_sqlite(fn):
    return await asyncio.to_thread(fn)