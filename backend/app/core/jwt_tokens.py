"""
JWT access token helpers — PraxisMed Sprint 7 / Module 59

Provides create_access_token and decode_access_token for human user sessions.
Reads JWT_SECRET_KEY from the environment.  Missing or empty secret raises
MissingJWTSecretError so callers can surface a safe 503 rather than silently
using a weak key.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class JWTError(RuntimeError):
    """Base class for JWT errors."""


class MissingJWTSecretError(JWTError):
    """Raised when JWT_SECRET_KEY is not configured."""


class InvalidJWTError(JWTError):
    """Raised when a token cannot be decoded (malformed, bad signature, etc.)."""


class ExpiredJWTError(InvalidJWTError):
    """Raised when a token has expired."""


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

JWT_ALGORITHM = "HS256"
DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = 60


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_jwt_secret() -> str:
    secret = os.environ.get("JWT_SECRET_KEY", "")
    if not secret.strip():
        raise MissingJWTSecretError(
            "JWT_SECRET_KEY environment variable is not set or empty"
        )
    return secret


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def create_access_token(
    user_id: str,
    clinic_id: str,
    role: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Encode a signed JWT access token.

    Claims: sub (user_id), clinic_id, role, iat, exp.
    Raises MissingJWTSecretError if JWT_SECRET_KEY is not set.
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES)
    secret = _get_jwt_secret()
    now = datetime.now(timezone.utc)
    payload: Dict[str, Any] = {
        "sub":       user_id,
        "clinic_id": clinic_id,
        "role":      role,
        "iat":       now,
        "exp":       now + expires_delta,
    }
    return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and verify *token*, returning the payload dict.

    Raises:
        MissingJWTSecretError — JWT_SECRET_KEY not configured.
        ExpiredJWTError       — token exp claim is in the past.
        InvalidJWTError       — any other decode failure.
    """
    secret = _get_jwt_secret()
    try:
        return jwt.decode(token, secret, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise ExpiredJWTError("Token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise InvalidJWTError(f"Invalid token: {exc}") from exc
