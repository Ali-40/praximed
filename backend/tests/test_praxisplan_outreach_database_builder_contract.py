"""
Static contract tests for Praxisplan outreach database builder.

Sprint 21 / Outreach — Praxisplan lead database builder.

Verifies file content only. No database. No network. No secrets.
No real patient data. No PHI. Production PHI remains NO-GO.

Tests confirm:
- Script exists with correct structure
- Required columns are defined
- Dropdown/status values are defined
- Rate limiting present in script
- Deduplication present in script
- CSV and XLSX export present
- Mode A (URL) and Mode B (HTML fallback) supported
- README exists with responsible outreach rules
- Template files exist
- No secrets, no auto-email, no auto-call
- No PHI, no patient data
"""

from __future__ import annotations

import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))
_SCRIPT = os.path.join(_REPO_ROOT, "scripts", "sales", "build_praxisplan_lead_database.py")
_OUTREACH_DIR = os.path.join(_REPO_ROOT, "docs", "sales", "outreach")
_README = os.path.join(_OUTREACH_DIR, "praxisplan_child_psychiatry_leads_README.md")
_TEMPLATE_XLSX = os.path.join(_OUTREACH_DIR, "praxisplan_child_psychiatry_leads_template.xlsx")
_TEMPLATE_CSV = os.path.join(_OUTREACH_DIR, "praxisplan_child_psychiatry_leads_template.csv")
_LEADS_XLSX = os.path.join(_OUTREACH_DIR, "praxisplan_child_psychiatry_leads.xlsx")
_LEADS_CSV = os.path.join(_OUTREACH_DIR, "praxisplan_child_psychiatry_leads.csv")


def _script() -> str:
    with open(_SCRIPT, encoding="utf-8") as f:
        return f.read()


