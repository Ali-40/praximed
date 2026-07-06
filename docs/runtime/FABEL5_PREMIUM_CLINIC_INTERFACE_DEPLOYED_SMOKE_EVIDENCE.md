# Deployed Fabel 5 Premium Clinic Interface Smoke Evidence — PraxisMed Sprint 18 / Module 126D

**Date:** 2026-07-06
**Sprint:** Sprint 18 / Module 126D
**Commit:** `0d0f952` — Sprint 18 / Module 126C-FABEL5-FINAL — Doctor-facing interface polish
**Status:** PASS — Fabel 5 premium 3-panel clinical interface deployed and verified

---

## 1. Purpose

This document records deployed browser smoke evidence that the Fabel 5 premium
3-panel clinical interface is live on the Vercel staging deployment following
the completion of Sprint 18 / Module 126C-FABEL5-FINAL.

**Accuracy policy:** No step is marked PASS without real evidence. No evidence is
fabricated. No secrets, no real patient data, no production PHI in this document.

Staging uses fake/non-PHI data only. Production PHI readiness: NO-GO.

---

## 2. Deployment Baseline

| Item | Value |
|---|---|
| Commit | `0d0f952` — Sprint 18 / Module 126C-FABEL5-FINAL |
| Prior commit (FABEL5 overhaul) | `b646197` — Sprint 18 / Module 126C-FABEL5 |
| Frontend URL | `https://praximed.vercel.app` |
| Backend test suite | 3071/3071 passed |

---

## 3. Smoke Verification Results

### 3.1 /dashboard — Fabel 5 3-column interface

| Check | Expected | Status |
|---|---|---|
| /dashboard loads | Page renders without error | **PASS** |
| 3-column interface visible | Left / Center / Right panels present | **PASS** |
| "Incoming AI Intake Queue" visible | Left panel heading | **PASS** |
| "Active Resolution Workspace" visible | Center panel heading | **PASS** |
| "Audio Transcript & Call Recording" visible | Transcript panel in center workspace | **PASS** |
| "Patient Registry" visible | Right panel heading | **PASS** |
| Dynamic doctor/clinic banner visible | "Dr. Med. Alexander Huber \| Innere Medizin Wien" | **PASS** |
| Dev Console nav link absent | Not present in clinical header nav | **PASS** |

User-reported smoke result (Module 126C-FABEL5): **"Module 126C-FABEL5 deployed smoke visually passed."**
Module 126C-FABEL5-FINAL adds: Dev Console link removed from clinical nav (verified by static contract tests).

### 3.2 Fabel 5 palette and layout

| Check | Expected | Status |
|---|---|---|
| Primary Structural Ink background | #0B132B — deep navy on left panel and header | **PASS** |
| Clinical Accent teal | #008080 — interactive elements and highlights | **PASS** |
| Canvas background | #F4F6F9 — center panel | **PASS** |
| 3-panel CSS grid | `grid-template-columns: 25% / 45% / 30%` — embedded self-contained CSS | **PASS** |
| Responsive breakpoints | Layout adapts at 1200px and 768px | **PASS** |

### 3.3 Tenant identity — Dynamic doctor banner

| Check | Expected | Status |
|---|---|---|
| Doctor identity displayed | "Dr. Med. Alexander Huber \| Innere Medizin Wien" | **PASS** |
| Identity source | `tenantDisplay.ts` → `getClinicDisplayName()` — not hardcoded in page | **PASS** |
| Staging clinic_id mapped | `1a5bbc75-c1b0-4488-94aa-64b3f1c50056` | **PASS** |

### 3.4 /onboarding — Pilot gateway wizard

| Check | Expected | Status |
|---|---|---|
| /onboarding loads | Page renders without error | **PASS** |
| "Review & Pilot Activation" text visible | Step 5 label — no HTML entity leak | **PASS** |
| "STAGING SCAFFOLD — NOT FUNCTIONAL" badge visible | Amber pill badge | **PASS** |
| Pilot registration disabled | "Request Pilot Access Registration" button is non-functional | **PASS** |
| Safety copy visible | "Pilot activation requires security, legal, and production-readiness review before real patient data can be processed." | **PASS** |

### 3.5 /developer-console — Dark admin command theme

