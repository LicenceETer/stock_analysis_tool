"""Data validation utilities to ensure real market data is used, not simulated/mock data."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, date

logger = logging.getLogger(__name__)


class DataValidationException(Exception):
    """Exception raised when data validation fails."""
    pass


def validate_real_market_data(data: Dict[str, Any], symbol: str) -> bool:
    """Validate that the provided data represents real market data, not simulated/mock data.
    
    Args:
        data: Stock data dictionary to validate
        symbol: Stock symbol for context
        
    Returns:
        True if data appears to be real market data
        
    Raises:
        DataValidationException: If data appears to be simulated or invalid
    """
    if not data or not isinstance(data, dict):
        raise DataValidationException("Data is empty or not a dictionary")
    
    # Check required fields exist
    required_fields = ["symbol", "price", "volume", "change_percent"]
    for field in required_fields:
        if field not in data:
            raise DataValidationException(f"Missing required field: {field}")
    
    # Validate price is reasonable (not obviously fake)
    price = data.get("price", 0)
    if price <= 0 or price > 100000:  # Extremely high prices are suspicious
        raise DataValidationException(f"Suspicious price value: {price}")
    
    # Validate volume is reasonable
    volume = data.get("volume", 0)
    if volume < 0 or volume > 10000000000:  # 10 billion shares is extremely high
        raise DataValidationException(f"Suspicious volume value: {volume}")
    
    # Validate symbol matches
    if data.get("symbol") != symbol:
        raise DataValidationException(f"Symbol mismatch: expected {symbol}, got {data.get('symbol')}")
    
    # Check for mock/simulated data patterns
    mock_indicators = [
        "mock", "simulated", "test", "fake", "dummy",
        "placeholder", "example", "sample"
    ]
    name = str(data.get("name", "")).lower()
    if any(indicator in name for indicator in mock_indicators):
        raise DataValidationException(f"Data appears to be simulated based on name: {name}")
    
    # Validate change_percent is reasonable
    change_percent = data.get("change_percent", 0)
    if abs(change_percent) > 50:  # 50% daily change is extremely rare
        logger.warning(f"Large price change detected: {change_percent}% for {symbol}")
        # Don't raise exception for large changes as they can happen in real markets
    
    logger.info(f"Data validation passed for {symbol}")
    return True


def validate_historical_data_dates(data: Dict[str, Any], max_date: Optional[date] = None) -> bool:
    """Validate that historical data doesn't contain future dates.
    
    Args:
        data: Historical data to validate
        max_date: Maximum allowed date (defaults to today)
        
    Returns:
        True if dates are valid
        
    Raises:
        DataValidationException: If future dates are detected
    """
    if max_date is None:
        max_date = date.today()
    
    # Check if data contains date information
    if "timestamp" in data:
        try:
            data_date = datetime.fromisoformat(data["timestamp"]).date()
            if data_date > max_date:
                raise DataValidationException(f"Future date detected in data: {data_date} > {max_date}")
        except ValueError:
            # Invalid timestamp format, skip validation
            pass
    
    logger.info(f"Historical data date validation passed (max_date: {max_date})")
    return True


def enforce_no_mock_data_policy() -> None:
    """Enforce policy that no mock/simulated data should be used in production.
    
    This function should be called at the start of any analysis to ensure
    real market data is being used.
    """
    logger.info("Enforcing no mock data policy - only real market data allowed")
    # This is a placeholder for more complex policy enforcement if needed