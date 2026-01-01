from psycopg2.extensions import connection

def get_vendor_collections(
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
            return None  # vendor not found

        vendor_version_id = row[0]

        # 2️⃣ Fetch collections
        cur.execute("""
            SELECT id, name, slug, description, cover_image,
                   sort_order, is_featured
            FROM portfolio_collection
            WHERE vendor_version_id = %s
            ORDER BY sort_order ASC, id ASC
        """, (vendor_version_id,))

        collections = cur.fetchall()
        if not collections:
            return []

        collection_ids = [c[0] for c in collections]

        # 3️⃣ Fetch product mappings
        cur.execute("""
            SELECT collection_id, product_id
            FROM portfolio_collection_product
            WHERE collection_id = ANY(%s)
            ORDER BY sort_order ASC
        """, (collection_ids,))

        map_rows = cur.fetchall()

        # 4️⃣ Build response
        product_map = {}
        for cid, pid in map_rows:
            product_map.setdefault(cid, []).append(pid)

        result = []
        for c in collections:
            (
                cid,
                name,
                slug,
                description,
                cover_image,
                sort_order,
                is_featured,
            ) = c

            result.append({
                "id": cid,
                "name": name,
                "slug": slug,
                "description": description,
                "cover_image": cover_image,
                "sort_order": sort_order,
                "is_featured": is_featured,
                "product_ids": product_map.get(cid, []),
            })

        return result


from psycopg2.extensions import connection


def get_vendor_collection_details(
    conn: connection,
    handle: str,
    collection_id: int,
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
            return None  # vendor not found

        vendor_version_id = row[0]

        # 2️⃣ Fetch collection
        cur.execute("""
            SELECT *
            FROM portfolio_collection
            WHERE id = %s
              AND vendor_version_id = %s
            LIMIT 1
        """, (collection_id, vendor_version_id))

        collection = cur.fetchone()
        if not collection:
            return None

        col_columns = [d[0] for d in cur.description]
        collection_dict = dict(zip(col_columns, collection))

        # 3️⃣ Fetch product mappings
        cur.execute("""
            SELECT product_id
            FROM portfolio_collection_product
            WHERE collection_id = %s
            ORDER BY sort_order ASC
        """, (collection_id,))

        product_ids = [r[0] for r in cur.fetchall()]
        collection_dict["product_ids"] = product_ids

        return collection_dict


# from services.sqlite_manager import sqlite_manager


# async def get_vendor_collections(handle: str):

#     async with sqlite_manager.get_db(handle) as conn:

#         # 1) Get portfolio ID
#         row = conn.execute("SELECT id FROM portfolio LIMIT 1").fetchone()
#         if not row:
#             return None

#         pid = row["id"]

#         # 2) Fetch collections
#         collections = conn.execute(
#             """
#             SELECT *
#             FROM portfolio_collection
#             WHERE portfolio_id = ?
#               AND is_active = 1
#             ORDER BY "order" ASC, id ASC
#             """,
#             (pid,)
#         ).fetchall()

#         if not collections:
#             return []

#         coll_ids = [c["id"] for c in collections]
#         placeholders = ",".join("?" * len(coll_ids))

#         # 3) Fetch product mappings
#         map_rows = conn.execute(
#             f"""
#             SELECT collection_id, product_id
#             FROM portfolio_collection_product
#             WHERE collection_id IN ({placeholders})
#             """,
#             coll_ids
#         ).fetchall()

#         product_map = {}
#         for m in map_rows:
#             product_map.setdefault(m["collection_id"], []).append(m["product_id"])

#         # 4) Build final JSON
#         final = []
#         for c in collections:
#             cd = dict(c)
#             cd["product_ids"] = product_map.get(c["id"], [])
#             final.append(cd)

#         return final

# async def get_vendor_collection_details(handle: str, collection_id: int):
#     async with sqlite_manager.get_db(handle) as conn:
#         # Fetch the collection
#         collection = conn.execute(
#             """
#             SELECT *
#             FROM portfolio_collection
#             WHERE id = ?
#               AND is_active = 1
#             """,
#             (collection_id,)
#         ).fetchone()

#         if not collection:
#             return None

#         # Fetch product mappings for this collection
#         map_rows = conn.execute(
#             """
#             SELECT product_id
#             FROM portfolio_collection_product
#             WHERE collection_id = ?
#             """,
#             (collection_id,)
#         ).fetchall()

#         # Build the response with product_ids
#         collection_dict = dict(collection)
#         collection_dict["product_ids"] = [row["product_id"] for row in map_rows]

#         return collection_dict