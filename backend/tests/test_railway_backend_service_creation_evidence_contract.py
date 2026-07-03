"""
Static contract tests for Sprint 16 / Module 112 — Railway Backend Service Creation
Evidence.

Verifies:
- Evidence doc exists and records PASS with real Railway service details
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

_EVIDENCE_PATH = os.path.join(
    _REPO_ROOT,
    "docs",
    "runtime",
    "RAILWAY_BACKEND_SERVICE_CREATION_EVIDENCE.md",
)


def _evidence() -> str:
    with open(_EVIDENCE_PATH, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. Doc existence
# ---------------------------------------------------------------------------


def test_evidence_doc_exists() -> None:
    assert os.path.isfile(_EVIDENCE_PATH), f"Evidence doc not found at {_EVIDENCE_PATH}"


def test_evidence_not_empty() -> None:
    assert len(_evidence()) > 1000


# ---------------------------------------------------------------------------
# 2. PASS result
# ---------------------------------------------------------------------------


def test_evidence_mentions_pass() -> None:
    assert "PASS" in _evidence().upper()


# ---------------------------------------------------------------------------
# 3. Railway service active
# ---------------------------------------------------------------------------


def test_evidence_mentions_railway_service_active() -> None:
    text = _evidence().lower()
    assert "active" in text or "online" in text or "running" in text


# ---------------------------------------------------------------------------
# 4. Railway URL
# ---------------------------------------------------------------------------


def test_evidence_mentions_railway_url() -> None:
    assert "web-production-fd91d.up.railway.app" in _evidence()


# ---------------------------------------------------------------------------
# 5. Health endpoint
# ---------------------------------------------------------------------------


def test_evidence_mentions_health_endpoint() -> None:
    assert "/health" in _evidence()


# ---------------------------------------------------------------------------
# 6. Health response body
# ---------------------------------------------------------------------------


def test_evidence_mentions_status_ok_response() -> None:
    text = _evidence().lower()
    assert (
        '"status":"ok"' in text
        or '"status": "ok"' in text
        or "status.*ok" in text
        or "status ok" in text
    )


# ---------------------------------------------------------------------------
# 7. Deployed commit
# ---------------------------------------------------------------------------


def test_evidence_mentions_commit_081121b() -> None:
    assert "081121b" in _evidence()


# ---------------------------------------------------------------------------
# 8. Root requirements.txt direct dependencies
# ---------------------------------------------------------------------------


def test_evidence_mentions_root_requirements_direct_deps() -> None:
    text = _evidence().lower()
    assert "requirements.txt" in text and (
        "direct" in text or "flat" in text or "directly" in text
    )


# ---------------------------------------------------------------------------
# 9. Procfile / start command
# ---------------------------------------------------------------------------


def test_evidence_mentions_procfile_or_start_command() -> None:
    text = _evidence().lower()
    assert "procfile" in text or "start command" in text or "backend.app.main" in text


# ---------------------------------------------------------------------------
# 10. Backend imports from repo root
# ---------------------------------------------------------------------------


def test_evidence_mentions_repo_root_imports() -> None:
    text = _evidence().lower()
    assert "repo root" in text or "backend.app.main" in text


# ---------------------------------------------------------------------------
# 11. Fake/non-PHI staging
# ---------------------------------------------------------------------------


def test_evidence_mentions_fake_non_phi_staging() -> None:
    text = _evidence().lower()
    assert ("fake" in text or "non-phi" in text) and "staging" in text


# ---------------------------------------------------------------------------
# 12. No real patient data
# ---------------------------------------------------------------------------


def test_evidence_mentions_no_real_patient_data() -> None:
    text = _evidence().lower()
    assert "no real patient" in text or (
        "real" in text and "patient" in text and (
            "not" in text or "no " in text or "never" in text or "fake" in text
        )
    )


# ---------------------------------------------------------------------------
# 13. Production PHI not ready
# ---------------------------------------------------------------------------


def test_evidence_mentions_production_phi_not_ready() -> None:
    text = _evidence().lower()
    assert "production phi" in text or (
        "production" in text and (
            "no-go" in text or "not proven" in text or "not ready" in text
            or "no.*go" in text
        )
    )


# ---------------------------------------------------------------------------
# 14. PostgreSQL / DATABASE_URL pending
# ---------------------------------------------------------------------------


def test_evidence_mentions_postgresql_or_database_url_pending() -> None:
    text = _evidence().lower()
    assert (
        "postgresql" in text or "database_url" in text
    ) and (
        "pending" in text or "not proven" in text or "not yet" in text
    )


# ---------------------------------------------------------------------------
# 15. Migrations pending
# ---------------------------------------------------------------------------


def test_evidence_mentions_migrations_pending() -> None:
    text = _evidence().lower()
    assert "migration" in text and (
        "pending" in text or "not proven" in text or "not yet" in text
    )


# ---------------------------------------------------------------------------
# 16. Vercel pending
# ---------------------------------------------------------------------------


def test_evidence_mentions_vercel_pending() -> None:
    text = _evidence().lower()
    assert "vercel" in text and (
        "pending" in text or "not proven" in text or "not yet" in text
    )


# ---------------------------------------------------------------------------
# 17. Vapi pending
# ---------------------------------------------------------------------------


def test_evidence_mentions_vapi_pending() -> None:
    text = _evidence().lower()
    assert "vapi" in text and (
        "pending" in text or "not proven" in text or "not yet" in text
    )


# ---------------------------------------------------------------------------
# 18. Module 113 Railway PostgreSQL
# ---------------------------------------------------------------------------


def test_evidence_mentions_module_113() -> None:
    text = _evidence().lower()
    assert "module 113" in text and (
        "postgresql" in text or "railway" in text
    )


# ---------------------------------------------------------------------------
# 19. No obvious real secrets
# ---------------------------------------------------------------------------


def test_evidence_no_real_api_keys() -> None:
    real_key_pattern = re.compile(r"sk-[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{50,}")
    assert not real_key_pattern.findall(_evidence())
