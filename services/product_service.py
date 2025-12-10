import math
import json
from typing import Optional
from .sqlite_manager import sqlite_manager


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

        #  PRICE FILTERS
        if min_price is not None:
            conditions.append("p.price >= ?")
            params.append(min_price)
        if max_price is not None:
            conditions.append("p.price <= ?")
            params.append(max_price)

        #  CATEGORY FILTER
        if category:
            conditions.append("p.category_name = ?")
            params.append(category)

        #  SEARCH via FTS5
        if search:
            fts = """
                SELECT rowid FROM products_search 
                WHERE products_search MATCH ?
            """
            match = f'"{search}" OR {search}*'
            conditions.append(f"p.id IN ({fts})")
            params.append(match)

        where_sql = "WHERE " + " AND ".join(conditions)

        # Count
        total = conn.execute(
            f"SELECT COUNT(*) FROM product p {where_sql}",
            params
        ).fetchone()[0]

        # Query
        rows = conn.execute(
            f"""
            SELECT p.*
            FROM product p
            {where_sql}
            ORDER BY p.created_at DESC
            LIMIT ? OFFSET ?
            """,
            params + [page_size, offset]
        ).fetchall()

        results = []
        for r in rows:
            p = dict(r)

            # Parse JSON fields
            try:
                p["images"] = json.loads(p["images_processed"]) if p["images_processed"] else []
            except:
                p["images"] = []

            try:
                p["sizes"] = json.loads(p["sizes"]) if p["sizes"] else []
            except:
                p["sizes"] = []

            try:
                p["dimensions"] = json.loads(p["dimensions"]) if p["dimensions"] else None
            except:
                p["dimensions"] = None

            results.append(p)

    return {
        "results": results,
        "count": total,
        "total_pages": math.ceil(total / page_size),
        "current_page": page,
        "has_next": page * page_size < total,
        "has_previous": page > 1,
    }




async def get_vendor_product_detail(handle: str, product_id: int):
    async with sqlite_manager.get_db(handle) as conn:

        row = conn.execute(
            """
            SELECT *
            FROM product
            WHERE id = ?
              AND is_active = 1
              AND is_archived = 0
            """,
            (product_id,)
        ).fetchone()

        if not row:
            return None

        p = dict(row)

        # JSON fields
        try:
            p["images"] = json.loads(p["images_processed"]) if p["images_processed"] else []
        except:
            p["images"] = []

        try:
            p["sizes"] = json.loads(p["sizes"]) if p["sizes"] else []
        except:
            p["sizes"] = []

        try:
            p["dimensions"] = json.loads(p["dimensions"]) if p["dimensions"] else None
        except:
            p["dimensions"] = None

        return p

