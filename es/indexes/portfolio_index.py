
# from elasticsearch import Elasticsearch

# es = Elasticsearch("http://localhost:9205")

# INDEX_NAME = "portfolio_index"

# mapping = {'mappings': {'properties': {'vendor': {'type': 'keyword'}, 'display_name': {'type': 'keyword'}, 'tagline': {'type': 'keyword'}, 'slug': {'type': 'keyword'}, 'about_us': {'type': 'text'}, 'our_story': {'type': 'text'}, 'mission': {'type': 'text'}, 'vision': {'type': 'text'}, 'gallery_images': {'type': 'object'}, 'title': {'type': 'keyword'}, 'featured_products': {'type': 'keyword'}, 'theme_color': {'type': 'keyword'}, 'accent_color': {'type': 'keyword'}, 'background_color': {'type': 'keyword'}, 'text_color': {'type': 'keyword'}, 'font_family': {'type': 'keyword'}}}, 'settings': {'number_of_shards': 1, 'number_of_replicas': 0}}

# def create_index():
#     if es.indices.exists(index=INDEX_NAME):
    
#         print(f"Index '{INDEX_NAME}' already exists. Skipping...")
#     else:
#         es.indices.create(index=INDEX_NAME, body=mapping)
#         print(f"Created index: {INDEX_NAME}")

from elasticsearch import Elasticsearch
from es.es_sync_client import get_es_sync_client
es = get_es_sync_client()
INDEX_NAME = "portfolio_index"

def create_index():

    if es.indices.exists(index=INDEX_NAME):
        print(f"✅ Index already exists: {INDEX_NAME}")
        return

    mapping = {
        "mappings": {
            "properties": {
                "id": {"type": "integer"},
                "business_name": {"type": "keyword"},
                "display_name": {"type": "keyword"},
                "tagline": {"type": "text"},
                "slug": {"type": "keyword"},
                "business_name_slug": { "type": "keyword" },

                "about_us": {"type": "text"},
                "theme_color": {"type": "keyword"},
                "accent_color": {"type": "keyword"},
                "background_color": {"type": "keyword"},
                "font_family":{"type": "keyword"},
                "text_color": {"type": "keyword"},
                "layout_style": {"type": "keyword"},
                "show_pricing": {"type": "boolean"},
                "show_contact_form": {"type": "boolean"},
                "is_public": {"type": "boolean"},
                "is_carousel": {"type": "boolean"},
                "show_stock_status": {"type": "boolean"},
                

                "view_count": {"type": "integer"},
                "total_collections": {"type": "integer"},
                "total_testimonials": {"type": "integer"},

                "banner_image": {"type": "keyword"},
                "logo": {"type": "keyword"},
                "gallery_images": {"type": "keyword"},
                "carousel_images": {"type": "keyword"},
                "contact_email": {"type": "keyword"},
                "contact_phone": {"type": "keyword"},
                "whatsapp_number": {"type": "keyword"},

                "featured_products": {
                    "type": "nested",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "keyword"},
                        "price": {"type": "keyword"},
                        "stock_quantity": {"type": "integer"},
                        "vendor_name": {"type": "keyword"},
                        "description": {"type": "text"},
                        "meta_title": {"type": "keyword"},
                        "meta_description": {"type": "text"},
                        "images": {"type": "keyword"},
                        "is_in_stock": {"type": "boolean"},
                        "is_featured": {"type": "boolean"},
                        "created_at": {"type": "date"},
                        "is_active": {"type": "boolean"},
                    }
                },

                "address": {
                    "type": "nested",
                    "properties": {
                        "street_address": {"type": "text"},
                        "city": {"type": "keyword"},
                        "state": {"type": "keyword"},
                        "postal_code": {"type": "keyword"},
                        "country": {"type": "keyword"},
                        "zip_code": {"type": "keyword"},
                        "is_default": {"type": "boolean"},
                    }
                },

                "social_links": {
                    "type": "object",
                    "properties": {
                        "facebook": {"type": "keyword"},
                        "instagram": {"type": "keyword"},
                        "twitter": {"type": "keyword"},
                        "linkedin": {"type": "keyword"},
                        "youtube": {"type": "keyword"},
                    }
                },

                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
            }
        }
    }

    es.indices.create(index=INDEX_NAME, body=mapping)
    print(f"✅ Created index: {INDEX_NAME}")

        

def delete_index():
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
        print(f" Deleted index: {INDEX_NAME}")
    else:
        print(f"Index does not exist: {INDEX_NAME}")   
        
        


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "delete":
        delete_index()
    else:
        create_index()             
