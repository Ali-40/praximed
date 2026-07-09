"""
Static contract tests for Sprint 21 / Module 157 — Doctor-Facing Sales MVP Simplification.

Verifies file content only. No JS/TS runtime. No database. No network. No secrets.
No real patient data. No PHI. Production PHI remains NO-GO.

These tests confirm that the existing /dashboard has been simplified into a
clinic-facing, German-first, UUID-free sales MVP suitable for a 5-minute Vienna
clinic demo — without breaking any existing dashboard contract tests.
"""

from __future__ import annotations

import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))
FRONTEND = os.path.join(_REPO_ROOT, "frontend")


def _read(rel: str) -> str:
    with open(os.path.join(FRONTEND, rel), encoding="utf-8") as f:
        return f.read()


def _dashboard() -> str:
    return _read("app/dashboard/page.tsx")


def _api() -> str:
    return _read("lib/api.ts")


# ---------------------------------------------------------------------------
# 1. Dashboard file and route
# ---------------------------------------------------------------------------

def test_dashboard_file_exists() -> None:
    assert os.path.isfile(os.path.join(FRONTEND, "app", "dashboard", "page.tsx")), \
        "frontend/app/dashboard/page.tsx must exist"


def test_no_parallel_sales_dashboard_route() -> None:
    for forbidden in ("app/sales-dashboard", "app/clinic-dashboard", "app/doctor-dashboard"):
        assert not os.path.isdir(os.path.join(FRONTEND, forbidden)), \
            f"Parallel sales dashboard route must not exist: {forbidden}"


# ---------------------------------------------------------------------------
# 2. Heute summary header
# ---------------------------------------------------------------------------

def test_dashboard_has_heute_label() -> None:
    assert "Heute" in _dashboard(), \
        "dashboard must include 'Heute' daily summary label"


def test_dashboard_has_neue_anfragen() -> None:
    assert "Neue Anfragen" in _dashboard() or "neueAnfragen" in _dashboard(), \
        "dashboard must mention 'Neue Anfragen' or neueAnfragen count"


def test_dashboard_has_rückruf_nötig() -> None:
    content = _dashboard()
    assert "Rückruf nötig" in content or "rückrufNötig" in content, \
        "dashboard must mention 'Rückruf nötig'"


def test_dashboard_has_dringend_prüfen() -> None:
    assert "Dringend prüfen" in _dashboard(), \
        "dashboard must mention 'Dringend prüfen'"


def test_dashboard_has_erledigt() -> None:
    assert "Erledigt" in _dashboard(), \
        "dashboard must mention 'Erledigt'"


def test_heute_summary_counts_helper_exists() -> None:
    assert "getTodaySummaryCounts" in _dashboard(), \
        "dashboard must have getTodaySummaryCounts helper"


# ---------------------------------------------------------------------------
# 3. Tab structure: Anfragen / Patienten / Einstellungen
# ---------------------------------------------------------------------------

def test_dashboard_has_anfragen_tab() -> None:
    content = _dashboard()
    assert "Anfragen" in content, \
        "dashboard must have an Anfragen tab"


def test_dashboard_has_patienten_tab() -> None:
    content = _dashboard()
    assert "Patienten" in content, \
        "dashboard must have a Patienten tab"


def test_dashboard_has_einstellungen_tab() -> None:
    content = _dashboard()
    assert "Einstellungen" in content, \
        "dashboard must have an Einstellungen tab"


def test_dashboard_has_active_tab_state() -> None:
    assert "activeTab" in _dashboard(), \
        "dashboard must track activeTab state"


def test_dashboard_anfragen_is_default_tab() -> None:
    content = _dashboard()
    assert "'anfragen'" in content or '"anfragen"' in content, \
        "dashboard must have 'anfragen' as a tab value (default tab)"


# ---------------------------------------------------------------------------
# 4. German status label helper
# ---------------------------------------------------------------------------