def _readme() -> str:
    with open(_README, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. File existence
# ---------------------------------------------------------------------------

def test_script_exists() -> None:
    assert os.path.isfile(_SCRIPT), \
        "scripts/sales/build_praxisplan_lead_database.py must exist"


def test_outreach_dir_exists() -> None:
    assert os.path.isdir(_OUTREACH_DIR), \
        "docs/sales/outreach/ directory must exist"


def test_readme_exists() -> None:
    assert os.path.isfile(_README), \
        "praxisplan_child_psychiatry_leads_README.md must exist"


def test_template_xlsx_exists() -> None:
    assert os.path.isfile(_TEMPLATE_XLSX), \
        "praxisplan_child_psychiatry_leads_template.xlsx must exist"


def test_template_csv_exists() -> None:
    assert os.path.isfile(_TEMPLATE_CSV), \
        "praxisplan_child_psychiatry_leads_template.csv must exist"


def test_leads_xlsx_exists() -> None:
    assert os.path.isfile(_LEADS_XLSX), \
        "praxisplan_child_psychiatry_leads.xlsx must exist (real or template)"


def test_leads_csv_exists() -> None:
    assert os.path.isfile(_LEADS_CSV), \
        "praxisplan_child_psychiatry_leads.csv must exist (real or template)"


# ---------------------------------------------------------------------------
# 2. Required columns defined in script
# ---------------------------------------------------------------------------

REQUIRED_COLUMNS = [
    "Lead ID",
    "Doctor Name",
    "Title",
    "Practice Name",
    "Specialty",
    "Address",
    "Postal Code",
    "City",
    "District",
    "Phone",
    "Email",
    "Website",
    "Praxisplan Profile URL",
    "Source URL",
    "Source",
    "Outreach Status",
    "Call Attempt 1 Date",
    "Call Attempt 1 Result",
    "Call Attempt 2 Date",
    "Call Attempt 2 Result",
    "Email Sent Date",
    "Email Result",
    "Walk-in Date",
    "Walk-in Result",
    "Contact Person",
    "Best Time to Call",
    "Follow-up Date",
    "Demo Offered",
    "Demo Booked",
    "Demo Date",
    "Pilot Interest",
    "Objection",
    "Next Action",
    "Notes",
    "Last Updated",
    "Priority Score",
    "Priority Reason",
    "Existing System Mentioned",
    "Likely LATIDO / Online Booking",
    "Sub-specialty / Notes from Listing",
]


def test_columns_list_present() -> None:
    assert "COLUMNS" in _script(), \
        "script must define a COLUMNS list"


def test_required_column_outreach_status() -> None:
    assert '"Outreach Status"' in _script() or "'Outreach Status'" in _script(), \
        "COLUMNS must include 'Outreach Status'"


def test_required_column_call_attempt_1() -> None:
    assert "Call Attempt 1" in _script(), \
        "COLUMNS must include 'Call Attempt 1 Date' and 'Call Attempt 1 Result'"


def test_required_column_call_attempt_2() -> None:
    assert "Call Attempt 2" in _script(), \
        "COLUMNS must include 'Call Attempt 2 Date' and 'Call Attempt 2 Result'"


def test_required_column_demo_booked() -> None:
    assert "Demo Booked" in _script(), \
        "COLUMNS must include 'Demo Booked'"


def test_required_column_follow_up_date() -> None:
    assert "Follow-up Date" in _script(), \
        "COLUMNS must include 'Follow-up Date'"


def test_required_column_notes() -> None:
    assert '"Notes"' in _script() or "'Notes'" in _script(), \
        "COLUMNS must include 'Notes'"


def test_required_column_pilot_interest() -> None:
    assert "Pilot Interest" in _script(), \
        "COLUMNS must include 'Pilot Interest'"


def test_required_column_priority_score() -> None:
    assert "Priority Score" in _script(), \
        "COLUMNS must include 'Priority Score'"


def test_required_column_phone() -> None:
    assert '"Phone"' in _script() or "'Phone'" in _script(), \
        "COLUMNS must include 'Phone'"


def test_required_column_email() -> None:
    assert '"Email"' in _script() or "'Email'" in _script(), \
        "COLUMNS must include 'Email'"


def test_required_column_website() -> None:
    assert '"Website"' in _script() or "'Website'" in _script(), \
        "COLUMNS must include 'Website'"


def test_required_column_lead_id() -> None:
    assert "Lead ID" in _script(), \
        "COLUMNS must include 'Lead ID'"


def test_required_column_district() -> None:
    assert "District" in _script(), \
        "COLUMNS must include 'District'"


# ---------------------------------------------------------------------------
# 3. Dropdown / status values defined
# ---------------------------------------------------------------------------

def test_outreach_status_values_defined() -> None:
    content = _script()
    assert "Not contacted" in content, "script must define 'Not contacted' status"
    assert "Do not contact" in content, "script must define 'Do not contact' status"
    assert "Demo booked" in content, "script must define 'Demo booked' status"


def test_call_result_values_defined() -> None:
    content = _script()
    assert "No answer" in content, "script must define 'No answer' call result"
    assert "Reception reached" in content, "script must define 'Reception reached' call result"


def test_email_result_values_defined() -> None:
    content = _script()
    assert "Replied interested" in content, "script must define email result values"
    assert "Bounced" in content, "script must define 'Bounced' email result"


def test_walk_in_result_values_defined() -> None:
    content = _script()
    assert "Left flyer" in content, "script must define 'Left flyer' walk-in result"
    assert "Reception conversation" in content, "script must define 'Reception conversation'"


def test_demo_yn_values_defined() -> None:
    content = _script()
    assert "DEMO_YN" in content or ('"Yes"' in content and '"No"' in content), \
        "script must define Yes/No values for Demo Offered and Demo Booked"


def test_pilot_interest_values_defined() -> None:
    content = _script()
    assert "Unknown" in content and "High" in content and "Not interested" in content, \
        "script must define pilot interest levels"


def test_priority_score_values_defined() -> None:
    content = _script()
    assert "PRIORITY_SCORE" in content or "'1'" in content, \
        "script must define priority score values"


# ---------------------------------------------------------------------------
# 4. Rate limiting
# ---------------------------------------------------------------------------

def test_rate_limiting_present() -> None:
    content = _script()
    assert "sleep" in content, "script must use time.sleep() for rate limiting"
    assert "1.5" in content or "REQUEST_DELAY" in content, \
        "script must enforce minimum 1.5s delay between requests"


def test_rate_limiting_no_parallelism() -> None:
    content = _script()
    assert "ThreadPool" not in content, "script must not use ThreadPool (parallel requests)"
    assert "asyncio" not in content, "script must not use asyncio (parallel requests)"


# ---------------------------------------------------------------------------
# 5. Deduplication
# ---------------------------------------------------------------------------

def test_deduplication_present() -> None:
    content = _script()
    assert "seen" in content or "dedup" in content or "deduplicate" in content, \
        "script must deduplicate records"


def test_deduplication_by_name_and_phone() -> None:
    content = _script()
    assert "Doctor Name" in content and "Phone" in content and "seen" in content, \
        "deduplication should reference Doctor Name and Phone"


# ---------------------------------------------------------------------------
# 6. Export functions
# ---------------------------------------------------------------------------

def test_csv_export_present() -> None:
    content = _script()
    assert "save_csv" in content or "csv.DictWriter" in content or ".csv" in content, \
        "script must export CSV"


def test_xlsx_export_present() -> None:
    content = _script()
    assert "save_xlsx" in content or "openpyxl" in content or ".xlsx" in content, \
        "script must export XLSX"


def test_xlsx_uses_openpyxl() -> None:
    assert "openpyxl" in _script(), \
        "XLSX export must use openpyxl"


# ---------------------------------------------------------------------------
# 7. Mode A and Mode B support
# ---------------------------------------------------------------------------

def test_mode_a_url_argument() -> None:
    content = _script()
    assert "--url" in content, "script must support --url argument (Mode A)"


def test_mode_b_input_html_argument() -> None:
    content = _script()
    assert "--input-html" in content or "input_html" in content or "input-html" in content, \
        "script must support --input-html argument (Mode B)"


def test_template_only_mode() -> None:
    assert "--template-only" in _script() or "template_only" in _script(), \
        "script must support --template-only mode"


# ---------------------------------------------------------------------------
# 8. No secrets / no auto-actions
# ---------------------------------------------------------------------------

def test_no_database_url_in_script() -> None:
    assert "DATABASE_URL" not in _script(), \
        "script must not contain DATABASE_URL"


def test_no_jwt_secret_in_script() -> None:
    content = _script().lower()
    assert "jwt_secret" not in content and "secret_key" not in content, \
        "script must not contain JWT or secret key references"


def test_no_vapi_api_key_in_script() -> None:
    content = _script().lower()
    assert "vapi_api_key" not in content and "vapi_secret" not in content, \
        "script must not contain Vapi API key"


def test_no_webhook_secret_in_script() -> None:
    content = _script().lower()
    assert "webhook_secret" not in content, \
        "script must not contain webhook secret"


def test_no_auto_email_sending() -> None:
    content = _script().lower()
    assert "smtplib" not in content and "sendmail" not in content and "send_email" not in content, \
        "script must not auto-send emails"


def test_no_auto_calling() -> None:
    content = _script().lower()
    # Check for actual auto-call libraries/imports, not comments/docs that mention the restriction
    assert "import twilio" not in content and "from twilio" not in content, \
        "script must not import Twilio (auto-calling)"
    assert "autodial" not in content and "robo_call" not in content, \
        "script must not use auto-dialing functions"


def test_no_api_key_literals() -> None:
    content = _script()
    import re
    api_key_pattern = re.compile(r'["\']([A-Za-z0-9]{32,})["\']')
    matches = api_key_pattern.findall(content)
    assert not matches, f"script must not contain hardcoded API key literals: {matches[:3]}"


# ---------------------------------------------------------------------------
# 9. README responsible outreach content
# ---------------------------------------------------------------------------

def test_readme_mentions_public_contact_only() -> None:
    content = _readme().lower()
    assert "public" in content and "contact" in content, \
        "README must mention public practice contact details only"


def test_readme_mentions_no_mass_spam() -> None:
    content = _readme().lower()
    assert "mass" in content or "bulk" in content or "automated" in content, \
        "README must mention no mass-spam / no automated outreach"


def test_readme_mentions_do_not_contact() -> None:
    content = _readme()
    assert "Do not contact" in content or "opt-out" in content.lower() or "opt out" in content.lower(), \
        "README must mention 'Do not contact' / opt-out"


def test_readme_mentions_no_patient_data() -> None:
    content = _readme().lower()
    assert "patient" in content and ("no" in content or "not" in content), \
        "README must mention no patient data"


def test_readme_mentions_no_phi() -> None:
    content = _readme().upper()
    assert "PHI" in content, \
        "README must mention PHI boundary"


def test_readme_mentions_no_auto_email() -> None:
    content = _readme().lower()
    assert "automated" in content or "auto" in content or "mass" in content, \
        "README must mention no automated emailing"


def test_readme_mentions_opt_out() -> None:
    content = _readme().lower()
    assert "opt-out" in content or "do not contact" in content or "nicht mehr kontaktier" in content, \
        "README must mention opt-out / do not contact rule"


def test_readme_source_is_praxisplan() -> None:
    assert "praxisplan" in _readme().lower(), \
        "README must mention Praxisplan as source"


def test_readme_is_sales_tracker_not_product_db() -> None:
    content = _readme().lower()
    assert "tracker" in content or "outreach" in content, \
        "README must clarify this is a sales tracker"


# ---------------------------------------------------------------------------
# 10. CSV column verification
# ---------------------------------------------------------------------------

def test_csv_has_required_columns() -> None:
    import csv
    csv_file = _LEADS_CSV if os.path.isfile(_LEADS_CSV) else _TEMPLATE_CSV
    with open(csv_file, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []

    required = [
        "Lead ID", "Doctor Name", "Phone", "Email", "Website",
        "Outreach Status", "Demo Booked", "Follow-up Date", "Notes",
        "Priority Score", "Pilot Interest",
    ]
    for col in required:
        assert col in fieldnames, f"CSV must have column '{col}'"


def test_csv_outreach_status_default() -> None:
    import csv
    csv_file = _LEADS_CSV if os.path.isfile(_LEADS_CSV) else _TEMPLATE_CSV
    with open(csv_file, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if rows:
        assert rows[0].get("Outreach Status") == "Not contacted", \
            "Default Outreach Status must be 'Not contacted'"


def test_csv_source_default() -> None:
    import csv
    csv_file = _LEADS_CSV if os.path.isfile(_LEADS_CSV) else _TEMPLATE_CSV
    with open(csv_file, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if rows:
        assert rows[0].get("Source") == "Praxisplan", \
            "Source column default must be 'Praxisplan'"


def test_csv_demo_offered_default() -> None:
    import csv
    csv_file = _LEADS_CSV if os.path.isfile(_LEADS_CSV) else _TEMPLATE_CSV
    with open(csv_file, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if rows:
        assert rows[0].get("Demo Offered") == "No", \
            "Demo Offered default must be 'No'"


def test_csv_no_real_patient_data() -> None:
    import csv
    csv_file = _LEADS_CSV if os.path.isfile(_LEADS_CSV) else _TEMPLATE_CSV
    with open(csv_file, encoding="utf-8-sig") as f:
        content = f.read().lower()
    # These should never appear in a sales lead tracker
    assert "patient_id" not in content, "CSV must not contain patient_id"
    assert "diagnosis" not in content, "CSV must not contain diagnosis data"
    assert "medical record" not in content, "CSV must not contain medical records"


def test_csv_has_rows() -> None:
    import csv
    csv_file = _LEADS_CSV if os.path.isfile(_LEADS_CSV) else _TEMPLATE_CSV
    with open(csv_file, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) >= 1, "CSV must have at least one data row"


# ---------------------------------------------------------------------------
# 11. Safety invariants
# ---------------------------------------------------------------------------

def test_script_no_diagnosis() -> None:
    assert "diagnosis" not in _script().lower(), \
        "script must not reference diagnosis"


def test_script_no_medical_advice() -> None:
    assert "medical advice" not in _script().lower(), \
        "script must not contain medical advice"


def test_script_no_triage() -> None:
    assert "triage" not in _script().lower(), \
        "script must not contain triage logic"


def test_script_no_production_phi() -> None:
    assert "production_phi_enabled" not in _script().lower(), \
        "script must not reference production_phi_enabled (sales tool, not product code)"


def test_script_public_contact_only() -> None:
    content = _script()
    assert "public" in content.lower() or "publicly" in content.lower(), \
        "script must state it collects only public contact details"


def test_script_rate_limit_comment() -> None:
    content = _script()
    assert "rate" in content.lower() or "REQUEST_DELAY" in content, \
        "script must reference rate limiting"


def test_script_praxisplan_base_url() -> None:
    assert "praxisplan.at" in _script(), \
        "script must reference praxisplan.at as the data source"
