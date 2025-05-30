import pytest
from askengine_core.query_parser import QueryParser

@pytest.fixture
def parser():
    return QueryParser()

def test_validate_query(parser):
    # Valid queries
    assert parser.validate_query("Who had the most goals in La Liga 2014?")
    assert parser.validate_query("Top 10 WAR leaders in MLB 2001")
    assert parser.validate_query("Which NBA player had the highest PPG in 2022?")
    
    # Invalid queries (no temporal reference)
    assert not parser.validate_query("Who has the most goals in La Liga?")
    assert not parser.validate_query("Best NBA players")
    
    # Invalid queries (no sport entity)
    assert not parser.validate_query("What happened in 2014?")
    assert not parser.validate_query("Top performers of 2022")

def test_route_query(parser):
    # Soccer queries
    assert parser.route_query("Who scored most goals in La Liga 2014?") == "soccer"
    assert parser.route_query("Best EPL assists 2023") == "soccer"
    
    # Baseball queries
    assert parser.route_query("Highest WAR in MLB 2020") == "baseball"
    assert parser.route_query("MLB HR leaders 2019") == "baseball"
    
    # Basketball queries
    assert parser.route_query("NBA PPG leaders 2022") == "basketball"
    assert parser.route_query("Best FG% in NBA 2021") == "basketball"
    
    # Unknown queries
    assert parser.route_query("Sports events in 2014") == "unknown"

def test_parse_query(parser):
    # Test soccer query
    query = "Who had the most goals in La Liga 2014?"
    intent = parser.parse_query(query)
    assert intent.action == "get_ranking"
    assert any(e.type == "league" and e.value == "La Liga" for e in intent.entities)
    assert any(e.type == "stat" and e.value == "goals" for e in intent.entities)
    assert intent.time_range == {"year": 2014}
    
    # Test baseball query
    query = "Top 10 WAR leaders in MLB 2001"
    intent = parser.parse_query(query)
    assert intent.action == "get_ranking"
    assert any(e.type == "league" and e.value == "MLB" for e in intent.entities)
    assert any(e.type == "stat" and e.value == "WAR" for e in intent.entities)
    assert intent.time_range == {"year": 2001}
    
    # Test basketball query
    query = "Which NBA player had the highest PPG in 2022?"
    intent = parser.parse_query(query)
    assert intent.action == "get_ranking"
    assert any(e.type == "league" and e.value == "NBA" for e in intent.entities)
    assert any(e.type == "stat" and e.value == "PPG" for e in intent.entities)
    assert intent.time_range == {"year": 2022} 