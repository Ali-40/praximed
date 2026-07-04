"""
Sprint 16 / Module 114 — Railway PostgreSQL migration retest evidence contract tests.

Static tests verifying that the migration evidence doc records the real PASS result
with all required sanitized evidence and no secrets.
"""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
MIGRATION_EVIDENCE = (
    ROOT / "docs" / "runtime" / "RAILWAY_POSTGRESQL_MIGRATION_EVIDENCE.md"
)


def _text() -> str:
    return MIGRATION_EVIDENCE.read_text()


def test_migration_evidence_doc_exists():
    assert MIGRATION_EVIDENCE.exists(), (
        "RAILWAY_POSTGRESQL_MIGRATION_EVIDENCE.md must exist"
    )


def test_migration_evidence_doc_nonempty():
    assert len(_text()) > 100, "migration evidence doc must not be empty"


def test_migration_evidence_mentions_pass():
    assert "PASS" in _text(), "migration evidence doc must record PASS result"


def test_migration_evidence_mentions_railway_postgresql():
    text = _text()
    assert "Railway PostgreSQL" in text or "Railway PostgreSQL" in text, (
        "migration evidence doc must mention Railway PostgreSQL"
    )


def test_migration_evidence_mentions_database_url_wired_not_value():
    text = _text()
    assert "DATABASE_URL" in text, (
        "migration evidence doc must confirm DATABASE_URL was wired"
    )
    assert "value not recorded" in text or "name only" in text, (
        "migration evidence doc must confirm DATABASE_URL value is not recorded "
        "(no secrets policy)"
    )


def test_migration_evidence_mentions_run_migrations_script():
    assert "python backend/scripts/run_migrations.py" in _text(), (
        "migration evidence doc must record the migration command"
    )


def test_migration_evidence_mentions_0001_initial_schema():
    assert "0001_initial_schema" in _text(), (
        "migration evidence doc must record the 0001_initial_schema revision"
    )


def test_migration_evidence_mentions_0002_password_hash():
    assert "0002_password_hash" in _text(), (
        "migration evidence doc must record the 0002_password_hash revision"
    )


def test_migration_evidence_mentions_db_smoke_test():
    assert "db_smoke_test.py" in _text(), (
        "migration evidence doc must record the DB smoke test command"
    )


def test_migration_evidence_mentions_select_1_passed():
    assert "SELECT 1 passed" in _text(), (
        "migration evidence doc must record 'SELECT 1 passed' from DB smoke output"
    )


def test_migration_evidence_mentions_clinics_table():
    assert "clinics" in _text(), (
        "migration evidence doc must confirm 'clinics' table exists"
    )


def test_migration_evidence_mentions_patients_table():
    assert "patients" in _text(), (
        "migration evidence doc must confirm 'patients' table exists"
    )


def test_migration_evidence_mentions_consultation_sessions_table():
    assert "consultation_sessions" in _text(), (
        "migration evidence doc must confirm 'consultation_sessions' table exists"
    )


def test_migration_evidence_mentions_audit_log_table():
    assert "audit_log" in _text(), (
        "migration evidence doc must confirm 'audit_log' table exists"
    )


def test_migration_evidence_health_still_pass():
    text = _text()
    assert "web-production-fd91d.up.railway.app" in text or "/health" in text, (
        "migration evidence doc must confirm /health is still PASS"
    )


def test_migration_evidence_no_secrets():
    text = _text()
    assert "No secrets" in text or "no secrets" in text or "value not recorded" in text, (
        "migration evidence doc must confirm no secrets are recorded"
    )


def test_migration_evidence_no_real_patient_data():
    text = _text()
    assert "no real patient" in text.lower() or "No real patient" in text, (
        "migration evidence doc must confirm no real patient data"
    )


def test_migration_evidence_fake_non_phi_staging():
    text = _text()
    assert "fake" in text.lower() or "non-PHI" in text, (
        "migration evidence doc must confirm fake/non-PHI staging only"
    )


def test_migration_evidence_fake_clinic_user_still_pending():
    text = _text()
    assert "fake clinic" in text.lower() or "fake staging clinic" in text.lower(), (
        "migration evidence doc must note that fake staging clinic/user is still pending"
    )
    assert "PENDING" in text, (
        "migration evidence doc must have PENDING items (fake clinic/user not yet provisioned)"
    )


def test_migration_evidence_vercel_still_pending():
    text = _text()
    assert "Vercel" in text, (
        "migration evidence doc must note Vercel frontend is still pending"
    )


def test_migration_evidence_vapi_still_pending():
    text = _text()
    assert "Vapi" in text, (
        "migration evidence doc must note Vapi staging is still pending"
    )


def test_migration_evidence_mentions_module_115():
    assert "Module 115" in _text(), (
        "migration evidence doc must reference Module 115 "
        "for fake staging clinic/user provisioning"
    )
