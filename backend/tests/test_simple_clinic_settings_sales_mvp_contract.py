"""
Static contract tests for Sprint 21 / Module 159 — Simple Clinic Settings.

Verifies file content only. No JS/TS runtime. No database. No network. No secrets.
No real patient data. No PHI. Production PHI remains NO-GO.

These tests confirm that:
- The Einstellungen tab contains all required clinic-facing settings fields
- AI tone selector and KI-Vorschau exist with correct content
- No technical fields are exposed to clinic users
- No appointment auto-confirmation is promised
- No diagnosis, medical advice, or triage scoring appears
- All safety boundaries from Module 157/158 remain intact
"""

from __future__ import annotations

import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))
FRONTEND = os.path.join(_REPO_ROOT, "frontend")


def _read_frontend(rel: str) -> str:
    with open(os.path.join(FRONTEND, rel), encoding="utf-8") as f:
        return f.read()


def _dashboard() -> str:
    return _read_frontend("app/dashboard/page.tsx")


# ---------------------------------------------------------------------------
# 1. Dashboard and Einstellungen tab exist
# ---------------------------------------------------------------------------

def test_dashboard_file_exists() -> None:
    assert os.path.isfile(os.path.join(FRONTEND, "app", "dashboard", "page.tsx")), \
        "frontend/app/dashboard/page.tsx must exist"


def test_dashboard_has_einstellungen_tab() -> None:
    assert "Einstellungen" in _dashboard(), \
        "dashboard must have an Einstellungen tab"


def test_dashboard_settings_subtitle_is_german() -> None:
    assert "Passen Sie an" in _dashboard(), \
        "settings tab must have German subtitle starting with 'Passen Sie an'"


# ---------------------------------------------------------------------------
# 2. Praxisprofil fields
# ---------------------------------------------------------------------------

def test_settings_has_praxisname_field() -> None:
    assert "Praxisname" in _dashboard(), \
        "settings must include Praxisname field"


def test_settings_has_arzt_field() -> None:
    content = _dashboard()
    assert "Arzt" in content or "Ärztin" in content, \
        "settings must include Arzt / Ärztin field"


def test_settings_has_fachrichtung_field() -> None:
    assert "Fachrichtung" in _dashboard(), \
        "settings must include Fachrichtung field"


def test_settings_has_ort_field() -> None:
    assert "Ort" in _dashboard(), \
        "settings must include Ort field"


def test_settings_has_telefonnummer_field() -> None:
    assert "Telefonnummer" in _dashboard(), \
        "settings must include Telefonnummer field"


# ---------------------------------------------------------------------------
# 3. Öffnungszeiten section
# ---------------------------------------------------------------------------

def test_settings_has_oeffnungszeiten_section() -> None:
    assert "Öffnungszeiten" in _dashboard(), \
        "settings must include Öffnungszeiten section"


# ---------------------------------------------------------------------------
# 4. Sprachen section
# ---------------------------------------------------------------------------

def test_settings_has_sprachen_section() -> None:
    assert "Sprachen" in _dashboard(), \
        "settings must include Sprachen section"


def test_settings_includes_deutsch_language() -> None:
    assert "Deutsch" in _dashboard(), \
        "settings must include Deutsch language option"


def test_settings_includes_englisch_language() -> None:
    assert "Englisch" in _dashboard(), \
        "settings must include Englisch language option"


# ---------------------------------------------------------------------------
# 5. KI-Rezeption and KI-Vorschau
# ---------------------------------------------------------------------------

def test_settings_has_ki_rezeption_section() -> None:
    assert "KI-Rezeption" in _dashboard(), \
        "settings must include KI-Rezeption section"


def test_settings_has_ki_vorschau() -> None:
    assert "KI-Vorschau" in _dashboard(), \
        "settings must include KI-Vorschau preview card"


def test_settings_tone_freundlich_und_ruhig() -> None:
    assert "Freundlich und ruhig" in _dashboard(), \
        "settings must include 'Freundlich und ruhig' tone option"


def test_settings_tone_kurz_und_direkt() -> None:
    assert "Kurz und direkt" in _dashboard(), \
        "settings must include 'Kurz und direkt' tone option"


def test_settings_tone_sehr_formell() -> None:
    assert "Sehr formell" in _dashboard(), \
        "settings must include 'Sehr formell' tone option"


def test_settings_preview_mentions_praxisteam() -> None:
    content = _dashboard()
    assert "Praxisteam" in content, \
        "KI-Vorschau must mention 'Praxisteam' confirming callback"


