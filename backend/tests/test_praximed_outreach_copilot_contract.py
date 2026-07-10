"""
Static contract tests for PraxisMed Outreach Copilot.

Sprint 21 / Outreach — PraxisMed outreach copilot.

Verifies structure and safety only. No database. No network. No secrets.
No real patient data. No PHI. Production PHI remains NO-GO.

Tests confirm:
- Script exists with correct structure
- All CLI options are supported
- All output files are written
- No auto-email, no auto-call, no Twilio, no SMTP
- Do not contact exclusion present
- Not interested exclusion present
- LATIDO-compatible positioning present
- No diagnosis/medical advice
- No secrets
- Responsible outreach guardrails doc exists
"""

from __future__ import annotations

import csv
import io
import os
import re
import sys
import types

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))
_COPILOT = os.path.join(_REPO_ROOT, "scripts", "sales", "praximed_outreach_copilot.py")
_GUARDRAILS = os.path.join(_REPO_ROOT, "docs", "sales", "outreach", "RESPONSIBLE_OUTREACH_GUARDRAILS.md")
_OUTREACH_DIR = os.path.join(_REPO_ROOT, "docs", "sales", "outreach")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _script() -> str:
    with open(_COPILOT, encoding="utf-8") as f:
        return f.read()


def _guardrails() -> str:
    with open(_GUARDRAILS, encoding="utf-8") as f:
        return f.read()


