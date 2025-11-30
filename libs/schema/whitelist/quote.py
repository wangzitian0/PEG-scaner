"""DailyQuote field whitelist."""

from datetime import date, datetime
from typing import Any, Dict, List, Tuple

# Required fields
REQUIRED = ['ticker', 'date', 'close']

# Validated fields
VALIDATED = ['open', 'high', 'low', 'volume']

QUOTE_WHITELIST = {
    'required': REQUIRED,
    'validated': VALIDATED,
}


def validate_quote(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate quote data against whitelist.
    
    Returns:
        (is_valid, error_messages)
    """
    errors = []
    
    # Required: ticker
    ticker = data.get('ticker')
    if not ticker:
        errors.append("ticker is required")
    
    # Required: date
    quote_date = data.get('date')
    if not quote_date:
        errors.append("date is required")
    else:
        # Validate date format
        if isinstance(quote_date, str):
            try:
                datetime.fromisoformat(quote_date.replace('Z', '+00:00'))
            except ValueError:
                errors.append(f"date format invalid: {quote_date}")
    
    # Required: close > 0
    close = data.get('close')
    if close is None:
        errors.append("close is required")
    elif not isinstance(close, (int, float)) or close <= 0:
        errors.append(f"close must be > 0: {close}")
    
    # Validated: volume >= 0
    volume = data.get('volume')
    if volume is not None:
        if not isinstance(volume, (int, float)) or volume < 0:
            errors.append(f"volume must be >= 0: {volume}")
    
    # Validated: high >= low
    high = data.get('high')
    low = data.get('low')
    if high is not None and low is not None:
        if high < low:
            errors.append(f"high ({high}) must be >= low ({low})")
    
    return len(errors) == 0, errors

