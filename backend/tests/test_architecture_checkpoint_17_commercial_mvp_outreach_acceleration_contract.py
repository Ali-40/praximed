"""
Architecture Checkpoint 17 — Commercial MVP and Clinic Outreach Acceleration Plan
contract tests.

Static tests verifying the checkpoint doc records:
- Immediate clinic outreach (fake-data staging is demo-ready)
- 30-day pilot offer structure
- Fake-data staging core PASS
- Production PHI NO-GO
- Patient database linking (Module 121 commercial)
- Doctor/reception notification
- Pre-appointment patient summary
- Consultation summary draft
- Fabel 5 premium UI/UX (Sprint 18 high priority)
- 14-day execution timeline
- First 50 private clinics in Vienna
- No real patient data
- No secrets
- Module 121 — Patient and Appointment Data Linking Foundation (commercial next)
"""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
CHECKPOINT_DOC = (
    ROOT
    / "docs"
    / "architecture"
    / "ARCHITECTURE_CHECKPOINT_17_COMMERCIAL_MVP_OUTREACH_ACCELERATION.md"
)


def _text() -> str:
    return CHECKPOINT_DOC.read_text()


def test_checkpoint_doc_exists():
    assert CHECKPOINT_DOC.exists(), (
        "ARCHITECTURE_CHECKPOINT_17_COMMERCIAL_MVP_OUTREACH_ACCELERATION.md must exist"
    )


def test_checkpoint_doc_non_empty():
    assert len(_text()) > 500, "checkpoint doc must have substantial content"


def test_checkpoint_doc_mentions_immediate_outreach():
    text = _text()
    assert "outreach" in text.lower() and (
        "immediately" in text.lower() or "now" in text.lower() or "immediate" in text.lower()
    ), "checkpoint doc must state that clinic outreach starts immediately"


def test_checkpoint_doc_mentions_30_day_pilot():
    text = _text()
    assert "30-day pilot" in text.lower() or "30 day" in text.lower() or "30-day" in text, (
        "checkpoint doc must mention the 30-day pilot offer"
    )


def test_checkpoint_doc_mentions_fake_data_staging_pass():
    text = _text()
    assert (
        "fake" in text.lower()
        and "staging" in text.lower()
        and "PASS" in text
    ), "checkpoint doc must record fake-data staging core as PASS"


def test_checkpoint_doc_mentions_production_phi_no_go():
    text = _text()
    assert "production phi" in text.lower() and (
        "no-go" in text.lower() or "NO-GO" in text
    ), "checkpoint doc must confirm production PHI readiness is NO-GO"


def test_checkpoint_doc_mentions_patient_database_linking():
    text = _text()
    assert "patient" in text.lower() and (
        "linking" in text.lower() or "database" in text.lower()
    ), "checkpoint doc must mention patient database linking as a commercial feature"


def test_checkpoint_doc_mentions_doctor_notification():
    text = _text()
    assert (
        "notification" in text.lower()
        and ("doctor" in text.lower() or "reception" in text.lower())
    ), "checkpoint doc must mention doctor/reception notification"


def test_checkpoint_doc_mentions_pre_appointment_summary():
    text = _text()
    assert "pre-appointment" in text.lower() or (
        "pre" in text.lower() and "appointment" in text.lower() and "summary" in text.lower()
    ), "checkpoint doc must mention pre-appointment patient summary"


def test_checkpoint_doc_mentions_consultation_summary_draft():
    text = _text()
    assert "consultation" in text.lower() and "summary" in text.lower(), (
        "checkpoint doc must mention consultation summary draft"
    )


def test_checkpoint_doc_mentions_fabel_5():
    text = _text()
    assert "fabel 5" in text.lower() or "Fabel 5" in text, (
        "checkpoint doc must mention Fabel 5 premium UI/UX"
    )


def test_checkpoint_doc_mentions_premium_uiux():
    text = _text()
    assert (
        "premium" in text.lower()
        and ("ui" in text.lower() or "ux" in text.lower())
    ), "checkpoint doc must mention premium UI/UX"


def test_checkpoint_doc_mentions_14_day_timeline():
    text = _text()
    assert "14-day" in text.lower() or "14 day" in text.lower() or "14" in text, (
        "checkpoint doc must include a 14-day execution timeline"
    )


def test_checkpoint_doc_mentions_first_50_clinics():
    text = _text()
    assert "50" in text and "clinic" in text.lower(), (
        "checkpoint doc must mention the first 50 private clinics target"
    )


def test_checkpoint_doc_mentions_vienna():
    text = _text()
    assert "vienna" in text.lower() or "Wien" in text, (
        "checkpoint doc must mention Vienna as the outreach geography"
    )


def test_checkpoint_doc_mentions_no_real_patient_data():
    text = _text()
    assert "no real patient data" in text.lower() or "No real patient data" in text, (
        "checkpoint doc must confirm no real patient data"
    )


def test_checkpoint_doc_mentions_no_secrets():
    text = _text()
    assert (
        "no secrets" in text.lower()
        or "not recorded" in text.lower()
        or "ENFORCED" in text
    ), "checkpoint doc must confirm no secrets are recorded"


def test_checkpoint_doc_mentions_module_121_commercial():
    text = _text()
    assert "Module 121" in text and (
        "patient" in text.lower()
        or "appointment" in text.lower()
        or "linking" in text.lower()
    ), (
        "checkpoint doc must identify Module 121 — Patient and Appointment Data Linking Foundation"
    )


def test_checkpoint_doc_mentions_founding_clinic():
    text = _text()
    assert "founding clinic" in text.lower() or "founding" in text.lower(), (
        "checkpoint doc must mention founding clinic partner positioning"
    )


def test_checkpoint_doc_mentions_pricing():
    text = _text()
    assert (
        "pricing" in text.lower()
        or "€" in text
        or "per month" in text.lower()
        or "/month" in text.lower()
    ), "checkpoint doc must include indicative pricing information"


def test_checkpoint_doc_mentions_no_phi_claims():
    text = _text()
    assert (
        "gdpr" in text.lower() or "hipaa" in text.lower() or "compliance" in text.lower()
    ) and (
        "not permitted" in text.lower()
        or "no formal" in text.lower()
        or "ENFORCED" in text
    ), "checkpoint doc must prohibit premature GDPR/HIPAA compliance claims"


def test_checkpoint_doc_mentions_sprint_18():
    text = _text()
    assert "sprint 18" in text.lower() or "Sprint 18" in text, (
        "checkpoint doc must reference Sprint 18 for Fabel 5 UI/UX polish"
    )


def test_checkpoint_doc_mentions_follow_up_reminder():
    text = _text()
    assert "follow-up" in text.lower() or "reminder" in text.lower(), (
        "checkpoint doc must mention follow-up/reminder workflow"
    )


def test_checkpoint_doc_mentions_no_auto_confirm():
    text = _text()
    assert (
        "no auto" in text.lower()
        or "manual" in text.lower()
        or "staff confirm" in text.lower()
    ), "checkpoint doc must confirm no automated appointment confirmation"