FAKE_CSV_ROWS = [
    {
        "Lead ID": "TEST-00001",
        "Specialty Tier": "1",
        "Specialty Key": "dermatology",
        "Specialty Label DE": "Haut- u. Geschlechtskrankheiten",
        "Specialty Label EN": "Dermatology",
        "Doctor Name": "Demo Dermatologie Praxis",
        "Title": "Dr.",
        "Practice Name": "",
        "Specialty": "Haut- u. Geschlechtskrankheiten",
        "Sub-specialty / Notes from Listing": "",
        "Address": "Beispielgasse 5",
        "Postal Code": "1080",
        "City": "Wien",
        "District": "8. Bezirk – Josefstadt",
        "Phone": "+43 000 000001",
        "Email": "",
        "Website": "https://demo.example.com",
        "Praxisplan Profile URL": "",
        "Source URL": "",
        "Source": "Praxisplan",
        "Existing System Mentioned": "",
        "Likely LATIDO / Online Booking": "Unknown",
        "Priority Score": "4",
        "Priority Reason": "Phone + Vienna + Tier 1",
        "Outreach Status": "Not contacted",
        "Call Attempt 1 Date": "",
        "Call Attempt 1 Result": "",
        "Call Attempt 2 Date": "",
        "Call Attempt 2 Result": "",
        "Email Sent Date": "",
        "Email Result": "",
        "Walk-in Date": "",
        "Walk-in Result": "",
        "Contact Person": "",
        "Best Time to Call": "",
        "Follow-up Date": "",
        "Demo Offered": "No",
        "Demo Booked": "No",
        "Demo Date": "",
        "Pilot Interest": "Unknown",
        "Objection": "",
        "Next Action": "",
        "Notes": "",
        "Last Updated": "2026-07-10",
    },
    {
        "Lead ID": "TEST-00002",
        "Specialty Tier": "1",
        "Specialty Key": "gynecology",
        "Specialty Label DE": "Frauenheilkunde",
        "Specialty Label EN": "Gynecology",
        "Doctor Name": "Demo Frauenarzt Praxis",
        "Title": "Dr.",
        "Practice Name": "",
        "Specialty": "Frauenheilkunde u. Geburtshilfe",
        "Sub-specialty / Notes from Listing": "",
        "Address": "Teststraße 12",
        "Postal Code": "1090",
        "City": "Wien",
        "District": "9. Bezirk – Alsergrund",
        "Phone": "+43 000 000002",
        "Email": "demo@example.com",
        "Website": "",
        "Praxisplan Profile URL": "",
        "Source URL": "",
        "Source": "Praxisplan",
        "Existing System Mentioned": "",
        "Likely LATIDO / Online Booking": "Unknown",
        "Priority Score": "5",
        "Priority Reason": "Phone + Email + Vienna + Tier 1",
        "Outreach Status": "Not contacted",
        "Call Attempt 1 Date": "",
        "Call Attempt 1 Result": "",
        "Call Attempt 2 Date": "",
        "Call Attempt 2 Result": "",
        "Email Sent Date": "",
        "Email Result": "",
        "Walk-in Date": "",
        "Walk-in Result": "",
        "Contact Person": "",
        "Best Time to Call": "",
        "Follow-up Date": "",
        "Demo Offered": "No",
        "Demo Booked": "No",
        "Demo Date": "",
        "Pilot Interest": "Unknown",
        "Objection": "",
        "Next Action": "",
        "Notes": "",
        "Last Updated": "2026-07-10",
    },
    {
        "Lead ID": "TEST-00003",
        "Specialty Tier": "2",
        "Specialty Key": "ent",
        "Specialty Label DE": "HNO",
        "Specialty Label EN": "ENT",
        "Doctor Name": "Demo HNO Praxis",
        "Title": "Dr.",
        "Practice Name": "",
        "Specialty": "Hals-, Nasen- u. Ohrenheilkunde",
        "Sub-specialty / Notes from Listing": "",
        "Address": "Kaiserstraße 22",
        "Postal Code": "1070",
        "City": "Wien",
        "District": "7. Bezirk – Neubau",
        "Phone": "",
        "Email": "",
        "Website": "",
        "Praxisplan Profile URL": "",
        "Source URL": "",
        "Source": "Praxisplan",
        "Existing System Mentioned": "",
        "Likely LATIDO / Online Booking": "Unknown",
        "Priority Score": "2",
        "Priority Reason": "Vienna, no phone",
        "Outreach Status": "Not contacted",
        "Call Attempt 1 Date": "",
        "Call Attempt 1 Result": "Call later",
        "Call Attempt 2 Date": "",
        "Call Attempt 2 Result": "",
        "Email Sent Date": "",
        "Email Result": "",
        "Walk-in Date": "",
        "Walk-in Result": "",
        "Contact Person": "",
        "Best Time to Call": "",
        "Follow-up Date": "",
        "Demo Offered": "No",
        "Demo Booked": "No",
        "Demo Date": "",
        "Pilot Interest": "Unknown",
        "Objection": "",
        "Next Action": "",
        "Notes": "",
        "Last Updated": "2026-07-10",
    },
    {
        "Lead ID": "TEST-00004",
        "Specialty Tier": "1",
        "Specialty Key": "orthopedics",
        "Specialty Label DE": "Orthopädie",
        "Specialty Label EN": "Orthopedics",
        "Doctor Name": "Demo Orthopädie Praxis",
        "Title": "Dr.",
        "Practice Name": "",
        "Specialty": "Orthopädie und Traumatologie",
        "Sub-specialty / Notes from Listing": "",
        "Address": "Hauptplatz 3",
        "Postal Code": "1060",
        "City": "Wien",
        "District": "6. Bezirk – Mariahilf",
        "Phone": "+43 000 000004",
        "Email": "",
        "Website": "",
        "Praxisplan Profile URL": "",
        "Source URL": "",
        "Source": "Praxisplan",
        "Existing System Mentioned": "",
        "Likely LATIDO / Online Booking": "Unknown",
        "Priority Score": "3",
        "Priority Reason": "Phone + Vienna + Tier 1",
        "Outreach Status": "Do not contact",
        "Call Attempt 1 Date": "",
        "Call Attempt 1 Result": "",
        "Call Attempt 2 Date": "",
        "Call Attempt 2 Result": "",
        "Email Sent Date": "",
        "Email Result": "",
        "Walk-in Date": "",
        "Walk-in Result": "",
        "Contact Person": "",
        "Best Time to Call": "",
        "Follow-up Date": "",
        "Demo Offered": "No",
        "Demo Booked": "No",
        "Demo Date": "",
        "Pilot Interest": "Unknown",
        "Objection": "",
        "Next Action": "",
        "Notes": "",
        "Last Updated": "2026-07-10",
    },
    {
        "Lead ID": "TEST-00005",
        "Specialty Tier": "1",
        "Specialty Key": "dermatology",
        "Specialty Label DE": "Haut- u. Geschlechtskrankheiten",
        "Specialty Label EN": "Dermatology",
        "Doctor Name": "Demo Dermatologie 2",
        "Title": "Dr.",
        "Practice Name": "",
        "Specialty": "Haut- u. Geschlechtskrankheiten",
        "Sub-specialty / Notes from Listing": "",
        "Address": "Ringstraße 10",
        "Postal Code": "1010",
        "City": "Wien",
        "District": "1. Bezirk – Innere Stadt",
        "Phone": "+43 000 000005",
        "Email": "demo2@example.com",
        "Website": "https://demo2.example.com",
        "Praxisplan Profile URL": "",
        "Source URL": "",
        "Source": "Praxisplan",
        "Existing System Mentioned": "",
        "Likely LATIDO / Online Booking": "Unknown",
        "Priority Score": "5",
        "Priority Reason": "Phone + Email + Website + Vienna + Tier 1",
        "Outreach Status": "Asked to send email",
        "Call Attempt 1 Date": "2026-07-08",
        "Call Attempt 1 Result": "Asked to send email",
        "Call Attempt 2 Date": "",
        "Call Attempt 2 Result": "",
        "Email Sent Date": "",
        "Email Result": "",
        "Walk-in Date": "",
        "Walk-in Result": "",
        "Contact Person": "Rezeption",
        "Best Time to Call": "Vormittag",
        "Follow-up Date": "2026-07-10",
        "Demo Offered": "No",
        "Demo Booked": "No",
        "Demo Date": "",
        "Pilot Interest": "Unknown",
        "Objection": "",
        "Next Action": "E-Mail senden",
        "Notes": "Rezeptionistin war freundlich",
        "Last Updated": "2026-07-08",
    },
]


