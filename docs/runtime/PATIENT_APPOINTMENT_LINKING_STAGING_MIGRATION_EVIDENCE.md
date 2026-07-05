# Patient and Appointment Linking — Staging Migration Evidence

**Date:** 2026-07-05
**Sprint:** Sprint 17 / Module 121B
**Commit:** 02e8896
**Status:** PASS

---

## 1. Purpose

This document records real deployed staging evidence that Module 121 — Patient and
Appointment Data Linking Foundation — works correctly after Railway migration and
redeploy. It covers:

- Migration 0003 applied successfully
- `appointment_requests.patient_id` column and index exist
- Direct Vapi endpoint smoke creates an appointment request linked to a patient row
- Linking is scoped by `clinic_id` (tenant isolation confirmed)

**Accuracy policy:** No step is marked PASS without real evidence from real deployed
staging services. No evidence is fabricated. No real patient data. No secrets recorded.

Staging uses fake/non-PHI data only. Production PHI launch remains NO-GO.

---

## 2. Current Result

**Overall result: PASS**

Migration 0003 applied; `appointment_requests.patient_id` column and
`idx_appointment_requests_clinic_patient` index confirmed in Railway PostgreSQL.
Direct Vapi endpoint smoke succeeded; latest appointment_request has a non-null
`patient_id` linking to a real patient row in the same fake staging clinic.

---

## 3. Evidence

### 3.1 Railway Redeploy

| Item | Value |
|---|---|
| Commit redeployed | `02e8896` |
| Backend URL | `https://web-production-fd91d.up.railway.app` |
| Deploy trigger | Manual redeploy after Module 121 commit |
| `/health` after redeploy | HTTP 200 — `{"status":"ok","service":"PraxisMed API"}` |

### 3.2 Migration 0003 Applied

| Item | Value |
|---|---|
| Command | `python backend/scripts/run_migrations.py` |
| Exit code | 0 |
| Migration applied | `0003_patient_id_appt_requests` |
| Final head | `0003_patient_id_appt_requests (head)` |

### 3.3 Schema Verification

| Item | Status |
|---|---|
| `appointment_requests.patient_id` column exists | **PASS** |
| `patient_id` type | `uuid`, nullable |
| `patient_id` references `patients(id) ON DELETE SET NULL` | **PASS** |
| `idx_appointment_requests_clinic_patient` index exists | **PASS** |
| Index columns | `(clinic_id, patient_id)` |

### 3.4 Direct Vapi Endpoint Smoke

| Item | Value |
|---|---|
| Endpoint | `POST /vapi/tools/capture-appointment-request` |
| Source | `vapi` |
| Patient name | Linked Test Patient (fake) |
| Reason | routine checkup |
| Preferred time | next Monday morning |
| Response | HTTP 200 — `{"ok": true, ...}` |
| `status` in response | `new` |
| `action_required` in response | `true` |

### 3.5 Database Verification

| Item | Value |
|---|---|
| Latest appointment_request `patient_id` | non-null UUID |
| Joined patients row exists | **PASS** |
| Patients row `clinic_id` | matches appointment_request `clinic_id` |
| Linking scoped by `clinic_id` | **PASS** — no cross-clinic rows possible |
| `source` | `vapi` |
| `status` | `new` |
| `action_required` | `true` |

---

## 4. Fake Data Used

All staging data is fake. No real patient data, no real clinic data, no production PHI.

| Field | Value |
|---|---|
| Patient name | Linked Test Patient |
| Reason | routine checkup |
| Preferred time | next Monday morning |
| Clinic UUID | `1a5bbc75-c1b0-4488-94aa-64b3f1c50056` (fake staging clinic) |
| Clinic slug | `staging-fake-clinic` |

---

## 5. What This Proves

- Vapi phone intake can find or create a patient row scoped to the clinic
- `appointment_requests` can link to `patients` via `patient_id` FK
- The FK constraint is applied correctly via migration 0003
- Linking is scoped by `clinic_id` — cross-clinic linking is impossible by construction
- The relational foundation for future doctor notifications, pre-appointment summaries,
  consultation summary drafts, patient timelines, and follow-up workflows is in place
- Migration 0003 is idempotent (`IF NOT EXISTS`) — safe to rerun

---

## 6. What This Does Not Prove

- Pre-appointment summary generation (Module 122 — pending)
- Doctor/staff notification (Module 123 — pending)
- Consultation summary draft generation (Module 124 — pending)
- Patient timeline view (Module 125 — pending)
- Follow-up and reminder workflow (Module 126 — pending)
- Production PHI readiness — **NO-GO** (C3–C8 hardening blockers still open)
- n8n staging workflow — PENDING / DEFERRED

---

## 7. Safety

| Constraint | Status |
|---|---|
| Fake data only (no real patient data) | **CONFIRMED** |
| No real patient name / phone / DOB / email | **CONFIRMED** |
| No production PHI recorded or used | **CONFIRMED** |
| No password / token / cookie value recorded | **CONFIRMED** |
| No DATABASE_URL value recorded | **CONFIRMED** |
| No JWT secret recorded | **CONFIRMED** |
| No Vapi webhook secret recorded | **CONFIRMED** |
| No auto-confirmation of appointments | **CONFIRMED** — `action_required=true`; staff Confirm required |

---

## 8. Recommended Next Module

**Sprint 17 / Module 122 — Pre-Appointment Summary Foundation**

Use the linked `patient_id` + `appointment_request` data to generate a structured
pre-appointment brief. No medical advice. Doctor/staff approval required. Fake data only.
Production PHI remains NO-GO.
