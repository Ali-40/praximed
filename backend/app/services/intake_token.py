"""
Intake Token Service — PraxisMed Sprint 20 / Module 151.

Generates and hashes secure intake link tokens.
Raw token is returned only once at creation.
Token hash is stored; raw token is never persisted or logged.
Token prefix is stored for admin identification only.

No patient data in token. No PHI. No secrets.
Synthetic/fake staging only. Production PHI remains NO-GO.
"""

from __future__ import annotations

import hashlib
import secrets


_TOKEN_BYTES = 32
_PREFIX_LENGTH = 8


def generate_intake_token() -> str:
    return secrets.token_urlsafe(_TOKEN_BYTES)


def hash_intake_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def token_prefix(raw_token: str) -> str:
    return raw_token[:_PREFIX_LENGTH]