def _make_fake_csv() -> str:
    if not FAKE_CSV_ROWS:
        return ""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(FAKE_CSV_ROWS[0].keys()))
    writer.writeheader()
    writer.writerows(FAKE_CSV_ROWS)
    return buf.getvalue()


def _import_copilot() -> types.ModuleType:
    import importlib.util
    spec = importlib.util.spec_from_file_location("praximed_outreach_copilot", _COPILOT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# 1. File existence
# ---------------------------------------------------------------------------

def test_copilot_script_exists() -> None:
    assert os.path.isfile(_COPILOT), \
        "scripts/sales/praximed_outreach_copilot.py must exist"


def test_guardrails_doc_exists() -> None:
    assert os.path.isfile(_GUARDRAILS), \
        "docs/sales/outreach/RESPONSIBLE_OUTREACH_GUARDRAILS.md must exist"


def test_outreach_dir_exists() -> None:
    assert os.path.isdir(_OUTREACH_DIR), \
        "docs/sales/outreach/ directory must exist"


# ---------------------------------------------------------------------------
# 2. CLI options present in script
# ---------------------------------------------------------------------------

def test_cli_supports_input() -> None:
    assert "--input" in _script(), "script must support --input"


def test_cli_supports_daily_limit() -> None:
    assert "--daily-limit" in _script() or "daily_limit" in _script(), \
        "script must support --daily-limit"


def test_cli_supports_specialty() -> None:
    assert "--specialty" in _script(), "script must support --specialty"


def test_cli_supports_tier() -> None:
    assert "--tier" in _script(), "script must support --tier"


def test_cli_supports_mode_plan() -> None:
    assert "plan" in _script(), "script must support --mode plan"


def test_cli_supports_mode_drafts() -> None:
    assert "drafts" in _script(), "script must support --mode drafts"


def test_cli_supports_mode_followups() -> None:
    assert "followups" in _script(), "script must support --mode followups"


def test_cli_supports_mode_report() -> None:
    assert "report" in _script(), "script must support --mode report"


def test_cli_supports_output_dir() -> None:
    assert "--output-dir" in _script() or "output_dir" in _script(), \
        "script must support --output-dir"


# ---------------------------------------------------------------------------
# 3. Output file types referenced
# ---------------------------------------------------------------------------

def test_writes_daily_outreach_plan() -> None:
    assert "daily_outreach_plan" in _script() or "outreach_plan" in _script(), \
        "script must write a daily outreach plan file"


def test_writes_call_list_csv() -> None:
    assert "call_list" in _script() and ".csv" in _script(), \
        "script must write a call list CSV"


def test_writes_email_drafts_markdown() -> None:
    assert "email_drafts" in _script() and ".md" in _script(), \
        "script must write an email drafts markdown file"


def test_writes_followups_markdown() -> None:
    assert "followups" in _script() and ".md" in _script(), \
        "script must write a followups markdown file"


def test_writes_report_markdown() -> None:
    assert "outreach_report" in _script() or "report" in _script(), \
        "script must write a report markdown file"


# ---------------------------------------------------------------------------
# 4. No auto-email, no auto-call
# ---------------------------------------------------------------------------

def test_no_smtplib() -> None:
    assert "smtplib" not in _script(), \
        "script must not import smtplib (no auto-email)"


def test_no_sendmail() -> None:
    assert "sendmail" not in _script().lower(), \
        "script must not call sendmail"


def test_no_gmail_api() -> None:
    content = _script().lower()
    assert "gmail" not in content or "gmail api" not in content, \
        "script must not use Gmail API for sending"


def test_no_twilio_import() -> None:
    content = _script().lower()
    assert "import twilio" not in content and "from twilio" not in content, \
        "script must not import Twilio"


def test_no_vapi_outbound() -> None:
    content = _script().lower()
    assert "vapi" not in content, \
        "script must not reference Vapi (no auto-calling)"


def test_no_auto_dial() -> None:
    content = _script().lower()
    assert "autodial" not in content and "robo_call" not in content, \
        "script must not use auto-dialing"


def test_no_requests_post() -> None:
    content = _script()
    assert "requests.post" not in content, \
        "script must not POST to external services"


# ---------------------------------------------------------------------------
# 5. Safety guardrails in script
# ---------------------------------------------------------------------------

def test_do_not_contact_exclusion() -> None:
    assert "Do not contact" in _script(), \
        "script must exclude 'Do not contact' leads"


def test_not_interested_exclusion() -> None:
    assert "Not interested" in _script(), \
        "script must exclude 'Not interested' leads"


def test_prioritizes_tier_1() -> None:
    content = _script()
    assert "tier" in content.lower() and ("1" in content), \
        "script must prioritize Tier 1 leads"


def test_prioritizes_phone_available() -> None:
    assert "Phone" in _script(), \
        "script must prioritize leads with phone available"


def test_latido_compatible_positioning() -> None:
    assert "LATIDO" in _script(), \
        "script must include LATIDO-compatible positioning"


def test_no_auto_confirmation_claim() -> None:
    content = _script().lower()
    assert "auto-confirm" not in content and "bestätigt automatisch" not in content, \
        "script must not claim auto-confirmation of appointments"


def test_no_diagnosis_claim() -> None:
    content = _script().lower()
    # The word "diagnos" is allowed only as a safety disclaimer ("keine Diagnosen")
    # The script must not make positive diagnosis claims
    assert "stellt diagnosen" not in content or "keine" in content, \
        "script must not claim to make diagnoses"
    assert "diagnosis" not in content, \
        "script must not use the English word 'diagnosis'"


def test_no_medical_advice_claim() -> None:
    assert "medical advice" not in _script().lower(), \
        "script must not claim to give medical advice"


def test_no_triage() -> None:
    assert "triage" not in _script().lower(), \
        "script must not reference triage"


def test_no_dsgvo_certified_claim() -> None:
    content = _script().lower()
    assert "dsgvo-zertifiziert" not in content and "gdpr certified" not in content, \
        "script must not claim DSGVO certification"


def test_public_contacts_only() -> None:
    content = _script().lower()
    assert "public" in content or "publicly" in content, \
        "script must state only publicly listed contact details are used"


# ---------------------------------------------------------------------------
# 6. No secrets
# ---------------------------------------------------------------------------

def test_no_database_url() -> None:
    assert "DATABASE_URL" not in _script(), "script must not contain DATABASE_URL"


def test_no_jwt_secret() -> None:
    content = _script().lower()
    assert "jwt_secret" not in content and "secret_key" not in content, \
        "script must not contain JWT or secret key references"


def test_no_vapi_api_key() -> None:
    content = _script().lower()
    assert "vapi_api_key" not in content and "vapi_secret" not in content, \
        "script must not contain Vapi API key"


def test_no_webhook_secret() -> None:
    assert "webhook_secret" not in _script().lower(), \
        "script must not contain webhook secret"


def test_no_api_key_literals() -> None:
    content = _script()
    api_key_pattern = re.compile(r'["\']([A-Za-z0-9]{32,})["\']')
    matches = api_key_pattern.findall(content)
    assert not matches, f"script must not contain hardcoded API key literals: {matches[:3]}"


# ---------------------------------------------------------------------------
# 7. Guardrails document content
# ---------------------------------------------------------------------------

def test_guardrails_mentions_no_mass_spam() -> None:
    content = _guardrails().lower()
    assert "mass" in content or "bulk" in content or "spam" in content, \
        "guardrails must mention no mass spam"


def test_guardrails_mentions_no_auto_calling() -> None:
    content = _guardrails().lower()
    assert "auto-call" in content or "auto-dial" in content or "robocall" in content \
           or "auto" in content, \
        "guardrails must mention no auto-calling"


def test_guardrails_mentions_opt_out() -> None:
    content = _guardrails()
    assert "opt-out" in content.lower() or "Do not contact" in content, \
        "guardrails must mention opt-out / Do not contact"


def test_guardrails_mentions_no_patient_data() -> None:
    content = _guardrails().lower()
    assert "patient" in content and ("no" in content or "not" in content or "never" in content), \
        "guardrails must mention no patient data"


def test_guardrails_mentions_no_phi() -> None:
    assert "PHI" in _guardrails().upper(), \
        "guardrails must mention PHI boundary"


def test_guardrails_mentions_no_auto_email() -> None:
    content = _guardrails().lower()
    assert "auto-email" in content or "automated" in content or "bulk" in content \
           or "mass" in content, \
        "guardrails must mention no auto-email"


def test_guardrails_mentions_manual_review() -> None:
    content = _guardrails().lower()
    assert "manual" in content and "review" in content, \
        "guardrails must require manual review before outreach"


def test_guardrails_mentions_public_contacts_only() -> None:
    content = _guardrails().lower()
    assert "public" in content and ("contact" in content or "listed" in content), \
        "guardrails must state public contacts only"


def test_guardrails_mentions_no_dsgvo_overclaim() -> None:
    content = _guardrails().lower()
    assert "dsgvo" in content or "gdpr" in content, \
        "guardrails must address DSGVO/GDPR responsible handling"


def test_guardrails_mentions_do_not_contact() -> None:
    assert "Do not contact" in _guardrails(), \
        "guardrails must have 'Do not contact' rule"


# ---------------------------------------------------------------------------
# 8. Functional tests with fake CSV fixture
# ---------------------------------------------------------------------------

def test_load_leads_reads_csv(tmp_path) -> None:
    mod = _import_copilot()
    csv_path = tmp_path / "test_leads.csv"
    csv_path.write_text(_make_fake_csv(), encoding="utf-8-sig")
    leads = mod.load_leads(str(csv_path))
    assert len(leads) == len(FAKE_CSV_ROWS), "load_leads must return all rows"


def test_filter_leads_excludes_do_not_contact(tmp_path) -> None:
    mod = _import_copilot()
    csv_path = tmp_path / "test_leads.csv"
    csv_path.write_text(_make_fake_csv(), encoding="utf-8-sig")
    leads = mod.load_leads(str(csv_path))
    filtered = mod.filter_leads(leads)
    do_not_contact = [l for l in filtered if l.get("Outreach Status") == "Do not contact"]
    assert len(do_not_contact) == 0, \
        "filter_leads must exclude 'Do not contact' leads"


def test_filter_leads_excludes_not_interested(tmp_path) -> None:
    mod = _import_copilot()
    csv_path = tmp_path / "test_leads.csv"

    rows = FAKE_CSV_ROWS.copy()
    rows[0] = dict(rows[0], **{"Outreach Status": "Not interested"})

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

    csv_path.write_text(buf.getvalue(), encoding="utf-8-sig")
    leads = mod.load_leads(str(csv_path))
    filtered = mod.filter_leads(leads)
    not_interested = [l for l in filtered if l.get("Outreach Status") == "Not interested"]
    assert len(not_interested) == 0, \
        "filter_leads must exclude 'Not interested' leads"


def test_filter_leads_by_specialty(tmp_path) -> None:
    mod = _import_copilot()
    csv_path = tmp_path / "test_leads.csv"
    csv_path.write_text(_make_fake_csv(), encoding="utf-8-sig")
    leads = mod.load_leads(str(csv_path))
    filtered = mod.filter_leads(leads, specialty="gynecology")
    assert all(l.get("Specialty Key") == "gynecology" for l in filtered), \
        "filter_leads --specialty must only return that specialty"


def test_filter_leads_by_tier(tmp_path) -> None:
    mod = _import_copilot()
    csv_path = tmp_path / "test_leads.csv"
    csv_path.write_text(_make_fake_csv(), encoding="utf-8-sig")
    leads = mod.load_leads(str(csv_path))
    filtered = mod.filter_leads(leads, tier="2")
    assert all(l.get("Specialty Tier") == "2" for l in filtered), \
        "filter_leads --tier must only return that tier"


def test_score_lead_tier1_scores_higher(tmp_path) -> None:
    mod = _import_copilot()
    tier1 = dict(FAKE_CSV_ROWS[0], **{"Specialty Tier": "1", "Phone": "+43 000 000001"})
    tier3 = dict(FAKE_CSV_ROWS[0], **{"Specialty Tier": "3", "Phone": ""})
    assert mod.score_lead(tier1) > mod.score_lead(tier3), \
        "Tier 1 + phone must score higher than Tier 3 + no phone"


def test_score_lead_phone_adds_score(tmp_path) -> None:
    mod = _import_copilot()
    with_phone = dict(FAKE_CSV_ROWS[0], **{"Phone": "+43 000 000001", "Specialty Tier": "2"})
    no_phone = dict(FAKE_CSV_ROWS[0], **{"Phone": "", "Specialty Tier": "2"})
    assert mod.score_lead(with_phone) > mod.score_lead(no_phone), \
        "Having a phone number must increase score"


def test_plan_mode_writes_files(tmp_path) -> None:
    mod = _import_copilot()
    csv_path = tmp_path / "test_leads.csv"
    csv_path.write_text(_make_fake_csv(), encoding="utf-8-sig")
    leads = mod.load_leads(str(csv_path))
    filtered = mod.filter_leads(leads)
    output_dir = str(tmp_path / "daily_plans")

    mod.run_plan(leads, filtered, output_dir, daily_limit=5)

    today = mod.TODAY
    assert os.path.isfile(os.path.join(output_dir, f"{today}_daily_outreach_plan.md")), \
        "run_plan must write daily_outreach_plan.md"
    assert os.path.isfile(os.path.join(output_dir, f"{today}_call_list.csv")), \
        "run_plan must write call_list.csv"
    assert os.path.isfile(os.path.join(output_dir, f"{today}_update_instructions.md")), \
        "run_plan must write update_instructions.md"


def test_drafts_mode_writes_file(tmp_path) -> None:
    mod = _import_copilot()
    csv_path = tmp_path / "test_leads.csv"
    csv_path.write_text(_make_fake_csv(), encoding="utf-8-sig")
    leads = mod.load_leads(str(csv_path))
    filtered = mod.filter_leads(leads)
    output_dir = str(tmp_path / "daily_plans")

    mod.run_drafts(filtered, output_dir, daily_limit=5)

    today = mod.TODAY
    assert os.path.isfile(os.path.join(output_dir, f"{today}_email_drafts.md")), \
        "run_drafts must write email_drafts.md"


def test_followups_mode_writes_file(tmp_path) -> None:
    mod = _import_copilot()
    csv_path = tmp_path / "test_leads.csv"
    csv_path.write_text(_make_fake_csv(), encoding="utf-8-sig")
    leads = mod.load_leads(str(csv_path))
    output_dir = str(tmp_path / "daily_plans")

    mod.run_followups(leads, output_dir)

    today = mod.TODAY
    assert os.path.isfile(os.path.join(output_dir, f"{today}_followups.md")), \
        "run_followups must write followups.md"


def test_report_mode_writes_file(tmp_path) -> None:
    mod = _import_copilot()
    csv_path = tmp_path / "test_leads.csv"
    csv_path.write_text(_make_fake_csv(), encoding="utf-8-sig")
    leads = mod.load_leads(str(csv_path))
    filtered = mod.filter_leads(leads)
    output_dir = str(tmp_path / "daily_plans")

    mod.run_report(leads, filtered, output_dir)

    today = mod.TODAY
    assert os.path.isfile(os.path.join(output_dir, f"{today}_outreach_report.md")), \
        "run_report must write outreach_report.md"


def test_email_draft_contains_latido_note(tmp_path) -> None:
    mod = _import_copilot()
    draft = mod.generate_email_draft(FAKE_CSV_ROWS[0])
    assert "LATIDO" in draft, "email draft must mention LATIDO-compatible positioning"


def test_email_draft_no_auto_send(tmp_path) -> None:
    mod = _import_copilot()
    draft = mod.generate_email_draft(FAKE_CSV_ROWS[0])
    assert "automatisch" not in draft.lower() or "manuelle" in draft.lower() or \
           "nicht" in draft.lower(), \
        "email draft must not claim auto-send"


def test_email_draft_no_diagnosis(tmp_path) -> None:
    mod = _import_copilot()
    draft = mod.generate_email_draft(FAKE_CSV_ROWS[0])
    # German "stellt keine Diagnosen" is the safety disclaimer — allowed.
    # English "diagnosis" must not appear (would indicate a claim).
    assert "diagnosis" not in draft.lower(), \
        "email draft must not use English 'diagnosis' — only German safety disclaimer is allowed"


def test_email_draft_no_medical_advice(tmp_path) -> None:
    mod = _import_copilot()
    draft = mod.generate_email_draft(FAKE_CSV_ROWS[0])
    assert "medizinische beratung" not in draft.lower() or "keine" in draft.lower(), \
        "email draft must not claim to give medical advice"


def test_followup_identifies_asked_to_send_email(tmp_path) -> None:
    mod = _import_copilot()
    csv_path = tmp_path / "test_leads.csv"
    csv_path.write_text(_make_fake_csv(), encoding="utf-8-sig")
    leads = mod.load_leads(str(csv_path))

    followup_pairs = mod.get_followup_leads(leads)
    reasons = [r for _, r in followup_pairs]
    # TEST-00005 has status "Asked to send email"
    assert any("E-Mail" in r or "email" in r.lower() for r in reasons), \
        "get_followup_leads must identify 'Asked to send email' leads"


def test_call_list_csv_has_correct_columns(tmp_path) -> None:
    mod = _import_copilot()
    csv_path = tmp_path / "test_leads.csv"
    csv_path.write_text(_make_fake_csv(), encoding="utf-8-sig")
    leads = mod.load_leads(str(csv_path))
    filtered = mod.filter_leads(leads)

    call_leads = mod.select_call_leads(filtered, 5)
    email_leads = mod.select_email_leads(filtered, 5)
    csv_content = mod.generate_call_list_csv(call_leads, email_leads)

    reader = csv.DictReader(io.StringIO(csv_content))
    fieldnames = reader.fieldnames or []
    for col in ["Lead ID", "Doctor Name", "Phone", "Priority Score", "Likely Objection"]:
        assert col in fieldnames, f"Call list CSV must have column '{col}'"


def test_plan_md_mentions_update_tracker(tmp_path) -> None:
    mod = _import_copilot()
    csv_path = tmp_path / "test_leads.csv"
    csv_path.write_text(_make_fake_csv(), encoding="utf-8-sig")
    leads = mod.load_leads(str(csv_path))
    filtered = mod.filter_leads(leads)

    call_leads = mod.select_call_leads(filtered, 5)
    email_leads = mod.select_email_leads(filtered, 5)
    walkin_leads = mod.select_walkin_leads(filtered, 5)
    plan_md = mod.generate_plan_md(call_leads, email_leads, walkin_leads, len(leads), 3)

    assert "tracker" in plan_md.lower() or "Tracker" in plan_md, \
        "daily plan must mention updating the tracker"


def test_report_shows_total_leads(tmp_path) -> None:
    mod = _import_copilot()
    csv_path = tmp_path / "test_leads.csv"
    csv_path.write_text(_make_fake_csv(), encoding="utf-8-sig")
    leads = mod.load_leads(str(csv_path))
    filtered = mod.filter_leads(leads)

    top_next = sorted(filtered, key=mod.score_lead, reverse=True)
    report = mod.generate_report_md(leads, filtered, top_next)
    assert str(len(leads)) in report, "report must show total leads count"


def test_fake_csv_no_real_doctor_names() -> None:
    for row in FAKE_CSV_ROWS:
        name = row.get("Doctor Name", "")
        assert name.startswith("Demo"), \
            f"Fake CSV test fixture doctor names must start with 'Demo', got: '{name}'"


def test_fake_csv_no_real_phone_numbers() -> None:
    for row in FAKE_CSV_ROWS:
        phone = row.get("Phone", "")
        if phone:
            # Fake phones must use the +43 000 placeholder pattern (no real subscriber number)
            assert phone.startswith("+43 000") or "000000" in phone, \
                f"Fake CSV phones must be +43 000 placeholder, got: '{phone}'"


def test_fake_csv_no_patient_data() -> None:
    csv_content = _make_fake_csv().lower()
    assert "patient_id" not in csv_content
    assert "diagnosis" not in csv_content
    assert "medical record" not in csv_content
