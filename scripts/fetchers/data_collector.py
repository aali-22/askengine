import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import requests
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

class DataCollector:
    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)
        self.mlb_path = self.base_path / "baseball"
        self.nba_path = self.base_path / "basketball"
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('data_collector.log'),
                logging.StreamHandler()
            ]
        )
        
        # MLB teams
        self.mlb_teams = {
            "ARI": "Arizona Diamondbacks",
            "ATL": "Atlanta Braves",
            "BAL": "Baltimore Orioles",
            "BOS": "Boston Red Sox",
            "CHC": "Chicago Cubs",
            "CHW": "Chicago White Sox",
            "CIN": "Cincinnati Reds",
            "CLE": "Cleveland Guardians",
            "COL": "Colorado Rockies",
            "DET": "Detroit Tigers",
            "HOU": "Houston Astros",
            "KCR": "Kansas City Royals",
            "LAA": "Los Angeles Angels",
            "LAD": "Los Angeles Dodgers",
            "MIA": "Miami Marlins",
            "MIL": "Milwaukee Brewers",
            "MIN": "Minnesota Twins",
            "NYM": "New York Mets",
            "NYY": "New York Yankees",
            "OAK": "Oakland Athletics",
            "PHI": "Philadelphia Phillies",
            "PIT": "Pittsburgh Pirates",
            "SDP": "San Diego Padres",
            "SEA": "Seattle Mariners",
            "SFG": "San Francisco Giants",
            "STL": "St. Louis Cardinals",
            "TBR": "Tampa Bay Rays",
            "TEX": "Texas Rangers",
            "TOR": "Toronto Blue Jays",
            "WSN": "Washington Nationals"
        }
        
        # NBA teams
        self.nba_teams = {
            "ATL": "Atlanta Hawks",
            "BOS": "Boston Celtics",
            "BKN": "Brooklyn Nets",
            "CHA": "Charlotte Hornets",
            "CHI": "Chicago Bulls",
            "CLE": "Cleveland Cavaliers",
            "DAL": "Dallas Mavericks",
            "DEN": "Denver Nuggets",
            "DET": "Detroit Pistons",
            "GSW": "Golden State Warriors",
            "HOU": "Houston Rockets",
            "IND": "Indiana Pacers",
            "LAC": "Los Angeles Clippers",
            "LAL": "Los Angeles Lakers",
            "MEM": "Memphis Grizzlies",
            "MIA": "Miami Heat",
            "MIL": "Milwaukee Bucks",
            "MIN": "Minnesota Timberwolves",
            "NOP": "New Orleans Pelicans",
            "NYK": "New York Knicks",
            "OKC": "Oklahoma City Thunder",
            "ORL": "Orlando Magic",
            "PHI": "Philadelphia 76ers",
            "PHX": "Phoenix Suns",
            "POR": "Portland Trail Blazers",
            "SAC": "Sacramento Kings",
            "SAS": "San Antonio Spurs",
            "TOR": "Toronto Raptors",
            "UTA": "Utah Jazz",
            "WAS": "Washington Wizards"
        }

    def create_season_directory(self, sport: str, year: int) -> Path:
        """Create directory structure for a season."""
        sport_path = self.mlb_path if sport == "mlb" else self.nba_path
        year_path = sport_path / str(year)
        
        # Create main season directory
        year_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (year_path / "league").mkdir(exist_ok=True)
        (year_path / "players").mkdir(exist_ok=True)
        
        return year_path

    def fetch_team_data(self, sport: str, team: str, year: int) -> Optional[Dict]:
        """Fetch team data from the appropriate API."""
        try:
            if sport == "mlb":
                # MLB API endpoint
                url = f"https://statsapi.mlb.com/api/v1/teams/{team}/stats?season={year}"
            else:
                # NBA API endpoint
                url = f"https://stats.nba.com/stats/team/{team}/stats?Season={year}"
            
            response = requests.get(url)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logging.error(f"Error fetching {sport} team data for {team} in {year}: {str(e)}")
            return None

    def fetch_league_data(self, sport: str, year: int) -> Optional[Dict]:
        """Fetch league-wide data from the appropriate API."""
        try:
            if sport == "mlb":
                # MLB API endpoint
                url = f"https://statsapi.mlb.com/api/v1/standings?season={year}"
            else:
                # NBA API endpoint
                url = f"https://stats.nba.com/stats/leaguestandings?Season={year}"
            
            response = requests.get(url)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logging.error(f"Error fetching {sport} league data for {year}: {str(e)}")
            return None

    def fetch_player_data(self, sport: str, year: int) -> Optional[Dict]:
        """Fetch player statistics from the appropriate API."""
        try:
            if sport == "mlb":
                # MLB API endpoint
                url = f"https://statsapi.mlb.com/api/v1/stats?season={year}"
            else:
                # NBA API endpoint
                url = f"https://stats.nba.com/stats/leaguedashplayerstats?Season={year}"
            
            response = requests.get(url)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logging.error(f"Error fetching {sport} player data for {year}: {str(e)}")
            return None

    def save_data(self, data: Dict, path: Path) -> bool:
        """Save data to a JSON file."""
        try:
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logging.error(f"Error saving data to {path}: {str(e)}")
            return False

    def collect_season_data(self, sport: str, year: int) -> bool:

        """Collect all data for a single season."""
        try:
            # Create directory structure
            year_path = self.create_season_directory(sport, year)
            
            # fetch and save league data
            league_data = self.fetch_league_data(sport, year)
            if league_data:
                self.save_data(league_data, year_path / "league" / "standings.json")
            
            # fetch and save team data
            teams = self.mlb_teams if sport == "mlb" else self.nba_teams
            for team in teams:
                team_data = self.fetch_team_data(sport, team, year)
                if team_data:
                    self.save_data(team_data, year_path / f"{team}.json")
            
            # fetch and save player data
            player_data = self.fetch_player_data(sport, year)
            if player_data:
                self.save_data(player_data, year_path / "players" / "season_stats.json")
            
            return True
        except Exception as e:
            logging.error(f"Error collecting {sport} data for {year}: {str(e)}")
            return False

    def collect_data_range(self, sport: str, start_year: int, end_year: int, max_workers: int = 5) -> None:
        """Collect data for a range of years using parallel processing."""


        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for year in range(start_year, end_year + 1):
                futures.append(executor.submit(self.collect_season_data, sport, year))
            
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logging.error(f"Error in data collection task: {str(e)}")

def main():
    collector = DataCollector()
    
    # Collect MLB data
    logging.info("Starting MLB data collection...")
    collector.collect_data_range("mlb", 2010, 2025)
    
    # Collect NBA data
    logging.info("Starting NBA data collection...")
    collector.collect_data_range("nba", 2010, 2025)
    
    logging.info("Data collection completed")

if __name__ == "__main__":
    main() 