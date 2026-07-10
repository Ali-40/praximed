#!/usr/bin/env python3
"""
praximed_outreach_copilot.py

PraxisMed Outreach Copilot — local AI-assisted sales operations tool.

Reads existing outreach tracker CSV, prioritizes leads, and writes daily
call/email/walk-in plans, German email drafts, follow-up tasks, and
sales reports for manual review by Ali.

RESPONSIBLE USE:
- Reads only publicly visible practice contact details.
- No private data. No patient data. No PHI.
- NEVER sends emails automatically.
- NEVER makes phone calls automatically.
- All output is for manual human review before any action.
- Respects Do not contact / Not interested flags.
- No DSGVO certified claims. No Diagnose claims. No Beratung claims.

Usage:
  # Full daily plan (all modes):
  python scripts/sales/praximed_outreach_copilot.py \\
      --input docs/sales/outreach/praxisplan_all_high_potential_leads.csv \\
      --daily-limit 25

  # One specialty only:
  python scripts/sales/praximed_outreach_copilot.py \\
      --input docs/sales/outreach/praxisplan_all_high_potential_leads.csv \\
      --specialty dermatology --daily-limit 15

  # One mode only:
  python scripts/sales/praximed_outreach_copilot.py \\
      --input docs/sales/outreach/praxisplan_all_high_potential_leads.csv \\
      --mode drafts

  # Tier 1 only:
  python scripts/sales/praximed_outreach_copilot.py \\
      --input docs/sales/outreach/praxisplan_all_high_potential_leads.csv \\
      --tier 1 --daily-limit 25
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from collections import Counter
from datetime import date, datetime, timedelta
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TODAY = date.today().isoformat()
DEFAULT_OUTPUT_DIR = "docs/sales/outreach/daily_plans"
DEFAULT_DAILY_LIMIT = 25

EXCLUDED_STATUSES = {"Do not contact", "Not interested", "Demo booked", "Wrong target"}

TIER_PRIORITY = {"1": 3, "2": 2, "3": 1}

# Specialty-specific phone pain points
SPECIALTY_PAIN_POINTS: dict[str, str] = {
    "child_adolescent_psychiatry": (
        "Gerade bei vielen Anfragen von Eltern kann es schwer sein, "
        "Rückrufe sauber zu organisieren."
    ),
    "dermatology": (
        "Viele Hautarztpraxen haben viele Terminanfragen, Rückfragen "
        "und Rückrufe rund um Behandlungen und Kontrollen."
    ),
    "gynecology": (
        "Viele Patientinnen rufen wegen Terminen, Rückfragen oder "
        "Verschiebungen an. PraxisMed hilft, diese Rückrufe sauber zu sortieren."
    ),
    "orthopedics": (
        "Viele Patienten rufen wegen Beschwerden und Terminwünschen an. "
        "PraxisMed nimmt die Anfrage auf, ohne medizinisch zu bewerten."
    ),
    "internal_medicine": (
        "Viele Patienten bevorzugen weiterhin das Telefon. "
        "PraxisMed hilft, diese Anfragen übersichtlich zu organisieren."
    ),
    "ent": (
        "HNO-Praxen haben oft viele Anfragen rund um Termin­koordination. "
        "PraxisMed nimmt Rückrufwünsche sauber auf."
    ),
    "urology": (
        "Patienten rufen häufig wegen Terminwünschen und Rückfragen an. "
        "PraxisMed sortiert diese Anfragen übersichtlich für Ihr Team."
    ),
    "neurology": (
        "Neurologische Praxen haben oft komplexe Anfragen und Rückrufwünsche. "
        "PraxisMed hilft, diese strukturiert aufzunehmen."
    ),
    "ophthalmology": (
        "Augenarztpraxen haben viele Anfragen rund um Kontrollen und Termine. "
        "PraxisMed organisiert Rückrufwünsche übersichtlich."
    ),
    "pediatrics": (
        "Eltern rufen häufig mit Fragen zu Terminen und Rückrufen an. "
        "PraxisMed nimmt diese Anfragen strukturiert auf."
    ),
    "private_dental": (
        "Viele Patientinnen und Patienten rufen wegen Terminen und "
        "Rückfragen an — PraxisMed hilft, diese sauber zu organisieren."
    ),
    "aesthetic_medicine": (
        "Anfragen zu ästhetischen Behandlungen kommen oft per Telefon. "
        "PraxisMed nimmt Rückrufwünsche diskret und sauber auf."
    ),
    "plastic_surgery": (
        "Patienten informieren sich häufig telefonisch vor einer Behandlung. "
        "PraxisMed hilft, diese Anfragen übersichtlich zu erfassen."
    ),
    "adult_psychiatry": (
        "Psychiatrische Praxen erhalten viele sensible Anfragen. "
        "PraxisMed nimmt Rückrufwünsche diskret auf, ohne medizinisch zu bewerten."
    ),
    "private_group_practices": (
        "Gruppenpraxen koordinieren Anfragen für mehrere Ärzte gleichzeitig. "
        "PraxisMed hilft, Rückrufe strukturiert zu verwalten."
    ),
}

DEFAULT_PAIN_POINT = (
    "Viele Praxen haben viele eingehende Anfragen, die schwer zu organisieren sind. "
    "PraxisMed hilft, Rückrufwünsche übersichtlich zu sortieren."
)

# Email subject lines by specialty
SPECIALTY_SUBJECTS: dict[str, str] = {
    "child_adolescent_psychiatry": "Wie Ihre Praxis Eltern-Rückrufe sauber organisiert",
    "dermatology": "Wie Ihre Praxis Rückruf-Anfragen übersichtlich organisiert",
    "gynecology": "Wie Ihre Praxis Patientinnen-Rückrufe sauber sortiert",
    "orthopedics": "Wie Ihre Praxis Terminanfragen einfacher verwaltet",
    "internal_medicine": "Wie Ihre Praxis Rückruf-Anfragen strukturiert abarbeitet",
    "ent": "Wie Ihre HNO-Praxis Rückrufe übersichtlich organisiert",
    "urology": "Wie Ihre Praxis Patientenanfragen sauber sortiert",
    "neurology": "Wie Ihre Praxis Rückrufwünsche strukturiert aufnimmt",
    "ophthalmology": "Wie Ihre Praxis Anfragen und Rückrufe einfacher verwaltet",
    "pediatrics": "Wie Ihre Praxis Eltern-Rückrufe einfacher organisiert",
    "adult_psychiatry": "Wie Ihre Praxis Rückrufwünsche diskret und sauber aufnimmt",
    "aesthetic_medicine": "Wie Ihre Praxis Anfragen zu Behandlungen sauber erfasst",
    "plastic_surgery": "Wie Ihre Praxis Patientenanfragen übersichtlich sortiert",
    "private_dental": "Wie Ihre Praxis Terminanfragen sauber organisiert",
    "private_group_practices": "Wie Ihre Gruppenpraxis Rückrufe strukturiert verwaltet",
}

DEFAULT_SUBJECT = "Wie Ihre Praxis verpasste Anrufe automatisch zurückruft"

LATIDO_NOTE = (
    "Falls Sie bereits LATIDO oder ein anderes Praxissystem nutzen — "
    "PraxisMed ersetzt das nicht. Es hilft davor: Rückrufwünsche und "
    "Telefonanfragen werden sauber aufgenommen, Ihr Team trägt bestätigte "
    "Termine wie gewohnt ins System ein."
)

EMAIL_SIGNATURE = "Mit freundlichen Grüßen\nAli Abdeltawab\nPraxisMed\n"

# ---------------------------------------------------------------------------
# Lead loading
# ---------------------------------------------------------------------------

def load_leads(csv_path: str) -> list[dict]:
    with open(csv_path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def filter_leads(
    leads: list[dict],
    specialty: Optional[str] = None,
    tier: Optional[str] = None,
    exclude_statuses: set[str] = EXCLUDED_STATUSES,
) -> list[dict]:
    result = []
    for lead in leads:
        status = lead.get("Outreach Status", "")
        if status in exclude_statuses:
            continue
        if specialty and lead.get("Specialty Key", "") != specialty:
            continue
        if tier and lead.get("Specialty Tier", "") != tier:
            continue
        result.append(lead)
    return result


def score_lead(lead: dict) -> int:
    """Higher = more actionable. Used for daily plan ordering."""
    score = 0
    tier = lead.get("Specialty Tier", "3")
    score += TIER_PRIORITY.get(tier, 1) * 10

    if lead.get("Phone"):
        score += 8
    if lead.get("Email"):
        score += 4
    if lead.get("Website"):
        score += 2
    if lead.get("City", "").lower() in ("wien", "vienna"):
        score += 5

    raw_score = lead.get("Priority Score", "")
    try:
        score += int(raw_score) * 2
    except (ValueError, TypeError):
        pass

    status = lead.get("Outreach Status", "")
    if status == "Not contacted":
        score += 3
    elif status in ("Called", "No answer"):
        score += 1

    return score


def _name(lead: dict) -> str:
    return lead.get("Doctor Name") or lead.get("Practice Name") or "Unbekannte Praxis"


def _salutation(lead: dict) -> str:
    name = lead.get("Doctor Name", "")
    title = lead.get("Title", "")
    if title and name:
        last = name.split()[-1] if name else ""
        return f"Sehr geehrte/r {title} {last}"
    if name:
        last = name.split()[-1]
        return f"Sehr geehrte/r Frau/Herr {last}"
    return "Guten Tag"


def _pain_point(lead: dict) -> str:
    key = lead.get("Specialty Key", "")
    return SPECIALTY_PAIN_POINTS.get(key, DEFAULT_PAIN_POINT)


def _subject(lead: dict) -> str:
    key = lead.get("Specialty Key", "")
    return SPECIALTY_SUBJECTS.get(key, DEFAULT_SUBJECT)


def _likely_objection(lead: dict) -> str:
    status = lead.get("Outreach Status", "")
    key = lead.get("Specialty Key", "")
    likely_latido = lead.get("Likely LATIDO / Online Booking", "Unknown")

    if likely_latido == "Yes":
        return "Wir haben bereits LATIDO / ein System"
    if status == "Asked to send email":
        return "Schicken Sie uns eine E-Mail"
    if key in ("adult_psychiatry", "private_group_practices"):
        return "Keine Zeit / Kein Bedarf"
    if lead.get("Priority Score", "") in ("1", "2"):
        return "Kein Interesse"
    return "Schicken Sie uns eine E-Mail / Keine Zeit"


# ---------------------------------------------------------------------------
# Plan mode
# ---------------------------------------------------------------------------

def select_call_leads(leads: list[dict], limit: int) -> list[dict]:
    eligible = [l for l in leads if l.get("Phone")]
    return sorted(eligible, key=score_lead, reverse=True)[:limit]


def select_email_leads(leads: list[dict], limit: int) -> list[dict]:
    eligible = [l for l in leads if (l.get("Email") or l.get("Website")) and not l.get("Phone")]
    all_with_email = sorted(eligible, key=score_lead, reverse=True)
    # Also include phone leads that also have email, after call leads
    phone_with_email = [l for l in leads if l.get("Phone") and (l.get("Email") or l.get("Website"))]
    phone_with_email = sorted(phone_with_email, key=score_lead, reverse=True)
    combined = all_with_email + [l for l in phone_with_email if l not in all_with_email]
    return combined[:limit]


def select_walkin_leads(leads: list[dict], limit: int) -> list[dict]:
    eligible = [
        l for l in leads
        if l.get("Address") and l.get("City", "").lower() in ("wien", "vienna")
        and not l.get("Phone")
    ]
    return sorted(eligible, key=score_lead, reverse=True)[:limit]


def generate_phone_script(lead: dict) -> str:
    name = _name(lead)
    pain = _pain_point(lead)
    phone = lead.get("Phone", "")

    lines = [
        f"**Telefon-Skript für: {name}**",
        f"Nummer: {phone}",
        "",
        "**Eröffnung:**",
        "Guten Tag, mein Name ist Ali Abdeltawab von PraxisMed. "
        "Darf ich kurz mit der Praxisleitung oder dem/der behandelnden Arzt/Ärztin sprechen?",
        "",
        "**Wenn Rezeption:**",
        f"Ich wollte kurz vorstellen, wie PraxisMed Ihrer Praxis helfen kann. "
        f"{pain} Hätten Sie zwei Minuten?",
        "",
        "**Kern-Pitch:**",
        "PraxisMed nimmt Terminanfragen und Rückrufwünsche auf, sortiert diese "
        "übersichtlich und hilft Ihrem Team, Anfragen sauber abzuarbeiten. "
        "Wir ersetzen kein bestehendes System wie LATIDO — wir helfen nur davor.",
        "",
        "**Demo-Anfrage:**",
        "Darf ich Ihnen eine kurze 5-Minuten-Demo zeigen? "
        "Entweder per Videocall oder ich komme kurz vorbei.",
        "",
        "**Wenn: Schicken Sie uns eine E-Mail:**",
        f"Sehr gerne. An welche E-Mail-Adresse darf ich schreiben? "
        "[E-Mail-Adresse notieren → Manuell als Draft verfassen und senden]",
        "",
        "**Wenn: Kein Interesse:**",
        "Verstehe, danke für Ihre ehrliche Antwort. "
        "Darf ich fragen, ob Sie bereits eine Lösung für Rückruf-Anfragen haben?",
        "",
        "**Wenn: Was kostet das?**",
        "Das hängt von der Praxisgröße ab. In der Demo zeige ich Ihnen auch das. "
        "Für kleinere Praxen beginnt es ab ca. €290/Monat.",
        "",
        "**Wenn: Wir haben LATIDO / ein anderes System:**",
        "Perfekt — dann müssen wir LATIDO nicht ersetzen. "
        "PraxisMed organisiert nur den Telefon- und Rückruf-Teil davor. "
        "Ihr Team trägt bestätigte Termine wie gewohnt in LATIDO ein.",
        "",
        "**Wenn: Wann kann man anrufen?**",
        "Notiere bevorzugte Zeit: [Best Time to Call im Tracker eintragen]",
    ]
    return "\n".join(lines)


def generate_plan_md(
    call_leads: list[dict],
    email_leads: list[dict],
    walkin_leads: list[dict],
    total_leads: int,
    not_contacted: int,
) -> str:
    sections = [
        f"# PraxisMed Tagesplan — {TODAY}",
        "",
        f"**Gesamte Leads:** {total_leads} | "
        f"**Noch nicht kontaktiert:** {not_contacted} | "
        f"**Anrufe heute:** {len(call_leads)} | "
        f"**E-Mails heute:** {len(email_leads)} | "
        f"**Walk-ins heute:** {len(walkin_leads)}",
        "",
        "> Alle Kontaktversuche sind manuell. Kein Auto-Email. Kein Auto-Call.",
        "",
    ]

    # Call leads
    sections += [
        "---",
        "## Anruf-Liste (priorisiert)",
        "",
        "| # | Name | Specialty | Priorität | Phone | Objection likely | Opening line |",
        "|---|---|---|---|---|---|---|",
    ]
    for i, lead in enumerate(call_leads, 1):
        name = _name(lead)
        spec = lead.get("Specialty Label DE", lead.get("Specialty Key", ""))[:30]
        prio = lead.get("Priority Score", "?")
        phone = lead.get("Phone", "—")
        obj = _likely_objection(lead)
        opening = _pain_point(lead)[:60] + "…"
        sections.append(f"| {i} | {name} | {spec} | {prio} | {phone} | {obj} | {opening} |")

    sections += [
        "",
        "---",
        "## E-Mail / Kontaktformular-Liste",
        "",
        "| # | Name | Specialty | Website/Email | Priorität | Subject |",
        "|---|---|---|---|---|---|",
    ]
    for i, lead in enumerate(email_leads, 1):
        name = _name(lead)
        spec = lead.get("Specialty Label DE", lead.get("Specialty Key", ""))[:30]
        contact = lead.get("Email") or lead.get("Website") or "—"
        prio = lead.get("Priority Score", "?")
        subj = _subject(lead)
        sections.append(f"| {i} | {name} | {spec} | {contact} | {prio} | {subj} |")

    if walkin_leads:
        sections += [
            "",
            "---",
            "## Walk-in Kandidaten",
            "",
            "| # | Name | Adresse | Bezirk | Specialty |",
            "|---|---|---|---|---|",
        ]
        for i, lead in enumerate(walkin_leads, 1):
            name = _name(lead)
            addr = lead.get("Address", "—")
            district = lead.get("District", "—")
            spec = lead.get("Specialty Label DE", "")[:30]
            sections.append(f"| {i} | {name} | {addr} | {district} | {spec} |")

    # Phone scripts
    sections += [
        "",
        "---",
        "## Telefon-Skripte",
        "",
    ]
    for lead in call_leads[:10]:
        sections.append(generate_phone_script(lead))
        sections.append("")
        sections.append("---")
        sections.append("")

    sections += [
        "## Update-Anleitung",
        "",
        "Nach jedem Anruf sofort im Master-Tracker eintragen:",
        "1. Outreach Status setzen",
        "2. Call Attempt 1 Date = heute",
        "3. Call Attempt 1 Result = Ergebnis aus Dropdown",
        "4. Contact Person = Name Rezeption/Arzt",
        "5. Follow-up Date setzen falls nötig",
        "6. Demo Offered / Demo Booked anpassen",
        "7. Objection notieren",
        "8. Notes ausfüllen",
        "",
        "> **Master-Tracker:** `docs/sales/outreach/praxisplan_all_high_potential_leads.xlsx`",
    ]

    return "\n".join(sections)


def generate_call_list_csv(call_leads: list[dict], email_leads: list[dict]) -> str:
    cols = [
        "Lead ID", "Doctor Name", "Specialty Label DE", "Specialty Tier",
        "Phone", "Email", "Website", "Address", "District",
        "Priority Score", "Priority Reason", "Outreach Status",
        "Likely Objection", "Opening Line",
    ]
    rows_out = []
    for lead in call_leads + email_leads:
        rows_out.append({
            "Lead ID": lead.get("Lead ID", ""),
            "Doctor Name": _name(lead),
            "Specialty Label DE": lead.get("Specialty Label DE", ""),
            "Specialty Tier": lead.get("Specialty Tier", ""),
            "Phone": lead.get("Phone", ""),
            "Email": lead.get("Email", ""),
            "Website": lead.get("Website", ""),
            "Address": lead.get("Address", ""),
            "District": lead.get("District", ""),
            "Priority Score": lead.get("Priority Score", ""),
            "Priority Reason": lead.get("Priority Reason", ""),
            "Outreach Status": lead.get("Outreach Status", ""),
            "Likely Objection": _likely_objection(lead),
            "Opening Line": _pain_point(lead),
        })
    import io
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=cols)
    writer.writeheader()
    writer.writerows(rows_out)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Drafts mode
# ---------------------------------------------------------------------------

def generate_email_draft(lead: dict) -> str:
    salutation = _salutation(lead)
    name = _name(lead)
    spec = lead.get("Specialty Label DE", "")
    subj = _subject(lead)
    pain = _pain_point(lead)

    body_lines = [
        f"### {name}",
        f"**Fachgebiet:** {spec}",
        f"**Lead ID:** {lead.get('Lead ID', '—')}",
        f"**E-Mail / Website:** {lead.get('Email') or lead.get('Website') or '—'}",
        "",
        f"**Betreff:** {subj}",
        "",
        "**E-Mail-Text:**",
        "```",
        f"{salutation},",
        "",
        f"mein Name ist Ali Abdeltawab. Ich baue PraxisMed, eine einfache "
        f"KI-Rezeption für Wiener Privatpraxen.",
        "",
        pain,
        "",
        "PraxisMed nimmt Terminanfragen auf, sortiert Rückrufe und hilft Ihrem "
        "Praxisteam, Anfragen sauber abzuarbeiten.",
        "",
        LATIDO_NOTE,
        "",
        "Die KI bestätigt keine Termine, stellt keine Diagnosen und gibt keine "
        "medizinische Beratung. Ihr Team bleibt immer in Kontrolle.",
        "",
        "Darf ich Ihnen eine kurze 5-Minuten-Demo zeigen?",
        "",
        EMAIL_SIGNATURE,
        "```",
        "",
        "**Kurz-Version (für Kontaktformular):**",
        "```",
        f"Guten Tag, mein Name ist Ali von PraxisMed. "
        f"Ich baue eine einfache KI-Rezeption für Wiener Privatpraxen — "
        f"für Rückruf-Anfragen und Telefonorganisation, ohne Ihr bestehendes System zu ersetzen. "
        f"Darf ich Ihnen 5 Minuten Demo zeigen? "
        f"Danke, Ali Abdeltawab — praximed.at",
        "```",
        "",
        "---",
    ]
    return "\n".join(body_lines)


def generate_drafts_md(leads: list[dict]) -> str:
    sections = [
        f"# PraxisMed E-Mail Drafts — {TODAY}",
        "",
        "> **WICHTIG:** Diese Drafts sind NUR zur manuellen Überprüfung. "
        "> Kein E-Mail wird automatisch gesendet. "
        "> Jeden Draft vor dem Senden persönlich überprüfen und anpassen.",
        "",
        f"**{len(leads)} Drafts**",
        "",
        "---",
        "",
    ]
    for lead in leads:
        sections.append(generate_email_draft(lead))
        sections.append("")
    return "\n".join(sections)


# ---------------------------------------------------------------------------
# Follow-ups mode
# ---------------------------------------------------------------------------

def get_followup_leads(leads: list[dict]) -> list[dict]:
    today = date.today()
    result = []

    for lead in leads:
        status = lead.get("Outreach Status", "")
        email_result = lead.get("Email Result", "")
        call1_result = lead.get("Call Attempt 1 Result", "")
        demo_offered = lead.get("Demo Offered", "No")
        demo_booked = lead.get("Demo Booked", "No")
        followup_date_str = lead.get("Follow-up Date", "")

        needs_followup = False
        reason = ""

        if status == "Asked to send email":
            needs_followup = True
            reason = "Sie haben gebeten, eine E-Mail zu senden"
        elif status == "Follow-up needed":
            needs_followup = True
            reason = "Follow-up steht aus"
        elif email_result == "Sent":
            needs_followup = True
            reason = "E-Mail gesendet — noch keine Antwort"
        elif call1_result == "Call later":
            needs_followup = True
            reason = "Haben gebeten, später anzurufen"
        elif demo_offered == "Yes" and demo_booked == "No":
            needs_followup = True
            reason = "Demo angeboten aber noch nicht gebucht"

        if followup_date_str:
            try:
                followup_date = date.fromisoformat(followup_date_str)
                if followup_date > today:
                    continue  # Not due yet
            except ValueError:
                pass

        if needs_followup:
            result.append((lead, reason))

    return result


def generate_followups_md(followup_pairs: list[tuple]) -> str:
    if not followup_pairs:
        return (
            f"# PraxisMed Follow-ups — {TODAY}\n\n"
            "Keine offenen Follow-ups für heute.\n"
        )

    sections = [
        f"# PraxisMed Follow-ups — {TODAY}",
        "",
        f"**{len(followup_pairs)} offene Follow-ups**",
        "",
        "> Jeden Follow-up manuell durchführen. Kein Auto-Call. Kein Auto-Email.",
        "",
        "---",
        "",
    ]

    for lead, reason in followup_pairs:
        name = _name(lead)
        phone = lead.get("Phone", "—")
        email = lead.get("Email", "—")
        status = lead.get("Outreach Status", "")
        followup_date = lead.get("Follow-up Date", "—")
        spec = lead.get("Specialty Label DE", "")

        sections += [
            f"### {name}",
            f"**Lead ID:** {lead.get('Lead ID', '—')} | "
            f"**Fachgebiet:** {spec} | "
            f"**Status:** {status}",
            f"**Warum Follow-up:** {reason}",
            f"**Telefon:** {phone} | **E-Mail:** {email}",
            f"**Follow-up Datum:** {followup_date}",
            "",
            "**Empfohlene Nachricht:**",
        ]

        status = lead.get("Outreach Status", "")
        if status == "Asked to send email":
            sections.append(
                f"> Guten Tag, hier ist Ali Abdeltawab von PraxisMed. "
                f"Wie besprochen schicke ich Ihnen kurze Infos zu unserem Angebot. "
                f"Darf ich Ihnen eine 5-Minuten-Demo anbieten?"
            )
        elif lead.get("Demo Offered") == "Yes" and lead.get("Demo Booked") == "No":
            sections.append(
                f"> Guten Tag, hier ist Ali. Ich wollte kurz nachfragen, "
                f"ob Sie Zeit für eine 5-Minuten-Demo von PraxisMed hätten."
            )
        else:
            sections.append(
                f"> Guten Tag, Ali Abdeltawab von PraxisMed. "
                f"Ich wollte kurz nachfragen, ob Sie Interesse an einer kurzen Demo haben."
            )

        sections += [
            "",
            f"**Nächste Aktion:** {lead.get('Next Action', 'Manuell prüfen')}",
            "",
            "---",
            "",
        ]

    return "\n".join(sections)


# ---------------------------------------------------------------------------
# Report mode
# ---------------------------------------------------------------------------

def generate_report_md(
    all_leads: list[dict],
    filtered_leads: list[dict],
    top_next: list[dict],
) -> str:
    status_counts: Counter = Counter(l.get("Outreach Status", "") for l in all_leads)
    tier_remaining: Counter = Counter(
        l.get("Specialty Tier", "?")
        for l in all_leads
        if l.get("Outreach Status", "") not in EXCLUDED_STATUSES
    )
    specialty_remaining: Counter = Counter(
        l.get("Specialty Label DE", "?")
        for l in all_leads
        if l.get("Outreach Status", "") not in EXCLUDED_STATUSES
        and l.get("Outreach Status", "") == "Not contacted"
    )

    total = len(all_leads)
    not_contacted = status_counts.get("Not contacted", 0)
    called = sum(v for k, v in status_counts.items()
                 if k in ("Called", "No answer", "Reception reached", "Asked to send email"))
    emailed = status_counts.get("Email sent", 0) + status_counts.get("Asked to send email", 0)
    interested = sum(v for k, v in status_counts.items()
                     if k in ("Interested", "Demo offered"))
    demo_booked = status_counts.get("Demo booked", 0)
    not_interested = status_counts.get("Not interested", 0)
    do_not_contact = status_counts.get("Do not contact", 0)

    sections = [
        f"# PraxisMed Outreach Report — {TODAY}",
        "",
        "## Gesamtübersicht",
        "",
        f"| Metrik | Anzahl |",
        f"|---|---|",
        f"| Gesamt Leads | {total} |",
        f"| Noch nicht kontaktiert | {not_contacted} |",
        f"| Angerufen (alle Versuche) | {called} |",
        f"| E-Mail gesendet / angefragt | {emailed} |",
        f"| Interessiert / Demo angeboten | {interested} |",
        f"| Demo gebucht | {demo_booked} |",
        f"| Kein Interesse | {not_interested} |",
        f"| Do not contact | {do_not_contact} |",
        "",
        "## Verbleibende Leads nach Tier",
        "",
        "| Tier | Offen |",
        "|---|---|",
    ]
    for tier in ["1", "2", "3"]:
        sections.append(f"| Tier {tier} | {tier_remaining.get(tier, 0)} |")

    sections += [
        "",
        "## Top Specialties (nicht kontaktiert)",
        "",
        "| Fachgebiet | Offen |",
        "|---|---|",
    ]
    for spec, count in specialty_remaining.most_common(10):
        sections.append(f"| {spec} | {count} |")

    sections += [
        "",
        "## Empfohlene nächste 25 Leads",
        "",
        "| # | Name | Specialty | Tier | Prio | Telefon | Status |",
        "|---|---|---|---|---|---|---|",
    ]
    for i, lead in enumerate(top_next[:25], 1):
        sections.append(
            f"| {i} | {_name(lead)} | "
            f"{lead.get('Specialty Label DE', '')[:28]} | "
            f"{lead.get('Specialty Tier', '')} | "
            f"{lead.get('Priority Score', '')} | "
            f"{lead.get('Phone', '—')} | "
            f"{lead.get('Outreach Status', '')} |"
        )

    sections += [
        "",
        "---",
        "> Kein Auto-Email. Kein Auto-Call. "
        "Alle Kontaktversuche sind manuell und individuell.",
    ]
    return "\n".join(sections)


# ---------------------------------------------------------------------------
# Update instructions
# ---------------------------------------------------------------------------

def generate_update_instructions_md() -> str:
    return f"""\
