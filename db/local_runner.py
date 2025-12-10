import os
import json
import logging
import time
import redis

from .sqlite_builder import SQLiteBuilder
from .postgres_reader import PostgresReader

logger = logging.getLogger(__name__)

def cleanup_tmp_files(base_path: str):
    """
    Remove stale SQLite tmp, tmp-wal, tmp-shm files.
    """
    for ext in ["", "-wal", "-shm"]:
        p = f"{base_path}{ext}"
        if os.path.exists(p):
            try:
                os.remove(p)
                logger.info(f"Removed stale temp file: {p}")
            except Exception as e:
                logger.error(f"Could not remove tmp file {p}: {e}")


def build_local(vendor_slug: str, output_dir: str = os.environ.get("SQLITE_CACHE_DIR", "../sqlite_cache")):
    os.makedirs(output_dir, exist_ok=True)

    timestamp = str(int(time.time()))
    db_name = f"{vendor_slug}.db"

    final_path = os.path.join(output_dir, db_name)
    tmp_base = os.path.join(output_dir, f"{vendor_slug}_{timestamp}.tmp")  # NO EXTENSION

    logger.info(f"Starting LOCAL DB build for vendor: {vendor_slug}")

    # ------------------
    # 1. Read Postgres
    # ------------------
    try:
        from config import settings
        db_params = {
            "host": settings.POSTGRES_HOST,
            "database": settings.POSTGRES_DB,
            "user": settings.POSTGRES_USER,
            "password": settings.POSTGRES_PASSWORD,
            "port": settings.POSTGRES_PORT,
        }
    except ImportError:
        db_params = {}

    reader = PostgresReader(**db_params)

    try:
        data = reader.fetch_vendor_data(vendor_slug)
        if not data:
            logger.error(f"Vendor not found: {vendor_slug}")
            return False
    finally:
        if hasattr(reader, "close"):
            reader.close()

    # ------------------
    # 2. Build SQLite TMP
    # ------------------
    cleanup_tmp_files(tmp_base)   # Remove stale files before building

    tmp_path = tmp_base  # Your builder writes directly to tmp_base

    builder = SQLiteBuilder(tmp_path)
    try:
        builder.create_tables()
        builder.insert_data(data)
        builder.create_fts_index()
        builder.optimize_db()
    finally:
        builder.close()

    # ------------------
    # 3. Move TMP → FINAL
    # ------------------
    os.replace(tmp_path, final_path)
    logger.info(f"Final SQLite DB ready: {final_path}")

    # Cleanup leftover tmp WAL/SHM
    cleanup_tmp_files(tmp_base)

    # ------------------
    # 4. Publish Redis Event
    # ------------------
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")

    try:
        r = redis.from_url(redis_url, decode_responses=True)
        message = {
            "vendor_slug": vendor_slug,
            "local_path": final_path,
            "version": timestamp,
            "s3_key": None,
        }
        r.publish("vendor.sqlite.ready", json.dumps(message))
        logger.info(f"Published local redis event: {message}")

    except Exception as e:
        logger.error(f"Redis publish failed: {e}")

    return True
