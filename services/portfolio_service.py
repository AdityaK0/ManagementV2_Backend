import asyncio
from typing import Dict, Any, Optional
from services.sqlite_manager import sqlite_manager

# OPT-3: Use ujson for 20-40% faster JSON parsing
try:
    import ujson as json
except ImportError:
    import json  # Fallback to stdlib


async def get_vendor_portfolio(handle: str) -> Optional[Dict[str, Any]]:
    async with sqlite_manager.get_db(handle) as conn:
        row = await asyncio.to_thread(
            lambda: conn.execute(
                "SELECT response_json FROM portfolio LIMIT 1"
            ).fetchone()
        )

    if not row:
        return None

    # OPT-4: Parse large JSON off event loop
    def parse_json(row):
        try:
            return json.loads(row["response_json"])
        except Exception:
            return None
    
    return await asyncio.to_thread(lambda: parse_json(row))


import os
import logging

# Simple cache to track last known mtime for each vendor DB
_vendor_db_mtimes: Dict[str, float] = {}
_logger = logging.getLogger("portfolio_service")

async def get_meta_data(business_name: str):
    """
    Fetches the database version.
    CRITICAL: This method also acts as a health check for the DB file.
    It checks if the file has been replaced (e.g., during a publish).
    If a change is detected, it invalidates the connection pool to ensure fresh data.
    """
    
    # 1. Freshness Check using internal API of SQLiteManager (User Requested Path)
    try:
        db_path = sqlite_manager._get_db_path(business_name)
        if os.path.exists(db_path):
            current_mtime = os.stat(db_path).st_mtime
            last_known = _vendor_db_mtimes.get(business_name)
            
            if last_known is not None and current_mtime != last_known:
                _logger.info(f"DB update detected for {business_name}. Invalidating connection pool.")
                # Force clear the pool so get_db() below creates a FRESH connection
                if business_name in sqlite_manager._pools:
                    # Best-effort close of stale connections
                    pool = sqlite_manager._pools[business_name]
                    while pool:
                        try:
                            # If pool stores (conn, mtime) tuples or just conn, handle both just in case
                            item = pool.pop()
                            conn = item[0] if isinstance(item, tuple) else item
                            conn.close()
                        except Exception as e:
                            _logger.warning(f"Error closing stale connection: {e}")
                    
                    # Ensure pool is empty
                    sqlite_manager._pools[business_name].clear()
            
            _vendor_db_mtimes[business_name] = current_mtime
    except Exception as e:
        _logger.error(f"Failed to perform freshness check: {e}")

    # 2. Standard Query (Now guaranteed to use fresh connection if invalidation occurred)
    async with sqlite_manager.get_db(business_name) as conn:
        row = await asyncio.to_thread(
            lambda: conn.execute(
                "SELECT version FROM db_version LIMIT 1"
            ).fetchone()
        )

    if not row:
        return {"version": None}

    return {"version": row["version"]}
# import sqlite3
# import json
# from typing import Dict, Any, Optional
# from services.sqlite_manager import sqlite_manager


# async def get_vendor_portfolio(handle: str) -> Optional[Dict[str, Any]]:
#     """
#     Fetch vendor public portfolio from SQLite (replaces Elasticsearch).
#     """

#     import asyncio

#     async with sqlite_manager.get_db(handle) as conn:
#         row = await asyncio.to_thread(
#             lambda: conn.execute(
#                 "SELECT response_json FROM portfolio LIMIT 1"
#             ).fetchone()
#         )

    
#     # async with sqlite_manager.get_db(handle) as conn:
#     #     row = conn.execute("SELECT response_json FROM portfolio LIMIT 1").fetchone()

#     if not row:
#         return None

#     try:
#         return json.loads(row["response_json"])
#     except Exception:
#         return None
