import os
import json
from typing import Dict, Any, Optional
from fastapi import HTTPException

BASE_DB_FOLDER = os.environ.get("SQLITE_CACHE_DIR", "../sqlite_cache")  # <-- configure this

def load_sqlite_db(vendor_slug: str) -> str:
    """
    Resolve vendor slug → SQLite file path.
    """
    db_path = os.path.join(BASE_DB_FOLDER, f"{vendor_slug}.db")

    if not os.path.exists(db_path):
        return None
    return db_path
