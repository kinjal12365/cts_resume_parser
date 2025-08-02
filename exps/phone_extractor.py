import re
from typing import Optional

def _is_valid_phone(phone: str) -> bool:
    digits = phone.replace('+', '')
    return 10 <= len(digits) <= 15 and len(set(digits)) >= 3

def extract_phone_number_from_text(text: str) -> Optional[str]:
    """
    Extract a phone number (preferably international format) from the given text.
    """
    clean_text = re.sub(r'[^\d+()\-. ]', ' ', text)

    phone_patterns = [
        r'(\+?\d{1,4}[\s\-]?\(?\d{2,5}\)?[\s\-]?\d{3,5}[\s\-]?\d{3,5})',
        r'(\d{10,15})'
    ]

    phone_candidates = []
    for pattern in phone_patterns:
        matches = re.findall(pattern, clean_text)
        for match in matches:
            cleaned = re.sub(r'[^\d+]', '', match)
            if _is_valid_phone(cleaned):
                phone_candidates.append(cleaned)

    phone_candidates = list(set(phone_candidates))

    for phone in phone_candidates:
        if phone.startswith('+'):
            return phone

    return phone_candidates[0] if phone_candidates else None
