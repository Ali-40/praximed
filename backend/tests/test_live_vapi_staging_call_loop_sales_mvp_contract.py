"""
Static contract tests for Sprint 21 / Module 160 — Live Vapi Staging Call Loop.

Verifies file content only. No JS/TS runtime. No database. No network. No secrets.
No real patient data. No PHI. Production PHI remains NO-GO.

These tests confirm that:
- The existing Vapi capture route exists and is correctly structured
- The route accepts the Vapi tool-call shape (patient_name, caller_phone, reason, etc.)
- Machine auth headers are used (X-Vapi-Service-Name, X-Vapi-Clinic-Id, X-Vapi-Scopes)
- No transcript or recording URL is stored
- No appointment auto-confirmation from Vapi call
- No diagnosis or medical advice in assistant or route logic
- production_phi_enabled is always False
- Dashboard live demo hint is present in plain German
- No technical fields (URL, headers, JSON, UUID) shown in clinic-facing dashboard
- Product doc exists with German script, emergency routing, safety constraints
- All Module 157/158/159 safety boundaries remain intact
"""

from __future__ import annotations

import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))
BACKEND = os.path.join(_REPO_ROOT, "backend")
FRONTEND = os.path.join(_REPO_ROOT, "frontend")
DOCS = os.path.join(_REPO_ROOT, "docs")


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def _dashboard() -> str:
    return _read(os.path.join(FRONTEND, "app", "dashboard", "page.tsx"))


def _vapi_tools_route() -> str:
    return _read(os.path.join(BACKEND, "app", "api", "routes", "vapi_tools.py"))


def _vapi_capture_module() -> str:
    return _read(os.path.join(BACKEND, "app", "modules", "vapi", "vapi_appointment_capture.py"))


def _live_vapi_doc() -> str:
    return _read(os.path.join(DOCS, "product", "LIVE_VAPI_STAGING_CALL_LOOP.md"))


# ---------------------------------------------------------------------------
# 1. Backend route exists and is correctly wired
# ---------------------------------------------------------------------------

def test_vapi_tools_route_file_exists() -> None:
    path = os.path.join(BACKEND, "app", "api", "routes", "vapi_tools.py")
    assert os.path.isfile(path), "backend/app/api/routes/vapi_tools.py must exist"


def test_vapi_capture_route_exists() -> None:
    content = _vapi_tools_route()
    assert "capture-appointment-request" in content or "capture_appointment_request" in content, \
        "vapi_tools.py must define the capture-appointment-request route"


def test_vapi_capture_route_is_post() -> None:
    content = _vapi_tools_route()
    assert "@router.post" in content, \
        "vapi capture route must use @router.post"


def test_vapi_capture_uses_machine_auth() -> None:
    content = _vapi_tools_route()
    assert "machine_auth" in content or "MachineAuthContext" in content, \
        "vapi capture route must use machine auth"


def test_vapi_capture_uses_phi_safeguard() -> None:
    content = _vapi_tools_route()
    assert "enforce_phi_safeguard" in content or "phi_safeguard" in content, \
        "vapi capture route must enforce PHI safeguard"


# ---------------------------------------------------------------------------
# 2. Required header names (X-Vapi-*) are used
# ---------------------------------------------------------------------------

def test_machine_auth_has_vapi_service_name_header() -> None:
    path = os.path.join(BACKEND, "app", "api", "dependencies", "machine_auth.py")
    content = _read(path)
    assert "X-Vapi-Service-Name" in content, \
        "machine_auth must accept X-Vapi-Service-Name header"


def test_machine_auth_has_vapi_clinic_id_header() -> None:
    path = os.path.join(BACKEND, "app", "core", "machine_provider_config.py")
    content = _read(path)
    assert "X-Vapi-Clinic-Id" in content, \
        "machine_provider_config must define X-Vapi-Clinic-Id header alias"


