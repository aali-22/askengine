"""
AskEngine Core Module
--------------------

This module provides the core functionality for parsing and routing sports queries
across different sports domains (soccer, baseball, basketball).

Main components:
- QueryParser: Handles natural language processing of sports queries
- QueryEntity: Represents extracted entities from queries
- QueryIntent: Represents the structured intent of a query
"""

from .query_parser import QueryParser, QueryEntity, QueryIntent

__version__ = "0.1.0"
__all__ = ["QueryParser", "QueryEntity", "QueryIntent"] 