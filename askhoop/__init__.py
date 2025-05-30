"""
AskHoop - Basketball data analysis and query module
Part of the AskEngine sports intelligence system
"""

from pathlib import Path
from typing import Dict

# Module configuration
MODULE_NAME = "askhoop"
DATA_DIR = Path(__file__).parent / "data"
SUPPORTED_LEAGUES = ["NBA"]

# Stats configuration
PLAYER_STATS = [
    "Points per Game (PPG)",
    "Rebounds",
    "Field Goal Percentage (FG%)",
    "3-Point Percentage (3P%)"
]

# NBA API endpoints
BASE_URL = "https://data.nba.net/prod/v1"
TEAMS_ENDPOINT = f"{BASE_URL}/{{year}}/teams.json"
PLAYERS_ENDPOINT = f"{BASE_URL}/{{year}}/players.json"
TEAM_STATS_ENDPOINT = f"{BASE_URL}/{{year}}/team_stats_rankings.json"
PLAYER_STATS_ENDPOINT = f"{BASE_URL}/{{year}}/player_stats_rankings.json"

# Required headers for NBA API
API_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Origin": "https://www.nba.com",
    "Referer": "https://www.nba.com/stats/",
    "Connection": "keep-alive"
}

def get_team_stats_params(season: str) -> Dict:
    """Get parameters for team stats request"""
    return {
        "season": season,
        "seasonType": "Regular Season"
    }

def get_player_stats_params(season: str) -> Dict:
    """Get parameters for player stats request"""
    return {
        "season": season,
        "seasonType": "Regular Season"
    }

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True) 