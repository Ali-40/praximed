"""
PraxisMed Vapi/log pseudonymization helper — Sprint 19 / Module 130.

Provides HMAC-SHA256 pseudonymization for PII values that appear in logs,
Vapi payloads, and audit records. The pseudonymized token is stable across
calls with the same input and pepper — it is NOT encryption (no recovery
without the pepper + algorithm), but prevents accidental PII exposure in
log sinks.

Environment variables consumed (never logged):
  PSEUDONYMIZATION_PEPPER — secret pepper for HMAC-SHA256.
      Optional in local/staging (falls back to a fixed staging sentinel
      that is NOT secret and NOT used in production).
      Required in production: assert_pseudonymization_ready() raises if absent.

Usage:
    from backend.app.core.pseudonymization import pseudonymize, pseudonymize_phone

    safe_name  = pseudonymize(patient_name, context="patient_name")
    safe_phone = pseudonymize_phone(caller_phone)

The original value is never stored or returned. Only the hex digest appears
in logs or audit records.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os

logger = logging.getLogger(__name__)

# Used only in local/staging when PSEUDONYMIZATION_PEPPER is absent.
# This constant is intentionally not secret — it signals "staging pseudonym".
_STAGING_FALLBACK_PEPPER = "praximed-staging-pseudonymization-pepper-not-secret"


def _get_pepper() -> bytes:
    """Return the pseudonymization pepper as bytes. Never logs the value."""
    raw = os.getenv("PSEUDONYMIZATION_PEPPER", "").strip()
    if raw:
        return raw.encode("utf-8")
    return _STAGING_FALLBACK_PEPPER.encode("utf-8")


def _is_pepper_set() -> bool:
    return bool(os.getenv("PSEUDONYMIZATION_PEPPER", "").strip())


def assert_pseudonymization_ready() -> None:
    """
    Raise AssertionError if PSEUDONYMIZATION_PEPPER is not set.

    Call this before production PHI processing to ensure the pepper is
    provisioned. In local/staging this check can be skipped or caught
    and logged as a warning.
    """
    if not _is_pepper_set():
        raise AssertionError(
            "PSEUDONYMIZATION_PEPPER is required for production PHI processing. "
            "Set the env var via Railway secrets — never commit the value."
        )


def pseudonymize(value: str | None, context: str = "") -> str:
    """
    Return a stable HMAC-SHA256 hex digest for *value*.

    - Returns the empty string if *value* is None or empty.
    - Uses PSEUDONYMIZATION_PEPPER from env; falls back to staging sentinel.
    - *context* is included in the HMAC message to produce distinct tokens
      for the same raw value in different fields (e.g. phone vs name).
    - The digest is 64 hex characters. It is safe to store in logs/audit records.

    The original value is never returned and never logged.
    """
    if not value:
        return ""
    pepper = _get_pepper()
    message = f"{context}:{value}".encode("utf-8")
    digest = hmac.new(pepper, message, hashlib.sha256).hexdigest()
    if not _is_pepper_set():
        logger.debug(
            "pseudonymize: using staging fallback pepper (context=%s). "
            "Set PSEUDONYMIZATION_PEPPER for production.",
            context,
        )
    return digest


def pseudonymize_phone(phone: str | None) -> str:
    """Pseudonymize a caller phone number for safe audit/log storage."""
    return pseudonymize(phone, context="phone")


def pseudonymize_name(name: str | None) -> str:
    """Pseudonymize a patient name for safe audit/log storage."""
    return pseudonymize(name, context="patient_name")


def pseudonymize_email(email: str | None) -> str:
    """Pseudonymize a patient email for safe audit/log storage."""
    return pseudonymize(email, context="email")
