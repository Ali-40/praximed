# Dashboard Notification and Summary UI Foundation

**Sprint:** Sprint 17 / Module 125
**Status:** Implemented — functional; premium polish deferred to Sprint 18 (Fabel 5)
**Date:** 2026-07-05

---

## 1. Purpose

Wire the internal `clinic_notifications` foundation (Module 123/123A/124) and the
pre-appointment summary endpoint (Module 122) into the existing dashboard UI so clinic
staff and doctors can see notification alerts and per-appointment summaries without
a new UI being built from scratch. Sprint 18 (Fabel 5) handles premium polish.

---

## 2. What Changed

### `frontend/lib/api.ts`

- Added `PreAppointmentSummary` interface (all fields from `build_pre_appointment_summary`
  service: `patient_name`, `patient_type`, `reason`, `urgency_level`,
  `previous_request_count`, `suggested_next_action`, `safety_note`, etc.)
- Added `fetchPreAppointmentSummary(requestId, clinicId)` — calls
  `GET /appointment-requests/{id}/pre-appointment-summary?clinic_id=...`
  through the shared `apiFetch` wrapper (cookie-based auth, `credentials: "include"`)

### `frontend/app/dashboard/page.tsx`

**Appointments section:**
- Added `summaryOpenId: string | null` state — tracks which row's summary panel is open
- Added `summaries: Record<string, PreAppointmentSummary | 'loading' | 'error'>` — caches
  fetched summaries so re-opening a row doesn't re-fetch
- Added `handleViewSummary(appt)` — toggles open/close; fetches on first open; sets
  `'loading'` then `PreAppointmentSummary` or `'error'`
- Each appointment row now has a "View summary" / "Hide summary" toggle button
- Inline `data-state="summary-panel"` panel below each row shows:
  patient_name, patient_type, reason, urgency_level, previous_request_count,
  suggested_next_action, safety_note
- **No diagnosis. No medical advice.**
- Existing Confirm button unchanged; works only when `status === 'new'`

**Notifications section:**
- Each notification row now shows `message` (truncated to 100 chars) below the title
- Status badge shown alongside priority badge
- Rows with `status === 'pending'` receive a highlighted background

---

## 3. Data Flow

```
Dashboard load
  └── fetchNotifications(clinic_id)
        └── GET /notifications?clinic_id=...
              └── clinic_notifications rows
                    title, message, status (pending/read), priority, created_at

Appointment row click "View summary"
  └── fetchPreAppointmentSummary(request_id, clinic_id)
        └── GET /appointment-requests/{id}/pre-appointment-summary?clinic_id=...
              └── build_pre_appointment_summary (rule-based, no AI)
                    patient_name, patient_type, reason, urgency_level,
                    previous_request_count, suggested_next_action, safety_note
```

---

## 4. Safety Constraints

- No diagnosis displayed — summary shows only structured factual fields
- No medical advice displayed — `suggested_next_action` is a workflow hint ("Review and confirm"),
  not clinical guidance
- `safety_note` is always rendered — backend always returns it; display is mandatory
- No auto-confirm — doctor/staff must press Confirm explicitly; summary is read-only
- Fake/non-PHI data only in all staging tests
- No secrets in any file; no token storage in browser (cookie-based session)
- Production PHI: NO-GO (C3–C8 hardening blockers still open)

---

## 5. Endpoints Used

| Endpoint | Method | Purpose |
|---|---|---|
| `/notifications?clinic_id=...` | GET | List internal clinic notifications |
| `/appointment-requests/{id}/pre-appointment-summary?clinic_id=...` | GET | Fetch safe structured summary |
| `/appointment-requests/{id}/status?clinic_id=...` | PATCH | Confirm appointment (existing) |

All requests use `credentials: "include"` — session cookie set by `POST /auth/login`.

---

## 6. What Is Deferred

- Premium UI/UX polish — Sprint 18 (Fabel 5)
- Notification read/dismiss action
- Notification delivery: phone, email, SMS, WhatsApp — NOT implemented
- Real-time notification push (WebSocket/SSE) — NOT implemented
- Summary auto-refresh on Confirm

---

## 7. Related Modules

- Module 122 — `build_pre_appointment_summary` service and route
- Module 122B — Deployed smoke for pre-appointment summary
- Module 123 — Doctor notification system foundation (internal channel)
- Module 123A — UUID→str blocker fix; logging added
- Module 124 — Deployed doctor notification smoke evidence
