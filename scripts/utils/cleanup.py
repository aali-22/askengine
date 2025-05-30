import os
import json
from pathlib import Path
import shutil
import logging
from typing import List, Set

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SportsDataCleaner:
    def __init__(self):
        self.base_dir = Path("data")
        self.sports = {
            "baseball": {
                "team_extensions": [".json"],
                "keep_dirs": ["teams", "players", "league"],
                "remove_dirs": ["cache"],
                "valid_team_files": {
                    "atl.json", "az.json", "bal.json", "bos.json", "chc.json",
                    "cin.json", "cle.json", "col.json", "cws.json", "det.json",
                    "hou.json", "kc.json", "laa.json", "lad.json", "mia.json",
                    "mil.json", "min.json", "nym.json", "nyy.json", "oak.json",
                    "phi.json", "pit.json", "sd.json", "sea.json", "sf.json",
                    "stl.json", "tb.json", "tex.json", "tor.json", "wsh.json"
                }
            },
            "basketball": {
                "team_extensions": [".json"],
                "keep_dirs": ["teams", "players", "league"],
                "remove_dirs": ["Regular_Season", "Playoffs", "cache"],
                "valid_team_files": {
                    "1610612737.json", "1610612738.json", "1610612739.json",
                    "1610612740.json", "1610612741.json", "1610612742.json",
                    "1610612743.json", "1610612744.json", "1610612745.json",
                    "1610612746.json", "1610612747.json", "1610612748.json",
                    "1610612749.json", "1610612750.json", "1610612751.json",
                    "1610612752.json", "1610612753.json", "1610612754.json",
                    "1610612755.json", "1610612756.json", "1610612757.json",
                    "1610612758.json", "1610612759.json", "1610612760.json",
                    "1610612761.json", "1610612762.json", "1610612763.json",
                    "1610612764.json", "1610612765.json", "1610612766.json"
                }
            }
        }

    def clean_season(self, sport: str, season: str):
        """Clean up a specific season's data"""
        season_dir = self.base_dir / sport / season
        if not season_dir.exists():
            return

        logger.info(f"Cleaning {sport} data for season {season}")
        sport_config = self.sports[sport]

        # Remove unnecessary directories
        for dir_name in sport_config["remove_dirs"]:
            dir_path = season_dir / dir_name
            if dir_path.exists():
                shutil.rmtree(dir_path)
                logger.info(f"Removed directory: {dir_path}")

        # Remove redundant team files (since they're in teams/)
        for file in season_dir.glob("*.json"):
            if file.name in sport_config["valid_team_files"]:
                file.unlink()
                logger.info(f"Removed redundant team file: {file}")

        # Ensure required directories exist
        for dir_name in sport_config["keep_dirs"]:
            (season_dir / dir_name).mkdir(parents=True, exist_ok=True)

    def clean_all_seasons(self):
        """Clean up all seasons for all sports"""
        for sport in self.sports:
            sport_dir = self.base_dir / sport
            if not sport_dir.exists():
                continue

            # Clean each season
            for season_dir in sport_dir.iterdir():
                if season_dir.is_dir() and season_dir.name.isdigit():
                    self.clean_season(sport, season_dir.name)

    def verify_data_structure(self):
        """Verify that the data structure is consistent across all seasons"""
        for sport in self.sports:
            sport_dir = self.base_dir / sport
            if not sport_dir.exists():
                continue

            for season_dir in sport_dir.iterdir():
                if season_dir.is_dir() and season_dir.name.isdigit():
                    # Check required directories
                    for dir_name in self.sports[sport]["keep_dirs"]:
                        dir_path = season_dir / dir_name
                        if not dir_path.exists():
                            logger.warning(f"Missing directory {dir_path}")

                    # Check for any remaining team files in root
                    for file in season_dir.glob("*.json"):
                        if file.name in self.sports[sport]["valid_team_files"]:
                            logger.warning(f"Found team file in root directory: {file}")

def main():
    cleaner = SportsDataCleaner()
    cleaner.clean_all_seasons()
    cleaner.verify_data_structure()

if __name__ == "__main__":
    main() 