"""
Webhook signature verification — PraxisMed Sprint 5 / Module 46

Provides HMAC-SHA256-based webhook signature helpers for verifying
payloads from external services (Vapi, n8n, internal).

No FastAPI imports. No database usage. No external service calls.
Safe to import in tests without side effects.
"""

from __future__ import annotations

import hmac
import hashlib
import os
from typing import Optional


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class WebhookSignatureError(RuntimeError):
    """Base class for webhook signature errors."""


class InvalidWebhookSignatureError(WebhookSignatureError):
    """Raised when a signature is present but does not match the expected digest."""


class MissingWebhookSecretError(WebhookSignatureError):
    """Raised when the required webhook secret env var is not set or is empty."""


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_SIGNATURE_ALGORITHM = "hmac-sha256"

ALLOWED_WEBHOOK_PROVIDERS = {"vapi", "n8n", "internal"}

# Maps provider → environment variable name for the webhook secret
_PROVIDER_SECRET_ENV: dict[str, str] = {
    "vapi":     "VAPI_WEBHOOK_SECRET",
    "n8n":      "N8N_WEBHOOK_SECRET",
    "internal": "INTERNAL_WEBHOOK_SECRET",
}

_SHA256_PREFIX = "sha256="


# ---------------------------------------------------------------------------
# 1. normalize_webhook_provider
# ---------------------------------------------------------------------------


def normalize_webhook_provider(provider: str) -> str:
    """Validate and normalise a webhook provider name.

    Returns the lowercase, stripped provider string.
    Raises WebhookSignatureError for empty or unknown providers.
    """
    if not provider or not str(provider).strip():
        raise WebhookSignatureError("'provider' must not be empty")
    normalised = provider.strip().lower()
    if normalised not in ALLOWED_WEBHOOK_PROVIDERS:
        raise WebhookSignatureError(
            f"Unknown webhook provider {normalised!r}. "
            f"Allowed: {sorted(ALLOWED_WEBHOOK_PROVIDERS)}"
        )
    return normalised


# ---------------------------------------------------------------------------
# 2. get_webhook_secret_from_env
# ---------------------------------------------------------------------------


def get_webhook_secret_from_env(provider: str) -> str:
    """Read the webhook secret for *provider* from the environment.

    Raises MissingWebhookSecretError when the variable is absent or empty.
    """
    normalised = normalize_webhook_provider(provider)
    env_var = _PROVIDER_SECRET_ENV[normalised]
    secret = os.environ.get(env_var, "")
    if not secret or not secret.strip():
        raise MissingWebhookSecretError(
            f"Webhook secret for provider {normalised!r} is not configured. "
            f"Set the {env_var!r} environment variable."
        )
    return secret.strip()


# ---------------------------------------------------------------------------
# 3. normalize_signature_header
# ---------------------------------------------------------------------------


def normalize_signature_header(signature: Optional[str]) -> str:
    """Extract the raw hex digest from an incoming signature header.

    Accepts either:
      - a plain hex digest: ``abcdef01...``
      - a sha256-prefixed value: ``sha256=abcdef01...``

    Raises InvalidWebhookSignatureError for None, empty, or malformed values.
    """
    if signature is None:
        raise InvalidWebhookSignatureError(
            "Webhook signature header is missing."
        )
    stripped = signature.strip()
    if not stripped:
        raise InvalidWebhookSignatureError(
            "Webhook signature header is empty."
        )
    if stripped.startswith(_SHA256_PREFIX):
        digest = stripped[len(_SHA256_PREFIX):]
        if not digest:
            raise InvalidWebhookSignatureError(
                f"Webhook signature has 'sha256=' prefix but no digest value."
            )
        return digest
    return stripped


# ---------------------------------------------------------------------------
# 4. compute_hmac_sha256_signature
# ---------------------------------------------------------------------------


def compute_hmac_sha256_signature(payload_body: bytes, secret: str) -> str:
    """Compute the HMAC-SHA256 signature for *payload_body* using *secret*.

    Returns a lowercase hex digest string.
    """
    if not isinstance(payload_body, bytes):
        raise WebhookSignatureError(
            f"'payload_body' must be bytes; got {type(payload_body).__name__}"
        )
    if not secret or not str(secret).strip():
        raise WebhookSignatureError("'secret' must not be empty")

    return hmac.new(
        secret.encode("utf-8"),
        payload_body,
        hashlib.sha256,
    ).hexdigest()


# ---------------------------------------------------------------------------
# 5. verify_hmac_sha256_signature
# ---------------------------------------------------------------------------


def verify_hmac_sha256_signature(
    payload_body: bytes,
    signature_header: Optional[str],
    secret: str,
) -> bool:
    """Verify an HMAC-SHA256 webhook signature using constant-time comparison.

    Returns True if the signature is valid.
    Raises InvalidWebhookSignatureError if the signature does not match.
    Propagates InvalidWebhookSignatureError from normalize_signature_header
    if the header is absent or malformed.
    """
    provided_digest = normalize_signature_header(signature_header)
    expected_digest = compute_hmac_sha256_signature(payload_body, secret)

    if not hmac.compare_digest(expected_digest, provided_digest):
        raise InvalidWebhookSignatureError(
            "Webhook signature verification failed: digest mismatch."
        )
    return True


# ---------------------------------------------------------------------------
# 6. verify_provider_webhook_signature
# ---------------------------------------------------------------------------


def verify_provider_webhook_signature(
    provider: str,
    payload_body: bytes,
    signature_header: Optional[str],
    secret: Optional[str] = None,
) -> bool:
    """Verify a webhook signature for the named provider.

    If *secret* is None, the secret is loaded from the environment via
    get_webhook_secret_from_env.  Raises MissingWebhookSecretError when the
    env var is absent, or InvalidWebhookSignatureError on digest mismatch.
    """
    normalize_webhook_provider(provider)          # validate provider name
    resolved_secret = secret if secret is not None else get_webhook_secret_from_env(provider)
    return verify_hmac_sha256_signature(payload_body, signature_header, resolved_secret)
