"""
Static contract tests for Sprint 19 / Module 130 — Operational Staging Readiness.

Verifies file content only. No JS/TS runtime. No database. No network. No secrets.
No real patient data.
"""

from __future__ import annotations

import json
import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))
DOCS_RUNTIME = os.path.join(_REPO_ROOT, "docs", "runtime")
TENANT_CONFIG = os.path.join(
    _REPO_ROOT,
    "backend", "tenants", "configs",
    "1a5bbc75-c1b0-4488-94aa-64b3f1c50056",
    "clinic_config.json",
)

DATA_FLOW_DOC  = os.path.join(DOCS_RUNTIME, "BACKEND_DATA_FLOW_AND_STORAGE_MAP.md")
RUNBOOK_DOC    = os.path.join(DOCS_RUNTIME, "STAGING_END_TO_END_DEMO_RUNBOOK.md")
VAPI_SETUP_DOC = os.path.join(DOCS_RUNTIME, "VAPI_GERMAN_ENGLISH_ASSISTANT_SETUP.md")


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. Backend data flow doc
# ---------------------------------------------------------------------------

def test_data_flow_doc_exists():
    assert os.path.isfile(DATA_FLOW_DOC)


def test_data_flow_doc_mentions_railway_postgresql():
    content = _read(DATA_FLOW_DOC)
    assert "Railway" in content and "PostgreSQL" in content


def test_data_flow_doc_mentions_vercel():
    assert "Vercel" in _read(DATA_FLOW_DOC)


def test_data_flow_doc_mentions_fastapi():
    assert "FastAPI" in _read(DATA_FLOW_DOC)


def test_data_flow_doc_mentions_appointment_requests():
    assert "appointment_requests" in _read(DATA_FLOW_DOC)


def test_data_flow_doc_mentions_patients():
    assert "patients" in _read(DATA_FLOW_DOC)


def test_data_flow_doc_mentions_clinic_notifications():
    assert "clinic_notifications" in _read(DATA_FLOW_DOC)


def test_data_flow_doc_mentions_vapi_flow():
    content = _read(DATA_FLOW_DOC)
    assert "Vapi" in content and ("flow" in content.lower() or "tool" in content.lower())


def test_data_flow_doc_mentions_secure_cookie():
    content = _read(DATA_FLOW_DOC).lower()
    assert "cookie" in content


def test_data_flow_doc_mentions_fake_data_staging():
    content = _read(DATA_FLOW_DOC).lower()
    assert "fake" in content and "staging" in content


def test_data_flow_doc_mentions_production_phi_no_go():
    content = _read(DATA_FLOW_DOC)
    assert "Production PHI" in content and "NO-GO" in content


def test_data_flow_doc_no_secrets():
    content = _read(DATA_FLOW_DOC)
    assert not re.search(r"eyJ[A-Za-z0-9_\-]{20,}", content), "JWT in data flow doc"
    assert "sk-" not in content, "API key in data flow doc"


# ---------------------------------------------------------------------------
# 2. Staging end-to-end demo runbook
# ---------------------------------------------------------------------------

def test_runbook_exists():
    assert os.path.isfile(RUNBOOK_DOC)


def test_runbook_mentions_health_endpoint():
    content = _read(RUNBOOK_DOC)
    assert "/health" in content


def test_runbook_mentions_ready_endpoint():
    content = _read(RUNBOOK_DOC)
    assert "/health/ready" in content or "ready" in content.lower()


def test_runbook_mentions_vapi_curl():
    content = _read(RUNBOOK_DOC)
    assert "curl" in content and "capture-appointment-request" in content


def test_runbook_mentions_demo_patient():
    assert "Demo Patient" in _read(RUNBOOK_DOC)


def test_runbook_mentions_view_summary():
    content = _read(RUNBOOK_DOC)
    assert "View summary" in content or "view summary" in content.lower()


def test_runbook_mentions_confirm():
    content = _read(RUNBOOK_DOC)
    assert "Confirm" in content or "confirm" in content


def test_runbook_mentions_no_real_patient_data():
    content = _read(RUNBOOK_DOC).lower()
    assert "no real patient data" in content or "fake" in content


def test_runbook_mentions_no_secrets_recorded():
    content = _read(RUNBOOK_DOC).lower()
    assert "no secrets" in content or "not recorded" in content or "do not record" in content


def test_runbook_mentions_staging_clinic_id():
    assert "1a5bbc75-c1b0-4488-94aa-64b3f1c50056" in _read(RUNBOOK_DOC)


