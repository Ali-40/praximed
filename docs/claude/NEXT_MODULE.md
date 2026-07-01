# Sprint 3 / Module 40 — Apply Machine Guards to Vapi, n8n, and Availability Routes

## Current project folder
`/Users/aliabdeltawab/Documents/praximed`

## Completed modules
- Sprint 1, Modules 1–23: all committed.
- Sprint 2, Modules 24–34: all committed.
- Sprint 3, Modules 35–39: all committed.

Do not modify completed modules unless absolutely required.

## Task scope
Apply the existing MachineAuthContext dependencies to machine/internal API routes.

## Purpose
Human-facing PHI routes are now protected. This module protects machine-facing routes used by:

- Vapi tools
- Vapi webhooks
- n8n calendar sync
- availability check/suggest endpoints

These routes should not use human AuthContext. They should use the machine access helpers created in Module 39.

## Protect these route groups only

1. Vapi tool routes
2. Vapi webhook routes
3. n8n calendar sync webhook route
4. calendar availability check/suggest routes

Do not modify patient routes.
Do not modify consultation routes.
Do not modify clinical workflow routes.
Do not modify appointment request routes.
Do not modify notification routes.
Do not modify auth_context.py.
Do not modify machine_auth.py unless absolutely required by tests.
Do not modify repositories.
Do not modify service modules.
Do not use a real database in tests.

## Access policy

### A) Availability routes

Apply availability-read machine access:
- allowed services: vapi, internal, system, dashboard
- required scope: availability:read
- requested clinic_id must match MachineAuthContext.clinic_id unless service has internal:admin scope

Use: `get_machine_auth_context`, `require_availability_read_access`

Routes:
- POST /calendar/availability/check
- POST /calendar/availability/suggest

Clinic ID source: `body.clinic_id`

### B) Vapi tool routes

Apply Vapi tool machine access:
- allowed services: vapi, internal, system
- required scope: vapi:tool
- requested clinic_id must match MachineAuthContext.clinic_id unless service has internal:admin scope

Use: `get_machine_auth_context`, `require_vapi_tool_access`

Routes:
- POST /vapi/tools/check-availability
- POST /vapi/tools/suggest-slots
- any Vapi appointment capture tool route if it exists

Clinic ID source: body.clinic_id or resolved clinic_id from the request schema/config logic.

### C) Vapi webhook routes

Apply Vapi webhook machine access:
- allowed services: vapi, internal, system
- required scope: vapi:webhook
- requested clinic_id must match MachineAuthContext.clinic_id if clinic_id is available in payload

Use: `get_machine_auth_context`, `require_vapi_webhook_access`

Routes:
- POST /webhooks/vapi/call-event

Clinic ID source: normalized event clinic_id if available.

### D) n8n calendar sync webhook route

Apply n8n calendar sync machine access:
- allowed services: n8n, internal, system
- required scope: calendar:sync
- requested clinic_id must match MachineAuthContext.clinic_id unless service has internal:admin scope

Use: `get_machine_auth_context`, `require_n8n_calendar_sync_access`

Routes:
- POST /webhooks/n8n/calendar-sync

Clinic ID source: `body.clinic_id`

## Error behavior

- Missing machine auth headers → HTTP 401
- Invalid service name → HTTP 401
- Invalid scope → HTTP 401
- Wrong clinic_id → HTTP 403
- Service not allowed → HTTP 403
- Missing required scope → HTTP 403
- Existing validation errors remain HTTP 422 where applicable
- Existing repository/service errors keep current mappings
- Missing db_pool remains HTTP 503, but machine authorization may happen before db_pool access

## Acceptance criteria

- All Module 40 tests pass.
- All previous tests still pass.
- Vapi tool routes require machine auth and vapi:tool scope.
- Vapi webhook routes require machine auth and vapi:webhook scope.
- n8n calendar sync route requires machine auth and calendar:sync scope.
- Availability routes require machine auth and availability:read scope.
- No real database connection is used.
- Human AuthContext is not used for machine routes.
- Patient/consultation/clinical workflow/appointment/notification route behavior is not changed.
- Commit all changes only if tests pass.

## Commit message

`Sprint 3 / Module 40 — Apply machine guards to integration routes`
