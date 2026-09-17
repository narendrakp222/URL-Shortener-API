import string
import secrets
import urllib.parse

BASE62_ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase


def generate_short_code(length: int = 6) -> str:
    """
    Generates a cryptographically secure random short code using Base62 characters.

    Args:
        length (int): Desired length of the short code (default: 6)

    Returns:
        str: Random short code string, e.g., 'abc123'
    """
    return "".join(secrets.choice(BASE62_ALPHABET) for _ in range(length))


def is_valid_url(url: str) -> bool:
    """
    Validates if a string is a properly formatted HTTP/HTTPS URL.
    """
    try:
        parsed = urllib.parse.urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False
