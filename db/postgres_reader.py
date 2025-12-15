# postgres_reader.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from utils import fetch_portfolio_full_json


class PostgresReader:
    def __init__(self, host=None, database=None, user=None, password=None, port=None):
        self.conn = psycopg2.connect(
            host=host or os.environ.get("POSTGRES_HOST"),
            database=database or os.environ.get("POSTGRES_DB"),
            user=user or os.environ.get("POSTGRES_USER"),
            password=password or os.environ.get("POSTGRES_PASSWORD"),
            port=port or os.environ.get("POSTGRES_PORT", 5432),
        )

    def close(self):
        if self.conn:
            self.conn.close()

    def fetch_vendor_data(self, vendor_slug: str):
        data = {}

        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:

            # Vendor
            cursor.execute("SELECT * FROM vendors_vendor WHERE handle=%s", (vendor_slug,))
            vendor = cursor.fetchone()
            if not vendor:
                return None

            vendor_id = vendor["id"]
            data["vendor"] = [vendor]

            # Portfolio JSON (NEW)
            portfolio_complete = fetch_portfolio_full_json(self, vendor_slug)

            if portfolio_complete:
                data["portfolio"] = [portfolio_complete["portfolio_row"]]
            else:
                data["portfolio"] = []

            # Portfolio collections
            cursor.execute("SELECT * FROM portfolio_portfoliocollection WHERE portfolio_id=%s",
                           (portfolio_complete["portfolio_row"]["id"],))
            collections = cursor.fetchall()
            data["portfolio_collection"] = collections

            # Collection → product mapping
            if collections:
                ids = tuple([c["id"] for c in collections])
                sql_tuple = str(ids) if len(ids) > 1 else f"({ids[0]})"
                cursor.execute(f"""
                    SELECT portfoliocollection_id AS collection_id, product_id
                    FROM portfolio_portfoliocollection_products
                    WHERE portfoliocollection_id IN {sql_tuple}
                """)
                data["portfolio_collection_product"] = cursor.fetchall()
            else:
                data["portfolio_collection_product"] = []

            # Categories
            cursor.execute("SELECT * FROM products_category WHERE vendor_id=%s", (vendor_id,))
            categories = cursor.fetchall()
            data["category"] = categories

            data["category_map"] = {c["id"]: c["name"] for c in categories}

            # Products
            cursor.execute("SELECT * FROM products_product WHERE vendor_id=%s", (vendor_id,))
            data["product"] = cursor.fetchall()

        return data