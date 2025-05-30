import os
import json
import pandas as pd
import boto3
from pathlib import Path
from typing import Dict, Any, List
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_json_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Clean JSON data by removing null values and standardizing formats."""
    if isinstance(data, dict):
        return {k: clean_json_data(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        return [clean_json_data(item) for item in data if item is not None]
    return data

def process_file(file_path: Path, s3_bucket: str, s3_client) -> None:
    """Process a single JSON file and upload it to S3."""
    try:
        # Read the JSON Lines file
        data_list = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():  # Skip empty lines
                    data_list.append(json.loads(line))
        
        # Clean the data
        cleaned_data = [clean_json_data(item) for item in data_list]
        
        # Convert to DataFrame for additional cleaning
        df = pd.DataFrame(cleaned_data)
        
        # Remove duplicate rows
        df = df.drop_duplicates()
        
        # Convert back to JSON Lines format
        cleaned_json = '\n'.join([json.dumps(row.to_dict()) for _, row in df.iterrows()])
        
        # Create S3 key (path in S3)
        s3_key = f"cleaned/{file_path.name}"
        
        # Upload to S3
        s3_client.put_object(
            Bucket=s3_bucket,
            Key=s3_key,
            Body=cleaned_json,
            ContentType='application/json'
        )
        
        logger.info(f"Successfully processed and uploaded {file_path.name}")
        
    except Exception as e:
        logger.error(f"Error processing {file_path.name}: {str(e)}")

def main():
    # Get AWS credentials from environment variables
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    s3_bucket = os.getenv('S3_BUCKET_NAME')
    
    if not all([aws_access_key, aws_secret_key, s3_bucket]):
        logger.error("Missing required environment variables. Please set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and S3_BUCKET_NAME")
        return
    
    # Initialize S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=aws_region
    )
    
    # Get the data directory path
    data_dir = Path('data')
    
    # Process all JSON files
    for file_path in data_dir.glob('*.json'):
        logger.info(f"Processing {file_path.name}")
        process_file(file_path, s3_bucket, s3_client)

if __name__ == "__main__":
    main() 