# Patient Intake Link Flow Foundation

**Sprint 20 / Module 151 — 2026-07-08**

## Purpose

Demo-only tokenized consent-first patient intake questionnaire flow.
Admin generates a short-lived intake link. Patient follows the link, gives consent first,
answers an anamnesis template, and submits. Answers are stored as synthetic intake
submissions for staff review. No patient history writes. No AI structuring.

## Safety boundaries

- Demo tokens only — no live patient intake
- Raw token returned exactly once at link creation; never stored
- token_hash stored; raw token never persisted or logged
- token_prefix stored for admin identification only
- Consent step required before questionnaire renders
- No patient history writes in this module
- No AI structuring in this module
- No diagnosis. No medical advice. No treatment recommendations. No triage scoring
- `production_phi_enabled` always `False` — enforced by DB CHECK, service, and route layers
- `synthetic_demo` always `True` — enforced by DB CHECK
- No appointment confirmation promise
- No real patient data
- Synthetic/fake staging only
- Production PHI remains NO-GO

## Token flow

```
Admin creates link:
  generate_intake_token() → raw_token (urlsafe random 32 bytes)
  hash_intake_token(raw_token) → token_hash (SHA-256 hex)
  token_prefix(raw_token) → first 8 chars (admin display only)

  DB stores: token_hash, token_prefix
  Response returns: intake_url = /intake/{raw_token}   ← shown once only

Patient follows /intake/{raw_token}:
  Backend: SHA-256 hash raw_token → lookup by token_hash
  Validates: active, not expired, not revoked, not at max submissions

Patient submits:
  Backend: SHA-256 hash raw_token → validate link again
  Creates consent_event (channel=intake_link, granted=True)
  Stores patient_intake_submission with answers JSONB
  Escalation keywords matched (staff flag list, no scoring)
  Increments submission_count; marks submitted if max reached
  Does NOT write patient_history_* tables
  Does NOT call AI structuring
```

## Database tables

**`patient_intake_links`** (migration `0009_patient_intake_links`)

| Column | Notes |
|---|---|
| `token_hash` | SHA-256 of raw token. UNIQUE. Never expose raw token. |
| `token_prefix` | First 8 chars of raw token. Admin display only. |
| `status` | active → submitted / expired / revoked |
| `production_phi_enabled` | Always false (CHECK constraint) |
| `synthetic_demo` | Always true (CHECK constraint) |
| `expires_at` | Required, must be future on creation |
| `max_submissions` | Default 1 |
| `submission_count` | Incremented on each submission |

**`patient_intake_submissions`**

| Column | Notes |
|---|---|
| `consent_event_id` | NOT NULL — consent created on submission |
| `answers` | JSONB. Forbidden keys: diagnosis_score, risk_score, triage_score, medical_advice, etc. |
| `skipped_questions` | JSONB array of skipped question_keys |
| `escalation_matches` | JSONB array of staff flag keywords (no scoring) |
| `production_phi_enabled` | Always false |
| `synthetic_demo` | Always true |

## Escalation keyword matching

`_match_escalation_keywords(answers, keywords)` checks if each keyword (de/en)
appears in the combined answer text. Returns list of matched keyword strings.
Staff flag only — no triage score, no automated decision, no diagnosis.

## API routes

| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | `/clinics/{clinic_id}/patient-intake-links` | Required | Create link; returns intake_url once |
| GET | `/clinics/{clinic_id}/patient-intake-links` | Required | List clinic links |
| GET | `/clinics/{clinic_id}/patient-intake-submissions` | Required | List submissions |
| PATCH | `/patient-intake-links/{link_id}/revoke` | Required | Revoke link |
| GET | `/intake/{token}` | None | Public: load template by token |
| POST | `/intake/{token}/submit` | None | Public: submit answers |

No DELETE route. No raw token logging.

## Frontend (mobile-first)

**`/intake/[token]/page.tsx`**
- Loads template from `GET /intake/{token}`
- Consent step renders first — questionnaire blocked until consent checked
- Language selector: de / en / ar
- ar language selection applies `direction: 'rtl'`
- Supports all question types: text, textarea, yes_no, single_select, multi_select, date, number
- Required questions block submit; optional questions have skip checkbox
- Success: "Intake submitted for staff review." — no appointment confirmation
- Error states: expired/revoked link, invalid link, submit failure
- Demo notice: "Demo staging intake only. Do not enter real medical information."
- No localStorage. No sessionStorage. No diagnosis language.

**`/developer-console/intake-links/page.tsx`**
- Dark admin console theme
- Create intake link form (template_id, language, purpose, expires_in_hours, optional patient_id)
- Generated intake_url shown once after creation — not stored after page navigation
- Token prefix shown in list (not raw token)
- Revoke active links
- View submissions (escalation_matches count, language, status)
- Safety Boundary panel with explicit guardrails

## File map

| File | Role |
|---|---|
| `backend/migrations/versions/0009_patient_intake_links.py` | Migration |
| `backend/app/db/schema.sql` | Reference DDL |
| `backend/app/schemas/patient_intake_link.py` | Pydantic validators |
| `backend/app/services/intake_token.py` | Token generation and hashing |
| `backend/app/db/repositories/patient_intake_link_repo.py` | Async SQL repo |
| `backend/app/services/patient_intake_link.py` | Business logic |
| `backend/app/api/routes/patient_intake_links.py` | FastAPI routes |
| `frontend/app/intake/[token]/page.tsx` | Public mobile-first intake page |
| `frontend/app/developer-console/intake-links/page.tsx` | Admin link management |
| `frontend/lib/api.ts` | API helpers (admin + public) |
| `backend/tests/test_patient_intake_link_flow_foundation.py` | ≥60 tests |

## What remains after Module 151

- Live smoke evidence: deploy, run migration, create link, complete intake, verify submission
- AI structuring service: convert submitted intake answers to unverified history proposals
- Doctor review and merge UI: approve/reject proposals → patient_history entries
- Longitudinal timeline view
- Patient story pre-visit narrative (Module 155+)
- Arabic/RTL full foundation
- Gulf readiness architecture
- Production PHI unlock (hardening + legal review — future)
