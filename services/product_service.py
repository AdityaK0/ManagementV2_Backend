

from services.sqlite_manager import sqlite_manager
from config import settings
import math
import json

from typing import Optional

async def get_vendor_products(
    handle: str,
    page: int,
    page_size: int,
    search: str = "",
    min_price: float | None = None,
    max_price: float | None = None,
    category: str | None = None,
):
    offset = (page - 1) * page_size

    async with sqlite_manager.get_db(handle) as conn:
        conditions = ["p.is_active = 1", "p.is_archived = 0"]
        params = []

        # 1️⃣ PRICE FILTERS
        if min_price is not None:
            conditions.append("p.price >= ?")
            params.append(min_price)
        if max_price is not None:
            conditions.append("p.price <= ?")
            params.append(max_price)

        # 2️⃣ CATEGORY FILTER
        if category:
            conditions.append("p.category_name = ?")
            params.append(category)

        # 3️⃣ SEARCH via FTS5
        if search:
            fts_sql = """
                SELECT rowid FROM products_search 
                WHERE products_search MATCH ?
            """
            match_query = f'"{search}" OR {search}*'
            conditions.append(f"p.id IN ({fts_sql})")
            params.append(match_query)

        where_sql = "WHERE " + " AND ".join(conditions)

        # 4️⃣ COUNT QUERY
        count_sql = f"""
            SELECT COUNT(*)
            FROM product p
            {where_sql}
        """
        total_records = conn.execute(count_sql, params).fetchone()[0]

        # 5️⃣ DATA QUERY
        sql = f"""
            SELECT p.*
            FROM product p
            {where_sql}
            ORDER BY p.created_at DESC
            LIMIT ? OFFSET ?
        """
        rows = conn.execute(sql, params + [page_size, offset]).fetchall()

        # 6️⃣ ENRICH EACH PRODUCT
        results = []
        for r in rows:
            p = dict(r)

            # parse JSON fields safely
            try:
                p["images"] = json.loads(p["images_processed"]) if p["images_processed"] else []
            except:
                p["images"] = []

            try:
                p["sizes"] = json.loads(p["sizes"]) if p["sizes"] else []
            except:
                pass

            try:
                p["dimensions"] = json.loads(p["dimensions"]) if p["dimensions"] else None
            except:
                pass

            results.append(p)

    total_pages = math.ceil(total_records / page_size)

    return {
        "results": results,
        "count": total_records,
        "total_pages": total_pages,
        "current_page": page,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


async def get_vendor_product_detail(handle: str, product_id: int):
    async with sqlite_manager.get_db(handle) as conn:
        row = conn.execute(
            "SELECT * FROM product WHERE id = ? AND is_active = 1 AND is_archived = 0",
            (product_id,)
        ).fetchone()

        if not row:
            return None

        p = dict(row)

        # Parse JSON
        try:
            p["images"] = json.loads(p["images_processed"]) if p["images_processed"] else []
        except:
            p["images"] = []

        try:
            p["sizes"] = json.loads(p["sizes"]) if p["sizes"] else []
        except:
            pass

        try:
            p["dimensions"] = json.loads(p["dimensions"]) if p["dimensions"] else None
        except:
            pass

        return p


        

# async def get_vendor_products(handle: str, page: int, page_size: int, search: str = ""):
#     from_ = (page - 1) * page_size

#     async with get_es_context() as es:
#         response = await es.search(
#             index=settings.PRODUCTS_INDEX,
#             body={
#                 "query": {
#                     "bool": {
#                         "filter": [
#                             {"term": {"handle": handle}},
#                             # {"term": {"is_active": True}}
#                         ],
#                         "must": (
#                             [
#                                 {
#                                     "bool": {
#                                         "should": [
#                                             {"wildcard": {"name": f"*{search.lower()}*"}},
#                                             {"wildcard": {"description": f"*{search.lower()}*"}},
#                                             {"wildcard": {"sku": f"*{search.lower()}*"}},
#                                         ]
#                                     }
#                                 }
#                             ]
#                             if search
#                             else [{"match_all": {}}]
#                         ),
#                     }
#                 },
#                 "from": from_,
#                 "size": page_size,
#             },
#         )

#     hits = response["hits"]["hits"]
#     products = [hit["_source"] for hit in hits]

#     total_records = response["hits"]["total"]["value"]
#     total_pages = math.ceil(total_records / page_size)

#     return {
#         "results": products,
#         "count": total_records,
#         "total_pages": total_pages,
#         "current_page": page,
#         "has_next": page < total_pages,
#         "has_previous": page > 1,
#     }