# Master-Tracker Update-Anleitung — {TODAY}

> Jeden Kontaktversuch sofort nach dem Anruf/E-Mail im Master-Tracker eintragen.
> **Master-Tracker:** `docs/sales/outreach/praxisplan_all_high_potential_leads.xlsx`

---

## Nach jedem Anruf

| Feld | Was eintragen |
|---|---|
| Outreach Status | Dropdown: Called / No answer / Reception reached / Asked to send email / Interested / Not interested / Do not contact |
| Call Attempt 1 Date | Datum: {TODAY} |
| Call Attempt 1 Result | Dropdown: No answer / Busy / Reception reached / Doctor unavailable / Asked to send email / Interested / Not interested / Call later / Demo booked |
| Contact Person | Name der Rezeptionsperson / des Arztes |
| Best Time to Call | Falls angegeben |
| Follow-up Date | Falls ein Rückruf vereinbart |
| Demo Offered | Yes / No |
| Demo Booked | Yes / No |
| Objection | Haupteinwand, z.B. "Wir haben LATIDO" |
| Notes | Kurze Notiz zum Gespräch |
| Last Updated | {TODAY} |

## Nach jeder E-Mail

| Feld | Was eintragen |
|---|---|
| Outreach Status | Email sent |
| Email Sent Date | {TODAY} |
| Email Result | Sent |
| Notes | An welche Adresse gesendet |
| Last Updated | {TODAY} |