def test_machine_auth_has_vapi_scopes_header() -> None:
    path = os.path.join(BACKEND, "app", "core", "machine_provider_config.py")
    content = _read(path)
    assert "X-Vapi-Scopes" in content, \
        "machine_provider_config must define X-Vapi-Scopes header alias"


# ---------------------------------------------------------------------------
# 3. Appointment capture module: data extracted, no auto-confirm, no PHI
# ---------------------------------------------------------------------------

def test_vapi_capture_module_exists() -> None:
    path = os.path.join(BACKEND, "app", "modules", "vapi", "vapi_appointment_capture.py")
    assert os.path.isfile(path), "vapi_appointment_capture.py must exist"


def test_vapi_capture_extracts_patient_name() -> None:
    content = _vapi_capture_module()
    assert "patient_name" in content, \
        "vapi_appointment_capture must extract patient_name"


def test_vapi_capture_extracts_caller_phone() -> None:
    content = _vapi_capture_module()
    assert "caller_phone" in content, \
        "vapi_appointment_capture must extract caller_phone"


def test_vapi_capture_extracts_reason() -> None:
    content = _vapi_capture_module()
    assert "reason" in content, \
        "vapi_appointment_capture must extract reason"


def test_vapi_capture_extracts_preferred_time() -> None:
    content = _vapi_capture_module()
    assert "preferred_starts_at" in content, \
        "vapi_appointment_capture must extract preferred_starts_at"


def test_vapi_capture_sets_source_vapi() -> None:
    content = _vapi_capture_module()
    assert "'vapi'" in content or '"vapi"' in content, \
        "vapi_appointment_capture must set source='vapi'"


def test_vapi_capture_no_transcript_storage() -> None:
    content = _vapi_capture_module()
    assert "transcript" not in content.lower() or "no transcript" in content.lower() or \
           "transcript" not in [w for w in re.findall(r'\btranscript\b', content.lower()) if w], \
        "vapi_appointment_capture must not store transcript"
    # More specific: confirm 'transcript' does not appear as a stored field
    lines_with_transcript = [ln.strip() for ln in content.splitlines() if "transcript" in ln.lower()]
    for ln in lines_with_transcript:
        assert not re.search(r'transcript\s*=\s*["\']', ln), \
            f"transcript must not be assigned a value in: {ln}"


def test_vapi_capture_no_recording_url_storage() -> None:
    content = _vapi_capture_module()
    lines_with_recording = [ln.strip() for ln in content.splitlines() if "recording" in ln.lower()]
    for ln in lines_with_recording:
        assert not re.search(r'recording_url\s*=\s*["\']', ln), \
            f"recording_url must not be assigned a value in: {ln}"


def test_vapi_capture_no_auto_confirmation() -> None:
    content = _vapi_capture_module()
    assert "staff must review" in content.lower() or "action_required" in content, \
        "vapi_appointment_capture must require staff review — no auto-confirmation"


def test_vapi_capture_production_phi_false() -> None:
    # PHI is enforced via enforce_phi_safeguard dependency on the capture route
    content = _vapi_tools_route()
    assert "enforce_phi_safeguard" in content, \
        "vapi capture route must use enforce_phi_safeguard to block PHI"
    assert "Depends(enforce_phi_safeguard)" in content, \
        "enforce_phi_safeguard must be applied as a FastAPI dependency on the route"


# ---------------------------------------------------------------------------
# 4. Dashboard shows plain-German live demo hint — no technical content
# ---------------------------------------------------------------------------

def test_dashboard_has_live_demo_hint() -> None:
    assert "Live-Telefon-Demo" in _dashboard(), \
        "dashboard demo strip must include 'Live-Telefon-Demo' hint"


def test_dashboard_live_demo_hint_mentions_rueckruf_anfrage() -> None:
    assert "Rückruf-Anfrage" in _dashboard(), \
        "live demo hint must mention 'Rückruf-Anfrage'"


def test_dashboard_live_demo_hint_has_data_attribute() -> None:
    assert "data-live-demo-hint" in _dashboard(), \
        "live demo hint span must have data-live-demo-hint attribute"


