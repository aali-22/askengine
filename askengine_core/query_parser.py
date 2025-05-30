from typing import Dict, List, Optional, Union
from pydantic import BaseModel
import spacy
from datetime import datetime

class QueryEntity(BaseModel):
    """Entity extracted from a sports query."""
    type: str  # 'stat', 'league', 'year', 'player', 'team'
    value: str
    confidence: float

class QueryIntent(BaseModel):
    """The interpreted intent of a sports query."""
    action: str  # 'get_stat', 'get_ranking', 'compare'
    entities: List[QueryEntity]
    time_range: Optional[Dict[str, Union[str, int]]] = None

class QueryParser:
    def __init__(self):
        """Initialize the query parser with NLP models."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Download if not available
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        # Sports-specific entities
        self.sports_entities = {
            "leagues": {
                "soccer": ["La Liga", "EPL", "Premier League", "Champions League", "UCL"],
                "baseball": ["MLB"],
                "basketball": ["NBA"]
            },
            "stats": {
                "soccer": ["goals", "assists", "clean sheets"],
                "baseball": ["HR", "RBI", "AVG", "OBP", "WAR"],
                "basketball": ["PPG", "rebounds", "assists", "FG%"]
            }
        }

    def parse_query(self, query: str) -> QueryIntent:
        """Parse a natural language sports query into structured intent."""
        # Process with spaCy
        doc = self.nlp(query.lower())
        
        # Extract entities
        entities = []
        
        # Look for years
        years = [token.text for token in doc if token.like_num and len(token.text) == 4]
        if years:
            entities.append(QueryEntity(
                type="year",
                value=years[0],
                confidence=1.0
            ))
        
        # Look for leagues
        for sport, leagues in self.sports_entities["leagues"].items():
            for league in leagues:
                if league.lower() in query.lower():
                    entities.append(QueryEntity(
                        type="league",
                        value=league,
                        confidence=1.0
                    ))
        
        # Look for stats
        for sport, stats in self.sports_entities["stats"].items():
            for stat in stats:
                if stat.lower() in query.lower():
                    entities.append(QueryEntity(
                        type="stat",
                        value=stat,
                        confidence=1.0
                    ))
        
        # Determine action
        action = "get_stat"  # default
        if any(word in query.lower() for word in ["most", "highest", "best", "top"]):
            action = "get_ranking"
        elif any(word in query.lower() for word in ["compare", "vs", "versus"]):
            action = "compare"
        
        return QueryIntent(
            action=action,
            entities=entities,
            time_range={"year": int(years[0])} if years else None
        )

    def validate_query(self, query: str) -> bool:
        """Validate if a query can be processed."""
        # Must have at least one sport-related entity
        doc = self.nlp(query.lower())
        
        has_sport_entity = False
        for sport_entities in self.sports_entities.values():
            for entity_list in sport_entities.values():
                if any(entity.lower() in query.lower() for entity in entity_list):
                    has_sport_entity = True
                    break
        
        # Must have a year or temporal reference
        has_temporal = False
        years = [token.text for token in doc if token.like_num and len(token.text) == 4]
        if years or any(word in query.lower() for word in ["season", "year", "current"]):
            has_temporal = True
        
        return has_sport_entity and has_temporal

    def route_query(self, query: str) -> str:
        """Route query to appropriate sport-specific module."""
        query_lower = query.lower()
        
        # Check each sport's entities
        for sport, leagues in self.sports_entities["leagues"].items():
            if any(league.lower() in query_lower for league in leagues):
                return sport
            
        # If no league mentioned, try to infer from stats
        for sport, stats in self.sports_entities["stats"].items():
            if any(stat.lower() in query_lower for stat in stats):
                return sport
        
        return "unknown" 