## Falls Klinik abgelehnt

| Feld | Was eintragen |
|---|---|
| Outreach Status | **Do not contact** |
| Notes | Grund notieren |

---

> **Wichtig:** Outreach Status = "Do not contact" bedeutet: nie wieder kontaktieren.
> Das wird bei der nächsten Plan-Generierung automatisch ausgeschlossen.
"""


# ---------------------------------------------------------------------------
# File I/O helpers
# ---------------------------------------------------------------------------

def _out(output_dir: str, filename: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, filename)


def write_text(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Wrote: {path}")


def write_csv(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        f.write(content)
    print(f"  Wrote: {path}")


# ---------------------------------------------------------------------------
# Modes
# ---------------------------------------------------------------------------

def run_plan(
    leads: list[dict],
    filtered: list[dict],
    output_dir: str,
    daily_limit: int,
) -> None:
    half = daily_limit // 2
    rest = daily_limit - half

    call_leads = select_call_leads(filtered, half + 5)
    email_leads = select_email_leads(filtered, rest + 5)
    walkin_leads = select_walkin_leads(filtered, 5)

    total = len(leads)
    not_contacted = sum(1 for l in leads if l.get("Outreach Status") == "Not contacted")

    plan_md = generate_plan_md(
        call_leads[:half], email_leads[:rest], walkin_leads, total, not_contacted
    )
    call_csv = generate_call_list_csv(call_leads[:half], email_leads[:rest])
    update_md = generate_update_instructions_md()

    write_text(_out(output_dir, f"{TODAY}_daily_outreach_plan.md"), plan_md)
    write_csv(_out(output_dir, f"{TODAY}_call_list.csv"), call_csv)
    write_text(_out(output_dir, f"{TODAY}_update_instructions.md"), update_md)


def run_drafts(filtered: list[dict], output_dir: str, daily_limit: int) -> None:
    # Prefer leads with email/website, but fall back to all leads so Ali
    # can use the draft for contact forms found via the Praxisplan profile URL.
    preferred = [l for l in filtered if l.get("Email") or l.get("Website")]
    fallback = [l for l in filtered if not l.get("Email") and not l.get("Website")]
    candidates = sorted(preferred, key=score_lead, reverse=True)
    if len(candidates) < daily_limit:
        candidates += sorted(fallback, key=score_lead, reverse=True)[: daily_limit - len(candidates)]
    candidates = candidates[:daily_limit]
    drafts_md = generate_drafts_md(candidates)
    write_text(_out(output_dir, f"{TODAY}_email_drafts.md"), drafts_md)


def run_followups(leads: list[dict], output_dir: str) -> None:
    followup_pairs = get_followup_leads(leads)
    followups_md = generate_followups_md(followup_pairs)
    write_text(_out(output_dir, f"{TODAY}_followups.md"), followups_md)


def run_report(leads: list[dict], filtered: list[dict], output_dir: str) -> None:
    top_next = sorted(filtered, key=score_lead, reverse=True)
    report_md = generate_report_md(leads, filtered, top_next)
    write_text(_out(output_dir, f"{TODAY}_outreach_report.md"), report_md)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="PraxisMed Outreach Copilot — manual outreach planning tool"
    )
    parser.add_argument(
        "--input", required=True, metavar="CSV",
        help="Path to master leads CSV (e.g. docs/sales/outreach/praxisplan_all_high_potential_leads.csv)",
    )
    parser.add_argument(
        "--output-dir", default=DEFAULT_OUTPUT_DIR, metavar="DIR",
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--daily-limit", type=int, default=DEFAULT_DAILY_LIMIT, metavar="N",
        help=f"Number of leads to include in daily plan (default: {DEFAULT_DAILY_LIMIT})",
    )
    parser.add_argument(
        "--specialty", metavar="KEY",
        help="Filter by specialty_key (e.g. dermatology)",
    )
    parser.add_argument(
        "--tier", metavar="N",
        help="Filter by tier (1, 2, or 3)",
    )
    parser.add_argument(
        "--mode",
        choices=["plan", "drafts", "followups", "report"],
        default=None,
        help="Run only one mode. Omit to run all modes.",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"[ERROR] Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading leads from: {args.input}")
    all_leads = load_leads(args.input)
    print(f"  {len(all_leads)} total leads")

    filtered = filter_leads(
        all_leads,
        specialty=args.specialty,
        tier=args.tier,
    )
    print(f"  {len(filtered)} leads after filters (specialty={args.specialty}, tier={args.tier})")
    print(f"Output directory: {args.output_dir}")
    print()

    modes = [args.mode] if args.mode else ["plan", "drafts", "followups", "report"]

    if "plan" in modes:
        print("[plan] Generating daily outreach plan...")
        run_plan(all_leads, filtered, args.output_dir, args.daily_limit)

    if "drafts" in modes:
        print("[drafts] Generating email drafts...")
        run_drafts(filtered, args.output_dir, args.daily_limit)

    if "followups" in modes:
        print("[followups] Generating follow-up list...")
        run_followups(all_leads, args.output_dir)

    if "report" in modes:
        print("[report] Generating sales report...")
        run_report(all_leads, filtered, args.output_dir)

    print()
    print("Done. All files are for MANUAL REVIEW only.")
    print("No emails sent. No calls made.")


if __name__ == "__main__":
    main()
