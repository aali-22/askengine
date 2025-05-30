import os
import json
import logging
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple
from scripts.uploaders.s3_uploader import S3Uploader
from scripts.uploaders.s3_downloader import S3Downloader
from scripts.uploaders.config import (
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
        logging.FileHandler('sync.log'),
        logging.StreamHandler()
    ]
)

class DataSync:
    def __init__(self):
        """Initialize uploader and downloader."""
        self.uploader = S3Uploader()
        self.downloader = S3Downloader()

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def get_local_files(self, directory: Path) -> Dict[str, str]:
        """Get all JSON files and their hashes from a local directory."""
        files = {}
        for path in directory.rglob("*.json"):
            relative_path = str(path.relative_to(directory))
            files[relative_path] = self.calculate_file_hash(path)
        return files

    def get_s3_files(self, prefix: str) -> Dict[str, str]:
        """Get all files and their ETags from an S3 prefix."""
        files = {}
        s3_files = self.downloader.list_s3_files(prefix)
        
        for s3_key in s3_files:
            try:
                response = self.uploader.s3_client.head_object(
                    Bucket=self.uploader.bucket_name,
                    Key=s3_key
                )
                # Remove quotes from ETag
                etag = response['ETag'].strip('"')
                relative_path = s3_key[len(prefix):].lstrip('/')
                files[relative_path] = etag
            except Exception as e:
                logging.error(f"Error getting ETag for {s3_key}: {str(e)}")
        
        return files

    def compare_files(self, local_files: Dict[str, str], s3_files: Dict[str, str]) -> Tuple[Set[str], Set[str], Set[str]]:
        """Compare local and S3 files to determine what needs to be synced."""
        local_paths = set(local_files.keys())
        s3_paths = set(s3_files.keys())
        
        # Files that exist in both places but have different hashes
        modified = {
            path for path in local_paths & s3_paths
            if local_files[path] != s3_files[path]
        }
        
        # Files that only exist locally
        local_only = local_paths - s3_paths
        
        # Files that only exist in S3
        s3_only = s3_paths - local_paths
        
        return modified, local_only, s3_only

    def sync_directory(self, local_path: Path, s3_prefix: str) -> Dict[str, int]:
        """Sync a directory between local storage and S3."""
        stats = {
            "uploaded": 0,
            "downloaded": 0,
            "skipped": 0,
            "errors": 0
        }
        
        # Get file lists and hashes
        local_files = self.get_local_files(local_path)
        s3_files = self.get_s3_files(s3_prefix)
        
        # Compare files
        modified, local_only, s3_only = self.compare_files(local_files, s3_files)
        
        # Upload new and modified files
        for path in local_only | modified:
            local_file = local_path / path
            s3_key = f"{s3_prefix}/{path}"
            if self.uploader.upload_file(str(local_file), s3_key):
                stats["uploaded"] += 1
            else:
                stats["errors"] += 1
        
        # Download files that only exist in S3
        for path in s3_only:
            s3_key = f"{s3_prefix}/{path}"
            local_file = local_path / path
            if self.downloader.download_file(s3_key, local_file):
                stats["downloaded"] += 1
            else:
                stats["errors"] += 1
        
        # Count skipped files
        stats["skipped"] = len(local_files) - len(modified) - len(local_only)
        
        return stats

    def sync_all_data(self) -> Dict[str, Dict[str, int]]:
        """Sync all MLB and NBA data between local storage and S3."""
        results = {
            "mlb": {"uploaded": 0, "downloaded": 0, "skipped": 0, "errors": 0},
            "nba": {"uploaded": 0, "downloaded": 0, "skipped": 0, "errors": 0}
        }
        
        # Sync MLB data
        mlb_stats = self.sync_directory(MLB_PATH, S3_MLB_PATH)
        results["mlb"] = mlb_stats
        
        # Sync NBA data
        nba_stats = self.sync_directory(NBA_PATH, S3_NBA_PATH)
        results["nba"] = nba_stats
        
        return results

def main():
    """Main function to sync all data between local storage and S3."""
    syncer = DataSync()
    results = syncer.sync_all_data()
    
    # Print summary
    logging.info("\nSync Summary:")
    for sport, stats in results.items():
        logging.info(f"\n{sport.upper()}:")
        logging.info(f"  Uploaded: {stats['uploaded']} files")
        logging.info(f"  Downloaded: {stats['downloaded']} files")
        logging.info(f"  Skipped: {stats['skipped']} files")
        logging.info(f"  Errors: {stats['errors']} files")

if __name__ == "__main__":
    main() 