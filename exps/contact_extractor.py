import re
from typing import Optional, Dict

from name_extractor import extract_name_from_resume
from phone_extractor import extract_phone_number_from_text

def extract_email_from_text(text: str) -> Optional[str]:
    """
    Extract the first email found in the text.
    """
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else None

def extract_contact_info(text: str) -> Dict[str, Optional[str]]:
    """
    Extract name, phone, and email from raw resume text.
    """
    return {
        "name": extract_name_from_resume(text),
        "phone": extract_phone_number_from_text(text),
        "email": extract_email_from_text(text)
    }
