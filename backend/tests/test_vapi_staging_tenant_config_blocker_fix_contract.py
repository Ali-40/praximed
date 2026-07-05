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


def _config() -> dict:
    return json.loads(TENANT_CONFIG.read_text())


def _wiring() -> str:
    return WIRING_DOC.read_text()


def _smoke() -> str:
    return SMOKE_DOC.read_text()


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


# --- Wiring doc: Vapi dashboard loop not PASS ---

def test_wiring_doc_vapi_still_pending_or_blocked():
    text = _wiring()
    assert "PENDING" in text or "BLOCKED" in text, (
        "wiring doc must record Vapi dashboard loop as PENDING or BLOCKED"
    )


def test_wiring_doc_vapi_not_marked_pass():
    text = _wiring()
    vapi_idx = text.find("Vapi test call creates row")
    assert vapi_idx != -1, "wiring doc must mention Vapi test call creates row"
    snippet = text[vapi_idx : vapi_idx + 300]
    assert "PASS" not in snippet, (
        "Vapi test call creates row must NOT be marked PASS — no DB row was inserted"
    )


# --- Wiring doc: real diagnostic evidence ---

def test_wiring_doc_staging_count_zero():
    assert "staging_count=0" in _wiring(), (
        "wiring doc must record staging_count=0 from Railway DB check"
    )


def test_wiring_doc_vapi_completed_but_no_db_row():
    text = _wiring()
    assert "completed successfully" in text.lower() and (
        "no DB row was inserted" in text or "no row" in text.lower()
    ), (
        "wiring doc must record that Vapi UI showed 'completed successfully' "
        "but no DB row was inserted"
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


# --- Smoke doc: overall still blocked ---

def test_smoke_doc_overall_blocked_or_pending():
    text = _smoke()
    assert "BLOCKED" in text or "PENDING" in text, (
        "smoke doc must record overall staging smoke as BLOCKED/PENDING"
    )


def test_smoke_doc_vapi_check_not_pass():
    text = _smoke()
    vapi_idx = text.find("Vapi test assistant fake call")
    assert vapi_idx != -1, "smoke doc must include Vapi test assistant fake call check"
    snippet = text[vapi_idx : vapi_idx + 300]
    assert "**PASS**" not in snippet, (
        "Vapi test assistant call must NOT be marked PASS in smoke doc"
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
