"""
Tests for webhook signature verification core — PraxisMed Sprint 5 / Module 46

Strategy:
- Pure unit tests; no database, no HTTP, no external calls.
- Environment variables are set/cleared via monkeypatch.
"""

from __future__ import annotations

import hashlib
import hmac

import pytest

from backend.app.core.webhook_signature import (
    DEFAULT_SIGNATURE_ALGORITHM,
    ALLOWED_WEBHOOK_PROVIDERS,
    InvalidWebhookSignatureError,
    MissingWebhookSecretError,
    WebhookSignatureError,
    compute_hmac_sha256_signature,
    get_webhook_secret_from_env,
    normalize_signature_header,
    normalize_webhook_provider,
    verify_hmac_sha256_signature,
    verify_provider_webhook_signature,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SECRET = "test-secret-value"
PAYLOAD = b'{"event": "test"}'


def _expected_digest(payload: bytes, secret: str) -> str:
    return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


# ===========================================================================
# normalize_webhook_provider (tests 1–4)
# ===========================================================================


def test_normalize_webhook_provider_accepts_vapi():
    """Test 1 — 'vapi' is a valid provider."""
    assert normalize_webhook_provider("vapi") == "vapi"


def test_normalize_webhook_provider_lowercases_provider():
    """Test 2 — Provider string is lowercased and stripped."""
    assert normalize_webhook_provider("  VAPI  ") == "vapi"
    assert normalize_webhook_provider("N8N") == "n8n"


def test_normalize_webhook_provider_rejects_empty():
    """Test 3 — Empty or whitespace-only provider raises WebhookSignatureError."""
    with pytest.raises(WebhookSignatureError):
        normalize_webhook_provider("")
    with pytest.raises(WebhookSignatureError):
        normalize_webhook_provider("   ")


def test_normalize_webhook_provider_rejects_unknown():
    """Test 4 — Unknown provider raises WebhookSignatureError."""
    with pytest.raises(WebhookSignatureError):
        normalize_webhook_provider("stripe")


# ===========================================================================
# get_webhook_secret_from_env (tests 5–7)
# ===========================================================================


def test_get_webhook_secret_reads_vapi_secret(monkeypatch):
    """Test 5 — Reads VAPI_WEBHOOK_SECRET for provider 'vapi'."""
    monkeypatch.setenv("VAPI_WEBHOOK_SECRET", "vapi-secret-abc")
    assert get_webhook_secret_from_env("vapi") == "vapi-secret-abc"


def test_get_webhook_secret_reads_n8n_secret(monkeypatch):
    """Test 6 — Reads N8N_WEBHOOK_SECRET for provider 'n8n'."""
    monkeypatch.setenv("N8N_WEBHOOK_SECRET", "n8n-secret-xyz")
    assert get_webhook_secret_from_env("n8n") == "n8n-secret-xyz"


def test_get_webhook_secret_raises_when_missing(monkeypatch):
    """Test 7 — Raises MissingWebhookSecretError when env var is absent."""
    monkeypatch.delenv("VAPI_WEBHOOK_SECRET", raising=False)
    with pytest.raises(MissingWebhookSecretError):
        get_webhook_secret_from_env("vapi")


# ===========================================================================
# normalize_signature_header (tests 8–11)
# ===========================================================================


def test_normalize_signature_header_accepts_plain_digest():
    """Test 8 — A plain hex digest is returned as-is."""
    digest = "abc123def456"
    assert normalize_signature_header(digest) == digest


def test_normalize_signature_header_accepts_sha256_prefixed():
    """Test 9 — 'sha256=<digest>' prefix is stripped; raw digest returned."""
    digest = "abc123def456"
    assert normalize_signature_header(f"sha256={digest}") == digest


def test_normalize_signature_header_rejects_none():
    """Test 10 — None raises InvalidWebhookSignatureError."""
    with pytest.raises(InvalidWebhookSignatureError):
        normalize_signature_header(None)


def test_normalize_signature_header_rejects_empty():
    """Test 11 — Empty / whitespace-only string raises InvalidWebhookSignatureError."""
    with pytest.raises(InvalidWebhookSignatureError):
        normalize_signature_header("")
    with pytest.raises(InvalidWebhookSignatureError):
        normalize_signature_header("   ")


# ===========================================================================
# compute_hmac_sha256_signature (tests 12–14)
# ===========================================================================


def test_compute_hmac_sha256_signature_deterministic():
    """Test 12 — Same inputs always produce the same digest."""
    digest1 = compute_hmac_sha256_signature(PAYLOAD, SECRET)
    digest2 = compute_hmac_sha256_signature(PAYLOAD, SECRET)
    assert digest1 == digest2
    assert digest1 == _expected_digest(PAYLOAD, SECRET)


def test_compute_hmac_sha256_signature_rejects_non_bytes():
    """Test 13 — Non-bytes payload raises WebhookSignatureError."""
    with pytest.raises(WebhookSignatureError):
        compute_hmac_sha256_signature("not bytes", SECRET)  # type: ignore[arg-type]


def test_compute_hmac_sha256_signature_rejects_empty_secret():
    """Test 14 — Empty secret raises WebhookSignatureError."""
    with pytest.raises(WebhookSignatureError):
        compute_hmac_sha256_signature(PAYLOAD, "")


# ===========================================================================
# verify_hmac_sha256_signature (tests 15–17)
# ===========================================================================


def test_verify_hmac_sha256_signature_returns_true_for_valid():
    """Test 15 — Returns True when the plain digest matches."""
    sig = compute_hmac_sha256_signature(PAYLOAD, SECRET)
    assert verify_hmac_sha256_signature(PAYLOAD, sig, SECRET) is True


def test_verify_hmac_sha256_signature_returns_true_for_prefixed():
    """Test 16 — Returns True when the sha256-prefixed digest matches."""
    sig = "sha256=" + compute_hmac_sha256_signature(PAYLOAD, SECRET)
    assert verify_hmac_sha256_signature(PAYLOAD, sig, SECRET) is True


def test_verify_hmac_sha256_signature_raises_for_invalid():
    """Test 17 — Raises InvalidWebhookSignatureError for a wrong digest."""
    with pytest.raises(InvalidWebhookSignatureError):
        verify_hmac_sha256_signature(PAYLOAD, "sha256=deadbeef00000000", SECRET)


# ===========================================================================
# verify_provider_webhook_signature (tests 18–20)
# ===========================================================================


def test_verify_provider_webhook_signature_with_explicit_secret():
    """Test 18 — Uses the caller-supplied secret when provided."""
    sig = compute_hmac_sha256_signature(PAYLOAD, SECRET)
    assert verify_provider_webhook_signature("vapi", PAYLOAD, sig, secret=SECRET) is True


def test_verify_provider_webhook_signature_loads_secret_from_env(monkeypatch):
    """Test 19 — Loads secret from env when secret=None."""
    monkeypatch.setenv("VAPI_WEBHOOK_SECRET", SECRET)
    sig = compute_hmac_sha256_signature(PAYLOAD, SECRET)
    assert verify_provider_webhook_signature("vapi", PAYLOAD, sig) is True


def test_verify_provider_webhook_signature_rejects_invalid_provider():
    """Test 20 — Raises WebhookSignatureError for an unknown provider."""
    with pytest.raises(WebhookSignatureError):
        verify_provider_webhook_signature("stripe", PAYLOAD, "sig", secret=SECRET)


# ===========================================================================
# Safety checks (tests 21–23)
# ===========================================================================


def test_no_database_usage():
    """Test 21 — Core module does not import any database modules."""
    import backend.app.core.webhook_signature as mod
    import sys
    db_modules = [k for k in sys.modules if "asyncpg" in k or "sqlalchemy" in k]
    # If any db modules are present in sys.modules they were loaded by other tests,
    # not by this module. Verify webhook_signature does not import them directly.
    source = mod.__file__
    content = open(source).read()
    assert "import asyncpg" not in content
    assert "import sqlalchemy" not in content


def test_no_external_service_calls():
    """Test 22 — Core module does not import requests or httpx."""
    import backend.app.core.webhook_signature as mod
    content = open(mod.__file__).read()
    assert "import requests" not in content
    assert "import httpx" not in content


def test_no_real_secrets_hardcoded():
    """Test 23 — Core module does not contain hard-coded secret values."""
    import backend.app.core.webhook_signature as mod
    content = open(mod.__file__).read().lower()
    forbidden = ["prod_secret", "real_password", "sk-", "api_key="]
    for token in forbidden:
        assert token not in content, f"Possible hard-coded secret: {token!r}"
