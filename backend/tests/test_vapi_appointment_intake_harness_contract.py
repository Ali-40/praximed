"""
Contract tests — Sprint 11 / Module 83
Vapi Intake to Appointment Dashboard Smoke Harness

Static checks verifying the harness payload, smoke script, capture service fix,
and prep documentation are correctly structured.
No real Vapi calls, no real database, no live backend required.
"""

import json
import pathlib

REPO_ROOT = pathlib.Path(__file__).parents[2]

PAYLOAD_FILE = REPO_ROOT / "docs" / "integrations" / "local_payloads" / "vapi_appointment_intake.json"
SMOKE_SCRIPT = REPO_ROOT / "backend" / "scripts" / "smoke_vapi_appointment_intake.py"
PREP_DOC     = REPO_ROOT / "docs" / "integrations" / "VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md"
CAPTURE_SVC  = REPO_ROOT / "backend" / "app" / "modules" / "vapi" / "vapi_appointment_capture.py"

LOCAL_CLINIC_UUID = "11111111-1111-1111-1111-111111111111"


# ---------------------------------------------------------------------------
# 1. Local payload file exists and is valid JSON
# ---------------------------------------------------------------------------

def test_payload_file_exists_and_is_valid_json():
    assert PAYLOAD_FILE.is_file(), f"Payload file not found: {PAYLOAD_FILE}"
    data = json.loads(PAYLOAD_FILE.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "Payload must be a JSON object"


# ---------------------------------------------------------------------------
# 2. Payload uses local fake clinic UUID
# ---------------------------------------------------------------------------

def test_payload_uses_local_clinic_uuid():
    data = json.loads(PAYLOAD_FILE.read_text(encoding="utf-8"))
    assert data.get("clinic_ref") == LOCAL_CLINIC_UUID, (
        f"clinic_ref must be the local seed clinic UUID {LOCAL_CLINIC_UUID!r}"
    )


# ---------------------------------------------------------------------------
# 3. Payload has all required VapiAppointmentCaptureRequest fields
# ---------------------------------------------------------------------------

def test_payload_has_required_capture_fields():
    data = json.loads(PAYLOAD_FILE.read_text(encoding="utf-8"))
    for field in ("clinic_ref", "call_id", "patient_name"):
        assert field in data and data[field], (
            f"Payload must contain non-empty field: {field!r}"
        )


# ---------------------------------------------------------------------------
# 4. Payload contains no real patient data markers
# ---------------------------------------------------------------------------

def test_payload_no_real_patient_data():
    text = PAYLOAD_FILE.read_text(encoding="utf-8")
    assert "eyJ" not in text, "Payload must not contain a hardcoded JWT token"
    assert "local-dev-password" not in text, "Payload must not contain dev passwords"
    assert "doctor.local@praximed.test" not in text, (
        "Payload must not contain the local login email"
    )


# ---------------------------------------------------------------------------
# 5. Smoke script file exists
# ---------------------------------------------------------------------------

def test_smoke_script_exists():
    assert SMOKE_SCRIPT.is_file(), f"Smoke script not found: {SMOKE_SCRIPT}"


# ---------------------------------------------------------------------------
# 6. Smoke script reads PRAXIMED_API_BASE_URL with 127.0.0.1:8000 fallback
# ---------------------------------------------------------------------------

def test_smoke_script_has_api_base_url_fallback():
    content = SMOKE_SCRIPT.read_text(encoding="utf-8")
    assert "PRAXIMED_API_BASE_URL" in content, (
        "Smoke script must read the PRAXIMED_API_BASE_URL environment variable"
    )
    assert "http://127.0.0.1:8000" in content, (
        "Smoke script must fall back to http://127.0.0.1:8000"
    )


# ---------------------------------------------------------------------------
# 7. Smoke script sends machine auth headers (no HMAC needed for tool endpoint)
# ---------------------------------------------------------------------------

def test_smoke_script_sends_machine_auth_headers():
    content = SMOKE_SCRIPT.read_text(encoding="utf-8")
    assert "X-Vapi-Service-Name" in content, "Smoke script must send X-Vapi-Service-Name"
    assert "X-Vapi-Clinic-Id" in content, "Smoke script must send X-Vapi-Clinic-Id"
    assert "X-Vapi-Scopes" in content, "Smoke script must send X-Vapi-Scopes"
    assert "vapi:tool" in content, "Smoke script must use vapi:tool scope"


# ---------------------------------------------------------------------------
# 8. Smoke script does not print secrets
# ---------------------------------------------------------------------------

def test_smoke_script_does_not_print_secrets():
    content = SMOKE_SCRIPT.read_text(encoding="utf-8")
    # No hardcoded secrets; the script does not print env var values
    assert "print(secret" not in content.lower(), (
        "Smoke script must not print secret values directly"
    )
    assert "VAPI_WEBHOOK_SECRET" not in content or "print(VAPI_WEBHOOK_SECRET" not in content, (
        "Smoke script must not print VAPI_WEBHOOK_SECRET"
    )
    assert "local-dev-password" not in content, (
        "Smoke script must not contain hardcoded dev passwords"
    )


# ---------------------------------------------------------------------------
# 9. Smoke script exits non-zero on non-2xx response
# ---------------------------------------------------------------------------

def test_smoke_script_exits_nonzero_on_failure():
    content = SMOKE_SCRIPT.read_text(encoding="utf-8")
    assert "return 1" in content, (
        "Smoke script must return exit code 1 on non-2xx or connection failure"
    )
    assert "sys.exit" in content, (
        "Smoke script must call sys.exit() to propagate the exit code"
    )


# ---------------------------------------------------------------------------
# 10. Prep doc references the Module 83 harness and manual flow commands
# ---------------------------------------------------------------------------

def test_prep_doc_references_harness():
    content = PREP_DOC.read_text(encoding="utf-8")
    assert "smoke_vapi_appointment_intake" in content, (
        "Prep doc must reference the smoke script by name"
    )
    assert "capture-appointment-request" in content or "Module 83" in content, (
        "Prep doc must mention the capture endpoint or Module 83 harness"
    )
