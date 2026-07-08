# Sprint 20 / Module 156 — Longitudinal Timeline and Delta View Foundation

Status: pending.

## Context

Module 155 complete (Live Doctor Review & Merge Smoke Evidence):
- Full intake → structure → review → merge pipeline verified live on staging.
- Staff reject and approve/merge flows confirmed.
- Approved patient_history_* rows created only after explicit staff confirmation.
- No auto-approval. No external LLM. No PHI.
- 4975/4975 backend tests passing. Frontend build clean.
- Production PHI remains NO-GO.

## Goal

Build a longitudinal patient timeline aggregator that collects approved structured history entries,
recent intake submissions, consent events, and structuring run summaries into a single chronological
view for a given patient. Add a delta view showing changes since the last appointment visit.

No diagnosis. No medical advice. No triage scoring. No treatment recommendations.
Approved structured data only for the clinical timeline (status=approved, source_type=ai_proposal).
Unverified proposals shown separately, clearly labeled as unverified.
Production PHI remains NO-GO.

## What Module 156 must implement

### 1. Backend timeline aggregator

New service: `backend/app/services/patient_timeline.py`

Function: `get_patient_timeline(pool, clinic_id, patient_id, limit=50) → dict`

Aggregates in reverse chronological order:
- Approved `patient_history_*` entries (all 7 types) — labeled `source: approved_history`
- Unverified proposals from `patient_history_proposals` — labeled `source: unverified_proposal`
- Structuring runs from `patient_history_structuring_runs`
- Consent events from `consent_events`
- Intake submissions (submitted status) from `patient_intake_submissions`

Each item has:
- `event_type` (approved_history / unverified_proposal / structuring_run / consent_event / intake_submission)
- `occurred_at` (timestamp for chronological sort)
- `history_type` where applicable
- `production_phi_enabled: false`
- `synthetic_demo: true`

No raw answers. No transcript content. No diagnosis fields. No triage fields.
No medical advice fields. No clinical_confidence. No risk_score.

### 2. Delta view

Function: `get_patient_timeline_delta(pool, clinic_id, patient_id, since_appointment_date) → dict`

Returns only entries newer than `since_appointment_date`.
Useful for pre-visit summary: what changed since last appointment?

No diagnosis inference. No clinical summary generation. No LLM calls.
Purely structural: approved history entries added since the given date.

### 3. Backend routes

New file: `backend/app/api/routes/patient_timeline.py`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/clinics/{clinic_id}/patients/{patient_id}/timeline` | Full chronological timeline |
| GET | `/clinics/{clinic_id}/patients/{patient_id}/timeline/delta` | Delta since date (query param: since) |

All routes:
- Require `get_current_user` (authenticated session)
- Return `production_phi_enabled: false`
- No DELETE. No public routes.

### 4. Frontend timeline panel

New page: `frontend/app/developer-console/patient-timeline/page.tsx`

Dark admin console theme (INK=#0B132B, PANEL=#111C3D, ACCENT=#008080).

Features:
- Clinic ID + patient ID inputs
- "Load Timeline" button
- Chronological event list with event_type labels
- Approved history entries highlighted (green border or badge)
- Unverified proposals shown with "UNVERIFIED — pending staff review" label
- Delta view: "since date" input, "Load Delta" button
- extraction_confidence labeled "Extraction confidence only — not a medical judgment."
- Safety warning: no diagnosis, no medical advice, no PHI, production PHI NO-GO

Link from developer-console/page.tsx.

### 5. Tests

`backend/tests/test_longitudinal_timeline_delta_view_foundation.py` (new — ≥60 tests):
- Service: aggregates all 7 history types + proposals + runs + consent + submissions
- Service: delta view filters by date correctly
- Service: no diagnosis/advice/triage fields in output
- Service: no external LLM calls
- Service: production_phi_enabled=False in all items
- Routes: all require auth (401/403/503)
- Routes: no DELETE
- Routes: production_phi_enabled=False in responses
- Routes: no auto-approval, no diagnosis in route source
- Frontend page: exists, mentions patient timeline, delta view
- Frontend page: shows unverified label separately from approved
- Frontend page: extraction confidence labeled correctly
- Frontend page: no localStorage, no sessionStorage
- Frontend page: safety warning present
- Arch doc exists and covers key constraints

### 6. Docs

- `docs/architecture/LONGITUDINAL_TIMELINE_DELTA_VIEW_FOUNDATION.md` (new)
- `docs/claude/CURRENT_STATE.md` — Module 156 entry
- `docs/claude/NEXT_MODULE.md` — updated to Module 157

## Constraints

- No diagnosis. No medical advice. No triage scoring. No treatment recommendations.
- No external LLM calls. No Anthropic/OpenAI/Vapi API calls.
- Approved structured data only for clinical timeline items.
- Unverified proposals shown separately and clearly labeled.
- No raw patient answers surfaced in timeline output.
- production_phi_enabled always False.
- synthetic_demo always True.
- All routes require authenticated session.
- No DELETE route.
- No auto-approval or auto-merge in this module.
- Full test suite must remain green.
- Frontend build must remain clean.
- Commit message:
  Sprint 20 / Module 156 — Longitudinal timeline and delta view foundation
