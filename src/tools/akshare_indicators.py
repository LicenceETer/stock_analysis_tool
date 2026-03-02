"""AKShare-based technical indicators calculation using raw market data."""

import logging
import pandas as pd
import talib as ta
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def calculate_indicators_from_akshare_data(
    symbol: str,
    periods: Optional[Dict[str, int]] = None
) -> Dict[str, Any]:
    """Calculate technical indicators using AKShare raw data and pandas/TALib.
    
    Args:
        symbol: Stock code (e.g., "600519")
        periods: Dictionary of indicator periods
        
    Returns:
        Dictionary containing calculated technical indicators
    """
    try:
        import akshare as ak
        
        # Set default periods
        if periods is None:
            periods = {
                "ma5": 5,
                "ma10": 10,
                "ma20": 20,
                "rsi": 14,
                "macd_fast": 12,
                "macd_slow": 26,
                "macd_signal": 9
            }
            
        # Fetch raw historical data from AKShare
        logger.info(f"Fetching raw historical data for {symbol} from AKShare")
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            adjust="qfq"
        )
        
        if df.empty:
            raise ValueError(f"No historical data available for {symbol}")
            
        # Rename columns to standard format
        column_mapping = {
            '日期': 'date',
            '开盘': 'open', 
            '最高': 'high',
            '最低': 'low',
            '收盘': 'close',
            '成交量': 'volume',
            '成交额': 'amount'
        }
        df = df.rename(columns=column_mapping)
        
        # Ensure we have enough data points
        min_required = max(periods.values()) if periods else 20
        if len(df) < min_required:
            logger.warning(f"Insufficient data points for {symbol}: {len(df)} < {min_required}")
            
        # Calculate moving averages using pandas rolling
        indicators = {}
        
        # Moving averages
        if "ma5" in periods:
            df["MA5"] = df["close"].rolling(window=periods["ma5"]).mean()
            indicators["ma5"] = float(df["MA5"].iloc[-1]) if not pd.isna(df["MA5"].iloc[-1]) else float(df["close"].iloc[-1])
            
        if "ma10" in periods:
            df["MA10"] = df["close"].rolling(window=periods["ma10"]).mean()
            indicators["ma10"] = float(df["MA10"].iloc[-1]) if not pd.isna(df["MA10"].iloc[-1]) else float(df["close"].iloc[-1])
            
        if "ma20" in periods:
            df["MA20"] = df["close"].rolling(window=periods["ma20"]).mean()
            indicators["ma20"] = float(df["MA20"].iloc[-1]) if not pd.isna(df["MA20"].iloc[-1]) else float(df["close"].iloc[-1])
            
        # RSI using TALib
        if "rsi" in periods:
            close_array = df["close"].values
            rsi_values = ta.RSI(close_array, timeperiod=periods["rsi"])
            indicators["rsi"] = float(rsi_values[-1]) if len(rsi_values) > 0 and not pd.isna(rsi_values[-1]) else 50.0
            
        # MACD using TALib
        if all(k in periods for k in ["macd_fast", "macd_slow", "macd_signal"]):
            close_array = df["close"].values
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
        close_array = df["close"].values
        upper_band, middle_band, lower_band = ta.BBANDS(close_array, timeperiod=20, nbdevup=2, nbdevdn=2)
        indicators["bb_upper"] = float(upper_band[-1]) if len(upper_band) > 0 and not pd.isna(upper_band[-1]) else float(df["close"].iloc[-1]) * 1.02
        indicators["bb_middle"] = float(middle_band[-1]) if len(middle_band) > 0 and not pd.isna(middle_band[-1]) else float(df["close"].iloc[-1])
        indicators["bb_lower"] = float(lower_band[-1]) if len(lower_band) > 0 and not pd.isna(lower_band[-1]) else float(df["close"].iloc[-1]) * 0.98
        
        # Add timestamp
        indicators["timestamp"] = datetime.now().isoformat()
        
        logger.info(f"Successfully calculated indicators from AKShare data for {symbol}")
        return indicators
        
    except Exception as e:
        logger.error(f"Error calculating indicators from AKShare data for {symbol}: {str(e)}")
        raise


def get_current_price_from_akshare(symbol: str) -> float:
    """Get current price from AKShare real-time data.
    
    Args:
        symbol: Stock code
        
    Returns:
        Current stock price
    """
    try:
        import akshare as ak
        
        # Get real-time quotes
        quote_data = ak.stock_zh_a_spot_em()
        stock_quote = quote_data[quote_data["代码"] == symbol]
        
        if not stock_quote.empty:
            return float(stock_quote.iloc[0]["最新价"])
        else:
            # Fallback to historical data
            hist_data = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")
            if not hist_data.empty:
                return float(hist_data.iloc[-1]["收盘"])
            else:
                raise ValueError(f"No price data found for {symbol}")
                
    except Exception as e:
        logger.error(f"Error getting current price from AKShare for {symbol}: {str(e)}")
        raise