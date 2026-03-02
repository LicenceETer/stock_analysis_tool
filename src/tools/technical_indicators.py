"""Technical indicators calculation using available data sources."""

import logging
import pandas as pd
import talib as ta
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def calculate_technical_indicators_fallback(symbol: str, current_price: float) -> Dict[str, Any]:
    """Calculate technical indicators with fallback when historical data is unavailable.
    
    Args:
        symbol: Stock code
        current_price: Current stock price
        
    Returns:
        Dictionary containing calculated or estimated technical indicators
    """
    try:
        # When historical data is unavailable, we can still provide some basic indicators
        # based on current price and reasonable assumptions
        
        indicators = {
            "ma5": current_price,  # Use current price as proxy
            "ma10": current_price,
            "ma20": current_price,
            "rsi": 50.0,  # Neutral RSI when no data
            "macd": 0.0,
            "macd_signal": 0.0,
            "macd_histogram": 0.0,
            "bb_upper": current_price * 1.02,  # Estimated upper band
            "bb_middle": current_price,
            "bb_lower": current_price * 0.98,  # Estimated lower band,
            "price_vs_ma5": 0.0,
            "price_vs_ma20": 0.0,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Using fallback technical indicators for {symbol}")
        return indicators
        
    except Exception as e:
        logger.error(f"Error in fallback technical indicators for {symbol}: {str(e)}")
        # Return minimal indicators
        return {
            "ma5": current_price,
            "rsi": 50.0,
            "timestamp": datetime.now().isoformat()
        }


def get_historical_data_with_retry(symbol: str, days: int = 60) -> Optional[pd.DataFrame]:
    """Get historical data with multiple retry attempts and fallback sources.
    
    Args:
        symbol: Stock code
        days: Number of days to fetch
        
    Returns:
        DataFrame with historical data or None if all sources fail
    """
    import akshare as ak
    import tushare as ts
    import time
    import random
    
    # Try AKShare first
    max_retries = 3
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                time.sleep(random.uniform(1.0, 2.0))
                
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                adjust="qfq"
            )
            
            if not df.empty:
                # Process the data
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
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date')
                df = df.sort_index(ascending=False).head(days).sort_index(ascending=True)
                
                # Ensure numeric columns
                numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'amount']
                for col in numeric_columns:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                        
                logger.info(f"AKShare historical data successful for {symbol}")
                return df
                
        except Exception as e:
            logger.warning(f"AKShare attempt {attempt + 1} failed for {symbol}: {e}")
    
    # Try Tushare as fallback
    try:
        # Format symbol for Tushare
        if symbol.startswith(('6', '7')):
            ts_code = f"{symbol}.SH"
        else:
            ts_code = f"{symbol}.SZ"
            
        df = ts.pro_bar(ts_code=ts_code, adj='qfq', limit=days)
        if not df.empty:
            # Rename columns to standard format
            df = df.rename(columns={
                'trade_date': 'date',
                'open': 'open',
                'high': 'high', 
                'low': 'low',
                'close': 'close',
                'vol': 'volume'
            })
            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
            df = df.set_index('date')
            df = df.sort_index()
            
            logger.info(f"Tushare historical data successful for {symbol}")
            return df
            
    except Exception as e:
        logger.warning(f"Tushare historical data failed for {symbol}: {e}")
    
    logger.error(f"All historical data sources failed for {symbol}")
    return None


def calculate_technical_indicators_robust(symbol: str, current_price: float) -> Dict[str, Any]:
    """Robust technical indicator calculation with multiple fallbacks.
    
    Args:
        symbol: Stock code
        current_price: Current stock price (for fallback scenarios)
        
    Returns:
        Dictionary containing technical indicators
    """
    try:
        # Try to get historical data
        historical_data = get_historical_data_with_retry(symbol)
        
        if historical_data is not None and not historical_data.empty:
            # Calculate proper technical indicators
            close_array = historical_data['close'].values
            open_array = historical_data['open'].values
            high_array = historical_data['high'].values
            low_array = historical_data['low'].values
            volume_array = historical_data['volume'].values
            
            indicators = {}
            
            # Moving averages
            indicators["ma5"] = float(historical_data["close"].rolling(window=5).mean().iloc[-1])
            indicators["ma10"] = float(historical_data["close"].rolling(window=10).mean().iloc[-1])
            indicators["ma20"] = float(historical_data["close"].rolling(window=20).mean().iloc[-1])
            
            # RSI
            rsi_values = ta.RSI(close_array, timeperiod=14)
            indicators["rsi"] = float(rsi_values[-1]) if len(rsi_values) > 0 else 50.0
            
            # MACD
            macd_line, macd_signal_line, macd_hist = ta.MACD(
                close_array, fastperiod=12, slowperiod=26, signalperiod=9
            )
            indicators["macd"] = float(macd_line[-1]) if len(macd_line) > 0 else 0.0
            indicators["macd_signal"] = float(macd_signal_line[-1]) if len(macd_signal_line) > 0 else 0.0
            indicators["macd_histogram"] = float(macd_hist[-1]) if len(macd_hist) > 0 else 0.0
            
            # Bollinger Bands
            upper_band, middle_band, lower_band = ta.BBANDS(close_array, timeperiod=20, nbdevup=2, nbdevdn=2)
            indicators["bb_upper"] = float(upper_band[-1]) if len(upper_band) > 0 else current_price * 1.02
            indicators["bb_middle"] = float(middle_band[-1]) if len(middle_band) > 0 else current_price
            indicators["bb_lower"] = float(lower_band[-1]) if len(lower_band) > 0 else current_price * 0.98
            
            # Price position relative to indicators
            indicators["price_vs_ma5"] = ((current_price - indicators["ma5"]) / indicators["ma5"]) * 100
            indicators["price_vs_ma20"] = ((current_price - indicators["ma20"]) / indicators["ma20"]) * 100
            
            indicators["timestamp"] = datetime.now().isoformat()
            
            logger.info(f"Proper technical indicators calculated for {symbol}")
            return indicators
            
        else:
            # Fallback to estimated indicators
            logger.warning(f"Using fallback indicators for {symbol}")
            return calculate_technical_indicators_fallback(symbol, current_price)
            
    except Exception as e:
        logger.error(f"Error in robust technical indicators for {symbol}: {str(e)}")
        return calculate_technical_indicators_fallback(symbol, current_price)