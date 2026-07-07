# Admin Vapi Binding Metadata UI

Sprint 19 / Module 146 — internal admin panel for Vapi binding metadata.

## Purpose

Give an internal operator a safe browser UI to create, view, and update the
Vapi binding metadata records introduced in Module 145 — without ever exposing,
entering, or transmitting an actual secret. The page manages **secret reference
names only** (environment-variable labels such as `VAPI_API_KEY_REF_CLINIC_DEMO`);
the actual credential values live exclusively in secure environment variables
on the backend deployment and are never present in the browser, the database,
or any API response.

## Route

`/developer-console/vapi-bindings`
(`frontend/app/developer-console/vapi-bindings/page.tsx`), linked from the
Vapi Binding Metadata panel on the developer console page. Dark admin command
theme (#0B132B ink, teal #008080 accents, red #E63946 guardrails, amber
#FFB703 warnings) — visually segregated from the clinical UI.

## What the page does

1. **Load** — operator pastes a provisioned clinic_id (or the staging
   clinic_id `1a5bbc75-c1b0-4488-94aa-64b3f1c50056`) and loads the latest
   binding via `GET /clinics/{clinic_id}/vapi-bindings`. Shows status badge,
   reference-name labels, language_mode, assistant_id / phone_number_id /
   vapi_project_id / assistant_config_version (read-only; set by a later
   live-binding module), production_phi_enabled (always false), and timestamps.
   Empty state: "No Vapi binding found for this clinic."
2. **Create** — form with `api_key_secret_ref`, `webhook_secret_ref`
   (environment-variable reference names only, never secret values) and
   `language_mode` (german_first / english_first / bilingual_auto), submitted
   via `POST /clinics/{clinic_id}/vapi-bindings`. A client-side pattern
   (`^[A-Z][A-Z0-9_]{2,99}$`) mirrors the backend validator and blocks anything
   resembling an actual secret before it leaves the browser; the backend
   rejects actual-looking values with 400/422 regardless. New bindings start
   at status `draft`.
3. **Update status** — draft / configured / disabled / revoked via
   `PATCH /clinic-vapi-bindings/{binding_id}/status`.

All requests go through the shared `lib/api.ts` helpers
(`fetchClinicVapiBindings`, `createClinicVapiBinding`,
`updateClinicVapiBindingStatus`), which apply `NEXT_PUBLIC_API_BASE_URL` and
`credentials: "include"` (cookie session). Error states are mapped to safe
copy: 401/403 → "Admin session required. Please log in first.", clinic 404 →
"Clinic not found or no access.", validation → "Secret values are not
allowed…", generic → "Could not load Vapi binding metadata."

## Secret boundary

- Reference names only; no actual VAPI_API_KEY or webhook secret values are
  accepted, displayed, stored, logged, or transmitted by this page.
- No input field exists for a secret value; there is no password-type field.
- Actual credentials are managed via secure environment variables on the
  backend deployment, per the Module 144 secret boundary.

## What this enables

An operator can register which environment-variable labels a clinic's future
live Vapi binding will use, and track the binding lifecycle
(draft → configured → disabled/revoked), without any secret ever entering the
browser. This is the last scaffolding step before Module 147 captures live
binding metadata smoke evidence.

## Hard limits

- No live Vapi API calls are made from this page.
- No PHI. No patient data. No call recordings.
- No production activation. `production_phi_enabled` remains false everywhere.
- Production PHI remains NO-GO until the C3–C8 readiness gate and
  Article 28/32 review are complete.
