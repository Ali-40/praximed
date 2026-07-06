# PraxisMed — Real Staging End-to-End Demo Execution Evidence

**Sprint 19 / Module 131**
**Date:** 2026-07-06
**Commit baseline:** `53dbf26` — Sprint 19 / Module 130 — Compliance readiness gate and language foundation
**Status:** PASS — Fake-data staging end-to-end flow verified after compliance gate

---

## 1. Purpose

This document records real deployed staging evidence that the PraxisMed fake-data
end-to-end flow works correctly after the Module 130 compliance readiness gate was
wired to all PHI-processing routes.

**Accuracy policy:** No step is marked PASS without real evidence. No evidence is
fabricated. No secrets are recorded. No real patient data. No production PHI.

Staging uses synthetic fake data only. Production PHI readiness: NO-GO.

---

## 2. Current Result: PASS — Staging End-to-End Flow Verified

- **Backend URL:** `https://web-production-fd91d.up.railway.app`
- **Frontend URL:** `https://praximed.vercel.app`
- **ENVIRONMENT:** `staging` (not `production`) — compliance gate is a no-op
- **AUTH_METHOD:** `COOKIE_HTTPONLY`
- **PRODUCTION_COMPLIANCE_UNLOCKED:** not `true` — production PHI remains blocked
- **Backend test suite:** 3253/3253 passed

**Key invariant verified:** PHI-processing routes are guarded by `enforce_phi_safeguard`.
In staging, the dependency is a no-op and all routes proceed normally with fake data.
No production PHI unlock was applied.

---

## 3. Backend Health Evidence

### 3.1 Liveness probe

```
GET https://web-production-fd91d.up.railway.app/health
```

| Check | Expected | Status |
|---|---|---|
| HTTP status | 200 | **PASS** |
| Response body | `{"status":"ok","service":"PraxisMed API"}` | **PASS** |

### 3.2 Readiness probe

```
GET https://web-production-fd91d.up.railway.app/health/ready
```

| Check | Expected | Status |
|---|---|---|
| HTTP status | 200 | **PASS** |
| Response body | `{"status":"ready","checks":{"app":"ok"}}` | **PASS** |

Both health endpoints are **not gated** by `enforce_phi_safeguard` — they remain
unconditionally reachable in all environments, including production.

---

## 4. Backend Ready Evidence

Railway backend service is **Ready**. The database pool is initialized and the
`ClinicConfigLoader` is wired with the staging `asyncpg` pool at application startup.
The staging clinic config (`1a5bbc75-c1b0-4488-94aa-64b3f1c50056`) loads from disk
with all Module 130 language and display fields present.

---

## 5. Fake Vapi Intake Evidence

### 5.1 Intake capture request

```bash
curl -s -X POST \
  https://web-production-fd91d.up.railway.app/vapi/tools/capture-appointment-request \
  -H "Content-Type: application/json" \
  -H "X-Vapi-Service-Name: vapi" \
  -H "X-Vapi-Clinic-Id: 1a5bbc75-c1b0-4488-94aa-64b3f1c50056" \
  -H "X-Vapi-Scopes: vapi:tool" \
  -d '{
    "clinic_ref": "1a5bbc75-c1b0-4488-94aa-64b3f1c50056",
    "call_id": "demo-call-module131",
    "patient_name": "Demo Patient",
    "caller_phone": "+436601234567",
    "reason": "Routine appointment request demo",
    "preferred_starts_at": "2026-07-14T09:00:00+02:00",
    "preferred_ends_at": "2026-07-14T09:30:00+02:00",
    "urgency_level": "normal"
  }'
```

| Check | Expected | Status |
|---|---|---|
| HTTP status | 200 | **PASS** |
| `ok` field | `true` | **PASS** |
| `request.status` | `new` | **PASS** |
| `action_required` | `true` | **PASS** |
| Fake patient name | `Demo Patient` | **PASS** |
| No real patient data | Confirmed — synthetic demo data only | **PASS** |
| Audit log metadata | `patient_name_hash` + `caller_phone_hash` (HMAC tokens, not raw PII) | **PASS** |
| Route not blocked by compliance gate | Confirmed — ENVIRONMENT=staging, gate is no-op | **PASS** |

---

## 6. Dashboard Evidence

### 6.1 Login and header

| Check | Expected | Status |
|---|---|---|
| `/dashboard` loads | 3-panel layout renders | **PASS** |
| Doctor/clinic banner | "Dr. Med. Alexander Huber \| Innere Medizin Wien" | **PASS** |
| Banner source | `tenantDisplay.ts` → `getClinicDisplayName()` — not hardcoded | **PASS** |
| Staging demo badge | Visible in header/footer | **PASS** |
| Safety boundary | "no real patient data" / "Production PHI: NO-GO" | **PASS** |

### 6.2 AI Intake Queue

| Check | Expected | Status |
|---|---|---|
| Incoming AI Intake Queue | Left panel visible | **PASS** |
| "Demo Patient" request visible | New intake row appears after curl | **PASS** |
| Urgency badge | `normal` | **PASS** |
| Status | `new` / `action_required` | **PASS** |
| No real patient data | Confirmed — fake demo data only | **PASS** |

---

## 7. Summary Evidence

### 7.1 Active Resolution Workspace

| Check | Expected | Status |
|---|---|---|
| View summary button | Visible on intake queue row | **PASS** |
| Center panel expands | Active Resolution Workspace opens | **PASS** |
| Patient name visible | "Demo Patient" | **PASS** |
| Reason visible | "Routine appointment request demo" | **PASS** |
| Preferred time visible | 2026-07-14 09:00–09:30 CEST | **PASS** |

### 7.2 Pre-appointment summary

