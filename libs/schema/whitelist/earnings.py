"""EarningsReport field whitelist."""

import re
from typing import Any, Dict, List, Tuple

# Required fields
REQUIRED = ['ticker', 'fiscal_period']

# Validated fields
VALIDATED = ['eps', 'revenue', 'pe_ratio']

EARNINGS_WHITELIST = {
    'required': REQUIRED,
    'validated': VALIDATED,
}


def validate_earnings(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate earnings data against whitelist.
    
    Returns:
        (is_valid, error_messages)
    """
    errors = []
    
    # Required: ticker
    ticker = data.get('ticker')
    if not ticker:
        errors.append("ticker is required")
    
    # Required: fiscal_period format YYYYQN
    fiscal_period = data.get('fiscal_period')
    if not fiscal_period:
        errors.append("fiscal_period is required")
    elif not re.match(r'^\d{4}Q[1-4]$', str(fiscal_period)):
        errors.append(f"fiscal_period format invalid (expected YYYYQN): {fiscal_period}")
    
    # Validated: revenue >= 0 if present
    revenue = data.get('revenue')
    if revenue is not None:
        if not isinstance(revenue, (int, float)) or revenue < 0:
            errors.append(f"revenue must be >= 0: {revenue}")
    
    return len(errors) == 0, errors

