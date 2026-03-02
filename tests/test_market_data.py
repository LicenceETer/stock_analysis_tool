"""Tests for market data tools."""

import pytest
from src.tools.market_data import get_realtime_quotes, validate_symbol


def test_validate_symbol():
    """Test stock symbol validation."""
    # Valid symbols
    assert validate_symbol("600519") == True  # Shanghai
    assert validate_symbol("000001") == True  # Shenzhen
    assert validate_symbol("300750") == True  # ChiNext
    
    # Invalid symbols
    assert validate_symbol("12345") == False   # Too short
    assert validate_symbol("1234567") == False # Too long
    assert validate_symbol("800000") == False  # Invalid exchange
    assert validate_symbol("") == False        # Empty
    assert validate_symbol(None) == False      # None


@pytest.mark.skip(reason="Requires internet connection and AKShare API")
def test_get_realtime_quotes():
    """Test real-time quotes fetching (requires internet)."""
    # Test with a well-known stock
    result = get_realtime_quotes("600519")
    
    # Basic structure checks
    assert "symbol" in result
    assert "name" in result
    assert "price" in result
    assert "change" in result
    assert "volume" in result
    
    # Value type checks
    assert isinstance(result["symbol"], str)
    assert isinstance(result["name"], str)
    assert isinstance(result["price"], float)
    assert isinstance(result["volume"], int)
    
    # Reasonable value checks
    assert result["price"] > 0
    assert result["volume"] >= 0