"""
Unit tests for webhook provider config — PraxisMed Sprint 6 / Module 53

Strategy:
- No FastAPI imports.
- No database connection.
- No external service calls.
- monkeypatch for env var reads.
"""

from __future__ import annotations

import pytest

from backend.app.core.webhook_provider_config import (
    InvalidWebhookProviderConfigError,
    WebhookProviderConfig,
    extract_signature_from_headers,
    get_default_provider_config,
    get_provider_secret_from_env,
    get_signature_env_var,
    get_signature_header_names,
)
from backend.app.core.webhook_signature import MissingWebhookSecretError


# ===========================================================================
# WebhookProviderConfig validation (tests 1–7)
# ===========================================================================


def test_config_accepts_valid_vapi_config():
    """Test 1 — Valid vapi config is created without errors."""
    cfg = WebhookProviderConfig(
        provider="vapi",
        signature_header_names=("X-Vapi-Signature",),
        signature_env_var="VAPI_WEBHOOK_SECRET",
    )
    assert cfg.provider == "vapi"
    assert cfg.algorithm == "hmac-sha256"
    assert "sha256=" in cfg.accepted_signature_prefixes


def test_config_rejects_empty_provider():
    """Test 2 — Empty provider raises InvalidWebhookProviderConfigError."""
    with pytest.raises(InvalidWebhookProviderConfigError):
        WebhookProviderConfig(
            provider="",
            signature_header_names=("X-Vapi-Signature",),
            signature_env_var="VAPI_WEBHOOK_SECRET",
        )


def test_config_rejects_invalid_provider():
    """Test 3 — Unknown provider raises InvalidWebhookProviderConfigError."""
    with pytest.raises(InvalidWebhookProviderConfigError):
        WebhookProviderConfig(
            provider="unknown_provider",
            signature_header_names=("X-Signature",),
            signature_env_var="SOME_SECRET",
        )


def test_config_rejects_empty_signature_header_names():
    """Test 4 — Empty signature_header_names tuple raises InvalidWebhookProviderConfigError."""
    with pytest.raises(InvalidWebhookProviderConfigError):
        WebhookProviderConfig(
            provider="vapi",
            signature_header_names=(),
            signature_env_var="VAPI_WEBHOOK_SECRET",
        )


def test_config_rejects_empty_string_in_signature_header_names():
    """Test 5 — Empty string inside signature_header_names raises InvalidWebhookProviderConfigError."""
    with pytest.raises(InvalidWebhookProviderConfigError):
        WebhookProviderConfig(
            provider="vapi",
            signature_header_names=("X-Vapi-Signature", ""),
            signature_env_var="VAPI_WEBHOOK_SECRET",
        )


def test_config_rejects_empty_signature_env_var():
    """Test 6 — Empty signature_env_var raises InvalidWebhookProviderConfigError."""
    with pytest.raises(InvalidWebhookProviderConfigError):
        WebhookProviderConfig(
            provider="vapi",
            signature_header_names=("X-Vapi-Signature",),
            signature_env_var="",
        )


def test_config_rejects_unsupported_algorithm():
    """Test 7 — algorithm other than 'hmac-sha256' raises InvalidWebhookProviderConfigError."""
    with pytest.raises(InvalidWebhookProviderConfigError):
        WebhookProviderConfig(
            provider="vapi",
            signature_header_names=("X-Vapi-Signature",),
            signature_env_var="VAPI_WEBHOOK_SECRET",
            algorithm="md5",
        )


# ===========================================================================
# get_default_provider_config (tests 8–10)
# ===========================================================================


def test_get_default_provider_config_returns_vapi_config():
    """Test 8 — get_default_provider_config returns correct vapi config."""
    cfg = get_default_provider_config("vapi")
    assert cfg.provider == "vapi"
    assert cfg.signature_env_var == "VAPI_WEBHOOK_SECRET"
    assert "X-Vapi-Signature" in cfg.signature_header_names


def test_get_default_provider_config_returns_n8n_config():
    """Test 9 — get_default_provider_config returns correct n8n config."""
    cfg = get_default_provider_config("n8n")
    assert cfg.provider == "n8n"
    assert cfg.signature_env_var == "N8N_WEBHOOK_SECRET"
    assert "X-N8N-Signature" in cfg.signature_header_names


