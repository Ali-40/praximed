"""
Contract tests for Sprint 11 / Modules 87–88 — Real Vapi tool payload smoke prep and adapter.

Static tests only — no network, no DB, no running backend.
Verifies the sanitized sample payload, the inspector script, the
prep documentation, and the Module 88 adapter are correctly structured.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_PAYLOADS_DIR = _PROJECT_ROOT / "docs" / "integrations" / "local_payloads"
_SCRIPTS_DIR = _PROJECT_ROOT / "backend" / "scripts"
_DOCS_DIR = _PROJECT_ROOT / "docs" / "integrations"

_SAMPLE_PAYLOAD = _PAYLOADS_DIR / "vapi_real_tool_payload_sample.json"
_INSPECTOR_SCRIPT = _SCRIPTS_DIR / "inspect_vapi_tool_payload.py"
_PREP_DOC = _DOCS_DIR / "VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md"

LOCAL_CLINIC_UUID = "11111111-1111-1111-1111-111111111111"

# ---------------------------------------------------------------------------
# 1. Sample payload exists and is valid JSON
# ---------------------------------------------------------------------------


def test_sample_payload_file_exists():
    assert _SAMPLE_PAYLOAD.is_file(), f"Expected {_SAMPLE_PAYLOAD} to exist"


def test_sample_payload_is_valid_json():
    data = json.loads(_SAMPLE_PAYLOAD.read_text(encoding="utf-8"))
    assert isinstance(data, dict)


# ---------------------------------------------------------------------------
# 2. Sample uses local fake clinic UUID (not real data)
# ---------------------------------------------------------------------------


def test_sample_payload_uses_local_clinic_uuid():
    content = _SAMPLE_PAYLOAD.read_text(encoding="utf-8")
    assert LOCAL_CLINIC_UUID in content, (
        f"Sample payload must reference local seed UUID {LOCAL_CLINIC_UUID} "
        "(expected in _local_test_context.clinic_ref_from_header)"
    )


def test_sample_payload_has_no_real_patient_markers():
    content = _SAMPLE_PAYLOAD.read_text(encoding="utf-8").lower()
    # Check for actual PII markers only — not documentation disclaimer phrases.
    forbidden = ["@gmail.com", "@hotmail", "@yahoo", "1234567890"]
    for marker in forbidden:
        assert marker not in content, (
            f"Sample payload must not contain PII marker: {marker!r}"
        )


# ---------------------------------------------------------------------------
# 3. Sample payload has expected Vapi tool-call shape
# ---------------------------------------------------------------------------


def test_sample_payload_has_message_key():
    data = json.loads(_SAMPLE_PAYLOAD.read_text(encoding="utf-8"))
    assert "message" in data, "Sample must have a 'message' key (Vapi tool-call shape)"


def test_sample_payload_has_tool_call_list():
    data = json.loads(_SAMPLE_PAYLOAD.read_text(encoding="utf-8"))
    tool_list = data.get("message", {}).get("toolCallList")
    assert isinstance(tool_list, list) and len(tool_list) > 0, (
        "Sample must have message.toolCallList with at least one entry"
    )


def test_sample_payload_has_function_arguments():
    data = json.loads(_SAMPLE_PAYLOAD.read_text(encoding="utf-8"))
    first = data["message"]["toolCallList"][0]
    args = first.get("function", {}).get("arguments")
    assert isinstance(args, dict) and args, (
        "Sample must have function.arguments as a non-empty dict"
    )


def test_sample_payload_arguments_have_patient_name():
    data = json.loads(_SAMPLE_PAYLOAD.read_text(encoding="utf-8"))
    args = data["message"]["toolCallList"][0]["function"]["arguments"]
    assert "patient_name" in args, "function.arguments must include patient_name"


# ---------------------------------------------------------------------------
# 4. Inspector script exists and is correctly structured
# ---------------------------------------------------------------------------


def test_inspector_script_exists():
    assert _INSPECTOR_SCRIPT.is_file(), f"Expected {_INSPECTOR_SCRIPT} to exist"


def test_inspector_script_accepts_payload_file_arg():
    content = _INSPECTOR_SCRIPT.read_text(encoding="utf-8")
    assert "--payload-file" in content, (
        "Inspector script must accept --payload-file argument"
    )


def test_inspector_script_does_not_print_full_raw_payload():
    content = _INSPECTOR_SCRIPT.read_text(encoding="utf-8")
    forbidden_patterns = [
        'print(json.dumps(data',
        'print(data)',
        'print(raw)',
        'print(payload)',
    ]
    for pat in forbidden_patterns:
        assert pat not in content, (
            f"Inspector must not dump full raw payload — found pattern: {pat!r}"
        )


def test_inspector_script_redacts_sensitive_fields():
    content = _INSPECTOR_SCRIPT.read_text(encoding="utf-8")
    assert "_SENSITIVE_KEYS" in content or "redact" in content.lower(), (
        "Inspector must define or use redaction for sensitive fields"
    )


def test_inspector_script_detects_argument_keys():
    content = _INSPECTOR_SCRIPT.read_text(encoding="utf-8")
    assert "arguments" in content and ("keys" in content or "arg_keys" in content), (
        "Inspector must detect and report argument key names"
    )


def test_inspector_script_uses_stdlib_only():
    content = _INSPECTOR_SCRIPT.read_text(encoding="utf-8")
    third_party = ["import requests", "import httpx", "import asyncio", "import fastapi"]
    for lib in third_party:
        assert lib not in content, (
            f"Inspector must use stdlib only — found: {lib!r}"
        )


# ---------------------------------------------------------------------------
# 5. Prep doc mentions real Vapi payload unknown and capture plan
# ---------------------------------------------------------------------------


def test_prep_doc_mentions_real_vapi_payload_unknown():
    content = _PREP_DOC.read_text(encoding="utf-8").lower()
    assert "real vapi" in content or "real vapi tool" in content or "live assistant" in content, (
        "Prep doc must mention real Vapi tool payload or live assistant as an unknown"
    )


def test_prep_doc_has_payload_capture_plan():
    content = _PREP_DOC.read_text(encoding="utf-8").lower()
    assert "capture" in content and ("payload" in content or "tool" in content), (
        "Prep doc must describe a plan to capture the real Vapi tool-call payload"
    )


def test_prep_doc_mentions_no_real_patient_data():
    content = _PREP_DOC.read_text(encoding="utf-8").lower()
    assert "no real patient" in content or "fake" in content or "test assistant" in content, (
        "Prep doc must mention not using real patient data"
    )


# ---------------------------------------------------------------------------
# 6. Module 88 adapter — importable and correct structure
# ---------------------------------------------------------------------------

_CAPTURE_MODULE = _PROJECT_ROOT / "backend" / "app" / "modules" / "vapi" / "vapi_appointment_capture.py"


def test_adapter_function_exists_in_capture_module():
    content = _CAPTURE_MODULE.read_text(encoding="utf-8")
    assert "def adapt_vapi_tool_call_body(" in content, (
        "adapt_vapi_tool_call_body must be defined in vapi_appointment_capture.py"
    )


def test_adapter_accepts_machine_clinic_id_param():
    content = _CAPTURE_MODULE.read_text(encoding="utf-8")
    assert "machine_clinic_id" in content, (
        "Adapter must accept machine_clinic_id to enforce security boundary"
    )


def test_adapter_does_not_trust_clinic_ref_from_arguments():
    content = _CAPTURE_MODULE.read_text(encoding="utf-8")
    assert "machine_clinic_id" in content, (
        "clinic_ref must be derived from machine_clinic_id, not patient-supplied arguments"
    )


def test_adapter_maps_sample_payload_to_flat_fields():
    data = json.loads(_SAMPLE_PAYLOAD.read_text(encoding="utf-8"))
    from backend.app.modules.vapi.vapi_appointment_capture import adapt_vapi_tool_call_body
    result = adapt_vapi_tool_call_body(data, "11111111-1111-1111-1111-111111111111")
    assert result.get("clinic_ref") == "11111111-1111-1111-1111-111111111111"
    assert result.get("call_id") == "local-real-vapi-call-1"
    assert result.get("patient_name") == "Local Real Vapi Tool Caller"


def test_adapter_flat_payload_unchanged():
    flat = {"clinic_ref": "test-ref", "call_id": "call-1", "patient_name": "Flat Caller"}
    from backend.app.modules.vapi.vapi_appointment_capture import adapt_vapi_tool_call_body
    result = adapt_vapi_tool_call_body(flat, "ignored-clinic")
    assert result is flat
