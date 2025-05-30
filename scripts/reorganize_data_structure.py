import os
import shutil
from pathlib import Path
import json
import logging
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataReorganizer:
    """Handles the reorganization of sports data directory structure."""
    
    def __init__(self, base_dir: Path = Path('data')):
        """Initialize the DataReorganizer.
        
        Args:
            base_dir: Base directory for all sports data
        """
        self.base_dir = base_dir
        self.sports = ['baseball', 'basketball', 'soccer']

    def create_empty_json_file(self, file_path: Path) -> None:
        """Create an empty JSON file if it doesn't exist.
        
        Args:
            file_path: Path to the JSON file to create
        """
        if not file_path.exists():
            with open(file_path, 'w') as f:
                json.dump([], f)
            logger.debug(f"Created empty JSON file: {file_path}")

    def create_directory_structure(self) -> None:
        """Create the new directory structure for all sports."""
        for sport in self.sports:
            sport_dir = self.base_dir / sport
            sport_dir.mkdir(exist_ok=True)
            logger.info(f"Created directory for {sport}")
            
            if sport == 'baseball':
                records_dir = sport_dir / 'records'
                records_dir.mkdir(exist_ok=True)
                
                for record_type in ['team', 'player']:
                    record_file = records_dir / f'{record_type}_alltime_record.json'
                    self.create_empty_json_file(record_file)

    def reorganize_baseball(self) -> None:
        """Reorganize baseball data structure."""
        baseball_dir = self.base_dir / 'baseball'
        
        for year_dir in baseball_dir.iterdir():
            if not year_dir.is_dir() or year_dir.name == 'records':
                continue
                
            try:
                # Create new structure
                league_dir = year_dir / 'league'
                league_dir.mkdir(exist_ok=True)
                
                # Create reg_season and playoff directories
                reg_season_dir = league_dir / 'reg_season'
                playoff_dir = league_dir / 'playoff'
                reg_season_dir.mkdir(exist_ok=True)
                playoff_dir.mkdir(exist_ok=True)
                
                # Move standings to reg_season if it exists
                old_standings = league_dir / 'standings.json'
                if old_standings.exists():
                    shutil.move(str(old_standings), str(reg_season_dir / 'standings.json'))
                    logger.info(f"Moved standings for {year_dir.name}")
                
                # Create records directory
                records_dir = year_dir / 'records'
                records_dir.mkdir(exist_ok=True)
                self.create_empty_json_file(records_dir / 'season_records.json')
                
                # Create player_stats directory
                player_stats_dir = year_dir / 'player_stats'
                player_stats_dir.mkdir(exist_ok=True)
                
                # Move team JSON files
                for file in year_dir.glob('*.json'):
                    if file.name not in ['teams.json', 'standings.json']:
                        shutil.move(str(file), str(player_stats_dir / file.name))
                        logger.debug(f"Moved {file.name} to player_stats")
                
                # Clean up empty directories
                for dir_to_check in ['players', 'teams']:
                    dir_path = year_dir / dir_to_check
                    if dir_path.exists() and not any(dir_path.iterdir()):
                        shutil.rmtree(dir_path)
                        logger.debug(f"Removed empty directory: {dir_path}")
                        
            except Exception as e:
                logger.error(f"Error processing {year_dir}: {str(e)}")
                continue

    def reorganize_basketball(self) -> None:
        """Reorganize basketball data structure."""
        basketball_dir = self.base_dir / 'basketball'
        
        for year_dir in basketball_dir.iterdir():
            if not year_dir.is_dir():
                continue
                
            try:
                # Create new structure
                league_dir = year_dir / 'league'
                league_dir.mkdir(exist_ok=True)
                
                # Create standings directory
                standings_dir = league_dir / 'standings'
                standings_dir.mkdir(exist_ok=True)
                
                for standing_type in ['division', 'conference']:
                    self.create_empty_json_file(standings_dir / f'{standing_type}.json')
                
                # Create playoff directory
                playoff_dir = year_dir / 'playoff'
                playoff_dir.mkdir(exist_ok=True)
                self.create_empty_json_file(playoff_dir / 'bracket.json')
                
                # Create records directory
                records_dir = year_dir / 'records'
                records_dir.mkdir(exist_ok=True)
                self.create_empty_json_file(records_dir / 'season_records.json')
                
                # Clean up empty teams directory
                teams_dir = year_dir / 'teams'
                if teams_dir.exists() and not any(teams_dir.iterdir()):
                    shutil.rmtree(teams_dir)
                    logger.debug(f"Removed empty teams directory: {teams_dir}")
                
                # Handle players directory
                players_dir = year_dir / 'players'
                players_dir.mkdir(exist_ok=True)
                
                league_players = league_dir / 'players.json'
                if league_players.exists():
                    shutil.move(str(league_players), str(players_dir / 'players.json'))
                    logger.info(f"Moved players.json for {year_dir.name}")
                else:
                    self.create_empty_json_file(players_dir / 'players.json')
                    
            except Exception as e:
                logger.error(f"Error processing {year_dir}: {str(e)}")
                continue

def main() -> None:
    """Main entry point for the script."""
    try:
        reorganizer = DataReorganizer()
        
        logger.info("Creating new directory structure...")
        reorganizer.create_directory_structure()
        
        logger.info("Reorganizing baseball data...")
        reorganizer.reorganize_baseball()
        
        logger.info("Reorganizing basketball data...")
        reorganizer.reorganize_basketball()
        
        logger.info("Data structure reorganization complete!")
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 