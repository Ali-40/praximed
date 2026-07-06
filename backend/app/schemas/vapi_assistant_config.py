"""
Vapi Assistant Config Pack schema — PraxisMed Sprint 19 / Module 141.

Read model for GET /clinics/{clinic_id}/vapi-assistant-config-pack.

No PHI. No secrets. No Vapi API keys. No webhook secrets.
production_phi_enabled is always False.
recording_ingestion_enabled is always False unless explicitly enabled.
transcript_ingestion_enabled is always False unless explicitly enabled.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class VapiAssistantConfigPack(BaseModel):
    """Safe, per-tenant Vapi assistant configuration pack.

    Derived from clinic language settings and tenant config.
    No live Vapi binding. No secrets. No PHI.
    """

    clinic_id: str
    clinic_display_name: str
    specialty: str
    city: str

    # Language configuration
    primary_language: str
    fallback_language: str
    supported_languages: List[str]
    vapi_assistant_language_mode: str

    # Assistant identity
    assistant_name: str
    voice_locale_recommendation: str

    # First messages (language-specific greeting)
    first_message_de: str
    first_message_en: str

    # System prompts (language-specific)
    system_prompt_de: str
    system_prompt_en: str

    # Tool schema for appointment request capture
    tool_schema: Dict[str, Any]

    # Required fields the assistant must collect
    required_capture_fields: List[str]

    # Safety rules applied to this assistant
    safety_rules: List[str]

    # Escalation rules
    escalation_rules: List[str]

    # Claims the assistant must never make
    forbidden_claims: List[str]

    # Safety flags — these are always False in the generated config pack
    production_phi_enabled: bool = False
    recording_ingestion_enabled: bool = False
    transcript_ingestion_enabled: bool = False

    # Metadata
    generated_at: Optional[str] = None
