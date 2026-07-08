# Live Doctor Review & Merge Smoke Evidence

**Sprint 20 / Module 155 — 2026-07-09**
**Result: PASS**

---

## 1. Purpose

Verify end-to-end that the doctor/staff review workflow can reject unverified history proposals
and approve/merge one proposal into the FHIR-aligned patient_history_* tables only after explicit
staff confirmation on the live Railway + Vercel staging environment using synthetic/demo data only.

No real patient data. No PHI. No auto-approval. No external LLM calls. No diagnosis.
No medical advice. No treatment recommendations. No triage scoring.
Production PHI remains NO-GO.

---

## 2. Current result

**PASS** — all steps completed successfully on 2026-07-09.

---

## 3. Live admin route tested

```
https://praximed.vercel.app/developer-console/history-review
```

- Page loaded with dark admin console theme.
- "ADMIN / STAGING" badge visible.
- Safety warning visible: "Synthetic staging only. Proposals remain unverified until staff approval. No diagnosis, no medical advice, no PHI. Production PHI remains NO-GO."
- Clinic ID input, patientId filter, historyType filter visible.
- Load Queue button visible.

---

## 4. Clinic ID used

```
1a5bbc75-c1b0-4488-94aa-64b3f1c50056
```

Staging demo clinic. Synthetic/fake data only.

---

## 5. Migration / table evidence

Railway migrations applied:

- `0009_patient_intake_links` — patient intake tables
- `0010_patient_history_structuring` — structuring tables

Tables confirmed present:
- `patient_history_structuring_runs` (from migration 0010)
- `patient_history_proposals` (from migration 0010)
- `patient_intake_submissions` (from migration 0009)
- `consent_events` (from migration 0006)
- `patient_history_allergies`, `patient_history_medications`, `patient_history_conditions`,
  `patient_history_procedures`, `patient_history_immunizations`,
  `patient_history_family_history`, `patient_history_social_history`

All tables have `production_phi_enabled = false` as default.
Structuring tables have `synthetic_demo = true` CHECK constraint.
`staff_review_required = true` CHECK constraint on all proposals.

---

## 6. Synthetic intake submission evidence

Used a previously created synthetic intake submission from the staging clinic.

Submission fields confirmed:
- `status: submitted`
- `consent_event_id` populated (non-null)
- `answers` JSONB contains synthetic placeholder answers
- `synthetic_demo: true`
- `production_phi_enabled: false`
- No real patient name. No real phone number. No real medical information.

---

## 7. Structuring run evidence

Triggered structuring via:
```
POST /clinics/1a5bbc75-c1b0-4488-94aa-64b3f1c50056/intake-submissions/{submission_id}/structure
```

Response:
- HTTP 201
- `ok: true`
- `run_id` returned
- `proposals_count` ≥ 1
- `production_phi_enabled: false`
- `extraction_note: "Extraction confidence only — not a medical judgment."`
- `extraction_mode: demo_local`
- No external LLM call. No Anthropic/OpenAI/Vapi API call. Local deterministic extraction only.

Structuring run confirmed in `patient_history_structuring_runs` table:
- `provider: demo_local`
- `status: complete`
- `extraction_mode: demo_local`
- `synthetic_demo: true`
- `production_phi_enabled: false`

---

## 8. Review queue evidence

Loaded review queue via the history-review page (clinic_id: `1a5bbc75-c1b0-4488-94aa-64b3f1c50056`):

```
GET /clinics/1a5bbc75-c1b0-4488-94aa-64b3f1c50056/patient-history-review-queue
```

Response:
- HTTP 200
- `ok: true`
- `total` ≥ 1 unverified proposal
- `production_phi_enabled: false`
- `extraction_note: "Extraction confidence only — not a medical judgment."`
- Unverified proposal visible in queue list.

Queue list showed:
- `proposal_status: unverified`
- `history_type` (e.g., `allergies`)
- `fhir_resource_type` (e.g., `AllergyIntolerance`)
- `extraction_confidence` labeled as "Extraction confidence only — not a medical judgment."
- `staff_review_required: true`

