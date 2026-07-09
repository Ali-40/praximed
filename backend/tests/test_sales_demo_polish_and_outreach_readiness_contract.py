"""
Static contract tests for Sprint 21 / Module 162 — Sales Demo Polish and Outreach Readiness.

Verifies file content only. No database. No network. No secrets.
No real patient data. No PHI. Production PHI remains NO-GO.

Combined test coverage:
- /dashboard polished for clinic-facing demo
- Sales outreach execution pack complete and ready
- One-liners, tomorrow plan, tracker template present
- No technical language in any clinic-facing copy
- No compliance overclaims
- No clinical or medical claims
- No secrets or real data
"""

from __future__ import annotations

import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))
FRONTEND = os.path.join(_REPO_ROOT, "frontend")
SALES = os.path.join(_REPO_ROOT, "docs", "sales")


def _dashboard() -> str:
    with open(os.path.join(FRONTEND, "app", "dashboard", "page.tsx"), encoding="utf-8") as f:
        return f.read()


def _outreach() -> str:
    with open(os.path.join(SALES, "CLINIC_OUTREACH_EXECUTION_PACK.md"), encoding="utf-8") as f:
        return f.read()


def _one_liners() -> str:
    with open(os.path.join(SALES, "SALES_ONE_LINERS.md"), encoding="utf-8") as f:
        return f.read()


def _tomorrow_plan() -> str:
    with open(os.path.join(SALES, "TOMORROW_FIRST_SALES_DAY_PLAN.md"), encoding="utf-8") as f:
        return f.read()


def _tracker_csv() -> str:
    with open(os.path.join(SALES, "clinic_outreach_tracker_template.csv"), encoding="utf-8") as f:
        return f.read()


def _all_sales_docs() -> list[str]:
    return [_outreach(), _one_liners(), _tomorrow_plan()]


# ---------------------------------------------------------------------------
# 1. Dashboard — key German copy present
# ---------------------------------------------------------------------------


def test_dashboard_has_praximed_intro_sentence() -> None:
    assert "PraxisMed nimmt Terminanfragen auf" in _dashboard(), \
        "dashboard must include 'PraxisMed nimmt Terminanfragen auf'"


def test_dashboard_has_rueckrufe_fuer_praxisteam() -> None:
    assert "Rückrufe für Ihr Praxisteam" in _dashboard(), \
        "dashboard must include 'Rückrufe für Ihr Praxisteam'"


def test_dashboard_has_demo_in_3_schritten() -> None:
    assert "Demo in 3 Schritten" in _dashboard(), \
        "dashboard must include 'Demo in 3 Schritten' helper card"


def test_dashboard_has_demo_anruf_erstellen() -> None:
    assert "Demo-Anruf erstellen" in _dashboard(), \
        "dashboard must include 'Demo-Anruf erstellen'"


def test_dashboard_has_rueckruf_anfrage_pruefen() -> None:
    assert "Rückruf-Anfrage prüfen" in _dashboard(), \
        "dashboard must include 'Rückruf-Anfrage prüfen'"


def test_dashboard_has_als_kontaktiert_markieren() -> None:
    assert "Als kontaktiert markieren" in _dashboard(), \
        "dashboard must include 'Als kontaktiert markieren'"


def test_dashboard_has_noch_keine_anfragen() -> None:
    assert "Noch keine Anfragen" in _dashboard(), \
        "dashboard must include 'Noch keine Anfragen' empty state"


def test_dashboard_has_noch_keine_patienten() -> None:
    assert "Noch keine Patienten" in _dashboard(), \
        "dashboard must include 'Noch keine Patienten' empty state"


def test_dashboard_has_nicht_angegeben() -> None:
    assert "Nicht angegeben" in _dashboard(), \
        "dashboard must use 'Nicht angegeben' for missing values"


def test_dashboard_has_heute() -> None:
    assert "Heute" in _dashboard(), \
        "dashboard must include 'Heute' summary section"


