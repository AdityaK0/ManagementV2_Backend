import sqlite3
from typing import Dict, Any, Optional
from config import settings
import json
async def get_vendor_portfolio(handle: str) -> Optional[Dict[str, Any]]:
    """
    Fetch vendor public portfolio from its SQLite DB.
    Replaces Elasticsearch.
    """

    db_path = load_sqlite_db(handle)
    if not db_path:
        return None

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        # Only one row in table
        cur.execute("SELECT response_json FROM portfolio LIMIT 1;")
        row = cur.fetchone()

        conn.close()

        if not row:
            return None

        response_json = row["response_json"]
        try:
            return json.loads(response_json)
        except:
            return None

    except Exception as e:
        print("[SQLite ERROR]", e)
        return None


# """
# Portfolio service — fetch portfolio details from Elasticsearch
# """

# from typing import Dict, Any, Optional
# from config import settings
# from es.es_client import get_es_context



# async def get_vendor_portfolio(handle: str) -> Optional[Dict[str, Any]]:
#     """
#     Fetch a vendor portfolio document from Elasticsearch.

#     Args:
#         handle (str): vendor slug from route
#     Returns:
#         dict | None
#     """

#     async with get_es_context() as es:
#         try:
#             response = await es.search(
#                 index=settings.PORTFOLIOS_INDEX,
#                 query={
#                     "bool": {
#                         "filter": [
#                             {"term": {"handle": handle}},
#                             {"term": {"is_public": True}}
#                         ]
#                     }
#                 },
#                 size=1
#             )

#             hits = response.get("hits", {}).get("hits", [])
#             if not hits:
#                 return None

#             # Return ES document source
#             return hits[0]["_source"]

#         except Exception as ex:
#             print(f"[ES ERROR] get_vendor_portfolio: {ex}")
#             return None
