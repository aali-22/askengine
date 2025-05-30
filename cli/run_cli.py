"""
CLI interface for testing AskEngine functionality
"""
import sys
import os
import typer
from typing import Optional
from pathlib import Path
import logging

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from askengine_core.query_parser import QueryParser
from askengine_core.data_parser import create_parser, SportDataSource

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = typer.Typer(help="AskEngine CLI - Natural language sports data querying")

@app.command()
def query(
    query_text: str = typer.Argument(..., help="The sports query to process"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed parsing information")
):
    """Process a natural language sports query."""
    try:
        parser = QueryParser()
        
        # Validate query
        if not parser.validate_query(query_text):
            typer.echo(typer.style("Error: Query must contain a sport-related entity and a temporal reference", fg="red"))
            raise typer.Exit(1)
        
        # Route query
        sport = parser.route_query(query_text)
        if sport == "unknown":
            typer.echo(typer.style("Error: Unable to determine sport from query", fg="red"))
            raise typer.Exit(1)
        
        # Parse query
        intent = parser.parse_query(query_text)
        
        if verbose:
            typer.echo(f"\n{typer.style('Query:', fg='blue')} {query_text}")
            typer.echo(f"{typer.style('Sport:', fg='blue')} {sport}")
            typer.echo(f"\n{typer.style('Parsed Intent:', fg='blue')}")
            typer.echo(f"  Action: {intent.action}")
            typer.echo(f"\n{typer.style('Entities:', fg='blue')}")
            for entity in intent.entities:
                typer.echo(f"  - {entity.type}: {entity.value} (confidence: {entity.confidence})")
            if intent.time_range:
                typer.echo(f"\n{typer.style('Time Range:', fg='blue')} {intent.time_range}")
        else:
            typer.echo(f"{typer.style('Sport:', fg='green')} {sport}")
            typer.echo(f"{typer.style('Action:', fg='green')} {intent.action}")
            entities_str = ", ".join(f"{e.type}={e.value}" for e in intent.entities)
            typer.echo(f"{typer.style('Entities:', fg='green')} {entities_str}")
            
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        typer.echo(typer.style(f"Error: {str(e)}", fg="red"))
        raise typer.Exit(1)

@app.command()
def interactive():
    """Start an interactive query session."""
    typer.echo(typer.style("Welcome to AskEngine CLI!", fg="green", bold=True))
    typer.echo("Enter your sports queries (or 'exit' to quit):\n")
    
    parser = QueryParser()
    
    while True:
        try:
            query_text = typer.prompt("Query")
            
            if query_text.lower() in ("exit", "quit"):
                typer.echo(typer.style("\nGoodbye!", fg="green"))
                break
            
            if not parser.validate_query(query_text):
                typer.echo(typer.style("Error: Query must contain a sport-related entity and a temporal reference\n", fg="red"))
                continue
            
            sport = parser.route_query(query_text)
            if sport == "unknown":
                typer.echo(typer.style("Error: Unable to determine sport from query\n", fg="red"))
                continue
            
            intent = parser.parse_query(query_text)
            
            typer.echo(f"\n{typer.style('Sport:', fg='green')} {sport}")
            typer.echo(f"{typer.style('Action:', fg='green')} {intent.action}")
            for entity in intent.entities:
                typer.echo(f"{typer.style('Entity:', fg='green')} ({entity.type}) {entity.value}")
            if intent.time_range:
                typer.echo(f"{typer.style('Time Range:', fg='green')} {intent.time_range}")
            typer.echo("")
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            typer.echo(typer.style(f"Error: {str(e)}\n", fg="red"))

@app.command()
def parse_data(
    sport: str = typer.Argument(..., help="Sport type (football, baseball, basketball)"),
    source_url: str = typer.Argument(..., help="URL of the data source"),
    data_type: str = typer.Option("player_stats", help="Type of data to parse"),
    season: str = typer.Option("2023", help="Season to parse data for"),
    output: Optional[str] = typer.Option(None, help="Output file name")
):
    """Parse sports data from a given source"""
    try:
        # Create data source config
        source = SportDataSource(
            name=f"{sport}_{data_type}",
            url=source_url,
            sport_type=sport,
            season=season,
            data_type=data_type
        )
        
        # Get appropriate parser
        data_dir = Path(__file__).parent.parent / sport / "data"
        parser = create_parser(sport, data_dir)
        
        # Parse data
        typer.echo(f"{typer.style('Parsing data...', fg='blue')}")
        df = parser.parse(source)
        
        # Validate
        if not parser.validate(df):
            typer.echo(typer.style("Warning: Parsed data does not match expected schema", fg="yellow"))
            
        # Save if output specified
        if output:
            parser.save(df, output)
            typer.echo(f"{typer.style('Success:', fg='green')} Data saved to {output}")
        
        # Print summary
        typer.echo(f"\n{typer.style('Summary:', fg='blue')}")
        typer.echo(f"Records parsed: {len(df)}")
        typer.echo(f"\n{typer.style('Sample data:', fg='blue')}")
        typer.echo(df.head())
        
    except Exception as e:
        logger.error(f"Error parsing data: {str(e)}")
        typer.echo(typer.style(f"Error: {str(e)}", fg="red"))
        raise typer.Exit(1)

@app.command()
def list_sources():
    """List supported data sources for each sport"""
    sources = {
        "football": [
            "La Liga",
            "English Premier League",
            "UEFA Champions League",
            "FIFA World Cup",
            "UEFA Euro"
        ],
        "baseball": ["MLB"],
        "basketball": ["NBA"]
    }
    
    typer.echo(f"\n{typer.style('Supported Data Sources:', fg='blue', bold=True)}")
    for sport, leagues in sources.items():
        typer.echo(f"\n{typer.style(sport.title(), fg='green', bold=True)}:")
        for league in leagues:
            typer.echo(f"  • {league}")

if __name__ == "__main__":
    app() 