def test_settings_preview_no_appointment_confirmation_promise() -> None:
    content = _dashboard()
    assert "Termin bestätigt" not in content, \
        "KI-Vorschau must not promise 'Termin bestätigt'"
    assert "appointment confirmed" not in content.lower(), \
        "KI-Vorschau must not promise appointment confirmed"
    assert "Kein automatischer Terminabschluss" in content, \
        "settings must clarify no automatic appointment confirmation"


def test_settings_preview_no_medical_advice_promise() -> None:
    content = _dashboard()
    assert "medizinische Beratung" not in content, \
        "KI-Vorschau must not promise medical advice"


# ---------------------------------------------------------------------------
# 6. Save and reset controls
# ---------------------------------------------------------------------------

def test_settings_has_speichern_button() -> None:
    assert "Speichern" in _dashboard(), \
        "settings must have a Speichern (save) button"


def test_settings_has_save_action() -> None:
    assert 'data-action="save-settings"' in _dashboard(), \
        "settings save button must have data-action=\"save-settings\""


def test_settings_has_reset_button() -> None:
    assert "Änderungen zurücksetzen" in _dashboard(), \
        "settings must have 'Änderungen zurücksetzen' reset button"


def test_settings_has_save_handler() -> None:
    assert "handleSaveSettings" in _dashboard(), \
        "dashboard must have handleSaveSettings handler"


def test_settings_has_reset_handler() -> None:
    assert "handleResetSettings" in _dashboard(), \
        "dashboard must have handleResetSettings handler"


def test_settings_has_settings_saving_state() -> None:
    assert "settingsSaving" in _dashboard(), \
        "dashboard must track settingsSaving state"


# ---------------------------------------------------------------------------
# 7. German success and error copy
# ---------------------------------------------------------------------------

def test_settings_success_copy_is_german() -> None:
    assert "Einstellungen gespeichert" in _dashboard(), \
        "settings success message must be 'Einstellungen gespeichert.'"


def test_settings_error_copy_is_german() -> None:
    assert "Einstellungen konnten nicht gespeichert werden" in _dashboard(), \
        "settings error message must be in German"


def test_settings_message_state_exists() -> None:
    assert "settingsMessage" in _dashboard(), \
        "dashboard must track settingsMessage state"


# ---------------------------------------------------------------------------
# 8. Language settings wired to existing api.ts endpoint
# ---------------------------------------------------------------------------

def test_dashboard_imports_fetch_clinic_language_settings() -> None:
    assert "fetchClinicLanguageSettings" in _dashboard(), \
        "dashboard must import fetchClinicLanguageSettings"


def test_dashboard_imports_update_clinic_language_settings() -> None:
    assert "updateClinicLanguageSettings" in _dashboard(), \
        "dashboard must import updateClinicLanguageSettings"


# ---------------------------------------------------------------------------
# 9. No technical fields in clinic-facing settings UI
# ---------------------------------------------------------------------------

def test_settings_does_not_expose_clinic_id_label() -> None:
    assert ">clinic_id<" not in _dashboard(), \
        "settings must not show clinic_id as a visible label"


def test_settings_does_not_expose_tenant_id() -> None:
    assert ">tenant_id<" not in _dashboard(), \
        "settings must not show tenant_id as a visible label"


def test_settings_does_not_expose_uuid_label() -> None:
    content = _dashboard()
    assert ">UUID<" not in content and ">uuid<" not in content, \
        "settings must not show UUID as a visible label"


def test_settings_does_not_expose_vapi_config_label() -> None:
    content = _dashboard()
    assert "Vapi-Konfiguration" not in content and "Vapi-Schlüssel" not in content, \
        "settings must not expose Vapi configuration labels"


def test_settings_does_not_expose_webhook_label() -> None:
    assert ">webhook<" not in _dashboard().lower(), \
        "settings must not expose webhook as a visible label"


def test_settings_does_not_expose_fhir_label() -> None:
    content = _dashboard()
    assert ">FHIR<" not in content and ">fhir<" not in content.lower(), \
        "settings must not expose FHIR as a visible label"


def test_settings_does_not_expose_jwt_label() -> None:
    assert ">JWT<" not in _dashboard(), \
        "settings must not expose JWT as a visible label"


def test_settings_does_not_expose_database_url_label() -> None:
    assert ">DATABASE_URL<" not in _dashboard(), \
        "settings must not expose DATABASE_URL as a visible label"


def test_settings_does_not_expose_proposal_id_label() -> None:
    assert ">proposal_id<" not in _dashboard(), \
        "settings must not expose proposal_id as a visible label"


