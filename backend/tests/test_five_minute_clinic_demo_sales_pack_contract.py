"""
Static contract tests for Sprint 21 / Module 161 — Five-Minute Clinic Demo Script and Sales Pack.

Verifies file content only. No database. No network. No secrets.
No real patient data. No PHI. Production PHI remains NO-GO.

These tests confirm that:
- All five sales-pack docs exist
- Key sales messages are present (Vienna, receptionist, missed calls, callback, 30-day pilot)
- Pricing anchor is present (€390, €290–€490/month)
- Safety wording is present (no diagnosis, no medical advice, no auto-confirmation, 144 emergency)
- No compliance overclaims (no "DSGVO-zertifiziert", no "vollständig konform", no "production ready")
- No technical secrets or infrastructure details exposed
- No real patient data or PHI claims
"""

from __future__ import annotations

import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))
SALES = os.path.join(_REPO_ROOT, "docs", "sales")


def _read(filename: str) -> str:
    with open(os.path.join(SALES, filename), encoding="utf-8") as f:
        return f.read()


def _demo_script() -> str:
    return _read("FIVE_MINUTE_CLINIC_DEMO_SCRIPT.md")


def _pilot_offer() -> str:
    return _read("THIRTY_DAY_PILOT_OFFER.md")


def _handout() -> str:
    return _read("ONE_PAGE_CLINIC_HANDOUT.md")


def _objections() -> str:
    return _read("OBJECTION_HANDLING.md")


def _checklist() -> str:
    return _read("DEMO_DAY_CHECKLIST.md")


def _all_docs() -> str:
    return (
        _demo_script() + "\n" +
        _pilot_offer() + "\n" +
        _handout() + "\n" +
        _objections() + "\n" +
        _checklist()
    )


# ---------------------------------------------------------------------------
# 1. All five docs exist
# ---------------------------------------------------------------------------

def test_demo_script_exists() -> None:
    assert os.path.isfile(os.path.join(SALES, "FIVE_MINUTE_CLINIC_DEMO_SCRIPT.md")), \
        "docs/sales/FIVE_MINUTE_CLINIC_DEMO_SCRIPT.md must exist"


def test_pilot_offer_exists() -> None:
    assert os.path.isfile(os.path.join(SALES, "THIRTY_DAY_PILOT_OFFER.md")), \
        "docs/sales/THIRTY_DAY_PILOT_OFFER.md must exist"


def test_handout_exists() -> None:
    assert os.path.isfile(os.path.join(SALES, "ONE_PAGE_CLINIC_HANDOUT.md")), \
        "docs/sales/ONE_PAGE_CLINIC_HANDOUT.md must exist"


def test_objections_exists() -> None:
    assert os.path.isfile(os.path.join(SALES, "OBJECTION_HANDLING.md")), \
        "docs/sales/OBJECTION_HANDLING.md must exist"


def test_checklist_exists() -> None:
    assert os.path.isfile(os.path.join(SALES, "DEMO_DAY_CHECKLIST.md")), \
        "docs/sales/DEMO_DAY_CHECKLIST.md must exist"


# ---------------------------------------------------------------------------
# 2. Demo script — required content
# ---------------------------------------------------------------------------

def test_demo_script_mentions_module_161() -> None:
    assert "161" in _demo_script(), \
        "demo script must mention Module 161"


def test_demo_script_mentions_five_minutes() -> None:
    content = _demo_script().lower()
    assert "5-minute" in content or "five-minute" in content or "five minute" in content or \
           "5 minute" in content or "5-minuten" in content or "5 minuten" in content, \
        "demo script must reference the 5-minute timeframe"


def test_demo_script_mentions_vienna() -> None:
    content = _demo_script()
    assert "Wien" in content or "Vienna" in content or "Wiener" in content, \
        "demo script must mention Vienna / Wien"


def test_demo_script_mentions_receptionist() -> None:
    content = _demo_script().lower()
    assert "rezeptionist" in content or "receptionist" in content or "rezeption" in content, \
        "demo script must mention the receptionist"


def test_demo_script_mentions_missed_calls() -> None:
    content = _demo_script().lower()
    assert "verpasste" in content or "missed" in content or "verloren" in content, \
        "demo script must mention missed calls / verpasste Anrufe"


def test_demo_script_mentions_callback() -> None:
    content = _demo_script().lower()
    assert "rückruf" in content or "callback" in content or "zurückruf" in content, \
        "demo script must mention Rückruf / callback"


def test_demo_script_mentions_rueckruf_noetig() -> None:
    content = _demo_script()
    assert "Rückruf nötig" in content or "Rückruf-Anfrage" in content, \
        "demo script must mention 'Rückruf nötig' status"