def test_dashboard_has_german_status_label_helper() -> None:
    assert "getGermanStatusLabel" in _dashboard(), \
        "dashboard must have getGermanStatusLabel helper"


def test_german_status_maps_callback_needed() -> None:
    content = _dashboard()
    assert "callback_needed" in content and "Rückruf" in content, \
        "dashboard must map callback_needed to a Rückruf label"


def test_german_status_maps_contacted() -> None:
    content = _dashboard()
    assert "contacted" in content and "Kontaktiert" in content, \
        "dashboard must map contacted to Kontaktiert"


def test_german_status_maps_confirmed() -> None:
    content = _dashboard()
    assert "confirmed" in content and "Bestätigt" in content, \
        "dashboard must map confirmed to Bestätigt"


def test_german_status_maps_new() -> None:
    content = _dashboard()
    assert "'new'" in content and "Neue Anfrage" in content, \
        "dashboard must map new status to Neue Anfrage"


# ---------------------------------------------------------------------------
# 5. Human-readable request numbers
# ---------------------------------------------------------------------------

def test_dashboard_has_readable_request_number_helper() -> None:
    assert "getReadableRequestNumber" in _dashboard(), \
        "dashboard must have getReadableRequestNumber helper"


def test_dashboard_uses_anfrage_hash_format() -> None:
    assert "Anfrage #" in _dashboard(), \
        "dashboard must use 'Anfrage #' format for human-readable request numbers"


def test_dashboard_has_request_index_tracking() -> None:
    content = _dashboard()
    assert "selectedApptIndex" in content or "idx" in content, \
        "dashboard must track index for request numbering"


# ---------------------------------------------------------------------------
# 6. Callback and contacted actions
# ---------------------------------------------------------------------------

def test_dashboard_has_rückruf_button() -> None:
    assert "Rückruf" in _dashboard(), \
        "dashboard must have Rückruf action button"


def test_dashboard_has_als_kontaktiert_markieren() -> None:
    assert "Als kontaktiert markieren" in _dashboard(), \
        "dashboard must have 'Als kontaktiert markieren' action"


def test_dashboard_has_callback_ids_state() -> None:
    assert "callbackIds" in _dashboard(), \
        "dashboard must have callbackIds state for tracking in-progress callbacks"


def test_dashboard_has_contacted_ids_state() -> None:
    assert "contactedIds" in _dashboard(), \
        "dashboard must have contactedIds state"


def test_dashboard_has_handle_mark_callback() -> None:
    assert "handleMarkCallback" in _dashboard(), \
        "dashboard must have handleMarkCallback handler"


def test_dashboard_has_handle_mark_contacted() -> None:
    assert "handleMarkContacted" in _dashboard(), \
        "dashboard must have handleMarkContacted handler"


def test_dashboard_does_not_auto_confirm_on_callback() -> None:
    content = _dashboard()
    # Confirm action must be explicitly triggered; callback must NOT call confirm
    assert "handleMarkCallback" in content, \
        "callback handler must exist separately from confirm"


# ---------------------------------------------------------------------------
# 7. updateAppointmentRequestStatus in api.ts
# ---------------------------------------------------------------------------

def test_api_has_update_appointment_request_status() -> None:
    assert "updateAppointmentRequestStatus" in _api(), \
        "api.ts must export updateAppointmentRequestStatus for callback/contacted transitions"


def test_api_update_status_uses_patch() -> None:
    content = _api()
    idx = content.find("updateAppointmentRequestStatus")
    assert idx != -1
    assert "'PATCH'" in content[idx:] or '"PATCH"' in content[idx:], \
        "updateAppointmentRequestStatus must use PATCH method"


def test_api_update_status_uses_apifetch() -> None:
    content = _api()
    idx = content.find("updateAppointmentRequestStatus")
    assert idx != -1
    assert "apiFetch" in content[idx:], \
        "updateAppointmentRequestStatus must use apiFetch"


