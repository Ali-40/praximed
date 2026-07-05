# Doctor Notification System Foundation — PraxisMed Sprint 17 / Module 123 / 123A

**Status:** Implemented and blocker-fixed — internal notification record only. No external delivery.
**Date:** 2026-07-05
**Safety:** No diagnosis. No medical advice. Fake/non-PHI staging data only. Production PHI NO-GO.

---

## 1. Purpose

When a new appointment request is captured via Vapi, the clinic team needs to know
immediately — without manually refreshing the dashboard. Module 123 establishes the
internal notification foundation: a `clinic_notifications` row is created for every
new appointment request, scoped by clinic_id, referencing the appointment_request_id,
and carrying a safe factual brief.

This foundation enables:
- Dashboard alert badges and notification lists (current)
- Future: email/SMS/WhatsApp/push delivery when hardening is complete
- Future: doctor phone call notification via an outbound Vapi call

---

## 1A. Module 123A — Blocker Fix

**Root cause:** `appointment_request_repo.create_appointment_request` returns
`dict(asyncpg_record)`. asyncpg represents UUID columns as `uuid.UUID` Python
objects, not strings. The notification block passed `row.get("id")` (a `uuid.UUID`)
directly as `related_resource_id` to the notification INSERT, where the column type
is `TEXT`. asyncpg sends a UUID-OID typed parameter; PostgreSQL may reject it for a
TEXT column if the implicit UUID→TEXT cast is not applied in the binary protocol
parameter context — this caused a silent exception that was swallowed by
`except Exception: notification_created = False` with no logging.

**Fixes applied in Module 123A:**

1. `str(row["id"])` — convert asyncpg `uuid.UUID` to plain `str` before passing
   as `related_resource_id` (TEXT column). asyncpg sends str with text OID → no
   type mismatch.

2. `logger.error(...)` — the exception is now logged at ERROR level. If another
   cause exists, it will appear in Railway logs and is no longer invisible.

3. `notification_error` — added to the return dict of
   `capture_vapi_appointment_request`. `None` on success; `"ExcType: message"` on
   failure. Allows tests and observability to distinguish success from failure.

**Why tests passed before the fix:** All tests mocked `create_appointment_request_notification`
at the module level — the real asyncpg INSERT call was never exercised. The fix adds
test 16 which injects a `uuid.UUID` as the row id and asserts the notification call
receives a `str`.

---

## 2. Internal Notification Foundation — What Is Implemented

### 2.1 Notification creation trigger

`capture_vapi_appointment_request` (in `backend/app/modules/vapi/vapi_appointment_capture.py`)
calls `notification_router.create_appointment_request_notification` after
a successful appointment_request insert. The call is wrapped in try/except — a
notification failure is non-fatal and is surfaced in the response as
`notification_created: false`, so the Vapi capture flow is never blocked.

### 2.2 Notification content

| Field | Value |
|---|---|
| `notification_type` | `"appointment_request"` |
| `channel` | `"internal"` |
| `priority` | Derived from `urgency_level` via `infer_priority` |
| `title` | `"New appointment request"` |
| `message` | `"New appointment request from {patient_name}. Reason: {reason}. Action: {suggested_next_action}."` |
| `related_resource_type` | `"appointment_requests"` |
| `related_resource_id` | The `appointment_requests.id` UUID |
| `clinic_id` | Tenant-scoped clinic UUID |
| `status` | `"pending"` (initial) |

The message includes:
- Patient name (from Vapi intake — not a real patient name in staging)
- Reason (from Vapi intake fields, optional)
- Suggested next action — always `"Review and confirm"` for new Vapi requests

The message never includes:
- Diagnosis
- Medical recommendation or advice
- Treatment or prognosis
- Secrets or credentials

### 2.3 Data model

The `clinic_notifications` table (defined in `backend/app/db/schema.sql`,
managed by `backend/app/db/repositories/notification_repo.py`):

