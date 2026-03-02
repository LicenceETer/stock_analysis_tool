"""Simplified market data fetching with Tushare as primary source."""

import logging
from typing import Dict, Any
import akshare as ak
from .tushare_client import get_realtime_quotes_tushare, TUSHARE_AVAILABLE
from .data_validation import validate_real_market_data, enforce_no_mock_data_policy

logger = logging.getLogger(__name__)


def get_realtime_quotes_simple(symbol: str) -> Dict[str, Any]:
    """Fetch real-time stock quotes with Tushare as primary source.
    
    Args:
        symbol: Stock code (e.g., "600519" for 贵州茅台)
        
    Returns:
        Dictionary containing real-time stock data
        
    Raises:
        ValueError: If symbol is invalid or data cannot be retrieved
    """
    try:
        # Enforce no mock data policy
        enforce_no_mock_data_policy()
        
        # Validate symbol format
        if not symbol or not isinstance(symbol, str):
            raise ValueError("Invalid symbol format")
            
        # Ensure symbol is in correct format (6 digits)
        symbol = symbol.zfill(6)
        
        # Try Tushare first (more reliable)
        if TUSHARE_AVAILABLE:
            logger.info(f"Using Tushare as primary source for {symbol}")
            tushare_result = get_realtime_quotes_tushare(symbol)
            if tushare_result:
                # Validate that this is real market data, not simulated
                validate_real_market_data(tushare_result, symbol)
                logger.info(f"Tushare successful for {symbol}")
                return tushare_result
            else:
                logger.warning(f"Tushare failed for {symbol}, trying AKShare")
        
        # Fallback to AKShare
        try:
            # Get stock info
            stock_info = ak.stock_individual_info_em(symbol=symbol)
            if stock_info.empty:
                raise ValueError(f"No basic info found for symbol {symbol}")
                
            # Get real-time quotes
            quote_data = ak.stock_zh_a_spot_em()
            stock_quote = quote_data[quote_data["代码"] == symbol]
            
            if not stock_quote.empty:
                # Extract relevant fields
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
                
                # Validate real market data
                validate_real_market_data(result, symbol)
                logger.info(f"AKShare successful for {symbol}")
                return result
                
        except Exception as akshare_error:
            logger.error(f"AKShare also failed for {symbol}: {akshare_error}")
            raise ValueError(f"Both Tushare and AKShare failed for {symbol}")
            
    except Exception as e:
        logger.error(f"Error in get_realtime_quotes_simple for {symbol}: {str(e)}")
        raise ValueError(f"Invalid symbol or data retrieval error: {str(e)}")