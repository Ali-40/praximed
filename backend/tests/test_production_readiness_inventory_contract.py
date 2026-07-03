"""
Static contract tests for Sprint 12 / Module 91 — Production Readiness Inventory.

Verifies:
- Inventory document exists
- .env.example exists and contains key env var names
- No real secrets in .env.example
- Inventory mentions required env vars from main.py
- Inventory mentions critical production components
"""

from __future__ import annotations

import os
import re


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

_INVENTORY_PATH = os.path.join(
    _REPO_ROOT, "docs", "deployment", "PRODUCTION_READINESS_INVENTORY.md"
)

_ENV_EXAMPLE_PATH = os.path.join(_REPO_ROOT, "backend", ".env.example")


def _inventory_text() -> str:
    with open(_INVENTORY_PATH, encoding="utf-8") as f:
        return f.read()


def _env_example_text() -> str:
    with open(_ENV_EXAMPLE_PATH, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. Inventory document exists
# ---------------------------------------------------------------------------


def test_inventory_doc_exists() -> None:
    assert os.path.isfile(_INVENTORY_PATH), (
        f"Inventory doc not found at {_INVENTORY_PATH}"
    )


def test_inventory_doc_not_empty() -> None:
    text = _inventory_text()
    assert len(text) > 500, "Inventory doc appears too short to be complete"


# ---------------------------------------------------------------------------
# 2. .env.example exists and contains required env var names
# ---------------------------------------------------------------------------


def test_env_example_exists() -> None:
    assert os.path.isfile(_ENV_EXAMPLE_PATH), (
        f".env.example not found at {_ENV_EXAMPLE_PATH}"
    )


def test_env_example_contains_database_url() -> None:
    assert "DATABASE_URL" in _env_example_text()


def test_env_example_contains_jwt_secret_key() -> None:
    assert "JWT_SECRET_KEY" in _env_example_text()


def test_env_example_contains_vapi_webhook_secret() -> None:
    assert "VAPI_WEBHOOK_SECRET" in _env_example_text()


def test_env_example_contains_n8n_webhook_secret() -> None:
    assert "N8N_WEBHOOK_SECRET" in _env_example_text()


def test_env_example_contains_internal_webhook_secret() -> None:
    assert "INTERNAL_WEBHOOK_SECRET" in _env_example_text()


def test_env_example_contains_frontend_cors_origins() -> None:
    assert "FRONTEND_CORS_ORIGINS" in _env_example_text()


# ---------------------------------------------------------------------------
# 3. No real secrets in .env.example
# ---------------------------------------------------------------------------

_REAL_SECRET_PATTERNS = [
    r"sk-[A-Za-z0-9]{20,}",          # OpenAI / Anthropic key patterns
    r"[A-Za-z0-9+/]{40,}={0,2}$",    # base64-encoded secret of realistic length
    r"eyJ[A-Za-z0-9_-]{50,}",         # JWT token (base64url header)
]

_PLACEHOLDER_MARKERS = [
    "change-me",
    "change-in-production",
    "placeholder",
    "local-dev",
    "local_password",
]


def test_env_example_jwt_secret_is_placeholder() -> None:
    text = _env_example_text()
    for line in text.splitlines():
        if line.startswith("JWT_SECRET_KEY="):
            value = line.split("=", 1)[1].strip()
            assert any(marker in value for marker in _PLACEHOLDER_MARKERS), (
                f"JWT_SECRET_KEY value does not look like a placeholder: {value!r}"
            )


def test_env_example_vapi_secret_is_placeholder() -> None:
    text = _env_example_text()
    for line in text.splitlines():
        if line.startswith("VAPI_WEBHOOK_SECRET="):
            value = line.split("=", 1)[1].strip()
            assert any(marker in value for marker in _PLACEHOLDER_MARKERS), (
                f"VAPI_WEBHOOK_SECRET value does not look like a placeholder: {value!r}"
            )


def test_env_example_n8n_secret_is_placeholder() -> None:
    text = _env_example_text()
    for line in text.splitlines():
        if line.startswith("N8N_WEBHOOK_SECRET="):
            value = line.split("=", 1)[1].strip()
            assert any(marker in value for marker in _PLACEHOLDER_MARKERS), (
                f"N8N_WEBHOOK_SECRET value does not look like a placeholder: {value!r}"
            )


def test_env_example_db_password_is_placeholder() -> None:
    text = _env_example_text()
    for line in text.splitlines():
        if line.startswith("POSTGRES_PASSWORD="):
            value = line.split("=", 1)[1].strip()
            assert "local" in value.lower() or "change" in value.lower(), (
                f"POSTGRES_PASSWORD does not look like a local placeholder: {value!r}"
            )


def test_env_example_no_real_api_keys() -> None:
    text = _env_example_text()
    for pattern in _REAL_SECRET_PATTERNS:
        matches = re.findall(pattern, text, re.MULTILINE)
        assert not matches, (
            f"Possible real secret found in .env.example matching {pattern!r}: {matches}"
        )


# ---------------------------------------------------------------------------
# 4. Inventory mentions all required env vars from main.py
# ---------------------------------------------------------------------------


def test_inventory_mentions_database_url() -> None:
    assert "DATABASE_URL" in _inventory_text()


def test_inventory_mentions_frontend_cors_origins() -> None:
    assert "FRONTEND_CORS_ORIGINS" in _inventory_text()


def test_inventory_mentions_jwt_secret_key() -> None:
    assert "JWT_SECRET_KEY" in _inventory_text()


def test_inventory_mentions_vapi_webhook_secret() -> None:
    assert "VAPI_WEBHOOK_SECRET" in _inventory_text()


def test_inventory_mentions_n8n_webhook_secret() -> None:
    assert "N8N_WEBHOOK_SECRET" in _inventory_text()


def test_inventory_mentions_internal_webhook_secret() -> None:
    assert "INTERNAL_WEBHOOK_SECRET" in _inventory_text()


def test_inventory_mentions_next_public_api_base_url() -> None:
    assert "NEXT_PUBLIC_API_BASE_URL" in _inventory_text()


# ---------------------------------------------------------------------------
# 5. Inventory mentions critical production components
# ---------------------------------------------------------------------------


def test_inventory_mentions_postgresql() -> None:
    assert "PostgreSQL" in _inventory_text() or "postgresql" in _inventory_text()


def test_inventory_mentions_jwt() -> None:
    assert "JWT" in _inventory_text()


def test_inventory_mentions_cors() -> None:
    assert "CORS" in _inventory_text()


def test_inventory_mentions_vapi() -> None:
    assert "Vapi" in _inventory_text() or "VAPI" in _inventory_text()


def test_inventory_mentions_https() -> None:
    assert "HTTPS" in _inventory_text() or "https" in _inventory_text()


def test_inventory_mentions_production_blockers() -> None:
    text = _inventory_text()
    assert "blocker" in text.lower() or "Blocker" in text, (
        "Inventory does not contain a production blockers section"
    )


def test_inventory_mentions_tls() -> None:
    text = _inventory_text()
    assert "TLS" in text or "tls" in text or "HTTPS" in text


def test_inventory_mentions_session_storage_risk() -> None:
    text = _inventory_text()
    assert "sessionStorage" in text or "session_storage" in text or "httpOnly" in text
