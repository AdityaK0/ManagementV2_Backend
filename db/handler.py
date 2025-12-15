import os
import sys
import logging
import time
from postgres_reader import PostgresReader
from sqlite_builder import SQLiteBuilder
from s3_uploader import S3Uploader
from redis_publisher import RedisPublisher

# Configure Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Lambda Handler to build SQLite DB for a vendor.
    Event payload: { "vendor_slug": "some-slug" }
    """
    logger.info(f"Received event: {event}")
    
    vendor_slug = event.get("vendor_slug")
    if not vendor_slug:
        logger.error("No vendor_slug provided.")
        return {"statusCode": 400, "body": "Missing vendor_slug"}

    timestamp = str(int(time.time()))
    db_name = f"{vendor_slug}.db"
    tmp_path = f"/tmp/{db_name}"
    
    # 1. READ Data
    logger.info("Step 1: Reading data from Postgres...")
    pg_reader = PostgresReader()
    try:
        data = pg_reader.fetch_vendor_data(vendor_slug)
        if not data:
            logger.error(f"No data found for vendor: {vendor_slug}")
            pg_reader.close()
            return {"statusCode": 404, "body": "Vendor not found"}
    except Exception as e:
        logger.error(f"Postgres Error: {e}")
        pg_reader.close()
        return {"statusCode": 500, "body": str(e)}
    pg_reader.close()

    # 2. BUILD SQLite
    logger.info(f"Step 2: Building SQLite DB at {tmp_path}...")
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
        
    builder = SQLiteBuilder(tmp_path)
    try:
        builder.create_tables()
        builder.insert_data(data)
        builder.create_fts_index()
        builder.optimize_db()
    except Exception as e:
        logger.error(f"SQLite Build Error: {e}")
        builder.close()
        if os.path.exists(tmp_path): 
            os.remove(tmp_path)
        return {"statusCode": 500, "body": str(e)}
    builder.close()

    # 3. UPLOAD to S3
    logger.info("Step 3: Uploading to S3...")
    uploader = S3Uploader()
    try:
        keys = uploader.upload_db(tmp_path, vendor_slug, timestamp)
    except Exception as e:
        logger.error(f"S3 Upload Error: {e}")
        if os.path.exists(tmp_path): 
            os.remove(tmp_path)
        return {"statusCode": 500, "body": str(e)}

    # 4. PUBLISH to Redis
    logger.info("Step 4: Publishing to Redis...")
    publisher = RedisPublisher()
    # Use the 'latest' key or versioned key? Usually we want the listeners to know a new thing is ready.
    # The listener downloads from the "Latest" pointer (vendor.db) usually, or the versioned one.
    # Step 6 says: "Download DB from S3 into: /sqlite_cache/vendor.db.tmp ... Atomically replace"
    # It probably downloads the *content* of the latest pointer. 
    # But sending the version helps debugging.
    
    # publisher.publish_update(
    #     vendor_slug=vendor_slug,
    #     s3_key=keys['latest_key'], # Point them to the standard key
    #     version=timestamp
    # )
    publisher.publish_update(
        vendor_slug=vendor_slug,
        s3_key=keys['current_key'],
        version=timestamp
    )



    # 5. CLEANUP
    logger.info("Step 5: Cleanup...")
    if os.path.exists(tmp_path):
        os.remove(tmp_path)

    logger.info("Success.")
    return {
        "statusCode": 200,
        "body": "Database built and published",
        "details": keys
    }