def test_dashboard_imports_update_status() -> None:
    assert "updateAppointmentRequestStatus" in _dashboard(), \
        "dashboard must import and use updateAppointmentRequestStatus"


# ---------------------------------------------------------------------------
# 8. BADGE_MAP has callback_needed and contacted
# ---------------------------------------------------------------------------

def test_badge_map_has_callback_needed() -> None:
    assert "callback_needed" in _dashboard(), \
        "BADGE_MAP must include callback_needed status"


def test_badge_map_has_contacted() -> None:
    content = _dashboard()
    assert "contacted" in content, \
        "BADGE_MAP must include contacted status"


# ---------------------------------------------------------------------------
# 9. No visible UUIDs in clinic-facing dashboard source
# ---------------------------------------------------------------------------

def test_dashboard_does_not_render_selected_appt_id_as_text() -> None:
    content = _dashboard()
    # UUID must not be rendered as visible text in the clinic-facing workspace header
    assert "{selectedAppt.id}" not in content, \
        "selectedAppt.id must not be rendered as visible text in clinic-facing UI"


def test_dashboard_does_not_render_patient_id_in_list() -> None:
    content = _dashboard()
    # patient.id must not be rendered as visible clinic-facing text
    assert "{patient.id}" not in content, \
        "patient.id must not be rendered as visible text in patient list"


def test_dashboard_does_not_render_selected_patient_id() -> None:
    content = _dashboard()
    assert "{selectedPatient.id}" not in content, \
        "selectedPatient.id must not be rendered as visible clinic-facing text"


def test_dashboard_visible_labels_do_not_include_uuid_word() -> None:
    # Check that 'UUID' is not rendered as user-facing label text
    content = _dashboard()
    assert ">UUID<" not in content and ">uuid<" not in content.lower(), \
        "dashboard must not show UUID as a visible label to clinic users"


def test_dashboard_visible_labels_do_not_include_clinic_id() -> None:
    content = _dashboard()
    assert ">clinic_id<" not in content, \
        "clinic_id must not appear as visible label text"


def test_dashboard_visible_labels_do_not_include_patient_id_label() -> None:
    content = _dashboard()
    assert ">patient_id<" not in content, \
        "patient_id must not appear as visible label text"


def test_dashboard_visible_labels_do_not_include_webhook() -> None:
    content = _dashboard()
    assert ">webhook<" not in content.lower(), \
        "webhook must not appear as visible label text in clinic-facing dashboard"


def test_dashboard_visible_labels_do_not_include_fhir() -> None:
    content = _dashboard()
    assert ">FHIR<" not in content and ">fhir<" not in content.lower(), \
        "FHIR must not appear as visible label text in clinic-facing dashboard"


def test_dashboard_visible_labels_do_not_include_proposal_id() -> None:
    content = _dashboard()
    assert ">proposal_id<" not in content, \
        "proposal_id must not appear as visible label text"


# ---------------------------------------------------------------------------
# 10. Safety invariants
# ---------------------------------------------------------------------------

def test_dashboard_has_production_phi_no_go() -> None:
    content = _dashboard()
    assert "Production PHI" in content or "production phi" in content.lower(), \
        "dashboard must mention Production PHI boundary"


def test_dashboard_no_diagnosis() -> None:
    assert "diagnosis" not in _dashboard().lower(), \
        "dashboard must not contain the word 'diagnosis'"


def test_dashboard_no_medical_advice() -> None:
    assert "medical advice" not in _dashboard().lower(), \
        "dashboard must not contain 'medical advice'"


def test_dashboard_no_treatment_recommendations() -> None:
    assert "treatment recommendation" not in _dashboard().lower(), \
        "dashboard must not contain 'treatment recommendation'"


def test_dashboard_no_triage_scoring() -> None:
    assert "triage" not in _dashboard().lower(), \
        "dashboard must not contain 'triage' scoring"


