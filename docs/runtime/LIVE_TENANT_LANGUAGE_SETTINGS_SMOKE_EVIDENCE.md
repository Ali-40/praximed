# PraxisMed — Live Tenant Language Settings Smoke Evidence

**Sprint 19 / Module 140**
**Date:** 2026-07-06
**Commit tested:** 1cf85f0

---

## 1. Purpose

Verify that the admin language settings UI (Module 139) works end-to-end against
the live staging backend: loading German-first defaults for a provisioned clinic
and persisting a PATCH update through a full reload cycle.

No PHI. No secrets. No Vapi credentials. Production PHI remains NO-GO.

---

## 2. Current Result

**PASS**

All evidence steps completed successfully on staging.

---

## 3. Live Route Tested

```
https://praximed.vercel.app/developer-console/language-settings
```

Backend endpoints exercised:

```
GET  /clinics/{clinic_id}/language-settings
PATCH /clinics/{clinic_id}/language-settings
```

---

## 4. Clinic ID Used

```
1a5bbc75-c1b0-4488-94aa-64b3f1c50056
```

Staging fake clinic — Demo Wahlarzt Praxis Wien. Provisioned in Module 137.
No real patient records. No PHI. No production activation.

---

## 5. Load Settings Evidence

- Opened `/developer-console/language-settings` with admin session active.
- Entered clinic_id: `1a5bbc75-c1b0-4488-94aa-64b3f1c50056`.
- Clicked "Load settings".
- GET `/clinics/1a5bbc75-c1b0-4488-94aa-64b3f1c50056/language-settings` responded
  HTTP 200 with language settings JSON.
- Form populated successfully. `updated_at` displayed.

---

## 6. German-First Defaults Evidence

After loading, the following German-first defaults were visible in the form:

| Field | Value |
|---|---|
| `primary_language` | `de` |
| `fallback_language` | `en` |
| `supported_languages` | `de`, `en` (both checked) |
| `default_patient_language` | `de` |
| `vapi_assistant_language_mode` | `german_first` |
| `clinic_ui_language` | `de` |

Label "German-first is recommended for Austrian Wahlärzte." visible on the page.

---

## 7. English Fallback Evidence

- `fallback_language` field displayed `en` (English).
- English fallback is the correct default for German-first Austrian clinics.
- "English" checkbox was visible and checked in `supported_languages`.

---

## 8. PATCH / Update Evidence

- Changed `vapi_assistant_language_mode` from `german_first` to `bilingual_auto`.
- Clicked "Save language settings".
- PATCH `/clinics/1a5bbc75-c1b0-4488-94aa-64b3f1c50056/language-settings` sent
  with body `{"vapi_assistant_language_mode": "bilingual_auto"}`.
- HTTP 200 response received.
- "Language settings saved" confirmation message displayed.

---

## 9. Reload / Persistence Evidence

- Reloaded the page and entered the same clinic_id.
- Clicked "Load settings" again.
- GET response confirmed `vapi_assistant_language_mode` was now `bilingual_auto`.
- Update persisted end-to-end through the backend.
- Changed `vapi_assistant_language_mode` back to `german_first` and saved.
- Second reload confirmed `german_first` restored.

---

## 10. Safety Boundaries

| Boundary | Status |
|---|---|
| No PHI entered or displayed | CONFIRMED |
| No Vapi credentials entered or stored | CONFIRMED |
| No sessionStorage used | CONFIRMED |
| No localStorage used | CONFIRMED |
| production_phi_enabled remained false | CONFIRMED |
| No production activation | CONFIRMED |
| credentials: 'include' session auth | CONFIRMED |
| Admin session required (401 if unauthenticated) | CONFIRMED by design |
| No secrets entered into UI | CONFIRMED |

---

## 11. What This Proves

- GET `/clinics/{clinic_id}/language-settings` returns correct German-first defaults
  for a provisioned staging clinic.
- English fallback is visible and correct.
- PATCH `/clinics/{clinic_id}/language-settings` persists partial updates to the
  backend (clinics.locale + language_config JSON file).
- Admin UI round-trip (load → update → reload → confirm) works end-to-end on staging.
- `credentials: 'include'` session auth works for both the GET and PATCH endpoints.
- `bilingual_auto` is a valid accepted vapi_assistant_language_mode value.
- German-first can be restored after a change (idempotent round-trip).
- "Language settings saved" confirmation is displayed on successful PATCH.
- reload confirmed update persisted.

---

## 12. What This Does Not Prove

- Production readiness.
- DSGVO / Austrian data protection compliance.
- Vapi assistant binding (language mode controls config intent, not live Vapi wiring).
- Security hardening (C3–C8 blockers remain open).
- Bilingual assistant audio testing.
- Multi-tenant isolation of language settings under concurrent updates.

---

## 13. Remaining Blockers

| Blocker | Status |
|---|---|
| C3 — Secrets hardening | Open |
| C4 — PHI logging/redaction hardening | Open |
| C5 — Tenant isolation verification | Open |
| C6 — Audit trail hardening | Open |
| C7 — Backup/restore runbook | Open |
| C8 — Legal / DSGVO review | Open |
| Vapi assistant config binding (Module 141) | Next |
| Bilingual assistant testing | Pending |

Production PHI remains NO-GO until C3–C8 hardening blockers are resolved.
