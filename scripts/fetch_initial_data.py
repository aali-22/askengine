"""
Script to fetch initial data for all supported sports and leagues
"""
import os
from pathlib import Path
import typer
from typing import List, Optional
from datetime import datetime
import time

from askengine_core.data_parser import create_parser, SportDataSource

app = typer.Typer()

def fetch_football_data(data_dir: Path, season: str, api_key: Optional[str]):
    """Fetch football data for all supported leagues"""
    parser = create_parser('football', data_dir, api_key)
    
    for league in ["La Liga", "English Premier League", "UEFA Champions League"]:
        typer.echo(f"\nFetching data for {league}...")
        
        # Fetch team stats
        source = SportDataSource(
            name=league,
            url="",  # Not needed for football API
            sport_type="football",
            season=season,
            data_type="team_stats"
        )
        
        try:
            df = parser.parse(source)
            parser.save(df, f"{league.lower().replace(' ', '_')}_{season}_teams.json")
            typer.echo(f"Saved team stats for {league}")
            
            # Fetch matches for each team
            for _, team in df.iterrows():
                team_source = SportDataSource(
                    name=f"{league} - {team['team_name']}",
                    url=team['team_name'],  # Using team name as identifier
                    sport_type="football",
                    season=season,
                    data_type="matches"
                )
                matches_df = parser.parse(team_source)
                parser.save(matches_df, f"{league.lower().replace(' ', '_')}_{season}_matches_{team['team_name'].lower().replace(' ', '_')}.json")
            typer.echo(f"Saved match data for {league}")
            
        except Exception as e:
            typer.echo(f"Error fetching {league} data: {str(e)}", err=True)

def fetch_baseball_data(data_dir: Path, seasons: List[str]):
    """Fetch baseball data for MLB"""
    parser = create_parser('baseball', data_dir)
    
    for season in seasons:
        typer.echo(f"\nFetching MLB data for {season}...")
        
        try:
            # Get team stats first
            typer.echo("Fetching MLB team stats...")
            teams_source = SportDataSource(
                name="MLB",
                url="",
                sport_type="baseball",
                season=season,
                data_type="team_stats"
            )
            teams_df = parser.parse(teams_source)
            output_file = f"mlb_{season}_teams.json"
            parser.save(teams_df, output_file)
            typer.echo(f"Saved MLB team stats to {output_file}")
            
            # For each team, get player stats
            for _, team in teams_df.iterrows():
                team_id = team['team_id']
                typer.echo(f"\nFetching player stats for team {team['team_name']} (ID: {team_id})...")
                # Get player stats
                player_source = SportDataSource(
                    name=f"MLB-{team_id}",
                    url=str(team_id),
                    sport_type="baseball",
                    season=season,
                    data_type="player_stats"
                )
                try:
                    player_df = parser.parse(player_source)
                    if not player_df.empty:
                        output_file = f"mlb_{season}_player_{team_id}.json"
                        parser.save(player_df, output_file)
                        typer.echo(f"Saved MLB stats for team {team['team_name']} players to {output_file}")
                except Exception as e:
                    typer.echo(f"Error fetching players for team {team['team_name']} ({team_id}): {str(e)}", err=True)
                time.sleep(0.5)  # Rate limiting for player requests
            
            time.sleep(1)  # Rate limiting between teams
            
        except Exception as e:
            typer.echo(f"Error fetching MLB data for {season}: {str(e)}", err=True)
            continue

def fetch_basketball_data(data_dir: Path, seasons: List[str]):
    """Fetch basketball data for NBA"""
    parser = create_parser('basketball', data_dir)
    
    for season in seasons:
        typer.echo(f"\nFetching NBA data for {season}...")
        
        try:
            # Fetch team stats first
            typer.echo("Fetching NBA team stats...")
            teams_source = SportDataSource(
                name="NBA",
                url="",
                sport_type="basketball",
                season=season,
                data_type="team_stats"
            )
            df = parser.parse(teams_source)
            output_file = f"nba_{season}_teams.json"
            parser.save(df, output_file)
            typer.echo(f"Saved NBA team stats to {output_file}")
            
            # Fetch player stats
            typer.echo("\nFetching NBA player stats...")
            players_source = SportDataSource(
                name="NBA",
                url="",
                sport_type="basketball",
                season=season,
                data_type="player_stats"
            )
            df = parser.parse(players_source)
            output_file = f"nba_{season}_players.json"
            parser.save(df, output_file)
            typer.echo(f"Saved NBA player stats to {output_file}")
            
            time.sleep(2)  # Rate limiting between seasons
            
        except Exception as e:
            typer.echo(f"Error fetching NBA data for {season}: {str(e)}", err=True)
            continue

@app.command()
def main(
    start_year: int = typer.Option(1999, help="Start year for data fetching"),
    end_year: int = typer.Option(datetime.now().year, help="End year for data fetching"),
    data_dir: Optional[str] = typer.Option(None, help="Base directory for data storage")
):
    """Fetch data for all supported sports and leagues"""
    
    # Use default data directory if not provided
    if not data_dir:
        data_dir = Path(__file__).parent.parent / "data"
    else:
        data_dir = Path(data_dir)
    
    # Create data directories
    data_dir.mkdir(parents=True, exist_ok=True)
    typer.echo(f"Using data directory: {data_dir.absolute()}")
    
    # Generate list of seasons
    seasons = [str(year) for year in range(start_year, end_year + 1)]
    typer.echo(f"Fetching data for seasons {start_year}-{end_year}")
    
    # Fetch baseball data
    fetch_baseball_data(data_dir, seasons)
    
    # Fetch basketball data
    fetch_basketball_data(data_dir, seasons)
    
    typer.echo("\nData fetching complete!")

if __name__ == "__main__":
    app() 