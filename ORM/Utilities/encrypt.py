"""
Password hashing utilities using bcrypt.

Passwords are never stored in plain text:
  - hash_password()   → called when creating a user
  - verify_password() → called during login to compare input against the stored hash
"""

import bcrypt


def hash_password(password: str) -> str:
    """Hash a plain-text password and return the bcrypt string (starts with $2b$)."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """Return True if the plain-text password matches the stored bcrypt hash."""
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )
