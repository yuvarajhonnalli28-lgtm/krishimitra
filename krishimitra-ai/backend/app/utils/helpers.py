# backend/app/utils/helpers.py

import uuid
import hashlib
import random
import string
from datetime import datetime
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

def generate_image_id() -> str:
    """
    Generate a unique image ID
    
    Returns:
        Unique image identifier string
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"img_{timestamp}_{unique_id}"


def generate_session_id() -> str:
    """
    Generate a unique session ID for chat
    
    Returns:
        Unique session identifier
    """
    return str(uuid.uuid4())[:8]


def calculate_confidence_score(predictions: list, index: int) -> float:
    """
    Calculate confidence score from model predictions
    
    Args:
        predictions: List of prediction probabilities
        index: Index of predicted class
    
    Returns:
        Confidence score as float
    """
    try:
        return float(predictions[0][index])
    except (IndexError, TypeError):
        return 0.0


def calculate_image_hash(image_bytes: bytes) -> str:
    """
    Calculate MD5 hash of image for duplicate detection
    
    Args:
        image_bytes: Image as bytes
    
    Returns:
        MD5 hash string
    """
    return hashlib.md5(image_bytes).hexdigest()


def format_price(price: float, currency: str = "₹") -> str:
    """
    Format price with currency symbol
    
    Args:
        price: Price value
        currency: Currency symbol
    
    Returns:
        Formatted price string
    """
    return f"{currency} {price:,.2f}"


def generate_otp(length: int = 6) -> str:
    """
    Generate OTP for verification
    
    Args:
        length: Length of OTP
    
    Returns:
        OTP string
    """
    return ''.join(random.choices(string.digits, k=length))


def sanitize_input(text: str) -> str:
    """
    Basic input sanitization
    
    Args:
        text: Input text
    
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    # Remove potentially dangerous characters
    dangerous = ['<', '>', '"', "'", ';', '--', '/*', '*/']
    for char in dangerous:
        text = text.replace(char, '')
    return text.strip()


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to specified length
    
    Args:
        text: Input text
        max_length: Maximum length
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def parse_date(date_str: str) -> Optional[datetime]:
    """
    Parse date string to datetime
    
    Args:
        date_str: Date string
    
    Returns:
        Datetime object or None
    """
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y%m%d",
        "%Y-%m-%d %H:%M:%S"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename
    
    Args:
        filename: File name
    
    Returns:
        File extension (including dot)
    """
    import os
    return os.path.splitext(filename)[1].lower()


def is_allowed_file(filename: str, allowed_extensions: list) -> bool:
    """
    Check if file extension is allowed
    
    Args:
        filename: File name
        allowed_extensions: List of allowed extensions
    
    Returns:
        True if allowed, False otherwise
    """
    ext = get_file_extension(filename)
    return ext in allowed_extensions


def create_slug(text: str) -> str:
    """
    Create URL-friendly slug from text
    
    Args:
        text: Input text
    
    Returns:
        Slug string
    """
    # Convert to lowercase
    text = text.lower()
    # Replace spaces with hyphens
    text = text.replace(' ', '-')
    # Remove special characters
    text = ''.join(c for c in text if c.isalnum() or c == '-')
    # Remove multiple hyphens
    while '--' in text:
        text = text.replace('--', '-')
    # Remove leading/trailing hyphens
    return text.strip('-')


def mask_email(email: str) -> str:
    """
    Mask email for display
    
    Args:
        email: Email address
    
    Returns:
        Masked email
    """
    if not email or '@' not in email:
        return email
    
    local, domain = email.split('@')
    if len(local) <= 2:
        masked_local = local[0] + '*' * len(local[1:])
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"


def mask_phone(phone: str) -> str:
    """
    Mask phone number for display
    
    Args:
        phone: Phone number
    
    Returns:
        Masked phone number
    """
    if not phone or len(phone) < 6:
        return phone
    
    return phone[:3] + '*' * (len(phone) - 6) + phone[-3:]


# Test the module
if __name__ == "__main__":
    print("\n🧪 Testing Helpers Module")
    print("="*40)
    
    # Test generate_image_id
    img_id = generate_image_id()
    print(f"✅ generate_image_id(): {img_id}")
    
    # Test generate_session_id
    session_id = generate_session_id()
    print(f"✅ generate_session_id(): {session_id}")
    
    # Test format_price
    price = format_price(1234.56)
    print(f"✅ format_price(): {price}")
    
    # Test sanitize_input
    dirty = "<script>alert('test')</script>"
    clean = sanitize_input(dirty)
    print(f"✅ sanitize_input(): {clean}")
    
    # Test truncate_text
    long_text = "This is a very long text that needs to be truncated"
    short = truncate_text(long_text, 20)
    print(f"✅ truncate_text(): {short}")
    
    # Test mask_email
    email = "farmer@example.com"
    masked = mask_email(email)
    print(f"✅ mask_email(): {masked}")
    
    print("\n✨ All helper functions ready!\n")