def test_runbook_no_hardcoded_secrets():
    content = _read(RUNBOOK_DOC)
    assert not re.search(r"eyJ[A-Za-z0-9_\-]{20,}", content), "JWT in runbook"
    assert "sk-" not in content, "API key in runbook"


# ---------------------------------------------------------------------------
# 3. Vapi German/English assistant setup doc
# ---------------------------------------------------------------------------

def test_vapi_setup_doc_exists():
    assert os.path.isfile(VAPI_SETUP_DOC)


def test_vapi_setup_doc_mentions_german_first():
    content = _read(VAPI_SETUP_DOC)
    assert "German" in content and ("first" in content.lower() or "primary" in content.lower() or "German-first" in content)


def test_vapi_setup_doc_mentions_english_fallback():
    content = _read(VAPI_SETUP_DOC)
    assert "English" in content and "fallback" in content.lower()


def test_vapi_setup_doc_mentions_no_diagnosis():
    content = _read(VAPI_SETUP_DOC)
    assert "no diagnosis" in content.lower() or "Never diagnose" in content or "keine Diagnose" in content or "diagnos" in content.lower()


def test_vapi_setup_doc_mentions_no_medical_advice():
    content = _read(VAPI_SETUP_DOC)
    assert "no medical advice" in content.lower() or "medical advice" in content.lower()


def test_vapi_setup_doc_mentions_staff_doctor_confirms():
    content = _read(VAPI_SETUP_DOC)
    assert ("staff" in content.lower() or "doctor" in content.lower()) and "confirm" in content.lower()


def test_vapi_setup_doc_mentions_patient_name():
    assert "patient_name" in _read(VAPI_SETUP_DOC)


def test_vapi_setup_doc_mentions_phone():
    assert "phone" in _read(VAPI_SETUP_DOC).lower()


def test_vapi_setup_doc_mentions_preferred_time():
    content = _read(VAPI_SETUP_DOC)
    assert "preferred_starts_at" in content or "preferred_time" in content or "preferred" in content.lower()


def test_vapi_setup_doc_mentions_tool_call_json():
    content = _read(VAPI_SETUP_DOC)
    assert "tool call" in content.lower() or "tool_call" in content or "Tool Call" in content


def test_vapi_setup_doc_mentions_recording_ingestion_pending():
    content = _read(VAPI_SETUP_DOC)
    assert "recording" in content.lower() and ("pending" in content.lower() or "not yet" in content.lower())


def test_vapi_setup_doc_no_secrets():
    content = _read(VAPI_SETUP_DOC)
    assert not re.search(r"eyJ[A-Za-z0-9_\-]{20,}", content), "JWT in Vapi setup doc"
    assert "sk-" not in content, "API key in Vapi setup doc"


# ---------------------------------------------------------------------------
# 4. Staging clinic config — language/display fields
# ---------------------------------------------------------------------------

def test_staging_clinic_config_exists():
    assert os.path.isfile(TENANT_CONFIG)


def test_staging_clinic_config_has_language_de():
    with open(TENANT_CONFIG, encoding="utf-8") as f:
        config = json.load(f)
    assert config.get("language") == "de"


def test_staging_clinic_config_has_fallback_language_en():
    with open(TENANT_CONFIG, encoding="utf-8") as f:
        config = json.load(f)
    assert config.get("fallback_language") == "en"


def test_staging_clinic_config_has_clinic_display_name():
    with open(TENANT_CONFIG, encoding="utf-8") as f:
        config = json.load(f)
    assert config.get("clinic_display_name") is not None


def test_staging_clinic_config_has_specialty():
    with open(TENANT_CONFIG, encoding="utf-8") as f:
        config = json.load(f)
    assert config.get("specialty") is not None


def test_staging_clinic_config_appointment_intake_enabled():
    with open(TENANT_CONFIG, encoding="utf-8") as f:
        config = json.load(f)
    features = config.get("features", {})
    assert features.get("appointment_intake_enabled") is True


def test_staging_clinic_config_recording_ingestion_disabled():
    with open(TENANT_CONFIG, encoding="utf-8") as f:
        config = json.load(f)
    features = config.get("features", {})
    assert features.get("recording_ingestion_enabled") is False


def test_staging_clinic_config_production_phi_disabled():
    with open(TENANT_CONFIG, encoding="utf-8") as f:
        config = json.load(f)
    features = config.get("features", {})
    assert features.get("production_phi_enabled") is False


def test_staging_clinic_config_no_secrets():
    content = _read(TENANT_CONFIG)
    assert not re.search(r"eyJ[A-Za-z0-9_\-]{20,}", content), "JWT in clinic config"
    assert "sk-" not in content, "API key in clinic config"
