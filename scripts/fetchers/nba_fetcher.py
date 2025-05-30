import os
import json
import time
from pathlib import Path
import requests
from typing import Dict, List, Optional
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# NBA API configuration
NBA_BASE_URL = "https://stats.nba.com/stats"
TEAMS_ENDPOINT = f"{NBA_BASE_URL}/leaguestandingsv3"
PLAYER_STATS_ENDPOINT = f"{NBA_BASE_URL}/leaguedashplayerstats"
TEAM_ROSTER_ENDPOINT = f"{NBA_BASE_URL}/commonteamroster"
PLAYOFF_STATS_ENDPOINT = f"{NBA_BASE_URL}/playoffstats"
STANDINGS_ENDPOINT = f"{NBA_BASE_URL}/leaguestandingsv3"

# Team abbreviations mapping
TEAM_ABBREVIATIONS = {
    '1610612737': 'ATL',  # Atlanta Hawks
    '1610612738': 'BOS',  # Boston Celtics
    '1610612751': 'BKN',  # Brooklyn Nets
    '1610612766': 'CHA',  # Charlotte Hornets
    '1610612741': 'CHI',  # Chicago Bulls
    '1610612739': 'CLE',  # Cleveland Cavaliers
    '1610612742': 'DAL',  # Dallas Mavericks
    '1610612743': 'DEN',  # Denver Nuggets
    '1610612765': 'DET',  # Detroit Pistons
    '1610612744': 'GSW',  # Golden State Warriors
    '1610612745': 'HOU',  # Houston Rockets
    '1610612754': 'IND',  # Indiana Pacers
    '1610612746': 'LAC',  # LA Clippers
    '1610612747': 'LAL',  # Los Angeles Lakers
    '1610612763': 'MEM',  # Memphis Grizzlies
    '1610612748': 'MIA',  # Miami Heat
    '1610612749': 'MIL',  # Milwaukee Bucks
    '1610612750': 'MIN',  # Minnesota Timberwolves
    '1610612740': 'NOP',  # New Orleans Pelicans
    '1610612752': 'NYK',  # New York Knicks
    '1610612760': 'OKC',  # Oklahoma City Thunder
    '1610612753': 'ORL',  # Orlando Magic
    '1610612755': 'PHI',  # Philadelphia 76ers
    '1610612756': 'PHX',  # Phoenix Suns
    '1610612757': 'POR',  # Portland Trail Blazers
    '1610612758': 'SAC',  # Sacramento Kings
    '1610612759': 'SAS',  # San Antonio Spurs
    '1610612761': 'TOR',  # Toronto Raptors
    '1610612762': 'UTA',  # Utah Jazz
    '1610612764': 'WAS',  # Washington Wizards
}

NBA_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.nba.com/',
    'Origin': 'https://www.nba.com'
}

class NBADataFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(NBA_HEADERS)
        
        # Set up retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
    
    def get_teams(self, season: str, season_type: str = 'Regular Season') -> Dict:
        """Get list of all NBA teams"""
        params = {
            'LeagueID': '00',
            'Season': season,
            'SeasonType': season_type
        }
        try:
            response = self.session.get(TEAMS_ENDPOINT, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching teams for {season} {season_type}: {str(e)}")
            return {"resultSets": [{"rowSet": []}]}
    
    def get_team_roster(self, team_id: str, season: str) -> Dict:
        """Get team roster"""
        params = {
            'TeamID': team_id,
            'Season': season
        }
        try:
            response = self.session.get(TEAM_ROSTER_ENDPOINT, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching roster for team {team_id}: {str(e)}")
            return {"resultSets": [{"rowSet": []}]}
    
    def get_player_stats(self, season: str, season_type: str = 'Regular Season') -> Dict:
        """Get all player statistics"""
        params = {
            'LeagueID': '00',
            'Season': season,
            'SeasonType': season_type,
            'PerMode': 'PerGame',
            'MeasureType': 'Base',
            'PlusMinus': 'N',
            'PaceAdjust': 'N',
            'Rank': 'N',
            'Outcome': '',
            'Location': '',
            'Month': '0',
            'SeasonSegment': '',
            'DateFrom': '',
            'DateTo': '',
            'OpponentTeamID': '0',
            'VsConference': '',
            'VsDivision': '',
            'GameSegment': '',
            'Period': '0',
            'ShotClockRange': '',
            'LastNGames': '0',
            'GameScope': '',
            'PlayerExperience': '',
            'PlayerPosition': '',
            'StarterBench': '',
            'Active': '1'
        }
        try:
            response = self.session.get(PLAYER_STATS_ENDPOINT, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching player stats for {season} {season_type}: {str(e)}")
            return {"resultSets": [{"rowSet": []}]}

    def get_standings(self, season: str, season_type: str = 'Regular Season') -> Dict:
        """Get team standings"""
        params = {
            'LeagueID': '00',
            'Season': season,
            'SeasonType': season_type
        }
        try:
            response = self.session.get(STANDINGS_ENDPOINT, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching standings for {season} {season_type}: {str(e)}")
            return {"resultSets": [{"rowSet": []}]}

def create_team_data(team: Dict, season: str, season_type: str, fetcher: NBADataFetcher, player_stats_lookup: dict) -> Dict:
    """Create comprehensive team data including player stats"""
    team_id = str(team[0])  # TEAM_ID
    team_name = team[3]  # TEAM_NAME
    team_abbr = team[4]  # TEAM_ABBREVIATION
    
    # Get roster
    roster_data = fetcher.get_team_roster(team_id, season)
    
    team_data = {
        "team_id": team_id,
        "team_name": team_name,
        "team_abbreviation": team_abbr,
        "season": season,
        "season_type": season_type,
        "standings": {
            "wins": team[15],  # WINS
            "losses": team[16],  # LOSSES
            "win_pct": team[17],  # WIN_PCT
            "conference_rank": team[11],  # CONF_RANK
            "division_rank": team[12],  # DIV_RANK
            "home_wins": team[18],  # HOME_WINS
            "home_losses": team[19],  # HOME_LOSSES
            "away_wins": team[20],  # AWAY_WINS
            "away_losses": team[21],  # AWAY_LOSSES
            "last_ten_wins": team[22],  # L10_WINS
            "last_ten_losses": team[23],  # L10_LOSSES
            "streak": team[24]  # STREAK
        },
        "players": []
    }
    
    # Get player stats from the lookup
    for player in roster_data.get('resultSets', [])[0].get('rowSet', []):
        player_id = str(player[2])  # PLAYER_ID
        player_name = player[3]  # PLAYER
        player_stats = player_stats_lookup.get(player_id)
        if player_stats:
            player_data = {
                "player_id": player_id,
                "player_name": player_name,
                "position": player[5],  # POSITION
                "jersey_number": player[4],  # NUMBER
                "stats": {
                    "games_played": player_stats[3],  # GP
                    "minutes": player_stats[8],  # MIN
                    "points": player_stats[24],  # PTS
                    "rebounds": player_stats[18],  # REB
                    "assists": player_stats[19],  # AST
                    "steals": player_stats[20],  # STL
                    "blocks": player_stats[21],  # BLK
                    "turnovers": player_stats[22],  # TOV
                    "field_goal_pct": player_stats[10],  # FG_PCT
                    "three_point_pct": player_stats[13],  # FG3_PCT
                    "free_throw_pct": player_stats[16],  # FT_PCT
                    "plus_minus": player_stats[23]  # PLUS_MINUS
                }
            }
            team_data["players"].append(player_data)
        # else: skip players with no stats
        time.sleep(0.1)
    return team_data

def main():
    # Create data directory structure
    base_dir = Path("data/basketball")
    seasons = ["2023", "2024"]
    season_types = ["Regular Season", "Playoffs"]
    
    for season in seasons:
        for season_type in season_types:
            # Create directory for season type
            season_dir = base_dir / season / season_type.replace(" ", "_")
            season_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize data fetcher
            fetcher = NBADataFetcher()
            
            # Get all teams
            teams_data = fetcher.get_teams(season, season_type)
            
            # Get all player stats once and build lookup
            all_player_stats = fetcher.get_player_stats(season, season_type)
            player_stats_lookup = {}
            for stat in all_player_stats.get('resultSets', [])[0].get('rowSet', []):
                player_stats_lookup[str(stat[0])] = stat
            
            # Process each team
            for team in teams_data.get('resultSets', [])[0].get('rowSet', []):
                try:
                    team_id = str(team[0])
                    team_name = team[3]
                    team_abbr = team[4]
                    logger.info(f"Processing {team_name} ({season_type})...")
                    team_data = create_team_data(team, season, season_type, fetcher, player_stats_lookup)
                    # Save team data
                    output_file = season_dir / f"{team_abbr}.json"
                    with open(output_file, 'w') as f:
                        json.dump(team_data, f, indent=2)
                    logger.info(f"Saved data for {team_name} to {output_file}")
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Error processing {team[3]}: {str(e)}")
                    continue

if __name__ == "__main__":
    main() 