import os
import boto3
import logging

logger = logging.getLogger()

class S3Uploader:
    def __init__(self):
        self.bucket_name = os.environ.get("S3_BUCKET_NAME")
        self.s3_client = boto3.client('s3')

    def upload_db(self, file_path: str, vendor_slug: str, timestamp: str):
        """
        Uploads DB to S3:
        1. sqlite_cache/{vendor_slug}/{timestamp}.db
        2. sqlite_cache/{vendor_slug}.db (Latest)
        
        Returns the keys uploaded.
        """
        if not self.bucket_name:
            raise ValueError("S3_BUCKET_NAME env var not set")

        filename = os.path.basename(file_path)
        
        # Versioned Key
        versioned_key = f"sqlite_cache/{vendor_slug}/{timestamp}.db"
        
        # Latest Key
        latest_key = f"sqlite_cache/{vendor_slug}.db"
        
        logger.info(f"Uploading to S3: {versioned_key}")
        self.s3_client.upload_file(file_path, self.bucket_name, versioned_key)
        
        logger.info(f"Uploading to S3 (Latest): {latest_key}")
        self.s3_client.upload_file(file_path, self.bucket_name, latest_key)
        
        return {
            "versioned_key": versioned_key,
            "latest_key": latest_key
        }
