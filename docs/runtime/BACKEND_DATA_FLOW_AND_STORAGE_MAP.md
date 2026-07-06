# PraxisMed — Backend Data Flow and Storage Map

**Sprint 19 / Module 130**
**Date:** 2026-07-06
**Status:** Staging fake-data only — Production PHI: NO-GO

---

## 1. Infrastructure Overview

| Component | Platform | URL |
|---|---|---|
| Frontend (Next.js 14) | Vercel | `https://praximed.vercel.app` |
| Backend API (FastAPI) | Railway | `https://web-production-fd91d.up.railway.app` |
| Database (PostgreSQL) | Railway PostgreSQL | Internal Railway connection string |
| Tenant configs | Backend filesystem | `backend/tenants/configs/<clinic_id>/clinic_config.json` |

The frontend and backend are deployed independently. The frontend calls the backend over HTTPS using cookie-based session auth (`credentials: "include"` on every request). No secrets are stored in the frontend.

---

## 2. Database — Railway PostgreSQL

All persistent state lives in the Railway PostgreSQL database. The backend connects via `asyncpg` connection pool initialized at application startup.

### Main Tables

| Table | Purpose |
|---|---|
| `clinics` | One row per tenant clinic. Stores clinic_id, name, config reference. |
| `users` | Doctor/admin accounts. Belongs to one clinic. Role: `doctor` or `admin`. |
| `patients` | Patient records linked to a clinic. Created or matched on first Vapi intake. |
| `appointment_requests` | Every appointment request captured from Vapi. Status lifecycle: `new` → `confirmed` / `rejected`. |
| `clinic_notifications` | Internal notifications for clinic staff (e.g., "New appointment request"). |
| `consultation_sessions` | Post-appointment session records. Used for pre-appointment summary flow. |
| `audit_log` | Append-only audit trail of machine and user actions. |

### Key Schema Relationships

```
clinics
  └─ users          (clinic_id FK)
  └─ patients       (clinic_id FK)
  └─ appointment_requests  (clinic_id FK, patient_id FK optional)
  └─ clinic_notifications  (clinic_id FK, linked to appointment_requests)
  └─ consultation_sessions (clinic_id FK, patient_id FK)
  └─ audit_log      (clinic_id FK)
```

---

## 3. Vapi Intake Data Flow

```
Caller dials Vapi phone number
        │
        ▼
Vapi receptionist assistant
  ├── Greets caller in German (fallback: English)
  ├── Captures: patient_name, phone, reason, preferred_time, urgency_level
  └── Calls tool: POST /vapi/tools/capture-appointment-request
        │
        ▼
FastAPI — /vapi/tools/capture-appointment-request
  ├── Validates machine auth headers (X-Vapi-Service-Name, X-Vapi-Clinic-Id, X-Vapi-Scopes)
  ├── Adapts Vapi nested tool-call payload → flat schema
  ├── Validates request body (patient_name required, urgency_level ∈ {low,normal,urgent,emergency})
  ├── Matches or creates patient record (patients table)
  ├── Creates appointment_request row (status=new, action_required=True)
  ├── Creates clinic_notification row (type=new_appointment_request)
  └── Records audit_log entry (action=vapi.appointment_capture, severity=warning)
        │
        ▼
Dashboard — doctor/staff review
  ├── GET /api/appointment-requests  → Incoming AI Intake Queue (left panel)
  ├── GET /api/appointment-requests/{id}/summary  → Intake Resolution Workspace (center)
  ├── GET /api/patients  → Patient Registry (right panel)
  └── POST /api/appointment-requests/{id}/confirm  → doctor confirms
        │
        ▼
Appointment marked confirmed — notification resolved
```

**Key invariant:** The appointment is never automatically booked. `action_required=True` until a doctor/staff member explicitly confirms via the dashboard.

---

## 4. Auth and Session Flow

```
POST /auth/login  (username + password)
        │
        ▼
FastAPI verifies credentials against users table
        │
        ▼
Sets HttpOnly secure session cookie (no token in JS/localStorage)
        │
        ▼
Dashboard loads — all subsequent requests include cookie automatically
  ├── GET /auth/me  → returns {user_id, clinic_id, role}
  ├── All API calls use credentials: "include" (set globally in frontend/lib/api.ts)
  └── clinic_id from /auth/me scopes all queries (tenant isolation)

POST /auth/logout  → clears session cookie
```

**Session storage:** HttpOnly cookie only. No sessionStorage. No localStorage. No JWT in browser memory.

---

## 5. Tenant Config Flow

Each clinic has a JSON config file at:
```
backend/tenants/configs/<clinic_id>/clinic_config.json
```

The config loader reads this file at request time (with caching). It provides:
- Clinic display name, specialty, language
- Feature flags (appointment_booking, recording_ingestion, etc.)
- AI persona name and tone

The staging clinic config for `1a5bbc75-c1b0-4488-94aa-64b3f1c50056` sets:
- `language: "de"` — German primary
- `fallback_language: "en"` — English fallback
- `appointment_intake_enabled: true`
- `recording_ingestion_enabled: false` — audio/transcript ingestion not yet wired
- `production_phi_enabled: false` — staging only

---

## 6. Frontend → Backend API Map

| Frontend action | Backend endpoint | Auth |
|---|---|---|
| Login | `POST /auth/login` | Public |
| Get current user | `GET /auth/me` | Cookie session |
| Logout | `POST /auth/logout` | Cookie session |
| List appointment requests | `GET /api/appointment-requests` | Cookie session |
| Get request summary | `GET /api/appointment-requests/{id}/summary` | Cookie session |
| Confirm appointment | `POST /api/appointment-requests/{id}/confirm` | Cookie session |
| List patients | `GET /api/patients` | Cookie session |
| List notifications | `GET /api/notifications` | Cookie session |
| Vapi intake capture | `POST /vapi/tools/capture-appointment-request` | Machine auth headers |
| Health liveness | `GET /health` | Public |
| Health readiness | `GET /health/ready` | Public |

---

## 7. Safety Constraints

| Constraint | Status |
|---|---|
| Fake/non-PHI data only | **ENFORCED** — staging clinic uses synthetic data |
| No real patient data | **ENFORCED** — no real names, phone, DOB, or medical records in staging |
| No diagnosis stored or displayed | **ENFORCED** |
| No medical advice stored or displayed | **ENFORCED** |
| No auto-confirmation | **ENFORCED** — doctor explicit action required |
| No external delivery (SMS/email/WhatsApp) | **NOT IMPLEMENTED** |
| Production PHI readiness | **NO-GO** — C3–C8 hardening blockers still open |
| DSGVO / Austrian data protection compliance | **NOT CLAIMED** at this stage |

---

## 8. What Is Not Yet Wired

- **Vapi recording/transcript ingestion** — placeholder UI only; no audio pipeline
- **External notifications** — no SMS, email, or push delivery
- **Real tenant provisioning** — staging clinic is manually configured
- **Production secrets hardening** — C3 blocker open
- **PHI logging/redaction** — C4 blocker open
- **Tenant isolation verification** — C5 blocker open
- **Audit trail hardening** — C6 blocker open
- **Backup/restore runbook** — C7 blocker open
- **Legal / DSGVO review** — C8 blocker open
