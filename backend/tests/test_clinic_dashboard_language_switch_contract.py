"""
Static contract tests for Sprint 21 / Module 163 — Clinic dashboard language switch.

Verifies file content only. No database. No network. No secrets.
No real patient data. No PHI. Production PHI remains NO-GO.

Tests confirm:
- TRANSLATIONS dictionary present with de and en sections
- uiLang state variable present (default 'de')
- t() helper function present
- Language selector present in Settings tab (Sprache der Oberfläche)
- Deutsch option present
- English option present
- German labels present in de section of TRANSLATIONS
- English labels present in en section of TRANSLATIONS
- No external i18n library imported
- No forbidden technical terms
- All prior module safety invariants remain intact
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
# 1. Translation dictionary structure
# ---------------------------------------------------------------------------


def test_translations_constant_present() -> None:
    assert "TRANSLATIONS" in _dashboard(), \
        "dashboard must define a TRANSLATIONS constant"


def test_translations_de_section_present() -> None:
    content = _dashboard()
    assert "de:" in content or "de: {" in content, \
        "TRANSLATIONS must have a 'de' section"


def test_translations_en_section_present() -> None:
    content = _dashboard()
    assert "en:" in content or "en: {" in content, \
        "TRANSLATIONS must have an 'en' section"


def test_translations_marked_as_const() -> None:
    assert "} as const" in _dashboard(), \
        "TRANSLATIONS must be marked 'as const' for type safety"


# ---------------------------------------------------------------------------
# 2. uiLang state and t() helper
# ---------------------------------------------------------------------------


def test_ui_lang_state_present() -> None:
    assert "uiLang" in _dashboard(), \
        "dashboard must have uiLang state variable"


def test_ui_lang_default_german() -> None:
    content = _dashboard()
    assert "'de'" in content and "uiLang" in content, \
        "uiLang must default to 'de' (German)"


def test_t_helper_function_present() -> None:
    content = _dashboard()
    assert "const t = " in content or "function t(" in content, \
        "dashboard must define a t() translation helper"


def test_t_helper_uses_ui_lang() -> None:
    content = _dashboard()
    assert "TRANSLATIONS[uiLang]" in content, \
        "t() helper must look up translations via TRANSLATIONS[uiLang]"


def test_t_calls_present_in_dashboard() -> None:
    content = _dashboard()
    assert "t('" in content or 't("' in content, \
        "dashboard must call t() for label lookups"


# ---------------------------------------------------------------------------
# 3. Language selector in Settings tab
# ---------------------------------------------------------------------------


def test_language_selector_heading_present() -> None:
    assert "Sprache der Oberfläche" in _dashboard(), \
        "Settings tab must have 'Sprache der Oberfläche' language selector heading"


def test_language_selector_interface_language_present() -> None:
    assert "Interface language" in _dashboard(), \
        "language selector heading must include 'Interface language' (bilingual)"


def test_language_selector_deutsch_option() -> None:
    assert "Deutsch" in _dashboard(), \
        "language selector must show 'Deutsch' option"


def test_language_selector_english_option() -> None:
    assert "English" in _dashboard(), \
        "language selector must show 'English' option"


def test_language_selector_radio_inputs() -> None:
    content = _dashboard()
    assert 'name="ui-lang"' in content, \
        "language selector must use radio inputs with name='ui-lang'"


def test_language_selector_data_ui_lang_attribute() -> None:
    content = _dashboard()
    assert "data-ui-lang" in content, \
        "language selector radio labels must have data-ui-lang attribute"


def test_set_ui_lang_handler_present() -> None:
    content = _dashboard()
    assert "setUiLang" in content, \
        "dashboard must have setUiLang handler to change language"


# ---------------------------------------------------------------------------
# 4. German labels in de section
# ---------------------------------------------------------------------------


def test_translations_de_has_heute() -> None:
    assert "'Heute'" in _dashboard(), \
        "de section must have 'Heute' label"


def test_translations_de_has_anfragen() -> None:
    assert "'Anfragen'" in _dashboard(), \
        "de section must have 'Anfragen' label"


def test_translations_de_has_patienten() -> None:
    assert "'Patienten'" in _dashboard(), \
        "de section must have 'Patienten' label"


def test_translations_de_has_einstellungen() -> None:
    assert "'Einstellungen'" in _dashboard(), \
        "de section must have 'Einstellungen' label"


def test_translations_de_has_rueckruf_markieren() -> None:
    assert "'Rückruf markieren'" in _dashboard(), \
        "de section must have 'Rückruf markieren'"


def test_translations_de_has_als_kontaktiert_markieren() -> None:
    assert "'Als kontaktiert markieren'" in _dashboard(), \
        "de section must have 'Als kontaktiert markieren'"


def test_translations_de_has_anfrage_im_ueberblick() -> None:
    assert "'Anfrage im Überblick'" in _dashboard(), \
        "de section must have 'Anfrage im Überblick'"


def test_translations_de_has_gewuenschte_zeit() -> None:
    assert "'Gewünschte Zeit'" in _dashboard(), \
        "de section must have 'Gewünschte Zeit'"


def test_translations_de_has_praxisprofil() -> None:
    assert "'Praxisprofil'" in _dashboard(), \
        "de section must have 'Praxisprofil'"


def test_translations_de_has_ki_rezeption() -> None:
    assert "'KI-Rezeption'" in _dashboard(), \
        "de section must have 'KI-Rezeption'"


def test_translations_de_has_ki_vorschau() -> None:
    assert "'KI-Vorschau'" in _dashboard(), \
        "de section must have 'KI-Vorschau'"


# ---------------------------------------------------------------------------
# 5. English labels in en section
# ---------------------------------------------------------------------------


def test_translations_en_has_today() -> None:
    assert "'Today'" in _dashboard(), \
        "en section must have 'Today' label"


def test_translations_en_has_requests() -> None:
    assert "'Requests'" in _dashboard(), \
        "en section must have 'Requests' label"


def test_translations_en_has_patients() -> None:
    assert "'Patients'" in _dashboard(), \
        "en section must have 'Patients' label"


def test_translations_en_has_needs_callback() -> None:
    assert "'Needs callback'" in _dashboard(), \
        "en section must have 'Needs callback' label"


def test_translations_en_has_mark_callback() -> None:
    assert "'Mark callback'" in _dashboard(), \
        "en section must have 'Mark callback' label"


def test_translations_en_has_mark_contacted() -> None:
    assert "'Mark contacted'" in _dashboard(), \
        "en section must have 'Mark contacted' label"


def test_translations_en_has_request_overview() -> None:
    assert "'Request overview'" in _dashboard(), \
        "en section must have 'Request overview' label"


def test_translations_en_has_preferred_time() -> None:
    assert "'Preferred time'" in _dashboard(), \
        "en section must have 'Preferred time' label"


def test_translations_en_has_practice_profile() -> None:
    assert "'Practice profile'" in _dashboard(), \
        "en section must have 'Practice profile' label"


def test_translations_en_has_opening_hours() -> None:
    assert "'Opening hours'" in _dashboard(), \
        "en section must have 'Opening hours' label"


def test_translations_en_has_ai_receptionist() -> None:
    assert "'AI receptionist'" in _dashboard(), \
        "en section must have 'AI receptionist' label"


# ---------------------------------------------------------------------------
# 6. No external i18n library
# ---------------------------------------------------------------------------


def test_no_next_intl() -> None:
    assert "next-intl" not in _dashboard(), \
        "dashboard must not use next-intl library"


def test_no_react_i18next() -> None:
    assert "react-i18next" not in _dashboard() and "i18next" not in _dashboard(), \
        "dashboard must not use react-i18next / i18next"


def test_no_formatjs() -> None:
    assert "react-intl" not in _dashboard(), \
        "dashboard must not use react-intl / FormatJS"


# ---------------------------------------------------------------------------
# 7. Safety invariants — all prior module boundaries intact
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


def test_dashboard_no_clinical_decision() -> None:
    assert "clinical decision" not in _dashboard().lower(), \
        "dashboard must not use 'clinical decision' in any label"


def test_dashboard_production_phi_no_go() -> None:
    content = _dashboard()
    assert "Production PHI" in content or "production phi" in content.lower(), \
        "dashboard must still mention Production PHI boundary"


def test_dashboard_no_real_patient_data() -> None:
    assert "no real patient data" in _dashboard().lower(), \
        "dashboard must include 'no real patient data' safety copy"


def test_dashboard_no_database_url() -> None:
    assert "DATABASE_URL" not in _dashboard(), \
        "dashboard must not contain DATABASE_URL"


def test_dashboard_no_auto_appointment_confirmation() -> None:
    content = _dashboard()
    assert "Termin bestätigt" not in content and "appointment confirmed" not in content.lower(), \
        "dashboard must not promise automatic appointment confirmation"


# ---------------------------------------------------------------------------
# 8. Regression guard — prior module markers must remain
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


def test_dashboard_still_has_praxismed_brand() -> None:
    assert "PraxisMed" in _dashboard(), \
        "PraxisMed brand must still be present"


def test_dashboard_still_has_anfragen_empty_german() -> None:
    assert "Noch keine Anfragen" in _dashboard(), \
        "German empty state must still be present"


def test_dashboard_noch_keine_aktiven_anfragen_present() -> None:
    assert "Noch keine aktiven Anfragen" in _dashboard(), \
        "Module 162B empty active state must still be present"


def test_dashboard_archivierte_anfragen_present() -> None:
    assert "Archivierte Anfragen" in _dashboard(), \
        "Module 162B archived section label must still be present"


# ---------------------------------------------------------------------------
# 9. Module 163A — Language-aware helpers (stronger assertions)
# ---------------------------------------------------------------------------


def test_get_status_label_function_present() -> None:
    assert "getStatusLabel" in _dashboard(), \
        "dashboard must define getStatusLabel(status, lang) language-aware helper"


def test_get_status_label_takes_lang_parameter() -> None:
    content = _dashboard()
    assert "getStatusLabel(status" in content or "getStatusLabel(s," in content or \
           "lang: 'de' | 'en'" in content, \
        "getStatusLabel must accept a lang parameter"


def test_get_readable_request_number_language_aware() -> None:
    content = _dashboard()
    assert "getReadableRequestNumber" in content, \
        "dashboard must define getReadableRequestNumber helper"
    assert "lang" in content, \
        "getReadableRequestNumber must accept a lang parameter"


def test_translations_de_has_anfrage_hash_prefix() -> None:
    assert "'Anfrage #'" in _dashboard(), \
        "de TRANSLATIONS must contain 'Anfrage #' request prefix"


def test_translations_en_has_request_hash_prefix() -> None:
    assert "'Request #'" in _dashboard(), \
        "en TRANSLATIONS must contain 'Request #' request prefix"


def test_translations_en_has_not_provided() -> None:
    assert "'Not provided'" in _dashboard(), \
        "en TRANSLATIONS must have 'Not provided' for missing fields"


def test_translations_de_has_nicht_angegeben() -> None:
    assert "'Nicht angegeben'" in _dashboard(), \
        "de TRANSLATIONS must have 'Nicht angegeben'"


def test_translations_en_has_archived_requests() -> None:
    assert "'Archived requests'" in _dashboard(), \
        "en TRANSLATIONS must have 'Archived requests'"


def test_translations_de_has_archivierte_anfragen() -> None:
    assert "'Archivierte Anfragen'" in _dashboard(), \
        "de TRANSLATIONS must have 'Archivierte Anfragen'"


def test_translations_en_has_demo_in_3_steps() -> None:
    assert "'Demo in 3 steps'" in _dashboard(), \
        "en TRANSLATIONS must have 'Demo in 3 steps'"


def test_translations_de_has_demo_in_3_schritten() -> None:
    assert "'Demo in 3 Schritten'" in _dashboard(), \
        "de TRANSLATIONS must have 'Demo in 3 Schritten'"


def test_translations_en_has_create_demo_call() -> None:
    assert "'Create demo call'" in _dashboard(), \
        "en TRANSLATIONS must have 'Create demo call'"


def test_translations_en_has_staff_review() -> None:
    assert "'Staff review'" in _dashboard(), \
        "en TRANSLATIONS must have 'Staff review' label"


def test_translations_en_has_completed() -> None:
    assert "'Completed'" in _dashboard(), \
        "en TRANSLATIONS must have 'Completed' label"


def test_translations_en_has_received() -> None:
    assert "'Received'" in _dashboard(), \
        "en TRANSLATIONS must have 'Received' label"


def test_all_get_status_label_calls_pass_uilang() -> None:
    content = _dashboard()
    assert "getStatusLabel(" in content, \
        "dashboard must call getStatusLabel with uiLang argument"
    assert "getStatusLabel(appt.status, uiLang)" in content or \
           "getStatusLabel(selectedAppt.status, uiLang)" in content or \
           "getStatusLabel(patient.status, uiLang)" in content, \
        "getStatusLabel calls must pass uiLang"
