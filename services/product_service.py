import math
import json

from psycopg2.extensions import connection

def get_vendor_products(
    conn: connection,
    handle: str,
    page: int,
    page_size: int,
    search: str = "",
    min_price: float | None = None,
    max_price: float | None = None,
    category: str | None = None,
    version: str | None = None,
):
    offset = (page - 1) * page_size

    with conn.cursor() as cur:

        # 1️⃣ Resolve vendor_version_id
        if version:
            cur.execute("""
                SELECT vv.id
                FROM vendor_version vv
                JOIN vendor v ON v.id = vv.vendor_id
                WHERE v.handle = %s
                  AND vv.version = %s
                LIMIT 1
            """, (handle, version))
        else:
            cur.execute("""
                SELECT vv.id
                FROM vendor_version vv
                JOIN vendor v ON v.id = vv.vendor_id
                WHERE v.handle = %s
                ORDER BY
                    vv.is_active DESC,
                    vv.published_at DESC
                LIMIT 1
            """, (handle,))

        row = cur.fetchone()
        if not row:
            return None

        vendor_version_id = row[0]

        # 2️⃣ Build filters
        conditions = ["p.vendor_version_id = %s", "p.is_active = true"]
        params = [vendor_version_id]

        if min_price is not None:
            conditions.append("p.price >= %s")
            params.append(min_price)

        if max_price is not None:
            conditions.append("p.price <= %s")
            params.append(max_price)

        if category:
            conditions.append("p.category_name = %s")
            params.append(category)

        if search:
            conditions.append("""
                (
                    p.name ILIKE %s
                    OR p.slug ILIKE %s
                )
            """)
            params.extend([f"%{search}%", f"%{search}%"])

        where_sql = "WHERE " + " AND ".join(conditions)

        # 3️⃣ Count
        cur.execute(
            f"SELECT COUNT(*) FROM product p {where_sql}",
            params
        )
        total = cur.fetchone()[0]

        # 4️⃣ Fetch rows
        cur.execute(
            f"""
            SELECT p.*
            FROM product p
            {where_sql}
            ORDER BY p.created_at DESC
            LIMIT %s OFFSET %s
            """,
            params + [page_size, offset]
        )
        rows = cur.fetchall()

        # 5️⃣ Process rows
        results = []
        columns = [d[0] for d in cur.description]

        for r in rows:
            p = dict(zip(columns, r))

            # try:
            #     p["sizes"] = json.loads(p.get("sizes") or "[]")
            # except Exception:
            #     p["sizes"] = []

            results.append(p)

        return {
            "results": results,
            "count": total,
            "total_pages": math.ceil(total / page_size),
            "current_page": page,
            "has_next": page * page_size < total,
            "has_previous": page > 1,
        }


def get_vendor_product_detail(
    conn: connection,
    handle: str,
    product_id: int,
    version: str | None = None,
):
    with conn.cursor() as cur:

        # 1️⃣ Resolve vendor_version_id
        if version:
            cur.execute("""
                SELECT vv.id
                FROM vendor_version vv
                JOIN vendor v ON v.id = vv.vendor_id
                WHERE v.handle = %s
                  AND vv.version = %s
                LIMIT 1
            """, (handle, version))
        else:
            cur.execute("""
                SELECT vv.id
                FROM vendor_version vv
                JOIN vendor v ON v.id = vv.vendor_id
                WHERE v.handle = %s
                ORDER BY
                    vv.is_active DESC,
                    vv.published_at DESC
                LIMIT 1
            """, (handle,))

        row = cur.fetchone()
        if not row:
            return None

        vendor_version_id = row[0]

        # 2️⃣ Fetch product within that version
        cur.execute("""
            SELECT *
            FROM product
            WHERE source_id = %s
              AND vendor_version_id = %s
              AND is_active = true
        """, (product_id, vendor_version_id))

        row = cur.fetchone()
        if not row:
            return None

        # 3️⃣ Normalize JSON fields
        product = dict(zip([d[0] for d in cur.description], row))


        try:
            product["dimensions"] = json.loads(product.get("dimensions") or "{}")
        except Exception:
            product["dimensions"] = None

        return product


from psycopg2.extensions import connection


