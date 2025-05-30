import boto3
from pathlib import Path
from typing import List, Dict, Any
import logging
from uploaders.config import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    S3_BUCKET_NAME
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_s3_client() -> boto3.client:
    """Initialize and return an S3 client with configured credentials.
    
    Returns:
        boto3.client: Configured S3 client
    """
    return boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

def clear_s3_bucket() -> None:
    """Clear all objects from the S3 bucket.
    
    Raises:
        Exception: If there's an error clearing the bucket
    """
    try:
        s3 = get_s3_client()
        paginator = s3.get_paginator('list_objects_v2')
        
        for page in paginator.paginate(Bucket=S3_BUCKET_NAME):
            if 'Contents' in page:
                objects_to_delete = [{'Key': obj['Key']} for obj in page['Contents']]
                if objects_to_delete:
                    s3.delete_objects(
                        Bucket=S3_BUCKET_NAME,
                        Delete={'Objects': objects_to_delete}
                    )
        logger.info("S3 bucket cleared successfully")
    except Exception as e:
        logger.error(f"Error clearing S3 bucket: {str(e)}")
        raise

def upload_file_to_s3(s3_client: boto3.client, file_path: Path, s3_key: str) -> None:
    """Upload a single file to S3.
    
    Args:
        s3_client: Configured S3 client
        file_path: Path to the local file
        s3_key: Target S3 key for the file
    
    Raises:
        Exception: If there's an error uploading the file
    """
    try:
        with open(file_path, 'rb') as f:
            s3_client.upload_fileobj(f, S3_BUCKET_NAME, s3_key)
        logger.info(f"Uploaded {s3_key}")
    except Exception as e:
        logger.error(f"Error uploading {s3_key}: {str(e)}")
        raise

def upload_to_s3() -> None:
    """Upload the reorganized data to S3, excluding cache directories.
    
    This function walks through the data directory and uploads all files
    except those in cache directories. It maintains the same directory
    structure in S3 as locally.
    
    Raises:
        Exception: If there's an error during the upload process
    """
    try:
        s3 = get_s3_client()
        data_dir = Path('data')
        sports = ['baseball', 'basketball', 'soccer']
        
        for sport in sports:
            sport_dir = data_dir / sport
            if not sport_dir.exists():
                logger.info(f"Skipping {sport} - directory not found")
                continue
                
            for item in sport_dir.rglob('*'):
                if item.is_file() and 'cache' not in item.parts:
                    s3_key = str(item.relative_to(data_dir)).replace('\\', '/')
                    upload_file_to_s3(s3, item, s3_key)
                    
        logger.info("Upload completed successfully")
    except Exception as e:
        logger.error(f"Error during upload process: {str(e)}")
        raise

def main() -> None:
    """Main entry point for the script."""
    try:
        clear_s3_bucket()
        upload_to_s3()
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 