# Sprint 19 / Module 134 — Internal Clinic Onboarding Review Console

Status: pending implementation.

## Context

Module 133 complete:
- `frontend/app/onboarding/page.tsx` — real controlled form submitting to POST /clinic-onboarding-requests
- `backend/tests/test_onboarding_frontend_backend_connection_contract.py` — 36 tests, all pass
- `docs/architecture/ONBOARDING_FRONTEND_BACKEND_CONNECTION.md`
- Two stale scaffold tests updated (staging badge, language selector)
- Frontend build: ✓ clean
- 3402/3402 backend tests pass
- Commit: Sprint 19 / Module 133 — Connect onboarding frontend to backend request API

The backend `GET /clinic-onboarding-requests` and `PATCH /clinic-onboarding-requests/{id}/status`
routes exist and are auth-protected, but there is no frontend UI to review them.

Production PHI remains NO-GO until C3–C8 hardening blockers are resolved.

## Goal

Build an internal review console page for PraxisMed staff/admin to view and process
submitted clinic onboarding requests, without creating production tenants automatically.

## What Module 134 must implement

### 1. Frontend — `/onboarding-review` page

`frontend/app/onboarding-review/page.tsx` (new):
- Requires authenticated session (redirects to /login if unauthenticated)
- Lists all submitted clinic onboarding requests via GET /clinic-onboarding-requests
- Shows: clinic_name, doctor_name, contact_email, specialty, city, preferred_language, status, created_at
- Status badge colours: submitted (WARN), reviewed (ACCENT), demo_booked (ACCENT), pilot_approved (green-ish), rejected (DANGER), archived (MUTED)
- Click row to expand details panel: full request fields, contact info, workflow preferences
- Status update dropdown + "Update Status" button → PATCH /clinic-onboarding-requests/{id}/status
- Empty state: "No pilot requests submitted yet."
- Staging demo badge visible
- No automatic tenant creation on any status change
- Safety copy: "Changing status to pilot_approved does not activate a production tenant."

### 2. Auth guard

Use existing `get_current_user` dependency pattern and cookie auth. Redirect to /login if not authenticated.

### 3. API client additions

`frontend/lib/api.ts` (updated):
- `fetchClinicOnboardingRequests()` → GET /clinic-onboarding-requests
- `updateClinicOnboardingRequestStatus(id, status)` → PATCH /clinic-onboarding-requests/{id}/status

### 4. Tests

`backend/tests/test_onboarding_review_console_contract.py` (new):
- Static tests verify the review page exists
- Contains "onboarding-review" route or heading
- Lists status labels (submitted, reviewed, demo_booked, pilot_approved, rejected, archived)
- Contains status update action
- Has safety copy: pilot_approved does not activate production tenant
- Staging demo badge present
- No sessionStorage / localStorage
- api.ts has fetchClinicOnboardingRequests
- api.ts has updateClinicOnboardingRequestStatus

### 5. Docs

- `docs/architecture/CLINIC_ONBOARDING_REVIEW_CONSOLE.md` (new)
- `docs/claude/CURRENT_STATE.md` — Module 134 entry
- `docs/claude/NEXT_MODULE.md` — updated to Module 135

## Constraints

- No automatic tenant creation on any status transition (including pilot_approved)
- No PHI displayed (onboarding requests contain clinic/doctor info only, not patient data)
- No secrets shown
- Status changes are admin markers only — provisioning requires a separate manual process
- Production PHI remains NO-GO
- Full test suite must remain green
- Frontend build must pass
