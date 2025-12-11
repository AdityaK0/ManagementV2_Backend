import os
import asyncio
import json
import logging
import shutil
import boto3
import redis.asyncio as redis
from pathlib import Path

logger = logging.getLogger("redis_listener")

class RedisListener:
    def __init__(self):
        self.redis_url = os.environ.get("REDIS_URL", "redis://localhost:6380")
        self.s3_bucket = os.environ.get("S3_BUCKET_NAME")
        self.cache_dir = Path(os.environ.get("SQLITE_CACHE_DIR", "/tmp/sqlite_cache"))
        
        # Ensure cache dir exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # S3 Client (Initialize only if S3_BUCKET_NAME is set, otherwise assume local/mock)
        if self.s3_bucket:
            self.s3_client = boto3.client(
                's3',
                region_name=os.environ.get("AWS_REGION", "us-east-1"),
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY")
            )
        else:
            self.s3_client = None

    async def start(self):
        """Starts the Redis subscription loop."""
        print(f"Connecting to Redis at {self.redis_url}...")
        logger.info(f"Connecting to Redis at {self.redis_url}...")
        try:
            r = redis.from_url(self.redis_url, decode_responses=True)
            async with r.pubsub() as pubsub:
                await pubsub.subscribe("vendor.sqlite.ready")
                logger.info("Subscribed to channel: vendor.sqlite.ready")
                
                async for message in pubsub.listen():
                    if message["type"] == "message":
                        await self.handle_message(message["data"])
        except Exception as e:
            logger.error(f"Redis Listener Error: {e}")
            # Retry logic could go here
            await asyncio.sleep(5)
            await self.start()

    async def handle_message(self, data_str: str):
        try:
            data = json.loads(data_str)
            vendor_slug = data.get("vendor_slug")
            s3_key = data.get("s3_key")
            local_path = data.get("local_path")
            version = data.get("version")
            
            logger.info(f"Received update for {vendor_slug} (v{version})")
            
            if vendor_slug:
                # Run blocking download/copy in executor
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.update_db_file, vendor_slug, s3_key, local_path)
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
        except Exception as e:
            logger.error(f"Error handling message: {e}")

    def update_db_file(self, vendor_slug: str, s3_key: str = None, local_path: str = None):
        """
        Updates the local DB file from S3 OR a local source path.
        """
        target_file = self.cache_dir / f"{vendor_slug}.db"
        tmp_file = self.cache_dir / f"{vendor_slug}.db.tmp"
        
        try:
            if local_path and os.path.exists(local_path):
                logger.info(f"[Local Mode] Copying from {local_path} to {tmp_file}...")
                shutil.copy2(local_path, tmp_file)
            elif s3_key and self.s3_client:
                logger.info(f"[S3 Mode] Downloading {s3_key} to {tmp_file}...")
                self.s3_client.download_file(self.s3_bucket, s3_key, str(tmp_file))
            else:
                logger.warning(f"No valid source (s3_key or local_path) for {vendor_slug}")
                return

            logger.info(f"Atomically replacing {target_file}...")
            os.replace(tmp_file, target_file)
            logger.info(f"Successfully updated DB for {vendor_slug}")
            
        except Exception as e:
            logger.error(f"Update failed: {e}")
            if tmp_file.exists():
                os.remove(tmp_file)

async def start_background_listener():
    """Entry point to run as background task."""
    logger.info(f"REDIS URL: {os.environ.get('REDIS_URL')}")
    listener = RedisListener()
    await listener.start()
