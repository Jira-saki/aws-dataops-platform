import hashlib
import os

SALT = os.getenv("PII_SALT", "dataops-secret-salt-2026")

def hash_ip(ip_address: str) -> str:
    """Mask IP address with deterministic SHA-256 hash (12-char prefix)."""
    if not ip_address or ip_address == "-":
        return "unknown"
    raw_value = f"{ip_address}{SALT}".encode("utf-8")
    return hashlib.sha256(raw_value).hexdigest()[:12]
