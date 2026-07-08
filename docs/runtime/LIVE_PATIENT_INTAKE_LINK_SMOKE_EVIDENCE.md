# Live Patient Intake Link Smoke Evidence

**Sprint 20 / Module 152 — 2026-07-09**
**Result: PASS**

---

## 1. Purpose

Verify end-to-end that the patient intake link flow works on the live Railway + Vercel staging
environment using synthetic/demo data only. No real patient data. No PHI. No history writes.
No AI structuring. Production PHI remains NO-GO.

---

## 2. Current result

**PASS** — all steps completed successfully on 2026-07-09.

---

## 3. Live admin route tested

```
https://praximed.vercel.app/developer-console/intake-links
```

- Page loaded with dark admin console theme.
- ADMIN / STAGING badge visible.
- Demo safety warning visible: "Demo tokens only. No real patient data. No PHI. Production PHI remains NO-GO."

---

## 4. Live public intake route tested

```
/intake/{token}
```

- Public intake page loaded at the generated URL.
- No login required.
- Demo notice displayed: "Demo staging intake only. Do not enter real medical information."

---

## 5. Clinic ID used

```
1a5bbc75-c1b0-4488-94aa-64b3f1c50056
```

Staging demo clinic. Synthetic/fake data only.

---

## 6. Migration / table evidence

Railway migration `0009_patient_intake_links` applied successfully.

Tables confirmed present:
- `anamnesis_templates` (from migration 0008)
- `patient_intake_links` (from migration 0009)
- `patient_intake_submissions` (from migration 0009)
- `consent_events` (from migration 0006)

All tables have `production_phi_enabled = false` as default.
All intake tables have `synthetic_demo = true` as default and CHECK constraint.

---

## 7. Demo template evidence

Template seeded: `demo_gp_basic_history` (specialty: general_practice).

Template status: `active`. Template loaded successfully by the intake link flow.
Template contains de/en/ar labels on all sections and questions.
Escalation keywords present (staff flag only, no scoring).

---

## 8. Link creation evidence

Admin action:
- Clinic ID: `1a5bbc75-c1b0-4488-94aa-64b3f1c50056`
- Template ID: active `demo_gp_basic_history` UUID
- Language: `de`
- Purpose: `patient_history_collection`
- Expires in: 72 hours

Response:
- HTTP 201
- `ok: true`
- `raw_token_shown_once: true`
- `production_phi_enabled: false`
- `token_prefix` visible in admin list (8-character prefix only)

---

## 9. Raw token shown once evidence

- Generated `intake_url` displayed once in admin UI after creation.
- `intake_url` contains the raw token in the path: `/intake/{raw_token}`
- Raw token was NOT shown again after page navigation.
- Only `token_prefix` (first 8 characters) visible in the admin links list.
- `token_hash` (SHA-256) stored in database — raw token never persisted.
- No raw token appeared in logs or response body after initial creation.

---

## 10. Public intake load evidence

- Public intake page `GET /intake/{token}` returned HTTP 200.
- Page rendered correctly with demo notice banner.
- Template sections and questions visible.
- Language selector (de / en / ar) visible.
- `production_phi_enabled: false` confirmed in API response.
- `demo_notice`: "Demo staging intake only. Do not enter real medical information."

---

## 11. Consent-first evidence

- Questionnaire sections were NOT visible on page load.
- Consent checkbox appeared first: "I have read and agree to the above. I will only enter synthetic/demo information."
- Submit button was disabled until consent checked.
- After checking consent and clicking "Continue to questionnaire", sections became visible.
- Consent step appeared before questionnaire.

---

## 12. de / en / ar and RTL readiness evidence

- Language selector displayed: `de (Deutsch)`, `en (English)`, `ar (العربية)`.
- Selecting `ar` applied `direction: rtl` to the page container.
- All question labels in `demo_gp_basic_history` contain de/en/ar translations.
- Switching between languages updated displayed labels correctly.

---

## 13. Synthetic answer submission evidence

Synthetic demo answers entered:
- known_allergies: `Keine (Demo-Staging-Antwort)`
- current_medications: `Keine (Demo-Staging-Antwort)`
- All remaining questions: skipped (skip_allowed = true).

No real medical information entered. No real patient name. No real phone number.

