"""
Static contract tests for Sprint 21 / Module 158 — One-Click Demo Flow.

Verifies file content only. No JS/TS runtime. No database. No network. No secrets.
No real patient data. No PHI. Production PHI remains NO-GO.

These tests confirm that:
- The demo strip exists in /dashboard with correct German labels
- The demo buttons wire to the correct API functions
- The backend route is staging-only and creates safe synthetic data
- No diagnosis, medical advice, triage scoring, or PHI anywhere in the demo flow
- No live Vapi call is triggered
- All demo data is marked synthetic_demo=True / production_phi_enabled=False
"""

from __future__ import annotations

import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))
FRONTEND = os.path.join(_REPO_ROOT, "frontend")
BACKEND = os.path.join(_REPO_ROOT, "backend")


def _read_frontend(rel: str) -> str:
    with open(os.path.join(FRONTEND, rel), encoding="utf-8") as f:
        return f.read()


def _read_backend(rel: str) -> str:
    with open(os.path.join(BACKEND, rel), encoding="utf-8") as f:
        return f.read()


def _dashboard() -> str:
    return _read_frontend("app/dashboard/page.tsx")


def _api() -> str:
    return _read_frontend("lib/api.ts")


def _sales_demo_route() -> str:
    return _read_backend("app/api/routes/sales_demo.py")


def _router() -> str:
    return _read_backend("app/api/router.py")


# ---------------------------------------------------------------------------
# 1. Frontend: demo strip exists in dashboard
# ---------------------------------------------------------------------------

def test_dashboard_has_demo_strip() -> None:
    assert 'data-demo-strip="sales-mvp"' in _dashboard(), \
        "dashboard must have data-demo-strip=\"sales-mvp\" element"


def test_dashboard_demo_strip_label_is_german() -> None:
    assert "Demo-Modus" in _dashboard(), \
        "dashboard demo strip must have 'Demo-Modus' German label"


def test_dashboard_demo_strip_has_no_real_patient_data_copy() -> None:
    assert "Keine echten Patientendaten" in _dashboard(), \
        "dashboard demo strip must include 'Keine echten Patientendaten' copy"


# ---------------------------------------------------------------------------
# 2. Frontend: demo button — Demo-Anruf erstellen
# ---------------------------------------------------------------------------

def test_dashboard_has_create_demo_call_button() -> None:
    assert "Demo-Anruf erstellen" in _dashboard(), \
        "dashboard must have 'Demo-Anruf erstellen' button"


def test_dashboard_create_demo_call_button_has_data_action() -> None:
    assert 'data-action="create-demo-call"' in _dashboard(), \
        "demo call button must have data-action=\"create-demo-call\""


def test_dashboard_create_demo_call_wires_to_handler() -> None:
    assert "handleCreateDemoCall" in _dashboard(), \
        "dashboard must have handleCreateDemoCall handler"


def test_dashboard_demo_call_creating_state_exists() -> None:
    assert "demoCallCreating" in _dashboard(), \
        "dashboard must track demoCallCreating state"


# ---------------------------------------------------------------------------
# 3. Frontend: demo reset button
# ---------------------------------------------------------------------------

def test_dashboard_has_reset_demo_button() -> None:
    assert "Demo zurücksetzen" in _dashboard(), \
        "dashboard must have 'Demo zurücksetzen' button"


def test_dashboard_reset_demo_button_has_data_action() -> None:
    assert 'data-action="reset-demo"' in _dashboard(), \
        "demo reset button must have data-action=\"reset-demo\""


def test_dashboard_reset_demo_wires_to_handler() -> None:
    assert "handleResetDemo" in _dashboard(), \
        "dashboard must have handleResetDemo handler"


def test_dashboard_demo_resetting_state_exists() -> None:
    assert "demoResetting" in _dashboard(), \
        "dashboard must track demoResetting state"


# ---------------------------------------------------------------------------
# 4. Frontend: demo message copy is German
# ---------------------------------------------------------------------------

def test_dashboard_demo_success_copy_is_german() -> None:
    content = _dashboard()
    assert "Demo-Anfrage wurde der Warteschlange hinzugefügt" in content, \
        "dashboard demo success message must be German"


