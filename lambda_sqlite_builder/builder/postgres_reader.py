# postgres_reader.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from .utils import fetch_portfolio_full_json


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


# import os
# import psycopg2
# from psycopg2.extras import RealDictCursor
# import json
# from datetime import datetime

# class PostgresReader:
#     def __init__(self, host=None, database=None, user=None, password=None, port=None):
#         self.conn = psycopg2.connect(
#             host=host or os.environ.get("POSTGRES_HOST"),
#             database=database or os.environ.get("POSTGRES_DB"),
#             user=user or os.environ.get("POSTGRES_USER"),
#             password=password or os.environ.get("POSTGRES_PASSWORD"),
#             port=port or os.environ.get("POSTGRES_PORT", 5432)
#         )
#         # Debugging print (optional, can be removed in prod)
#         # print("Pg Config: ", [host, database, user, "******", port])
    
#     def close(self):
#         if self.conn:
#             self.conn.close()

#     def fetch_vendor_data(self, vendor_slug: str):
#         """
#         Fetches all relevant data for a specific vendor.
#         Returns a dictionary keyed by table name with list of dict rows.
#         """
#         data = {}
#         with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
#             # 1. Vendor
#             cursor.execute("""
#                 SELECT 
#                     v.id, v.user_id, v.business_name, v.business_name_slug, v.business_description,
#                     v.business_email, v.business_type, v.business_phone, v.whatsapp_number, 
#                     v.gstin, v.website, v.telegram_chat_id, v.logo, v.is_onboarded, 
#                     v.is_active, v.is_verified, v.secret, v.secret_expires_at, 
#                     v.geolocation, v.handle, v.created_at, v.updated_at
#                 FROM vendors_vendor v
#                 WHERE v.handle = %s
#             """, (vendor_slug,))
#             vendor = cursor.fetchone()
            
#             if not vendor:
#                 return None
            
#             vendor_id = vendor['id']
#             data['vendor'] = [vendor]

#             # 2. Portfolio
#             cursor.execute("""
#                 SELECT 
#                     id, vendor_id, display_name, tagline, slug, business_name_slug, 
#                     about_us, our_story, mission, vision, logo, banner_image, 
#                     gallery_images, carousel_images, title, theme_color, accent_color, 
#                     background_color, text_color, font_family, layout_style, 
#                     portfolio_url, facebook_url, instagram_url, twitter_url, linkedin_url, 
#                     youtube_url, website_url, show_pricing, show_stock_status, 
#                     show_contact_form, show_social_links, show_testimonials, show_gallery, 
#                     is_public, is_featured, is_carousel, want_to_show_on_platform, 
#                     custom_domain, custom_css, meta_title, meta_description, meta_keywords, 
#                     view_count, last_viewed, created_at, updated_at
#                 FROM portfolio_portfolio
#                 WHERE vendor_id = %s
#             """, (vendor_id,))
#             portfolio = cursor.fetchone()
#             if portfolio:
#                 data['portfolio'] = [portfolio]
#                 portfolio_id = portfolio['id']
                
#                 # Portfolio Collections
#                 cursor.execute("""
#                     SELECT 
#                         id, portfolio_id, name, description, cover_image, is_featured, 
#                         is_active, "order", slug, created_at, updated_at 
#                     FROM portfolio_portfoliocollection WHERE portfolio_id = %s
#                 """, (portfolio_id,))
#                 collections = cursor.fetchall()
#                 data['portfolio_collection'] = collections

#                 # Collection Products
#                 collection_ids = tuple([c['id'] for c in collections])
#                 if collection_ids:
#                     # Handle single item tuple syntax for SQL
#                     c_ids_sql = str(collection_ids) if len(collection_ids) > 1 else f"({collection_ids[0]})"
#                     cursor.execute(f"""
#                         SELECT portfoliocollection_id as collection_id, product_id 
#                         FROM portfolio_portfoliocollection_products 
#                         WHERE portfoliocollection_id IN {c_ids_sql}
#                     """)
#                     data['portfolio_collection_product'] = cursor.fetchall()
#                 else:
#                     data['portfolio_collection_product'] = []

#             else:
#                 data['portfolio'] = []
#                 data['portfolio_collection'] = []
#                 data['portfolio_collection_product'] = []

#             # 3. Categories
#             cursor.execute("""
#                 SELECT id, vendor_id, name, description, parent_id, is_active, is_default, created_at 
#                 FROM products_category WHERE vendor_id = %s
#             """, (vendor_id,))
#             data['category'] = cursor.fetchall()

#             # 4. Products
#             cursor.execute("""
#                 SELECT 
#                     id, vendor_id, category_id, name, description, price, cost_price, 
#                     stock_quantity, min_stock_level, sku, gender, sizes, dimensions, 
#                     image_urls, primary_image, is_active, is_featured, is_archived, 
#                     meta_title, meta_description, created_at, updated_at 
#                 FROM products_product WHERE vendor_id = %s
#             """, (vendor_id,))
#             products = cursor.fetchall()
#             data['product'] = products
#         # Create category map for fast lookup
#         data["category_map"] = {c["id"]: c["name"] for c in data["category"]}
    
#         return data

#     @staticmethod
#     def json_serializer(obj):
#         if isinstance(obj, datetime):
#             return obj.isoformat()
#         raise TypeError(f"Type {type(obj)} not serializable")
