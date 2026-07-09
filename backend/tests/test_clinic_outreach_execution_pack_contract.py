"""
Static contract tests for Sprint 21 / Module 163 — Clinic Outreach Execution Pack.

Verifies file content only. No database. No network. No secrets.
No real patient data. No PHI. Production PHI remains NO-GO.

Tests confirm that:
- All outreach scripts exist in the execution pack
- All scripts mention missed calls / verpasste Anrufe
- All scripts mention 30-day pilot
- All scripts contain a pilot or demo CTA
- No compliance certification claims in any script
- No technical language in any script
- No diagnosis or medical advice claims
- No production readiness claims
- No real patient data
- No real names (generic placeholders only)
"""

from __future__ import annotations

import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))
SALES = os.path.join(_REPO_ROOT, "docs", "sales")


def _outreach() -> str:
    with open(
        os.path.join(SALES, "CLINIC_OUTREACH_EXECUTION_PACK.md"), encoding="utf-8"
    ) as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. All scripts present in the execution pack
# ---------------------------------------------------------------------------


def test_cold_email_script_exists() -> None:
    assert "Cold Email Script" in _outreach(), \
        "execution pack must contain a Cold Email Script section"


def test_whatsapp_script_exists() -> None:
    content = _outreach()
    assert "WhatsApp" in content or "SMS" in content, \
        "execution pack must contain a WhatsApp / SMS script section"


def test_linkedin_script_exists() -> None:
    assert "LinkedIn" in _outreach(), \
        "execution pack must contain a LinkedIn outreach script section"


def test_walk_in_script_exists() -> None:
    content = _outreach()
    assert "Walk-In" in content or "walk-in" in content or "Walk-in" in content, \
        "execution pack must contain a walk-in cold approach script"


def test_followup_sequence_exists() -> None:
    content = _outreach()
    assert "Follow-Up Sequence" in content or "Folge" in content or "Day 1" in content, \
        "execution pack must contain a follow-up sequence section"


def test_objection_quick_replies_exist() -> None:
    content = _outreach()
    assert "Kein Interesse" in content or "Objection" in content, \
        "execution pack must contain objection-specific quick replies"


# ---------------------------------------------------------------------------
# 2. All scripts mention missed calls / verpasste Anrufe
# ---------------------------------------------------------------------------


def test_scripts_mention_missed_calls_german() -> None:
    content = _outreach().lower()
    assert "verpasste" in content or "verpassten" in content, \
        "execution pack must mention 'verpasste Anrufe' (missed calls) in German"


def test_cold_email_mentions_missed_calls() -> None:
    content = _outreach()
    cold_email_section = content.split("## 2.")[0] if "## 2." in content else content
    assert "verpasste" in cold_email_section.lower() or "verloren" in cold_email_section.lower(), \
        "cold email script must mention missed calls"


def test_walkin_mentions_missed_calls() -> None:
    content = _outreach()
    assert "verpasst" in content.lower() or "verloren" in content.lower(), \
        "walk-in script must reference missed calls"


# ---------------------------------------------------------------------------
# 3. All scripts contain a pilot or demo CTA
# ---------------------------------------------------------------------------


def test_cold_email_has_demo_cta() -> None:
    content = _outreach()
    assert "Demo-Termin" in content or "Demo" in content, \
        "cold email must include a demo CTA"


def test_cold_email_has_30_minuten_cta() -> None:
    content = _outreach()
    assert "30 Minuten" in content or "30-Minuten" in content, \
        "cold email must reference 30-minute demo"


def test_whatsapp_has_demo_cta() -> None:
    content = _outreach()
    assert "Demo" in content, \
        "WhatsApp script must include a demo CTA"


def test_followup_day7_has_pilot_offer() -> None:
    content = _outreach()
    assert "30-Tage" in content or "30 Tage" in content or "Pilotangebot" in content, \
        "Day 7 follow-up must mention the 30-day pilot offer"


# ---------------------------------------------------------------------------
# 4. No compliance certification claims
# ---------------------------------------------------------------------------


def test_no_dsgvo_certified_claim() -> None:
    content = _outreach().lower()
    assert "dsgvo-zertifiziert" not in content, \
        "execution pack must not claim DSGVO certification"


def test_no_fully_compliant_claim() -> None:
    content = _outreach().lower()
    assert "vollständig konform" not in content, \
        "execution pack must not claim full compliance"


def test_no_certified_claim() -> None:
    content = _outreach().lower()
    assert "zertifiziert" not in content, \
        "execution pack must not use 'zertifiziert' (certified) in outreach copy"


# ---------------------------------------------------------------------------
# 5. No technical language
# ---------------------------------------------------------------------------


def test_no_api_in_outreach() -> None:
    content = _outreach()
    assert " API " not in content and ">API<" not in content and "\nAPI\n" not in content, \
        "execution pack must not mention 'API' in clinic-facing copy"


def test_no_webhook_in_outreach() -> None:
    assert "webhook" not in _outreach().lower(), \
        "execution pack must not mention 'webhook'"


