"""Corrected AKShare data fetching using the right functions."""

import logging
import pandas as pd
import talib as ta
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def get_historical_data_corrected(symbol: str, days: int = 30) -> pd.DataFrame:
    """Get historical data using the correct AKShare function.
    
    Args:
        symbol: Stock code (6-digit format)
        days: Number of recent days to fetch
        
    Returns:
        DataFrame with historical OHLCV data
    """
    try:
        import akshare as ak
        
        # Use the correct function that works
        df = ak.stock_zh_a_daily(
            symbol=f"sh{symbol}" if symbol.startswith(('6', '7')) else f"sz{symbol}",
            adjust="qfq"
        )
        
        if df.empty:
            raise ValueError(f"No historical data found for {symbol}")
            
        # Sort by date and get recent data
        df = df.sort_index(ascending=False).head(days).sort_index(ascending=True)
        
        # Ensure we have the required columns
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_columns):
            raise ValueError("Missing required columns in historical data")
            
        logger.info(f"Successfully fetched {len(df)} days of historical data for {symbol}")
        return df
        
    except Exception as e:
        logger.error(f"Error fetching corrected historical data for {symbol}: {str(e)}")
        raise


def calculate_technical_indicators_corrected(symbol: str, periods: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
    """Calculate technical indicators using corrected AKShare data.
    
    Args:
        symbol: Stock code
        periods: Dictionary of indicator periods
        
    Returns:
        Dictionary containing calculated technical indicators
    """
    try:
        # Set default periods
        if periods is None:
            periods = {
                "ma5": 5,
                "ma10": 10,
                "ma20": 20,
                "ma30": 30,
                "rsi": 14,
                "macd_fast": 12,
                "macd_slow": 26,
                "macd_signal": 9
            }
            
        # Get historical data
        historical_data = get_historical_data_corrected(symbol, max(periods.values()))
        
        # Calculate moving averages using pandas rolling
        indicators = {}
        
        # Moving averages
        for ma_name, window in [("ma5", 5), ("ma10", 10), ("ma20", 20), ("ma30", 30)]:
            if ma_name in periods:
                ma_series = historical_data["close"].rolling(window=window).mean()
                indicators[ma_name] = float(ma_series.iloc[-1]) if not pd.isna(ma_series.iloc[-1]) else float(historical_data["close"].iloc[-1])
                
        # RSI
        if "rsi" in periods:
            close_array = historical_data["close"].values
            rsi_values = ta.RSI(close_array, timeperiod=periods["rsi"])
            indicators["rsi"] = float(rsi_values[-1]) if len(rsi_values) > 0 and not pd.isna(rsi_values[-1]) else 50.0
            
        # MACD
        if all(k in periods for k in ["macd_fast", "macd_slow", "macd_signal"]):
            close_array = historical_data["close"].values
            macd_line, macd_signal_line, macd_hist = ta.MACD(
                close_array,
                fastperiod=periods["macd_fast"],
                slowperiod=periods["macd_slow"],
                signalperiod=periods["macd_signal"]
            )
            indicators["macd"] = float(macd_line[-1]) if len(macd_line) > 0 and not pd.isna(macd_line[-1]) else 0.0
            indicators["macd_signal"] = float(macd_signal_line[-1]) if len(macd_signal_line) > 0 and not pd.isna(macd_signal_line[-1]) else 0.0
            indicators["macd_histogram"] = float(macd_hist[-1]) if len(macd_hist) > 0 and not pd.isna(macd_hist[-1]) else 0.0
            
        # Bollinger Bands
        close_array = historical_data["close"].values
        upper_band, middle_band, lower_band = ta.BBANDS(close_array, timeperiod=20, nbdevup=2, nbdevdn=2)
        indicators["bb_upper"] = float(upper_band[-1]) if len(upper_band) > 0 and not pd.isna(upper_band[-1]) else float(historical_data["close"].iloc[-1]) * 1.02
        indicators["bb_middle"] = float(middle_band[-1]) if len(middle_band) > 0 and not pd.isna(middle_band[-1]) else float(historical_data["close"].iloc[-1])
        indicators["bb_lower"] = float(lower_band[-1]) if len(lower_band) > 0 and not pd.isna(lower_band[-1]) else float(historical_data["close"].iloc[-1]) * 0.98
        
        # Add timestamp
        indicators["timestamp"] = datetime.now().isoformat()
        
        logger.info(f"Successfully calculated corrected indicators for {symbol}")
        return indicators
        
    except Exception as e:
        logger.error(f"Error calculating corrected indicators for {symbol}: {str(e)}")
        raise