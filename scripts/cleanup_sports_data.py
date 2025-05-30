import os
import shutil
from pathlib import Path
import json
from collections import defaultdict
import logging
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class PlayerData:
    """Represents player data with validation."""
    player_name: str
    data: Dict[str, Any]

    def __eq__(self, other: 'PlayerData') -> bool:
        """Compare player data for equality."""
        return self.player_name == other.player_name and self.data == other.data

class DataCleaner:
    """Handles cleaning and consolidation of sports data."""
    
    def __init__(self, base_dir: Path = Path('data')):
        """Initialize the DataCleaner.
        
        Args:
            base_dir: Base directory for all sports data
        """
        self.base_dir = base_dir
        self.sports = ['baseball', 'basketball']

    def verify_player_data(self, players_dir: Path) -> List[Dict[str, Any]]:
        """Verify that all player data is present and valid.
        
        Args:
            players_dir: Directory containing player data files
            
        Returns:
            List of verified player data dictionaries
        """
        all_players: List[Dict[str, Any]] = []
        player_files = list(players_dir.glob('*.json'))
        
        # Check for existing combined file
        existing_combined = self._load_combined_players(players_dir)
        
        if existing_combined:
            existing_players = {p['player_name']: p for p in existing_combined}
            for file in player_files:
                if file.name == 'players.json':
                    continue
                    
                try:
                    with open(file, 'r') as f:
                        player_data = json.load(f)
                        if player_data['player_name'] not in existing_players:
                            logger.warning(
                                f"Player {player_data['player_name']} in {file.name} "
                                "not found in combined file!"
                            )
                            all_players.append(player_data)
                        elif existing_players[player_data['player_name']] != player_data:
                            logger.warning(
                                f"Player {player_data['player_name']} data differs between files!"
                            )
                            all_players.append(player_data)
                except Exception as e:
                    logger.error(f"Error processing {file}: {str(e)}")
                    continue
                    
            return existing_combined
        
        # Combine all individual files
        for file in player_files:
            try:
                with open(file, 'r') as f:
                    player_data = json.load(f)
                    all_players.append(player_data)
            except Exception as e:
                logger.error(f"Error reading {file}: {str(e)}")
                continue
        
        return all_players

    def _load_combined_players(self, players_dir: Path) -> Optional[List[Dict[str, Any]]]:
        """Load the combined players.json file if it exists.
        
        Args:
            players_dir: Directory containing player data files
            
        Returns:
            List of player data dictionaries if file exists, None otherwise
        """
        combined_file = players_dir / 'players.json'
        if combined_file.exists():
            try:
                with open(combined_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error reading combined players file: {str(e)}")
        return None

    def backup_cache(self) -> None:
        """Create a backup of the cache directory before removal."""
        cache_dir = self.base_dir / 'cache'
        if not cache_dir.exists():
            return
            
        backup_dir = self.base_dir / 'cache_backup'
        try:
            if not backup_dir.exists():
                shutil.copytree(cache_dir, backup_dir)
                logger.info("Created backup of cache directory")
            shutil.rmtree(cache_dir)
            logger.info("Removed cache directory")
        except Exception as e:
            logger.error(f"Error backing up cache: {str(e)}")
            raise

    def cleanup_season_data(self, sport: str, season_dir: Path) -> None:
        """Clean up data for a specific season.
        
        Args:
            sport: Name of the sport
            season_dir: Directory containing season data
        """
        players_dir = season_dir / 'players'
        if not players_dir.exists():
            return
            
        logger.info(f"Processing {sport} season {season_dir.name}...")
        
        try:
            # Verify and combine player data
            all_players = self.verify_player_data(players_dir)
            
            if all_players:
                # Backup existing players.json
                existing_players = players_dir / 'players.json'
                if existing_players.exists():
                    backup_file = players_dir / 'players.json.backup'
                    shutil.copy2(existing_players, backup_file)
                    logger.info("Created backup of existing players.json")
                
                # Write combined players.json
                combined_file = players_dir / 'players.json'
                with open(combined_file, 'w') as f:
                    json.dump(all_players, f, indent=2)
                logger.info(f"Created combined players.json with {len(all_players)} players")
                
                # Remove individual player files
                for file in players_dir.glob('*.json'):
                    if file.name not in ['players.json', 'players.json.backup']:
                        file.unlink()
                        logger.debug(f"Removed individual file: {file.name}")
            else:
                logger.warning(f"No player data found for {sport} season {season_dir.name}")
                
        except Exception as e:
            logger.error(f"Error processing {season_dir}: {str(e)}")

    def cleanup_data(self) -> None:
        """Main method to clean up all sports data."""
        try:
            # Backup and remove cache
            self.backup_cache()
            
            # Clean up redundant player files
            for sport in self.sports:
                sport_dir = self.base_dir / sport
                if not sport_dir.exists():
                    continue
                    
                for season_dir in sport_dir.iterdir():
                    if not season_dir.is_dir():
                        continue
                    self.cleanup_season_data(sport, season_dir)
                    
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            raise

def main() -> None:
    """Main entry point for the script."""
    try:
        cleaner = DataCleaner()
        cleaner.cleanup_data()
        logger.info("Data cleanup completed successfully")
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 