def test_demo_script_mentions_staff_confirms() -> None:
    content = _demo_script().lower()
    assert "bestätigt" in content or "entscheidet" in content or "staff confirms" in content, \
        "demo script must state that staff confirms appointments"


def test_demo_script_mentions_no_diagnosis() -> None:
    content = _demo_script().lower()
    assert "keine diagnose" in content or "no diagnosis" in content or \
           "diagnosen" in content, \
        "demo script must mention no diagnosis"


def test_demo_script_mentions_no_medical_advice() -> None:
    content = _demo_script().lower()
    assert "keine medizinische beratung" in content or "no medical advice" in content or \
           "medizinische beratung" in content, \
        "demo script must mention no medical advice"


def test_demo_script_mentions_no_auto_confirmation() -> None:
    content = _demo_script().lower()
    assert "automatisch" in content and ("nicht" in content or "kein" in content or "no" in content), \
        "demo script must mention no automatic appointment confirmation"


def test_demo_script_mentions_144_emergency() -> None:
    assert "144" in _demo_script(), \
        "demo script must mention 144 for emergency routing"


def test_demo_script_mentions_30_day_pilot() -> None:
    content = _demo_script().lower()
    assert "30" in content and ("pilot" in content or "tag" in content), \
        "demo script must mention 30-day pilot"


def test_demo_script_mentions_synthetic_data() -> None:
    content = _demo_script().lower()
    assert "synthetisch" in content or "synthetic" in content or \
           "testdaten" in content or "demo-daten" in content or "keine echten" in content, \
        "demo script must mention synthetic / test data only"


def test_demo_script_no_auto_confirm_overclaim() -> None:
    content = _demo_script().lower()
    assert "automatisch gebucht" not in content, \
        "demo script must not claim appointments are auto-booked"


# ---------------------------------------------------------------------------
# 3. Pilot offer — required content
# ---------------------------------------------------------------------------

def test_pilot_offer_mentions_vienna() -> None:
    content = _pilot_offer()
    assert "Wien" in content or "Vienna" in content or "Wiener" in content or "Austrian" in content, \
        "pilot offer must mention Vienna / Wien / Austrian"


def test_pilot_offer_mentions_30_days() -> None:
    content = _pilot_offer().lower()
    assert "30" in content and ("tag" in content or "day" in content or "pilot" in content), \
        "pilot offer must mention 30-day structure"


def test_pilot_offer_mentions_pricing_390() -> None:
    assert "390" in _pilot_offer(), \
        "pilot offer must include €390 setup pricing anchor"


def test_pilot_offer_mentions_monthly_pricing() -> None:
    content = _pilot_offer()
    assert "290" in content or "490" in content, \
        "pilot offer must mention €290–€490/month pricing anchor"


def test_pilot_offer_mentions_no_production_phi() -> None:
    content = _pilot_offer().lower()
    assert "production phi" in content or "echte patientendaten" in content or \
           "no real patient" in content, \
        "pilot offer must state no production PHI / no real patient data in pilot"


def test_pilot_offer_mentions_no_auto_confirmation() -> None:
    content = _pilot_offer().lower()
    assert "automatisch" in content or "auto-confirm" in content or "auto confirm" in content, \
        "pilot offer must address no auto-confirmation"


def test_pilot_offer_mentions_no_diagnosis() -> None:
    content = _pilot_offer().lower()
    assert "diagnos" in content, \
        "pilot offer must mention no diagnosis"


def test_pilot_offer_mentions_safety_wording() -> None:
    content = _pilot_offer().lower()
    assert "no-go" in content or "no go" in content or "no real patient" in content or \
           "keine echten" in content or "production phi" in content, \
        "pilot offer must include PHI/safety wording"


# ---------------------------------------------------------------------------
# 4. One-page handout — required content
# ---------------------------------------------------------------------------

def test_handout_has_headline() -> None:
    content = _handout()
    assert "verpasste" in content.lower() or "Weniger verpasste" in content or \
           "missed" in content.lower(), \
        "handout must have headline mentioning missed calls / verpasste Anfragen"


def test_handout_mentions_callback_queue() -> None:
    content = _handout().lower()
    assert "rückruf" in content or "callback" in content or "warteschlange" in content, \
        "handout must mention callback queue / Rückruf"


def test_handout_mentions_staff_confirms() -> None:
    content = _handout().lower()
    assert "bestätigt" in content or "entscheidet" in content or "staff" in content or \
           "praxisteam" in content, \
        "handout must mention staff confirms appointments"


def test_handout_mentions_no_diagnosis() -> None:
    content = _handout().lower()
    assert "diagnos" in content, \
        "handout must mention no diagnosis"


def test_handout_mentions_144() -> None:
    assert "144" in _handout(), \
        "handout must mention 144 emergency routing"