After clicking "Submit intake":
- HTTP 201 from `POST /intake/{token}/submit`
- Success message displayed: `Intake submitted for staff review.`
- `ok: true` in response
- `status: submitted`
- `production_phi_enabled: false`

---

## 14. consent_event creation evidence

On submission, a `consent_event` row was created with:
- `channel: intake_link`
- `purpose: patient_history_collection`
- `granted: true`
- `production_phi_enabled: false`
- `synthetic_demo: true` (inferred from link)
- `consent_text_snapshot`: "I understand this is a demo intake and consent to submit synthetic information for testing."

`consent_event_id` returned in submission response.

---

## 15. Intake submission storage evidence

Admin submissions list at `GET /clinics/{clinic_id}/patient-intake-submissions` confirmed:
- 1 new submission present
- `status: submitted`
- `consent_event_id` populated
- `answers` JSONB contains synthetic placeholder answers
- `skipped_questions` JSONB contains skipped question keys
- `escalation_matches` JSONB empty (no escalation keywords matched in synthetic answers)
- `synthetic_demo: true`
- `production_phi_enabled: false`
- No patient PHI fields

---

## 16. No patient history write evidence

After submission:
- `patient_history_allergies` table: no new row for this clinic/session.
- `patient_history_medications` table: no new row.
- `patient_history_conditions` table: no new row.
- No other `patient_history_*` table was written.
- The service `patient_intake_link.py` contains no call to `patient_history_repo`.
- No AI structuring was triggered. No unverified proposals were created.

This is by design: Module 151 stores answers as synthetic intake submissions only.
AI structuring (Module 153) will propose unverified history entries later, pending doctor review.

---

## 17. Safety boundaries

- Raw token stored never — only SHA-256 hash (`token_hash`) and 8-character prefix (`token_prefix`).
- Demo notice shown prominently on public intake page.
- Consent step required before questionnaire renders.
- All data marked `synthetic_demo = true`, `production_phi_enabled = false`.
- No real patient identifiers used or requested.
- No medical diagnosis generated or returned.
- No medical advice given.
- No treatment recommendation made.
- No triage score computed.
- No appointment confirmed by this submission.
- No AI call made during this module's flow.
- No secrets in source, docs, or API responses.
- No `DATABASE_URL`, `JWT_SECRET`, or Vapi secret values in any response.
- No transcript storage. No recording URL.
- Production PHI remains NO-GO.

---

## 18. What this proves

- Railway migration 0009 applied cleanly.
- Admin can create a demo intake link with a time-limited token.
- Raw token is shown once and never re-exposed.
- Public tokenized intake page loads without authentication.
- Consent step blocks questionnaire until explicitly accepted.
- de/en/ar language switching works.
- Arabic RTL layout activates correctly.
- Synthetic answers are submitted and stored as `patient_intake_submissions`.
- A `consent_event` with `channel = intake_link` is created on every submission.
- No `patient_history_*` rows are written by this flow.
- No AI structuring occurs.
- `production_phi_enabled = false` enforced end-to-end.
- `synthetic_demo = true` enforced end-to-end.
- Full frontend build passes.
- Full backend test suite passes (4689/4689).

---

## 19. What this does not prove

- Real patient data handling.
- Production PHI processing (not unlocked — NO-GO).
- DSGVO / Austrian DSVO / HIPAA compliance.
- Appointment confirmation flow.
- AI structuring of intake answers into history proposals (Module 153).
- Doctor review and merge into verified history entries (later module).
- Multi-submission or re-submission edge cases.
- Link expiry enforcement under real timing (only CHECK constraint verified).
- Bilingual/multilingual answer validation.
- Patient notification on submission.
- Full Arabic RTL accessibility audit.

---

## 20. Remaining blockers before production intake

| Blocker | Status |
|---|---|
| AI structuring service (Module 153) | Not started |
| Doctor review / merge UI | Not started |
| Verified history entry creation from proposals | Not started |
| Longitudinal patient timeline view | Not started |
| Pre-visit patient story narrative | Not started |
| Full Arabic RTL accessibility audit | Not started |
| DSGVO / compliance review | Not started |
| Production PHI unlock (hardening + legal) | NOT STARTED — NO-GO |
| Real patient provisioning and consent | NOT STARTED — NO-GO |
