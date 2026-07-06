# PraxisMed — Vapi German/English Assistant Setup

**Sprint 19 / Module 130**
**Date:** 2026-07-06
**Status:** Staging scaffold — no real patient data, no production PHI

---

## 1. Purpose

This document describes how to configure the Vapi voice assistant for PraxisMed staging.
The assistant acts as an Austrian private clinic receptionist — German-first, English fallback.

**What the assistant does:**
- Greets the caller in German
- Captures appointment request details (name, phone, reason, preferred time, urgency)
- Ends the call politely and tells the caller that clinic staff will follow up
- Sends the captured data to the PraxisMed backend via tool call

**What the assistant does NOT do:**
- Does not diagnose
- Does not give medical advice
- Does not recommend treatments
- Does not book automatically — staff/doctor confirms everything
- Does not store or repeat sensitive health information beyond what is needed to route the request

---

## 2. Safe Boundaries (Non-Negotiable)

All Vapi assistant configurations for PraxisMed must enforce these constraints:

| Boundary | Rule |
|---|---|
| No diagnosis | Assistant must never say "You have X" or "This sounds like X condition" |
| No medical advice | No recommendations, dosage guidance, or clinical assessments |
| No treatment recommendations | Do not suggest medications, procedures, or therapies |
| Capture only | The assistant collects and routes — it does not decide |
| Staff/doctor confirms everything | No appointment is booked without explicit doctor/staff action |
| No repeat of sensitive data | Do not read back detailed health complaints to the caller |
| Caller safety escalation | If caller describes emergency, instruct to call 112 (Austrian emergency) |

---

## 3. Required Captured Fields

The assistant must extract these fields and pass them to the tool call:

| Field | Required | Notes |
|---|---|---|
| `patient_name` | Yes | Full name as stated by caller |
| `phone` / `caller_phone` | Yes | Caller's phone number (auto-captured by Vapi or confirmed) |
| `reason` | Yes | Brief reason for appointment — no clinical assessment |
| `preferred_starts_at` | Preferred | Date/time the caller would like — ISO 8601 with timezone |
| `preferred_ends_at` | Optional | End of preferred window — defaults to 30 min after start |
| `urgency_level` | Conditional | Capture if caller indicates urgency. Values: `low`, `normal`, `urgent`, `emergency` |
| `language_preference` | Optional | Detected language: `de` (German) or `en` (English) |

---

## 4. German Assistant Prompt

Use this as the system prompt for the German-language Vapi assistant:

```
Du bist die freundliche Rezeptionistin der Arztpraxis Dr. Alexander Huber, Innere Medizin, Wien.
Du nimmst Terminanfragen entgegen und leitest sie an das Praxisteam weiter.

Deine Aufgaben:
1. Begrüße den Anrufer höflich auf Deutsch.
2. Frage nach dem Namen des Patienten.
3. Frage nach dem Grund des Anrufes (kurze Beschreibung, keine Diagnose).
4. Frage nach dem gewünschten Termin (Datum, Uhrzeit).
5. Frage, ob es sich um eine dringende Angelegenheit handelt.
6. Bestätige, dass das Praxisteam sich melden wird.
7. Verabschiede dich freundlich.

Wichtige Grenzen:
- Du stellst keine Diagnosen.
- Du gibst keine medizinischen Ratschläge.
- Du empfiehlst keine Behandlungen.
- Alle Termine werden vom Praxisteam bestätigt — nicht automatisch gebucht.
- Bei Notfällen weise sofort auf die Notrufnummer 112 hin.

Wenn der Anrufer Englisch spricht, wechsle freundlich ins Englische.

Sobald du alle Informationen hast, rufe das Tool "capture-appointment-request" auf.
```

---

## 5. English Fallback Prompt

Add this as a fallback or second-language instruction block:

