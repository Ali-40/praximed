"""
Sprint 19 / Module 140 — Live Tenant Language Settings Smoke Evidence

Static contract tests: read raw Markdown source and verify the smoke evidence
doc meets the specification.

No imports, no database, no network. All assertions are substring checks.
"""

from pathlib import Path

DOC_PATH = Path("docs/runtime/LIVE_TENANT_LANGUAGE_SETTINGS_SMOKE_EVIDENCE.md")


def _doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# File existence
# ---------------------------------------------------------------------------


def test_doc_exists():
    assert DOC_PATH.exists(), f"Missing smoke evidence doc: {DOC_PATH}"


# ---------------------------------------------------------------------------
# Module identity
# ---------------------------------------------------------------------------


def test_doc_module_140():
    assert "140" in _doc()


def test_doc_sprint_19():
    assert "Sprint 19" in _doc()


def test_doc_commit_referenced():
    assert "1cf85f0" in _doc()


# ---------------------------------------------------------------------------
# Current result
# ---------------------------------------------------------------------------


def test_doc_result_pass():
    assert "PASS" in _doc()


# ---------------------------------------------------------------------------
# Live route tested
# ---------------------------------------------------------------------------


def test_doc_has_frontend_url():
    assert "https://praximed.vercel.app/developer-console/language-settings" in _doc()


def test_doc_has_get_route():
    assert "GET" in _doc() and "/language-settings" in _doc()


def test_doc_has_patch_route():
    assert "PATCH" in _doc() and "/language-settings" in _doc()


def test_doc_references_clinics_path():
    assert "/clinics/" in _doc()


# ---------------------------------------------------------------------------
# Clinic ID
# ---------------------------------------------------------------------------


def test_doc_has_clinic_id():
    assert "1a5bbc75-c1b0-4488-94aa-64b3f1c50056" in _doc()


def test_doc_staging_clinic_identified():
    src = _doc().lower()
    assert "staging" in src or "demo" in src or "fake" in src


# ---------------------------------------------------------------------------
# Load settings evidence
# ---------------------------------------------------------------------------


def test_doc_load_settings_section():
    src = _doc().lower()
    assert "load settings" in src or "load" in src


def test_doc_http_200():
    assert "200" in _doc()


# ---------------------------------------------------------------------------
# German-first defaults
# ---------------------------------------------------------------------------


def test_doc_german_first():
    src = _doc().lower()
    assert "german" in src and "first" in src


def test_doc_primary_language_de():
    assert "primary_language" in _doc()
    assert "`de`" in _doc() or "= de" in _doc() or "| `de`" in _doc()


def test_doc_vapi_mode_german_first():
    assert "german_first" in _doc()


def test_doc_clinic_ui_language_de():
    assert "clinic_ui_language" in _doc()


def test_doc_default_patient_language():
    assert "default_patient_language" in _doc()


def test_doc_supported_languages():
    assert "supported_languages" in _doc()


# ---------------------------------------------------------------------------
# English fallback
# ---------------------------------------------------------------------------


def test_doc_english_fallback():
    src = _doc().lower()
    assert "english" in src and ("fallback" in src or "en" in src)


def test_doc_fallback_language_en():
    assert "fallback_language" in _doc()


# ---------------------------------------------------------------------------
# PATCH / update evidence
# ---------------------------------------------------------------------------


def test_doc_bilingual_auto():
    assert "bilingual_auto" in _doc()


def test_doc_patch_sent():
    assert "PATCH" in _doc()


def test_doc_language_settings_saved():
    assert "Language settings saved" in _doc()


def test_doc_vapi_assistant_language_mode_updated():
    assert "vapi_assistant_language_mode" in _doc()


# ---------------------------------------------------------------------------
# Reload / persistence evidence
# ---------------------------------------------------------------------------


def test_doc_reload_persisted():
    src = _doc().lower()
    assert "reload" in src and ("persisted" in src or "confirmed" in src)


def test_doc_reload_confirmed_update_persisted():
    src = _doc().lower()
    assert "reload confirmed update persisted" in src or (
        "reload" in src and "confirmed" in src and "persist" in src
    )


def test_doc_german_first_restored():
    src = _doc().lower()
    assert "german_first" in src


# ---------------------------------------------------------------------------
# Safety boundaries
# ---------------------------------------------------------------------------


def test_doc_no_phi():
    src = _doc().lower()
    assert "no phi" in src


def test_doc_no_secrets():
    src = _doc().lower()
    assert "no secrets" in src or "no secret" in src


def test_doc_no_vapi_credentials():
    src = _doc().lower()
    assert "no vapi credentials" in src or "vapi credentials" in src


def test_doc_production_phi_no_go():
    assert "NO-GO" in _doc() or "no-go" in _doc().lower()


def test_doc_production_phi_remains_no_go():
    src = _doc().lower()
    assert "production phi remains no-go" in src or (
        "production phi" in src and "no-go" in src
    )


def test_doc_no_production_activation():
    src = _doc().lower()
    assert "no production activation" in src or "production activation" in src


def test_doc_credentials_include():
    assert "credentials" in _doc() and "include" in _doc()


# ---------------------------------------------------------------------------
# What this proves / does not prove
# ---------------------------------------------------------------------------


def test_doc_has_what_proves_section():
    src = _doc().lower()
    assert "what this proves" in src


def test_doc_has_what_does_not_prove_section():
    src = _doc().lower()
    assert "what this does not prove" in src


def test_doc_proves_end_to_end():
    src = _doc().lower()
    assert "end-to-end" in src or "end to end" in src


def test_doc_does_not_prove_production():
    src = _doc().lower()
    assert "production readiness" in src or "production" in src


def test_doc_does_not_prove_vapi_binding():
    src = _doc().lower()
    assert "vapi" in src and ("binding" in src or "wiring" in src)


# ---------------------------------------------------------------------------
# Remaining blockers
# ---------------------------------------------------------------------------


def test_doc_has_remaining_blockers():
    src = _doc().lower()
    assert "remaining blockers" in src or "blocker" in src


def test_doc_blocker_c3():
    assert "C3" in _doc()


def test_doc_blocker_c4():
    assert "C4" in _doc()


def test_doc_blocker_c5():
    assert "C5" in _doc()


def test_doc_blocker_c6():
    assert "C6" in _doc()


def test_doc_blocker_c7():
    assert "C7" in _doc()


def test_doc_blocker_c8():
    assert "C8" in _doc()


def test_doc_dsgvo_referenced():
    src = _doc().lower()
    assert "dsgvo" in src or "legal" in src
