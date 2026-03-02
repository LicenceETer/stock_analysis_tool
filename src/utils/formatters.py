"""Data formatting utilities for A-Share MCP Agent."""

from typing import Any, Dict, List, Optional


def format_stock_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Format raw stock data into standardized structure.
    
    Args:
        data: Raw stock data from AKShare or other sources
        
    Returns:
        Formatted stock data with consistent field names
    """
    return {
        "symbol": data.get("symbol", ""),
        "name": data.get("name", ""),
        "price": float(data.get("price", 0)),
        "change": float(data.get("change", 0)),
        "change_percent": float(data.get("change_percent", 0)),
        "open": float(data.get("open", 0)),
        "high": float(data.get("high", 0)),
        "low": float(data.get("low", 0)),
        "close": float(data.get("close", 0)),
        "volume": int(data.get("volume", 0)),
        "amount": float(data.get("amount", 0)),
        "turnover_rate": float(data.get("turnover_rate", 0)),
        "market_cap": float(data.get("market_cap", 0)),
        "pe_ratio": float(data.get("pe_ratio", 0)),
        "pb_ratio": float(data.get("pb_ratio", 0)),
    }


def format_news_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """Format news item into standardized structure.
    
    Args:
        item: Raw news data
        
    Returns:
        Formatted news item with consistent fields
    """
    return {
        "title": item.get("title", ""),
        "summary": item.get("summary", ""),
        "url": item.get("url", ""),
        "source": item.get("source", ""),
        "publish_time": item.get("publish_time", ""),
        "sentiment": item.get("sentiment", "neutral"),
    }


def format_analysis_report(
    stock_data: Dict[str, Any], 
    news_items: List[Dict[str, Any]], 
    technical_indicators: Dict[str, Any]
) -> Dict[str, Any]:
    """Format comprehensive analysis report.
    
    Args:
        stock_data: Formatted stock data
        news_items: List of formatted news items
        technical_indicators: Calculated technical indicators
        
    Returns:
        Complete analysis report structure
    """
    return {
        "stock": stock_data,
        "news": news_items[:5],  # Top 5 most relevant news items
        "technical_indicators": technical_indicators,
        "timestamp": technical_indicators.get("timestamp", ""),
    }