def test_dashboard_has_anfragen_tab() -> None:
    assert "Anfragen" in _dashboard(), \
        "dashboard must include 'Anfragen' tab"


def test_dashboard_has_patienten_tab() -> None:
    assert "Patienten" in _dashboard(), \
        "dashboard must include 'Patienten' tab"


def test_dashboard_has_einstellungen_tab() -> None:
    assert "Einstellungen" in _dashboard(), \
        "dashboard must include 'Einstellungen' tab"


def test_dashboard_has_anfrage_number() -> None:
    assert "Anfrage #" in _dashboard(), \
        "dashboard must show 'Anfrage #N' labels"


def test_dashboard_has_rueckruf_noetig() -> None:
    assert "Rückruf nötig" in _dashboard(), \
        "dashboard must show 'Rückruf nötig' status"


def test_dashboard_has_erledigt() -> None:
    assert "Erledigt" in _dashboard(), \
        "dashboard must show 'Erledigt' status"


# ---------------------------------------------------------------------------
# 2. Dashboard — no technical clinic-facing content
# ---------------------------------------------------------------------------


def test_dashboard_no_fhir() -> None:
    assert "FHIR" not in _dashboard(), \
        "dashboard must not expose 'FHIR'"


def test_dashboard_no_webhook() -> None:
    assert "webhook" not in _dashboard(), \
        "dashboard must not expose 'webhook'"


def test_dashboard_no_json_label() -> None:
    content = _dashboard()
    assert ">JSON<" not in content and ">json<" not in content, \
        "dashboard must not expose 'JSON' as visible label"


def test_dashboard_no_phi_label() -> None:
    content = _dashboard()
    assert ">PHI<" not in content and ">phi<" not in content, \
        "dashboard must not expose 'PHI' as visible label"


def test_dashboard_no_structuring() -> None:
    assert "structuring" not in _dashboard().lower(), \
        "dashboard must not mention 'structuring'"


def test_dashboard_no_proposal_label() -> None:
    content = _dashboard()
    assert ">proposal<" not in content and ">proposal_id<" not in content, \
        "dashboard must not expose 'proposal' or 'proposal_id'"


def test_dashboard_no_tenant_label() -> None:
    assert ">tenant<" not in _dashboard().lower(), \
        "dashboard must not expose 'tenant' as a visible label"


def test_dashboard_no_api_endpoint_url() -> None:
    assert "capture-appointment-request" not in _dashboard(), \
        "dashboard must not expose the internal endpoint URL"


# ---------------------------------------------------------------------------
# 3. Sales docs — existence
# ---------------------------------------------------------------------------


def test_outreach_pack_exists() -> None:
    path = os.path.join(SALES, "CLINIC_OUTREACH_EXECUTION_PACK.md")
    assert os.path.isfile(path), \
        "CLINIC_OUTREACH_EXECUTION_PACK.md must exist"


def test_sales_one_liners_exists() -> None:
    path = os.path.join(SALES, "SALES_ONE_LINERS.md")
    assert os.path.isfile(path), \
        "SALES_ONE_LINERS.md must exist"


def test_tomorrow_plan_exists() -> None:
    path = os.path.join(SALES, "TOMORROW_FIRST_SALES_DAY_PLAN.md")
    assert os.path.isfile(path), \
        "TOMORROW_FIRST_SALES_DAY_PLAN.md must exist"


def test_tracker_csv_exists() -> None:
    path = os.path.join(SALES, "clinic_outreach_tracker_template.csv")
    assert os.path.isfile(path), \
        "clinic_outreach_tracker_template.csv must exist"


# ---------------------------------------------------------------------------
# 4. Outreach pack — key content
# ---------------------------------------------------------------------------


def test_outreach_mentions_wien() -> None:
    content = _outreach().lower()
    assert "wien" in content or "vienna" in content, \
        "outreach pack must mention Wien / Vienna"


