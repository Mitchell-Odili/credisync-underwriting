import re
from typing import Optional

def clean_currency(raw_value: str) -> Optional[float]:
    """Cleans currency strings like 'KES 1,250,000.00' or '$45,000' into a clean float."""
    if not raw_value:
        return None
    # Remove all characters except digits and decimal points
    cleaned = re.sub(r"[^\d.]", "", str(raw_value))
    try:
        return float(cleaned)
    except ValueError:
        return None

def validate_tax_id(tax_id: str) -> bool:
    """Basic structural validation for tax identification numbers."""
    # Example regex check for standard formats
    return bool(re.match(r"^[A-Z0-9\-]{8,15}$", tax_id.strip()))