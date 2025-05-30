"""
CLI interface for testing AskEngine functionality
"""
import sys
import os
import typer
from typing import Optional
from pathlib import Path

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from askengine_core.query_parser import QueryParser
from askengine_core.data_parser import create_parser, SportDataSource

app = typer.Typer()

@app.command()
def query(
    query_text: str = typer.Argument(..., help="The sports query to process"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed parsing information")
):
    """Process a natural language sports query."""
    parser = QueryParser()
    
    # Validate query
    if not parser.validate_query(query_text):
        typer.echo("Error: Query must contain a sport-related entity and a temporal reference")
        raise typer.Exit(1)
    
    # Route query
    sport = parser.route_query(query_text)
    if sport == "unknown":
        typer.echo("Error: Unable to determine sport from query")
        raise typer.Exit(1)
    
    # Parse query
    intent = parser.parse_query(query_text)
    
    if verbose:
        typer.echo(f"\nQuery: {query_text}")
        typer.echo(f"Sport: {sport}")
        typer.echo("\nParsed Intent:")
        typer.echo(f"  Action: {intent.action}")
        typer.echo("\nEntities:")
        for entity in intent.entities:
            typer.echo(f"  - {entity.type}: {entity.value} (confidence: {entity.confidence})")
        if intent.time_range:
            typer.echo(f"\nTime Range: {intent.time_range}")
    else:
        typer.echo(f"Sport: {sport}")
        typer.echo(f"Action: {intent.action}")
        entities_str = ", ".join(f"{e.type}={e.value}" for e in intent.entities)
        typer.echo(f"Entities: {entities_str}")

@app.command()
def interactive():
    """Start an interactive query session."""
    typer.echo("Welcome to AskEngine CLI!")
    typer.echo("Enter your sports queries (or 'exit' to quit):\n")
    
    parser = QueryParser()
    
    while True:
        query_text = typer.prompt("Query")
        
        if query_text.lower() in ("exit", "quit"):
            break
        
        if not parser.validate_query(query_text):
            typer.echo("Error: Query must contain a sport-related entity and a temporal reference\n")
            continue
        
        sport = parser.route_query(query_text)
        if sport == "unknown":
            typer.echo("Error: Unable to determine sport from query\n")
            continue
        
        intent = parser.parse_query(query_text)
        
        typer.echo(f"\nSport: {sport}")
        typer.echo(f"Action: {intent.action}")
        for entity in intent.entities:
            typer.echo(f"Entity ({entity.type}): {entity.value}")
        if intent.time_range:
            typer.echo(f"Time Range: {intent.time_range}")
        typer.echo("")

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
        df = parser.parse(source)
        
        # Validate
        if not parser.validate(df):
            typer.echo("Warning: Parsed data does not match expected schema")
            
        # Save if output specified
        if output:
            parser.save(df, output)
            typer.echo(f"Data saved to {output}")
        
        # Print summary
        typer.echo(f"\nParsed {len(df)} records")
        typer.echo("\nSample data:")
        typer.echo(df.head())
        
    except Exception as e:
        typer.echo(f"Error: {str(e)}", err=True)
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
    
    for sport, leagues in sources.items():
        typer.echo(f"\n{sport.title()}:")
        for league in leagues:
            typer.echo(f"  - {league}")

if __name__ == "__main__":
    app() 