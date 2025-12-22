from services.sqlite_manager import sqlite_manager


async def get_vendor_collections(handle: str):

    async with sqlite_manager.get_db(handle) as conn:

        # 1) Get portfolio ID
        row = conn.execute("SELECT id FROM portfolio LIMIT 1").fetchone()
        if not row:
            return None

        pid = row["id"]

        # 2) Fetch collections
        collections = conn.execute(
            """
            SELECT *
            FROM portfolio_collection
            WHERE portfolio_id = ?
              AND is_active = 1
            ORDER BY "order" ASC, id ASC
            """,
            (pid,)
        ).fetchall()

        if not collections:
            return []

        coll_ids = [c["id"] for c in collections]
        placeholders = ",".join("?" * len(coll_ids))

        # 3) Fetch product mappings
        map_rows = conn.execute(
            f"""
            SELECT collection_id, product_id
            FROM portfolio_collection_product
            WHERE collection_id IN ({placeholders})
            """,
            coll_ids
        ).fetchall()

        product_map = {}
        for m in map_rows:
            product_map.setdefault(m["collection_id"], []).append(m["product_id"])

        # 4) Build final JSON
        final = []
        for c in collections:
            cd = dict(c)
            cd["product_ids"] = product_map.get(c["id"], [])
            final.append(cd)

        return final

async def get_vendor_collection_details(handle: str, collection_id: int):
    async with sqlite_manager.get_db(handle) as conn:
        # Fetch the collection
        collection = conn.execute(
            """
            SELECT *
            FROM portfolio_collection
            WHERE id = ?
              AND is_active = 1
            """,
            (collection_id,)
        ).fetchone()

        if not collection:
            return None

        # Fetch product mappings for this collection
        map_rows = conn.execute(
            """
            SELECT product_id
            FROM portfolio_collection_product
            WHERE collection_id = ?
            """,
            (collection_id,)
        ).fetchall()

        # Build the response with product_ids
        collection_dict = dict(collection)
        collection_dict["product_ids"] = [row["product_id"] for row in map_rows]

        return collection_dict