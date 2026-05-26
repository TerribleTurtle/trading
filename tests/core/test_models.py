import pytest
from pydantic import ValidationError
from src.shadow_bot.core.models import Market

def test_market_model_validation():
    """Test that the Market model properly parses valid data and calculates derived fields if needed."""
    valid_data = {
        "ticker": "KX-TEST",
        "title": "Test Market",
        "status": "active",
        "close_ts": 1700000000,
        "yes_bid": 0.02,
        "yes_ask": 0.03,
        "no_bid": 0.96,
        "no_ask": 0.98,
        "no_ask_depth": 500,
        "volume": 2000
    }
    
    market = Market(**valid_data)
    
    assert market.ticker == "KX-TEST"
    assert market.no_ask == 0.98
    assert market.no_ask_depth == 500

def test_market_model_invalid_data():
    """Test that the Market model strictly validates types."""
    invalid_data = {
        "ticker": "KX-TEST",
        "title": "Test Market",
        "status": "active",
        "close_ts": 1700000000,
        "yes_bid": "not_a_float",
        "yes_ask": 0.03,
        "no_bid": 0.96,
        "no_ask": 0.98,
        "no_ask_depth": 500,
        "volume": 2000
    }
    
    with pytest.raises(ValidationError):
        Market(**invalid_data)
