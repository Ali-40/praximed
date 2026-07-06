"""
Vapi Assistant Config Pack service — PraxisMed Sprint 19 / Module 141.

Derives a safe, per-tenant Vapi assistant configuration pack from clinic
language settings and tenant config.

No live Vapi API calls. No secrets stored or returned. No PHI.
production_phi_enabled is always False in the generated pack.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from backend.app.services.clinic_language_settings import (
    ClinicNotFoundError,
    get_clinic_language_settings,
)

# ---------------------------------------------------------------------------
# Tenant config path (mirrors clinic_language_settings.py)
# ---------------------------------------------------------------------------

_TENANTS_DIR = (
    Path(__file__).resolve().parents[3] / "backend" / "tenants" / "configs"
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_TOOL_SCHEMA: Dict[str, Any] = {
    "name": "capture_appointment_request",
    "description": (
        "Capture an appointment request from a caller and forward it to the clinic team. "
        "Call this tool once the caller has provided sufficient information. "
        "Do not call this tool for emergency situations — instruct the caller to "
        "call 144 (Austria) or seek urgent medical help first."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "clinic_ref": {
                "type": "string",
                "description": "Clinic identifier (provided by system, do not ask caller)",
            },
            "call_id": {
                "type": "string",
                "description": "Vapi call identifier (provided by system)",
            },
            "patient_name": {
                "type": "string",
                "description": "Full name of the patient as stated by the caller",
            },
            "phone": {
                "type": "string",
                "description": "Callback phone number provided by the caller",
            },
            "reason": {
                "type": "string",
                "description": "Reason for the appointment request, in the caller's own words",
            },
            "preferred_time": {
                "type": "string",
                "description": "Preferred appointment time or time range stated by the caller",
            },
            "urgency_level": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "description": "Urgency assessed from the caller's description",
            },
            "language_preference": {
                "type": "string",
                "description": "Language the caller preferred during the call",
            },
        },
        "required": ["patient_name", "phone", "reason"],
    },
    "headers": {
        "description": (
            "Required non-secret headers sent by the Vapi runtime. "
            "Secret values are never included here."
        ),
        "names": [
            "X-Vapi-Service-Name",
            "X-Vapi-Clinic-Id",
            "X-Vapi-Scopes",
        ],
    },
    "target_endpoint": "POST /vapi/tools/capture-appointment-request",
}

_REQUIRED_CAPTURE_FIELDS = [
    "patient_name",
    "phone",
    "reason",
    "preferred_time",
    "language_preference",
    "urgency_level",
]

_SAFETY_RULES = [
    "No diagnosis. Never provide a diagnosis or suggest what illness the caller may have.",
    "No medical advice. Do not give medical recommendations or treatment instructions.",
    "No treatment recommendations. Do not suggest medications, procedures, or therapies.",
    "No appointment confirmation. Never promise the appointment is confirmed. State that the clinic team will review and confirm.",
    "Emergency escalation. If the caller describes acute or life-threatening symptoms, immediately instruct them to call 144 (Austria) or seek urgent medical help. Do not attempt triage.",
    "Appointment capture only. The assistant's sole task is to capture the appointment request.",
    "No PHI beyond what is necessary. Do not repeat or store sensitive patient data beyond the captured request fields.",
    "No secrets in responses. Never output API keys, webhook secrets, or system credentials.",
]

_ESCALATION_RULES = [
    "Notfall (Austria): Bei akuten Notfällen sofort Notruf 144 oder medizinische Notaufnahme aufsuchen.",
    "Emergency (Austria): For acute emergencies, call 144 immediately or go to the nearest emergency department.",
    "Do not stay on the call to help with the emergency. Direct the caller to emergency services and end gracefully.",
]

_FORBIDDEN_CLAIMS = [
    "That the appointment is confirmed.",
    "A diagnosis of any kind.",
    "Medical advice or treatment recommendations.",
    "That the assistant is a doctor, nurse, or qualified medical professional.",
    "That calling 144 is unnecessary for serious symptoms.",
    "Any claim about specific medications or dosages.",
]


# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------


def _build_german_prompt(clinic_display_name: str, specialty: str, city: str) -> str:
    return (
        f"Du bist die KI-Rezeption von {clinic_display_name}, einer privaten Praxis in Wien.\n\n"
        "Deine Aufgabe ist es, Terminanfragen entgegenzunehmen. Du nimmst den Namen des Patienten, "
        "die Rückrufnummer, das Anliegen und den gewünschten Terminzeitraum auf.\n\n"
        "Tonalität:\n"
        "- Höflich und professionell\n"
        "- Ruhig und klar\n"
        "- Österreichischer Praxis-Kontext\n"
        "- Keine übertriebene Marketing-Sprache\n\n"
        "Sprachverhalten:\n"
        "- Führe das Gespräch auf Deutsch.\n"
        "- Wenn der Anrufer auf Englisch spricht, wechsle zu Englisch.\n"
        "- Erkenne die bevorzugte Sprache des Anrufers und passe dich an.\n\n"
        "Grenzen — diese müssen immer eingehalten werden:\n"
        "- Keine Diagnose. Nenne niemals eine mögliche Diagnose.\n"
        "- Keine medizinische Beratung. Gib keine Empfehlungen zu Behandlungen oder Medikamenten.\n"
        "- Keine Terminbestätigung versprechen. Sage, dass das Praxisteam die Anfrage prüft und bestätigt.\n"
        "- Nur der Arzt oder das Praxisteam bestätigt Termine.\n\n"
        "Notfall:\n"
        "Bei akuten Notfällen: Weise den Anrufer sofort an, den Notruf 144 zu wählen oder eine "
        "medizinische Notaufnahme aufzusuchen. Versuche nicht, selbst Triage durchzuführen.\n\n"
        "Ablauf:\n"
        "1. Begrüße den Anrufer freundlich.\n"
        "2. Frage nach dem Namen, dem Anliegen, der Rückrufnummer und dem gewünschten Termin.\n"
        "3. Bestätige die Anfrage und teile mit, dass das Praxisteam sich meldet.\n"
        "4. Verabschiede dich höflich."
    )


def _build_english_prompt(clinic_display_name: str, specialty: str, city: str) -> str:
    return (
        f"You are the AI receptionist for {clinic_display_name}, a private clinic in Vienna.\n\n"
        "Your task is to capture appointment requests. You collect the patient's name, "
        "callback phone number, reason for the appointment, and preferred time.\n\n"
        "Tone:\n"
        "- Polite and professional\n"
        "- Calm and clear\n"
        "- Clinic receptionist style\n"
        "- No exaggerated marketing language\n\n"
        "Language behaviour:\n"
        "- Conduct the conversation in English.\n"
        "- If the caller speaks German, switch to German.\n"
        "- Detect and adapt to the caller's preferred language.\n\n"
        "Boundaries — always enforced:\n"
        "- No diagnosis. Never suggest what condition the caller might have.\n"
        "- No medical advice. Do not recommend treatments, medications, or procedures.\n"
        "- Do not promise appointment confirmation. State that the clinic team will review and confirm.\n"
        "- Only the doctor or clinic team confirms appointments.\n\n"
        "Emergency:\n"
        "For urgent or life-threatening emergencies in Austria, instruct the caller to call 144 "
        "immediately or go to the nearest emergency department. Do not attempt triage.\n\n"
        "Workflow:\n"
        "1. Greet the caller warmly.\n"
        "2. Ask for their name, reason for the visit, callback number, and preferred appointment time.\n"
        "3. Confirm the request and let them know the clinic team will be in touch.\n"
        "4. Say goodbye politely."
    )


def _build_first_message_de(clinic_display_name: str) -> str:
    return (
        f"Guten Tag, Sie sind bei der KI-Rezeption von {clinic_display_name}. "
        "Wie kann ich Ihnen heute helfen?"
    )


def _build_first_message_en(clinic_display_name: str) -> str:
    return (
        f"Good day, you've reached the AI reception of {clinic_display_name}. "
        "How can I help you today?"
    )


def _voice_locale_for_mode(language_mode: str, primary_language: str) -> str:
    if language_mode == "english_first" or primary_language == "en":
        return "en-US"
    return "de-AT"


def _assistant_name_for_language(primary_language: str) -> str:
    return "Mia"


# ---------------------------------------------------------------------------
# Tenant config loader (safe, no secrets)
# ---------------------------------------------------------------------------


def _load_tenant_config(clinic_id: str) -> Dict[str, Any]:
    config_path = _TENANTS_DIR / clinic_id / "clinic_config.json"
    if not config_path.is_file():
        return {}
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def build_vapi_assistant_config_pack(
    pool: Any,
    clinic_id: str,
    actor_user: Optional[Any] = None,
) -> Dict[str, Any]:
    """Derive a safe, per-tenant Vapi assistant configuration pack.

    Reads clinic language settings and tenant config. No Vapi API calls.
    No secrets stored or returned. No PHI. production_phi_enabled is always False.

    Raises ClinicNotFoundError if the clinic does not exist.
    """
    # 1. Verify clinic exists + get display data from DB
    clinic_row = await pool.fetchrow(
        "SELECT id, name, slug, locale FROM clinics WHERE id = $1",
        clinic_id,
    )
    if clinic_row is None:
        raise ClinicNotFoundError(f"Clinic not found: {clinic_id}")

    db_clinic_name: str = str(clinic_row["name"])

    # 2. Load language settings
    lang_settings = await get_clinic_language_settings(pool=pool, clinic_id=clinic_id)

    # 3. Load safe tenant config for display fields (no secrets)
    tenant_cfg = _load_tenant_config(clinic_id)
    clinic_display_name: str = (
        tenant_cfg.get("clinic_display_name")
        or tenant_cfg.get("clinic_name")
        or db_clinic_name
    )
    specialty: str = tenant_cfg.get("specialty") or (
        ", ".join(tenant_cfg.get("specialties", []))
    ) or "Allgemeinmedizin"
    city: str = tenant_cfg.get("city") or "Wien"

    # 4. Derive language mode
    language_mode: str = lang_settings["vapi_assistant_language_mode"]
    primary_language: str = lang_settings["primary_language"]
    fallback_language: str = lang_settings["fallback_language"]
    supported_languages: list = lang_settings["supported_languages"]

    # 5. Build prompts
    system_prompt_de = _build_german_prompt(clinic_display_name, specialty, city)
    system_prompt_en = _build_english_prompt(clinic_display_name, specialty, city)
    first_message_de = _build_first_message_de(clinic_display_name)
    first_message_en = _build_first_message_en(clinic_display_name)

    assistant_name = _assistant_name_for_language(primary_language)
    voice_locale = _voice_locale_for_mode(language_mode, primary_language)

    return {
        "clinic_id": clinic_id,
        "clinic_display_name": clinic_display_name,
        "specialty": specialty,
        "city": city,
        "primary_language": primary_language,
        "fallback_language": fallback_language,
        "supported_languages": supported_languages,
        "vapi_assistant_language_mode": language_mode,
        "assistant_name": assistant_name,
        "voice_locale_recommendation": voice_locale,
        "first_message_de": first_message_de,
        "first_message_en": first_message_en,
        "system_prompt_de": system_prompt_de,
        "system_prompt_en": system_prompt_en,
        "tool_schema": _TOOL_SCHEMA,
        "required_capture_fields": list(_REQUIRED_CAPTURE_FIELDS),
        "safety_rules": list(_SAFETY_RULES),
        "escalation_rules": list(_ESCALATION_RULES),
        "forbidden_claims": list(_FORBIDDEN_CLAIMS),
        "production_phi_enabled": False,
        "recording_ingestion_enabled": bool(
            tenant_cfg.get("features", {}).get("recording_ingestion", False)
        ),
        "transcript_ingestion_enabled": bool(
            tenant_cfg.get("features", {}).get("transcript_ingestion", False)
        ),
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
    }
