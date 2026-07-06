# PraxisMed — Staging End-to-End Demo Runbook

**Sprint 19 / Module 130**
**Date:** 2026-07-06
**Environment:** Vercel + Railway staging — fake data only
**Production PHI: NO-GO**

---

## Safety Rules

- **No real patient data** — use only synthetic demo data as specified below.
- **No secrets recorded** — do not paste passwords, tokens, or cookie values into notes, screenshots, or this document.
- **No production PHI** — staging environment only. No real patient records exist here.
- **No external delivery** — no SMS/email/WhatsApp is sent from staging.
- **This runbook is for staging demo only.** No production readiness claim is made.

---

## Prerequisites

- Access to the staging doctor login (credentials held separately — not recorded here).
- `curl` installed locally (or use any HTTP client: Insomnia, Postman, HTTPie).
- Browser open to `https://praximed.vercel.app`.

---

## Step 1 — Verify Backend Health

Run both health checks before starting the demo. Both must return `ok` / `ready`.

```bash
# Liveness probe
curl -s https://web-production-fd91d.up.railway.app/health
# Expected: {"status":"ok","service":"PraxisMed API"}

# Readiness probe
curl -s https://web-production-fd91d.up.railway.app/health/ready
# Expected: {"status":"ready","checks":{"app":"ok"}}
```

If either check fails, the backend is down — do not continue the demo.

---

## Step 2 — Open Vercel Dashboard and Log In

1. Open `https://praximed.vercel.app` in a browser.
2. Navigate to `/login` if not redirected automatically.
3. Enter the staging doctor credentials (do not record credentials here).
4. After login, you should be redirected to `/dashboard`.
5. The header should show: **Dr. Med. Alexander Huber | Innere Medizin Wien**
6. The staging demo badge and "no real patient data" disclaimer should be visible.

---

## Step 3 — Inject a Fake Vapi Intake Request

This simulates a patient calling the Vapi receptionist. Use synthetic demo data only.

```bash
curl -s -X POST \
  https://web-production-fd91d.up.railway.app/vapi/tools/capture-appointment-request \
  -H "Content-Type: application/json" \
  -H "X-Vapi-Service-Name: vapi" \
  -H "X-Vapi-Clinic-Id: 1a5bbc75-c1b0-4488-94aa-64b3f1c50056" \
  -H "X-Vapi-Scopes: vapi:tool" \
  -d '{
    "clinic_ref": "1a5bbc75-c1b0-4488-94aa-64b3f1c50056",
    "call_id": "demo-call-001",
    "patient_name": "Demo Patient",
    "caller_phone": "+436601234567",
    "reason": "Routine appointment request demo",
    "preferred_starts_at": "2026-07-14T09:00:00+02:00",
    "preferred_ends_at": "2026-07-14T09:30:00+02:00",
    "urgency_level": "normal"
  }'
```

**Expected response:**
```json
{
  "ok": true,
  "message": "...",
  "request": { "id": "...", "status": "new", ... }
}
```

Note the `id` from the response — you can use it in Steps 4 and 5.

**Demo patient data used:**
- Name: `Demo Patient`
- Phone: `+436601234567`
- Reason: `Routine appointment request demo`
- Preferred time: next Monday morning (2026-07-14 09:00–09:30 CEST)
- Urgency: `normal`

---

## Step 4 — Verify Appointment Appears in Dashboard

1. In the browser, refresh `/dashboard` (or it may update automatically).
2. In the **Incoming AI Intake Queue** (left panel), the new "Demo Patient" request should appear with status `new`.
3. Verify the patient name, reason, and urgency level are visible.
4. Verify no real patient data appears anywhere.

---

## Step 5 — Open View Summary

1. Click **View summary** on the "Demo Patient" row in the intake queue.
2. The **Active Resolution Workspace** (center panel) should expand to show:
   - Patient name and phone
   - Reason for appointment
   - Preferred time
   - AI-suggested next action (if populated)
   - **Audio Transcript & Call Recording** section with the Vapi ingestion placeholder message
3. The transcript placeholder should read: *"Recording/transcript review will appear here when Vapi recording ingestion is enabled."*

---

## Step 6 — Confirm the Appointment

1. In the Active Resolution Workspace, click the **Confirm** button (or equivalent confirm action).
2. The appointment status should update from `new` to `confirmed`.
3. The row should move out of the pending queue.
4. A confirmation notification should appear in the **notifications** section.

---

## Step 7 — Verify Patient Registry Updates

1. Open the **Patient Registry** (right panel) in the dashboard.
2. The "Demo Patient" record should now appear (created or matched during intake).
3. Verify the patient row shows the clinic_id scoped to the staging clinic.
4. No real patient names or records should appear.

---

## Step 8 — Verify Notification

1. Check the notifications section of the dashboard.
2. A notification for the "Demo Patient" appointment request should appear (type: `new_appointment_request`).
3. After confirm, the notification should reflect the resolved state.

---

## Step 9 — Log Out

1. Click **Log Out** in the dashboard header.
2. Verify you are redirected to `/login` or the landing page.
3. Verify the session is cleared — refreshing `/dashboard` should redirect to login.

---

## Step 10 — Post-Demo Verification Checklist

| Check | Expected | Done? |
|---|---|---|
| Backend health (liveness) | `{"status":"ok"}` | ☐ |
| Backend ready (readiness) | `{"status":"ready"}` | ☐ |
| Dashboard loads | 3-panel layout visible | ☐ |
| Doctor banner visible | "Dr. Med. Alexander Huber \| Innere Medizin Wien" | ☐ |
| Staging safety banner visible | "no real patient data" / "Production PHI: NO-GO" | ☐ |
| Vapi intake accepted | `{"ok":true}` response | ☐ |
| Appointment appears in queue | "Demo Patient" in Incoming AI Intake Queue | ☐ |
| View summary works | Center panel expands with patient details | ☐ |
| Confirm works | Status changes to confirmed | ☐ |
| Patient Registry updates | Demo Patient record visible | ☐ |
| Notification appears | New appointment notification visible | ☐ |
| Logout works | Redirected to login | ☐ |
| No real patient data observed | ✓ — all data is fake demo data | ☐ |
| No secrets recorded | ✓ — no credentials in notes | ☐ |

---

## Troubleshooting

**Vapi intake returns 401 / 403:**
- Verify the `X-Vapi-Clinic-Id` header matches the staging clinic_id exactly.
- Verify `X-Vapi-Service-Name: vapi` and `X-Vapi-Scopes: vapi:tool` are present.
- Check that the backend is running (`/health` returns ok).

**Dashboard shows no appointments after curl:**
- Wait 2–3 seconds and refresh — the backend write is synchronous but the browser may cache.
- Verify the curl response contained `"ok": true` before refreshing.

**`call_id` conflict (duplicate key):**
- Change `"call_id": "demo-call-001"` to `"demo-call-002"` (or any unique string) and retry.

**Backend is down:**
- Check Railway dashboard for service status.
- The Vercel frontend will show API errors — this is expected during Railway restarts.

---

## Notes

- Recording/transcript ingestion is not yet enabled. The "Audio Transcript & Call Recording" section shows a placeholder only.
- No external delivery (SMS, email) is wired. Confirming an appointment does not send any message to the patient.
- All data created during this demo is fake staging data. It can be cleared via database reset if needed.
- Production PHI remains NO-GO until C3–C8 hardening blockers are resolved.
