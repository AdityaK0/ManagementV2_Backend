import os
import psycopg2
from psycopg2.extras import RealDictCursor
from .utils import fetch_portfolio_full_json, safe_json
from config import settings

class PostgresReader:
    def __init__(self):
        print(f"pg data : {settings.POSTGRES_HOST} {settings.POSTGRES_DB} {settings.POSTGRES_USER} {settings.POSTGRES_PASSWORD} {settings.POSTGRES_PORT}")
        self.conn = psycopg2.connect(
            host=settings.POSTGRES_HOST,
            database=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            port=settings.POSTGRES_PORT,
        )
        print(self.conn,"coonennn")

    def close(self):
        self.conn.close()

    def fetch_vendor_data(self, vendor_slug: str):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:

            cursor.execute("""
                SELECT id, handle, business_name
                FROM vendors_vendor
                WHERE handle = %s
            """, (vendor_slug,))
            vendor = cursor.fetchone()
            if not vendor:
                return None

            vendor_id = vendor["id"]

            portfolio = fetch_portfolio_full_json(self, vendor_slug)

            cursor.execute("""
                SELECT id, name, description, created_at
                FROM products_category
                WHERE vendor_id = %s
                ORDER BY created_at
            """, (vendor_id,))
            categories = cursor.fetchall()

            category_name_map = {c["id"]: c["name"] for c in categories}

            cursor.execute("""
                SELECT *
                FROM products_product
                WHERE vendor_id = %s AND is_active = true AND is_archived = false
            """, (vendor_id,))
            products_raw = cursor.fetchall()

            products = [{
                "source_id": p["id"],
                "uid": f"{vendor_id}:{p['id']}",
                "name": p["name"],
                # "slug": p["slug"],
                "category_name": category_name_map.get(p["category_id"]),
                "price": p["price"],
                "sku": p["sku"],
                "stock_quantity": p["stock_quantity"] or 0,
                "primary_image": p["primary_image"],
                "image_urls": safe_json(p["image_urls"]) or [],
                "sizes": safe_json(p["sizes"]),
                "is_active": p["is_active"],
                "is_featured": p["is_featured"],
                "meta_title": p["meta_title"],
                "meta_description": p["meta_description"],
            } for p in products_raw]

            cursor.execute("""
                SELECT pc.*
                FROM portfolio_portfoliocollection pc
                JOIN portfolio_portfolio p ON p.id = pc.portfolio_id
                WHERE p.vendor_id = %s
                ORDER BY pc.order
            """, (vendor_id,))
            collections_raw = cursor.fetchall()

            collections = []
            for c in collections_raw:
                cursor.execute("""
                    SELECT product_id
                    FROM portfolio_portfoliocollection_products
                    WHERE portfoliocollection_id = %s
                """, (c["id"],))
                product_ids = [r["product_id"] for r in cursor.fetchall()]

                collections.append({
                    "source_id": c["id"],
                    "name": c["name"],
                    "slug": c["slug"],
                    "description": c["description"],
                    "cover_image": c["cover_image"],
                    "sort_order": c["order"] or 0,
                    "is_featured": c["is_featured"],
                    "product_source_ids": product_ids
                })

            return {
                "vendor": vendor,
                "portfolio": portfolio["portfolio_json"],
                "categories": categories,
                "products": products,
                "collections": collections
            }
