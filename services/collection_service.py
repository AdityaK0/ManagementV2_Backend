from services.sqlite_manager import sqlite_manager
from config import settings
import math
import json


async def get_vendor_collections(handle: str):
    """
    Fetch all portfolio collections for a vendor from SQLite.
    """

    async with sqlite_manager.get_db(handle) as conn:

        # 1️⃣ Get portfolio ID
        portfolio_row = conn.execute(
            "SELECT id FROM portfolio LIMIT 1"
        ).fetchone()

        if not portfolio_row:
            return None
        
        portfolio_id = portfolio_row["id"]

        # 2️⃣ Fetch all active collections
        collections = conn.execute(
            """
            SELECT *
            FROM portfolio_collection
            WHERE portfolio_id = ?
              AND is_active = 1
            ORDER BY "order" ASC, id ASC
            """,
            (portfolio_id,)
        ).fetchall()

        if not collections:
            return []

        collection_ids = [c["id"] for c in collections]

        # 3️⃣ Fetch products for each collection
        placeholders = ",".join("?" * len(collection_ids))
        product_map = {}

        rows = conn.execute(
            f"""
            SELECT collection_id, product_id
            FROM portfolio_collection_product
            WHERE collection_id IN ({placeholders})
            """,
            collection_ids
        ).fetchall()

        for row in rows:
            cid = row["collection_id"]
            pid = row["product_id"]
            product_map.setdefault(cid, []).append(pid)

        # 4️⃣ Build final output
        result = []
        for c in collections:
            cid = c["id"]

            collection_dict = {key: c[key] for key in c.keys()}

            # add product ids
            collection_dict["product_ids"] = product_map.get(cid, [])

            result.append(collection_dict)

        return result





# from config import settings
# from es.es_client import get_es_context


# async def get_vendor_collections(handle: str):
#     """
#     Fetch all collections for a vendor from Elasticsearch
#     """
#     async with get_es_context() as es:
#         response = await es.search(
#             index=settings.COLLECTIONS_INDEX,
#             body={
#                 "query": {
#                     "bool": {
#                         "filter": [
#                             {"term": {"handle": handle}},
#                             {"term": {"is_active": True}},
#                         ]
#                     }
#                 },
#                 "size": 50,
#                 "sort": [{"order": "asc"}]
#             }
#         )

#     return [hit["_source"] for hit in response["hits"]["hits"]]

