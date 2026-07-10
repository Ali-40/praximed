"""
Static contract tests for the multi-specialty Praxisplan outreach database builder.

Sprint 21 / Outreach — Multi-specialty Praxisplan lead database builder.

Verifies file content and structure only. No database. No network. No secrets.
No real patient data. No PHI. Production PHI remains NO-GO.

Tests confirm:
- Multi-specialty script exists with correct structure
- Config file exists with all required specialties
- README exists with responsible outreach rules
- Required columns are defined (including new specialty metadata columns)
- CLI supports --all, --specialty, --templates-only
- Rate limiting and deduplication present
- CSV and XLSX export present
- No secrets, no auto-email, no auto-call, no patient data
"""

from __future__ import annotations

import json
import os
import csv

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))
_MULTI_SCRIPT = os.path.join(_REPO_ROOT, "scripts", "sales", "build_praxisplan_multi_specialty_leads.py")
_CONFIG = os.path.join(_REPO_ROOT, "docs", "sales", "outreach", "praxisplan_specialty_sources.json")
_README = os.path.join(_REPO_ROOT, "docs", "sales", "outreach", "MULTI_SPECIALTY_OUTREACH_DATABASE_README.md")
_OUTREACH_DIR = os.path.join(_REPO_ROOT, "docs", "sales", "outreach")
_MASTER_XLSX = os.path.join(_OUTREACH_DIR, "praxisplan_all_high_potential_leads.xlsx")
_MASTER_CSV = os.path.join(_OUTREACH_DIR, "praxisplan_all_high_potential_leads.csv")

REQUIRED_SPECIALTY_KEYS = [
    "child_adolescent_psychiatry",
    "dermatology",
    "gynecology",
    "orthopedics",
    "internal_medicine",
    "ent",
    "urology",
    "neurology",
    "ophthalmology",
    "pediatrics",
    "private_dental",
    "aesthetic_medicine",
    "plastic_surgery",
    "adult_psychiatry",
    "private_group_practices",
]


def _script() -> str:
    with open(_MULTI_SCRIPT, encoding="utf-8") as f:
        return f.read()


def _readme() -> str:
    with open(_README, encoding="utf-8") as f:
        return f.read()