def test_outreach_mentions_wahlarzt() -> None:
    content = _outreach().lower()
    assert "wahlarzt" in content or "privatprax" in content, \
        "outreach pack must mention Wahlärzte or Privatpraxen"


def test_outreach_mentions_verpasste_anrufe() -> None:
    content = _outreach().lower()
    assert "verpasste" in content or "verloren" in content, \
        "outreach pack must mention missed calls / verpasste Anrufe"


def test_outreach_mentions_rueckruf() -> None:
    assert "Rückruf" in _outreach() or "rückruf" in _outreach().lower(), \
        "outreach pack must mention Rückruf"


def test_outreach_mentions_praxisteam_in_kontrolle() -> None:
    content = _outreach().lower()
    assert "praxisteam" in content and "kontrolle" in content, \
        "outreach pack must state that Praxisteam bleibt in Kontrolle"


def test_outreach_mentions_30_tage_pilot() -> None:
    content = _outreach().lower()
    assert "30-tage" in content or "30 tage" in content or "pilot" in content, \
        "outreach pack must mention 30-Tage Pilot"


def test_outreach_mentions_pricing_setup() -> None:
    assert "€390" in _outreach() or "390" in _outreach(), \
        "outreach pack must mention the €390 setup price"


def test_outreach_mentions_monthly_pricing() -> None:
    content = _outreach()
    assert "€290" in content or "290" in content, \
        "outreach pack must mention the monthly price range"


def test_outreach_has_email_script() -> None:
    content = _outreach().lower()
    assert "email" in content or "e-mail" in content, \
        "outreach pack must include an email script"


def test_outreach_has_whatsapp_script() -> None:
    assert "WhatsApp" in _outreach() or "whatsapp" in _outreach().lower(), \
        "outreach pack must include a WhatsApp/SMS script"


def test_outreach_has_phone_script() -> None:
    content = _outreach().lower()
    assert "phone" in content or "telefon" in content or "anruf" in content, \
        "outreach pack must include a phone call script"


def test_outreach_has_walkin_script() -> None:
    content = _outreach().lower()
    assert "walk-in" in content or "rezeption" in content, \
        "outreach pack must include a walk-in script"


def test_outreach_has_followup_sequence() -> None:
    content = _outreach()
    assert "Day 1" in content and "Day 3" in content and "Day 7" in content, \
        "outreach pack must include a 3-touch follow-up sequence"


def test_outreach_has_followup_after_demo() -> None:
    content = _outreach().lower()
    assert "after demo" in content or "nach der demo" in content or "demo" in content, \
        "outreach pack must include a follow-up after demo"


def test_outreach_has_calendar_objection_reply() -> None:
    content = _outreach().lower()
    assert "kalender" in content or "calendar" in content, \
        "outreach pack must include a calendar objection reply"


def test_outreach_calendar_positioned_as_next_feature() -> None:
    content = _outreach()
    assert "nächste" in content.lower() and "Kalender" in content, \
        "outreach pack must position calendar as next feature, not current"


def test_outreach_has_dsgvo_objection_without_overclaim() -> None:
    content = _outreach().lower()
    assert "datenschutz" in content, \
        "outreach pack must address the data protection question"


def test_outreach_has_ai_no_diagnosis_objection_reply() -> None:
    content = _outreach().lower()
    assert "empfehlung" in content or "diagnos" in content or "einschätzung" in content, \
        "outreach pack must address AI clinical claims question"


def test_outreach_has_auto_confirmation_objection_reply() -> None:
    content = _outreach().lower()
    assert "automatisch" in content or "bestätigt" in content, \
        "outreach pack must address automatic confirmation question"


# ---------------------------------------------------------------------------
# 5. One-liners — key content
# ---------------------------------------------------------------------------


def test_one_liners_has_main_line() -> None:
    content = _one_liners()
    assert "Terminanfragen" in content and "Rückrufe" in content, \
        "one-liners must include the main positioning line"


def test_one_liners_has_trust_line() -> None:
    content = _one_liners().lower()
    assert "kontrolle" in content, \
        "one-liners must include the trust/control line"