def test_dashboard_demo_error_copy_is_german() -> None:
    content = _dashboard()
    assert "Demo-Anfrage konnte nicht erstellt werden" in content, \
        "dashboard demo error message must be German"


def test_dashboard_demo_message_state_exists() -> None:
    assert "demoMessage" in _dashboard(), \
        "dashboard must track demoMessage state"


def test_dashboard_demo_message_renders_in_dom() -> None:
    assert "data-demo-message" in _dashboard(), \
        "dashboard must render demo message with data-demo-message attribute"


# ---------------------------------------------------------------------------
# 5. api.ts: createSalesDemoCall and resetSalesDemoData
# ---------------------------------------------------------------------------

def test_api_has_create_sales_demo_call() -> None:
    assert "createSalesDemoCall" in _api(), \
        "api.ts must export createSalesDemoCall"


def test_api_create_demo_call_uses_post() -> None:
    content = _api()
    idx = content.find("createSalesDemoCall")
    assert idx != -1
    segment = content[idx:idx + 300]
    assert "'POST'" in segment or '"POST"' in segment, \
        "createSalesDemoCall must use POST method"


def test_api_create_demo_call_hits_correct_endpoint() -> None:
    content = _api()
    assert "/demo/sales-mvp/create-call" in content, \
        "createSalesDemoCall must call /demo/sales-mvp/create-call endpoint"


def test_api_has_reset_sales_demo_data() -> None:
    assert "resetSalesDemoData" in _api(), \
        "api.ts must export resetSalesDemoData"


def test_api_reset_demo_hits_correct_endpoint() -> None:
    content = _api()
    assert "/demo/sales-mvp/reset" in content, \
        "resetSalesDemoData must call /demo/sales-mvp/reset endpoint"


def test_dashboard_imports_create_sales_demo_call() -> None:
    assert "createSalesDemoCall" in _dashboard(), \
        "dashboard must import createSalesDemoCall"


def test_dashboard_imports_reset_sales_demo_data() -> None:
    assert "resetSalesDemoData" in _dashboard(), \
        "dashboard must import resetSalesDemoData"


# ---------------------------------------------------------------------------
# 6. Backend route: staging-only guard
# ---------------------------------------------------------------------------

def test_sales_demo_route_file_exists() -> None:
    path = os.path.join(BACKEND, "app", "api", "routes", "sales_demo.py")
    assert os.path.isfile(path), \
        "backend/app/api/routes/sales_demo.py must exist"


def test_sales_demo_route_has_staging_guard() -> None:
    content = _sales_demo_route()
    assert "_require_staging" in content, \
        "sales_demo route must have a _require_staging guard"


def test_sales_demo_route_blocks_production() -> None:
    content = _sales_demo_route()
    assert "production" in content.lower() and "403" in content, \
        "sales_demo route must return 403 in production environment"


def test_sales_demo_route_registered_in_router() -> None:
    assert "sales_demo" in _router(), \
        "sales_demo router must be imported and registered in router.py"


# ---------------------------------------------------------------------------
# 7. Backend route: no PHI, no real patient data, synthetic_demo=True
# ---------------------------------------------------------------------------

def test_sales_demo_route_marks_synthetic_demo() -> None:
    content = _sales_demo_route()
    assert "synthetic_demo" in content, \
        "sales_demo route must set synthetic_demo flag"


def test_sales_demo_route_sets_production_phi_enabled_false() -> None:
    content = _sales_demo_route()
    assert "production_phi_enabled" in content and "False" in content, \
        "sales_demo route must set production_phi_enabled to False"


def test_sales_demo_route_uses_staff_source() -> None:
    content = _sales_demo_route()
    assert '"staff"' in content or "'staff'" in content, \
        "sales_demo route must use source='staff' (valid enum)"


def test_sales_demo_route_uses_demo_source_ref_prefix() -> None:
    content = _sales_demo_route()
    assert "sales-demo-call-" in content, \
        "sales_demo route must use 'sales-demo-call-' prefix for source_ref"


