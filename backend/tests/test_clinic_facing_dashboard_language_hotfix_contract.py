"""
Static contract tests for Sprint 21 / Module 162B — Clinic-facing dashboard language hotfix.

Verifies file content only. No database. No network. No secrets.
No real patient data. No PHI. Production PHI remains NO-GO.

Tests confirm:
- Dashboard is German-first in all clinic-facing labels
- Technical terms (vapi badge, ingestion in visible text) are not shown as visible clinic text
- Archived requests have correct German status label
- "Rückruf markieren" button label present
- "Anfrage im Überblick" center heading present
- "Gewünschte Zeit" field label present
- "Noch keine aktiven Anfragen" empty state present
- Summary panel uses German labels
- No English safety blurb in visible workspace text
- All safety invariants from Modules 157–162 remain intact
"""

from __future__ import annotations

import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))
FRONTEND = os.path.join(_REPO_ROOT, "frontend")


def _dashboard() -> str:
    with open(os.path.join(FRONTEND, "app", "dashboard", "page.tsx"), encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. German labels — required visible copy
# ---------------------------------------------------------------------------


def test_dashboard_has_praximed_brand() -> None:
    assert "PraxisMed" in _dashboard(), \
        "dashboard must show PraxisMed brand name"


def test_dashboard_has_anfragen_tab() -> None:
    assert "Anfragen" in _dashboard(), \
        "dashboard must have Anfragen tab"


def test_dashboard_has_patienten_tab() -> None:
    assert "Patienten" in _dashboard(), \
        "dashboard must have Patienten tab"


def test_dashboard_has_einstellungen_tab() -> None:
    assert "Einstellungen" in _dashboard(), \
        "dashboard must have Einstellungen tab"


def test_dashboard_has_demo_anruf_erstellen() -> None:
    assert "Demo-Anruf erstellen" in _dashboard(), \
        "dashboard must have 'Demo-Anruf erstellen' button"


def test_dashboard_has_demo_zuruecksetzen() -> None:
    assert "Demo zurücksetzen" in _dashboard(), \
        "dashboard must have 'Demo zurücksetzen' button"


def test_dashboard_has_anfrage_im_ueberblick() -> None:
    assert "Anfrage im Überblick" in _dashboard(), \
        "dashboard must use 'Anfrage im Überblick' as center panel heading"


def test_dashboard_has_telefon_label() -> None:
    assert "Telefon" in _dashboard(), \
        "dashboard must use 'Telefon' as field label"


def test_dashboard_has_anliegen_label() -> None:
    assert "Anliegen" in _dashboard(), \
        "dashboard must use 'Anliegen' as field label"


def test_dashboard_has_gewuenschte_zeit() -> None:
    assert "Gewünschte Zeit" in _dashboard(), \
        "dashboard must use 'Gewünschte Zeit' as appointment time field label"


def test_dashboard_has_eingegangen_label() -> None:
    assert "Eingegangen" in _dashboard(), \
        "dashboard must use 'Eingegangen' as received date label"


def test_dashboard_has_rueckruf_noetig() -> None:
    assert "Rückruf nötig" in _dashboard(), \
        "dashboard must show 'Rückruf nötig' status"


def test_dashboard_has_rueckruf_markieren_button() -> None:
    assert "Rückruf markieren" in _dashboard(), \
        "dashboard must use 'Rückruf markieren' as the callback button label"


def test_dashboard_has_als_kontaktiert_markieren() -> None:
    assert "Als kontaktiert markieren" in _dashboard(), \
        "dashboard must have 'Als kontaktiert markieren' button"


def test_dashboard_has_archiviert_status() -> None:
    assert "Archiviert" in _dashboard(), \
        "dashboard must map archived status to 'Archiviert'"


def test_dashboard_has_aktiv_status() -> None:
    assert "Aktiv" in _dashboard(), \
        "dashboard must map active status to 'Aktiv'"


def test_dashboard_has_noch_keine_aktiven_anfragen() -> None:
    assert "Noch keine aktiven Anfragen" in _dashboard(), \
        "dashboard must show 'Noch keine aktiven Anfragen' when active list is empty after reset"


def test_dashboard_has_keine_echten_patientendaten() -> None:
    content = _dashboard().lower()
    assert "keine echten patientendaten" in content or "no real patient data" in content, \
        "dashboard must affirm no real patient data"


def test_dashboard_has_praximed_intro_sentence() -> None:
    assert "PraxisMed nimmt Terminanfragen auf" in _dashboard(), \
        "dashboard must include the intro sentence"


def test_dashboard_has_demo_in_3_schritten() -> None:
    assert "Demo in 3 Schritten" in _dashboard(), \
        "dashboard must include the Demo in 3 Schritten helper card"


# ---------------------------------------------------------------------------
# 2. German summary panel labels
# ---------------------------------------------------------------------------


def test_dashboard_summary_panel_has_german_art() -> None:
    assert "Art" in _dashboard(), \
        "summary panel must use German 'Art' (not 'Type')"


def test_dashboard_summary_panel_no_english_type() -> None:
    content = _dashboard()
    assert ">Type<" not in content and "'Type'" not in content and '"Type"' not in content, \
        "summary panel must not use English 'Type' as a visible label"


def test_dashboard_summary_panel_has_german_dringlichkeit() -> None:
    assert "Dringlichkeit" in _dashboard(), \
        "summary panel must use German 'Dringlichkeit' (not 'Urgency')"


def test_dashboard_summary_panel_no_english_urgency() -> None:
    content = _dashboard()
    assert ">Urgency<" not in content and '"Urgency"' not in content, \
        "summary panel must not use English 'Urgency' as a visible label"


def test_dashboard_summary_panel_has_fruehere_besuche() -> None:
    assert "Frühere Besuche" in _dashboard(), \
        "summary panel must use 'Frühere Besuche' (not 'Prior visits')"


def test_dashboard_summary_panel_no_prior_visits() -> None:
    assert "Prior visits" not in _dashboard(), \
        "summary panel must not contain English 'Prior visits'"


def test_dashboard_summary_panel_has_empfohlene_aktion() -> None:
    assert "Empfohlene Aktion" in _dashboard(), \
        "summary panel must use 'Empfohlene Aktion' (not 'Suggested action')"


def test_dashboard_summary_panel_no_suggested_action() -> None:
    assert "Suggested action" not in _dashboard(), \
        "summary panel must not contain English 'Suggested action'"


# ---------------------------------------------------------------------------
# 3. No visible "vapi" badge in request card list
# ---------------------------------------------------------------------------


def test_dashboard_no_visible_vapi_badge() -> None:
    content = _dashboard()
    assert ">vapi<" not in content, \
        "dashboard must not show a visible 'vapi' badge in request cards"


def test_dashboard_no_raw_vapi_badge_span() -> None:
    content = _dashboard()
    assert "badge('vapi')}>vapi<" not in content and "}}>vapi</span>" not in content, \
        "dashboard must not render a raw visible 'vapi' badge"


# ---------------------------------------------------------------------------
# 4. Technical terms not visible in clinic-facing context
# (strings may appear in sr-only spans or code comments — tested via context)
# ---------------------------------------------------------------------------


def test_dashboard_no_english_ai_intake_blurb() -> None:
    content = _dashboard()
    assert "AI intake output is administrative" not in content, \
        "dashboard must not show English 'AI intake output' safety blurb to clinic users"


def test_dashboard_no_english_clinical_decision_text() -> None:
    assert "clinical decision" not in _dashboard(), \
        "dashboard must not use English 'clinical decision' in visible workspace text"


def test_dashboard_webhook_absent() -> None:
    assert "webhook" not in _dashboard(), \
        "dashboard must not contain 'webhook'"


def test_dashboard_no_fhir() -> None:
    assert "FHIR" not in _dashboard(), \
        "dashboard must not mention FHIR"


def test_dashboard_no_json_label() -> None:
    content = _dashboard()
    assert ">JSON<" not in content and ">json<" not in content, \
        "dashboard must not expose JSON as a visible label"


def test_dashboard_no_structuring() -> None:
    assert "structuring" not in _dashboard().lower(), \
        "dashboard must not mention 'structuring'"


def test_dashboard_no_proposal_visible() -> None:
    content = _dashboard()
    assert ">proposal<" not in content and ">proposal_id<" not in content, \
        "dashboard must not expose 'proposal' as a visible label"


def test_dashboard_no_tenant_visible() -> None:
    assert ">tenant<" not in _dashboard().lower(), \
        "dashboard must not expose 'tenant' as a visible label"


def test_dashboard_no_api_endpoint_url_visible() -> None:
    assert "capture-appointment-request" not in _dashboard(), \
        "dashboard must not expose the API endpoint URL"


# ---------------------------------------------------------------------------
# 5. Archived request handling
# ---------------------------------------------------------------------------


def test_dashboard_archived_status_mapped() -> None:
    content = _dashboard()
    assert "'archived':         return 'Archiviert'" in content or \
           "case 'archived'" in content, \
        "dashboard must map 'archived' status to 'Archiviert' in German status label function"


def test_dashboard_active_appts_filter_exists() -> None:
    content = _dashboard()
    assert "activeAppts" in content or "activeAppointments" in content, \
        "dashboard must filter active vs archived appointments"


def test_dashboard_archived_section_exists() -> None:
    content = _dashboard()
    assert "archivedAppts" in content or "Archivierte Anfragen" in content, \
        "dashboard must have a separate archived section"


def test_dashboard_is_new_request_fixed() -> None:
    content = _dashboard()
    assert "status !== 'confirmed'" not in content, \
        "isNewRequest must not use 'status !== confirmed' which wrongly marks archived as new"


# ---------------------------------------------------------------------------
# 6. Safety invariants — all prior module boundaries intact
# ---------------------------------------------------------------------------


def test_dashboard_no_diagnosis() -> None:
    assert "diagnosis" not in _dashboard().lower(), \
        "dashboard must not contain 'diagnosis'"


def test_dashboard_no_medical_advice() -> None:
    assert "medical advice" not in _dashboard().lower(), \
        "dashboard must not contain 'medical advice'"


def test_dashboard_no_triage() -> None:
    assert "triage" not in _dashboard().lower(), \
        "dashboard must not contain 'triage'"


def test_dashboard_no_auto_appointment_confirmation() -> None:
    content = _dashboard()
    assert "Termin bestätigt" not in content and "appointment confirmed" not in content.lower(), \
        "dashboard must not promise automatic appointment confirmation"


def test_dashboard_production_phi_no_go() -> None:
    content = _dashboard()
    assert "Production PHI" in content or "production phi" in content.lower(), \
        "dashboard must still mention Production PHI boundary"


def test_dashboard_no_real_patient_data() -> None:
    content = _dashboard()
    assert "no real patient data" in content.lower(), \
        "dashboard must include 'no real patient data' safety copy"


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


def test_dashboard_no_database_url() -> None:
    assert "DATABASE_URL" not in _dashboard(), \
        "dashboard must not contain DATABASE_URL"


def test_dashboard_no_jwt_secret() -> None:
    content = _dashboard()
    assert "JWT_SECRET" not in content and "jwt_secret" not in content, \
        "dashboard must not contain JWT_SECRET"


# ---------------------------------------------------------------------------
# 7. Existing module markers still present (regression guard)
# ---------------------------------------------------------------------------


def test_dashboard_still_has_demo_strip() -> None:
    assert 'data-demo-strip="sales-mvp"' in _dashboard(), \
        "Module 158 demo strip must still be present"


def test_dashboard_still_has_live_demo_hint() -> None:
    assert "data-live-demo-hint" in _dashboard(), \
        "Module 160 live demo hint must still be present"


def test_dashboard_still_has_demo_guide() -> None:
    assert 'data-demo-guide="3-steps"' in _dashboard(), \
        "Module 162 Demo in 3 Schritten card must still be present"


def test_dashboard_still_has_ki_vorschau() -> None:
    assert "KI-Vorschau" in _dashboard(), \
        "Module 159 KI-Vorschau must still be present"


def test_dashboard_still_has_praxisprofil() -> None:
    assert "Praxisprofil" in _dashboard(), \
        "Module 159 Praxisprofil must still be present"


def test_dashboard_still_has_anfragen_empty_german() -> None:
    assert "Noch keine Anfragen" in _dashboard(), \
        "Module 162 German empty state must still be present"


def test_dashboard_noch_keine_patienten_present() -> None:
    assert "Noch keine Patienten" in _dashboard(), \
        "Patienten empty state must still be present"