def test_no_uuid_in_outreach() -> None:
    content = _outreach()
    import re
    uuid_pattern = re.compile(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.IGNORECASE
    )
    assert not uuid_pattern.search(content), \
        "execution pack must not contain UUIDs"


def test_no_fhir_in_outreach() -> None:
    assert "FHIR" not in _outreach(), \
        "execution pack must not mention 'FHIR'"


def test_no_vapi_in_clinic_facing_copy() -> None:
    content = _outreach()
    assert "Vapi" not in content and "vapi" not in content, \
        "execution pack must not mention 'Vapi' in clinic-facing copy"


# ---------------------------------------------------------------------------
# 6. No diagnosis or medical advice
# ---------------------------------------------------------------------------


def test_no_diagnosis_claim() -> None:
    assert "diagnosis" not in _outreach().lower(), \
        "execution pack must not contain 'diagnosis'"


def test_no_medical_advice_claim() -> None:
    assert "medical advice" not in _outreach().lower(), \
        "execution pack must not contain 'medical advice'"


def test_no_triage_claim() -> None:
    assert "triage" not in _outreach().lower(), \
        "execution pack must not contain 'triage'"


def test_no_treatment_recommendation() -> None:
    assert "treatment recommendation" not in _outreach().lower(), \
        "execution pack must not contain 'treatment recommendation'"


# ---------------------------------------------------------------------------
# 7. No production readiness claims
# ---------------------------------------------------------------------------


def test_no_production_ready_claim() -> None:
    assert "production ready" not in _outreach().lower(), \
        "execution pack must not claim production readiness"


def test_no_auto_appointment_confirmation() -> None:
    content = _outreach().lower()
    assert "termin bestätigt" not in content and "appointment confirmed" not in content, \
        "execution pack must not promise automatic appointment confirmation"


# ---------------------------------------------------------------------------
# 8. No real patient data or real names
# ---------------------------------------------------------------------------


def test_no_real_patient_data() -> None:
    content = _outreach().lower()
    assert "patient data" not in content or "no real patient data" in content, \
        "execution pack must not expose real patient data"


def test_uses_placeholder_not_real_name() -> None:
    content = _outreach()
    assert "[Name]" in content or "Placeholder" in content or "Ali Abdel Tawab" in content, \
        "walk-in script must use generic placeholders for names"


def test_safety_boundaries_section_exists() -> None:
    content = _outreach()
    assert "Safety Boundaries" in content or "Sicherheit" in content, \
        "execution pack must include a safety boundaries section"


# ---------------------------------------------------------------------------
# 9. Walk-in script has complete structure
# ---------------------------------------------------------------------------


def test_walkin_has_receptionist_step() -> None:
    content = _outreach()
    assert "Rezeption" in content or "Reception" in content or "Rezeptionist" in content, \
        "walk-in script must include what to say at the reception desk"


def test_walkin_has_leave_behind_reference() -> None:
    content = _outreach()
    assert "ONE_PAGE_CLINIC_HANDOUT" in content or "Handout" in content or "Übersicht" in content, \
        "walk-in script must reference the leave-behind handout"


def test_walkin_has_followup_step() -> None:
    content = _outreach()
    assert "24 Stunden" in content or "Follow-Up After Walk-In" in content or "Nachfrage" in content, \
        "walk-in script must include a follow-up step"


# ---------------------------------------------------------------------------
# 10. Objection quick replies cover required 5 objections
# ---------------------------------------------------------------------------


def test_objection_kein_interesse() -> None:
    assert "Kein Interesse" in _outreach(), \
        "execution pack must handle 'Kein Interesse' objection"


def test_objection_zu_teuer() -> None:
    assert "Zu teuer" in _outreach() or "zu teuer" in _outreach().lower(), \
        "execution pack must handle 'Zu teuer' objection"


def test_objection_already_have_solution() -> None:
    content = _outreach()
    assert "bereits eine Lösung" in content or "haben bereits" in content, \
        "execution pack must handle 'Wir haben bereits eine Lösung' objection"


def test_objection_keine_zeit() -> None:
    assert "Keine Zeit" in _outreach() or "keine Zeit" in _outreach(), \
        "execution pack must handle 'Keine Zeit' objection"


def test_objection_schicken_sie_email() -> None:
    content = _outreach()
    assert "E-Mail" in content and ("Schicken" in content or "schicken" in content), \
        "execution pack must handle 'Schicken Sie uns eine E-Mail' objection"


# ---------------------------------------------------------------------------
# 11. Follow-up sequence has 3 touches (Day 1, Day 3, Day 7)
# ---------------------------------------------------------------------------


def test_followup_has_day1() -> None:
    assert "Day 1" in _outreach(), \
        "follow-up sequence must include Day 1"


def test_followup_has_day3() -> None:
    assert "Day 3" in _outreach(), \
        "follow-up sequence must include Day 3"


def test_followup_has_day7() -> None:
    assert "Day 7" in _outreach(), \
        "follow-up sequence must include Day 7"


# ---------------------------------------------------------------------------
# 12. Related sales docs still present (regression guard)
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
