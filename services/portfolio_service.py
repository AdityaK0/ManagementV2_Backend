import asyncio
import json
from typing import Dict, Any, Optional
from services.sqlite_manager import sqlite_manager


async def get_vendor_portfolio(handle: str) -> Optional[Dict[str, Any]]:
    async with sqlite_manager.get_db(handle) as conn:
        row = await asyncio.to_thread(
            lambda: conn.execute(
                "SELECT response_json FROM portfolio LIMIT 1"
            ).fetchone()
        )

    if not row:
        return None

    try:
        return json.loads(row["response_json"])
    except Exception:
        return None


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
