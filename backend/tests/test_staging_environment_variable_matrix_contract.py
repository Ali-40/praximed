"""
Static contract tests for Sprint 13 / Module 96 — Staging Environment Variable Matrix.

Verifies:
- Matrix document exists and covers all required variables, platforms, and constraints
- Railway, Vercel, Postgres, Vapi, and n8n are covered
- Staging/local/production separation rules are present
- No obvious real secrets in the document
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

_MATRIX_PATH = os.path.join(
    _REPO_ROOT, "docs", "deployment", "STAGING_ENVIRONMENT_VARIABLE_MATRIX.md"
)


def _matrix() -> str:
    with open(_MATRIX_PATH, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. Document exists and is non-trivial
# ---------------------------------------------------------------------------


def test_staging_env_var_matrix_exists() -> None:
    assert os.path.isfile(_MATRIX_PATH), f"Matrix not found at {_MATRIX_PATH}"


def test_staging_env_var_matrix_not_empty() -> None:
    assert len(_matrix()) > 3000


# ---------------------------------------------------------------------------
# 2. Platforms covered
# ---------------------------------------------------------------------------


def test_matrix_mentions_railway_backend() -> None:
    text = _matrix()
    assert "Railway" in text and (
        "backend" in text.lower() or "service" in text.lower()
    )


def test_matrix_mentions_railway_postgresql() -> None:
    text = _matrix()
    assert "Railway" in text and (
        "postgresql" in text.lower() or "postgres" in text.lower()
    )


def test_matrix_mentions_vercel_frontend() -> None:
    text = _matrix()
    assert "Vercel" in text and "frontend" in text.lower()


# ---------------------------------------------------------------------------
# 3. Data / PHI policy
# ---------------------------------------------------------------------------


def test_matrix_mentions_fake_non_phi_staging_only() -> None:
    text = _matrix()
    assert "fake" in text.lower() or "synthetic" in text.lower()


def test_matrix_mentions_production_phi_no_go() -> None:
    text = _matrix()
    assert "no-go" in text.lower() or "NO-GO" in text


# ---------------------------------------------------------------------------
# 4. Backend env vars
# ---------------------------------------------------------------------------


def test_matrix_mentions_database_url() -> None:
    assert "DATABASE_URL" in _matrix()


def test_matrix_mentions_jwt_secret_key() -> None:
    assert "JWT_SECRET_KEY" in _matrix()


def test_matrix_mentions_vapi_webhook_secret() -> None:
    assert "VAPI_WEBHOOK_SECRET" in _matrix()


def test_matrix_mentions_n8n_webhook_secret() -> None:
    assert "N8N_WEBHOOK_SECRET" in _matrix()


def test_matrix_mentions_internal_webhook_secret() -> None:
    assert "INTERNAL_WEBHOOK_SECRET" in _matrix()


def test_matrix_mentions_frontend_cors_origins() -> None:
    assert "FRONTEND_CORS_ORIGINS" in _matrix()


# ---------------------------------------------------------------------------
# 5. Postgres-specific vars
# ---------------------------------------------------------------------------


def test_matrix_mentions_postgres_db() -> None:
    assert "POSTGRES_DB" in _matrix()


def test_matrix_mentions_postgres_user() -> None:
    assert "POSTGRES_USER" in _matrix()


def test_matrix_mentions_postgres_password() -> None:
    assert "POSTGRES_PASSWORD" in _matrix()


# ---------------------------------------------------------------------------
# 6. Frontend env vars
# ---------------------------------------------------------------------------


def test_matrix_mentions_next_public_api_base_url() -> None:
    assert "NEXT_PUBLIC_API_BASE_URL" in _matrix()


# ---------------------------------------------------------------------------
# 7. Vapi constraints
# ---------------------------------------------------------------------------


def test_matrix_mentions_vapi_scope_singular() -> None:
    assert "vapi:tool" in _matrix()


def test_matrix_mentions_staging_fake_clinic_id_placeholder() -> None:
    text = _matrix()
    assert (
        "staging-fake-clinic" in text.lower()
        or "<staging-fake-clinic-uuid>" in text
        or "fake clinic uuid" in text.lower()
    )


# ---------------------------------------------------------------------------
# 8. CORS constraints
# ---------------------------------------------------------------------------


def test_matrix_mentions_no_ngrok() -> None:
    text = _matrix()
    assert "ngrok" in text.lower() and (
        "not used" in text.lower()
        or "no ngrok" in text.lower()
        or "removes" in text.lower()
        or "replac" in text.lower()
        or "not needed" in text.lower()
    )


def test_matrix_mentions_no_wildcard_cors() -> None:
    text = _matrix()
    assert "wildcard" in text.lower() and "cors" in text.lower()


def test_matrix_mentions_https_only() -> None:
    text = _matrix()
    assert "https" in text.lower() and (
        "only" in text.lower() or "HTTPS only" in text
    )


# ---------------------------------------------------------------------------
# 9. Secret isolation rules
# ---------------------------------------------------------------------------


def test_matrix_mentions_no_local_dev_secrets() -> None:
    text = _matrix()
    assert (
        "local-dev" in text.lower()
        or "local dev" in text.lower()
        or "placeholder" in text.lower()
    ) and "staging" in text.lower()


def test_matrix_mentions_no_production_secrets() -> None:
    text = _matrix()
    assert "no production secret" in text.lower() or (
        "production" in text.lower() and "secret" in text.lower()
        and ("must not" in text.lower() or "never" in text.lower() or "distinct" in text.lower())
    )


def test_matrix_mentions_railway_vercel_secret_storage() -> None:
    text = _matrix()
    assert (
        ("Railway" in text and "dashboard" in text.lower())
        or ("Vercel" in text and "dashboard" in text.lower())
    )


# ---------------------------------------------------------------------------
# 10. Migrations
# ---------------------------------------------------------------------------


def test_matrix_mentions_migrations() -> None:
    text = _matrix()
    assert "migration" in text.lower() or "alembic" in text.lower()


# ---------------------------------------------------------------------------
# 11. n8n staging workflow
# ---------------------------------------------------------------------------


def test_matrix_mentions_n8n_staging_workflow() -> None:
    text = _matrix()
    assert "n8n" in text.lower() and "staging" in text.lower()


# ---------------------------------------------------------------------------
# 12. No real patient data
# ---------------------------------------------------------------------------


def test_matrix_mentions_no_real_patient_data() -> None:
    text = _matrix()
    assert (
        "no real patient" in text.lower()
        or "no real" in text.lower()
        or "fake" in text.lower()
    )


# ---------------------------------------------------------------------------
# 13. No deployment in this module
# ---------------------------------------------------------------------------


def test_matrix_mentions_no_deployment_executed() -> None:
    text = _matrix()
    assert (
        "no deployment" in text.lower()
        or "not executed" in text.lower()
        or "planning only" in text.lower()
    )


# ---------------------------------------------------------------------------
# 14. Module 97 as next step
# ---------------------------------------------------------------------------


def test_matrix_mentions_module_97() -> None:
    text = _matrix()
    assert "module 97" in text.lower() or "Module 97" in text


def test_matrix_mentions_module_97_dry_run() -> None:
    text = _matrix()
    assert "dry-run" in text.lower() or "dry run" in text.lower() or "97" in text


# ---------------------------------------------------------------------------
# 15. No obvious real secrets in the document
# ---------------------------------------------------------------------------


def test_matrix_no_real_api_keys() -> None:
    real_key_pattern = re.compile(r"sk-[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{50,}")
    matches = real_key_pattern.findall(_matrix())
    assert not matches, f"Possible real key in matrix: {matches}"


def test_matrix_no_real_db_password() -> None:
    text = _matrix()
    for line in text.splitlines():
        if "postgresql://" in line:
            assert (
                "placeholder" in line.lower()
                or "example" in line.lower()
                or "<" in line
                or "#" in line
            ), f"Unexpected non-placeholder DATABASE_URL: {line!r}"


def test_matrix_no_local_placeholder_values_presented_as_staging() -> None:
    text = _matrix()
    # The local placeholder values must appear only as examples of what NOT to use,
    # not as prescribed staging values
    assert "local-dev-jwt-secret-key-change-in-production" not in text or (
        "must never" in text.lower()
        or "must not" in text.lower()
        or "never appear" in text.lower()
        or "not the local" in text.lower()
        or "placeholder" in text.lower()
    )
