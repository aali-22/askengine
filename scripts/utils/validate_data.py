import os
import json
from pathlib import Path
from typing import Dict, List, Set
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_validation.log'),
        logging.StreamHandler()
    ]
)

class DataValidator:
    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)
        self.mlb_path = self.base_path / "baseball"
        self.nba_path = self.base_path / "basketball"
        
        # Required files for each season
        self.required_files = {
            "mlb": {
                "team": ["standings.json", "records.json"],
                "league": ["standings.json", "records.json"],
                "players": ["season_stats.json", "playoff_stats.json"]
            },
            "nba": {
                "team": ["standings.json", "records.json"],
                "league": ["standings.json", "records.json"],
                "players": ["season_stats.json", "playoff_stats.json"]
            }
        }
        
        # MLB teams
        self.mlb_teams = {
            "ARI", "ATL", "BAL", "BOS", "CHC", "CHW", "CIN", "CLE", "COL", "DET",
            "HOU", "KCR", "LAA", "LAD", "MIA", "MIL", "MIN", "NYM", "NYY", "OAK",
            "PHI", "PIT", "SDP", "SEA", "SFG", "STL", "TBR", "TEX", "TOR", "WSN"
        }
        
        # NBA teams
        self.nba_teams = {
            "ATL", "BOS", "BKN", "CHA", "CHI", "CLE", "DAL", "DEN", "DET", "GSW",
            "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", "MIN", "NOP", "NYK",
            "OKC", "ORL", "PHI", "PHX", "POR", "SAC", "SAS", "TOR", "UTA", "WAS"
        }

    def validate_season(self, sport: str, year: int) -> Dict:
        """Validate a single season's data."""
        sport_path = self.mlb_path if sport == "mlb" else self.nba_path
        year_path = sport_path / str(year)
        
        if not year_path.exists():
            return {
                "exists": False,
                "missing_files": [],
                "missing_teams": list(self.mlb_teams if sport == "mlb" else self.nba_teams)
            }
        
        results = {
            "exists": True,
            "missing_files": [],
            "missing_teams": []
        }
        
        # Check required files
        for category, files in self.required_files[sport].items():
            category_path = year_path / category
            if not category_path.exists():
                results["missing_files"].extend(files)
                continue
                
            for file in files:
                if not (category_path / file).exists():
                    results["missing_files"].append(f"{category}/{file}")
        
        # Check team files
        teams = self.mlb_teams if sport == "mlb" else self.nba_teams
        for team in teams:
            team_file = year_path / f"{team}.json"
            if not team_file.exists():
                results["missing_teams"].append(team)
        
        return results

    def validate_all_seasons(self, start_year: int = 2010, end_year: int = 2025) -> Dict:
        """Validate all seasons for both sports."""
        results = {
            "mlb": {},
            "nba": {}
        }
        
        for year in range(start_year, end_year + 1):
            results["mlb"][year] = self.validate_season("mlb", year)
            results["nba"][year] = self.validate_season("nba", year)
        
        return results

    def generate_report(self, results: Dict) -> None:
        """Generate a detailed report of data completeness."""
        logging.info("=== Data Validation Report ===")
        
        for sport in ["mlb", "nba"]:
            logging.info(f"\n=== {sport.upper()} Data Status ===")
            
            for year, status in results[sport].items():
                if not status["exists"]:
                    logging.info(f"\n{year}: No data directory found")
                    continue
                
                logging.info(f"\n{year}:")
                if status["missing_files"]:
                    logging.info("  Missing Files:")
                    for file in status["missing_files"]:
                        logging.info(f"    - {file}")
                
                if status["missing_teams"]:
                    logging.info("  Missing Teams:")
                    for team in status["missing_teams"]:
                        logging.info(f"    - {team}")
                
                if not status["missing_files"] and not status["missing_teams"]:
                    logging.info("  Complete!")

def main():
    validator = DataValidator()
    results = validator.validate_all_seasons()
    validator.generate_report(results)

if __name__ == "__main__":
    main() 