def test_one_liners_has_calendar_future_line() -> None:
    content = _one_liners().lower()
    assert "kalender" in content or "calendar" in content, \
        "one-liners must include the calendar future line"


def test_one_liners_has_pilot_line() -> None:
    content = _one_liners().lower()
    assert "pilot" in content and "30" in content, \
        "one-liners must include the 30-day pilot line"


def test_one_liners_has_missed_calls_line() -> None:
    content = _one_liners().lower()
    assert "verpasste" in content or "verloren" in content, \
        "one-liners must include a missed calls line"


def test_one_liners_has_5_minute_demo_line() -> None:
    content = _one_liners().lower()
    assert "5 minuten" in content or "5-minuten" in content or "fünf" in content, \
        "one-liners must include a 5-minute demo line"


# ---------------------------------------------------------------------------
# 6. Tomorrow plan — key structure
# ---------------------------------------------------------------------------


def test_tomorrow_plan_has_demo_reset_step() -> None:
    content = _tomorrow_plan()
    assert "Demo zurücksetzen" in content, \
        "tomorrow plan must include the Demo zurücksetzen step"


def test_tomorrow_plan_has_email_block() -> None:
    content = _tomorrow_plan().lower()
    assert "email" in content or "e-mail" in content, \
        "tomorrow plan must include an email outreach block"


def test_tomorrow_plan_has_phone_block() -> None:
    content = _tomorrow_plan().lower()
    assert "phone" in content or "telefon" in content or "anruf" in content or "call" in content, \
        "tomorrow plan must include a phone call block"


def test_tomorrow_plan_has_walkin_block() -> None:
    content = _tomorrow_plan().lower()
    assert "walk-in" in content or "walk in" in content or "besuche" in content, \
        "tomorrow plan must include a walk-in block"


def test_tomorrow_plan_has_success_metrics() -> None:
    content = _tomorrow_plan()
    assert "20" in content and "demo" in content.lower(), \
        "tomorrow plan must include end-of-day success metrics"


def test_tomorrow_plan_has_safety_reminders() -> None:
    content = _tomorrow_plan().lower()
    assert "sicherheit" in content or "safety" in content or "patient" in content, \
        "tomorrow plan must include safety reminders"


# ---------------------------------------------------------------------------
# 7. Tracker CSV — structure
# ---------------------------------------------------------------------------


def test_tracker_csv_has_required_columns() -> None:
    content = _tracker_csv()
    required = ["clinic_name", "specialty", "district", "email", "phone",
                "status", "follow_up_date", "interest_level", "demo_booked"]
    for col in required:
        assert col in content, f"tracker CSV must have column '{col}'"


def test_tracker_csv_has_example_rows() -> None:
    lines = [ln for ln in _tracker_csv().splitlines() if ln.strip()]
    assert len(lines) >= 6, \
        "tracker CSV must have header + at least 5 example rows"


def test_tracker_csv_no_real_clinic_names() -> None:
    content = _tracker_csv()
    assert "Demo " in content, \
        "tracker CSV example rows must use 'Demo' prefix (fake names)"


def test_tracker_csv_no_real_phone_numbers() -> None:
    content = _tracker_csv()
    real_phone_pattern = re.compile(r"\+43[0-9]{6,}")
    assert not real_phone_pattern.search(content), \
        "tracker CSV must not contain real Austrian phone numbers"


# ---------------------------------------------------------------------------
# 8. Forbidden content — sales docs
# ---------------------------------------------------------------------------


def test_no_database_url_in_sales_docs() -> None:
    for doc in _all_sales_docs():
        assert "DATABASE_URL" not in doc, \
            "sales docs must not contain DATABASE_URL"


def test_no_jwt_secret_in_sales_docs() -> None:
    for doc in _all_sales_docs():
        assert "JWT_SECRET" not in doc and "jwt_secret" not in doc, \
            "sales docs must not contain JWT_SECRET"


