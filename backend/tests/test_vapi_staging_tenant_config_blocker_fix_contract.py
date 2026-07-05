"""
Sprint 16 / Module 118A — Vapi staging tenant config blocker fix contract tests.

Static tests verifying:
- The staging fake clinic tenant config file exists with correct content
- The wiring and smoke docs accurately record the blocked Vapi staging state:
  Vapi UI "completed successfully" but staging_count=0; no DB row was inserted
- Required correct headers are documented
- X-Clinic-Ref removal is documented
- No secrets, no real patient data, fake/non-PHI staging only
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
TENANT_CONFIG = (
    ROOT
    / "backend"
    / "tenants"
    / "configs"
    / "1a5bbc75-c1b0-4488-94aa-64b3f1c50056"
    / "clinic_config.json"
)
WIRING_DOC = ROOT / "docs" / "runtime" / "STAGING_ENVIRONMENT_WIRING_EVIDENCE.md"
SMOKE_DOC = ROOT / "docs" / "runtime" / "STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md"
CURRENT_STATE_DOC = ROOT / "docs" / "claude" / "CURRENT_STATE.md"


def _config() -> dict:
    return json.loads(TENANT_CONFIG.read_text())


def _wiring() -> str:
    return WIRING_DOC.read_text()


def _smoke() -> str:
    return SMOKE_DOC.read_text()


def _current_state() -> str:
    return CURRENT_STATE_DOC.read_text()


# --- Tenant config file ---

def test_staging_tenant_config_exists():
    assert TENANT_CONFIG.exists(), (
        "Staging tenant config must exist at "
        "backend/tenants/configs/1a5bbc75-c1b0-4488-94aa-64b3f1c50056/clinic_config.json"
    )


def test_staging_tenant_config_tenant_id():
    assert _config()["tenant_id"] == "1a5bbc75-c1b0-4488-94aa-64b3f1c50056", (
        "tenant_id must be the staging clinic UUID"
    )


def test_staging_tenant_config_clinic_name():
    assert _config()["clinic_name"] == "Staging Fake Clinic", (
        "clinic_name must be 'Staging Fake Clinic'"
    )


def test_staging_tenant_config_timezone():
    assert _config()["timezone"] == "Europe/Vienna", (
        "timezone must be 'Europe/Vienna'"
    )


def test_staging_tenant_config_appointment_booking_enabled():
    assert _config()["features"]["appointment_booking"] is True, (
        "appointment_booking feature must be enabled (true)"
    )


# --- Wiring doc: Vapi state ---

def test_wiring_doc_mentions_vapi():
    text = _wiring()
    assert "Vapi" in text, (
        "wiring doc must mention Vapi"
    )


def test_wiring_doc_vapi_headers_documented():
    text = _wiring()
    assert "X-Vapi-Service-Name" in text and "X-Vapi-Clinic-Id" in text, (
        "wiring doc must document the correct Vapi headers applied in Module 118B"
    )


# --- CURRENT_STATE.md: Module 118A diagnostic history ---

def test_current_state_records_staging_count_zero():
    assert "staging_count=0" in _current_state(), (
        "CURRENT_STATE.md must record staging_count=0 from the Module 118A Railway DB check"
    )


def test_current_state_records_vapi_completed_but_no_row():
    text = _current_state()
    assert "completed successfully" in text.lower() and (
        "no DB row" in text or "staging_count=0" in text
    ), (
        "CURRENT_STATE.md must record that Vapi UI showed 'completed successfully' "
        "but no DB row was inserted during Module 118A"
    )


# --- Wiring doc: required correct headers ---

def test_wiring_doc_content_type_header():
    assert "Content-Type" in _wiring(), (
        "wiring doc must document required Content-Type header"
    )


def test_wiring_doc_x_vapi_service_name_header():
    assert "X-Vapi-Service-Name" in _wiring(), (
        "wiring doc must document required X-Vapi-Service-Name header"
    )


def test_wiring_doc_x_vapi_clinic_id_header():
    assert "X-Vapi-Clinic-Id" in _wiring(), (
        "wiring doc must document required X-Vapi-Clinic-Id header"
    )


def test_wiring_doc_x_vapi_scopes_header():
    assert "X-Vapi-Scopes" in _wiring(), (
        "wiring doc must document required X-Vapi-Scopes header"
    )


def test_wiring_doc_x_clinic_ref_must_be_removed():
    text = _wiring()
    assert "X-Clinic-Ref" in text, (
        "wiring doc must mention X-Clinic-Ref as the incorrect header that must be removed"
    )


# --- Smoke doc: includes Vapi check ---

def test_smoke_doc_includes_vapi_check():
    text = _smoke()
    assert "Vapi test assistant fake call" in text, (
        "smoke doc must include Vapi test assistant fake call check"
    )


def test_smoke_doc_mentions_pending_or_deferred():
    text = _smoke()
    assert "PENDING" in text or "DEFERRED" in text, (
        "smoke doc must record at least one item as PENDING or DEFERRED (e.g. n8n)"
    )


# --- Safety: no secrets, no real patient data ---

def test_wiring_doc_no_real_patient_data():
    text = _wiring()
    assert "no real patient" in text.lower() or "No real patient" in text, (
        "wiring doc must confirm no real patient data"
    )


def test_wiring_doc_fake_non_phi():
    text = _wiring()
    assert "fake" in text.lower() and "non-PHI" in text, (
        "wiring doc must confirm fake/non-PHI staging only"
    )


def test_wiring_doc_no_secrets_recorded():
    text = _wiring()
    assert "not recorded" in text.lower() or "REDACTED" in text or "no secrets" in text.lower(), (
        "wiring doc must confirm no secrets are recorded"
    )
