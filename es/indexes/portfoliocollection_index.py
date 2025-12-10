
# from elasticsearch import Elasticsearch

# es = Elasticsearch("http://localhost:9205")

# INDEX_NAME = "portfoliocollection_index"

# mapping = {'mappings': {'properties': {'portfolio': {'type': 'keyword'}, 'name': {'type': 'keyword'}, 'description': {'type': 'text'}, 'products': {'type': 'keyword'}, 'is_featured': {'type': 'boolean'}, 'is_active': {'type': 'boolean'}, 'order': {'type': 'integer'}, 'slug': {'type': 'keyword'}, 'created_at': {'type': 'date'}, 'updated_at': {'type': 'date'}}}, 'settings': {'number_of_shards': 1, 'number_of_replicas': 0}}

# def create_index():
#     if es.indices.exists(index=INDEX_NAME):
    
#         print(f"Index '{INDEX_NAME}' already exists. Skipping...")
#     else:
#         es.indices.create(index=INDEX_NAME, body=mapping)
#         print(f"Created index: {INDEX_NAME}")



from elasticsearch import Elasticsearch
from es.es_sync_client import get_es_sync_client

es = get_es_sync_client()
INDEX_NAME = "portfoliocollection_index"

def create_index():
    if es.indices.exists(index=INDEX_NAME):
        print(f"✅ Index already exists: {INDEX_NAME}")
        return

    mapping = {
        "mappings": {
            "properties": {
                "id": {"type": "integer"},
                "vendor_id": {"type": "integer"},
                "name": {"type": "keyword"},
                "description": {"type": "text"},
                "cover_image": {"type": "keyword"},
                "cover_image_url": {"type": "keyword"},
                "slug": {"type": "keyword"},
                "business_name_slug": {"type": "keyword"},
                "is_featured": {"type": "boolean"},
                "is_active": {"type": "boolean"},
                "order": {"type": "integer"},
                "product_count": {"type": "integer"},
                "created_at": {"type": "date"},

                "products": {
                    "type": "nested",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "keyword"},
                        "price": {"type": "float"},
                        "stock_quantity": {"type": "integer"},
                        "vendor_name": {"type": "keyword"},
                        "description": {"type": "text"},
                        "meta_title": {"type": "keyword"},
                        "meta_description": {"type": "text"},
                        "images": {"type": "keyword"},
                        "business_name_slug": {"type": "keyword"},
                        "is_in_stock": {"type": "boolean"},
                        "is_featured": {"type": "boolean"},
                        "created_at": {"type": "date"},
                        "is_active": {"type": "boolean"}
                    }
                }
            }
        }
    }

    es.indices.create(index=INDEX_NAME, body=mapping)
    print(f" Created index: {INDEX_NAME}")

        

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
