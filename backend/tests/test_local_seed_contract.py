"""
Static/unit contract tests for local seed data tooling — PraxisMed Sprint 5 / Module 50

Strategy:
- No external service calls.
- No real database connection.
- No backend server started.
- File-existence checks via pathlib.
- Module import safety via importlib.util.
- JSON validity via json.loads.
"""

from __future__ import annotations

import importlib.util
import json
import uuid
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------

PROJECT_ROOT      = Path(__file__).parent.parent.parent
BACKEND_DIR       = Path(__file__).parent.parent
SCRIPTS_DIR       = BACKEND_DIR / "scripts"
LOCAL_PAYLOADS    = PROJECT_ROOT / "docs" / "integrations" / "local_payloads"
RUNBOOK_PATH      = PROJECT_ROOT / "docs" / "integrations" / "LOCAL_INTEGRATION_RUNBOOK.md"

SEED_SCRIPT_PATH       = SCRIPTS_DIR / "seed_local_data.py"
VAPI_PAYLOAD_PATH      = LOCAL_PAYLOADS / "vapi_call_event.json"
N8N_PAYLOAD_PATH       = LOCAL_PAYLOADS / "n8n_calendar_sync.json"


def _load_seed():
    spec   = importlib.util.spec_from_file_location("seed_local_data", SEED_SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ===========================================================================
# Seed script existence and constants (tests 1–6)
# ===========================================================================


def test_seed_local_data_script_exists():
    """Test 1 — seed_local_data.py exists in backend/scripts/."""
    assert SEED_SCRIPT_PATH.exists(), f"Missing: {SEED_SCRIPT_PATH}"


def test_seed_script_defines_local_clinic_id():
    """Test 2 — Seed script defines LOCAL_CLINIC_ID."""
    mod = _load_seed()
    assert hasattr(mod, "LOCAL_CLINIC_ID")
    assert mod.LOCAL_CLINIC_ID == "11111111-1111-1111-1111-111111111111"


def test_seed_script_defines_local_doctor_user_id():
    """Test 3 — Seed script defines LOCAL_DOCTOR_USER_ID."""
    mod = _load_seed()
    assert hasattr(mod, "LOCAL_DOCTOR_USER_ID")
    assert mod.LOCAL_DOCTOR_USER_ID == "22222222-2222-2222-2222-222222222222"


def test_seed_script_defines_local_patient_id():
    """Test 4 — Seed script defines LOCAL_PATIENT_ID."""
    mod = _load_seed()
    assert hasattr(mod, "LOCAL_PATIENT_ID")
    assert mod.LOCAL_PATIENT_ID == "33333333-3333-3333-3333-333333333333"


def test_seed_script_defines_local_consultation_session_id():
    """Test 5 — Seed script defines LOCAL_CONSULTATION_SESSION_ID."""
    mod = _load_seed()
    assert hasattr(mod, "LOCAL_CONSULTATION_SESSION_ID")
    assert mod.LOCAL_CONSULTATION_SESSION_ID == "44444444-4444-4444-4444-444444444444"


def test_deterministic_ids_are_valid_uuids():
    """Test 6 — All four deterministic IDs parse as valid UUID strings."""
    mod = _load_seed()
    for attr in (
        "LOCAL_CLINIC_ID",
        "LOCAL_DOCTOR_USER_ID",
        "LOCAL_PATIENT_ID",
        "LOCAL_CONSULTATION_SESSION_ID",
    ):
        value = getattr(mod, attr)
        try:
            uuid.UUID(value)
        except ValueError:
            pytest.fail(f"{attr} = {value!r} is not a valid UUID")


# ===========================================================================
# Seed script safety (tests 7–11)
# ===========================================================================


def test_seed_script_reads_database_url_from_env():
    """Test 7 — Seed script source references DATABASE_URL environment variable."""
    content = SEED_SCRIPT_PATH.read_text()
    assert "DATABASE_URL" in content


def test_seed_script_imports_asyncpg_inside_function_not_at_top_level():
    """Test 8 — asyncpg is imported inside a function, not at module top level."""
    content = SEED_SCRIPT_PATH.read_text()
    lines   = content.splitlines()
    asyncpg_lines = [l for l in lines if "import asyncpg" in l]
    assert asyncpg_lines, "asyncpg import not found in seed_local_data.py"
    # Every asyncpg import line must be indented (inside a function body)
    for line in asyncpg_lines:
        assert line.startswith(("    ", "\t")), (
            f"asyncpg import is at module top level: {line!r}"
        )


def test_seed_script_has_main_guard():
    """Test 9 — Script contains if __name__ == '__main__': guard."""
    content = SEED_SCRIPT_PATH.read_text()
    assert 'if __name__ == "__main__":' in content or "if __name__ == '__main__':" in content


def test_seed_script_uses_on_conflict_for_idempotency():
    """Test 10 — Script uses ON CONFLICT for idempotent upserts."""
    content = SEED_SCRIPT_PATH.read_text().upper()
    assert "ON CONFLICT" in content


def test_importing_seed_script_does_not_connect_to_db(capsys):
    """Test 11 — Importing seed_local_data.py does not open a DB connection."""
    _load_seed()
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


# ===========================================================================
# Payload fixture files (tests 12–18)
# ===========================================================================


def test_vapi_call_event_json_exists():
    """Test 12 — vapi_call_event.json exists in docs/integrations/local_payloads/."""
    assert VAPI_PAYLOAD_PATH.exists(), f"Missing: {VAPI_PAYLOAD_PATH}"


def test_vapi_call_event_json_is_valid_json():
    """Test 13 — vapi_call_event.json parses as valid JSON."""
    data = json.loads(VAPI_PAYLOAD_PATH.read_text())
    assert isinstance(data, dict)


def test_vapi_call_event_json_uses_deterministic_clinic_id():
    """Test 14 — vapi_call_event.json uses LOCAL_CLINIC_ID."""
    data = json.loads(VAPI_PAYLOAD_PATH.read_text())
    assert data.get("clinic_id") == "11111111-1111-1111-1111-111111111111"


def test_n8n_calendar_sync_json_exists():
    """Test 15 — n8n_calendar_sync.json exists in docs/integrations/local_payloads/."""
    assert N8N_PAYLOAD_PATH.exists(), f"Missing: {N8N_PAYLOAD_PATH}"


def test_n8n_calendar_sync_json_is_valid_json():
    """Test 16 — n8n_calendar_sync.json parses as valid JSON."""
    data = json.loads(N8N_PAYLOAD_PATH.read_text())
    assert isinstance(data, dict)


def test_n8n_calendar_sync_json_uses_deterministic_clinic_id():
    """Test 17 — n8n_calendar_sync.json uses LOCAL_CLINIC_ID."""
    data = json.loads(N8N_PAYLOAD_PATH.read_text())
    assert data.get("clinic_id") == "11111111-1111-1111-1111-111111111111"


def test_payload_fixtures_do_not_contain_real_patient_data_markers():
    """Test 18 — Payload fixtures do not contain obvious real patient data markers."""
    forbidden = ["@gmail.com", "@yahoo.com", "@hotmail.com", "real_patient", "ssn", "dob="]
    for path in (VAPI_PAYLOAD_PATH, N8N_PAYLOAD_PATH):
        content = path.read_text().lower()
        for marker in forbidden:
            assert marker not in content, (
                f"{path.name} contains suspicious marker: {marker!r}"
            )


# ===========================================================================
# Runbook content (tests 19–22)
# ===========================================================================


def _runbook() -> str:
    return RUNBOOK_PATH.read_text()


def test_runbook_mentions_seed_local_data():
    """Test 19 — Runbook documents the seed_local_data.py step."""
    assert "seed_local_data.py" in _runbook()


def test_runbook_uses_deterministic_uuid_not_clinic_1():
    """Test 20 — Runbook uses the deterministic UUID instead of 'clinic-1'."""
    content = _runbook()
    assert "11111111-1111-1111-1111-111111111111" in content
    assert "clinic-1" not in content


def test_runbook_documents_payload_file_signing():
    """Test 21 — Runbook shows --payload-file usage for signature generation."""
    content = _runbook()
    assert "--payload-file" in content
    assert "local_payloads" in content


def test_runbook_states_seed_data_is_fake_local_only():
    """Test 22 — Runbook explicitly states seed data is fake/local only."""
    content = _runbook().lower()
    assert "fake" in content or "not production" in content or "local only" in content


# ===========================================================================
# Password hash / login credentials (tests 23–28)
# ===========================================================================


def test_seed_script_references_password_hash():
    """Test 23 — seed_local_data.py sets password_hash on the user row."""
    content = SEED_SCRIPT_PATH.read_text()
    assert "password_hash" in content, \
        "seed_local_data.py must include password_hash in the clinic_users INSERT"


def test_seed_script_uses_hash_password():
    """Test 24 — seed_local_data.py calls the hash_password helper."""
    content = SEED_SCRIPT_PATH.read_text()
    assert "hash_password" in content, \
        "seed_local_data.py must call hash_password to produce the bcrypt hash"


def test_seed_script_includes_local_login_email():
    """Test 25 — seed_local_data.py defines the deterministic local login email."""
    content = SEED_SCRIPT_PATH.read_text()
    assert "doctor.local@praximed.test" in content, \
        "seed_local_data.py must contain the local login email"


def test_seed_script_local_login_email_constant_defined():
    """Test 26 — Module exports LOCAL_LOGIN_EMAIL with the correct value."""
    mod = _load_seed()
    assert hasattr(mod, "LOCAL_LOGIN_EMAIL"), \
        "seed_local_data module must define LOCAL_LOGIN_EMAIL"
    assert mod.LOCAL_LOGIN_EMAIL == "doctor.local@praximed.test"


def test_seed_script_includes_local_dev_password_label():
    """Test 27 — seed_local_data.py references the local-dev password label."""
    content = SEED_SCRIPT_PATH.read_text()
    assert "local-dev-password" in content, \
        "seed_local_data.py must include the local-dev password label"


def test_seed_script_does_not_print_password_hash():
    """Test 28 — No print() call in the script outputs the raw password_hash variable."""
    for line in SEED_SCRIPT_PATH.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("print") and "pwd_hash" in stripped:
            pytest.fail(
                f"seed_local_data.py prints the raw password hash: {stripped!r}"
            )


def test_seed_script_has_sys_path_project_root_safety():
    """Test 29 — Script contains sys.path project-root insertion for direct execution."""
    content = SEED_SCRIPT_PATH.read_text()
    # Must reference sys.path so that `python backend/scripts/seed_local_data.py`
    # can find the backend package without the caller setting PYTHONPATH.
    assert "sys.path" in content, \
        "seed_local_data.py must add the project root to sys.path for direct execution"
    assert "_PROJECT_ROOT" in content or "project_root" in content.lower() or \
           "dirname" in content, \
        "seed_local_data.py must compute the project root path dynamically"