def test_handout_mentions_pilot() -> None:
    content = _handout().lower()
    assert "pilot" in content, \
        "handout must mention pilot offer"


def test_handout_mentions_pricing() -> None:
    content = _handout()
    assert "390" in content or "290" in content or "490" in content, \
        "handout must include pricing anchor"


def test_handout_has_no_technical_words() -> None:
    content = _handout().lower()
    forbidden = ["uuid", "api key", "webhook", "database_url", "jwt", "fhir", "vapi config"]
    for word in forbidden:
        assert word not in content, \
            f"one-page handout must not contain technical term '{word}'"


def test_handout_safety_wording() -> None:
    content = _handout().lower()
    assert "keine echten patientendaten" in content or "no real patient" in content or \
           "demo" in content, \
        "handout must include safety wording about no real patient data"


# ---------------------------------------------------------------------------
# 5. Objection handling — required answers
# ---------------------------------------------------------------------------

def test_objections_addresses_gdpr() -> None:
    content = _objections().lower()
    assert "dsgvo" in content or "gdpr" in content or "avv" in content, \
        "objections must address DSGVO / data protection"


def test_objections_no_dsgvo_overclaim() -> None:
    content = _objections().lower()
    assert "dsgvo-zertifiziert" not in content, \
        "objections must not claim 'DSGVO-zertifiziert'"


def test_objections_addresses_no_auto_confirmation() -> None:
    content = _objections().lower()
    assert "automatisch" in content and "bestätigt" in content or \
           "auto-confirm" in content or "staff confirms" in content or \
           "praxisteam bestätigt" in content, \
        "objections must address no automatic appointment confirmation"


def test_objections_addresses_no_medical_advice() -> None:
    content = _objections().lower()
    assert "medizinische beratung" in content or "no medical advice" in content or \
           "diagnos" in content, \
        "objections must address no medical advice / no diagnosis"


def test_objections_addresses_emergency_144() -> None:
    assert "144" in _objections(), \
        "objections must address emergency routing to 144"


def test_objections_addresses_no_replacement_of_receptionist() -> None:
    content = _objections().lower()
    assert "ersetzt" in content or "replace" in content, \
        "objections must address that AI does not replace the receptionist"


def test_objections_no_fully_compliant_claim() -> None:
    content = _objections().lower()
    assert "vollständig konform" not in content and "fully compliant" not in content, \
        "objections must not claim 'vollständig konform' / 'fully compliant'"


def test_objections_no_production_readiness_claim() -> None:
    content = _objections().lower()
    assert "production ready" not in content and "produktionsbereit für alle" not in content, \
        "objections must not claim full production readiness"


# ---------------------------------------------------------------------------
# 6. Demo day checklist — required content
# ---------------------------------------------------------------------------

def test_checklist_mentions_demo_reset() -> None:
    content = _checklist()
    assert "Demo zurücksetzen" in content or "reset" in content.lower(), \
        "checklist must include demo reset step"


def test_checklist_mentions_demo_anruf_erstellen() -> None:
    content = _checklist()
    assert "Demo-Anruf erstellen" in content or "demo call" in content.lower(), \
        "checklist must include Demo-Anruf erstellen step"


def test_checklist_mentions_rueckruf_noetig() -> None:
    content = _checklist()
    assert "Rückruf nötig" in content or "rueckruf noetig" in content.lower(), \
        "checklist must verify Rückruf nötig appears"


def test_checklist_mentions_no_uuid_visible() -> None:
    content = _checklist().lower()
    assert "uuid" in content, \
        "checklist must remind to verify no UUID is visible"


def test_checklist_mentions_synthetic_data() -> None:
    content = _checklist().lower()
    assert "synthetisch" in content or "synthetic" in content or \
           "testdaten" in content or "fake" in content, \
        "checklist must require synthetic data only"


def test_checklist_mentions_pilot_close_question() -> None:
    content = _checklist().lower()
    assert "pilot" in content and ("darf ich" in content or "wann" in content or \
           "close" in content or "offer" in content), \
        "checklist must include pilot close question"


def test_checklist_no_technical_words_in_demo_language_rules() -> None:
    content = _checklist().lower()
    assert "uuid" in content and "api" in content and "webhook" in content, \
        "checklist must list forbidden technical words in language rules section"


# ---------------------------------------------------------------------------
# 7. Cross-doc: forbidden content
# ---------------------------------------------------------------------------

def test_no_database_url_in_sales_docs() -> None:
    assert "DATABASE_URL" not in _all_docs(), \
        "sales docs must not contain DATABASE_URL"


def test_no_jwt_secret_in_sales_docs() -> None:
    content = _all_docs()
    assert "JWT_SECRET" not in content and "jwt_secret" not in content, \
        "sales docs must not contain JWT_SECRET"