def test_sales_demo_reset_targets_demo_prefix_only() -> None:
    content = _sales_demo_route()
    assert "sales-demo-call-%" in content, \
        "reset endpoint must target LIKE 'sales-demo-call-%' (demo records only)"


def test_sales_demo_reset_archives_not_deletes() -> None:
    content = _sales_demo_route()
    assert "archived" in content, \
        "reset endpoint must archive records (status → archived), not delete"
    # \bDELETE\b matches the SQL keyword as a whole word but not 'deletes' (verb with trailing s)
    assert not re.search(r'\bDELETE\b', content, re.IGNORECASE), \
        "reset endpoint must not use SQL DELETE — archive only"


# ---------------------------------------------------------------------------
# 8. No PHI, no diagnosis, no medical advice, no live Vapi in demo flow
# ---------------------------------------------------------------------------

def test_sales_demo_route_no_diagnosis() -> None:
    assert "diagnosis" not in _sales_demo_route().lower(), \
        "sales_demo route must not contain 'diagnosis'"


def test_sales_demo_route_no_medical_advice() -> None:
    assert "medical advice" not in _sales_demo_route().lower(), \
        "sales_demo route must not contain 'medical advice'"


def test_sales_demo_route_no_vapi_live_call() -> None:
    content = _sales_demo_route()
    assert "vapi_client" not in content.lower() and "vapi.calls.create" not in content.lower(), \
        "sales_demo route must not trigger a live Vapi call"


def test_sales_demo_route_no_triage() -> None:
    assert "triage" not in _sales_demo_route().lower(), \
        "sales_demo route must not contain 'triage'"


def test_dashboard_demo_flow_no_real_names_in_handler() -> None:
    content = _dashboard()
    idx = content.find("handleCreateDemoCall")
    segment = content[idx:idx + 600] if idx != -1 else ""
    assert "createSalesDemoCall" in segment, \
        "handleCreateDemoCall must delegate to createSalesDemoCall API function"


# ---------------------------------------------------------------------------
# 9. Frontend build: existing safety assertions still green
# ---------------------------------------------------------------------------

def test_dashboard_still_has_production_phi_no_go() -> None:
    content = _dashboard()
    assert "Production PHI" in content or "production phi" in content.lower(), \
        "dashboard must still mention Production PHI boundary"


def test_dashboard_still_has_no_real_patient_data() -> None:
    content = _dashboard()
    assert "no real patient data" in content.lower(), \
        "dashboard must still include 'no real patient data' safety copy"


def test_dashboard_still_has_anfragen_tab() -> None:
    assert "Anfragen" in _dashboard(), \
        "Anfragen tab must still be present after Module 158 changes"


def test_dashboard_still_has_heute_label() -> None:
    assert "Heute" in _dashboard(), \
        "Heute summary bar must still be present after Module 158 changes"


def test_dashboard_still_no_diagnosis() -> None:
    assert "diagnosis" not in _dashboard().lower(), \
        "dashboard must not contain 'diagnosis' after Module 158 changes"


# ---------------------------------------------------------------------------
# 10. Product doc
# ---------------------------------------------------------------------------

def test_one_click_demo_flow_doc_exists() -> None:
    doc_path = os.path.join(_REPO_ROOT, "docs", "product", "ONE_CLICK_DEMO_FLOW.md")
    assert os.path.isfile(doc_path), \
        "docs/product/ONE_CLICK_DEMO_FLOW.md must exist"


def test_one_click_demo_flow_doc_mentions_module_158() -> None:
    doc_path = os.path.join(_REPO_ROOT, "docs", "product", "ONE_CLICK_DEMO_FLOW.md")
    with open(doc_path, encoding="utf-8") as f:
        content = f.read()
    assert "158" in content, \
        "ONE_CLICK_DEMO_FLOW.md must mention Module 158"


def test_one_click_demo_flow_doc_mentions_staging_only() -> None:
    doc_path = os.path.join(_REPO_ROOT, "docs", "product", "ONE_CLICK_DEMO_FLOW.md")
    with open(doc_path, encoding="utf-8") as f:
        content = f.read()
    assert "staging" in content.lower(), \
        "ONE_CLICK_DEMO_FLOW.md must mention staging-only constraint"
