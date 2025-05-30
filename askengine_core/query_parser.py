"""
Query parser for natural language sports queries
"""
import logging
from typing import Dict, List, Optional, Union
from pydantic import BaseModel
import spacy
from datetime import datetime

logger = logging.getLogger(__name__)

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
            logger.info("Loading spaCy model...")
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Successfully loaded spaCy model")
        except OSError:
            logger.info("Downloading spaCy model...")
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Successfully downloaded and loaded spaCy model")
        
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
        logger.debug("Initialized sports entities")

    def parse_query(self, query: str) -> QueryIntent:
        """
        Parse a natural language sports query into structured intent.
        
        Args:
            query: The natural language query to parse
            
        Returns:
            QueryIntent object containing parsed information
            
        Raises:
            ValueError: If query cannot be parsed
        """
        logger.info(f"Parsing query: {query}")
        
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
            logger.debug(f"Found year entity: {years[0]}")
        
        # Look for leagues
        for sport, leagues in self.sports_entities["leagues"].items():
            for league in leagues:
                if league.lower() in query.lower():
                    entities.append(QueryEntity(
                        type="league",
                        value=league,
                        confidence=1.0
                    ))
                    logger.debug(f"Found league entity: {league}")
        
        # Look for stats
        for sport, stats in self.sports_entities["stats"].items():
            for stat in stats:
                if stat.lower() in query.lower():
                    entities.append(QueryEntity(
                        type="stat",
                        value=stat,
                        confidence=1.0
                    ))
                    logger.debug(f"Found stat entity: {stat}")
        
        if not entities:
            logger.warning("No entities found in query")
            raise ValueError("No entities found in query")
        
        # Determine action
        action = "get_stat"  # default
        if any(word in query.lower() for word in ["most", "highest", "best", "top"]):
            action = "get_ranking"
            logger.debug("Detected ranking action")
        elif any(word in query.lower() for word in ["compare", "vs", "versus"]):
            action = "compare"
            logger.debug("Detected comparison action")
        
        intent = QueryIntent(
            action=action,
            entities=entities,
            time_range={"year": int(years[0])} if years else None
        )
        logger.info(f"Successfully parsed query into intent: {intent}")
        return intent

    def validate_query(self, query: str) -> bool:
        """
        Validate if a query can be processed.
        
        Args:
            query: The query to validate
            
        Returns:
            bool: True if query is valid, False otherwise
        """
        logger.debug(f"Validating query: {query}")
        
        # Must have at least one sport-related entity
        doc = self.nlp(query.lower())
        
        has_sport_entity = False
        for sport_entities in self.sports_entities.values():
            for entity_list in sport_entities.values():
                if any(entity.lower() in query.lower() for entity in entity_list):
                    has_sport_entity = True
                    logger.debug("Found sport entity")
                    break
        
        # Must have a year or temporal reference
        has_temporal = False
        years = [token.text for token in doc if token.like_num and len(token.text) == 4]
        if years or any(word in query.lower() for word in ["season", "year", "current"]):
            has_temporal = True
            logger.debug("Found temporal reference")
        
        is_valid = has_sport_entity and has_temporal
        if not is_valid:
            logger.warning("Query validation failed")
        return is_valid

    def route_query(self, query: str) -> str:
        """
        Route query to appropriate sport-specific module.
        
        Args:
            query: The query to route
            
        Returns:
            str: Sport type or "unknown" if cannot determine
        """
        logger.debug(f"Routing query: {query}")
        query_lower = query.lower()
        
        # Check each sport's entities
        for sport, leagues in self.sports_entities["leagues"].items():
            if any(league.lower() in query_lower for league in leagues):
                logger.info(f"Routed query to {sport}")
                return sport
            
        # If no league mentioned, try to infer from stats
        for sport, stats in self.sports_entities["stats"].items():
            if any(stat.lower() in query_lower for stat in stats):
                logger.info(f"Routed query to {sport} based on stats")
                return sport
        
        logger.warning("Could not determine sport from query")
        return "unknown" 