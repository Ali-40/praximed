# Sprint 19 / Module 147 — Live Vapi Binding Metadata Smoke Evidence

Status: pending implementation.

## Context

Module 146 complete:
- `frontend/app/developer-console/vapi-bindings/page.tsx` — dark admin UI for Vapi
  binding metadata (reference names only, no secret values, no live Vapi calls)
- `frontend/lib/api.ts` — fetchClinicVapiBindings / createClinicVapiBinding /
  updateClinicVapiBindingStatus (credentials: "include")
- `frontend/app/developer-console/page.tsx` — Vapi Binding Metadata panel + link
- `backend/tests/test_admin_vapi_binding_metadata_ui_contract.py` — static contract tests
- `docs/architecture/ADMIN_VAPI_BINDING_METADATA_UI.md` — arch doc
- Commit: Sprint 19 / Module 146 — Admin Vapi binding metadata UI

The full binding-metadata stack now exists end to end (migration → repo → service →
routes → admin UI), all under the Module 144 secret boundary: reference names only,
no actual secrets, no live Vapi API calls. production_phi_enabled remains False.

Production PHI remains NO-GO until C3–C8 hardening blockers are resolved.

## Goal

Capture live deployed smoke evidence that the admin Vapi binding metadata flow works
end to end on staging (Vercel frontend + Railway backend + Railway PostgreSQL):
create a binding metadata record for the staging clinic through the deployed UI,
load it back, and update its status — using reference names only.

## What Module 147 must verify (after push / deploy)

1. Vercel deployment includes /developer-console/vapi-bindings and the page loads
   in the dark admin theme with the ADMIN / STAGING badge.
2. Unauthenticated access shows "Admin session required. Please log in first."
3. After admin login, loading the staging clinic_id
   (1a5bbc75-c1b0-4488-94aa-64b3f1c50056) shows either the empty state or an
   existing binding.
4. Creating a binding with reference names
   (e.g. VAPI_API_KEY_REF_CLINIC_STAGING / VAPI_WEBHOOK_SECRET_REF_CLINIC_STAGING,
   german_first) succeeds: "Vapi binding metadata saved", status=draft,
   production_phi_enabled=false.
5. Entering an actual-looking secret value is rejected with the
   "Secret values are not allowed" copy (client and backend).
6. Status update draft → configured succeeds: "Binding status updated."
7. Database row (via internal API response, not direct DB screenshots with secrets)
   contains reference names only — no secret values.
8. Railway logs contain no secret values and no PHI for these requests.
9. Safety boundaries visible: no live Vapi calls, no Vapi secrets, no PHI,
   Production PHI remains NO-GO.

## Deliverables

- `docs/runtime/ADMIN_VAPI_BINDING_METADATA_DEPLOYED_SMOKE_EVIDENCE.md` (new)
- `backend/tests/test_admin_vapi_binding_metadata_deployed_smoke_evidence_contract.py` (new)
- `docs/claude/CURRENT_STATE.md` and `docs/claude/NEXT_MODULE.md` updates
  (NEXT_MODULE → Module 148 — External Notification Design / Secret Boundary)

## Constraints

- Docs/static-tests only. No runtime code changes unless a deployed defect is found.
- No fabricated evidence — only document what is actually observed on staging.
- No live Vapi API calls. No actual secrets anywhere (UI, DB, logs, docs, screenshots).
- No PHI. No real patient data. production_phi_enabled remains False.
- Production PHI remains NO-GO.
- Commit message:
  Sprint 19 / Module 147 — Live Vapi binding metadata smoke evidence
