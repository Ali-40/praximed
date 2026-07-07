# Live Vapi Binding Metadata Smoke Evidence

**Sprint 19 / Module 147**
**Date:** 2026-07-07
**Commit tested:** 47c6940 (Sprint 19 / Module 146 — Admin Vapi binding metadata UI)

---

## 1. Purpose

Record live staging evidence that the admin Vapi binding metadata UI can load,
create, and update Vapi binding metadata records using secret reference names only.

Accuracy policy: only document what was actually observed on staging. No fabricated
success evidence. No secrets. No PHI.

---

## 2. Current Result

**PASS**

The admin Vapi binding metadata UI loads, creates, and updates Vapi binding metadata
records on the deployed Railway + Vercel staging environment. Reference names are
stored. Actual secret values are rejected. No live Vapi API calls are made.
production_phi_enabled remains false.

---

## 3. Live Route Tested

| Component | Detail |
|---|---|
| Frontend URL | https://praximed.vercel.app/developer-console/vapi-bindings |
| Backend service | https://web-production-fd91d.up.railway.app |
| Backend database | Railway PostgreSQL (fake/non-PHI staging) |
| Commit tested | 47c6940 |
| Environment | staging (ENVIRONMENT=staging) |
| Auth | httpOnly Secure SameSite=None cookie (praximed_session) |

---

## 4. Clinic ID Used

| Field | Value |
|---|---|
| clinic_id | 1a5bbc75-c1b0-4488-94aa-64b3f1c50056 |
| Clinic name | Demo Wahlarzt Praxis Wien (staging fake clinic — not a real clinic) |
| Source | Provisioned in Module 115 (fake staging tenant) |

This is a fake staging clinic. No real clinic, doctor, or patient is associated.

---

## 5. Railway Migration and Table Evidence

| Check | Result |
|---|---|
| Migration 0005_clinic_vapi_bindings applied | PASS |
| clinic_vapi_bindings table exists in Railway PostgreSQL | PASS |
| GET /clinics/{clinic_id}/vapi-bindings returns 200 | PASS |
| POST /clinics/{clinic_id}/vapi-bindings returns 201 | PASS |
| PATCH /clinic-vapi-bindings/{binding_id}/status returns 200 | PASS |

Migration 0005 was applied as part of Module 145. The table contains the columns
id, clinic_id, api_key_secret_ref, webhook_secret_ref, language_mode, status,
assistant_id, phone_number_id, vapi_project_id, created_by_user_id,
created_at, updated_at — all confirmed via API response.

---

## 6. Load Bindings Evidence

| Check | Result |
|---|---|
| Page /developer-console/vapi-bindings loads | PASS |
| Dark admin theme rendered (ADMIN / STAGING badge visible) | PASS |
| Clinic ID input field present | PASS |
| "Load bindings" button present | PASS |
| Entering staging clinic_id + clicking Load bindings | PASS |
| GET /clinics/1a5bbc75.../vapi-bindings returned 200 | PASS |
| No existing binding initially: empty state shown | PASS |
| Safety copy visible: "Reference names only. Never enter VAPI_API_KEY..." | PASS |
| "Production PHI remains NO-GO" safety copy visible | PASS |

---

## 7. Create Binding Metadata Evidence

| Field | Value submitted |
|---|---|
| api_key_secret_ref | VAPI_API_KEY_REF_STAGING_DEMO |
| webhook_secret_ref | VAPI_WEBHOOK_SECRET_REF_STAGING_DEMO |
| language_mode | german_first |

| Check | Result |
|---|---|
| POST /clinics/1a5bbc75.../vapi-bindings returned 201 | PASS |
| Success message: "Vapi binding metadata saved" | PASS |
| Binding id returned and visible in UI | PASS |
| clinic_id visible in response | PASS |
| status: draft visible | PASS |
| language_mode: german_first visible | PASS |
| api_key_secret_ref: VAPI_API_KEY_REF_STAGING_DEMO visible as reference label | PASS |
| webhook_secret_ref: VAPI_WEBHOOK_SECRET_REF_STAGING_DEMO visible as reference label | PASS |
| production_phi_enabled: false in response | PASS |

No actual VAPI_API_KEY value was entered. No actual webhook secret value was entered.
The ui accepts only reference-name-format strings.

---

## 8. Secret Reference Names Evidence

| Check | Result |
|---|---|
| api_key_secret_ref stored as uppercase reference label | PASS |
| webhook_secret_ref stored as uppercase reference label | PASS |
| No Vapi API key value stored in database | PASS (reference label only) |
| No webhook secret value stored in database | PASS (reference label only) |
| Reference names visible in UI response without resolving secret | PASS |
| No actual secret value returned in GET response | PASS |

The reference names VAPI_API_KEY_REF_STAGING_DEMO and
VAPI_WEBHOOK_SECRET_REF_STAGING_DEMO are labels pointing to environment variables.
Their actual values were never entered into the UI, never transmitted to the backend,
and never stored in the database.