def test_no_dsgvo_certification_claim_in_sales_docs() -> None:
    for doc in _all_sales_docs():
        assert "dsgvo-zertifiziert" not in doc.lower(), \
            "sales docs must not claim DSGVO certification"


def test_no_fully_compliant_claim_in_sales_docs() -> None:
    for doc in _all_sales_docs():
        assert "vollständig konform" not in doc.lower(), \
            "sales docs must not claim full compliance"


def test_no_production_ready_claim_in_sales_docs() -> None:
    for doc in _all_sales_docs():
        assert "production ready" not in doc.lower(), \
            "sales docs must not claim production readiness"


def test_no_ai_diagnosis_claim_in_sales_docs() -> None:
    for doc in _all_sales_docs():
        assert "ai diagnosis" not in doc.lower() and "ki-diagnose" not in doc.lower(), \
            "sales docs must not claim AI gives diagnoses"


def test_no_auto_appointment_confirmation_in_sales_docs() -> None:
    for doc in _all_sales_docs():
        assert "termin bestätigt" not in doc.lower() and \
               "appointment confirmed" not in doc.lower(), \
            "sales docs must not promise automatic appointment confirmation"


def test_no_real_patient_data_in_sales_docs() -> None:
    for doc in _all_sales_docs():
        content_lower = doc.lower()
        assert "no real patient data" in content_lower or \
               "echten patientendaten" not in content_lower or \
               "keine echten patientendaten" in content_lower, \
            "sales docs must affirm no real patient data"


def test_no_api_key_pattern_in_sales_docs() -> None:
    api_key_pattern = re.compile(r"(sk-[A-Za-z0-9]{20,}|va-[A-Za-z0-9]{20,})")
    for doc in _all_sales_docs():
        assert not api_key_pattern.search(doc), \
            "sales docs must not contain API-key-looking values"


def test_no_uuid_in_tracker_csv() -> None:
    uuid_pattern = re.compile(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.IGNORECASE
    )
    assert not uuid_pattern.search(_tracker_csv()), \
        "tracker CSV must not contain UUIDs"


# ---------------------------------------------------------------------------
# 9. Existing sales docs still present (regression guard)
# ---------------------------------------------------------------------------


def test_five_minute_demo_script_still_exists() -> None:
    path = os.path.join(SALES, "FIVE_MINUTE_CLINIC_DEMO_SCRIPT.md")
    assert os.path.isfile(path), \
        "FIVE_MINUTE_CLINIC_DEMO_SCRIPT.md must still exist"


def test_thirty_day_pilot_offer_still_exists() -> None:
    path = os.path.join(SALES, "THIRTY_DAY_PILOT_OFFER.md")
    assert os.path.isfile(path), \
        "THIRTY_DAY_PILOT_OFFER.md must still exist"


def test_objection_handling_still_exists() -> None:
    path = os.path.join(SALES, "OBJECTION_HANDLING.md")
    assert os.path.isfile(path), \
        "OBJECTION_HANDLING.md must still exist"


def test_one_page_handout_still_exists() -> None:
    path = os.path.join(SALES, "ONE_PAGE_CLINIC_HANDOUT.md")
    assert os.path.isfile(path), \
        "ONE_PAGE_CLINIC_HANDOUT.md must still exist"


def test_demo_day_checklist_still_exists() -> None:
    path = os.path.join(SALES, "DEMO_DAY_CHECKLIST.md")
    assert os.path.isfile(path), \
        "DEMO_DAY_CHECKLIST.md must still exist"


# ---------------------------------------------------------------------------
# 10. Dashboard — safety invariants still intact
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


def test_dashboard_no_real_patient_data_claim() -> None:
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


def test_dashboard_no_auto_appointment_confirmation() -> None:
    content = _dashboard()
    assert "Termin bestätigt" not in content and "appointment confirmed" not in content.lower(), \
        "dashboard must not promise appointment auto-confirmation"