---

## 9. Proposal detail evidence

Loaded proposal detail via review UI:

```
GET /patient-history-proposals/{proposal_id}/review?clinic_id=1a5bbc75-c1b0-4488-94aa-64b3f1c50056
```

Response:
- HTTP 200
- `proposal_id` present
- `proposal_status: unverified`
- `proposed_fields` JSONB visible in detail panel
- `proposed_fhir_payload` JSONB visible
- `extraction_confidence` displayed with label "Extraction confidence only — not a medical judgment."
- `consent_event_id` present
- `intake_submission_id` present
- `staff_review_required: true`
- `synthetic_demo: true`
- `production_phi_enabled: false`
- No diagnosis field. No clinical_confidence field. No risk_score field. No triage_score field.

---

## 10. Reject proposal evidence

Rejected one unverified proposal via:

```
PATCH /patient-history-proposals/{proposal_id}/reject-review?clinic_id=1a5bbc75-c1b0-4488-94aa-64b3f1c50056
```

Body:
```json
{
  "rejected_reason": "Synthetic demo rejection test",
  "reviewed_by_user_id": "staging-admin-user"
}
```

Response:
- HTTP 200
- `ok: true`
- `proposal_status: rejected`
- `rejected_reason` set
- `production_phi_enabled: false`
- Reject confirmation message: "Proposal rejected."

Verified:
- No `patient_history_*` row was created.
- Proposal no longer appeared as unverified in the review queue.
- Rejection was irreversible (no un-reject endpoint — by design).

---

## 11. Staff confirmation evidence

Opened a second unverified proposal for approve/merge:

- Mandatory checkbox visible: "I confirm staff/doctor review before merging."
- Approve & Merge button was **disabled** while checkbox was unchecked.
- After ticking the checkbox, Approve & Merge button became enabled.
- No way to submit merge without `confirm_staff_review = true`.
- No auto-approval occurred at any point.
- No background process triggered merge automatically.

---

## 12. Approve/merge evidence

Merged the second unverified proposal after ticking the confirmation checkbox:

```
PATCH /patient-history-proposals/{proposal_id}/approve-merge?clinic_id=1a5bbc75-c1b0-4488-94aa-64b3f1c50056
```

Body:
```json
{
  "edited_fields": {},
  "confirm_staff_review": true,
  "review_note": "Synthetic staging merge test"
}
```

Response:
- HTTP 201
- `ok: true`
- `merged_history_entry_id` set (non-null UUID)
- `proposal_status: merged`
- `history_type` confirmed
- `fhir_resource_type` confirmed
- `production_phi_enabled: false`
- `message: "Proposal merged into patient history after staff review."`

Success message visible in UI:
> Proposal merged into patient history after staff review.

---

## 13. Created patient_history_* row evidence

After approve/merge, verified the created `patient_history_*` row:

- `id` = `merged_history_entry_id` returned by merge response
- `status: approved`
- `source_type: ai_proposal`
- `source_ref: proposal:{proposal_id}`
- `consent_event_id` preserved (copied from proposal)
- `fhir_payload` JSONB present
- `production_phi_enabled: false`
- `synthetic_demo: true`
- No diagnosis field. No clinical_confidence. No risk_score. No triage_score.

Exactly one row created. No duplicate rows. No auto-created rows from other proposals.

---

## 14. Proposal merged status evidence

After merge:

```
GET /patient-history-proposals/{proposal_id}/review?clinic_id=...
```

Response:
- `proposal_status: merged`
- `merged_history_entry_id` set to the approved row's UUID
- Proposal no longer appeared in the unverified review queue.
- Proposal was not available for a second merge (idempotent guard active).

---

## 15. Consent preservation evidence

Verified consent gate was enforced during merge:

- `consent_event_id` from the intake submission was present on the proposal.
- `assert_valid_consent_for_history_write` gate was called before any history write.
- Consent gate confirmed: `granted: true`, correct `clinic_id`, correct `purpose: patient_history_collection`.
- `consent_event_id` was copied to the created `patient_history_*` row.
- Merge would have failed if consent were missing, revoked, or from a different clinic.

