"""Company field whitelist."""

import re
from typing import Any, Dict, List, Tuple

# Required fields - must exist and pass validation
REQUIRED = ['ticker', 'name']

# Validated fields - if present, must pass validation
VALIDATED = ['exchange', 'sector', 'industry']

COMPANY_WHITELIST = {
    'required': REQUIRED,
    'validated': VALIDATED,
}

# Valid exchanges
VALID_EXCHANGES = {'NASDAQ', 'NYSE', 'AMEX', 'OTC'}


def validate_company(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate company data against whitelist.
    
    Returns:
        (is_valid, error_messages)
    """
    errors = []
    
    # Required fields
    ticker = data.get('ticker')
    if not ticker:
        errors.append("ticker is required")
    elif not re.match(r'^[A-Z]{1,5}$', str(ticker).upper()):
        errors.append(f"ticker format invalid: {ticker}")
    
    name = data.get('name')
    if not name:
        errors.append("name is required")
    
    # Validated fields (optional but validated if present)
    exchange = data.get('exchange')
    if exchange and exchange.upper() not in VALID_EXCHANGES:
        errors.append(f"exchange invalid: {exchange}")
    
    return len(errors) == 0, errors

