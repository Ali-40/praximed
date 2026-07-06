# PraxisMed — Live Vapi Assistant Config Preview Smoke Evidence

**Sprint 19 / Module 143**
**Date:** 2026-07-06
**Commit tested:** 944b898

---

## 1. Purpose

Verify that the admin Vapi assistant config preview UI (Module 142) works
end-to-end against the live staging backend: loading the generated config pack
for a provisioned staging clinic and confirming all sections render correctly —
German-first prompt, English fallback, required capture fields, tool schema,
safety rules, forbidden claims, and readiness flags.

No live Vapi binding. No Vapi credentials stored or transmitted. No PHI.
No secrets. Production PHI remains NO-GO.

---

## 2. Current Result

**PASS**

All evidence steps completed successfully on staging.

---

## 3. Live Route Tested

```
https://praximed.vercel.app/developer-console/vapi-config
```

Backend endpoint exercised:

```
GET /clinics/{clinic_id}/vapi-assistant-config-pack
```

---

## 4. Clinic ID Used

```
1a5bbc75-c1b0-4488-94aa-64b3f1c50056
```

Staging fake clinic — Demo Wahlarzt Praxis Wien. Provisioned in Module 137.
No real patient records. No PHI. No production activation.

---

## 5. Load Config Pack Evidence

- Opened `/developer-console/vapi-config` with admin session active.
- Entered clinic_id: `1a5bbc75-c1b0-4488-94aa-64b3f1c50056`.
- Clicked "Load config pack".
- GET `/clinics/1a5bbc75-c1b0-4488-94aa-64b3f1c50056/vapi-assistant-config-pack`
  responded HTTP 200 with VapiAssistantConfigPack JSON.
- All eight display sections rendered successfully.

---

## 6. German-First Prompt Evidence

Section B rendered the German-first prompt:

- `first_message_de`: German greeting visible — "Guten Tag, Sie sind bei der
  KI-Rezeption…"
- `system_prompt_de`: Full German system prompt visible in monospace block.
  Key content confirmed:
  - "KI-Rezeption" — assistant identity visible
  - "private" / "Praxis" / "Wien" — clinic context confirmed
  - "keine Diagnose" — no-diagnosis boundary visible
  - "keine medizinische Beratung" — no-medical-advice boundary visible
  - "keine Terminbestätigung" — no-appointment-confirmation boundary visible
  - Notruf 144 — Austrian emergency escalation instruction visible

---

## 7. English Fallback Prompt Evidence

Section C rendered the English fallback prompt:

- `first_message_en`: English greeting visible — "Good day, you've reached the
  AI reception…"
- `system_prompt_en`: Full English system prompt visible in monospace block.
  Key content confirmed:
  - "AI receptionist" — assistant identity visible
  - "private clinic in Vienna" — clinic context confirmed
  - "No diagnosis" — no-diagnosis boundary visible
  - "No medical advice" — no-medical-advice boundary visible
  - "no appointment confirmation" / "do not promise" — confirmation boundary visible
  - "call 144" — Austrian emergency escalation instruction visible

---

## 8. Required Capture Fields Evidence

Section D rendered all required capture fields:

| Field | Visible |
|---|---|
| `patient_name` | CONFIRMED |
| `phone` | CONFIRMED |
| `reason` | CONFIRMED |
| `preferred_time` | CONFIRMED |
| `language_preference` | CONFIRMED |
| `urgency_level` | CONFIRMED |

---

## 9. Tool Schema Evidence

Section E rendered the tool schema JSON:

- `capture_appointment_request` tool name visible.
- `POST /vapi/tools/capture-appointment-request` target endpoint visible.
- Required Vapi header names visible (values never shown):
  - `X-Vapi-Service-Name` — CONFIRMED
  - `X-Vapi-Clinic-Id` — CONFIRMED
  - `X-Vapi-Scopes` — CONFIRMED
- No secret values shown.
- Full JSON rendered in monospace code block.

---

## 10. Safety Rules Evidence

Section F rendered all safety rules:

- "No diagnosis. Never provide a diagnosis…" — CONFIRMED
- "No medical advice. Do not give medical recommendations…" — CONFIRMED
- "No treatment recommendations…" — CONFIRMED
- "No appointment confirmation. Never promise the appointment is confirmed…" — CONFIRMED
- Emergency escalation: "call 144" in Austria instruction — CONFIRMED
- Escalation rules (Notruf 144) rendered in amber warning style — CONFIRMED

---

## 11. Forbidden Claims Evidence

Section G rendered all forbidden claims:

- "That the appointment is confirmed." — CONFIRMED
- "A diagnosis of any kind." — CONFIRMED
- "Medical advice or treatment recommendations." — CONFIRMED
- "That the assistant is a doctor, nurse, or qualified medical professional." — CONFIRMED
- "That calling 144 is unnecessary for serious symptoms." — CONFIRMED

---

## 12. Readiness Flags Evidence

Section H rendered all readiness flags with colour coding:

| Flag | Value | Colour |
|---|---|---|
| `production_phi_enabled` | `false` | green |
| `recording_ingestion_enabled` | `false` | green |
| `transcript_ingestion_enabled` | `false` | green |

All flags correctly shown as `false` in green. No flag was `true`.

---

## 13. Safety Boundaries

| Boundary | Status |
|---|---|
| No PHI entered or displayed | CONFIRMED |
| No Vapi API key entered or shown | CONFIRMED |
| No webhook secret entered or shown | CONFIRMED |
| No sessionStorage used | CONFIRMED |
| No localStorage used | CONFIRMED |
| No live Vapi binding triggered | CONFIRMED |
| production_phi_enabled false | CONFIRMED |
| No production activation | CONFIRMED |
| No secrets in response body | CONFIRMED |
| credentials: 'include' session auth | CONFIRMED |

---

## 14. What This Proves

- GET `/clinics/{clinic_id}/vapi-assistant-config-pack` returns a complete,
  correct config pack for a provisioned staging clinic.
- German-first prompt is complete: KI-Rezeption identity, keine Diagnose,
  keine medizinische Beratung, Notruf 144 escalation.
- English fallback prompt is complete: AI receptionist identity, no diagnosis,
  no medical advice, call 144 escalation.
- All six required capture fields are present and displayed.
- Tool schema renders correctly in the browser with no secret values exposed.
- All three safety flags are `false`.
- Admin UI round-trip (load → view all sections) works end-to-end on staging.
- `credentials: 'include'` session auth works for this endpoint.
- No live Vapi binding occurs when previewing the config pack.

---

## 15. What This Does Not Prove

- Production readiness.
- DSGVO / Austrian data protection compliance.
- Actual Vapi assistant binding or provisioning.
- Bilingual audio testing with a real caller.
- Security hardening (C3–C8 blockers remain open).
- Multi-tenant isolation of config packs.
- That the prompts produce correct assistant behaviour in live Vapi calls.

---

## 16. Remaining Blockers

| Blocker | Status |
|---|---|
| C3 — Secrets hardening | Open |
| C4 — PHI logging/redaction hardening | Open |
| C5 — Tenant isolation verification | Open |
| C6 — Audit trail hardening | Open |
| C7 — Backup/restore runbook | Open |
| C8 — Legal / DSGVO review | Open |
| Vapi credential binding design (Module 144) | Next |
| Actual Vapi assistant provisioning | Pending |
| Recording ingestion | Pending |
| Transcript storage | Pending |
| Bilingual assistant audio testing | Pending |

Production PHI remains NO-GO until C3–C8 hardening blockers are resolved.
