"""
Password hashing helpers — PraxisMed Sprint 7 / Module 59

Wraps bcrypt for secure password storage.  No plaintext passwords are stored
or logged anywhere in this module.
"""

from __future__ import annotations

import bcrypt


class PasswordHashingError(RuntimeError):
    """Raised when a password operation is invalid."""


def hash_password(password: str) -> str:
    """Return a bcrypt hash of *password*.

    Raises PasswordHashingError for empty input.
    """
    if not password or not password.strip():
        raise PasswordHashingError("Password must not be empty")
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Return True if *password* matches *hashed*, False otherwise.

    Returns False (not raises) for empty or mismatched input so callers
    can treat the result as a simple boolean gate.
    """
    if not password or not hashed:
        return False
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
