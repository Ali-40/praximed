"""
Static contract tests for Sprint 12 / Module 92 — Environment and Secrets Contract.

Verifies:
- Contract doc exists and covers required content
- backend/.env.example completeness and placeholder safety
- frontend/.env.example existence and content
- Key security rules mentioned in the contract
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

_CONTRACT_PATH = os.path.join(
    _REPO_ROOT, "docs", "deployment", "ENVIRONMENT_AND_SECRETS_CONTRACT.md"
)

_BACKEND_ENV_EXAMPLE = os.path.join(_REPO_ROOT, "backend", ".env.example")
_FRONTEND_ENV_EXAMPLE = os.path.join(_REPO_ROOT, "frontend", ".env.example")


def _contract() -> str:
    with open(_CONTRACT_PATH, encoding="utf-8") as f:
        return f.read()


def _backend_env() -> str:
    with open(_BACKEND_ENV_EXAMPLE, encoding="utf-8") as f:
        return f.read()


def _frontend_env() -> str:
    with open(_FRONTEND_ENV_EXAMPLE, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. Contract document exists
# ---------------------------------------------------------------------------


def test_contract_doc_exists() -> None:
    assert os.path.isfile(_CONTRACT_PATH), (
        f"Contract doc not found at {_CONTRACT_PATH}"
    )


def test_contract_doc_not_empty() -> None:
    assert len(_contract()) > 1000


# ---------------------------------------------------------------------------
# 2. Contract mentions all required backend env vars
# ---------------------------------------------------------------------------


def test_contract_mentions_database_url() -> None:
    assert "DATABASE_URL" in _contract()


def test_contract_mentions_jwt_secret_key() -> None:
    assert "JWT_SECRET_KEY" in _contract()


def test_contract_mentions_vapi_webhook_secret() -> None:
    assert "VAPI_WEBHOOK_SECRET" in _contract()


def test_contract_mentions_n8n_webhook_secret() -> None:
    assert "N8N_WEBHOOK_SECRET" in _contract()


def test_contract_mentions_internal_webhook_secret() -> None:
    assert "INTERNAL_WEBHOOK_SECRET" in _contract()


def test_contract_mentions_frontend_cors_origins() -> None:
    assert "FRONTEND_CORS_ORIGINS" in _contract()


def test_contract_mentions_postgres_db() -> None:
    assert "POSTGRES_DB" in _contract()


def test_contract_mentions_postgres_user() -> None:
    assert "POSTGRES_USER" in _contract()


def test_contract_mentions_postgres_password() -> None:
    assert "POSTGRES_PASSWORD" in _contract()


# ---------------------------------------------------------------------------
# 3. Contract mentions NEXT_PUBLIC_API_BASE_URL (frontend var)
# ---------------------------------------------------------------------------


def test_contract_mentions_next_public_api_base_url() -> None:
    assert "NEXT_PUBLIC_API_BASE_URL" in _contract()


# ---------------------------------------------------------------------------
# 4. Contract covers all four deployment tiers
# ---------------------------------------------------------------------------


def test_contract_mentions_local_tier() -> None:
    text = _contract()
    assert "local" in text.lower() or "Local" in text


def test_contract_mentions_test_or_ci_tier() -> None:
    text = _contract()
    assert "CI" in text or "Test / CI" in text or "test/ci" in text.lower()


def test_contract_mentions_staging_tier() -> None:
    assert "staging" in _contract().lower() or "Staging" in _contract()


def test_contract_mentions_production_tier() -> None:
    assert "production" in _contract().lower() or "Production" in _contract()


# ---------------------------------------------------------------------------
# 5. Security rules in contract
# ---------------------------------------------------------------------------


def test_contract_mentions_no_real_secrets() -> None:
    text = _contract()
    assert "no real secret" in text.lower() or "never commit" in text.lower() or "must never" in text.lower()


def test_contract_mentions_no_wildcard_cors() -> None:
    text = _contract()
    assert "wildcard" in text.lower() and ("cors" in text.lower() or "origin" in text.lower())


def test_contract_mentions_no_ngrok_in_production() -> None:
    text = _contract()
    assert "ngrok" in text.lower() and "production" in text.lower()


def test_contract_mentions_stable_https_url() -> None:
    text = _contract()
    assert "stable" in text.lower() and "https" in text.lower()


def test_contract_mentions_secret_rotation() -> None:
    text = _contract()
    assert "rotat" in text.lower()


def test_contract_mentions_managed_postgres() -> None:
    text = _contract()
    assert "managed" in text.lower() and "postgres" in text.lower()


def test_contract_mentions_no_seed_data_in_production() -> None:
    text = _contract()
    assert "seed" in text.lower() and "production" in text.lower()


def test_contract_mentions_vapi_scope_singular() -> None:
    assert "vapi:tool" in _contract()


def test_contract_mentions_clinic_id_from_trusted_header() -> None:
    text = _contract()
    assert "machine auth header" in text.lower() or "X-Vapi-Clinic-Id" in text


def test_contract_mentions_no_raw_payload_logging() -> None:
    text = _contract()
    assert "log" in text.lower() and (
        "raw" in text.lower() or "PHI" in text or "patient" in text.lower()
    )


def test_contract_mentions_no_production_deployment_in_module() -> None:
    text = _contract()
    assert "no production deployment" in text.lower() or "not a deployment" in text.lower()


# ---------------------------------------------------------------------------
# 6. backend/.env.example completeness
# ---------------------------------------------------------------------------


def test_backend_env_example_exists() -> None:
    assert os.path.isfile(_BACKEND_ENV_EXAMPLE)


def test_backend_env_example_contains_database_url() -> None:
    assert "DATABASE_URL" in _backend_env()


def test_backend_env_example_contains_jwt_secret_key() -> None:
    assert "JWT_SECRET_KEY" in _backend_env()


def test_backend_env_example_contains_vapi_webhook_secret() -> None:
    assert "VAPI_WEBHOOK_SECRET" in _backend_env()


def test_backend_env_example_contains_n8n_webhook_secret() -> None:
    assert "N8N_WEBHOOK_SECRET" in _backend_env()


def test_backend_env_example_contains_internal_webhook_secret() -> None:
    assert "INTERNAL_WEBHOOK_SECRET" in _backend_env()


def test_backend_env_example_contains_frontend_cors_origins() -> None:
    assert "FRONTEND_CORS_ORIGINS" in _backend_env()


def test_backend_env_example_jwt_is_placeholder() -> None:
    for line in _backend_env().splitlines():
        if line.startswith("JWT_SECRET_KEY="):
            value = line.split("=", 1)[1].strip()
            assert any(m in value for m in ("change", "local", "placeholder")), (
                f"JWT_SECRET_KEY appears non-placeholder: {value!r}"
            )


def test_backend_env_example_vapi_secret_is_placeholder() -> None:
    for line in _backend_env().splitlines():
        if line.startswith("VAPI_WEBHOOK_SECRET="):
            value = line.split("=", 1)[1].strip()
            assert any(m in value for m in ("change", "local", "placeholder")), (
                f"VAPI_WEBHOOK_SECRET appears non-placeholder: {value!r}"
            )


def test_backend_env_example_no_real_api_keys() -> None:
    real_key_pattern = re.compile(r"sk-[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{50,}")
    matches = real_key_pattern.findall(_backend_env())
    assert not matches, f"Possible real key found in backend/.env.example: {matches}"


# ---------------------------------------------------------------------------
# 7. frontend/.env.example
# ---------------------------------------------------------------------------


def test_frontend_env_example_exists() -> None:
    assert os.path.isfile(_FRONTEND_ENV_EXAMPLE), (
        f"frontend/.env.example not found at {_FRONTEND_ENV_EXAMPLE}"
    )


def test_frontend_env_example_contains_next_public_api_base_url() -> None:
    assert "NEXT_PUBLIC_API_BASE_URL" in _frontend_env()


def test_frontend_env_example_no_jwt_secret() -> None:
    assert "JWT_SECRET_KEY" not in _frontend_env()


def test_frontend_env_example_no_webhook_secrets() -> None:
    text = _frontend_env()
    assert "VAPI_WEBHOOK_SECRET" not in text
    assert "N8N_WEBHOOK_SECRET" not in text
    assert "INTERNAL_WEBHOOK_SECRET" not in text


def test_frontend_env_example_no_database_url() -> None:
    assert "DATABASE_URL" not in _frontend_env()


def test_frontend_env_example_local_value_is_localhost() -> None:
    for line in _frontend_env().splitlines():
        if line.startswith("NEXT_PUBLIC_API_BASE_URL="):
            value = line.split("=", 1)[1].strip()
            assert "127.0.0.1" in value or "localhost" in value, (
                f"NEXT_PUBLIC_API_BASE_URL example value should be localhost: {value!r}"
            )
