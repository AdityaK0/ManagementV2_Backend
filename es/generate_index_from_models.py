"""
AUTO MAPPING GENERATOR
Reads: models_dump.md
Output: files inside elasticsearch/indexes/*.py
"""

import os
import re

INPUT_FILE = "models_dump.md"
OUTPUT_FOLDER = "indexes"

FIELD_TYPE_MAP = {
    "CharField": "keyword",
    "SlugField": "keyword",
    "EmailField": "keyword",
    "URLField": "keyword",
    "UUIDField": "keyword",
    "TextField": "text",
    "IntegerField": "integer",
    "BigIntegerField": "integer",
    "PositiveIntegerField": "integer",
    "DecimalField": "float",
    "FloatField": "float",
    "BooleanField": "boolean",
    "DateTimeField": "date",
    "DateField": "date",
    "ForeignKey": "keyword",
    "OneToOneField": "keyword",
    "ManyToManyField": "keyword",
    "JSONField": "object",
}

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def detect_field_type(field_line):
    for django_type, es_type in FIELD_TYPE_MAP.items():
        if django_type in field_line:
            return es_type
    return None  # fallback

def generate_index(class_name, fields):
    index_name = f"{class_name.lower()}_index"

    mapping = {
        "mappings": {
            "properties": {}
        },
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }
    }

    for field_name, field_type in fields.items():
        mapping["mappings"]["properties"][field_name] = {"type": field_type}

    content = f"""
from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9205")

INDEX_NAME = "{index_name}"

mapping = {mapping}

def create_index():
    if es.indices.exists(index=INDEX_NAME):
    
        print(f"Index '{{INDEX_NAME}}' already exists. Skipping...")
    else:
        es.indices.create(index=INDEX_NAME, body=mapping)
        print(f"Created index: {{INDEX_NAME}}")
        

def delete_index():
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
        print(f" Deleted index: {{INDEX_NAME}}")
    else:
        print(f"Index does not exist: {{INDEX_NAME}}")   
        
        


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "delete":
        delete_index()
    else:
        create_index()             
"""

    return index_name, content


def main():
    ensure_dir(OUTPUT_FOLDER)

    with open(INPUT_FILE, "r") as f:
        data = f.read()

    models = re.findall(r"class\s+(\w+)\(.*?\):([\s\S]*?)(?=class|\Z)", data)

    for class_name, model_block in models:
        fields = {}

        for line in model_block.split("\n"):
            line = line.strip()

            if "=" in line and not line.startswith(("def", "@", "class", "#")):
                field_name = line.split("=")[0].strip()
                field_type = detect_field_type(line)

                if field_type:
                    fields[field_name] = field_type

        index_name, content = generate_index(class_name, fields)

        with open(f"{OUTPUT_FOLDER}/{index_name}.py", "w") as f:
            f.write(content)

        print(f"✅ Generated index schema for model: {class_name}")


if __name__ == "__main__":
    main()
    print("\n🎉 DONE! Check elasticsearch/indexes folder")
