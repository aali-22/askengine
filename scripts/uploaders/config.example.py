"""
AWS Configuration settings for data uploads.
Example configuration file - copy to config.py and fill in your credentials.
"""
import os
from pathlib import Path
from typing import Dict, List, Any
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# AWS Configuration
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-2')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'askengine-data')

# Validate required environment variables
if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY]):
    raise ValueError(
        "Missing required AWS credentials. Please set AWS_ACCESS_KEY_ID and "
        "AWS_SECRET_ACCESS_KEY environment variables."
    )

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / 'data'
LOG_DIR = BASE_DIR / 'logs'

# Sport-specific paths
SPORT_PATHS = {
    'baseball': {
        'local': DATA_DIR / 'baseball',
        's3': 'baseball'
    },
    'basketball': {
        'local': DATA_DIR / 'basketball',
        's3': 'basketball'
    }
}

# Required file structure
REQUIRED_FILES: Dict[str, Dict[str, List[str]]] = {
    'baseball': {
        'team': ['standings.json', 'records.json'],
        'league': ['standings.json', 'records.json'],
        'players': ['season_stats.json', 'playoff_stats.json']
    },
    'basketball': {
        'team': ['standings.json', 'records.json'],
        'league': ['standings.json', 'records.json'],
        'players': ['season_stats.json', 'playoff_stats.json']
    }
}

# Upload settings
UPLOAD_SETTINGS = {
    'batch_size': int(os.getenv('UPLOAD_BATCH_SIZE', '100')),
    'retry_attempts': int(os.getenv('RETRY_ATTEMPTS', '3')),
    'retry_delay': int(os.getenv('RETRY_DELAY', '5'))
}

# Logging configuration
LOG_FILE = LOG_DIR / 'upload.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Create required directories
for directory in [DATA_DIR, LOG_DIR]:
    directory.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def get_sport_path(sport: str, path_type: str = 'local') -> Path:
    """Get the path for a specific sport.
    
    Args:
        sport: Name of the sport (baseball or basketball)
        path_type: Type of path to return ('local' or 's3')
        
    Returns:
        Path object for the requested sport and path type
        
    Raises:
        ValueError: If sport or path_type is invalid
    """
    if sport not in SPORT_PATHS:
        raise ValueError(f"Invalid sport: {sport}")
    if path_type not in ['local', 's3']:
        raise ValueError(f"Invalid path type: {path_type}")
        
    return SPORT_PATHS[sport][path_type]

def get_required_files(sport: str) -> Dict[str, List[str]]:
    """Get the required files for a specific sport.
    
    Args:
        sport: Name of the sport (baseball or basketball)
        
    Returns:
        Dictionary of required files by category
        
    Raises:
        ValueError: If sport is invalid
    """
    if sport not in REQUIRED_FILES:
        raise ValueError(f"Invalid sport: {sport}")
        
    return REQUIRED_FILES[sport] 