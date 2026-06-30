"""
Vapi phone-agent prompt builder — PraxisMed Sprint 1 / Module 11

Builds the system prompt and supplementary context that are passed to the
Vapi voice agent at call start.  No external API calls are made here.
"""

from __future__ import annotations

import json
from typing import Any, Dict


def build_vapi_system_prompt(config: Any) -> str:
    """
    Build a safe, German-first phone receptionist system prompt using the
    clinic config.

    The prompt instructs the voice agent on:
    - language, tone, and persona
    - hard safety rules (no diagnosis, no treatment advice)
    - appointment booking flow
    - availability checking requirement
    - escalation rules from config
    """
    clinic_name = config.clinic_name
    locale = f"{config.language}-{config.country}"
    timezone = config.timezone
    ai_tone = config.ai_tone
    persona = config.ai_persona_name

    extra = config.extra or {}
    faqs = extra.get("faqs", [])
    escalation_rules = extra.get("escalation_rules", [])
    voice_prompt = extra.get("voice_prompt", "")

    opening_hours = config.opening_hours or {}
    calendar_rules = config.calendar_rules or {}

    # Opening hours block
    if opening_hours:
        oh_lines = []
        for day, hours in opening_hours.items():
            if hours:
                oh_lines.append(f"  {day.capitalize()}: {hours.get('open', '?')}–{hours.get('close', '?')}")
            else:
                oh_lines.append(f"  {day.capitalize()}: geschlossen")
        oh_block = "Öffnungszeiten:\n" + "\n".join(oh_lines)
    else:
        oh_block = "Öffnungszeiten: nicht konfiguriert"

    # Calendar rules block
    if calendar_rules:
        cr_block = "Terminregeln: " + json.dumps(calendar_rules, ensure_ascii=False)
    else:
        cr_block = ""

    # FAQs block
    if faqs:
        faq_lines = "\n".join(f"- {q}" for q in faqs)
        faq_block = f"Häufige Fragen (FAQ):\n{faq_lines}"
    else:
        faq_block = ""

    # Escalation block
    if escalation_rules:
        esc_lines = "\n".join(f"- {r}" for r in escalation_rules)
        esc_block = f"Eskalationsregeln:\n{esc_lines}"
    else:
        esc_block = (
            "Eskalationsregeln:\n"
            "- Bei Notfällen oder lebensbedrohlichen Symptomen sofort an den Notruf (144) verweisen.\n"
            "- Bei dringenden medizinischen Fragen an das Praxispersonal weitergeben."
        )

    # Voice prompt
    vp_block = f"\n{voice_prompt}" if voice_prompt else ""

    sections = [
        s for s in [oh_block, cr_block, faq_block, esc_block, vp_block] if s
    ]
    supplementary = "\n\n".join(sections)

    prompt = f"""\
Du bist {persona}, die KI-Telefonrezeptionistin der Praxis „{clinic_name}".
Locale: {locale} | Zeitzone: {timezone} | Tonalität: {ai_tone}

SPRACHREGELN:
- Sprich klares, professionelles österreichisches Deutsch.
- Halte Antworten kurz und präzise.
- Stelle immer nur eine Frage auf einmal.

SICHERHEITSREGELN (nicht verhandelbar):
- Stelle keine Diagnosen und gib keine Behandlungsempfehlungen.
- Versprich keinen Termin, bevor du die Verfügbarkeit geprüft hast.
- Bei Notfällen oder akuten Beschwerden: Eskaliere sofort gemäß den Eskalationsregeln.
- Wenn du unsicher bist, übergib das Gespräch an das Praxispersonal.

TERMINBUCHUNGS-ABLAUF:
1. Erfasse vollständigen Namen des Patienten.
2. Erfasse Telefonnummer.
3. Erfasse Geburtsdatum, wenn die Praxis es verlangt.
4. Erfasse den Grund des Termins.
5. Erfasse das bevorzugte Zeitfenster.
6. Prüfe die Verfügbarkeit über das Verfügbarkeits-Tool, BEVOR du einen Termin anbietest.
7. Falls kein Slot verfügbar ist, biete alternative Zeiten an oder erstelle eine Rückrufanfrage.

{supplementary}""".strip()

    return prompt


def build_vapi_tool_instructions() -> str:
    """
    Return compact instructions explaining when the voice agent should call
    the availability check tool and the slot suggestion tool.
    """
    return (
        "TOOL-ANWEISUNGEN:\n"
        "- check_availability: Rufe dieses Tool auf, sobald ein Patient einen "
        "konkreten Wunschtermin nennt. Übergib Startzeit, Endzeit und clinic_ref. "
        "Biete den Termin NUR an, wenn das Tool 'available: true' zurückgibt.\n"
        "- suggest_slots: Rufe dieses Tool auf, wenn der Patient kein konkretes "
        "Zeitfenster hat oder der gewünschte Termin nicht verfügbar ist. "
        "Übergib das Wunschdatum und clinic_ref. Präsentiere die vorgeschlagenen "
        "Slots dem Patienten zur Auswahl. Wenn keine Slots verfügbar sind, "
        "biete einen Rückruf an."
    )


def build_vapi_clinic_context(config: Any) -> Dict[str, Any]:
    """
    Return structured, non-patient clinic context for Vapi.

    Contains only static clinic metadata — no patient data, no secrets.
    """
    extra = config.extra or {}
    return {
        "clinic_id":        config.tenant_id,
        "clinic_name":      config.clinic_name,
        "locale":           f"{config.language}-{config.country}",
        "timezone":         config.timezone,
        "opening_hours":    config.opening_hours or {},
        "calendar_rules":   config.calendar_rules or {},
        "faqs":             extra.get("faqs", []),
        "escalation_rules": extra.get("escalation_rules", []),
    }
