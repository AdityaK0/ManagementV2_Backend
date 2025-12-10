import os
import redis
import json
import logging

logger = logging.getLogger()

class RedisPublisher:
    def __init__(self):
        self.redis_url = os.environ.get("REDIS_URL")
        # SSL setting might be needed for ElastiCache or similar
        self.client = redis.from_url(self.redis_url, decode_responses=True) if self.redis_url else None

    def publish_update(self, vendor_slug: str, s3_key: str, version: str):
        """
        Publishes update event to Redis.
        """
        if not self.client:
            logger.warning("Redis URL not set, skipping publish.")
            return

        channel = "vendor.sqlite.ready"
        message = {
            "vendor_slug": vendor_slug,
            "s3_key": s3_key,
            "version": version
        }
        
        logger.info(f"Publishing to {channel}: {message}")
        try:
            self.client.publish(channel, json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to publish to Redis: {e}")
