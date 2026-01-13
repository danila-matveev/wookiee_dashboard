import hashlib
import secrets
from datetime import datetime, timedelta, timezone


def generate_code(length: int = 6) -> str:
    return "".join(secrets.choice("0123456789") for _ in range(length))


def hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def expires_at(minutes: int = 15) -> str:
    return (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat()


def verify_code(code: str, code_hash: str) -> bool:
    return hash_code(code) == code_hash