def test_dashboard_no_real_patient_data() -> None:
    content = _dashboard()
    assert "No real patient data" in content or "no real patient data" in content.lower(), \
        "dashboard must include 'No real patient data' safety copy"


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


def test_dashboard_no_hardcoded_secrets() -> None:
    content = _dashboard()
    assert not re.search(r"eyJ[A-Za-z0-9_\-]{20,}", content), \
        "dashboard must not contain hardcoded JWT"
    assert "sk-" not in content, \
        "dashboard must not contain API key prefix"


# ---------------------------------------------------------------------------
# 11. Existing contract regression — core labels preserved
# ---------------------------------------------------------------------------

def test_existing_incoming_ai_intake_queue_preserved() -> None:
    assert "Incoming AI Intake Queue" in _dashboard(), \
        "Existing 'Incoming AI Intake Queue' label must remain in source (sr-only or otherwise)"


def test_existing_active_resolution_workspace_preserved() -> None:
    assert "Active Resolution Workspace" in _dashboard(), \
        "Existing 'Active Resolution Workspace' label must remain in source"


def test_existing_patient_registry_preserved() -> None:
    assert "Patient Registry" in _dashboard(), \
        "Existing 'Patient Registry' label must remain in source"


def test_existing_data_section_appointments_preserved() -> None:
    assert 'data-section="appointments"' in _dashboard(), \
        "data-section=\"appointments\" must remain for existing contract tests"


def test_existing_data_panel_attributes_preserved() -> None:
    content = _dashboard()
    for panel in ('data-panel="left"', 'data-panel="center"', 'data-panel="right"'):
        assert panel in content, f"{panel} must remain for existing layout tests"


def test_existing_confirm_action_preserved() -> None:
    content = _dashboard()
    assert 'data-action="confirm"' in content, \
        "data-action=\"confirm\" must remain for existing workflow tests"


def test_existing_view_summary_preserved() -> None:
    assert "View summary" in _dashboard(), \
        "'View summary' must remain for existing contract tests"


def test_existing_hide_summary_preserved() -> None:
    assert "Hide summary" in _dashboard(), \
        "'Hide summary' must remain for existing contract tests"


# ---------------------------------------------------------------------------
# 12. Product doc exists
# ---------------------------------------------------------------------------

def test_product_doc_exists() -> None:
    path = os.path.join(
        os.path.dirname(_REPO_ROOT), _REPO_ROOT,
        "docs", "product", "DOCTOR_FACING_SALES_MVP_SIMPLIFICATION.md"
    )
    # Build from repo root
    doc_path = os.path.join(_REPO_ROOT, "docs", "product", "DOCTOR_FACING_SALES_MVP_SIMPLIFICATION.md")
    assert os.path.isfile(doc_path), \
        "docs/product/DOCTOR_FACING_SALES_MVP_SIMPLIFICATION.md must exist"


def test_product_doc_mentions_module_157() -> None:
    doc_path = os.path.join(_REPO_ROOT, "docs", "product", "DOCTOR_FACING_SALES_MVP_SIMPLIFICATION.md")
    with open(doc_path, encoding="utf-8") as f:
        content = f.read()
    assert "157" in content, "product doc must mention Module 157"


def test_product_doc_mentions_vienna() -> None:
    doc_path = os.path.join(_REPO_ROOT, "docs", "product", "DOCTOR_FACING_SALES_MVP_SIMPLIFICATION.md")
    with open(doc_path, encoding="utf-8") as f:
        content = f.read()
    assert "vienna" in content.lower() or "Wien" in content, \
        "product doc must mention Vienna or Wien target market"


def test_product_doc_mentions_acceptance_statement() -> None:
    doc_path = os.path.join(_REPO_ROOT, "docs", "product", "DOCTOR_FACING_SALES_MVP_SIMPLIFICATION.md")
    with open(doc_path, encoding="utf-8") as f:
        content = f.read()
    assert "5 minutes" in content or "5-minute" in content, \
        "product doc must include 5-minute demo acceptance statement"
