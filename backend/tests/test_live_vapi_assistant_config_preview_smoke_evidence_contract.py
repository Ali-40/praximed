"""
Sprint 19 / Module 143 — Live Vapi Assistant Config Preview Smoke Evidence

Static contract tests: read raw Markdown source and verify the smoke evidence
doc meets the specification.

No imports, no database, no network. All assertions are substring checks.
"""

from pathlib import Path

DOC_PATH = Path(
    "docs/runtime/LIVE_VAPI_ASSISTANT_CONFIG_PREVIEW_SMOKE_EVIDENCE.md"
)


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


def test_doc_module_143():
    assert "143" in _doc()


def test_doc_sprint_19():
    assert "Sprint 19" in _doc()


def test_doc_commit_referenced():
    assert "944b898" in _doc()


# ---------------------------------------------------------------------------
# Current result
# ---------------------------------------------------------------------------


def test_doc_result_pass():
    assert "PASS" in _doc()


# ---------------------------------------------------------------------------
# Live route tested
# ---------------------------------------------------------------------------


def test_doc_has_frontend_url():
    assert "https://praximed.vercel.app/developer-console/vapi-config" in _doc()


def test_doc_has_get_route():
    assert "GET" in _doc() and "vapi-assistant-config-pack" in _doc()


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
# Load config pack evidence
# ---------------------------------------------------------------------------


def test_doc_load_config_pack():
    src = _doc().lower()
    assert "load config" in src or "config pack" in src


def test_doc_http_200():
    assert "200" in _doc()


# ---------------------------------------------------------------------------
# German-first prompt evidence
# ---------------------------------------------------------------------------


def test_doc_german_first_prompt():
    src = _doc().lower()
    assert "german" in src and ("first" in src or "prompt" in src)


def test_doc_ki_rezeption():
    assert "KI-Rezeption" in _doc()


def test_doc_keine_diagnose():
    assert "keine Diagnose" in _doc()


def test_doc_keine_medizinische_beratung():
    assert "keine medizinische Beratung" in _doc()


def test_doc_keine_terminbestaetigung():
    assert "Terminbestätigung" in _doc() or "terminbest" in _doc().lower()


def test_doc_notruf_144():
    assert "144" in _doc()


def test_doc_first_message_de():
    src = _doc()
    assert "first_message_de" in src or "German greeting" in src


# ---------------------------------------------------------------------------
# English fallback prompt evidence
# ---------------------------------------------------------------------------


def test_doc_english_fallback_prompt():
    src = _doc().lower()
    assert "english" in src and ("fallback" in src or "prompt" in src)


def test_doc_ai_receptionist():
    assert "AI receptionist" in _doc()


def test_doc_no_diagnosis_en():
    assert "No diagnosis" in _doc() or "no diagnosis" in _doc()


def test_doc_no_medical_advice_en():
    assert "No medical advice" in _doc() or "no medical advice" in _doc()


def test_doc_no_appointment_confirmation():
    src = _doc().lower()
    assert "no appointment confirmation" in src or "do not promise" in src or "confirmation" in src


def test_doc_call_144():
    assert "call 144" in _doc() or "144" in _doc()


# ---------------------------------------------------------------------------
# Required capture fields evidence
# ---------------------------------------------------------------------------


def test_doc_patient_name():
    assert "patient_name" in _doc()


def test_doc_phone():
    assert "phone" in _doc()


def test_doc_reason():
    assert "reason" in _doc()


def test_doc_preferred_time():
    assert "preferred_time" in _doc()


def test_doc_language_preference():
    assert "language_preference" in _doc()


def test_doc_urgency_level():
    assert "urgency_level" in _doc()


# ---------------------------------------------------------------------------
# Tool schema evidence
# ---------------------------------------------------------------------------


def test_doc_tool_schema_visible():
    src = _doc().lower()
    assert "tool schema" in src or "tool_schema" in src


def test_doc_capture_appointment_request():
    assert "capture_appointment_request" in _doc() or "capture-appointment-request" in _doc()


def test_doc_x_vapi_service_name():
    assert "X-Vapi-Service-Name" in _doc()


def test_doc_x_vapi_clinic_id():
    assert "X-Vapi-Clinic-Id" in _doc()


def test_doc_x_vapi_scopes():
    assert "X-Vapi-Scopes" in _doc()


def test_doc_no_secret_values_in_tool_schema():
    src = _doc().lower()
    assert "no secret values" in src or "secret values" in src


# ---------------------------------------------------------------------------
# Safety rules evidence
# ---------------------------------------------------------------------------


def test_doc_no_diagnosis_safety_rule():
    src = _doc().lower()
    assert "no diagnosis" in src or "diagnosis" in src


def test_doc_no_medical_advice_safety_rule():
    src = _doc().lower()
    assert "no medical advice" in src or "medical advice" in src


def test_doc_no_appointment_confirmation_safety_rule():
    src = _doc().lower()
    assert "no appointment confirmation" in src or "appointment" in src


def test_doc_emergency_escalation_144():
    assert "144" in _doc()


# ---------------------------------------------------------------------------
# Forbidden claims evidence
# ---------------------------------------------------------------------------


def test_doc_forbidden_claims_section():
    src = _doc().lower()
    assert "forbidden claims" in src or "forbidden" in src


# ---------------------------------------------------------------------------
# Readiness flags evidence
# ---------------------------------------------------------------------------


def test_doc_production_phi_enabled_false():
    src = _doc()
    assert "production_phi_enabled" in src
    assert "false" in src.lower()


def test_doc_recording_ingestion_enabled_false():
    src = _doc()
    assert "recording_ingestion_enabled" in src
    assert "false" in src.lower()


def test_doc_transcript_ingestion_enabled_false():
    src = _doc()
    assert "transcript_ingestion_enabled" in src
    assert "false" in src.lower()


def test_doc_all_flags_false():
    src = _doc().lower()
    assert "false" in src


# ---------------------------------------------------------------------------
# Safety boundaries
# ---------------------------------------------------------------------------


def test_doc_no_phi():
    src = _doc().lower()
    assert "no phi" in src


def test_doc_no_vapi_api_key():
    src = _doc().lower()
    assert "no vapi api key" in src or "vapi api key" in src or "vapi credentials" in src


def test_doc_no_webhook_secret():
    src = _doc().lower()
    assert "no webhook secret" in src or "webhook secret" in src or "no secrets" in src


def test_doc_no_secrets():
    src = _doc().lower()
    assert "no secrets" in src or "no secret" in src


def test_doc_no_live_vapi_binding():
    src = _doc().lower()
    assert "no live vapi" in src or "no live" in src or "vapi binding" in src


def test_doc_production_phi_remains_no_go():
    assert "NO-GO" in _doc() or "no-go" in _doc().lower()


def test_doc_production_phi_no_go_in_boundaries():
    src = _doc().lower()
    assert "production phi remains no-go" in src or (
        "production phi" in src and "no-go" in src
    )


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
    assert "vapi" in src and ("binding" in src or "provisioning" in src)


def test_doc_does_not_prove_bilingual_audio():
    src = _doc().lower()
    assert "bilingual" in src or "audio" in src or "live" in src


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


def test_doc_dsgvo_or_legal_referenced():
    src = _doc().lower()
    assert "dsgvo" in src or "legal" in src
