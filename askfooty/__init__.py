"""
AskFooty - Football data analysis and query module
Part of the AskEngine sports intelligence system
"""

from pathlib import Path

# Module configuration
MODULE_NAME = "askfooty"
DATA_DIR = Path(__file__).parent / "data"
SUPPORTED_LEAGUES = [
    "La Liga",
    "English Premier League",
    "UEFA Champions League",
    "FIFA World Cup",
    "UEFA Euro"
]

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True) 