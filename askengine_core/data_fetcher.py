"""
Data fetching utilities for AskEngine.
Handles API requests, rate limiting, and caching.
"""
import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# MLB API configuration
MLB_BASE_URL = "https://statsapi.mlb.com/api/v1"
TEAM_ENDPOINT = f"{MLB_BASE_URL}/teams"
ROSTER_ENDPOINT = f"{MLB_BASE_URL}/teams/{{team_id}}/roster/Active"
PLAYER_STATS_ENDPOINT = f"{MLB_BASE_URL}/people/{{player_id}}/stats?stats=season&group=hitting&season={{year}}&gameType=R"
MLB_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.mlb.com/'
}

# NBA API configuration
NBA_BASE_URL = "https://stats.nba.com/stats"
TEAMS_ENDPOINT = f"{NBA_BASE_URL}/leaguedashteamstats"
PLAYERS_ENDPOINT = f"{NBA_BASE_URL}/leaguedashplayerstats"
NBA_HEADERS = {
    'Host': 'stats.nba.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'x-nba-stats-origin': 'stats',
    'x-nba-stats-token': 'true',
    'Origin': 'https://www.nba.com',
    'Connection': 'keep-alive',
    'Referer': 'https://www.nba.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site'
}

class DataFetcher:
    """Base class for fetching data from APIs with rate limiting and caching"""
    
    def __init__(self, cache_dir: Union[str, Path], rate_limit: float = 1.0):
        """
        Initialize fetcher
        
        Args:
            cache_dir: Directory to store cached responses
            rate_limit: Minimum time between requests in seconds
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.rate_limit = rate_limit
        self.last_request_time = 0
        
        # Configure session with retries
        self.session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[408, 429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD", "OPTIONS"]
        )
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
    
    def _wait_for_rate_limit(self):
        """Ensure we don't exceed rate limit"""
        now = time.time()
        time_since_last = now - self.last_request_time
        if time_since_last < self.rate_limit:
            time.sleep(self.rate_limit - time_since_last)
        self.last_request_time = time.time()
    
    def _get_cache_path(self, url: str, params: Optional[Dict] = None) -> Path:
        """Generate cache file path from URL and params"""
        cache_key = url
        if params:
            cache_key += "_" + "_".join(f"{k}={v}" for k, v in sorted(params.items()))
        return self.cache_dir / f"{hash(cache_key)}.json"
    
    def _load_cache(self, cache_path: Path) -> Optional[Dict]:
        """Load cached response if it exists"""
        if cache_path.exists():
            with cache_path.open('r') as f:
                return json.load(f)
        return None
    
    def _save_cache(self, cache_path: Path, data: Dict):
        """Save response to cache"""
        with cache_path.open('w') as f:
            json.dump(data, f)
    
    def fetch(self, url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None, use_cache: bool = True, verify_ssl: bool = True) -> Dict:
        """
        Fetch data from URL with caching and rate limiting
        
        Args:
            url: API endpoint URL
            params: Query parameters
            headers: Request headers
            use_cache: Whether to use cached response if available
            verify_ssl: Whether to verify SSL certificate
            
        Returns:
            JSON response data
        """
        cache_path = self._get_cache_path(url, params)
        
        # Try cache first
        if use_cache:
            cached = self._load_cache(cache_path)
            if cached is not None:
                return cached
        
        # Make request with rate limiting
        self._wait_for_rate_limit()
        
        try:
            response = self.session.get(url, params=params, headers=headers, verify=verify_ssl, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Cache response
            self._save_cache(cache_path, data)
            
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {str(e)}")
            raise

class BaseballDataFetcher(DataFetcher):
    """Baseball data fetcher using MLB Stats API"""
    
    def __init__(self, cache_dir: Union[str, Path]):
        super().__init__(cache_dir, rate_limit=1.0)
        self.session.headers.update(MLB_HEADERS)
    
    def get_teams(self, season: str) -> Dict:
        """Get list of all MLB teams"""
        params = {
            'season': season,
            'sportId': 1,
            'fields': 'teams,id,name,teamName,abbreviation,record'
        }
        return self.fetch(TEAM_ENDPOINT, params=params)
    
    def get_roster(self, team_id: str, season: str) -> Dict:
        """Get team roster"""
        url = ROSTER_ENDPOINT.format(team_id=team_id)
        params = {'season': season}
        return self.fetch(url, params=params)
    
    def get_player_stats(self, player_id: str, season: str) -> Dict:
        """Get player statistics"""
        url = PLAYER_STATS_ENDPOINT.format(player_id=player_id, year=season)
        return self.fetch(url)

class BasketballDataFetcher(DataFetcher):
    """Basketball data fetcher using NBA Stats API"""
    
    def __init__(self, cache_dir: Union[str, Path]):
        super().__init__(cache_dir, rate_limit=1.0)
        self.session.headers.update(NBA_HEADERS)
    
    def fetch(self, url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None, use_cache: bool = True) -> Dict:
        """Override fetch to disable SSL verification for NBA API"""
        return super().fetch(url, params, headers, use_cache, verify_ssl=False)
    
    def get_teams(self, season: str) -> Dict:
        """Get list of all NBA teams"""
        params = {
            'MeasureType': 'Base',
            'PerMode': 'PerGame',
            'PlusMinus': 'N',
            'PaceAdjust': 'N',
            'Rank': 'N',
            'Season': f'2023-24',
            'SeasonType': 'Regular Season',
            'LastNGames': 0,
            'Conference': '',
            'DateFrom': '',
            'DateTo': '',
            'Division': '',
            'GameScope': '',
            'GameSegment': '',
            'LeagueID': '00',
            'Location': '',
            'Month': 0,
            'OpponentTeamID': 0,
            'Outcome': '',
            'Period': 0,
            'PlayerExperience': '',
            'PlayerPosition': '',
            'SeasonSegment': '',
            'ShotClockRange': '',
            'StarterBench': '',
            'TeamID': 0,
            'TwoWay': 0,
            'VsConference': '',
            'VsDivision': ''
        }
        return self.fetch(TEAMS_ENDPOINT, params=params)
    
    def get_players(self, season: str) -> Dict:
        """Get list of all NBA players"""
        params = {
            'MeasureType': 'Base',
            'PerMode': 'PerGame',
            'PlusMinus': 'N',
            'PaceAdjust': 'N',
            'Rank': 'N',
            'Season': f'2023-24',
            'SeasonType': 'Regular Season',
            'LastNGames': 0,
            'Conference': '',
            'DateFrom': '',
            'DateTo': '',
            'Division': '',
            'GameScope': '',
            'GameSegment': '',
            'LeagueID': '00',
            'Location': '',
            'Month': 0,
            'OpponentTeamID': 0,
            'Outcome': '',
            'Period': 0,
            'PlayerExperience': '',
            'PlayerPosition': '',
            'SeasonSegment': '',
            'ShotClockRange': '',
            'StarterBench': '',
            'TeamID': 0,
            'TwoWay': 0,
            'VsConference': '',
            'VsDivision': ''
        }
        return self.fetch(PLAYERS_ENDPOINT, params=params)
    
    def get_team_stats(self, season: str) -> Dict:
        """Get team statistics"""
        return self.get_teams(season)
    
    def get_player_stats(self, season: str) -> Dict:
        """Get player statistics"""
        return self.get_players(season) 