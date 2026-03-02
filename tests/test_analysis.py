"""Tests for analysis tools."""

import pytest
import pandas as pd
from src.tools.analysis import calculate_technical_indicators, generate_stock_analysis_report


@pytest.mark.skip(reason="Requires internet connection and AKShare API")
def test_calculate_technical_indicators():
    """Test technical indicator calculation (requires internet)."""
    # Test with a well-known stock
    result = calculate_technical_indicators("600519")
    
    # Basic structure checks
    assert "ma5" in result
    assert "ma20" in result
    assert "rsi" in result
    assert "timestamp" in result
    
    # Value type checks
    assert isinstance(result["ma5"], float)
    assert isinstance(result["ma20"], float)
    assert isinstance(result["rsi"], float)
    
    # Reasonable value checks
    assert result["ma5"] > 0
    assert result["ma20"] > 0
    assert 0 <= result["rsi"] <= 100


@pytest.mark.skip(reason="Requires internet connection and multiple APIs")
def test_generate_stock_analysis_report():
    """Test complete analysis report generation (requires internet)."""
    # Test with a well-known stock
    result = generate_stock_analysis_report("600519")
    
    # Basic structure checks
    assert "stock" in result
    assert "news" in result
    assert "technical_indicators" in result
    assert "timestamp" in result
    
    # Stock data checks
    assert "symbol" in result["stock"]
    assert "price" in result["stock"]
    assert "volume" in result["stock"]
    
    # News checks
    assert isinstance(result["news"], list)
    assert len(result["news"]) <= 5
    
    # Technical indicators checks
    assert "ma5" in result["technical_indicators"]
    assert "rsi" in result["technical_indicators"]