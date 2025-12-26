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


async def get_meta_data(business_name: str):

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
