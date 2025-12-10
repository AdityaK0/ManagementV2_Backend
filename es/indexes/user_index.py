
from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9205")

INDEX_NAME = "user_index"

mapping = {'mappings': {'properties': {'name': {'type': 'keyword'}, 'email': {'type': 'keyword'}, 'role': {'type': 'keyword'}, 'phone_number': {'type': 'keyword'}, 'is_verified': {'type': 'boolean'}, 'created_at': {'type': 'date'}, 'updated_at': {'type': 'date'}}}, 'settings': {'number_of_shards': 1, 'number_of_replicas': 0}}

def create_index():
    if es.indices.exists(index=INDEX_NAME):
    
        print(f"Index '{INDEX_NAME}' already exists. Skipping...")
    else:
        es.indices.create(index=INDEX_NAME, body=mapping)
        print(f"Created index: {INDEX_NAME}")
        

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
