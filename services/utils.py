import asyncio
import os

async def run_sqlite(fn):
    return await asyncio.to_thread(fn)


META_CACHE: dict[str, str] = {}

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

def get_meta(business_name: str) -> str:
    try:
        print("reading from cache")
        return META_CACHE[business_name]
    except KeyError:
        print("reading from disk")
        version = read_version_from_disk(business_name)
        META_CACHE[business_name] = version
        return version