```
clinic_notifications
├── id                  UUID PK
├── clinic_id           UUID FK → clinics.id  (tenant isolation)
├── recipient_user_id   UUID nullable (broadcast when null)
├── channel             TEXT CHECK (internal|sms|push|email|webhook)
├── notification_type   TEXT CHECK (appointment_request|urgent_call|...)
├── priority            TEXT CHECK (low|normal|high|urgent|emergency)
├── title               TEXT
├── message             TEXT
├── status              TEXT CHECK (pending|sent|failed|read|cancelled)
├── related_resource_type TEXT nullable
├── related_resource_id   TEXT nullable  ← appointment_requests.id
├── scheduled_for       TIMESTAMPTZ nullable
├── sent_at             TIMESTAMPTZ nullable
├── read_at             TIMESTAMPTZ nullable
├── error_message       TEXT nullable
├── raw_payload         JSONB nullable
├── created_at          TIMESTAMPTZ DEFAULT now()
└── updated_at          TIMESTAMPTZ DEFAULT now()
```

No migration is required for Module 123 — the table already exists from Module 20/21.

---

## 3. Tenant Isolation

Every notification row is scoped to a `clinic_id`. The notification_repo enforces
`WHERE clinic_id = $1` on all reads. The notification list route enforces
`require_staff_clinic_access` — a caller cannot read another clinic's notifications
via the API. Tenant isolation is verified by test 15 (403 for wrong clinic).

---

## 4. API Endpoints

All notification endpoints require a valid JWT with `clinic_id` matching the query param.

| Method | Path | Description |
|---|---|---|
| `POST` | `/notifications` | Create notification (staff+) |
| `GET` | `/notifications?clinic_id=...` | List notifications for clinic |
| `GET` | `/notifications/{id}?clinic_id=...` | Fetch single notification |
| `POST` | `/notifications/{id}/read?clinic_id=...` | Mark as read |
| `POST` | `/notifications/{id}/cancel?clinic_id=...` | Cancel notification |

---

## 5. No External Delivery — What This Means

`channel = "internal"` means the notification is a DB record only. No SMS, push,
email, WhatsApp, or phone call is made by this module.

Future delivery modules will:
1. Query `clinic_notifications WHERE status='pending' AND channel='sms'` (or push/email)
2. Call the appropriate delivery gateway
3. Update `status` to `"sent"` or `"failed"` with `sent_at`/`error_message`

The `channel` enum in the schema already reserves `sms`, `push`, `email`, `webhook`
for this purpose — no schema change is needed to add delivery later.

---

## 6. How This Enables Doctor Phone Notification Later

A future module can:
1. Listen for `clinic_notifications` rows with `notification_type = "appointment_request"`
   and `status = "pending"`
2. Trigger an outbound Vapi call to the on-call doctor's phone
3. Read the notification message as the Vapi call script
4. Mark the notification as `sent` or `failed` based on call outcome

No code change is needed to the notification creation path — only a delivery consumer
needs to be added.

---

## 7. Safety Boundaries

| Constraint | Enforced by |
|---|---|
| No diagnosis in notification | Message builder — only factual intake fields used |
| No medical advice | Same — `suggested_next_action` is a staff workflow prompt, not clinical advice |
| Doctor/staff approval required | Appointment remains `status=new, action_required=true` — notification does not confirm it |
| No auto-confirmation | `capture_vapi_appointment_request` never sets `status=confirmed` |
| No external delivery | `channel="internal"` only; no SMS/push/email/webhook sent |
| Tenant isolation | `clinic_id` enforced at repo and route layer |
| Fake data only | All staging data is non-PHI; no real patient names/phones/DOBs |
| Production PHI readiness | NO-GO — C3–C8 hardening blockers still open |

---

## 8. What This Enables Next

- **Module 124** — Deployed Doctor Notification Smoke Evidence: redeploy, create
  fake Vapi request, verify notification row exists, verify list endpoint returns it.
- **Module 125** — Consultation summary draft generator (post-notification)
- **Module 126** — Follow-up and reminder workflow
- **Sprint 18** — Fabel 5 premium UI/UX: surface notification badge/list on dashboard
