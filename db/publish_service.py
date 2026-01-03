import time
import json
import logging
import re

logger = logging.getLogger(__name__)

def make_slug(value: str) -> str:
    if not value:
        return None
    value = value.lower().strip()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[\s_-]+", "-", value)
    value = re.sub(r"^-+|-+$", "", value)
    return value


def publish_vendor(
    vendor_slug: str,
    reader,
    writer,
):
    logger.info(f"Publishing vendor: {vendor_slug}")

    version = f"v{int(time.time())}"

    # 1️⃣ READ
    data = reader.fetch_vendor_data(vendor_slug)
    if not data:
        raise Exception("Vendor not found")

    vendor = data["vendor"]
    vendor_id = vendor["id"]

    snapshot_json = json.dumps(data["portfolio"])

    writer.upsert_vendor(vendor)

    # 2️⃣ WRITE
    vendor_version_id = writer.create_new_version(
        vendor_id=vendor_id,
        version=version
    )

    writer.insert_portfolio_snapshot(
        vendor_id=vendor_id,
        vendor_version_id=vendor_version_id,
        snapshot_json=snapshot_json
    )

    # ---------- Categories ----------
    writer.bulk_insert(
        table="category",
        columns=[
            "vendor_id",
            "vendor_version_id",
            "name",
            "slug",
            "description",
            "sort_order",
        ],
        rows=[
            (
                vendor_id,
                vendor_version_id,
                c["name"],
                make_slug(c["name"]),
                c.get("description"),
                c.get("sort_order", 0),
            )
            for c in data["categories"]
        ]
    )

    # ---------- Products ----------
    writer.bulk_insert(
        table="product",
        columns=[
            "source_id",
            "vendor_id",
            "vendor_version_id",
            "product_uid",
            "name",
            "slug",
            "category_name",
            "price",
            "sku",
            "stock_quantity",
            "primary_image",
            "gender",
            "description",
            "image_urls",
            "sizes",
            "is_active",
            "is_featured",
            "meta_title",
            "meta_description",
            "created_at",
            "updated_at"
        ],
        rows=[
            (
                p["source_id"],
                vendor_id,
                vendor_version_id,
                p["uid"],
                p["name"],
                make_slug(p["name"]),
                p.get("category_name"),
                p["price"],
                p.get("sku"),
                p.get("stock_quantity", 0),
                p.get("primary_image"),
                p.get("gender"),
                p.get("description"),
                json.dumps(p.get("image_urls")),
                json.dumps(p.get("sizes")),
                p.get("is_active", True),
                p.get("is_featured", False),
                p.get("meta_title"),
                p.get("meta_description"),
                p.get("created_at"),
                p.get("updated_at")
            )
            for p in data["products"]
        ]
    )

    # ---------- Collections ----------
    writer.bulk_insert(
        table="portfolio_collection",
        columns=[
            "vendor_id",
            "vendor_version_id",
            "name",
            "slug",
            "description",
            "cover_image",
            "sort_order",
            "is_featured",
        ],
        rows=[
            (
                vendor_id,
                vendor_version_id,
                c["name"],
                make_slug(c["name"]),
                c.get("description"),
                c.get("cover_image"),
                c.get("sort_order", 0),
                c.get("is_featured", False),
            )
            for c in data["collections"]
        ]
    )

    # ---------- Mapping ----------
    product_id_map = writer.fetch_product_id_map(vendor_version_id)
    collection_id_map = writer.fetch_collection_id_map(vendor_version_id)

    mapping_rows = []
    for c in data["collections"]:
        collection_id = collection_id_map[make_slug(c["name"])]

        for source_pid in c["product_source_ids"]:
            product_uid = next(
                p["uid"] for p in data["products"]
                if p["source_id"] == source_pid
            )
            mapping_rows.append(
                (collection_id, product_id_map[product_uid], 0)
            )

    writer.bulk_insert(
        table="portfolio_collection_product",
        columns=["collection_id", "product_id", "sort_order"],
        rows=mapping_rows
    )

    return {
        "vendor": vendor_slug,
        "version": version,
        "vendor_version_id": vendor_version_id,
        "status": "published"
    }