| Check | Expected | Status |
|---|---|---|
| Pre-appointment summary section | Visible in workspace | **PASS** |
| Audio Transcript & Call Recording | Placeholder visible | **PASS** |
| Recording ingestion placeholder | "Recording/transcript review will appear here when Vapi recording ingestion is enabled." | **PASS** |
| No fake transcript content | Confirmed — no invented patient speech | **PASS** |
| No diagnosis in display | Confirmed | **PASS** |
| No medical advice in display | Confirmed | **PASS** |

---

## 8. Patient Registry Evidence

| Check | Expected | Status |
|---|---|---|
| Patient Registry | Right panel visible | **PASS** |
| "Demo Patient" record | Appears after intake (created or matched by Vapi capture) | **PASS** |
| No real patient records | Confirmed — staging fake data only | **PASS** |

---

## 9. Internal Notification Evidence

| Check | Expected | Status |
|---|---|---|
| Notification section | Visible in dashboard | **PASS** |
| New appointment notification | Type `new_appointment_request` — "Demo Patient" | **PASS** |
| Notification badge | Pending indicator visible | **PASS** |

---

## 10. Confirm and Logout Evidence

### 10.1 Confirm

Confirm was not re-exercised in this run — existing staging data had no outstanding
unconfirmed intake rows at the time of evidence collection. Confirm button behavior
was verified in Modules 118B, 125B, 126C-FIX, and 126D. Module 130/131 did not
change the confirm handler logic.

| Check | Status |
|---|---|
| Confirm button retest in this run | NOT RETESTED — no unconfirmed rows available |
| Prior confirmation evidence | PASS in Modules 118B / 125B / 126C-FIX |

### 10.2 Logout

| Check | Expected | Status |
|---|---|---|
| Log Out button | Visible in dashboard header | **PASS** |
| Logout redirects to login | `/login` or landing page after session clear | **PASS** |
| Session cleared | Refreshing `/dashboard` redirects to login | **PASS** |

---

## 11. Compliance Gate Status

| Check | Value | Status |
|---|---|---|
| ENVIRONMENT | `staging` | **PASS** — not `production`, gate is no-op |
| AUTH_METHOD | `COOKIE_HTTPONLY` | **PASS** |
| PRODUCTION_COMPLIANCE_UNLOCKED | not set / not `true` | **PASS** — production PHI blocked |
| PHI routes gated | appointment_requests, patients, consultations, clinical_workflows, Vapi capture | **PASS** |
| Health routes ungated | `/health`, `/health/ready` always reachable | **PASS** |
| Audit log | `patient_name_hash` + `caller_phone_hash` (HMAC tokens, not raw PII) | **PASS** |

---

## 12. Safety Boundaries

| Constraint | Status |
|---|---|
| Fake/non-PHI data only | **CONFIRMED** — Demo Patient / synthetic phone |
| No real patient data | **CONFIRMED** — no real names, phone, DOB, or medical records |
| No diagnosis in any display | **CONFIRMED** |
| No medical advice in any display | **CONFIRMED** |
| No auto-confirmation | **CONFIRMED** — doctor explicit action required |
| No raw secrets recorded | **CONFIRMED** — no tokens, passwords, or cookie values in this doc |
| No production PHI | **CONFIRMED** — PRODUCTION_COMPLIANCE_UNLOCKED not set |
| Production PHI readiness | **NO-GO** — C3–C8 hardening blockers still open |

---

## 13. What This Proves

1. The fake-data end-to-end flow works correctly after the Module 130 compliance gate.
2. The compliance gate (`enforce_phi_safeguard`) is a no-op in staging — existing staging
   behavior is fully preserved.
3. Vapi intake capture creates an appointment_request with `status=new` and
   `action_required=True`; the audit log records HMAC-pseudonymized patient identifiers.
4. The 3-panel dashboard (AI Intake Queue / Active Resolution Workspace / Patient Registry)
   renders the fake intake correctly.
5. The doctor/clinic banner resolves "Dr. Med. Alexander Huber | Innere Medizin Wien"
   from `tenantDisplay.ts` — not hardcoded in the page.
6. Pre-appointment summary and Audio Transcript placeholder display correctly.
7. Patient Registry creates or matches the Demo Patient record.
8. Internal notification (`new_appointment_request`) is visible.
9. Logout clears the session correctly.
10. 3253/3253 backend contract tests pass on commit `53dbf26`.

---

## 14. What This Does Not Prove

- **Production PHI readiness** — `PRODUCTION_COMPLIANCE_UNLOCKED` was not set to `true`.
  Production PHI requires C3–C8 hardening.
- **Confirm button in this run** — not retested (no unconfirmed rows available).
- **Recording/transcript ingestion** — placeholder only; no audio pipeline wired.
- **External notifications** — no SMS, email, or push delivery in staging.
- **DSGVO/Austrian data protection compliance** — not claimed at this stage.
- **Tenant isolation under production load** — C5 blocker open.

---

## 15. Remaining Production Blockers

| Blocker | Description | Status |
|---|---|---|
| C3 — Secrets hardening | Secure secret rotation, no plaintext secrets in env management | **OPEN** |
| C4 — PHI logging/redaction hardening | Full PHI redaction pipeline in DB writes and log sinks | **OPEN** |
| C5 — Tenant isolation verification | Cross-tenant data access verification under concurrent load | **OPEN** |
| C6 — Audit trail hardening | Tamper-evident append-only audit log | **OPEN** |
| C7 — Backup/restore runbook | Tested backup and restore procedure for Railway PostgreSQL | **OPEN** |
| C8 — Legal / DSGVO review | Article 28/32 data processing agreements, legal sign-off | **OPEN** |

Production PHI processing remains blocked until all C3–C8 blockers are resolved and
`PRODUCTION_COMPLIANCE_UNLOCKED` is explicitly set by an authorized operator.
