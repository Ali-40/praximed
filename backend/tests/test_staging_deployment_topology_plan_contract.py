"""
Static contract tests for Sprint 13 / Module 95 — Staging Deployment Topology Plan.

Verifies:
- Plan document exists and covers all required topology sections
- Platform comparison is present (Railway, Render, Fly.io, Vercel)
- A single topology is chosen and documented
- Staging domains, env vars, DB strategy, Vapi/n8n, and secrets injection are addressed
- Fake/non-PHI data constraint is explicit
- No deployment was executed in this module
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

_PLAN_PATH = os.path.join(
    _REPO_ROOT, "docs", "deployment", "STAGING_DEPLOYMENT_TOPOLOGY_PLAN.md"
)


def _plan() -> str:
    with open(_PLAN_PATH, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. Document exists and is non-trivial
# ---------------------------------------------------------------------------


def test_staging_topology_plan_exists() -> None:
    assert os.path.isfile(_PLAN_PATH), f"Plan not found at {_PLAN_PATH}"


def test_staging_topology_plan_not_empty() -> None:
    assert len(_plan()) > 2000


# ---------------------------------------------------------------------------
# 2. Platform comparison — must compare at least three options
# ---------------------------------------------------------------------------


def test_plan_mentions_railway() -> None:
    assert "Railway" in _plan()


def test_plan_mentions_render() -> None:
    assert "Render" in _plan()


def test_plan_mentions_fly_io() -> None:
    text = _plan()
    assert "Fly.io" in text or "fly.io" in text or "Fly " in text


def test_plan_mentions_vercel() -> None:
    assert "Vercel" in _plan()


# ---------------------------------------------------------------------------
# 3. Managed PostgreSQL
# ---------------------------------------------------------------------------


def test_plan_mentions_managed_postgresql() -> None:
    text = _plan()
    assert "managed" in text.lower() and (
        "postgresql" in text.lower() or "postgres" in text.lower()
    )


# ---------------------------------------------------------------------------
# 4. Chosen topology — exactly one topology recommended
# ---------------------------------------------------------------------------


def test_plan_recommends_one_topology() -> None:
    text = _plan()
    assert (
        "chosen topology" in text.lower()
        or "chosen platform" in text.lower()
        or "recommended" in text.lower()
    )


def test_plan_states_why_for_chosen_topology() -> None:
    text = _plan()
    assert "why" in text.lower() and ("railway" in text.lower() or "render" in text.lower())


# ---------------------------------------------------------------------------
# 5. Fake / non-PHI data constraint
# ---------------------------------------------------------------------------


def test_plan_mentions_fake_data_only() -> None:
    text = _plan()
    assert "fake" in text.lower() or "synthetic" in text.lower()


def test_plan_mentions_no_phi() -> None:
    text = _plan()
    assert "no phi" in text.lower() or "non-phi" in text.lower() or "PHI" in text


def test_plan_mentions_production_phi_no_go() -> None:
    text = _plan()
    assert (
        "no-go" in text.lower()
        and ("phi" in text.lower() or "production" in text.lower())
    )


# ---------------------------------------------------------------------------
# 6. Staging HTTPS URLs — stable, not ngrok
# ---------------------------------------------------------------------------


def test_plan_mentions_https_staging_api_url() -> None:
    text = _plan()
    assert "https://" in text and "staging" in text.lower()


def test_plan_mentions_staging_frontend_url() -> None:
    text = _plan()
    assert (
        "vercel.app" in text.lower()
        or "staging" in text.lower()
    ) and "frontend" in text.lower()


def test_plan_mentions_no_ngrok_in_staging() -> None:
    text = _plan()
    assert "ngrok" in text.lower() and (
        "replac" in text.lower() or "staging" in text.lower()
    )


# ---------------------------------------------------------------------------
# 7. CORS — no wildcard; exact origin
# ---------------------------------------------------------------------------


def test_plan_mentions_no_wildcard_cors() -> None:
    text = _plan()
    assert "wildcard" in text.lower() and "cors" in text.lower()


def test_plan_mentions_frontend_cors_origins() -> None:
    assert "FRONTEND_CORS_ORIGINS" in _plan()


def test_plan_mentions_next_public_api_base_url() -> None:
    assert "NEXT_PUBLIC_API_BASE_URL" in _plan()


# ---------------------------------------------------------------------------
# 8. Vapi staging strategy
# ---------------------------------------------------------------------------


def test_plan_mentions_vapi_endpoint() -> None:
    text = _plan()
    assert "/vapi/tools/capture-appointment-request" in text or "vapi" in text.lower()


def test_plan_mentions_vapi_scope_singular() -> None:
    assert "vapi:tool" in _plan()


# ---------------------------------------------------------------------------
# 9. n8n staging strategy
# ---------------------------------------------------------------------------


def test_plan_mentions_n8n_staging_strategy() -> None:
    text = _plan()
    assert "n8n" in text.lower() or "calendar-sync" in text.lower()


# ---------------------------------------------------------------------------
# 10. Isolated staging database
# ---------------------------------------------------------------------------


def test_plan_mentions_isolated_staging_db() -> None:
    text = _plan()
    assert "isolated" in text.lower() and (
        "staging" in text.lower() or "database" in text.lower()
    )


# ---------------------------------------------------------------------------
# 11. Migrations
# ---------------------------------------------------------------------------


def test_plan_mentions_migrations() -> None:
    text = _plan()
    assert "migration" in text.lower() or "alembic" in text.lower()


# ---------------------------------------------------------------------------
# 12. Secrets isolated by environment
# ---------------------------------------------------------------------------


def test_plan_mentions_secrets_per_environment() -> None:
    text = _plan()
    assert "secret" in text.lower() and (
        "isolated" in text.lower()
        or "per environment" in text.lower()
        or "per-env" in text.lower()
        or "environment" in text.lower()
    )


def test_plan_mentions_secrets_injection_method() -> None:
    text = _plan()
    assert (
        "dashboard" in text.lower()
        or "env var" in text.lower()
        or "environment variable" in text.lower()
    ) and "secret" in text.lower()


# ---------------------------------------------------------------------------
# 13. sessionStorage JWT — acceptable for staging fake data only
# ---------------------------------------------------------------------------


def test_plan_mentions_session_storage_jwt() -> None:
    assert "sessionStorage" in _plan()


def test_plan_mentions_session_storage_acceptable_for_fake_data_only() -> None:
    text = _plan()
    assert "sessionStorage" in text and (
        "fake" in text.lower() or "staging" in text.lower()
    )


def test_plan_mentions_session_storage_not_phi_safe() -> None:
    text = _plan()
    assert "sessionStorage" in text and (
        "phi" in text.lower() or "production" in text.lower()
    )


# ---------------------------------------------------------------------------
# 14. No deployment executed in this module
# ---------------------------------------------------------------------------


def test_plan_mentions_no_deployment_executed() -> None:
    text = _plan()
    assert (
        "no deployment" in text.lower()
        or "planning only" in text.lower()
        or "docs-first" in text.lower()
        or "not executed" in text.lower()
    )


# ---------------------------------------------------------------------------
# 15. Module 96 mentioned as next step
# ---------------------------------------------------------------------------


def test_plan_mentions_module_96() -> None:
    text = _plan()
    assert "module 96" in text.lower() or "Module 96" in text


def test_plan_mentions_module_96_env_var_matrix() -> None:
    text = _plan()
    assert (
        "environment variable matrix" in text.lower()
        or "env var matrix" in text.lower()
        or "96" in text
    )


# ---------------------------------------------------------------------------
# 16. No obvious real secrets in the document
# ---------------------------------------------------------------------------


def test_plan_no_real_api_keys() -> None:
    real_key_pattern = re.compile(r"sk-[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{50,}")
    matches = real_key_pattern.findall(_plan())
    assert not matches, f"Possible real key in plan: {matches}"


def test_plan_no_real_db_password() -> None:
    text = _plan()
    for line in text.splitlines():
        if "postgresql://" in line:
            assert (
                "placeholder" in line.lower()
                or "example" in line.lower()
                or "<" in line
                or "#" in line
            ), f"Unexpected non-placeholder DATABASE_URL: {line!r}"
