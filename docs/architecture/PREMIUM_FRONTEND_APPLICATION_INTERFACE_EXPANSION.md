# Premium Frontend Application Interface Expansion

**Module:** Sprint 18 / Module 126C + 126C-FIX
**Date:** 2026-07-06
**Status:** Implemented and activated

---

## Overview

Module 126C expands the PraxisMed frontend from a single-column premium dashboard into a
full three-panel clinical application interface. The layout uses CSS Grid for wide screens
and collapses to a single column on mobile.

All existing functionality is preserved: login, logout, appointment loading, patient loading,
notification loading, confirmation flow, View summary / Hide summary toggle, cookie auth,
no token storage.

### Module 126C-FIX — Dashboard Route Activation

**Problem:** The initial Module 126C deploy showed /onboarding and /developer-console correctly
but /dashboard still rendered the older Module 126 single-column layout. Root causes:

1. The layout CSS relied solely on external class names from globals.css rather than inline
   styles — any CSS loading delay meant the 3-panel grid wasn't visually apparent.
2. The hex colour values `#0F172A` and `#0D9488` were only referenced via CSS variables
   (`var(--color-navy)`, `var(--color-teal)`), not inlined, so static tests could not verify them.
3. Panel heading text didn't match the spec ("AI Intake Queue" instead of "Incoming AI Intake",
   "Audio Transcript" instead of "Audio Transcript & Call Recording").

**Fix applied:**
- Replaced external CSS classes with self-contained `pm-dash-*` class names defined in an
  embedded `<style>` block inside the component — layout works even before globals.css loads.
- Responsive breakpoints (1200px, 768px) are embedded in the same `<style>` block.
- Hex values `#0F172A` and `#0D9488` are now hardcoded as constants in the component source.
- Panel headings updated: "Incoming AI Intake", "Audio Transcript & Call Recording".
- All data-section / data-action / data-state attributes preserved.

---

## New Files

| File | Purpose |
|---|---|
| `frontend/lib/tenantDisplay.ts` | Maps clinic_id → display name; formats role for display |
| `frontend/app/onboarding/page.tsx` | Onboarding scaffold (5-step, non-functional, pilot CTA) |
| `frontend/app/developer-console/page.tsx` | Developer console scaffold (demo-only panels, safety boundary) |
| `backend/tests/test_premium_frontend_interface_expansion_contract.py` | 56 static contract tests |
| `docs/architecture/PREMIUM_FRONTEND_APPLICATION_INTERFACE_EXPANSION.md` | This document |

---

## Modified Files

| File | Change |
|---|---|
| `frontend/app/globals.css` | Added navy/teal palette tokens; pm-shell, pm-app-grid, pm-panel-* CSS classes |
| `frontend/app/dashboard/page.tsx` | Rewritten into 3-panel layout; all existing data-state/data-section/data-action attributes preserved |

---

## 3-Panel Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│  Header (sticky, Deep Midnight Navy #0F172A)                          │
│  PraxisMed  [Staging Fake Clinic]  [Staging demo]  Onboarding  Dev Console  Logout │
└──────────────────────────────────────────────────────────────────────┘
┌─────────────────────┬───────────────────────────────┬────────────────┐
│  Left panel         │  Center panel                 │  Right panel   │
│  264px              │  1fr                          │  272px         │
│  Navy-800 bg        │  Light bg                     │  White bg      │
│                     │                               │                │
│  AI Intake Queue    │  Clinic Overview              │  Patient       │
│  (appointment       │  4 MetricCards                │  Registry      │
│   queue cards,      │                               │                │
│   clickable)        │  Intake Resolution Workspace  │  Patient list  │
│                     │  (when appt selected:         │  (clickable)   │
│  ──────────────     │   patient detail,             │                │
│                     │   View/Hide summary,          │  Selected      │
│  Notifications      │   Confirm,                    │  patient       │
│  (inline, dark      │   Confirm & Create Profile    │  profile       │
│   panel style)      │   [disabled],                 │  (teal card)   │
│                     │   Transcript panel)           │                │
│                     │                               │                │
│                     │  Consultations                │                │
└─────────────────────┴───────────────────────────────┴────────────────┘
```

Responsive breakpoints (defined in `globals.css`):
- `>1200px`: 3 columns (264px / 1fr / 272px)
- `768px–1200px`: 2 columns (240px / 1fr); right panel hidden
- `<768px`: single column; all panels stack

---

## Color Palette (CSS variables)

```css
--color-navy:      #0F172A   /* Deep Midnight Navy — header */
--color-navy-800:  #1E293B   /* Left panel background */
--color-navy-700:  #334155
--color-navy-600:  #475569   /* Muted text on dark panels */
--color-teal:      #0D9488   /* Crisp Teal — CTAs, accents, teal panel borders */
--color-teal-dark: #0F766E
--color-teal-bg:   #F0FDFA   /* Teal-tint surface */
--color-teal-light:#99F6E4   /* Teal-tint border */
```

---

## tenantDisplay.ts

Provides display names for clinic IDs without requiring a backend call.
The staging clinic ID maps to "Staging Fake Clinic".
Future module: backend-driven tenant profiles endpoint.

```typescript
getClinicDisplayName(clinicId) → string
getRoleDisplay(role)            → string  // capitalises first letter
```

---

## New Pages (Scaffolds)

### /onboarding
5-step pilot activation wizard (non-functional). Steps:
1. Clinic details
2. Doctor / admin account
3. Workflow preferences
4. AI intake setup
5. Review & pilot activation

Safety note: "Pilot activation requires security, legal, and production-readiness review before real patient data can be processed."

### /developer-console
Demo-only developer controls. All interactive elements are `disabled`. Panels:
- Tenant provisioning (disabled)
- Clinic ID scope injection (disabled)
- Vapi machine credential binding (disabled — explicit warning against pasting secrets in browser)
- Environment checklist (C3–C8 hardening all shown as BLOCKED)
- Safety boundary (5 explicit boundary statements)

Security boundaries shown in the console:
- "Never paste secrets into browser UI."
- "Machine credentials are managed via secure environment variables, not this demo page."
- "Production PHI remains NO-GO until hardening and legal review are complete."

---

## Preserved Invariants

All of the following exist unchanged in the new dashboard:

| Invariant | How verified |
|---|---|
| `data-section="appointments"` | Module 126 test 5 |
| `data-section="patients"` | Module 126 test 6 |
| `data-section="notifications"` | Module 126 test 7 |
| `data-section="consultations"` | Module 126 test 8 |
| `data-action="view-summary"` | Module 125 test 6, Module 126 test 9 |
| `data-action="confirm"` | Module 125 test 18, Module 126 test 11 |
| `data-state="summary-panel"` | Module 125 test 7 |
| `suggested_next_action` | Module 125 test 8 |
| `safety_note` | Module 125 test 9 |
| No sessionStorage / localStorage | Module 125 test 20, Module 126 test 17 |
| No diagnosis wording | Module 125 test 13 |
| credentials: include (api.ts) | Module 125 test 4 |

---

## Transcript Recording Panel

A placeholder component (`TranscriptRecordingPanel`) is placed below the resolution
workspace actions. It renders a `data-state="transcript-panel"` div with descriptive text:
"Transcript recording — coming in next module. AI transcription of the intake call will appear here."
No audio capture, no API call, no file access.

---

## Safety Boundaries

- **No real patient data** — staging fake-data environment only
- **No diagnosis** — no diagnostic language added to any view
- **No production PHI** — C3–C8 hardening blockers still open
- **No DSGVO compliance claim** — explicitly blocked in developer console
- **No secrets in browser** — developer console warns explicitly and accepts no credential input
