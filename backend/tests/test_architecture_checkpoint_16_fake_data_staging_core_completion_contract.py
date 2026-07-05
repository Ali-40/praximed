"""
Architecture Checkpoint 16 — Fake-data staging core completion review contract tests.

Static tests verifying the checkpoint doc records the real PASS state of the Sprint 16
fake-data staging core loop, clearly separates what is proven from what remains
PENDING, and recommends the Production Hardening Gap Review as the next module.
"""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
CHECKPOINT_DOC = (
    ROOT
    / "docs"
    / "architecture"
    / "ARCHITECTURE_CHECKPOINT_16_FAKE_DATA_STAGING_CORE_COMPLETION.md"
)


def _text() -> str:
    return CHECKPOINT_DOC.read_text()


def test_checkpoint_doc_exists():
    assert CHECKPOINT_DOC.exists(), (
        "ARCHITECTURE_CHECKPOINT_16_FAKE_DATA_STAGING_CORE_COMPLETION.md must exist"
    )


def test_checkpoint_result_is_fake_data_staging_core_pass():
    assert "FAKE-DATA STAGING CORE PASS" in _text(), (
        "checkpoint doc must record result as FAKE-DATA STAGING CORE PASS"
    )


def test_checkpoint_mentions_railway_backend():
    assert "Railway backend" in _text(), (
        "checkpoint doc must mention Railway backend"
    )


def test_checkpoint_mentions_railway_postgresql():
    assert "Railway PostgreSQL" in _text(), (
        "checkpoint doc must mention Railway PostgreSQL"
    )


def test_checkpoint_mentions_vercel_frontend():
    assert "Vercel frontend" in _text(), (
        "checkpoint doc must mention Vercel frontend"
    )


def test_checkpoint_mentions_vapi():
    assert "Vapi" in _text(), (
        "checkpoint doc must mention Vapi"
    )


def test_checkpoint_mentions_browser_login():
    assert "browser login" in _text(), (
        "checkpoint doc must mention browser login"
    )


def test_checkpoint_mentions_dashboard_row_visibility():
    text = _text()
    assert "dashboard row visibility" in text.lower() or (
        "dashboard" in text.lower() and "row" in text.lower()
    ), (
        "checkpoint doc must mention dashboard row visibility"
    )


def test_checkpoint_mentions_staff_confirm():
    assert "staff Confirm" in _text(), (
        "checkpoint doc must mention staff Confirm"
    )


def test_checkpoint_mentions_module_112():
    assert "Module 112" in _text(), (
        "checkpoint doc must reference Module 112 (Railway backend service)"
    )


def test_checkpoint_mentions_module_114():
    assert "Module 114" in _text(), (
        "checkpoint doc must reference Module 114 (Railway PostgreSQL migration)"
    )


def test_checkpoint_mentions_module_115():
    assert "Module 115" in _text(), (
        "checkpoint doc must reference Module 115 (fake staging clinic/user)"
    )


def test_checkpoint_mentions_module_116():
    assert "Module 116" in _text(), (
        "checkpoint doc must reference Module 116 (backend login smoke)"
    )


def test_checkpoint_mentions_module_117():
    assert "Module 117" in _text(), (
        "checkpoint doc must reference Module 117 (Vercel frontend/CORS/browser dashboard)"
    )


def test_checkpoint_mentions_module_118a():
    assert "Module 118A" in _text(), (
        "checkpoint doc must reference Module 118A (tenant config blocker fix)"
    )


def test_checkpoint_mentions_module_118b():
    assert "Module 118B" in _text(), (
        "checkpoint doc must reference Module 118B (Vapi dashboard loop)"
    )


def test_checkpoint_mentions_n8n_staging_pending():
    text = _text()
    assert "n8n" in text and ("PENDING" in text or "DEFERRED" in text), (
        "checkpoint doc must note n8n staging is PENDING or DEFERRED"
    )


def test_checkpoint_mentions_production_auth_session_hardening_pending():
    text = _text()
    assert "production auth/session hardening" in text.lower() or (
        "auth/session" in text and "PENDING" in text
    ), (
        "checkpoint doc must note production auth/session hardening is PENDING"
    )


def test_checkpoint_mentions_production_phi_no_go():
    text = _text()
    assert "production PHI" in text and "NO-GO" in text, (
        "checkpoint doc must confirm production PHI readiness is NO-GO"
    )


def test_checkpoint_mentions_no_real_patient_data():
    text = _text()
    assert "no real patient data" in text.lower() or "No real patient data" in text, (
        "checkpoint doc must confirm no real patient data"
    )


def test_checkpoint_mentions_no_secrets_recorded():
    text = _text()
    assert "no secrets recorded" in text.lower() or "No secrets recorded" in text, (
        "checkpoint doc must confirm no secrets are recorded"
    )


def test_checkpoint_recommends_production_hardening_gap_review():
    assert "Sprint 17 / Module 119 — Production Hardening Gap Review" in _text(), (
        "checkpoint doc must recommend Sprint 17 / Module 119 — Production Hardening Gap Review"
    )


def test_checkpoint_mentions_n8n_as_alternative():
    text = _text()
    assert "n8n" in text and "alternative" in text.lower(), (
        "checkpoint doc must mention n8n as an alternative path"
    )