---

## 9. Invalid Non-Reference Input Rejection Evidence

| Input tested | Result |
|---|---|
| api_key_secret_ref set to lowercase string | Rejected — 422 |
| api_key_secret_ref starting with "sk-" | Rejected — 422 |
| Empty reference name submitted | Rejected — 422 |
| Mixed-case non-reference string | Rejected — 422 |

The frontend shows "Secret values are not allowed — use uppercase reference names only
(e.g. VAPI_API_KEY_REF_CLINIC_XXX)." or the equivalent 422 validation message.
The backend Pydantic validator enforces the ^[A-Z][A-Z0-9_]{2,99}$ pattern and rejects
known secret-looking prefixes (sk-, vapi_live_).

---

## 10. Status Update Evidence

| Status transition | Result |
|---|---|
| Load binding: status=draft visible | PASS |
| PATCH status draft → configured | PASS |
| "Binding status updated" confirmation visible | PASS |
| PATCH status configured → disabled | PASS |
| "Binding status updated" confirmation visible | PASS |
| Invalid status rejected (e.g. "active") | PASS — 422 |

PATCH /clinic-vapi-bindings/{binding_id}/status accepts only
draft / configured / disabled / revoked.

---

## 11. production_phi_enabled False Evidence

| Check | Result |
|---|---|
| POST response: production_phi_enabled=false | PASS |
| GET response: production_phi_enabled=false | PASS |
| PATCH response: production_phi_enabled=false | PASS |
| UI never shows production_phi_enabled=true | PASS |

production_phi_enabled is hardcoded False at the service layer and injected into every
response. It is not accepted from user input, not stored in the database, and not
controllable from the UI.

---

## 12. Safety Boundaries

The following were confirmed during the smoke session:

| Constraint | Confirmed |
|---|---|
| No actual VAPI_API_KEY entered into any field | Yes |
| No actual VAPI_WEBHOOK_SECRET entered into any field | Yes |
| No live Vapi API call made during binding creation | Yes |
| No Vapi assistant created or modified | Yes |
| No PHI entered | Yes |
| No patient name, phone, reason, or appointment data entered | Yes |
| No transcript entered or stored | Yes |
| No recording URL entered or stored | Yes |
| No sessionStorage or localStorage used | Yes |
| production_phi_enabled=false in all responses | Yes |
| ENVIRONMENT=staging (Railway env) | Yes |
| PRODUCTION_COMPLIANCE_UNLOCKED not set | Yes |
| Production PHI remains NO-GO | Yes |

No sensitive or personal data was entered, stored, transmitted, or observed during
this smoke session.

---

## 13. What This Proves

- The clinic_vapi_bindings table exists in Railway PostgreSQL and is accessible.
- Migration 0005 is applied and functional on the staging database.
- The admin UI at /developer-console/vapi-bindings loads and operates correctly.
- A Vapi binding metadata record can be created using secret reference names.
- Secret reference names are stored and returned correctly.
- Actual-looking secret values (sk-..., lowercase strings) are rejected.
- Status transitions (draft → configured → disabled) work via the PATCH route.
- production_phi_enabled is always false in all API responses and visible in the UI.
- Auth protection works: the page requires a valid session cookie.
- The entire binding metadata stack works end to end on deployed staging:
  Vercel frontend → Railway backend → Railway PostgreSQL.
- No live Vapi API call is made at any point in the binding creation flow.

---

## 14. What This Does Not Prove

- Production readiness — staging is fake data only; production PHI is NO-GO.
- GDPR / DSGVO / Article 28 AVV with Vapi — legal review not complete.
- C3–C8 security hardening — all blockers still open.
- Actual Vapi API key validity — no key resolution is attempted or proven.
- Vapi assistant binding — no assistant is created; this is metadata only.
- Phone number provisioning — phone_number_id remains null.
- Live Vapi call using the stored binding — deferred until C3–C8 cleared.
- Multi-tenant isolation at scale — tested for one staging tenant only.
- Audit log completeness — audit events written but not separately verified here.

---

## 15. Remaining Blockers

Production PHI remains NO-GO until the following are resolved:

| Blocker | Status |
|---|---|
| C3 — Production secrets provisioning (managed secret store) | OPEN |
| C4 — GDPR / Austrian DSG / Article 28 AVV with Vapi | OPEN |
| C5 — Article 32 technical and organisational measures | OPEN |
| C6 — Pseudonymisation at rest + in transit | OPEN |
| C7 — Audit log completeness and retention | OPEN |
| C8 — Backup and disaster recovery | OPEN |
| Vapi live credential resolution service | PENDING |
| Live Vapi assistant provisioning | PENDING — blocked on C3–C8 |
| Recording ingestion pipeline | PENDING |
| Transcript storage with pseudonymisation | PENDING |
