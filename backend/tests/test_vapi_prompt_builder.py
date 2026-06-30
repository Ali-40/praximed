"""
Unit tests for the Vapi prompt builder — PraxisMed Sprint 1 / Module 11
"""

from __future__ import annotations

from unittest.mock import MagicMock

from backend.app.modules.vapi.vapi_prompt_builder import (
    build_vapi_clinic_context,
    build_vapi_system_prompt,
    build_vapi_tool_instructions,
)

TENANT_ID = "11111111-1111-4111-8111-111111111111"


def _make_config(**overrides) -> MagicMock:
    cfg = MagicMock()
    cfg.tenant_id    = TENANT_ID
    cfg.clinic_name  = "Praxis Dr. Muster Wien"
    cfg.language     = "de"
    cfg.country      = "AT"
    cfg.timezone     = "Europe/Vienna"
    cfg.ai_persona_name = "Mia"
    cfg.ai_tone      = "professional"
    cfg.opening_hours = {
        "monday": {"open": "08:00", "close": "18:00"},
        "saturday": None,
    }
    cfg.calendar_rules = {"slot_minutes": 30}
    cfg.extra = {}
    for k, v in overrides.items():
        setattr(cfg, k, v)
    return cfg


# ---------------------------------------------------------------------------
# build_vapi_system_prompt
# ---------------------------------------------------------------------------

def test_prompt_includes_clinic_name():
    prompt = build_vapi_system_prompt(_make_config())
    assert "Praxis Dr. Muster Wien" in prompt


def test_prompt_includes_no_diagnosis_rule():
    prompt = build_vapi_system_prompt(_make_config())
    assert "Diagnose" in prompt or "diagnos" in prompt.lower()


def test_prompt_includes_one_question_at_a_time():
    prompt = build_vapi_system_prompt(_make_config())
    assert "eine Frage" in prompt or "nur eine" in prompt.lower()


def test_prompt_includes_availability_check_before_offering_slot():
    prompt = build_vapi_system_prompt(_make_config())
    lower = prompt.lower()
    assert "verfügbarkeit" in lower or "verfügbar" in lower


def test_prompt_includes_persona_name():
    prompt = build_vapi_system_prompt(_make_config())
    assert "Mia" in prompt


def test_prompt_includes_timezone():
    prompt = build_vapi_system_prompt(_make_config())
    assert "Europe/Vienna" in prompt


def test_prompt_includes_faqs_when_present():
    cfg = _make_config(extra={"faqs": ["Haben Sie Parkplätze?"]})
    prompt = build_vapi_system_prompt(cfg)
    assert "Parkplätze" in prompt


def test_prompt_includes_escalation_rules_when_present():
    cfg = _make_config(extra={"escalation_rules": ["Notfall sofort weiterleiten"]})
    prompt = build_vapi_system_prompt(cfg)
    assert "Notfall" in prompt


# ---------------------------------------------------------------------------
# build_vapi_tool_instructions
# ---------------------------------------------------------------------------

def test_tool_instructions_mention_availability_check():
    instructions = build_vapi_tool_instructions()
    assert "check_availability" in instructions or "availability" in instructions.lower()


def test_tool_instructions_mention_slot_suggestion():
    instructions = build_vapi_tool_instructions()
    assert "suggest_slots" in instructions or "slot" in instructions.lower()


# ---------------------------------------------------------------------------
# build_vapi_clinic_context
# ---------------------------------------------------------------------------

def test_clinic_context_includes_required_keys():
    ctx = build_vapi_clinic_context(_make_config())
    assert ctx["clinic_id"]   == TENANT_ID
    assert ctx["clinic_name"] == "Praxis Dr. Muster Wien"
    assert ctx["timezone"]    == "Europe/Vienna"


def test_clinic_context_contains_no_patient_data():
    cfg = _make_config()
    ctx = build_vapi_clinic_context(cfg)
    # None of these patient-related keys should appear
    for key in ("patient", "dob", "phone", "caller", "secret", "password"):
        assert key not in ctx


def test_clinic_context_includes_opening_hours():
    ctx = build_vapi_clinic_context(_make_config())
    assert "opening_hours" in ctx
    assert ctx["opening_hours"]["monday"]["open"] == "08:00"


def test_clinic_context_includes_calendar_rules():
    ctx = build_vapi_clinic_context(_make_config())
    assert ctx["calendar_rules"]["slot_minutes"] == 30
