"""
PraxisMed Vapi/log pseudonymization helper — Sprint 19 / Module 130.
Extended: sanitize_vapi_webhook_payload, sanitize_for_log, stable_hash, redact_transcript.

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


def stable_hash(value: str) -> str:
    """Return a stable HMAC-SHA256 hex digest for *value* with no context prefix."""
    return pseudonymize(value, context="")


def redact_transcript(value: str | None) -> str:
    """Return a safe placeholder for a transcript or audio content string.

    Transcripts are never hashed (too large, may contain identifiable passages).
    Instead a fixed sentinel is returned that signals "transcript redacted".
    """
    if not value:
        return ""
    return "[TRANSCRIPT REDACTED]"


# ---------------------------------------------------------------------------
# Keys considered sensitive in Vapi payloads and log objects.
# Preserve operational keys: clinic_id, clinic_ref, call_id, source,
# status, urgency_level, created_at, updated_at, action_required, ok.
# ---------------------------------------------------------------------------

_SENSITIVE_KEYS = frozenset({
    "patient_name", "name", "full_name",
    "phone", "phone_number", "mobile",
    "email",
    "transcript", "raw_transcript", "audio_transcript",
    "recording_url", "audio_url",
    "reason", "notes", "message",
})

_TRANSCRIPT_KEYS = frozenset({
    "transcript", "raw_transcript", "audio_transcript",
    "recording_url", "audio_url",
})


def _sanitize_value(key: str, value: object) -> object:
    """Return a safe representation for a single key/value pair."""
    if not isinstance(key, str):
        return value
    key_lower = key.lower()
    if key_lower in _TRANSCRIPT_KEYS:
        return redact_transcript(str(value) if value is not None else None)
    if key_lower in _SENSITIVE_KEYS:
        if value is None:
            return None
        return pseudonymize(str(value), context=key_lower)
    return value


def sanitize_for_log(obj: object) -> object:
    """Recursively sanitize a dict/list/scalar for safe logging.

    - dict values whose key matches a sensitive key are pseudonymized.
    - Lists are recursively sanitized.
    - Scalars are returned as-is.
    - The original object is never mutated.
    """
    if isinstance(obj, dict):
        return {
            k: _sanitize_value(k, sanitize_for_log(v))
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [sanitize_for_log(item) for item in obj]
    return obj


def sanitize_vapi_webhook_payload(payload: object) -> dict:
    """Sanitize a raw Vapi webhook or tool-call payload for safe logging.

    Sensitive fields (patient_name, phone, transcript, reason, message, etc.)
    are replaced with deterministic hash placeholders or redaction sentinels.
    Safe operational fields (clinic_id, clinic_ref, call_id, source, status,
    urgency_level) are preserved verbatim.

    Returns a new dict — the original payload is never mutated or logged.
    """
    if not isinstance(payload, dict):
        return {"_sanitized": True, "_type": type(payload).__name__}
    return sanitize_for_log(payload)  # type: ignore[return-value]
