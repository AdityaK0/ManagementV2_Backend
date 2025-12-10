

from services.sqlite_manager import sqlite_manager
from config import settings
import math
import json


# async def get_vendor_products(
#     business_name_slug: str,
#     page: int,
#     page_size: int,
#     search: str = "",
#     min_price: float | None = None,
#     max_price: float | None = None,
#     category: str | None = None,
# ):
#     offset = (page - 1) * page_size
    
#     async with sqlite_manager.get_db(business_name_slug) as conn:
#         # Build Query
#         conditions = ["p.is_active = 1"]
#         params = []
        
#         # Join Category if needed
#         join_clause = "LEFT JOIN category c ON p.category_id = c.id"
        
#         # 1. Price Filter
#         if min_price is not None:
#             conditions.append("p.price >= ?")
#             params.append(min_price)
#         if max_price is not None:
#             conditions.append("p.price <= ?")
#             params.append(max_price)
            
#         # 2. Category Filter
#         if category:
#             # Assumes 'category' arg is ID or Name? 
#             # Looking at original ES code: {"term": {"category": category}}
#             # Usually strict equality. Let's assume Category Name or ID. 
#             # Ideally we check if category is numeric. If string, match name.
#             conditions.append("c.name = ?")
#             params.append(category)

#         # 3. Search (FTS)
#         if search:
#             # Use FTS5 table
#             # "products_search" table has columns: name, description, sku, category_name
#             # JOIN back to product table
#             search_query = f"""
#                 SELECT rowid FROM products_search 
#                 WHERE products_search MATCH ? 
#                 ORDER BY rank
#             """
#             # Helper for robust search query formatting
#             fts_pattern = f'"{search}" OR {search}*' 
            
#             conditions.append(f"p.id IN ({search_query})")
#             params.append(fts_pattern)
            
#         where_clause = " WHERE " + " AND ".join(conditions)
        
#         # Count Query
#         count_sql = f"SELECT COUNT(*) FROM product p {join_clause} {where_clause}"
#         total_records = conn.execute(count_sql, params * 2 if search else params).fetchone()[0]
        
#         # Data Query
#         # Select p.* and potentially image or category name
#         sql = f"""
#             SELECT p.*, c.name as category_name 
#             FROM product p 
#             {join_clause}
#             {where_clause}
#             LIMIT ? OFFSET ?
#         """
        
#         # Add Limit/Offset params
#         query_params = (params * 2 if search else params) + [page_size, offset]
        
#         rows = conn.execute(sql, query_params).fetchall()
        
#         # Fetch Images efficiently?
#         # Or attach images in a second query or JSON_GROUP_ARRAY if supported
#         # For now, simplistic N+1 (since local SQLite is fast, but better to optimize)
#         # Let's use a single query approach if possible, but product images are separate.
#         # Let's do a quick enrichment.
        
#         product_ids = [r["id"] for r in rows]
#         images_map = {}
#         if product_ids:
#             placeholders = ",".join("?" * len(product_ids))
#             img_sql = f"SELECT * FROM product_image WHERE product_id IN ({placeholders})"
#             img_rows = conn.execute(img_sql, product_ids).fetchall()
#             for img in img_rows:
#                 pid = img["product_id"]
#                 if pid not in images_map:
#                     images_map[pid] = []
#                 images_map[pid].append(dict(img))

#         results = []
#         for r in rows:
#             prod_dict = dict(r)
#             # Reconstruct what ES gave us (often full structure)
#             prod_dict["images"] = images_map.get(r["id"], [])
            
#             # Dimensions/JSON fields
#             if prod_dict.get("dimensions"):
#                 try:
#                     prod_dict["dimensions"] = json.loads(prod_dict["dimensions"])
#                 except:
#                     pass
            
#             results.append(prod_dict)

#     total_pages = math.ceil(total_records / page_size)

#     return {
#         "results": results,
#         "count": total_records,
#         "total_pages": total_pages,
#         "current_page": page,
#         "has_next": page < total_pages,
#         "has_previous": page > 1,
#     }
from typing import Optional

async def get_vendor_products(
    business_name_slug: str,
    page: int,
    page_size: int,
    search: str = "",
    min_price: float | None = None,
    max_price: float | None = None,
    category: str | None = None,
):
    offset = (page - 1) * page_size

    async with sqlite_manager.get_db(business_name_slug) as conn:
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


async def get_vendor_product_detail(business_name_slug: str, product_id: int):
    async with sqlite_manager.get_db(business_name_slug) as conn:
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


        

# async def get_vendor_products(business_name_slug: str, page: int, page_size: int, search: str = ""):
#     from_ = (page - 1) * page_size

#     async with get_es_context() as es:
#         response = await es.search(
#             index=settings.PRODUCTS_INDEX,
#             body={
#                 "query": {
#                     "bool": {
#                         "filter": [
#                             {"term": {"business_name_slug": business_name_slug}},
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


