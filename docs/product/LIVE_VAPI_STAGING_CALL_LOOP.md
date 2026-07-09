# Live Vapi Staging Call Loop

**Sprint 21 / Module 160**
**Date:** 2026-07-09
**Status:** Complete

---

## Purpose

Module 159 made the clinic feel personal. Module 160 closes the live demo loop: a real
phone call to the staging Vapi number flows through the AI German receptionist, captures
a synthetic appointment request, and posts it to the existing intake endpoint — the
request then appears in `/dashboard` as **Rückruf nötig**.

Staging-only. No real patient data. No PHI. No appointment auto-confirmation.
No diagnosis. No medical advice. No triage scoring. Production PHI remains NO-GO.

---

## Demo Flow (Ali's Sales Script)

1. Open `/dashboard` → Anfragen tab (empty or demo queue visible).
2. Call the staging Vapi number from any phone.
3. Speak a short synthetic request in German (see assistant script below).
4. Hang up.
5. Refresh `/dashboard` → new Anfrage appears with **Rückruf nötig** status.
6. Press **Rückruf** or **Als kontaktiert markieren**.
7. Demo complete — no technical intervention needed.

---

## German AI Receptionist Script

The Vapi assistant is configured with a German-first `first_message` and `system_prompt`.

### Begrüßung (Greeting)

> "Guten Tag, hier ist die digitale Rezeption der Ordination. Wie kann ich Ihnen helfen?"

### Datenerfassung (Data Collection)

The assistant collects these fields in natural conversation:

| Feld | Beispiel-Frage |
|---|---|
| Name | "Darf ich Ihren Namen erfahren?" |
| Telefonnummer | "Unter welcher Nummer können Sie das Praxisteam zurückrufen?" |
| Anliegen | "Was ist der Grund Ihres Anrufs?" |
| Gewünschter Termin | "Wann würde Ihnen ein Termin am besten passen?" |

### Abschluss (Closing)

> "Vielen Dank. Das Praxisteam meldet sich zur Bestätigung zurück. Auf Wiederhören."

**Kein automatischer Terminabschluss.** The AI receptionist never confirms an appointment.
Staff must review and confirm before any booking is made.

### Notfall-Routing (Emergency)

If the caller describes an emergency:

> "Bei einem medizinischen Notfall wählen Sie bitte sofort die 144. Auf Wiederhören."

No diagnosis. No medical advice. No triage scoring. No treatment recommendation.

---

## Existing Backend Endpoint

```
POST /vapi/tools/capture-appointment-request
```

Deployed at: `https://web-production-fd91d.up.railway.app/vapi/tools/capture-appointment-request`

This endpoint already exists and handles the full call flow. No new backend code was needed
for Module 160.

### Required Headers (Vapi Dashboard Config — Names Only, No Secret Values Here)

| Header Name | Purpose |
|---|---|
| `X-Vapi-Service-Name` | Identifies the calling service |
| `X-Vapi-Clinic-Id` | Routes to the correct clinic |
| `X-Vapi-Scopes` | Permission scope |

Configure these in the Vapi assistant's server tool configuration. The actual values
are stored in environment variables — never in this document.

### Request Body Shape (Flat Format)

```json
{
  "call_id": "<vapi-call-id>",
  "patient_name": "<spoken-name>",
  "caller_phone": "<caller-number>",
  "reason": "<spoken-reason>",
  "preferred_starts_at": "<spoken-time-or-null>",
  "urgency_level": "normal"
}
```

No transcript stored. No recording URL stored. No PHI in any stored field.

### Example curl (Staging Only — Placeholder Values)

```bash
curl -X POST https://web-production-fd91d.up.railway.app/vapi/tools/capture-appointment-request \
  -H "Content-Type: application/json" \
  -H "X-Vapi-Service-Name: <service-name-from-env>" \
  -H "X-Vapi-Clinic-Id: <clinic-id-from-env>" \
  -H "X-Vapi-Scopes: <scopes-from-env>" \
  -d '{
    "call_id": "test-call-001",
    "patient_name": "Synthetics Demo",
    "caller_phone": "+43000000000",
    "reason": "Terminanfrage"
  }'
```

Replace placeholder values with staging credentials from the environment. Never commit
real values to this file.

---

## Vapi Dashboard Staging Checklist

Before the live demo, verify in the Vapi dashboard:

- [ ] Staging phone number assigned to the German assistant
- [ ] Server URL set to the staging endpoint above
- [ ] Required headers configured (values from environment, not from this doc)
- [ ] `first_message` set in German
- [ ] `system_prompt` instructs: collect Name, Telefon, Anliegen, gewünschte Zeit
- [ ] `system_prompt` includes: "Das Praxisteam meldet sich zur Bestätigung zurück."
- [ ] `system_prompt` includes emergency routing to 144
- [ ] No appointment auto-confirmation in assistant logic
- [ ] No diagnosis or medical advice in assistant logic
- [ ] Staging credentials only — no production number

---

## What the Backend Creates

When a call event arrives at the endpoint, the backend creates one `appointment_requests` row:

| Column | Value |
|---|---|
| `source` | `"vapi"` |
| `source_ref` | Vapi call ID |
| `status` | `"new"` |
| `action_required` | `True` |
| `production_phi_enabled` | `False` |

No transcript is stored. No recording URL is stored. No automatic appointment confirmation.
Staff must review before any booking.

---

## Dashboard Live Demo Hint

Inside the Demo-Modus strip (`data-demo-strip="sales-mvp"`), a plain-German hint line reads:

> "Live-Telefon-Demo: Ein Anruf erscheint hier als Rückruf-Anfrage. · Staging-Telefonnummer wird im Vapi Dashboard konfiguriert."

No API URL, header names, clinic UUID, Vapi config, JSON, or technical content is shown
in the clinic-facing dashboard.

---

## No Technical Fields in Dashboard

The following remain absent from the `/dashboard` UI:

- No endpoint URL
- No header names or values
- No clinic UUID visible to clinic staff
- No Vapi config or assistant ID
- No JSON
- No webhook, API key, or secret reference
- No FHIR or JWT
- No diagnosis, medical advice, or triage

The Developer Console (`/developer-console`) remains the appropriate place for all
technical configuration.

---

## Safety Boundaries (Unchanged)

All Module 157/158/159 safety boundaries remain in force:

- No real patient data
- No PHI
- `production_phi_enabled = False` throughout
- No live Vapi call during tests (static contract tests only)
- No browser storage (no localStorage, no sessionStorage)
- No transcript storage
- No recording URL storage
- No appointment auto-confirmation
- No diagnosis, medical advice, triage scoring, or treatment recommendation
- Emergency → 144 routing only (no clinical triage)
- Production PHI remains NO-GO

---

## Files Modified

- `frontend/app/dashboard/page.tsx` — added `data-live-demo-hint` span in demo strip
- `backend/tests/test_live_vapi_staging_call_loop_sales_mvp_contract.py` — new, ≥15 tests
- `docs/product/LIVE_VAPI_STAGING_CALL_LOOP.md` — this file

---

## Acceptance Statement

> "Ali kann eine Staging-Telefonnummer anrufen, ein synthetisches deutsches
> Terminanliegen sprechen, und die Anfrage erscheint in /dashboard als Rückruf nötig —
> ohne dass Ali eine einzige technische Einstellung berühren muss."
>
> (Ali can call one staging number, speak synthetic German appointment request data,
> and show the request appear in /dashboard as Rückruf nötig — without touching
> any technical settings.)