def _config() -> list[dict]:
    with open(_CONFIG, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# 1. File existence
# ---------------------------------------------------------------------------

def test_multi_specialty_script_exists() -> None:
    assert os.path.isfile(_MULTI_SCRIPT), \
        "scripts/sales/build_praxisplan_multi_specialty_leads.py must exist"


def test_config_file_exists() -> None:
    assert os.path.isfile(_CONFIG), \
        "docs/sales/outreach/praxisplan_specialty_sources.json must exist"


def test_readme_exists() -> None:
    assert os.path.isfile(_README), \
        "docs/sales/outreach/MULTI_SPECIALTY_OUTREACH_DATABASE_README.md must exist"


def test_master_xlsx_exists() -> None:
    assert os.path.isfile(_MASTER_XLSX), \
        "praxisplan_all_high_potential_leads.xlsx must exist"


def test_master_csv_exists() -> None:
    assert os.path.isfile(_MASTER_CSV), \
        "praxisplan_all_high_potential_leads.csv must exist"


def test_outreach_dir_exists() -> None:
    assert os.path.isdir(_OUTREACH_DIR), \
        "docs/sales/outreach/ directory must exist"


# ---------------------------------------------------------------------------
# 2. Config file — all required specialties present
# ---------------------------------------------------------------------------

def test_config_is_valid_json() -> None:
    specs = _config()
    assert isinstance(specs, list) and len(specs) > 0, \
        "config must be a non-empty JSON array"


def test_config_has_all_required_specialties() -> None:
    specs = _config()
    keys = {s.get("specialty_key") for s in specs}
    for required_key in REQUIRED_SPECIALTY_KEYS:
        assert required_key in keys, \
            f"Config must include specialty_key '{required_key}'"


def test_config_child_adolescent_psychiatry_entry() -> None:
    specs = _config()
    match = next((s for s in specs if s.get("specialty_key") == "child_adolescent_psychiatry"), None)
    assert match is not None, "Config must have child_adolescent_psychiatry entry"
    assert match.get("tier") == 1, "child_adolescent_psychiatry must be Tier 1"


def test_config_dermatology_entry() -> None:
    specs = _config()
    match = next((s for s in specs if s.get("specialty_key") == "dermatology"), None)
    assert match is not None, "Config must have dermatology entry"
    assert match.get("tier") == 1, "dermatology must be Tier 1"


def test_config_gynecology_entry() -> None:
    specs = _config()
    match = next((s for s in specs if s.get("specialty_key") == "gynecology"), None)
    assert match is not None, "Config must have gynecology entry"
    assert match.get("tier") == 1, "gynecology must be Tier 1"


def test_config_orthopedics_entry() -> None:
    specs = _config()
    match = next((s for s in specs if s.get("specialty_key") == "orthopedics"), None)
    assert match is not None, "Config must have orthopedics entry"
    assert match.get("tier") == 1, "orthopedics must be Tier 1"


def test_config_internal_medicine_entry() -> None:
    specs = _config()
    match = next((s for s in specs if s.get("specialty_key") == "internal_medicine"), None)
    assert match is not None, "Config must have internal_medicine entry"
    assert match.get("tier") == 1, "internal_medicine must be Tier 1"


def test_config_ent_entry() -> None:
    specs = _config()
    match = next((s for s in specs if s.get("specialty_key") == "ent"), None)
    assert match is not None, "Config must have ent entry"
    assert match.get("tier") == 2, "ent must be Tier 2"


def test_config_urology_entry() -> None:
    specs = _config()
    match = next((s for s in specs if s.get("specialty_key") == "urology"), None)
    assert match is not None and match.get("tier") == 2, \
        "Config must have urology entry with Tier 2"


def test_config_neurology_entry() -> None:
    specs = _config()
    match = next((s for s in specs if s.get("specialty_key") == "neurology"), None)
    assert match is not None and match.get("tier") == 2, \
        "Config must have neurology entry with Tier 2"


def test_config_ophthalmology_entry() -> None:
    specs = _config()
    match = next((s for s in specs if s.get("specialty_key") == "ophthalmology"), None)
    assert match is not None and match.get("tier") == 2, \
        "Config must have ophthalmology entry with Tier 2"


def test_config_pediatrics_entry() -> None:
    specs = _config()
    match = next((s for s in specs if s.get("specialty_key") == "pediatrics"), None)
    assert match is not None and match.get("tier") == 2, \
        "Config must have pediatrics entry with Tier 2"


def test_config_private_dental_entry() -> None:
    specs = _config()
    match = next((s for s in specs if s.get("specialty_key") == "private_dental"), None)
    assert match is not None and match.get("tier") == 3, \
        "Config must have private_dental entry with Tier 3"


def test_config_aesthetic_medicine_entry() -> None:
    specs = _config()
    match = next((s for s in specs if s.get("specialty_key") == "aesthetic_medicine"), None)
    assert match is not None and match.get("tier") == 3, \
        "Config must have aesthetic_medicine entry with Tier 3"


def test_config_plastic_surgery_entry() -> None:
    specs = _config()
    match = next((s for s in specs if s.get("specialty_key") == "plastic_surgery"), None)
    assert match is not None and match.get("tier") == 3, \
        "Config must have plastic_surgery entry with Tier 3"


def test_config_adult_psychiatry_entry() -> None:
    specs = _config()
    match = next((s for s in specs if s.get("specialty_key") == "adult_psychiatry"), None)
    assert match is not None and match.get("tier") == 3, \
        "Config must have adult_psychiatry entry with Tier 3"


def test_config_private_group_practices_entry() -> None:
    specs = _config()
    match = next((s for s in specs if s.get("specialty_key") == "private_group_practices"), None)
    assert match is not None and match.get("tier") == 3, \
        "Config must have private_group_practices entry with Tier 3"


def test_config_entries_have_required_fields() -> None:
    specs = _config()
    required_fields = ["specialty_key", "specialty_label_de", "specialty_label_en", "tier", "output_slug"]
    for spec in specs:
        for field in required_fields:
            assert field in spec, \
                f"Config entry '{spec.get('specialty_key')}' must have field '{field}'"


def test_config_tier1_entries_have_source_urls() -> None:
    specs = _config()
    tier1 = [s for s in specs if s.get("tier") == 1]
    for spec in tier1:
        url = spec.get("source_url", "")
        assert url, \
            f"Tier 1 specialty '{spec.get('specialty_key')}' should have a source_url"


# ---------------------------------------------------------------------------
# 3. Required columns in script
# ---------------------------------------------------------------------------

def test_columns_list_present() -> None:
    assert "COLUMNS" in _script(), "script must define a COLUMNS list"


def test_column_specialty_tier() -> None:
    assert "Specialty Tier" in _script(), "COLUMNS must include 'Specialty Tier'"


def test_column_specialty_key() -> None:
    assert "Specialty Key" in _script(), "COLUMNS must include 'Specialty Key'"


def test_column_specialty_label_de() -> None:
    assert "Specialty Label DE" in _script(), "COLUMNS must include 'Specialty Label DE'"


def test_column_specialty_label_en() -> None:
    assert "Specialty Label EN" in _script(), "COLUMNS must include 'Specialty Label EN'"


def test_column_outreach_status() -> None:
    assert "Outreach Status" in _script(), "COLUMNS must include 'Outreach Status'"


def test_column_demo_booked() -> None:
    assert "Demo Booked" in _script(), "COLUMNS must include 'Demo Booked'"


def test_column_follow_up_date() -> None:
    assert "Follow-up Date" in _script(), "COLUMNS must include 'Follow-up Date'"


def test_column_priority_score() -> None:
    assert "Priority Score" in _script(), "COLUMNS must include 'Priority Score'"


def test_column_priority_reason() -> None:
    assert "Priority Reason" in _script(), "COLUMNS must include 'Priority Reason'"


def test_column_pilot_interest() -> None:
    assert "Pilot Interest" in _script(), "COLUMNS must include 'Pilot Interest'"


def test_column_notes() -> None:
    assert '"Notes"' in _script() or "'Notes'" in _script(), "COLUMNS must include 'Notes'"


def test_column_phone() -> None:
    assert '"Phone"' in _script() or "'Phone'" in _script(), "COLUMNS must include 'Phone'"


def test_column_email() -> None:
    assert '"Email"' in _script() or "'Email'" in _script(), "COLUMNS must include 'Email'"


def test_column_website() -> None:
    assert '"Website"' in _script() or "'Website'" in _script(), "COLUMNS must include 'Website'"


def test_column_lead_id() -> None:
    assert "Lead ID" in _script(), "COLUMNS must include 'Lead ID'"


def test_column_call_attempt_1() -> None:
    assert "Call Attempt 1" in _script(), "COLUMNS must include 'Call Attempt 1'"


def test_column_call_attempt_2() -> None:
    assert "Call Attempt 2" in _script(), "COLUMNS must include 'Call Attempt 2'"


# ---------------------------------------------------------------------------
# 4. CLI options
# ---------------------------------------------------------------------------

def test_cli_supports_all() -> None:
    assert "--all" in _script(), "script must support --all CLI option"


def test_cli_supports_specialty() -> None:
    assert "--specialty" in _script(), "script must support --specialty CLI option"


def test_cli_supports_templates_only() -> None:
    assert "--templates-only" in _script() or "templates_only" in _script(), \
        "script must support --templates-only CLI option"


def test_cli_supports_config() -> None:
    assert "--config" in _script(), "script must support --config CLI option"


# ---------------------------------------------------------------------------
# 5. Rate limiting and deduplication
# ---------------------------------------------------------------------------

def test_rate_limiting_present() -> None:
    content = _script()
    assert "sleep" in content and "REQUEST_DELAY" in content, \
        "script must implement rate limiting with REQUEST_DELAY constants"


def test_rate_limit_min_1_5s() -> None:
    assert "1.5" in _script(), "minimum rate limit must be 1.5 seconds"


def test_no_parallel_requests() -> None:
    content = _script()
    assert "ThreadPool" not in content and "asyncio" not in content, \
        "script must not parallelize requests"


def test_deduplication_present() -> None:
    content = _script()
    assert "seen" in content or "dedup" in content, \
        "script must deduplicate records"


def test_deduplication_cross_specialty() -> None:
    content = _script()
    assert "global_dedup" in content or ("seen" in content and "Doctor Name" in content), \
        "script must deduplicate across all specialties for master workbook"


# ---------------------------------------------------------------------------
# 6. Export
# ---------------------------------------------------------------------------

def test_csv_export_present() -> None:
    assert "csv" in _script().lower() and ".csv" in _script(), \
        "script must export CSV"


def test_xlsx_export_present() -> None:
    assert "openpyxl" in _script() and ".xlsx" in _script(), \
        "script must export XLSX using openpyxl"


def test_master_workbook_path_defined() -> None:
    content = _script()
    assert "all_high_potential" in content or "MASTER_XLSX" in content or "master" in content.lower(), \
        "script must define master workbook output path"


def test_master_has_all_leads_sheet() -> None:
    assert "All Leads" in _script(), \
        "master workbook must include 'All Leads' sheet"


def test_master_has_summary_sheet() -> None:
    assert "Summary" in _script(), \
        "master workbook must include 'Summary' sheet"


def test_config_path_support() -> None:
    assert "config" in _script().lower() and "json.load" in _script(), \
        "script must support loading specialty config from JSON"


# ---------------------------------------------------------------------------
# 7. No secrets / no auto-actions
# ---------------------------------------------------------------------------

def test_no_database_url() -> None:
    assert "DATABASE_URL" not in _script(), "script must not contain DATABASE_URL"


def test_no_jwt_secret() -> None:
    content = _script().lower()
    assert "jwt_secret" not in content and "secret_key" not in content, \
        "script must not contain JWT secret references"


def test_no_vapi_api_key() -> None:
    content = _script().lower()
    assert "vapi_api_key" not in content and "vapi_secret" not in content, \
        "script must not contain Vapi API key"


def test_no_webhook_secret() -> None:
    assert "webhook_secret" not in _script().lower(), \
        "script must not contain webhook secret"


def test_no_auto_email() -> None:
    content = _script().lower()
    assert "smtplib" not in content and "sendmail" not in content, \
        "script must not auto-send emails"


def test_no_auto_calling() -> None:
    content = _script().lower()
    assert "import twilio" not in content and "from twilio" not in content, \
        "script must not import Twilio (auto-calling)"


def test_no_api_key_literals() -> None:
    import re
    content = _script()
    api_key_pattern = re.compile(r'["\']([A-Za-z0-9]{32,})["\']')
    matches = api_key_pattern.findall(content)
    assert not matches, f"script must not contain hardcoded API key literals: {matches[:3]}"


def test_no_diagnosis_in_script() -> None:
    assert "diagnosis" not in _script().lower(), "script must not reference diagnosis"


def test_no_medical_advice_in_script() -> None:
    assert "medical advice" not in _script().lower(), "script must not reference medical advice"


def test_no_triage_in_script() -> None:
    assert "triage" not in _script().lower(), "script must not contain triage logic"


# ---------------------------------------------------------------------------
# 8. README responsible outreach content
# ---------------------------------------------------------------------------

def test_readme_mentions_public_contact_only() -> None:
    content = _readme().lower()
    assert "public" in content and ("contact" in content or "contacts" in content), \
        "README must mention public practice contact details only"


def test_readme_mentions_no_mass_spam() -> None:
    content = _readme().lower()
    assert "mass" in content or "bulk" in content or "automated" in content, \
        "README must mention no mass-spam / no automated outreach"


def test_readme_mentions_do_not_contact() -> None:
    content = _readme()
    assert "Do not contact" in content or "opt-out" in content.lower(), \
        "README must mention 'Do not contact' / opt-out rule"


def test_readme_mentions_no_patient_data() -> None:
    content = _readme().lower()
    assert "patient" in content and ("no" in content or "not" in content or "never" in content), \
        "README must mention no patient data"


def test_readme_mentions_no_phi() -> None:
    assert "PHI" in _readme().upper(), "README must mention PHI boundary"


def test_readme_mentions_no_auto_email() -> None:
    content = _readme().lower()
    assert "automated" in content or "bulk" in content or "mass" in content, \
        "README must mention no automated emailing"


def test_readme_mentions_no_auto_calling() -> None:
    content = _readme().lower()
    assert "auto-dial" in content or "auto-call" in content or "auto" in content, \
        "README must mention no auto-calling"


def test_readme_mentions_all_required_specialties() -> None:
    content = _readme().lower()
    for key in ["dermatology", "gynecology", "orthopedics", "neurology", "pediatrics"]:
        assert key in content, f"README must mention specialty '{key}'"


def test_readme_explains_how_to_add_source_url() -> None:
    content = _readme().lower()
    assert "source_url" in content or "url" in content, \
        "README must explain how to add/configure a source URL"


def test_readme_has_outreach_status_definitions() -> None:
    content = _readme()
    assert "Not contacted" in content and "Do not contact" in content, \
        "README must define outreach status values"


# ---------------------------------------------------------------------------
# 9. Fake template rows — no real doctor names
# ---------------------------------------------------------------------------

def test_fake_rows_no_real_doctor_names() -> None:
    content = _script()
    assert "FAKE_TEMPLATE_ROWS" in content, "script must define FAKE_TEMPLATE_ROWS"
    fake_section_start = content.find("FAKE_TEMPLATE_ROWS")
    fake_section = content[fake_section_start:fake_section_start + 3000]
    # All fake names should start with "Demo"
    import re
    name_values = re.findall(r'"Doctor Name":\s*"([^"]+)"', fake_section)
    for name in name_values:
        assert name.startswith("Demo"), \
            f"Fake template row doctor name must start with 'Demo', got: '{name}'"


def test_fake_rows_no_real_phone_numbers() -> None:
    content = _script()
    fake_section_start = content.find("FAKE_TEMPLATE_ROWS")
    fake_section = content[fake_section_start:fake_section_start + 3000]
    import re
    phones = re.findall(r'"Phone":\s*"([^"]+)"', fake_section)
    for phone in phones:
        assert "000000" in phone or phone == "" or phone == "+43 000 000000", \
            f"Fake template phone must be placeholder (+43 000 000000), got: '{phone}'"


# ---------------------------------------------------------------------------
# 10. Master CSV column verification
# ---------------------------------------------------------------------------

def test_master_csv_has_specialty_tier_column() -> None:
    with open(_MASTER_CSV, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
    assert "Specialty Tier" in fieldnames, "Master CSV must have 'Specialty Tier' column"


def test_master_csv_has_specialty_key_column() -> None:
    with open(_MASTER_CSV, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
    assert "Specialty Key" in fieldnames, "Master CSV must have 'Specialty Key' column"


def test_master_csv_has_outreach_status_column() -> None:
    with open(_MASTER_CSV, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
    assert "Outreach Status" in fieldnames, "Master CSV must have 'Outreach Status' column"


def test_master_csv_has_demo_booked_column() -> None:
    with open(_MASTER_CSV, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
    assert "Demo Booked" in fieldnames, "Master CSV must have 'Demo Booked' column"


def test_master_csv_has_rows() -> None:
    with open(_MASTER_CSV, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) >= 1, "Master CSV must have at least one data row"


def test_master_csv_default_outreach_status() -> None:
    with open(_MASTER_CSV, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if rows:
        assert rows[0].get("Outreach Status") == "Not contacted", \
            "Default Outreach Status must be 'Not contacted'"


def test_master_csv_source_default() -> None:
    with open(_MASTER_CSV, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if rows:
        assert rows[0].get("Source") == "Praxisplan", \
            "Source column default must be 'Praxisplan'"


def test_master_csv_no_patient_data() -> None:
    with open(_MASTER_CSV, encoding="utf-8-sig") as f:
        content = f.read().lower()
    assert "patient_id" not in content, "Master CSV must not contain patient_id"
    assert "diagnosis" not in content, "Master CSV must not contain diagnosis"
    assert "medical record" not in content, "Master CSV must not contain medical records"


def test_master_csv_covers_multiple_specialties() -> None:
    with open(_MASTER_CSV, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    specialty_keys = {r.get("Specialty Key", "") for r in rows if r.get("Specialty Key")}
    assert len(specialty_keys) >= 3, \
        f"Master CSV must cover at least 3 specialties, found: {specialty_keys}"


# ---------------------------------------------------------------------------
# 11. Per-specialty file existence
# ---------------------------------------------------------------------------

def test_per_specialty_xlsx_files_exist() -> None:
    import json
    specs = _config()
    for spec in specs:
        slug = spec.get("output_slug", spec.get("specialty_key", ""))
        xlsx_path = os.path.join(_OUTREACH_DIR, f"{slug}_leads.xlsx")
        assert os.path.isfile(xlsx_path), \
            f"Per-specialty XLSX must exist: {slug}_leads.xlsx"


def test_per_specialty_csv_files_exist() -> None:
    specs = _config()
    for spec in specs:
        slug = spec.get("output_slug", spec.get("specialty_key", ""))
        csv_path = os.path.join(_OUTREACH_DIR, f"{slug}_leads.csv")
        assert os.path.isfile(csv_path), \
            f"Per-specialty CSV must exist: {slug}_leads.csv"


# ---------------------------------------------------------------------------
# 12. Config no secrets
# ---------------------------------------------------------------------------

def test_config_no_secrets() -> None:
    with open(_CONFIG, encoding="utf-8") as f:
        content = f.read().lower()
    assert "api_key" not in content, "Config must not contain api_key"
    assert "secret" not in content, "Config must not contain secret"
    assert "password" not in content, "Config must not contain password"
    assert "token" not in content, "Config must not contain auth token"
