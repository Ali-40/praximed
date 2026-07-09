# One-Click Demo Flow

**Sprint 21 / Module 158**
**Date:** 2026-07-09
**Status:** Complete

---

## Purpose

After Module 157 simplified `/dashboard` into a German-first clinic-facing MVP,
the next sales readiness step is making the demo instant and self-contained.

Ali walks into a Vienna clinic. The receptionist is watching.
Ali opens `/dashboard`, presses **"Demo-Anruf erstellen"**, and within seconds a
realistic synthetic appointment request appears in the Anfragen queue — ready to
demonstrate the full callback workflow without any backend setup, live calls,
or real patient data.

---

## What Module 158 Adds

### Backend — Staging-Only Endpoints

Two new routes under `/demo/sales-mvp/`:

**`POST /demo/sales-mvp/create-call`**
- Creates a synthetic appointment request in the clinic's queue
- `source = "staff"`, `source_ref = "sales-demo-call-{12-char-hex}"`
- `patient_name = "Mag. Klaus Hofer"` — realistic Austrian name, not a real patient
- `reason = "Rückenschmerzen seit 3 Tagen, Termin erbeten"` — plausible but synthetic
- `status = "callback_needed"`, `urgency_level = "normal"`
- `raw_payload.synthetic_demo = True`, `raw_payload.production_phi_enabled = False`
- Returns `{ ok, request_id, message, synthetic_demo, production_phi_enabled }`

**`POST /demo/sales-mvp/reset`**
- Archives all synthetic demo records: `source_ref LIKE 'sales-demo-call-%'`
- Archives (status → `archived`) — never deletes real records
- Returns `{ ok, archived_count, message }`

Both endpoints are **staging-only** — blocked with HTTP 403 in production.
Both require auth (session cookie).

### Frontend — Demo Strip in /dashboard

A slim **Demo-Modus strip** appears at the top of the Anfragen tab:

```
[ Demo-Modus ]  Nur Demo. Keine echten Patientendaten.
                [ Demo-Anruf erstellen ]  [ Demo zurücksetzen ]
```

- **"Demo-Anruf erstellen"** — calls `createSalesDemoCall(clinicId)`, refreshes queue
- **"Demo zurücksetzen"** — calls `resetSalesDemoData(clinicId)`, clears demo records
- Both buttons disabled while in progress
- German success/error messages shown inline:
  - Success: `"Demo-Anfrage wurde der Warteschlange hinzugefügt."`
  - Error: `"Demo-Anfrage konnte nicht erstellt werden."`
  - Reset success: backend message (e.g. `"Demo zurückgesetzt. 2 Demo-Anfrage(n) archiviert."`)
  - Reset error: `"Demo konnte nicht zurückgesetzt werden."`

### api.ts Additions

```typescript
export async function createSalesDemoCall(clinicId: string): Promise<{...}>
export async function resetSalesDemoData(clinicId: string): Promise<{...}>
```

Both use `apiFetch` (credentials: "include"). No browser storage. No JWT.

---

## Safety Boundaries (All Unchanged from Module 157)

- **No real patient data** — synthetic Austrian name only
- **No PHI** — `production_phi_enabled = False` in all demo records
- **No Vapi live call** — no audio, no recording, no transcript
- **No diagnosis** — none in backend route or frontend
- **No medical advice** — none anywhere in demo flow
- **No triage scoring** — none
- **No patient_history_* writes** — demo creates only appointment_request rows
- **Staging-only guard** — `ENVIRONMENT` must be `local` or `staging`, else HTTP 403
- **Archive not delete** — reset never removes records, only changes status
- **No new PHI unlock** — `production_phi_enabled` remains `False` throughout
- Production PHI remains NO-GO

---

## Demo Identification Pattern

Demo records are identified by `source_ref LIKE 'sales-demo-call-%'`.
This prefix is reserved for synthetic demo data created via this flow.
Real vapi/whatsapp/web records never use this prefix.

---

## Files Modified

- `backend/app/api/routes/sales_demo.py` — new
- `backend/app/api/router.py` — `sales_demo` router registered
- `frontend/lib/api.ts` — `createSalesDemoCall`, `resetSalesDemoData` added
- `frontend/app/dashboard/page.tsx` — demo strip, handlers, state
- `backend/tests/test_one_click_demo_flow_sales_mvp_contract.py` — new, ≥15 tests
- `docs/product/ONE_CLICK_DEMO_FLOW.md` — this file

---

## Acceptance Statement

> "Ali can open `/dashboard`, press 'Demo-Anruf erstellen', and within seconds show
> a Vienna receptionist a realistic callback request in the intake queue."

The demo flow is now instant and self-contained.

---

## What Remains

- Module 159 — Clinic Settings Editor (editable Einstellungen tab)
- Module 160 — AI receptionist value story
- Arabic/RTL foundation
- Production readiness / security / legal gates
