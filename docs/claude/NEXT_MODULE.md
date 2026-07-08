# Sprint 20 / Module 153 — AI Structuring Service Foundation

Status: pending implementation.

## Context

Module 152 complete (smoke evidence):
- Live intake link flow verified end-to-end on staging.
- patient_intake_submissions stores synthetic answers as-is.
- consent_event created with channel=intake_link.
- No patient_history_* writes occurred.
- No AI structuring triggered yet.
- Production PHI remains NO-GO.

Sprint 20 intake foundation is now complete:
- Consent ledger (Module 148)
- Patient history data model (Module 149)
- Anamnesis template engine (Module 150)
- Patient intake link flow (Module 151)
- Live intake smoke evidence (Module 152)

The next step is to transform synthetic intake submission answers into proposed
unverified patient history entries for doctor review. No approval without staff/doctor review.
No diagnosis. No medical advice. No treatment recommendations. No triage scoring.

## Goal

Create the AI structuring service foundation. It reads a `patient_intake_submission`,
sends free-text answers to an LLM (Claude) with a strictly scoped prompt, and produces
proposed unverified `patient_history_*` entries for one or more FHIR history types.
All proposals remain `status = unverified` until a doctor explicitly approves them.

No automatic approval. No diagnosis generation. No medical advice. No triage.
Confidence is extraction confidence only — never clinical confidence.
Logs are pseudonymized. Synthetic/fake staging only. Production PHI remains NO-GO.

## What Module 153 must implement

### 1. AI structuring prompt design

`backend/app/services/ai_structuring/prompts.py` (new):

- System prompt: defines the task as structured data extraction only.
- Explicitly forbids: diagnosis, medical advice, treatment recommendations, triage scoring.
- Output format: JSON array of proposed history entries per FHIR type.
- Confidence field: extraction_confidence (0.0–1.0) — how well the free text maps to a FHIR field.
  NOT clinical confidence, NOT diagnosis probability.
- Language: handles de/en/ar input, returns structured output in English FHIR fields.
- Pseudonymization instruction: do not echo back patient names or identifiers.

Proposal schema per item:
```json
{
  "history_type": "allergies | medications | conditions | ...",
  "proposed_text": "...",
  "extraction_confidence": 0.85,
  "source_question_key": "...",
  "source_answer_text": "..."
}
```

### 2. AI structuring service

`backend/app/services/ai_structuring/structuring_service.py` (new):

Functions:
- `structure_intake_submission(pool, submission_id, clinic_id, actor_user=None)`
  - Load submission by ID and clinic_id
  - Load linked anamnesis template for question metadata
  - For each question with history_target != "none" that has an answer:
    - Collect (question_key, history_target, answer_text, question_label)
  - Build prompt with collected pairs
  - Call Claude API with structured extraction prompt
  - Parse response JSON into proposal list
  - Validate each proposal:
    - history_type must be in FHIR history type set
    - proposed_text must not be empty
    - extraction_confidence must be 0.0–1.0
    - reject if proposed_text contains diagnosis/advice/treatment language
  - For each valid proposal, create a patient_history_* entry with status=unverified
    and source_type=ai_proposal
  - Return list of created entry IDs
  - Log: pseudonymized (no patient name, no raw answer text in logs)

Guards:
- No automatic approval
- No diagnosis field
- No medical advice field
- No treatment recommendation field
- No triage score
- All created entries must be status=unverified
- All created entries must have production_phi_enabled=false
- If Claude API is unavailable, fail gracefully and return empty proposals

### 3. Claude API integration

`backend/app/services/ai_structuring/claude_client.py` (new):

- Use Anthropic Python SDK (`anthropic` package)
- Model: claude-haiku-4-5-20251001 (fast, cost-effective for extraction)
- API key from environment variable `ANTHROPIC_API_KEY` (never hardcoded)
- max_tokens: 1024 for extraction tasks
- temperature: 0 (deterministic extraction)
- No streaming
- Timeout guard: 30 seconds
- Return raw response text for parsing
- Never log raw answer content (pseudonymize)

### 4. Protected service trigger route

`backend/app/api/routes/ai_structuring.py` (new):

- POST /clinics/{clinic_id}/intake-submissions/{submission_id}/structure
  - Auth required (admin/staff session)
  - Triggers structuring service
  - Returns: list of created unverified history entry IDs
  - 404 if submission not found or wrong clinic
  - 422 if submission already structured
  - production_phi_enabled always false

No public access. No automatic trigger. Staff/doctor must initiate.
No DELETE. No approval route in this module (approval is a later module).

Add router include in backend/app/api/router.py.

### 5. Database change (if needed)

Consider adding `structured_at TIMESTAMPTZ` and `structure_status TEXT` columns to
`patient_intake_submissions` to track whether structuring has been attempted.

If adding columns: new migration `0010_intake_submission_structuring_status.py`.

Alternative: track via patient_history entries (source_type=ai_proposal, linked submission ID).

Choose the simpler approach and document the decision.

### 6. Tests

`backend/tests/test_ai_structuring_service_foundation.py` (new — ≥60 tests):

- Prompt safety: no diagnosis field, no medical_advice field, no triage_score, no treatment
- Prompt language: extraction_confidence labeled as extraction only, not clinical
- Prompt coverage: history_type mapped from history_target, all 7 FHIR types covered
- Claude client: API key from env var only, never hardcoded, timeout guard present
- Service: structure_intake_submission calls Claude client, creates unverified history entries
- Service: all created entries have status=unverified and source_type=ai_proposal
- Service: empty answer → no proposal created for that question
- Service: history_target=none skips question
- Service: invalid history_type in response → rejected proposal
- Service: invalid extraction_confidence (>1.0 or <0.0) → rejected
- Service: graceful failure if Claude API unavailable
- Routes: POST trigger requires auth
- Routes: 404 for wrong clinic or missing submission
- Routes: production_phi_enabled=false in response
- Forbidden: no auto-approval, no diagnosis generation, no medical advice, no triage scoring
- Logs: no raw patient answer text in log statements

### 7. Architecture doc

`docs/architecture/AI_STRUCTURING_SERVICE_FOUNDATION.md` (new)

### 8. Docs

- `docs/claude/CURRENT_STATE.md` — Module 153 entry
- `docs/claude/NEXT_MODULE.md` — updated to Module 154

## Constraints

- ANTHROPIC_API_KEY from environment variable only — never hardcoded, never logged
- extraction_confidence ≠ clinical confidence — must be clearly labeled
- All structuring results = status unverified
- No automatic approval — staff/doctor review required
- No diagnosis. No medical advice. No triage. No treatment recommendation.
- Logs must be pseudonymized — no raw answer text, no patient name
- Synthetic/fake staging only
- production_phi_enabled always False
- Production PHI remains NO-GO
- Full test suite must remain green
- Commit message:
  Sprint 20 / Module 153 — AI structuring service foundation
