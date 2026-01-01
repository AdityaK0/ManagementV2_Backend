import asyncio
from typing import Optional, Dict, Any

try:
    import ujson as json
except ImportError:
    import json

from db.postgres_read_pool import get_pg_pool


async def get_vendor_portfolio(
    handle: str,
    version: str | None = None
) -> Optional[Dict[str, Any]]:
    pool = get_pg_pool()

    def db_call():
        conn = pool.getconn()
        try:
            with conn.cursor() as cur:
                if version:
                    # 🎯 Explicit version fetch (immutable)
                    cur.execute("""
                        SELECT p.snapshot
                        FROM portfolio p
                        JOIN vendor_version vv ON vv.id = p.vendor_version_id
                        JOIN vendor v ON v.id = p.vendor_id
                        WHERE v.handle = %s
                          AND vv.version = %s
                        LIMIT 1
                    """, (handle, version))
                else:
                    # 🧠 Fallback to best version
                    cur.execute("""
                        SELECT p.snapshot
                        FROM portfolio p
                        JOIN vendor_version vv ON vv.id = p.vendor_version_id
                        JOIN vendor v ON v.id = p.vendor_id
                        WHERE v.handle = %s
                        ORDER BY
                            vv.is_active DESC,
                            vv.published_at DESC
                        LIMIT 1
                    """, (handle,))

                row = cur.fetchone()
                return row[0] if row else None

        finally:
            pool.putconn(conn)

    return await asyncio.to_thread(db_call)



async def get_meta_data(handle: str) -> Dict[str, Any]:
    pool = get_pg_pool()

    def db_call():
        conn = pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT vv.version
                    FROM vendor_version vv
                    JOIN vendor v ON v.id = vv.vendor_id
                    WHERE v.handle = %s
                    ORDER BY
                        vv.is_active DESC,
                        vv.published_at DESC
                    LIMIT 1
                """, (handle,))
                row = cur.fetchone()
                return {
                    "version": row[0] if row else None
                }
        finally:
            pool.putconn(conn)

    return await asyncio.to_thread(db_call)



# import asyncio
# from typing import Dict, Any, Optional
# from services.sqlite_manager import sqlite_manager

# # OPT-3: Use ujson for 20-40% faster JSON parsing
# try:
#     import ujson as json
# except ImportError:
#     import json  # Fallback to stdlib


# async def get_vendor_portfolio(handle: str) -> Optional[Dict[str, Any]]:
#     async with sqlite_manager.get_db(handle) as conn:
#         row = await asyncio.to_thread(
#             lambda: conn.execute(
#                 "SELECT response_json FROM portfolio LIMIT 1"
#             ).fetchone()
#         )

#     if not row:
#         return None

#     # OPT-4: Parse large JSON off event loop
#     def parse_json(row):
#         try:
#             return json.loads(row["response_json"])
#         except Exception:
#             return None
    
#     return await asyncio.to_thread(lambda: parse_json(row))


# async def get_meta_data(business_name: str):

#     async with sqlite_manager.get_db(business_name) as conn:
#         row = await asyncio.to_thread(
#             lambda: conn.execute(
#                 "SELECT version FROM db_version LIMIT 1"
#             ).fetchone()
#         )

#     if not row:
#         return {"version": None}

#     return {"version": row["version"]}