```
If the caller speaks English, switch to English immediately and use this tone:

You are the friendly receptionist at Dr. Alexander Huber's practice, Internal Medicine, Vienna.
You take appointment requests and forward them to the clinic team.

Your tasks:
1. Greet the caller warmly in English.
2. Ask for the patient's name.
3. Ask for the reason for the call (brief description only — no clinical assessment).
4. Ask for the preferred appointment date and time.
5. Ask if this is urgent.
6. Confirm that the clinic team will follow up.
7. Say goodbye politely.

Boundaries:
- Never diagnose.
- Never give medical advice.
- Never recommend treatments.
- All appointments are confirmed by clinic staff — not booked automatically.
- For emergencies, direct the caller to 112 immediately.

Once you have all information, call the "capture-appointment-request" tool.
```

---

## 6. Tool Call JSON Shape

The assistant must call the backend with this JSON structure:

```json
{
  "clinic_ref": "1a5bbc75-c1b0-4488-94aa-64b3f1c50056",
  "call_id": "<vapi-call-id>",
  "patient_name": "<name spoken by caller>",
  "caller_phone": "<caller phone number>",
  "reason": "<brief reason — no clinical detail>",
  "preferred_starts_at": "<ISO 8601 datetime with timezone>",
  "preferred_ends_at": "<ISO 8601 datetime with timezone, optional>",
  "urgency_level": "normal"
}
```

Valid `urgency_level` values: `low`, `normal`, `urgent`, `emergency`.

The `call_id` is provided by Vapi automatically — use the Vapi call ID, not a made-up value.

---

## 7. Tool Endpoint and Headers

```
POST https://web-production-fd91d.up.railway.app/vapi/tools/capture-appointment-request
```

Required headers:

| Header | Value |
|---|---|
| `Content-Type` | `application/json` |
| `X-Vapi-Service-Name` | `vapi` |
| `X-Vapi-Clinic-Id` | `1a5bbc75-c1b0-4488-94aa-64b3f1c50056` |
| `X-Vapi-Scopes` | `vapi:tool` |

These headers are set in the Vapi assistant's server URL configuration in the Vapi dashboard — they are not visible to the caller and are not secrets shown here.

---

## 8. Vapi Dashboard Configuration

In the Vapi assistant settings:

1. **Server URL:** `https://web-production-fd91d.up.railway.app/vapi/tools/capture-appointment-request`
2. **Server URL Secret:** Set via Vapi dashboard secrets — never paste here. This is the `VAPI_WEBHOOK_SECRET` environment variable value.
3. **Language:** `de-AT` (German / Austria) primary, `en` fallback
4. **Voice:** Choose an Austrian-German voice from Vapi's voice library
5. **Tool name:** `capture-appointment-request`
6. **Tool description:** "Capture a patient appointment request and send to clinic backend for staff review"

---

## 9. What Not to Configure

- **Do not enable auto-booking** — the backend enforces `action_required=True` on every intake; there is no bypass.
- **Do not enable transcript auto-send to patient** — recording/transcript ingestion is not yet wired.
- **Do not store call recordings without legal/DSGVO review** — recording ingestion is pending compliance hardening.
- **Do not expose `VAPI_WEBHOOK_SECRET` or `DATABASE_URL`** — manage via Railway / Vapi environment secrets only.
- **Do not configure diagnosis or triage tools** — the assistant is a receptionist, not a clinical tool.

---

## 10. Recording and Transcript Ingestion

Recording/transcript ingestion is **not yet enabled** for the staging clinic.

The dashboard shows a placeholder:
> *"Recording/transcript review will appear here when Vapi recording ingestion is enabled."*

To enable in the future:
1. Set `recording_ingestion_enabled: true` in the clinic config JSON.
2. Implement the backend audio/transcript pipeline (future module).
3. Complete DSGVO/legal review for recording storage (C8 blocker).

---

## 11. Safety Summary

| Check | Status |
|---|---|
| German-first, English fallback | Documented above |
| No diagnosis | Enforced in prompt |
| No medical advice | Enforced in prompt |
| No treatment recommendations | Enforced in prompt |
| Staff/doctor confirms everything | Backend enforces `action_required=True` |
| Emergency escalation (112) | Included in prompt |
| No secrets in this document | Confirmed — no tokens, passwords, or webhook secrets |
| Recording/transcript ingestion | Pending — not yet enabled |
| Production PHI readiness | NO-GO — C3–C8 hardening blockers still open |
