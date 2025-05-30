"""
AskSlugger - Baseball data analysis and query module
Part of the AskEngine sports intelligence system
"""

from pathlib import Path
from typing import Dict, List

# Module configuration
MODULE_NAME = "askslugger"
DATA_DIR = Path(__file__).parent / "data"
SUPPORTED_LEAGUES = ["MLB"]

# Stats configuration
PLAYER_STATS = [
    "Home Runs (HR)",
    "Batting Average (AVG)",
    "On-Base Percentage (OBP)",
    "Slugging (SLG)",
    "RBIs",
    "WAR"
]

# MLB API endpoints
BASE_URL = "https://lookup-service-prod.mlb.com"
TEAM_ENDPOINT = f"{BASE_URL}/json/named.team_all_season.bam"
ROSTER_ENDPOINT = f"{BASE_URL}/json/named.roster_team_alltime.bam"
PLAYER_STATS_ENDPOINT = f"{BASE_URL}/json/named.sport_hitting_tm.bam"
TEAM_STATS_ENDPOINT = f"{BASE_URL}/json/named.team_stats_rankings_composed.bam"

# Required headers for MLB API
API_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Origin": "https://www.mlb.com",
    "Referer": "https://www.mlb.com/",
    "Connection": "keep-alive"
}

def get_team_params(season: str) -> Dict:
    """Get parameters for team request"""
    return {
        "sport_code": "'mlb'",
        "all_star_sw": "'N'",
        "sort_order": "name_asc",
        "season": season
    }

def get_roster_params(team_id: str, season: str) -> Dict:
    """Get parameters for roster request"""
    return {
        "team_id": f"'{team_id}'",
        "season": season,
        "roster_type": "active"
    }

def get_player_stats_params(player_id: str, season: str) -> Dict:
    """Get parameters for player stats request"""
    return {
        "game_type": "'R'",
        "player_id": f"'{player_id}'",
        "season": season,
        "sort_by": "name_asc"
    }

def get_team_stats_params(season: str) -> Dict:
    """Get parameters for team stats request"""
    return {
        "sport_code": "'mlb'",
        "game_type": "'R'",
        "season": season,
        "sort_by": "win_pct_desc"
    }

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True) 