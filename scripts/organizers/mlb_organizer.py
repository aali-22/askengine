import os
import json
from pathlib import Path
import shutil
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

BASE_DIR = Path("data/baseball")


def organize_season(season_dir: Path):
    # Remove teams/ and players/ folders if they exist
    for sub in ["teams", "players"]:
        subdir = season_dir / sub
        if subdir.exists():
            shutil.rmtree(subdir)
            logger.info(f"Removed {subdir}")
    # For each JSON file, ensure it's named by abbreviation and has correct team_name
    for team_file in season_dir.glob("*.json"):
        if team_file.name in ("league_stats.json", "standings.json"):
            continue
        try:
            with open(team_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            team_id = str(data.get("team_id"))
            team_info = TEAM_INFO.get(team_id)
            if team_info:
                abbr = team_info["abbr"]
                team_name = team_info["name"]
                data["team_name"] = team_name
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
        except Exception as e:
            logger.error(f"Error processing {team_file}: {str(e)}")
    # Remove leftover files
    for leftover in season_dir.glob("roster_*.json"):
        leftover.unlink()
        logger.info(f"Removed {leftover}")
    none_file = season_dir / "player_None.json"
    if none_file.exists():
        none_file.unlink()
        logger.info(f"Removed {none_file}")


def main():
    for season_dir in BASE_DIR.iterdir():
        if season_dir.is_dir() and season_dir.name.isdigit():
            logger.info(f"Organizing MLB data for season {season_dir.name}")
            organize_season(season_dir)

if __name__ == "__main__":
    main() 