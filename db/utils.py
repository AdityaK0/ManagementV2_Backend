# utils.py
import json
from datetime import datetime
from psycopg2.extras import RealDictCursor


def json_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def safe_json(value):
    """
    Safely normalizes any JSON-like value into a Python list or dict.
    
    Cases handled:
    - string → json.loads
    - list/dict → returned as-is
    - None → None
    - invalid JSON string → returned as raw string or []
    """
    if value is None:
        return None

    # Already JSON types
    if isinstance(value, (list, dict)):
        return value

    # Try to decode JSON string
    if isinstance(value, str):
        value = value.strip()
        if value == "":
            return None
        try:
            return json.loads(value)
        except Exception:
            # Return raw string if not a JSON string
            return value

    # Unknown type → return as-is
    return value

def normalize_json(obj):
    """
    Recursively convert everything into JSON-safe types:
    - datetime → ISO string
    - dict → normalized dict
    - list → normalized list
    """
    if isinstance(obj, datetime):
        return obj.isoformat()

    if isinstance(obj, dict):
        return {k: normalize_json(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [normalize_json(v) for v in obj]

    return obj


def fetch_portfolio_full_json(self, vendor_slug: str):
    """
    Build DRF-like portfolio JSON, ready for SQLite.
    """
    with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:

        # 1) Vendor
        cursor.execute("""
            SELECT 
                id, business_name, handle, business_description,
                business_email, business_phone, whatsapp_number, google_maps_url, handle,
                business_role, business_categories, business_hours,business_started_year
            FROM vendors_vendor
            WHERE handle = %s
        """, (vendor_slug,))
        vendor = cursor.fetchone()
        if not vendor:
            return None

        vendor_id = vendor["id"]

        # 2) Portfolio
        cursor.execute("""
            SELECT *
            FROM portfolio_portfolio
            WHERE vendor_id = %s
        """, (vendor_id,))
        portfolio = cursor.fetchone()
        if not portfolio:
            return None

        portfolio_id = portfolio["id"]

        # 3) Featured products
        cursor.execute("""
            SELECT
                p.*, 
                c.name AS category_name
            FROM products_product p
            LEFT JOIN products_category c ON p.category_id = c.id
            INNER JOIN portfolio_portfolio_featured_products fp
                ON fp.product_id = p.id
            WHERE fp.portfolio_id = %s
            ORDER BY p.is_featured DESC, p.created_at DESC
            LIMIT 8
        """, (portfolio_id,))
        featured = cursor.fetchall()

        fp_final = []
        for p in featured:

            imgs = p["image_urls"] or []
            if isinstance(imgs, str):
                try:
                    imgs = json.loads(imgs)
                except:
                    imgs = [imgs]

            primary = p.get("primary_image")
            if primary:
                imgs = [primary] + [img for img in imgs if img != primary]

            fp_final.append({
                "id": p["id"],
                "name": p["name"],
                "description": p["description"],
                "price": str(p["price"]),
                "stock_quantity": p["stock_quantity"],
                "vendor_name": vendor["business_name"],
                "category_name": p["category_name"],
                "meta_title": p.get("meta_title") or "",
                "meta_description": p.get("meta_description") or "",
                "images": imgs,
                "sizes": safe_json(p["sizes"]),
                "is_in_stock": p["stock_quantity"] > 0,
                "is_featured": p["is_featured"],
                "created_at": p["created_at"],
                "is_active": p["is_active"],
                "gender": p["gender"]
            })

        # 4) Address
        cursor.execute("""
            SELECT *
            FROM users_address
            WHERE user_id = (SELECT user_id FROM vendors_vendor WHERE id = %s)
        """, (vendor_id,))
        addresses = cursor.fetchall()

        # 5) Build JSON
        response = {
            "id": portfolio_id,
            "business_name": vendor["business_name"],
            "display_name": portfolio["display_name"],
            "tagline": portfolio["tagline"],
            "slug": portfolio["slug"],
            "handle": portfolio["handle"],
            "about_us": portfolio["about_us"],
            "theme_color": portfolio["theme_color"],
            "accent_color": portfolio["accent_color"],
            "background_color": portfolio["background_color"],
            "font_family": portfolio["font_family"],
            "layout_style": portfolio["layout_style"],
            "show_pricing": portfolio["show_pricing"],
            "show_contact_form": portfolio["show_contact_form"],
            "show_stock_status": portfolio["show_stock_status"],
            "is_public": portfolio["is_public"],
            "view_count": portfolio["view_count"],
            "featured_products": fp_final,
            "banner_image": portfolio["banner_image"],
            "carousel_images": portfolio["carousel_images"] or [],
            "is_carousel": portfolio["is_carousel"],
            "logo": portfolio["logo"],
            "gallery_images": portfolio["gallery_images"] or [],
            "contact_email": vendor["business_email"],
            "contact_phone": vendor["business_phone"],
            "business_started_year": vendor["business_started_year"],
            "business_role": vendor["business_role"],
            "business_categories":vendor["business_categories"],
            "business_hours":vendor["business_hours"],
            "google_maps_url": vendor["google_maps_url"],
            "address": addresses,
            "whatsapp_number": vendor["whatsapp_number"],
            "social_links": {
                "facebook": portfolio["facebook_url"],
                "instagram": portfolio["instagram_url"],
                "twitter": portfolio["twitter_url"],
                "linkedin": portfolio["linkedin_url"],
                "youtube": portfolio["youtube_url"],
            },
            "created_at": portfolio["created_at"],
            "updated_at": portfolio["updated_at"]
        }

        safe_response = normalize_json(response)

        return {
            "portfolio_json": safe_response,
            "portfolio_row": {
                "id": portfolio_id,
                "response_json": json.dumps(safe_response)
            }
        }


