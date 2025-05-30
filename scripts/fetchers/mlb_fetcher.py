import os
import json
import time
from pathlib import Path
import requests
from typing import Dict, List, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MLB API configuration
MLB_BASE_URL = "https://statsapi.mlb.com/api/v1"
TEAM_ENDPOINT = f"{MLB_BASE_URL}/teams"
ROSTER_ENDPOINT = f"{MLB_BASE_URL}/teams/{{team_id}}/roster/Active"
PLAYER_HITTING_STATS = f"{MLB_BASE_URL}/people/{{player_id}}/stats?stats=season&group=hitting&season={{year}}&gameType=R"
PLAYER_PITCHING_STATS = f"{MLB_BASE_URL}/people/{{player_id}}/stats?stats=season&group=pitching&season={{year}}&gameType=R"

MLB_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.mlb.com/'
}

class MLBDataFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(MLB_HEADERS)
    
    def get_teams(self, season: str) -> Dict:
        """Get list of all MLB teams"""
        params = {
            'season': season,
            'sportId': 1,
            'fields': 'teams,id,name,teamName,abbreviation'
        }
        response = self.session.get(TEAM_ENDPOINT, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_roster(self, team_id: str, season: str) -> Dict:
        """Get team roster"""
        url = ROSTER_ENDPOINT.format(team_id=team_id)
        params = {'season': season}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_player_hitting_stats(self, player_id: str, season: str) -> Dict:
        """Get player hitting statistics"""
        url = PLAYER_HITTING_STATS.format(player_id=player_id, year=season)
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_player_pitching_stats(self, player_id: str, season: str) -> Dict:
        """Get player pitching statistics"""
        url = PLAYER_PITCHING_STATS.format(player_id=player_id, year=season)
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

def create_team_data(team: Dict, season: str, fetcher: MLBDataFetcher) -> Dict:
    """Create comprehensive team data including both hitting and pitching stats"""
    team_id = team['id']
    team_name = team['name']
    
    # Get roster
    roster_data = fetcher.get_roster(str(team_id), season)
    
    team_data = {
        "team_id": team_id,
        "team_name": team_name,
        "season": season,
        "hitters": [],
        "pitchers": []
    }
    
    for player in roster_data.get('roster', []):
        player_id = player['person']['id']
        player_name = player['person']['fullName']
        position = player['position']['type']
        
        player_data = {
            "player_id": player_id,
            "player_name": player_name,
            "position": position,
            "jersey_number": player['jerseyNumber'],
            "status": player['status']['description']
        }
        
        # Get hitting stats
        try:
            hitting_stats = fetcher.get_player_hitting_stats(str(player_id), season)
            if hitting_stats.get('stats'):
                for split in hitting_stats['stats'][0].get('splits', []):
                    stat = split.get('stat', {})
                    player_data.update({
                        "hitting": {
                            "games": stat.get('gamesPlayed', 0),
                            "at_bats": stat.get('atBats', 0),
                            "runs": stat.get('runs', 0),
                            "hits": stat.get('hits', 0),
                            "doubles": stat.get('doubles', 0),
                            "triples": stat.get('triples', 0),
                            "home_runs": stat.get('homeRuns', 0),
                            "rbi": stat.get('rbi', 0),
                            "avg": stat.get('avg', '.000'),
                            "obp": stat.get('obp', '.000'),
                            "slg": stat.get('slg', '.000'),
                            "ops": stat.get('ops', '.000'),
                            "stolen_bases": stat.get('stolenBases', 0),
                            "caught_stealing": stat.get('caughtStealing', 0),
                            "walks": stat.get('baseOnBalls', 0),
                            "strikeouts": stat.get('strikeOuts', 0)
                        }
                    })
        except Exception as e:
            logger.warning(f"Error fetching hitting stats for {player_name}: {str(e)}")
        
        # Get pitching stats
        try:
            pitching_stats = fetcher.get_player_pitching_stats(str(player_id), season)
            if pitching_stats.get('stats'):
                for split in pitching_stats['stats'][0].get('splits', []):
                    stat = split.get('stat', {})
                    player_data.update({
                        "pitching": {
                            "games": stat.get('gamesPlayed', 0),
                            "games_started": stat.get('gamesStarted', 0),
                            "wins": stat.get('wins', 0),
                            "losses": stat.get('losses', 0),
                            "era": stat.get('era', '0.00'),
                            "innings_pitched": stat.get('inningsPitched', '0.0'),
                            "hits_allowed": stat.get('hits', 0),
                            "runs_allowed": stat.get('runs', 0),
                            "earned_runs": stat.get('earnedRuns', 0),
                            "walks": stat.get('baseOnBalls', 0),
                            "strikeouts": stat.get('strikeOuts', 0),
                            "whip": stat.get('whip', '0.00'),
                            "batting_avg_against": stat.get('battingAvg', '.000')
                        }
                    })
        except Exception as e:
            logger.warning(f"Error fetching pitching stats for {player_name}: {str(e)}")
        
        # Add player to appropriate list
        if position == "Pitcher":
            team_data["pitchers"].append(player_data)
        else:
            team_data["hitters"].append(player_data)
        
        # Rate limiting
        time.sleep(0.5)
    
    return team_data

def main():
    # Create data directory structure
    base_dir = Path("data/baseball")
    
    # Initialize data fetcher
    fetcher = MLBDataFetcher()
    
    # Process seasons from 2010 to 2022
    for season in range(2010, 2023):
        season_str = str(season)
        logger.info(f"Processing season {season_str}...")
        
        season_dir = base_dir / season_str
        season_dir.mkdir(parents=True, exist_ok=True)
        
        # Get all teams
        teams_data = fetcher.get_teams(season_str)
        
        # Process each team
        for team in teams_data.get('teams', []):
            try:
                logger.info(f"Processing {team['name']} for {season_str}...")
                team_data = create_team_data(team, season_str, fetcher)
                
                # Save team data
                output_file = season_dir / f"{team['abbreviation'].lower()}.json"
                with open(output_file, 'w') as f:
                    json.dump(team_data, f, indent=2)
                
                logger.info(f"Saved data for {team['name']} to {output_file}")
                
                # Rate limiting between teams
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing {team['name']} for {season_str}: {str(e)}")
                continue
        
        # Rate limiting between seasons
        time.sleep(2)

if __name__ == "__main__":
    main() 