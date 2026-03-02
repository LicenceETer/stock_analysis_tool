"""Tushare client for fallback data source."""

import logging
import os
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Try to initialize Tushare with token if available
try:
    import tushare as ts
    
    # Check if Tushare token is available in environment
    TUSHARE_TOKEN = os.getenv("TUSHARE_TOKEN")
    if TUSHARE_TOKEN:
        ts.set_token(TUSHARE_TOKEN)
        pro = ts.pro_api()
        TUSHARE_AVAILABLE = True
        logger.info("Tushare initialized successfully")
    else:
        # Use free tier without token (limited functionality)
        TUSHARE_AVAILABLE = True
        pro = None
        logger.warning("Tushare token not found, using limited free tier")
        
except ImportError:
    TUSHARE_AVAILABLE = False
    logger.warning("Tushare not available")
except Exception as e:
    TUSHARE_AVAILABLE = False
    logger.error(f"Tushare initialization failed: {e}")


def get_realtime_quotes_tushare(symbol: str) -> Optional[Dict[str, Any]]:
    """Get real-time quotes using Tushare as fallback.
    
    Args:
        symbol: Stock code (6-digit format)
        
    Returns:
        Dictionary with stock data or None if failed
    """
    if not TUSHARE_AVAILABLE:
        return None
        
    try:
        # Format symbol for Tushare (add exchange suffix)
        if symbol.startswith(('6', '7')):
            ts_code = f"{symbol}.SH"  # Shanghai
        elif symbol.startswith(('0', '3')):
            ts_code = f"{symbol}.SZ"  # Shenzhen
        else:
            return None
            
        # Try to get real-time data
        if pro is not None:
            # Use pro API if token available
            df = pro.daily(ts_code=ts_code, limit=1)
            if not df.empty:
                row = df.iloc[0]
                return {
                    "symbol": symbol,
                    "name": row.get("name", symbol),
                    "price": float(row["close"]),
                    "change": float(row["close"] - row["pre_close"]) if "pre_close" in row else 0.0,
                    "change_percent": ((float(row["close"]) - float(row["pre_close"])) / float(row["pre_close"]) * 100) 
                                    if "pre_close" in row and row["pre_close"] != 0 else 0.0,
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": int(row["vol"] * 100),  # Convert from shares to lots
                    "amount": float(row["amount"] * 1000),  # Convert from thousands to yuan
                    "turnover_rate": 0.0,  # Not available in basic daily data
                    "market_cap": 0.0,  # Not available in basic daily data
                    "pe_ratio": 0.0,  # Not available in basic daily data
                    "pb_ratio": 0.0,  # Not available in basic daily data
                }
        else:
            # Use free tier
            df = ts.get_realtime_quotes(symbol)
            if not df.empty:
                row = df.iloc[0]
                # Handle empty string values
                def safe_float(val, default=0.0):
                    try:
                        return float(val) if val != '' else default
                    except (ValueError, TypeError):
                        return default
                
                pre_close = safe_float(row["pre_close"])
                current_price = safe_float(row["price"])
                
                change = current_price - pre_close
                change_percent = (change / pre_close * 100) if pre_close != 0 else 0.0
                
                return {
                    "symbol": symbol,
                    "name": row.get("name", symbol) if row.get("name") else symbol,
                    "price": current_price,
                    "change": change,
                    "change_percent": change_percent,
                    "open": safe_float(row["open"]),
                    "high": safe_float(row["high"]),
                    "low": safe_float(row["low"]),
                    "close": current_price,  # Real-time price as close
                    "volume": int(safe_float(row["volume"])),
                    "amount": safe_float(row["amount"]),
                    "turnover_rate": 0.0,
                    "market_cap": 0.0,
                    "pe_ratio": 0.0,
                    "pb_ratio": 0.0,
                }
                
    except Exception as e:
        logger.warning(f"Tushare fallback failed for {symbol}: {e}")
        return None
        
    return None