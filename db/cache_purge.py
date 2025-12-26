
import os
import requests
import redis
import json
import time

CLOUDFLARE_API_TOKEN = os.environ["CF_API_TOKEN"]
CLOUDFLARE_ZONE_ID = os.environ["CF_ZONE_ID"]

CLOUDFLARE_API = f"https://api.cloudflare.com/client/v4/zones/{CLOUDFLARE_ZONE_ID}/purge_cache"

HEADERS = {
    "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
    "Content-Type": "application/json",
}
def purge_vendor_cache(vendor_slug: str):
    try:
        urls = [
            f"https://v2-api.fordgeindia.online/api/portfolio/public/{vendor_slug}/",
            f"https://v2-api.fordgeindia.online/api/portfolio/public/{vendor_slug}/products/",
            f"https://v2-api.fordgeindia.online/api/portfolio/public/{vendor_slug}/categories/",
        ]

        resp = requests.post(
            CLOUDFLARE_API,
            headers=HEADERS,
            json={"files": urls},
            timeout=5,
        )

        resp.raise_for_status()
        return resp.json()

    except Exception as e:
        # Log but NEVER fail publish
        print(f"[Cloudflare purge failed] {vendor_slug}: {e}")
        return None




def wait_for_sqlite_ack(vendor_slug, version, timeout=15):
    r = redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
    pubsub = r.pubsub()
    pubsub.subscribe("vendor.sqlite.ack")

    start = time.time()
    for msg in pubsub.listen():
        if time.time() - start > timeout:
            raise TimeoutError("Timed out waiting for SQLite ACK")

        if msg["type"] != "message":
            continue

        data = json.loads(msg["data"])
        if (
            data.get("vendor_slug") == vendor_slug
            and data.get("version") == version
            and data.get("status") == "ready"
        ):
            return