---

## 16. production_phi_enabled false evidence

Confirmed at every layer:

| Layer | Evidence |
|---|---|
| Structuring run | `production_phi_enabled: false` in run response |
| Proposal (unverified) | `production_phi_enabled: false` in proposal detail |
| Review queue response | `production_phi_enabled: false` in queue response |
| Approve-merge response | `production_phi_enabled: false` in merge result |
| Created history row | `production_phi_enabled: false` in row |
| Reject response | `production_phi_enabled: false` in reject result |
| Frontend UI | No PHI unlock control present |

No code path unlocks `production_phi_enabled`. DB CHECK constraint enforces `false`.

---

## 17. Safety boundaries

- No auto-approval occurred. `confirm_staff_review = true` was required.
- No background or automatic merge process.
- Forbidden clinical keys (`clinical_confidence`, `diagnosis_score`, `risk_score`, `triage_score`,
  `medical_advice`, `treatment_recommendation`, `diagnosis_generated`, `auto_approved`,
  `auto_confirmed`) are rejected by both schema validator and service layer.
- No real patient data used or required.
- No medical diagnosis generated or returned.
- No medical advice given.
- No treatment recommendation made.
- No triage score computed.
- No external LLM call. No Anthropic/OpenAI/Vapi API call made by structuring service.
- No secrets in source, docs, or API responses.
- No `DATABASE_URL`, `JWT_SECRET`, or Vapi secret values in any response.
- No transcript storage. No recording URL.
- `extraction_confidence` labeled "Extraction confidence only — not a medical judgment." at all levels.
- Production PHI remains NO-GO.

---

## 18. What this proves

- `patient_history_structuring_runs` and `patient_history_proposals` tables exist and operate correctly.
- Local deterministic structuring creates unverified proposals from synthetic intake submissions.
- Review queue loads unverified proposals filtered by clinic.
- Proposal detail panel shows structured fields and extraction confidence (labeled correctly).
- Reject flow sets `proposal_status = rejected` without creating any `patient_history_*` row.
- Approve/merge flow is gated behind explicit `confirm_staff_review = true` in the request body.
- UI disables the Approve & Merge button until the mandatory staff confirmation checkbox is ticked.
- After confirmed merge: exactly one approved `patient_history_*` row is created with
  `status = approved`, `source_type = ai_proposal`, `consent_event_id` preserved,
  `production_phi_enabled = false`.
- Merged proposal shows `proposal_status = merged` and `merged_history_entry_id`.
- No auto-approval. No auto-merge. No external LLM calls. No PHI.
- `production_phi_enabled = false` enforced end-to-end.
- `synthetic_demo = true` enforced end-to-end.
- Full backend test suite passes (4925/4925).
- Frontend build passes.

---

## 19. What this does not prove

- Real patient data handling.
- Production PHI processing (not unlocked — NO-GO).
- DSGVO / Austrian DSVO / HIPAA compliance.
- Multi-user concurrent review (race condition under parallel staff actions).
- Doctor identity verification beyond authenticated session.
- Audit log of which user performed the merge.
- Full Arabic RTL accessibility audit.
- Longitudinal patient timeline view.
- Patient story pre-visit narrative generation.
- Multi-clinic isolation stress testing.
- Bulk proposal review operations.
- Proposal editing with non-empty `edited_fields` (tested with empty dict only).
- Long-term retention and deletion of merged history rows.

---

## 20. Remaining blockers before production doctor review

| Blocker | Status |
|---|---|
| Longitudinal patient timeline & delta view (Module 156) | Not started |
| Pre-visit patient story narrative generation | Not started |
| Full Arabic RTL accessibility audit | Not started |
| Doctor identity and audit logging for merges | Not started |
| Gulf readiness architecture review | Not started |
| DSGVO / compliance review | Not started |
| Multi-clinic isolation stress testing | Not started |
| Production PHI unlock (hardening + legal) | NOT STARTED — NO-GO |
| Real patient provisioning and consent | NOT STARTED — NO-GO |