def test_settings_does_not_expose_template_id_label() -> None:
    assert ">template_id<" not in _dashboard(), \
        "settings must not expose template_id as a visible label"


def test_settings_does_not_expose_secret_label() -> None:
    assert ">secret<" not in _dashboard().lower(), \
        "settings must not expose secret as a visible label"


# ---------------------------------------------------------------------------
# 10. Safety invariants remain intact
# ---------------------------------------------------------------------------

def test_settings_no_diagnosis() -> None:
    assert "diagnosis" not in _dashboard().lower(), \
        "dashboard must not contain 'diagnosis'"


def test_settings_no_medical_advice() -> None:
    assert "medical advice" not in _dashboard().lower(), \
        "dashboard must not contain 'medical advice'"


def test_settings_no_treatment_recommendation() -> None:
    assert "treatment recommendation" not in _dashboard().lower(), \
        "dashboard must not contain 'treatment recommendation'"


def test_settings_no_triage() -> None:
    assert "triage" not in _dashboard().lower(), \
        "dashboard must not contain 'triage'"


def test_settings_no_real_patient_data() -> None:
    content = _dashboard()
    assert "no real patient data" in content.lower(), \
        "dashboard must still include 'no real patient data' safety copy"


def test_settings_production_phi_no_go() -> None:
    content = _dashboard()
    assert "Production PHI" in content or "production phi" in content.lower(), \
        "dashboard must still mention Production PHI boundary"


def test_settings_no_session_storage() -> None:
    content = _dashboard()
    non_comment = "\n".join(ln for ln in content.splitlines() if not ln.strip().startswith("//"))
    assert "sessionStorage" not in non_comment, \
        "dashboard must not use sessionStorage"


def test_settings_no_local_storage() -> None:
    content = _dashboard()
    non_comment = "\n".join(ln for ln in content.splitlines() if not ln.strip().startswith("//"))
    assert "localStorage" not in non_comment, \
        "dashboard must not use localStorage"


# ---------------------------------------------------------------------------
# 11. Existing Module 157/158 assertions still green
# ---------------------------------------------------------------------------

def test_dashboard_still_has_heute_label() -> None:
    assert "Heute" in _dashboard(), \
        "Heute summary bar must still be present"


def test_dashboard_still_has_anfragen_tab() -> None:
    assert "Anfragen" in _dashboard(), \
        "Anfragen tab must still be present"


def test_dashboard_still_has_patienten_tab() -> None:
    assert "Patienten" in _dashboard(), \
        "Patienten tab must still be present"


def test_dashboard_still_has_demo_strip() -> None:
    assert 'data-demo-strip="sales-mvp"' in _dashboard(), \
        "Module 158 demo strip must still be present"


def test_dashboard_still_has_demo_anruf_erstellen() -> None:
    assert "Demo-Anruf erstellen" in _dashboard(), \
        "Module 158 demo button must still be present"


# ---------------------------------------------------------------------------
# 12. Product doc exists
# ---------------------------------------------------------------------------

def test_simple_clinic_settings_doc_exists() -> None:
    doc_path = os.path.join(_REPO_ROOT, "docs", "product", "SIMPLE_CLINIC_SETTINGS.md")
    assert os.path.isfile(doc_path), \
        "docs/product/SIMPLE_CLINIC_SETTINGS.md must exist"


def test_simple_clinic_settings_doc_mentions_module_159() -> None:
    doc_path = os.path.join(_REPO_ROOT, "docs", "product", "SIMPLE_CLINIC_SETTINGS.md")
    with open(doc_path, encoding="utf-8") as f:
        content = f.read()
    assert "159" in content, \
        "SIMPLE_CLINIC_SETTINGS.md must mention Module 159"


def test_simple_clinic_settings_doc_mentions_no_technical_fields() -> None:
    doc_path = os.path.join(_REPO_ROOT, "docs", "product", "SIMPLE_CLINIC_SETTINGS.md")
    with open(doc_path, encoding="utf-8") as f:
        content = f.read()
    assert "technical" in content.lower() or "technisch" in content.lower(), \
        "SIMPLE_CLINIC_SETTINGS.md must mention the no-technical-fields constraint"


def test_simple_clinic_settings_doc_mentions_acceptance() -> None:
    doc_path = os.path.join(_REPO_ROOT, "docs", "product", "SIMPLE_CLINIC_SETTINGS.md")
    with open(doc_path, encoding="utf-8") as f:
        content = f.read()
    assert "rezeptionist" in content.lower() or "Rezeptionist" in content, \
        "SIMPLE_CLINIC_SETTINGS.md must mention the receptionist acceptance statement"