def test_no_vapi_api_key_in_sales_docs() -> None:
    content = _all_docs().lower()
    # Must not contain what looks like a real API key assignment
    matches = re.findall(r'vapi[_-]?api[_-]?key\s*[:=]\s*\S+', content)
    for m in matches:
        assert "<" in m or "env" in m or "placeholder" in m, \
            f"sales docs must not contain real Vapi API key value near: {m}"


def test_no_webhook_secret_in_sales_docs() -> None:
    content = _all_docs().lower()
    matches = re.findall(r'webhook[_-]?secret\s*[:=]\s*\S+', content)
    for m in matches:
        assert "<" in m or "env" in m, \
            f"sales docs must not contain real webhook secret value near: {m}"


def test_no_clinic_uuid_in_sales_docs() -> None:
    # A UUID pattern: 8-4-4-4-12 hex chars
    uuid_pattern = re.compile(
        r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b',
        re.IGNORECASE
    )
    assert not uuid_pattern.search(_all_docs()), \
        "sales docs must not contain real UUIDs (clinic_id, patient_id, etc.)"


def test_no_real_patient_names_pattern() -> None:
    content = _all_docs().lower()
    # Check known demo patient names don't appear in sales docs
    assert "mag. Klaus" not in _all_docs() and "Klaus Hofer" not in _all_docs(), \
        "sales docs must not contain real demo patient names"


def test_no_dsgvo_certified_claim() -> None:
    content = _all_docs().lower()
    assert "dsgvo-zertifiziert" not in content and "gdpr certified" not in content, \
        "sales docs must not claim DSGVO/GDPR certified"


def test_no_fully_compliant_claim() -> None:
    content = _all_docs().lower()
    assert "vollständig konform" not in content and "fully compliant" not in content, \
        "sales docs must not claim fully compliant"


def test_no_production_ready_claim() -> None:
    content = _all_docs().lower()
    assert "production ready" not in content, \
        "sales docs must not claim 'production ready'"


def test_no_ai_diagnosis_claim() -> None:
    content = _all_docs().lower()
    # Must not claim AI makes diagnoses
    assert "ki stellt diagnosen" not in content and \
           "ai makes diagnos" not in content and \
           "ai diagnosis" not in content, \
        "sales docs must not claim AI makes diagnoses"


def test_no_ai_medical_advice_claim() -> None:
    content = _all_docs().lower()
    assert "ki gibt medizinische beratung" not in content and \
           "ai gives medical advice" not in content, \
        "sales docs must not claim AI gives medical advice"


def test_no_automatic_appointment_confirmation_claim() -> None:
    content = _all_docs().lower()
    assert "termine werden automatisch bestätigt" not in content and \
           "appointments are automatically confirmed" not in content, \
        "sales docs must not claim appointments are automatically confirmed"


# ---------------------------------------------------------------------------
# 8. Pricing anchor present across docs
# ---------------------------------------------------------------------------

def test_pricing_anchor_390_present() -> None:
    assert "390" in _all_docs(), \
        "sales pack must include €390 pilot setup pricing anchor"


def test_pricing_anchor_monthly_present() -> None:
    content = _all_docs()
    assert "290" in content or "490" in content, \
        "sales pack must include monthly pricing anchor (€290–€490)"


# ---------------------------------------------------------------------------
# 9. Safety wording present across docs
# ---------------------------------------------------------------------------

def test_safety_wording_no_real_patient_data() -> None:
    content = _all_docs().lower()
    assert "keine echten patientendaten" in content or "no real patient data" in content or \
           "keine echten patient" in content, \
        "sales pack must include 'keine echten Patientendaten' safety wording"


def test_safety_wording_no_auto_confirmation() -> None:
    content = _all_docs().lower()
    assert "kein automatischer terminabschluss" in content or \
           "kein termin wird automatisch" in content or \
           "no automatic appointment" in content or \
           "staff confirms" in content or \
           "praxisteam bestätigt" in content, \
        "sales pack must include no-auto-confirmation safety wording"


def test_safety_wording_no_diagnosis() -> None:
    content = _all_docs().lower()
    assert "keine diagnose" in content or "no diagnosis" in content or \
           "stellt keine diagnosen" in content, \
        "sales pack must include no-diagnosis safety wording"


def test_safety_wording_emergency_144() -> None:
    assert "144" in _all_docs(), \
        "sales pack must include 144 emergency routing"


def test_safety_wording_production_phi_no_go() -> None:
    content = _all_docs().lower()
    assert "production phi" in content or "no-go" in content or \
           "echte patientendaten" in content, \
        "sales pack must reference Production PHI / no-go boundary"