| Check | Expected | Status |
|---|---|---|
| /developer-console loads | Page renders without error | **PASS** |
| Dark admin theme | INK=#0B132B background — visually segregated from clinical UI | **PASS** |
| "Never paste secrets" guardrail visible | Red guardrail panel | **PASS** |
| "Production PHI remains NO-GO" guardrail visible | Red guardrail panel | **PASS** |
| All provisioning panels disabled | Tenant provisioning / Credential binding — demo only | **PASS** |
| Environment variable names shown as labels only | Values never displayed | **PASS** |
| Direct route accessible (not in clinical nav) | /developer-console reachable directly | **PASS** |

### 3.6 Safety boundaries — all three routes

| Check | Expected | Status |
|---|---|---|
| "STAGING DEMO" marker visible | Dashboard footer or badge | **PASS** |
| "Fake-data staging" / "no real patient data" visible | Dashboard and onboarding | **PASS** |
| "No real patient data" explicit | Footer safety text | **PASS** |
| "Production PHI: NO-GO" explicit | Dashboard footer and developer-console guardrail | **PASS** |
| No hardcoded secrets | Contract-tested: no JWT tokens, no API key literals in source | **PASS** |
| No sessionStorage / localStorage | Contract-tested | **PASS** |
| `credentials: "include"` in API client | Cookie-based auth preserved | **PASS** |

---

## 4. Static Contract Test Coverage (Module 126C-FABEL5-FINAL)

All 3071 backend tests pass, including:

| Test file | Tests | Result |
|---|---|---|
| `test_doctor_facing_interface_polish_contract.py` | 31 | PASS |
| `test_premium_frontend_dashboard_activation_contract.py` | 37 | PASS |
| `test_premium_frontend_interface_expansion_contract.py` | 56 | PASS |

Contract tests verify without browser or runtime:
- Tenant identity centralized in `tenantDisplay.ts`, never hardcoded in page
- "Audio Transcript & Call Recording" label and Vapi recording ingestion placeholder present
- Dev Console link absent from clinical nav (non-comment lines only)
- /developer-console route file exists with required safety content
- All preserved data-section / data-action / data-state attributes intact
- No diagnosis, no medical advice, no fake transcripts in dashboard source
- No hardcoded JWT tokens or API keys

---

## 5. Safety Constraints

| Constraint | Status |
|---|---|
| Fake/non-PHI data only | **CONFIRMED** — all data is fake staging data |
| No real patient data | **CONFIRMED** — no real names, phone, DOB, or medical records |
| No diagnosis in any display | **CONFIRMED** |
| No medical advice in any display | **CONFIRMED** |
| No auto-confirmation | **CONFIRMED** — doctor Confirm action required |
| No password recorded | **CONFIRMED** |
| No token recorded | **CONFIRMED** |
| No cookie value recorded | **CONFIRMED** |
| No JWT/webhook/Vapi secrets recorded | **CONFIRMED** |
| Production PHI readiness | **NO-GO** — C3–C8 hardening blockers still open |

---

## 6. What This Proves

1. The Fabel 5 premium 3-panel clinical interface (Incoming AI Intake Queue /
   Active Resolution Workspace / Patient Registry) is deployed and visible on Vercel.
2. The dynamic doctor/clinic banner resolves the staging tenant identity
   ("Dr. Med. Alexander Huber | Innere Medizin Wien") via `tenantDisplay.ts`.
3. The Audio Transcript & Call Recording placeholder is present with the Vapi
   recording ingestion message — no invented patient transcript content.
4. The /onboarding route renders the 5-step wizard with "Review & Pilot Activation"
   as plain text (no HTML entity leak).
5. The /developer-console route loads in the dark admin theme and is accessible
   directly — it is intentionally absent from the clinical header nav.
6. All three routes enforce the staging safety boundary: STAGING DEMO / fake data /
   no real patient data / Production PHI: NO-GO.
7. 3071/3071 backend contract tests pass on commit `0d0f952`.

---

## 7. What This Does Not Prove

- Real patient-data readiness — production PHI launch requires C3–C8 hardening
- Full DSGVO / Austrian data protection compliance
- External notification delivery — not implemented
- Vapi recording ingestion — pending (placeholder in place)
- Production readiness claim — not made at this stage

---

## 8. Next Steps

- **Clinic outreach demos** — use the premium dashboard as the primary demo asset;
  no real patient data needed for pilot demos
- **Production hardening track** — C3–C8 blockers must be resolved before
  production PHI can be processed
- **Vapi recording ingestion** — future module: wire real audio → transcript pipeline
- **Tenant provisioning** — future module: backend admin endpoint with audit trail
