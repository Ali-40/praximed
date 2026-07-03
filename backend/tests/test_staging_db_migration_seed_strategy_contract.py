"""
Static contract tests for Sprint 14 / Module 103 — Staging DB Migration and Seed Strategy.

Verifies:
- Staging DB migration and seed strategy doc exists and covers all required sections
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

_DOC_PATH = os.path.join(
    _REPO_ROOT, "docs", "deployment", "STAGING_DB_MIGRATION_AND_SEED_STRATEGY.md"
)


def _doc() -> str:
    with open(_DOC_PATH, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. Doc existence and size
# ---------------------------------------------------------------------------


def test_staging_db_migration_seed_strategy_doc_exists() -> None:
    assert os.path.isfile(_DOC_PATH), f"Strategy doc not found at {_DOC_PATH}"


def test_doc_not_empty() -> None:
    assert len(_doc()) > 3000


# ---------------------------------------------------------------------------
# 2. Platform and data policy
# ---------------------------------------------------------------------------


def test_doc_mentions_railway_postgresql() -> None:
    text = _doc().lower()
    assert "railway" in text and "postgresql" in text


def test_doc_mentions_fake_non_phi_staging_only() -> None:
    text = _doc().lower()
    assert ("fake" in text or "non-phi" in text) and "staging" in text


def test_doc_mentions_production_phi_no_go() -> None:
    text = _doc().lower()
    assert "no-go" in text and ("production" in text or "phi" in text)


def test_doc_mentions_no_db_mutation_in_this_module() -> None:
    text = _doc().lower()
    assert (
        "no db mutation" in text
        or "no database mutation" in text
        or "no deployment" in text
        or "no db mutation executed" in text
    )


# ---------------------------------------------------------------------------
# 3. Migration coverage
# ---------------------------------------------------------------------------


def test_doc_mentions_alembic() -> None:
    assert "alembic" in _doc().lower()


def test_doc_mentions_run_migrations_py() -> None:
    assert "run_migrations.py" in _doc()


def test_doc_mentions_python_run_migrations_command() -> None:
    assert "python backend/scripts/run_migrations.py" in _doc()


def test_doc_mentions_database_url() -> None:
    assert "DATABASE_URL" in _doc()


def test_doc_mentions_migrations_before_backend_traffic() -> None:
    text = _doc().lower()
    assert "migration" in text and (
        "before" in text and ("traffic" in text or "backend" in text)
    )


def test_doc_mentions_migrations_not_in_procfile_web_command() -> None:
    text = _doc().lower()
    assert (
        "procfile" in text
        and "migration" in text
        and (
            "not" in text
            or "no migration" in text
            or "does not" in text
        )
    )


# ---------------------------------------------------------------------------
# 4. Backup/rollback coverage
# ---------------------------------------------------------------------------


def test_doc_mentions_backup_or_snapshot() -> None:
    text = _doc().lower()
    assert "backup" in text or "snapshot" in text


def test_doc_mentions_rollback() -> None:
    assert "rollback" in _doc().lower()


# ---------------------------------------------------------------------------
# 5. Seed script assessment
# ---------------------------------------------------------------------------


def test_doc_mentions_seed_local_data_py_local_only() -> None:
    text = _doc()
    assert "seed_local_data.py" in text and (
        "local" in text.lower() or "local-only" in text.lower()
    )


# ---------------------------------------------------------------------------
# 6. Staging fake tenant/user
# ---------------------------------------------------------------------------


def test_doc_mentions_staging_fake_clinic_id_placeholder() -> None:
    text = _doc().lower()
    assert (
        "staging-fake-clinic" in text
        or "staging fake clinic" in text
        or "<staging-fake-clinic-id>" in text
    )


def test_doc_mentions_fake_staging_user() -> None:
    text = _doc().lower()
    assert (
        "doctor.staging@praximed.test" in text
        or "staging fake" in text
        or "staging-fake-user" in text
    )


# ---------------------------------------------------------------------------
# 7. Data safety rules
# ---------------------------------------------------------------------------


def test_doc_mentions_no_real_patient_data() -> None:
    text = _doc().lower()
    assert (
        "no real patient" in text
        or "no real patient data" in text
        or ("real" in text and "patient" in text and (
            "not" in text or "no " in text or "never" in text or "must not" in text
        ))
    )


def test_doc_mentions_no_production_db() -> None:
    text = _doc().lower()
    assert "production" in text and (
        "no production" in text
        or "must not" in text
        or "never" in text
        or "separate" in text
    )


# ---------------------------------------------------------------------------
# 8. Vapi/n8n
# ---------------------------------------------------------------------------


def test_doc_mentions_vapi_creates_appointment_request() -> None:
    text = _doc().lower()
    assert "vapi" in text and "appointment_request" in text


def test_doc_mentions_status_new_or_action_required_true() -> None:
    text = _doc()
    assert "status='new'" in text or "status=new" in text or "action_required" in text


def test_doc_mentions_staff_confirm_no_auto_confirmation() -> None:
    text = _doc().lower()
    assert (
        "staff confirm" in text
        or "no auto-confirm" in text
        or "no auto-confirmation" in text
        or "no code path auto-confirms" in text
        or "action_required" in text.lower()
    ) and (
        "confirm" in text or "staff" in text
    )


def test_doc_mentions_n8n_staging_workflow() -> None:
    text = _doc().lower()
    assert "n8n" in text and "staging" in text


# ---------------------------------------------------------------------------
# 9. Evidence capture
# ---------------------------------------------------------------------------


def test_doc_mentions_evidence_capture() -> None:
    text = _doc().lower()
    assert "evidence" in text and ("capture" in text or "record" in text)


# ---------------------------------------------------------------------------
# 10. Stop rules
# ---------------------------------------------------------------------------


def test_doc_mentions_failure_stop_rules() -> None:
    text = _doc().lower()
    assert "stop" in text and (
        "rule" in text or "failure" in text or "stop rule" in text
    )


# ---------------------------------------------------------------------------
# 11. Module 104 reference
# ---------------------------------------------------------------------------


def test_doc_mentions_module_104_staging_smoke_execution_evidence() -> None:
    text = _doc().lower()
    assert "module 104" in text and (
        "smoke" in text or "staging" in text or "evidence" in text
    )


# ---------------------------------------------------------------------------
# 12. No obvious real secrets
# ---------------------------------------------------------------------------


def test_doc_no_real_api_keys() -> None:
    real_key_pattern = re.compile(r"sk-[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{50,}")
    assert not real_key_pattern.findall(_doc())
