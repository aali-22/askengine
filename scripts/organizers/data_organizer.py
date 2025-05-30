import json
import shutil
from pathlib import Path
from typing import Dict, List
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_year_folders(base_path: Path, start_year: int = 1999, end_year: int = 2024):
    """Create year folders for both MLB and NBA data"""
    for sport in ['baseball', 'basketball']:
        sport_path = base_path / sport
        for year in range(start_year, end_year + 1):
            year_path = sport_path / str(year)
            year_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created folder: {year_path}")

def move_root_files(base_dir: Path):
    """Move files from root data directory into their proper year folders"""
    # MLB files
    mlb_pattern = re.compile(r'mlb_(\d{4})_(teams|player_\d+)\.json')
    for file in base_dir.glob('mlb_*.json'):
        match = mlb_pattern.match(file.name)
        if match:
            year = match.group(1)
            filename = match.group(2)
            target_dir = base_dir / 'baseball' / year
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = target_dir / f"{filename}.json"
            shutil.move(str(file), str(target_path))
            logger.info(f"Moved {file.name} to {target_path}")

    # NBA files
    nba_pattern = re.compile(r'nba_(\d{4})_(teams|players)\.json')
    for file in base_dir.glob('nba_*.json'):
        match = nba_pattern.match(file.name)
        if match:
            year = match.group(1)
            filename = match.group(2)
            target_dir = base_dir / 'basketball' / year
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = target_dir / f"{filename}.json"
            shutil.move(str(file), str(target_path))
            logger.info(f"Moved {file.name} to {target_path}")

def organize_mlb_data(cache_dir: Path, target_dir: Path):
    """Organize MLB data into year-based folders"""
    for cache_file in cache_dir.glob('*.json'):
        try:
            with cache_file.open('r') as f:
                data = json.load(f)
                
            # Extract year from data
            year = None
            if 'roster' in data:
                # This is a roster file
                year = data.get('season', '2024')  # Default to 2024 if not found
                team_id = data.get('teamId')
                filename = f"roster_{team_id}.json"
            elif 'teams' in data:
                # This is a teams file
                year = data.get('season', '2024')
                filename = "teams.json"
            elif 'stats' in data:
                # This is a player stats file
                year = data.get('season', '2024')
                player_id = data.get('person', {}).get('id')
                filename = f"player_{player_id}.json"
            
            if year:
                target_path = target_dir / 'baseball' / str(year) / filename
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with target_path.open('w') as f:
                    json.dump(data, f, indent=2)
                logger.info(f"Organized MLB data: {target_path}")
                
        except Exception as e:
            logger.error(f"Error processing {cache_file}: {str(e)}")

def organize_nba_data(cache_dir: Path, target_dir: Path):
    """Organize NBA data into year-based folders"""
    for cache_file in cache_dir.glob('*.json'):
        try:
            with cache_file.open('r') as f:
                data = json.load(f)
                
            # Extract year from data
            year = None
            if 'resultSets' in data:
                # This is a stats file
                for result_set in data['resultSets']:
                    if 'headers' in result_set:
                        if 'TEAM_ID' in result_set['headers']:
                            # This is a teams file
                            year = '2024'  # NBA API uses current season
                            filename = "teams.json"
                        elif 'PLAYER_ID' in result_set['headers']:
                            # This is a players file
                            year = '2024'
                            filename = "players.json"
            
            if year:
                target_path = target_dir / 'basketball' / str(year) / filename
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with target_path.open('w') as f:
                    json.dump(data, f, indent=2)
                logger.info(f"Organized NBA data: {target_path}")
                
        except Exception as e:
            logger.error(f"Error processing {cache_file}: {str(e)}")

def main():
    # Define paths
    base_dir = Path('data')
    mlb_cache = base_dir / 'baseball' / 'cache'
    nba_cache = base_dir / 'basketball' / 'cache'
    
    # Create organized structure
    create_year_folders(base_dir)
    
    # Move files from root directory
    logger.info("Moving files from root directory...")
    move_root_files(base_dir)
    
    # Organize data
    logger.info("Organizing MLB data...")
    organize_mlb_data(mlb_cache, base_dir)
    
    logger.info("Organizing NBA data...")
    organize_nba_data(nba_cache, base_dir)
    
    logger.info("Data organization complete!")

if __name__ == '__main__':
    main() 