def test_get_default_provider_config_returns_internal_config():
    """Test 10 — get_default_provider_config returns correct internal config."""
    cfg = get_default_provider_config("internal")
    assert cfg.provider == "internal"
    assert cfg.signature_env_var == "INTERNAL_WEBHOOK_SECRET"
    assert "X-Internal-Signature" in cfg.signature_header_names


# ===========================================================================
# get_signature_header_names / get_signature_env_var (tests 11–12)
# ===========================================================================


def test_get_signature_header_names_returns_tuple():
    """Test 11 — get_signature_header_names returns a tuple for vapi."""
    names = get_signature_header_names("vapi")
    assert isinstance(names, tuple)
    assert len(names) >= 1
    assert "X-Vapi-Signature" in names


def test_get_signature_env_var_returns_correct_var_for_vapi():
    """Test 12 — get_signature_env_var returns VAPI_WEBHOOK_SECRET for vapi."""
    assert get_signature_env_var("vapi") == "VAPI_WEBHOOK_SECRET"


# ===========================================================================
# extract_signature_from_headers (tests 13–18)
# ===========================================================================


def test_extract_reads_primary_vapi_header():
    """Test 13 — extract_signature_from_headers reads X-Vapi-Signature."""
    headers = {"X-Vapi-Signature": "sha256=abc123"}
    result = extract_signature_from_headers(headers, "vapi")
    assert result == "sha256=abc123"


def test_extract_reads_vapi_alias_header():
    """Test 14 — extract_signature_from_headers reads alias X-Vapi-Hmac-Sha256."""
    headers = {"X-Vapi-Hmac-Sha256": "sha256=deadbeef"}
    result = extract_signature_from_headers(headers, "vapi")
    assert result == "sha256=deadbeef"


def test_extract_is_case_insensitive():
    """Test 15 — extract_signature_from_headers matches header names case-insensitively."""
    headers = {"x-vapi-signature": "sha256=lower123"}
    result = extract_signature_from_headers(headers, "vapi")
    assert result == "sha256=lower123"


def test_extract_returns_none_when_no_matching_header():
    """Test 16 — extract_signature_from_headers returns None when no accepted header present."""
    headers = {"Authorization": "Bearer token", "Content-Type": "application/json"}
    result = extract_signature_from_headers(headers, "vapi")
    assert result is None


def test_extract_allows_duplicate_headers_with_same_value():
    """Test 17 — extract_signature_from_headers allows two accepted headers with identical values."""
    headers = {
        "X-Vapi-Signature": "sha256=abc",
        "X-Vapi-Hmac-Sha256": "sha256=abc",
    }
    result = extract_signature_from_headers(headers, "vapi")
    assert result == "sha256=abc"


def test_extract_rejects_duplicate_headers_with_different_values():
    """Test 18 — extract_signature_from_headers raises when accepted headers have conflicting values."""
    headers = {
        "X-Vapi-Signature": "sha256=abc",
        "X-Vapi-Hmac-Sha256": "sha256=xyz",
    }
    with pytest.raises(InvalidWebhookProviderConfigError):
        extract_signature_from_headers(headers, "vapi")


# ===========================================================================
# get_provider_secret_from_env (tests 19–20)
# ===========================================================================


def test_get_provider_secret_from_env_reads_env_var(monkeypatch):
    """Test 19 — get_provider_secret_from_env reads VAPI_WEBHOOK_SECRET from env."""
    monkeypatch.setenv("VAPI_WEBHOOK_SECRET", "my-test-secret")
    secret = get_provider_secret_from_env("vapi")
    assert secret == "my-test-secret"


def test_get_provider_secret_from_env_raises_when_missing(monkeypatch):
    """Test 20 — get_provider_secret_from_env raises MissingWebhookSecretError when env var absent."""
    monkeypatch.delenv("VAPI_WEBHOOK_SECRET", raising=False)
    with pytest.raises(MissingWebhookSecretError):
        get_provider_secret_from_env("vapi")


# ===========================================================================
# Safety (test 21)
# ===========================================================================


def test_config_module_does_not_contain_real_secrets():
    """Test 21 — Config module source does not contain hardcoded real secrets."""
    import backend.app.core.webhook_provider_config as mod

    content = open(mod.__file__).read()
    forbidden = [
        "sk-",
        "Bearer ",
        "password",
        "prod-secret",
        "real-secret",
    ]
    for marker in forbidden:
        assert marker not in content, (
            f"Possible real secret marker {marker!r} found in webhook_provider_config.py"
        )
