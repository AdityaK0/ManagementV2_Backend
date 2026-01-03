# import logging
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)

# def cleanup_old_versions(conn, active_version_id: int):
#     """
#     Deletes ALL old versioned data for the vendor
#     owning `active_version_id`, keeping ONLY that version.
#     """

#     with conn.cursor() as cur:

#         # 0️⃣ Resolve vendor_id safely
#         cur.execute("""
#             SELECT vendor_id
#             FROM vendor_version
#             WHERE id = %s
#         """, (active_version_id,))
#         row = cur.fetchone()

#         if not row:
#             logger.warning(
#                 f"No vendor_version found for id={active_version_id}, skipping cleanup"
#             )
#             return

#         vendor_id = row[0]

#         # 1️⃣ Collection ↔ Product mappings
#         cur.execute("""
#             DELETE FROM portfolio_collection_product
#             WHERE collection_id IN (
#                 SELECT id
#                 FROM portfolio_collection
#                 WHERE vendor_id = %s
#                   AND vendor_version_id <> %s
#             )
#         """, (vendor_id, active_version_id))
#         logger.info(f"Deleted {cur.rowcount} collection-product mappings")

#         # 2️⃣ Products
#         cur.execute("""
#             DELETE FROM product
#             WHERE vendor_id = %s
#               AND vendor_version_id <> %s
#         """, (vendor_id, active_version_id))
#         logger.info(f"Deleted {cur.rowcount} products")

#         # 3️⃣ Categories
#         cur.execute("""
#             DELETE FROM category
#             WHERE vendor_id = %s
#               AND vendor_version_id <> %s
#         """, (vendor_id, active_version_id))
#         logger.info(f"Deleted {cur.rowcount} categories")

#         # 4️⃣ Collections
#         cur.execute("""
#             DELETE FROM portfolio_collection
#             WHERE vendor_id = %s
#               AND vendor_version_id <> %s
#         """, (vendor_id, active_version_id))
#         logger.info(f"Deleted {cur.rowcount} collections")

#         # 5️⃣ Portfolio snapshots
#         cur.execute("""
#             DELETE FROM portfolio
#             WHERE vendor_id = %s
#               AND vendor_version_id <> %s
#         """, (vendor_id, active_version_id))
#         logger.info(f"Deleted {cur.rowcount} portfolios")

#         # 6️⃣ Old vendor_version rows
#         cur.execute("""
#             DELETE FROM vendor_version
#             WHERE vendor_id = %s
#               AND id <> %s
#         """, (vendor_id, active_version_id))
#         logger.info(f"Deleted {cur.rowcount} vendor versions")


def cleanup_old_versions(conn, active_version_id: int):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM vendor_version
            WHERE vendor_id = (
                SELECT vendor_id
                FROM vendor_version
                WHERE id = %s
            )
            AND id <> %s
        """, (active_version_id, active_version_id))