def get_vendor_product_categories(
    conn: connection,
    handle: str,
    version: str | None = None,
):
    with conn.cursor() as cur:

        # 1️⃣ Resolve vendor_version_id
        if version:
            cur.execute("""
                SELECT vv.id
                FROM vendor_version vv
                JOIN vendor v ON v.id = vv.vendor_id
                WHERE v.handle = %s
                  AND vv.version = %s
                LIMIT 1
            """, (handle, version))
        else:
            cur.execute("""
                SELECT vv.id
                FROM vendor_version vv
                JOIN vendor v ON v.id = vv.vendor_id
                WHERE v.handle = %s
                ORDER BY
                    vv.is_active DESC,
                    vv.published_at DESC
                LIMIT 1
            """, (handle,))

        row = cur.fetchone()
        if not row:
            return []

        vendor_version_id = row[0]

        # 2️⃣ Fetch categories
        cur.execute("""
            SELECT DISTINCT name
            FROM category
            WHERE vendor_version_id = %s
            ORDER BY name ASC
        """, (vendor_version_id,))

        rows = cur.fetchall()
        return [r[0] for r in rows]

# import math
# import json
# from typing import Optional
# from .sqlite_manager import sqlite_manager


# async def get_vendor_products(
#     handle: str,
#     page: int,
#     page_size: int,
#     search: str = "",
#     min_price: float | None = None,
#     max_price: float | None = None,
#     category: str | None = None,
# ):
#     offset = (page - 1) * page_size

#     async with sqlite_manager.get_db(handle) as conn:

#         conditions = ["p.is_active = 1", "p.is_archived = 0"]
#         params = []

#         #  PRICE FILTERS
#         if min_price is not None:
#             conditions.append("p.price >= ?")
#             params.append(min_price)
#         if max_price is not None:
#             conditions.append("p.price <= ?")
#             params.append(max_price)

#         #  CATEGORY FILTER
#         if category:
#             conditions.append("p.category_name = ?")
#             params.append(category)

#         #  SEARCH via FTS5
#         if search:
#             # fts = """
#             #     SELECT rowid FROM products_search 
#             #     WHERE products_search MATCH ?
#             # """
#             # match = f'"{search}" OR {search}*'
#             # conditions.append(f"p.id IN ({fts})")
#             # params.append(match)
#             # SEARCH via FTS5
#             fts = """
#                 SELECT id FROM products_search
#                 WHERE products_search MATCH ?
#             """
#             match = f"{search}*"
#             conditions.append(f"p.id IN ({fts})")
#             params.append(match)

#         where_sql = "WHERE " + " AND ".join(conditions)

#         # Count
#         total = conn.execute(
#             f"SELECT COUNT(*) FROM product p {where_sql}",
#             params
#         ).fetchone()[0]

#         # Query
#         rows = conn.execute(
#             f"""
#             SELECT p.*
#             FROM product p
#             {where_sql}
#             ORDER BY p.created_at DESC
#             LIMIT ? OFFSET ?
#             """,
#             params + [page_size, offset]
#         ).fetchall()

#         results = []
#         for r in rows:
#             p = dict(r)

#             # Parse JSON fields
#             try:
#                 p["images"] = json.loads(p["images_processed"]) if p["images_processed"] else []
#             except:
#                 p["images"] = []

#             try:
#                 p["sizes"] = json.loads(p["sizes"]) if p["sizes"] else []
#             except:
#                 p["sizes"] = []

#             try:
#                 p["dimensions"] = json.loads(p["dimensions"]) if p["dimensions"] else None
#             except:
#                 p["dimensions"] = None

#             results.append(p)

#     return {
#         "results": results,
#         "count": total,
#         "total_pages": math.ceil(total / page_size),
#         "current_page": page,
#         "has_next": page * page_size < total,
#         "has_previous": page > 1,
#     }




# async def get_vendor_product_detail(handle: str, product_id: int):
#     async with sqlite_manager.get_db(handle) as conn:

#         row = conn.execute(
#             """
#             SELECT *
#             FROM product
#             WHERE id = ?
#               AND is_active = 1
#               AND is_archived = 0
#             """,
#             (product_id,)
#         ).fetchone()

#         if not row:
#             return None

#         p = dict(row)

#         # JSON fields
#         try:
#             p["images"] = json.loads(p["images_processed"]) if p["images_processed"] else []
#         except:
#             p["images"] = []

#         try:
#             p["sizes"] = json.loads(p["sizes"]) if p["sizes"] else []
#         except:
#             p["sizes"] = []

#         try:
#             p["dimensions"] = json.loads(p["dimensions"]) if p["dimensions"] else None
#         except:
#             p["dimensions"] = None

#         return p

# async def get_vendor_product_categories(handle: str):
#     async with sqlite_manager.get_db(handle) as conn:
#         rows = conn.execute(
#             """
#             SELECT DISTINCT name
#             FROM category
#             WHERE is_active = 1
#             ORDER BY created_at ASC
#             """
#         ).fetchall()
        
#         return [r["name"] for r in rows]