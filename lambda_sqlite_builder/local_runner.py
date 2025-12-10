import os
import json
import logging
import time
import shutil
import redis

# Import existing logic
from lambda_sqlite_builder.builder.sqlite_builder import SQLiteBuilder
from lambda_sqlite_builder.builder.postgres_reader import PostgresReader

logger = logging.getLogger(__name__)

def build_local(vendor_slug: str, output_dir: str = os.environ.get("SQLITE_CACHE_DIR", "../sqlite_cache")):
    """
    Orchestrates the build process LOCALLY (without Lambda/S3).
    1. Fetch Data from Postgres (using local env/Django settings).
    2. Build SQLite DB.
    3. Save to output_dir.
    4. Publish Redis event pointing to local file.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = str(int(time.time()))
    db_name = f"{vendor_slug}.db"
    target_path = os.path.join(output_dir, db_name)
    tmp_path = os.path.join(output_dir, f"{vendor_slug}_{timestamp}.tmp")
    
    logger.info(f"Starting LOCAL build for {vendor_slug}...")
    
    # 1. Read Data
    # For local mode, we try to use the Django/FastAPI config settings 
    # which can load .env.local
    try:
        from config import settings
        db_params = {
            "host": settings.POSTGRES_HOST,
            "database": settings.POSTGRES_DB,
            "user": settings.POSTGRES_USER,
            "password": settings.POSTGRES_PASSWORD,
            "port": settings.POSTGRES_PORT
        }
    except ImportError:
        # Fallback to env vars if config module not found (e.g. running script standalone)
        db_params = {}

    reader = PostgresReader(**db_params)
    try:
        data = reader.fetch_vendor_data(vendor_slug)
        if not data:
            logger.error(f"No data found for {vendor_slug}")
            return False
    finally:
        reader.close()
        
    # 2. Build SQLite
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
    
    builder = SQLiteBuilder(tmp_path)
    try:
        builder.create_tables()
        builder.insert_data(data)
        builder.create_fts_index()
        builder.optimize_db()
    except Exception as e:
        logger.error(f"Build failed: {e}")
        builder.close()
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise e
    builder.close()
    
    # 3. Finalize File
    # We move it to a 'latest' location if we want, but Redis Listener expects a source path.
    # In 'local mode', the listener copies from 'local_path'.
    # So let's keep the temp file as the 'source' or just rename it to something stable?
    # Actually, let's provide the specific built file.
    
    final_source_path = os.path.join(output_dir, f"{vendor_slug}.db")
    os.replace(tmp_path, final_source_path)
    
    logger.info(f"Database built at: {final_source_path}")
    
    # 4. Redis Publish
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
    try:
        r = redis.from_url(redis_url, decode_responses=True)
        message = {
            "vendor_slug": vendor_slug,
            "local_path": final_source_path, # Tell listener where to copy FROM
            "version": timestamp,
            "s3_key": None # Explicitly null
        }
        r.publish("vendor.sqlite.ready", json.dumps(message))
        logger.info(f"Published local event: {message}")
    except Exception as e:
        logger.error(f"Redis publish failed: {e}")
        
    return True
