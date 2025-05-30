"""
S3 Uploader for sports data files.
"""
import logging
import time
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional, Dict
import os
import json

from .config import (
    AWS_REGION,
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    S3_BUCKET_NAME,
    MLB_DATA_PATH,
    NBA_DATA_PATH,
    LOG_FILE,
    UPLOAD_BATCH_SIZE,
    RETRY_ATTEMPTS,
    RETRY_DELAY,
    BASE_PATH,
    MLB_PATH,
    NBA_PATH,
    S3_MLB_PATH,
    S3_NBA_PATH
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class S3Uploader:
    def __init__(self):
        """Initialize S3 client with credentials."""
        self.s3_client = boto3.client(
            's3',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        self.bucket_name = S3_BUCKET_NAME

    def upload_file(self, file_path: Path, s3_key: str) -> bool:
        """
        Upload a single file to S3 with retry logic.
        
        Args:
            file_path: Local path to the file
            s3_key: S3 key (path) for the file
            
        Returns:
            bool: True if upload successful, False otherwise
        """
        for attempt in range(RETRY_ATTEMPTS):
            try:
                self.s3_client.upload_file(str(file_path), self.bucket_name, s3_key)
                logger.info(f"Successfully uploaded {file_path} to {s3_key}")
                return True
            except ClientError as e:
                logger.error(f"Error uploading {file_path} (attempt {attempt + 1}/{RETRY_ATTEMPTS}): {str(e)}")
                if attempt < RETRY_ATTEMPTS - 1:
                    time.sleep(RETRY_DELAY)
                continue
        return False

    def upload_directory(self, local_path: Path, s3_prefix: str) -> Dict[str, int]:
        """
        Upload all files in a directory to S3.
        
        Args:
            local_path: Local directory containing files to upload
            s3_prefix: S3 prefix (directory) for the files
            
        Returns:
            Dict[str, int]: Dictionary with counts of successful and failed uploads
        """
        stats = {"success": 0, "failed": 0}
        
        for file_path in local_path.rglob("*.json"):
            # Calculate S3 key by replacing local path with S3 prefix
            relative_path = file_path.relative_to(local_path)
            s3_key = f"{s3_prefix}/{relative_path}"
            
            if self.upload_file(file_path, s3_key):
                stats["success"] += 1
            else:
                stats["failed"] += 1
        
        return stats

    def upload_all_data(self) -> Dict[str, Dict[str, int]]:
        """
        Upload all MLB and NBA data to S3.
        
        Returns:
            Dict[str, Dict[str, int]]: Dictionary with results for MLB and NBA
        """
        results = {
            "mlb": {"success": 0, "failed": 0},
            "nba": {"success": 0, "failed": 0}
        }
        
        # Upload MLB data
        if MLB_PATH.exists():
            mlb_stats = self.upload_directory(MLB_PATH, S3_MLB_PATH)
            results["mlb"] = mlb_stats
        else:
            logger.warning(f"MLB data directory not found: {MLB_PATH}")
        
        # Upload NBA data
        if NBA_PATH.exists():
            nba_stats = self.upload_directory(NBA_PATH, S3_NBA_PATH)
            results["nba"] = nba_stats
        else:
            logger.warning(f"NBA data directory not found: {NBA_PATH}")
        
        return results

def main():
    """Main function to upload all sports data to S3."""
    if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY]):
        logger.error("AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables.")
        return
    
    uploader = S3Uploader()
    results = uploader.upload_all_data()
    
    # Print summary
    logger.info("\nUpload Summary:")
    for sport, stats in results.items():
        logger.info(f"\n{sport.upper()}:")
        logger.info(f"  Successfully uploaded: {stats['success']} files")
        logger.info(f"  Failed uploads: {stats['failed']} files")

if __name__ == "__main__":
    main() 