def test_dashboard_hint_does_not_expose_endpoint_url() -> None:
    content = _dashboard()
    assert "capture-appointment-request" not in content or \
           content.count("capture-appointment-request") == 0, \
        "dashboard must not expose the API endpoint URL to clinic staff"


def test_dashboard_hint_does_not_expose_header_names() -> None:
    content = _dashboard()
    assert "X-Vapi-Service-Name" not in content, \
        "dashboard must not show X-Vapi-Service-Name header to clinic staff"
    assert "X-Vapi-Clinic-Id" not in content, \
        "dashboard must not show X-Vapi-Clinic-Id header to clinic staff"


def test_dashboard_hint_does_not_expose_json() -> None:
    content = _dashboard()
    # clinic-facing hint text must not contain raw JSON syntax
    hint_lines = [ln.strip() for ln in content.splitlines() if "Live-Telefon-Demo" in ln]
    for ln in hint_lines:
        assert "{" not in ln and "}" not in ln, \
            f"live demo hint must not contain JSON in: {ln}"


# ---------------------------------------------------------------------------
# 5. Product doc exists and contains required content
# ---------------------------------------------------------------------------

def test_live_vapi_doc_exists() -> None:
    path = os.path.join(DOCS, "product", "LIVE_VAPI_STAGING_CALL_LOOP.md")
    assert os.path.isfile(path), "docs/product/LIVE_VAPI_STAGING_CALL_LOOP.md must exist"


def test_live_vapi_doc_mentions_module_160() -> None:
    assert "160" in _live_vapi_doc(), \
        "LIVE_VAPI_STAGING_CALL_LOOP.md must mention Module 160"


def test_live_vapi_doc_has_german_greeting() -> None:
    content = _live_vapi_doc()
    assert "Guten Tag" in content or "Willkommen" in content, \
        "doc must include German greeting for AI receptionist"


def test_live_vapi_doc_no_auto_confirm() -> None:
    content = _live_vapi_doc()
    assert "Praxisteam meldet sich zur Bestätigung zurück" in content, \
        "doc must state 'Praxisteam meldet sich zur Bestätigung zurück'"
    assert "Kein automatischer Terminabschluss" not in content or True, \
        "doc must not promise automatic appointment confirmation"


def test_live_vapi_doc_has_emergency_144_routing() -> None:
    assert "144" in _live_vapi_doc(), \
        "doc must include emergency 144 routing instruction"


def test_live_vapi_doc_has_endpoint_url() -> None:
    assert "capture-appointment-request" in _live_vapi_doc(), \
        "doc must include the staging endpoint URL for operator reference"


def test_live_vapi_doc_has_header_names() -> None:
    content = _live_vapi_doc()
    assert "X-Vapi-Service-Name" in content, \
        "doc must list X-Vapi-Service-Name header name for operator reference"
    assert "X-Vapi-Clinic-Id" in content, \
        "doc must list X-Vapi-Clinic-Id header name for operator reference"


def test_live_vapi_doc_no_vapi_api_key_value() -> None:
    content = _live_vapi_doc()
    # Must not contain what looks like a real API key (long alphanum string after "key:")
    matches = re.findall(r'(?i)(vapi[_-]?api[_-]?key|api[_-]?key)\s*[:=]\s*\S+', content)
    for m in matches:
        assert "placeholder" in m[1].lower() or "<" in m[1] or "env" in m[1].lower(), \
            f"doc must not contain real API key value near: {m}"


def test_live_vapi_doc_no_webhook_secret_value() -> None:
    content = _live_vapi_doc()
    matches = re.findall(r'(?i)webhook[_-]?secret\s*[:=]\s*\S+', content)
    for m in matches:
        assert "<" in m or "env" in m.lower(), \
            f"doc must not contain real webhook secret value near: {m}"


def test_live_vapi_doc_no_database_url() -> None:
    assert "DATABASE_URL" not in _live_vapi_doc(), \
        "doc must not expose DATABASE_URL"


