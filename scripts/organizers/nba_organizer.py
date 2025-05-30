import os
import json
from pathlib import Path
from collections import defaultdict
import shutil
import logging

def load_json_lines_or_array(filepath):
    """Load a file as JSON-lines or as a JSON array/object."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            first = f.read(1)
            f.seek(0)
            if first == '{' or first == '[':
                data = json.load(f)
                if isinstance(data, dict):
                    return [data]
                return data
            else:
                # JSON-lines
                return [json.loads(line) for line in f if line.strip()]
    except Exception as e:
        logger.error(f"Failed to load {filepath}: {e}")
        return []

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NBADataOrganizer:
    def __init__(self, base_dir="data/basketball"):
        self.base_dir = Path(base_dir)
        self.teams_dir = "teams"
        self.players_dir = "players"
        self.league_dir = "league"

    def create_directory_structure(self, season):
        season_path = self.base_dir / season
        for subdir in [self.teams_dir, self.players_dir, self.league_dir]:
            (season_path / subdir).mkdir(parents=True, exist_ok=True)

    def organize_season(self, season):
        logger.info(f"Organizing NBA data for season {season}")
        season_dir = self.base_dir / season
        self.create_directory_structure(season)

        # --- Organize players.json ---
        players_by_team = defaultdict(list)
        players_path = season_dir / "players.json"
        if players_path.exists():
            players = load_json_lines_or_array(players_path)
            for player in players:
                team = player.get("team")
                players_by_team[team].append(player)
                # Write player file
                player_file = season_dir / self.players_dir / f"{player['player_name'].replace(' ', '_')}.json"
                with open(player_file, "w", encoding="utf-8") as pf:
                    json.dump(player, pf, indent=2)

        # --- Organize teams.json ---
        teams_path = season_dir / "teams.json"
        if teams_path.exists():
            teams = load_json_lines_or_array(teams_path)
            for team in teams:
                team_id = team.get("team_id")
                team_abbr = team.get("team_name")
                # Find players for this team
                team_players = players_by_team.get(team_abbr, [])
                team_data = team.copy()
                team_data["players"] = team_players
                # Write team file
                team_file = season_dir / self.teams_dir / f"{team_id}.json"
                with open(team_file, "w", encoding="utf-8") as tf:
                    json.dump(team_data, tf, indent=2)

        # --- Move league-wide files ---
        for fname in ["players.json", "teams.json", "standings.json"]:
            fpath = season_dir / fname
            if fpath.exists():
                shutil.move(str(fpath), str(season_dir / self.league_dir / fname))

    def organize_all_seasons(self):
        for season_dir in self.base_dir.iterdir():
            if season_dir.is_dir() and season_dir.name.isdigit():
                self.organize_season(season_dir.name)

def main():
    organizer = NBADataOrganizer()
    organizer.organize_all_seasons()

if __name__ == "__main__":
    main() 