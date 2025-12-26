import os
import asyncio
import json
import logging
import shutil
import boto3
import redis.asyncio as redis
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import time

EXECUTOR = ThreadPoolExecutor(max_workers=1)

logger = logging.getLogger("redis_listener")

class RedisListener:
    def __init__(self):
        self.redis_url = os.environ.get("REDIS_URL", "redis://localhost:6380")
        self.s3_bucket = os.environ.get("S3_BUCKET_NAME")
        self.cache_dir = Path(os.environ.get("SQLITE_CACHE_DIR", "/tmp/sqlite_cache"))
        self.redis = redis.from_url(
            self.redis_url,
            decode_responses=True,
            socket_timeout=None
        )

        self.redis_kv = redis.from_url(
            self.redis_url,
            decode_responses=True,
            socket_timeout=5,
        )

        
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

    
    async def start(self): # single lister all over 
        while True:
            try:
                # r = redis.from_url(self.redis_url, decode_responses=True,socket_timeout=None)
                pubsub = self.redis.pubsub()
                await pubsub.subscribe("vendor.sqlite.ready")
                logger.info("Subscribed to vendor.sqlite.ready")

                async for message in pubsub.listen():
                    if message["type"] == "message":
                            await self.handle_message(message["data"])

            except Exception as e:
                logger.exception("Redis listener crashed. Retrying in 5s")
                await asyncio.sleep(5)


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
                success = await loop.run_in_executor(
                    EXECUTOR,
                    self.update_db_file,
                    vendor_slug,
                    s3_key,
                    local_path
                )
                if success:
                    logger.info(f"ACK published for {vendor_slug} (v{version})")

                    await self.redis_kv.setex(
                        f"vendor:sqlite:ready:{vendor_slug}:{version}",
                        120,
                        "1"
                    )
                    logger.info(
                        f"ACK KEY SET → vendor:sqlite:ready:{vendor_slug}:{version}"
                    )

                else:
                    logger.error("NOT publishing ACK — DB update failed")    


                # await loop.run_in_executor(None, self.update_db_file, vendor_slug, s3_key, local_path)
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
        except Exception as e:
            logger.error(f"Error handling message: {e}")

    def update_db_file(self, vendor_slug: str, s3_key: str = None, local_path: str = None):
        """
        Updates the local DB file from S3 OR a local source path.
        """
        # target_file = self.cache_dir / f"{vendor_slug}.db"
        # tmp_file = self.cache_dir / f"{vendor_slug}.db.tmp"

        current_file = self.cache_dir / f"{vendor_slug}.current.db"
        tmp_file = self.cache_dir / f"{vendor_slug}.{int(time.time())}.db"

        
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

            logger.info(f"Atomically replacing {current_file}...")
            # os.replace(tmp_file, target_file)
            os.replace(tmp_file, current_file)
            logger.info(f"Successfully updated DB for {vendor_slug}")

            for suffix in ("-wal", "-shm"):
                stale = self.cache_dir / f"{vendor_slug}.current.db{suffix}"
                if stale.exists():
                    stale.unlink()
            return True            
        except Exception as e:
            logger.error(f"Update failed: {e}")
            if tmp_file.exists():
                os.remove(tmp_file)
            return False    

async def start_background_listener():
    """Entry point to run as background task."""
    logger.info(f"REDIS URL: {os.environ.get('REDIS_URL')}")
    listener = RedisListener()
    await listener.start()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    try:
        asyncio.run(start_background_listener())
    except KeyboardInterrupt:
        logger.info("Redis listener stopped")
