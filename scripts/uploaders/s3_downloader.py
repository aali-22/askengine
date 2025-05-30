import os
import json
import logging
import boto3
from pathlib import Path
from typing import Dict, List, Optional
from botocore.exceptions import ClientError
from .config import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    S3_BUCKET_NAME,
    BASE_PATH,
    MLB_PATH,
    NBA_PATH,
    S3_MLB_PATH,
    S3_NBA_PATH
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('s3_download.log'),
        logging.StreamHandler()
    ]
)

class S3Downloader:
    def __init__(self):
        """Initialize S3 client with credentials."""
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        self.bucket_name = S3_BUCKET_NAME

    def download_file(self, s3_key: str, local_path: Path) -> bool:
        """Download a single file from S3."""
        try:
            # Create parent directories if they don't exist
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.s3_client.download_file(
                self.bucket_name,
                s3_key,
                str(local_path)
            )
            logging.info(f"Successfully downloaded {s3_key} to {local_path}")
            return True
        except ClientError as e:
            logging.error(f"Error downloading {s3_key}: {str(e)}")
            return False

    def list_s3_files(self, prefix: str) -> List[str]:
        """List all files in an S3 prefix."""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            return [obj['Key'] for obj in response.get('Contents', [])]
        except ClientError as e:
            logging.error(f"Error listing files in {prefix}: {str(e)}")
            return []

    def download_directory(self, s3_prefix: str, local_path: Path) -> Dict[str, int]:
        """Download all files from an S3 prefix."""
        stats = {"success": 0, "failed": 0}
        
        # List all files in the S3 prefix
        s3_files = self.list_s3_files(s3_prefix)
        
        for s3_key in s3_files:
            # Calculate local path by replacing S3 prefix with local path
            relative_path = s3_key[len(s3_prefix):].lstrip('/')
            local_file_path = local_path / relative_path
            
            if self.download_file(s3_key, local_file_path):
                stats["success"] += 1
            else:
                stats["failed"] += 1
        
        return stats

    def download_all_data(self) -> Dict[str, Dict[str, int]]:
        """Download all MLB and NBA data from S3."""
        results = {
            "mlb": {"success": 0, "failed": 0},
            "nba": {"success": 0, "failed": 0}
        }
        
        # Download MLB data
        mlb_stats = self.download_directory(S3_MLB_PATH, MLB_PATH)
        results["mlb"] = mlb_stats
        
        # Download NBA data
        nba_stats = self.download_directory(S3_NBA_PATH, NBA_PATH)
        results["nba"] = nba_stats
        
        return results

def main():
    """Main function to download all data from S3."""
    if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY]):
        logging.error("AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables.")
        return
    
    downloader = S3Downloader()
    results = downloader.download_all_data()
    
    # Print summary
    logging.info("\nDownload Summary:")
    for sport, stats in results.items():
        logging.info(f"\n{sport.upper()}:")
        logging.info(f"  Successfully downloaded: {stats['success']} files")
        logging.info(f"  Failed downloads: {stats['failed']} files")

if __name__ == "__main__":
    main() 