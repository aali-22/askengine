"""
Data parser module for AskEngine.
Handles parsing and standardization of sports data from various sources.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
from pathlib import Path
import json
import pandas as pd
from pydantic import BaseModel
import time

from .data_fetcher import BaseballDataFetcher, BasketballDataFetcher

class SportDataSource(BaseModel):
    """Base model for sport data sources"""
    name: str
    url: str
    sport_type: str
    season: str
    data_type: str  # e.g., 'player_stats', 'team_stats'

class DataParserBase(ABC):
    """Abstract base class for all data parsers"""
    
    def __init__(self, data_dir: Union[str, Path]):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    @abstractmethod
    def parse(self, source: SportDataSource) -> pd.DataFrame:
        """Parse data from source into standardized format"""
        pass
    
    @abstractmethod
    def validate(self, df: pd.DataFrame) -> bool:
        """Validate parsed data meets schema requirements"""
        pass
    
    def save(self, df: pd.DataFrame, filename: str):
        """Save parsed data to file"""
        output_path = self.data_dir / filename
        df.to_json(output_path, orient='records', lines=True)
        
    def load(self, filename: str) -> pd.DataFrame:
        """Load parsed data from file"""
        input_path = self.data_dir / filename
        return pd.read_json(input_path, orient='records', lines=True)

class BaseballDataParser(DataParserBase):
    """Parser for baseball data"""
    
    def __init__(self, data_dir: Union[str, Path]):
        super().__init__(data_dir)
        self.fetcher = BaseballDataFetcher(data_dir / "baseball" / "cache")
        self.required_columns = {
            'player_stats': ['player_id', 'player_name', 'team_id', 'team_name', 'hr', 'avg', 'obp', 'slg', 'rbi', 'season'],
            'team_stats': ['team_id', 'team_name', 'wins', 'losses', 'win_pct', 'season'],
        }
    
    def parse(self, source: SportDataSource) -> pd.DataFrame:
        """Parse baseball data from source (2023 only, team_stats and player_stats)"""
        if source.data_type == "team_stats":
            # Fetch all teams for 2023
            data = self.fetcher.get_teams('2023')
            records = []
            for team in data.get('teams', []):
                record = team.get('record', {}).get('records', [{}])[0] if team.get('record', {}).get('records') else {}
                records.append({
                    'team_id': team['id'],
                    'team_name': team['name'],
                    'wins': record.get('wins', 0),
                    'losses': record.get('losses', 0),
                    'win_pct': record.get('pct', '0.000'),
                    'season': '2023'
                })
            return pd.DataFrame(records)
        elif source.data_type == "player_stats":
            # Fetch all teams for 2023
            data = self.fetcher.get_teams('2023')
            player_records = []
            for team in data.get('teams', []):
                team_id = team['id']
                team_name = team['name']
                try:
                    # Get roster for this team
                    roster_data = self.fetcher.get_roster(str(team_id), '2023')
                    for player in roster_data.get('roster', []):
                        try:
                            player_id = player['person']['id']
                            player_name = player['person']['fullName']
                            # Get player stats
                            stats_data = self.fetcher.get_player_stats(str(player_id), '2023')
                            if stats_data.get('stats'):
                                for split in stats_data['stats'][0].get('splits', []):
                                    stat = split.get('stat', {})
                                    player_records.append({
                                        'player_id': player_id,
                                        'player_name': player_name,
                                        'team_id': team_id,
                                        'team_name': team_name,
                                        'hr': stat.get('homeRuns', 0),
                                        'avg': stat.get('avg', '.000'),
                                        'obp': stat.get('obp', '.000'),
                                        'slg': stat.get('slg', '.000'),
                                        'rbi': stat.get('rbi', 0),
                                        'season': '2023'
                                    })
                        except Exception as e:
                            print(f"Error fetching stats for player {player_name} ({player_id}): {str(e)}")
                            continue
                except Exception as e:
                    print(f"Error fetching roster for team {team_name} ({team_id}): {str(e)}")
                    continue
                time.sleep(0.5)  # Rate limiting between teams
            return pd.DataFrame(player_records)
        else:
            raise ValueError(f"Unsupported data type: {source.data_type}")
    
    def validate(self, df: pd.DataFrame) -> bool:
        """Validate baseball data schema"""
        if df.empty:
            return False
        required_cols = self.required_columns.get(df.attrs.get('data_type', 'player_stats'))
        return all(col in df.columns for col in required_cols)

class BasketballDataParser(DataParserBase):
    """Parser for basketball data"""
    
    def __init__(self, data_dir: Union[str, Path]):
        super().__init__(data_dir)
        self.fetcher = BasketballDataFetcher(data_dir / "basketball" / "cache")
        self.required_columns = {
            'player_stats': ['player_name', 'team_name', 'ppg', 'rebounds', 'fg_pct', 'fg3_pct', 'season'],
            'team_stats': ['team_id', 'team_name', 'wins', 'losses', 'win_pct', 'season'],
        }
    
    def parse(self, source: SportDataSource) -> pd.DataFrame:
        """Parse basketball data from source (2023 only, team_stats and player_stats)"""
        if source.data_type == "team_stats":
            data = self.fetcher.get_teams('2023')
            if not data.get('resultSets'):
                raise ValueError("Invalid NBA API response format")
                
            result_set = data['resultSets'][0]
            headers = result_set.get('headers', [])
            rows = result_set.get('rowSet', [])
            
            # Map column indices
            try:
                team_id_idx = headers.index('TEAM_ID')
                team_name_idx = headers.index('TEAM_NAME')
                wins_idx = headers.index('W')
                losses_idx = headers.index('L')
                win_pct_idx = headers.index('W_PCT')
            except ValueError as e:
                raise ValueError(f"Missing required column in NBA API response: {str(e)}")
            
            records = []
            for row in rows:
                try:
                    records.append({
                        'team_id': row[team_id_idx],
                        'team_name': row[team_name_idx],
                        'wins': row[wins_idx],
                        'losses': row[losses_idx],
                        'win_pct': row[win_pct_idx],
                        'season': '2023'
                    })
                except IndexError:
                    print(f"Skipping invalid row in NBA API response: {row}")
                    continue
            
            return pd.DataFrame(records)
        elif source.data_type == "player_stats":
            data = self.fetcher.get_players('2023')
            if not data.get('resultSets'):
                raise ValueError("Invalid NBA API response format")
                
            result_set = data['resultSets'][0]
            headers = result_set.get('headers', [])
            rows = result_set.get('rowSet', [])
            
            # Map column indices
            try:
                player_name_idx = headers.index('PLAYER_NAME')
                team_name_idx = headers.index('TEAM_NAME')
                ppg_idx = headers.index('PTS')
                rebounds_idx = headers.index('REB')
                fg_pct_idx = headers.index('FG_PCT')
                fg3_pct_idx = headers.index('FG3_PCT')
            except ValueError as e:
                raise ValueError(f"Missing required column in NBA API response: {str(e)}")
            
            records = []
            for row in rows:
                try:
                    records.append({
                        'player_name': row[player_name_idx],
                        'team_name': row[team_name_idx],
                        'ppg': row[ppg_idx],
                        'rebounds': row[rebounds_idx],
                        'fg_pct': row[fg_pct_idx],
                        'fg3_pct': row[fg3_pct_idx],
                        'season': '2023'
                    })
                except IndexError:
                    print(f"Skipping invalid row in NBA API response: {row}")
                    continue
            
            return pd.DataFrame(records)
        else:
            raise ValueError(f"Unsupported data type: {source.data_type}")
    
    def validate(self, df: pd.DataFrame) -> bool:
        """Validate basketball data schema"""
        if df.empty:
            return False
        required_cols = self.required_columns.get(df.attrs.get('data_type', 'player_stats'))
        return all(col in df.columns for col in required_cols)

# Factory for creating appropriate parser based on sport type
def create_parser(sport_type: str, data_dir: Union[str, Path], api_key: Optional[str] = None) -> DataParserBase:
    """Factory function to create appropriate parser for given sport"""
    parsers = {
        'baseball': lambda d: BaseballDataParser(d),
        'basketball': lambda d: BasketballDataParser(d)
    }
    
    if sport_type not in parsers:
        raise ValueError(f"Unsupported sport type: {sport_type}")
        
    return parsers[sport_type](data_dir) 