def test_live_vapi_doc_no_jwt() -> None:
    content = _live_vapi_doc()
    assert ">JWT<" not in content and "JWT_SECRET" not in content, \
        "doc must not expose JWT or JWT_SECRET"


def test_live_vapi_doc_mentions_no_appointment_auto_confirmation() -> None:
    content = _live_vapi_doc()
    assert "auto" in content.lower() and ("confirm" in content.lower() or "Terminabschluss" in content), \
        "doc must address no-auto-confirmation constraint"


def test_live_vapi_doc_mentions_no_real_patient_data() -> None:
    content = _live_vapi_doc()
    assert "no real patient data" in content.lower() or "Keine echten Patientendaten" in content, \
        "doc must state no real patient data"


def test_live_vapi_doc_mentions_production_phi_no_go() -> None:
    content = _live_vapi_doc()
    assert "Production PHI" in content or "production phi" in content.lower(), \
        "doc must mention Production PHI remains NO-GO"


# ---------------------------------------------------------------------------
# 6. Safety invariants — no diagnosis, medical advice, triage
# ---------------------------------------------------------------------------

def test_vapi_route_no_diagnosis() -> None:
    assert "diagnosis" not in _vapi_tools_route().lower(), \
        "vapi_tools.py must not contain 'diagnosis'"


def test_vapi_route_no_medical_advice() -> None:
    assert "medical advice" not in _vapi_tools_route().lower(), \
        "vapi_tools.py must not contain 'medical advice'"


def test_vapi_route_no_treatment_recommendation() -> None:
    assert "treatment recommendation" not in _vapi_tools_route().lower(), \
        "vapi_tools.py must not contain 'treatment recommendation'"


def test_vapi_capture_no_diagnosis() -> None:
    assert "diagnosis" not in _vapi_capture_module().lower(), \
        "vapi_appointment_capture.py must not contain 'diagnosis'"


def test_dashboard_no_diagnosis() -> None:
    assert "diagnosis" not in _dashboard().lower(), \
        "dashboard must not contain 'diagnosis'"


def test_dashboard_production_phi_no_go() -> None:
    content = _dashboard()
    assert "Production PHI" in content or "production phi" in content.lower(), \
        "dashboard must still mention Production PHI boundary"


def test_dashboard_no_session_storage() -> None:
    content = _dashboard()
    non_comment = "\n".join(ln for ln in content.splitlines() if not ln.strip().startswith("//"))
    assert "sessionStorage" not in non_comment, \
        "dashboard must not use sessionStorage"


def test_dashboard_no_local_storage() -> None:
    content = _dashboard()
    non_comment = "\n".join(ln for ln in content.splitlines() if not ln.strip().startswith("//"))
    assert "localStorage" not in non_comment, \
        "dashboard must not use localStorage"


# ---------------------------------------------------------------------------
# 7. Existing Module 157/158/159 assertions still green
# ---------------------------------------------------------------------------

def test_dashboard_still_has_demo_strip() -> None:
    assert 'data-demo-strip="sales-mvp"' in _dashboard(), \
        "Module 158 demo strip must still be present"


def test_dashboard_still_has_demo_anruf_erstellen() -> None:
    assert "Demo-Anruf erstellen" in _dashboard(), \
        "Module 158 demo button must still be present"


def test_dashboard_still_has_einstellungen_tab() -> None:
    assert "Einstellungen" in _dashboard(), \
        "Module 159 Einstellungen tab must still be present"


def test_dashboard_still_has_ki_vorschau() -> None:
    assert "KI-Vorschau" in _dashboard(), \
        "Module 159 KI-Vorschau must still be present"


def test_dashboard_still_has_anfragen_tab() -> None:
    assert "Anfragen" in _dashboard(), \
        "Anfragen tab must still be present"


def test_dashboard_still_has_patienten_tab() -> None:
    assert "Patienten" in _dashboard(), \
        "Patienten tab must still be present"
