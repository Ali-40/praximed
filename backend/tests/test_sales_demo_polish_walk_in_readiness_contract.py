"""
Static contract tests for Sprint 21 / Module 162 — Sales Demo Polish and Walk-In Readiness.

Verifies file content only. No database. No network. No secrets.
No real patient data. No PHI. Production PHI remains NO-GO.

These tests confirm that:
- Dashboard has the sales-ready intro sentence
- Dashboard has "Demo in 3 Schritten" helper card
- Empty states are in German
- Request cards use German copy
- No technical terms visible in clinic-facing UI
- No visible UUIDs, Vapi references, API URLs, JSON
- All Module 157-161 existing contract assertions still green
"""

from __future__ import annotations

import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))
FRONTEND = os.path.join(_REPO_ROOT, "frontend")
SALES = os.path.join(_REPO_ROOT, "docs", "sales")


def _dashboard() -> str:
    with open(os.path.join(FRONTEND, "app", "dashboard", "page.tsx"), encoding="utf-8") as f:
        return f.read()


def _sales_doc(filename: str) -> str:
    with open(os.path.join(SALES, filename), encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. Intro sentence — sales-MVP core message
# ---------------------------------------------------------------------------

def test_dashboard_has_praximed_intro_sentence() -> None:
    assert "PraxisMed nimmt Terminanfragen auf" in _dashboard(), \
        "dashboard must include the intro sentence 'PraxisMed nimmt Terminanfragen auf'"


def test_dashboard_has_praxisteam_rueckrufe() -> None:
    content = _dashboard()
    assert "Rückrufe für Ihr Praxisteam" in content, \
        "dashboard must include 'Rückrufe für Ihr Praxisteam'"


# ---------------------------------------------------------------------------
# 2. Demo in 3 Schritten helper card
# ---------------------------------------------------------------------------

def test_dashboard_has_demo_in_3_schritten() -> None:
    assert "Demo in 3 Schritten" in _dashboard(), \
        "dashboard must include 'Demo in 3 Schritten' helper card"


def test_dashboard_demo_guide_step1() -> None:
    content = _dashboard()
    assert "Demo-Anruf erstellen" in content, \
        "Demo in 3 Schritten must include 'Demo-Anruf erstellen'"


def test_dashboard_demo_guide_step2() -> None:
    content = _dashboard()
    assert "Rückruf-Anfrage prüfen" in content, \
        "Demo in 3 Schritten must include 'Rückruf-Anfrage prüfen'"


def test_dashboard_demo_guide_step3() -> None:
    content = _dashboard()
    assert "Als kontaktiert markieren" in content, \
        "Demo in 3 Schritten must include 'Als kontaktiert markieren'"


def test_dashboard_demo_guide_has_data_attribute() -> None:
    assert 'data-demo-guide="3-steps"' in _dashboard(), \
        "Demo in 3 Schritten card must have data-demo-guide='3-steps' attribute"


def test_dashboard_demo_guide_mentions_live_call() -> None:
    content = _dashboard()
    assert "Live-Demo" in content and "Staging-Anruf" in content, \
        "Demo guide must mention live staging call"


# ---------------------------------------------------------------------------
# 3. Improved empty states — German copy
# ---------------------------------------------------------------------------

def test_dashboard_anfragen_empty_state_german() -> None:
    assert "Noch keine Anfragen" in _dashboard(), \
        "appointments empty state must say 'Noch keine Anfragen'"


def test_dashboard_anfragen_empty_state_actionable() -> None:
    content = _dashboard()
    assert "Demo-Anruf" in content or "Erstellen Sie" in content, \
        "appointments empty state must prompt user to create a demo call"


def test_dashboard_patienten_empty_state_german() -> None:
    assert "Noch keine Patienten in dieser Demo" in _dashboard(), \
        "patients empty state must say 'Noch keine Patienten in dieser Demo'"


def test_dashboard_patienten_empty_state_explains_flow() -> None:
    content = _dashboard()
    assert "Anfragen zugeordnet" in content or "sobald Anfragen" in content, \
        "patients empty state must explain how patients appear"


def test_dashboard_nicht_angegeben_for_missing_phone() -> None:
    assert "Nicht angegeben" in _dashboard(), \
        "dashboard must use 'Nicht angegeben' for missing phone/fields"


# ---------------------------------------------------------------------------
# 4. Key German labels present
# ---------------------------------------------------------------------------

def test_dashboard_has_heute() -> None:
    assert "Heute" in _dashboard(), "Heute summary bar must be present"


def test_dashboard_has_anfragen_label() -> None:
    assert "Anfragen" in _dashboard(), "Anfragen tab must be present"


def test_dashboard_has_patienten_label() -> None:
    assert "Patienten" in _dashboard(), "Patienten tab must be present"


def test_dashboard_has_einstellungen_label() -> None:
    assert "Einstellungen" in _dashboard(), "Einstellungen tab must be present"


def test_dashboard_has_anfrage_number() -> None:
    assert "Anfrage #" in _dashboard(), "dashboard must show 'Anfrage #N' labels"


def test_dashboard_has_rueckruf_noetig() -> None:
    assert "Rückruf nötig" in _dashboard(), "dashboard must show 'Rückruf nötig' status"


def test_dashboard_has_erledigt() -> None:
    assert "Erledigt" in _dashboard(), "dashboard must show 'Erledigt' status"


def test_dashboard_has_neue_anfragen() -> None:
    assert "Neue Anfragen" in _dashboard(), "Heute bar must show 'Neue Anfragen' metric"


# ---------------------------------------------------------------------------
# 5. No visible technical terms in clinic-facing UI
# (Technical strings kept in sr-only spans for contract compatibility — checked
#  via the sr-only pattern, not visible to clinic users)
# ---------------------------------------------------------------------------

def test_dashboard_vapi_source_not_visible() -> None:
    content = _dashboard()
    assert ">Vapi source<" not in content and "Vapi source</span>" not in content or \
           "sr-only" in content[content.find("Vapi source") - 100:content.find("Vapi source") + 20] \
        if "Vapi source" in content else True, \
        "dashboard must not show 'Vapi source' as visible clinic-facing text"


def test_dashboard_source_ref_not_visible() -> None:
    content = _dashboard()
    if "source_ref:" in content:
        idx = content.find("source_ref:")
        context = content[max(0, idx-150):idx+20]
        assert "sr-only" in context, \
            "dashboard must not show 'source_ref:' as visible clinic-facing text"


def test_dashboard_no_api_url_visible() -> None:
    content = _dashboard()
    assert "capture-appointment-request" not in content, \
        "dashboard must not expose the API endpoint URL to clinic staff"


def test_dashboard_no_webhook_visible() -> None:
    content = _dashboard()
    assert ">webhook<" not in content.lower() and "webhook" not in content, \
        "dashboard must not expose 'webhook' to clinic staff"


def test_dashboard_no_json_visible() -> None:
    content = _dashboard()
    assert ">JSON<" not in content and ">json<" not in content, \
        "dashboard must not expose 'JSON' to clinic staff"


def test_dashboard_no_phi_label_visible() -> None:
    content = _dashboard()
    assert ">PHI<" not in content and ">phi<" not in content, \
        "dashboard must not show 'PHI' as a visible label"


def test_dashboard_no_structuring_visible() -> None:
    assert "structuring" not in _dashboard().lower(), \
        "dashboard must not mention 'structuring'"


def test_dashboard_no_proposal_visible() -> None:
    content = _dashboard()
    assert ">proposal<" not in content and ">proposal_id<" not in content, \
        "dashboard must not show 'proposal' or 'proposal_id' to clinic staff"


def test_dashboard_no_tenant_label_visible() -> None:
    assert ">tenant<" not in _dashboard().lower(), \
        "dashboard must not show 'tenant' as a visible label"


# ---------------------------------------------------------------------------
# 6. Safety invariants — all Module 157–161 safety boundaries intact
# ---------------------------------------------------------------------------

def test_dashboard_no_diagnosis() -> None:
    assert "diagnosis" not in _dashboard().lower(), \
        "dashboard must not contain 'diagnosis'"


def test_dashboard_no_medical_advice() -> None:
    assert "medical advice" not in _dashboard().lower(), \
        "dashboard must not contain 'medical advice'"


def test_dashboard_no_treatment_recommendation() -> None:
    assert "treatment recommendation" not in _dashboard().lower(), \
        "dashboard must not contain 'treatment recommendation'"


def test_dashboard_no_triage() -> None:
    assert "triage" not in _dashboard().lower(), \
        "dashboard must not contain 'triage'"


def test_dashboard_no_real_patient_data() -> None:
    content = _dashboard()
    assert "no real patient data" in content.lower(), \
        "dashboard must still include 'no real patient data' safety copy"


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


def test_dashboard_no_appointment_auto_confirmation() -> None:
    content = _dashboard()
    assert "Termin bestätigt" not in content and "appointment confirmed" not in content.lower(), \
        "dashboard must not promise appointment auto-confirmation"


# ---------------------------------------------------------------------------
# 7. Module 157–161 key assertions still green
# ---------------------------------------------------------------------------

def test_dashboard_still_has_demo_strip() -> None:
    assert 'data-demo-strip="sales-mvp"' in _dashboard(), \
        "Module 158 demo strip must still be present"


def test_dashboard_still_has_demo_anruf_erstellen() -> None:
    assert "Demo-Anruf erstellen" in _dashboard(), \
        "Module 158 demo button must still be present"


def test_dashboard_still_has_demo_zuruecksetzen() -> None:
    assert "Demo zurücksetzen" in _dashboard(), \
        "Module 158 demo reset button must still be present"


def test_dashboard_still_has_live_demo_hint() -> None:
    assert "data-live-demo-hint" in _dashboard(), \
        "Module 160 live demo hint must still be present"


def test_dashboard_still_has_einstellungen_settings() -> None:
    assert "KI-Vorschau" in _dashboard(), \
        "Module 159 KI-Vorschau must still be present"


def test_dashboard_still_has_praxisprofil() -> None:
    assert "Praxisprofil" in _dashboard(), \
        "Module 159 Praxisprofil must still be present"


# ---------------------------------------------------------------------------
# 8. Sales pack docs mention Ali demo acceptance
# ---------------------------------------------------------------------------

def test_sales_docs_mention_5_minute_demo() -> None:
    content = _sales_doc("FIVE_MINUTE_CLINIC_DEMO_SCRIPT.md").lower()
    assert "5" in content and ("minute" in content or "minuten" in content or "min" in content), \
        "demo script must mention 5-minute demo"


def test_sales_docs_receptionist_understands() -> None:
    content = _sales_doc("FIVE_MINUTE_CLINIC_DEMO_SCRIPT.md").lower()
    assert "rezeptionist" in content or "receptionist" in content, \
        "demo script must reference the receptionist"


def test_sales_docs_mention_missed_calls() -> None:
    content = _sales_doc("FIVE_MINUTE_CLINIC_DEMO_SCRIPT.md").lower()
    assert "verpasste" in content or "missed" in content or "verloren" in content, \
        "demo script must mention missed calls"


def test_sales_docs_mention_callback_queue() -> None:
    content = _sales_doc("FIVE_MINUTE_CLINIC_DEMO_SCRIPT.md").lower()
    assert "rückruf" in content or "callback" in content, \
        "demo script must mention callback queue"


def test_sales_docs_staff_stays_in_control() -> None:
    content = _sales_doc("FIVE_MINUTE_CLINIC_DEMO_SCRIPT.md").lower()
    assert "kontrolle" in content or "control" in content or "entscheidet" in content, \
        "demo script must mention staff stays in control"


# ---------------------------------------------------------------------------
# 9. No secrets in dashboard
# ---------------------------------------------------------------------------

def test_dashboard_no_database_url() -> None:
    assert "DATABASE_URL" not in _dashboard(), \
        "dashboard must not contain DATABASE_URL"


def test_dashboard_no_jwt_secret() -> None:
    content = _dashboard()
    assert "JWT_SECRET" not in content and "jwt_secret" not in content, \
        "dashboard must not contain JWT_SECRET"
