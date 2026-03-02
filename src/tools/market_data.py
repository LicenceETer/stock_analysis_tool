"""Market data fetching tools for A-Share MCP Agent."""

import logging
from typing import Dict, Any, Optional
import akshare as ak
import pandas as pd

logger = logging.getLogger(__name__)


def get_realtime_quotes(symbol: str) -> Dict[str, Any]:
    """Fetch real-time stock quotes for A-share market.
    
    Args:
        symbol: Stock code (e.g., "600519" for 贵州茅台)
        
    Returns:
        Dictionary containing real-time stock data
        
    Raises:
        ValueError: If symbol is invalid or data cannot be retrieved
    """
    import time
    import random
    from .tushare_client import get_realtime_quotes_tushare, TUSHARE_AVAILABLE
    
    try:
        # Validate symbol format
        if not symbol or not isinstance(symbol, str):
            raise ValueError("Invalid symbol format")
            
        # Ensure symbol is in correct format (6 digits)
        symbol = symbol.zfill(6)
        
        # Fetch real-time data using AKShare with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Add delay between retries to avoid rate limiting
                if attempt > 0:
                    delay = random.uniform(1.0, 3.0)
                    time.sleep(delay)
                    logger.info(f"Retry attempt {attempt + 1} for {symbol} after {delay:.1f}s delay")
                
                # Get stock info (this usually works)
                stock_info = ak.stock_individual_info_em(symbol=symbol)
                if stock_info.empty:
                    raise ValueError(f"No basic info found for symbol {symbol}")
                
                # Try primary method first
                primary_success = False
                try:
                    # Primary method: real-time quotes
                    quote_data = ak.stock_zh_a_spot_em()
                    stock_quote = quote_data[quote_data["代码"] == symbol]
                    
                    if not stock_quote.empty:
                        # Extract relevant fields from real-time data
                        stock_row = stock_quote.iloc[0]
                        info_dict = dict(zip(stock_info["item"], stock_info["value"]))
                        
                        result = {
                            "symbol": symbol,
                            "name": stock_row["名称"],
                            "price": float(stock_row["最新价"]),
                            "change": float(stock_row["涨跌额"]),
                            "change_percent": float(stock_row["涨跌幅"]),
                            "open": float(stock_row["今开"]),
                            "high": float(stock_row["最高"]),
                            "low": float(stock_row["最低"]),
                            "close": float(stock_row["昨收"]),
                            "volume": int(stock_row["成交量"]),
                            "amount": float(stock_row["成交额"]),
                            "turnover_rate": float(stock_row["换手率"]),
                            "market_cap": float(info_dict.get("总市值", 0)),
                            "pe_ratio": float(info_dict.get("市盈率-动态", 0)),
                            "pb_ratio": float(info_dict.get("市净率", 0)),
                        }
                        
                        logger.info(f"Successfully fetched real-time quotes for {symbol}")
                        primary_success = True
                        return result
                        
                except Exception as realtime_error:
                    logger.warning(f"Primary method (AKShare real-time) failed for {symbol}: {realtime_error}")
                
                # If primary failed, try fallbacks immediately
                if not primary_success:
                    # Fallback 1: Historical data
                    try:
                        hist_data = ak.stock_zh_a_hist(
                            symbol=symbol,
                            period="daily",
                            adjust="qfq"
                        )
                        if not hist_data.empty:
                            latest_row = hist_data.iloc[-1]
                            info_dict = dict(zip(stock_info["item"], stock_info["value"]))
                            
                            result = {
                                "symbol": symbol,
                                "name": info_dict.get("股票简称", symbol),
                                "price": float(latest_row["收盘"]),
                                "change": float(latest_row["涨跌额"]),
                                "change_percent": float(latest_row["涨跌幅"]),
                                "open": float(latest_row["开盘"]),
                                "high": float(latest_row["最高"]),
                                "low": float(latest_row["最低"]),
                                "close": float(latest_row["收盘"]),
                                "volume": int(latest_row["成交量"]),
                                "amount": float(latest_row["成交额"]),
                                "turnover_rate": float(latest_row["换手率"]),
                                "market_cap": float(info_dict.get("总市值", 0)),
                                "pe_ratio": float(info_dict.get("市盈率-动态", 0)),
                                "pb_ratio": float(info_dict.get("市净率", 0)),
                            }
                            
                            logger.info(f"Fallback 1 (historical data) successful for {symbol}")
                            return result
                            
                    except Exception as fallback_error:
                        logger.error(f"Fallback 1 (historical) failed for {symbol}: {fallback_error}")
                    
                    # Fallback 2: Tushare
                    if TUSHARE_AVAILABLE:
                        logger.info(f"Trying Fallback 2 (Tushare) for {symbol}")
                        tushare_result = get_realtime_quotes_tushare(symbol)
                        if tushare_result:
                            logger.info(f"Fallback 2 (Tushare) successful for {symbol}")
                            return tushare_result
                        else:
                            logger.warning(f"Fallback 2 (Tushare) failed for {symbol}")
                    
                    # All methods failed
                    raise ValueError(f"All data sources failed for {symbol}")
                
                # If we get here, all methods failed
                if attempt == max_retries - 1:
                    raise ValueError(f"No quote data found for symbol {symbol}")
                    
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed for {symbol}: {str(e)}")
                if attempt == max_retries - 1:
                    raise ValueError(f"Failed to fetch data for {symbol} after {max_retries} attempts: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error in get_realtime_quotes for {symbol}: {str(e)}")
        raise ValueError(f"Invalid symbol or data retrieval error: {str(e)}")


def validate_symbol(symbol: str) -> bool:
    """Validate A-share stock symbol format.
    
    Args:
        symbol: Stock symbol to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not symbol or not isinstance(symbol, str):
        return False
        
    # Remove any non-digit characters
    clean_symbol = "".join(c for c in symbol if c.isdigit())
    
    # Check length and format
    if len(clean_symbol) != 6:
        return False
        
    # Check if it's a valid A-share code
    first_digit = clean_symbol[0]
    if first_digit in ["6", "7"]:  # Shanghai exchange
        return True
    elif first_digit in ["0", "3"]:  # Shenzhen exchange
        return True
    else:
        return False