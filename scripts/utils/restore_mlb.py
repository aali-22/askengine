import os
import json
from pathlib import Path
import shutil
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MLB_DIR = Path("data/baseball")

# Map of team_id to team abbreviation and name
TEAM_INFO = {
    "108": {"abbr": "laa", "name": "Los Angeles Angels"},
    "109": {"abbr": "ari", "name": "Arizona Diamondbacks"},
    "110": {"abbr": "bal", "name": "Baltimore Orioles"},
    "111": {"abbr": "bos", "name": "Boston Red Sox"},
    "112": {"abbr": "chc", "name": "Chicago Cubs"},
    "113": {"abbr": "cin", "name": "Cincinnati Reds"},
    "114": {"abbr": "cle", "name": "Cleveland Guardians"},
    "115": {"abbr": "col", "name": "Colorado Rockies"},
    "116": {"abbr": "det", "name": "Detroit Tigers"},
    "117": {"abbr": "hou", "name": "Houston Astros"},
    "118": {"abbr": "kc", "name": "Kansas City Royals"},
    "119": {"abbr": "lad", "name": "Los Angeles Dodgers"},
    "120": {"abbr": "wsh", "name": "Washington Nationals"},
    "121": {"abbr": "nym", "name": "New York Mets"},
    "133": {"abbr": "oak", "name": "Oakland Athletics"},
    "134": {"abbr": "pit", "name": "Pittsburgh Pirates"},
    "135": {"abbr": "sd", "name": "San Diego Padres"},
    "136": {"abbr": "sea", "name": "Seattle Mariners"},
    "137": {"abbr": "sf", "name": "San Francisco Giants"},
    "138": {"abbr": "stl", "name": "St. Louis Cardinals"},
    "139": {"abbr": "tb", "name": "Tampa Bay Rays"},
    "140": {"abbr": "tex", "name": "Texas Rangers"},
    "141": {"abbr": "tor", "name": "Toronto Blue Jays"},
    "142": {"abbr": "min", "name": "Minnesota Twins"},
    "143": {"abbr": "phi", "name": "Philadelphia Phillies"},
    "144": {"abbr": "atl", "name": "Atlanta Braves"},
    "145": {"abbr": "cws", "name": "Chicago White Sox"},
    "146": {"abbr": "mia", "name": "Miami Marlins"},
    "147": {"abbr": "nyy", "name": "New York Yankees"},
    "158": {"abbr": "mil", "name": "Milwaukee Brewers"}
}

def fix_season(season_dir: Path):
    # Clean up leftover files
    for leftover in season_dir.glob("roster_*.json"):
        leftover.unlink()
        logger.info(f"Removed {leftover}")
    none_file = season_dir / "player_None.json"
    if none_file.exists():
        none_file.unlink()
        logger.info(f"Removed {none_file}")

    # For each team file, update team_name and rename to abbr.json if needed
    for team_file in season_dir.glob("*.json"):
        if team_file.name in ("league_stats.json", "standings.json"):
            continue
        # Read the file and get team_id
        with open(team_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        team_id = str(data.get("team_id"))
        team_info = TEAM_INFO.get(team_id)
        if team_info:
            abbr = team_info["abbr"]
            team_name = team_info["name"]
            # Update team_name
            data["team_name"] = team_name
            # Write back to file (possibly with new name)
            new_file = season_dir / f"{abbr}.json"
            with open(new_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            if new_file != team_file:
                team_file.unlink()
                logger.info(f"Renamed {team_file} to {new_file}")
            else:
                logger.info(f"Updated team name in {new_file}")
        else:
            logger.warning(f"Unknown team ID {team_id} in {team_file}")

def main():
    for season_dir in MLB_DIR.iterdir():
        if season_dir.is_dir() and season_dir.name.isdigit():
            logger.info(f"Fixing MLB team files for season {season_dir.name}")
            fix_season(season_dir)

if __name__ == "__main__":
    main() 