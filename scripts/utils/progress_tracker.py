import os
import json
from pathlib import Path
from typing import Dict, List, Set
import logging
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate

class ProgressTracker:
    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)
        self.mlb_path = self.base_path / "baseball"
        self.nba_path = self.base_path / "basketball"
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('progress_tracker.log'),
                logging.StreamHandler()
            ]
        )
        
        # Required files for each season
        self.required_files = {
            "mlb": {
                "team": ["standings.json", "records.json"],
                "league": ["standings.json", "records.json"],
                "players": ["season_stats.json", "playoff_stats.json"]
            },
            "nba": {
                "team": ["standings.json", "records.json"],
                "league": ["standings.json", "records.json"],
                "players": ["season_stats.json", "playoff_stats.json"]
            }
        }
        
        # MLB teams
        self.mlb_teams = {
            "ARI", "ATL", "BAL", "BOS", "CHC", "CHW", "CIN", "CLE", "COL", "DET",
            "HOU", "KCR", "LAA", "LAD", "MIA", "MIL", "MIN", "NYM", "NYY", "OAK",
            "PHI", "PIT", "SDP", "SEA", "SFG", "STL", "TBR", "TEX", "TOR", "WSN"
        }
        
        # NBA teams
        self.nba_teams = {
            "ATL", "BOS", "BKN", "CHA", "CHI", "CLE", "DAL", "DEN", "DET", "GSW",
            "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", "MIN", "NOP", "NYK",
            "OKC", "ORL", "PHI", "PHX", "POR", "SAC", "SAS", "TOR", "UTA", "WAS"
        }

    def check_season_completeness(self, sport: str, year: int) -> Dict:
        """Check completeness of a single season's data."""
        sport_path = self.mlb_path if sport == "mlb" else self.nba_path
        year_path = sport_path / str(year)
        
        if not year_path.exists():
            return {
                "exists": False,
                "completeness": 0.0,
                "missing_files": [],
                "missing_teams": list(self.mlb_teams if sport == "mlb" else self.nba_teams)
            }
        
        total_required = 0
        total_present = 0
        missing_files = []
        missing_teams = []
        
        # Check required files
        for category, files in self.required_files[sport].items():
            category_path = year_path / category
            if not category_path.exists():
                missing_files.extend(files)
                total_required += len(files)
                continue
                
            for file in files:
                total_required += 1
                if (category_path / file).exists():
                    total_present += 1
                else:
                    missing_files.append(f"{category}/{file}")
        
        # Check team files
        teams = self.mlb_teams if sport == "mlb" else self.nba_teams
        for team in teams:
            total_required += 1
            team_file = year_path / f"{team}.json"
            if team_file.exists():
                total_present += 1
            else:
                missing_teams.append(team)
        
        completeness = (total_present / total_required) * 100 if total_required > 0 else 0
        
        return {
            "exists": True,
            "completeness": completeness,
            "missing_files": missing_files,
            "missing_teams": missing_teams
        }

    def generate_progress_report(self, start_year: int = 2010, end_year: int = 2025) -> Dict:
        """Generate a comprehensive progress report."""
        report = {
            "mlb": {},
            "nba": {},
            "summary": {
                "mlb": {"total_completeness": 0.0, "seasons_complete": 0},
                "nba": {"total_completeness": 0.0, "seasons_complete": 0}
            }
        }
        
        for year in range(start_year, end_year + 1):
            report["mlb"][year] = self.check_season_completeness("mlb", year)
            report["nba"][year] = self.check_season_completeness("nba", year)
            
            # Update summary
            if report["mlb"][year]["exists"]:
                report["summary"]["mlb"]["total_completeness"] += report["mlb"][year]["completeness"]
                if report["mlb"][year]["completeness"] == 100:
                    report["summary"]["mlb"]["seasons_complete"] += 1
            
            if report["nba"][year]["exists"]:
                report["summary"]["nba"]["total_completeness"] += report["nba"][year]["completeness"]
                if report["nba"][year]["completeness"] == 100:
                    report["summary"]["nba"]["seasons_complete"] += 1
        
        # Calculate average completeness
        total_seasons = end_year - start_year + 1
        report["summary"]["mlb"]["total_completeness"] /= total_seasons
        report["summary"]["nba"]["total_completeness"] /= total_seasons
        
        return report

    def generate_visual_report(self, report: Dict, output_dir: str = "reports"):
        """Generate visual reports of progress."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Create progress over time plot
        years = list(report["mlb"].keys())
        mlb_completeness = [report["mlb"][year]["completeness"] for year in years]
        nba_completeness = [report["nba"][year]["completeness"] for year in years]
        
        plt.figure(figsize=(12, 6))
        plt.plot(years, mlb_completeness, label='MLB', marker='o')
        plt.plot(years, nba_completeness, label='NBA', marker='o')
        plt.title('Data Collection Progress Over Time')
        plt.xlabel('Year')
        plt.ylabel('Completeness (%)')
        plt.legend()
        plt.grid(True)
        plt.savefig(output_path / 'progress_over_time.png')
        plt.close()
        
        # Create summary table
        summary_data = []
        for year in years:
            summary_data.append([
                year,
                f"{report['mlb'][year]['completeness']:.1f}%",
                f"{report['nba'][year]['completeness']:.1f}%"
            ])
        
        summary_table = tabulate(
            summary_data,
            headers=['Year', 'MLB Completeness', 'NBA Completeness'],
            tablefmt='grid'
        )
        
        with open(output_path / 'summary_table.txt', 'w') as f:
            f.write(summary_table)
        
        # Create detailed report
        with open(output_path / 'detailed_report.txt', 'w') as f:
            f.write("=== Detailed Progress Report ===\n\n")
            
            for sport in ['mlb', 'nba']:
                f.write(f"\n=== {sport.upper()} Progress ===\n")
                f.write(f"Total Completeness: {report['summary'][sport]['total_completeness']:.1f}%\n")
                f.write(f"Complete Seasons: {report['summary'][sport]['seasons_complete']}\n\n")
                
                for year in years:
                    f.write(f"\n{year}:\n")
                    if not report[sport][year]["exists"]:
                        f.write("  No data directory found\n")
                        continue
                    
                    f.write(f"  Completeness: {report[sport][year]['completeness']:.1f}%\n")
                    
                    if report[sport][year]["missing_files"]:
                        f.write("  Missing Files:\n")
                        for file in report[sport][year]["missing_files"]:
                            f.write(f"    - {file}\n")
                    
                    if report[sport][year]["missing_teams"]:
                        f.write("  Missing Teams:\n")
                        for team in report[sport][year]["missing_teams"]:
                            f.write(f"    - {team}\n")

def main():
    tracker = ProgressTracker()
    report = tracker.generate_progress_report()
    tracker.generate_visual_report(report)
    logging.info("Progress report generated successfully")

if __name__ == "__main__":
    main() 