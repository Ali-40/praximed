# Fabel 5 Premium Clinic Interface Overhaul

Sprint 18 / Module 126C-FABEL5 — Premium Austrian Clinic Interface Overhaul.

## Purpose

Transform the PraxisMed frontend from a basic staging prototype into a premium,
high-density, authoritative, doctor-facing medical platform designed for
Austrian private clinics / Wahlärzte. Scope is frontend UI/UX, static frontend
contract tests, and docs only. No backend runtime changes, no migrations, no
real patient data, no secrets, no external delivery, and no production PHI.
Production readiness remains **NO-GO**.

## Result

The old low-density overview-table dashboard on `/dashboard` was replaced with
a premium 3-column split-screen clinical workspace. The onboarding page gained
a gated access entry module and the escaped-entity rendering bug was fixed. The
developer console received an explicit dense dark-mode command theme that is
visually segregated from the clinical UI. All existing data behavior, API
contracts, and test selectors were preserved.

## Visual identity palette

High-contrast, clean clinical identity, declared in `frontend/app/globals.css`
tokens and mirrored as constants in page components:

| Token | Hex | Use |
|---|---|---|
| Primary Structural Ink | `#0B132B` | Sidebar background, strong headers, developer console background, high-importance typography |
| Clinical Accent | `#008080` | Primary CTAs — Confirm, Create Profile, Confirm Appointment & Create Patient Profile |
| Highlight Muted Fill | `#E0F2F1` | Active queue items, selected states, soft teal surfaces |
| Warning / New State | `#FFB703` | New Request badges, pending/new intake markers |
| Critical Error State | `#E63946` | Guardrails, admin warnings, hard safety alerts |
| Canvas Background | `#F4F6F9` | Primary app background behind white cards |

Typography uses the Inter/system stack. Timestamps, phone numbers, dates,
metrics, and timeline entries use `font-variant-numeric: tabular-nums`
(`.pm-tabular`). Contrast targets WCAG 2.1 AA where feasible. Tone: premium,
calm, clinical, high-density, authoritative.

## Dashboard 3-column layout

`frontend/app/dashboard/page.tsx` renders a responsive split-screen workspace:

- Desktop/widescreen: `grid-template-columns: minmax(280px,25%) minmax(420px,45%) minmax(320px,30%)`
- Laptop/tablet (≤1200px): 2 columns with the registry spanning full width below
- Mobile (≤768px): stacked, no horizontal overflow
- Each panel scrolls independently

### Dynamic tenant/doctor header

Sticky global header (`sticky top, z-50`) on Primary Structural Ink: PraxisMed
brand, then a dynamic multi-tenant identity banner resolved through
`frontend/lib/tenantDisplay.ts` (staging clinic id
`1a5bbc75-c1b0-4488-94aa-64b3f1c50056` maps to
"Dr. Med. Alexander Huber | Innere Medizin Wien"; unknown tenants fall back to
"Staging Fake Clinic"). The display name is centralized in the helper and never
hardcoded in pages. The header also carries the STAGING DEMO marker, the safety
boundary line "Fake-data staging · No real patient data · Production PHI:
NO-GO", nav links, and the Log Out button.

### Column 1 — Incoming AI Intake Queue

Real-time Vapi phone intake requests from the existing appointment-request API.
Cards show patient name, phone (or "No phone captured"), created/preferred
time, reason preview, source badge for `vapi`, status and urgency badges, and
an amber "New Request" badge (`#FFB703`) when status is new, action is
required, or the request is not yet confirmed. Selection uses `#E0F2F1` and
drives the center workspace; the first request is selected by default. Empty
state: "No incoming AI intake requests yet." The internal notifications panel
sits below the queue ("Internal notification only" — no email/SMS/WhatsApp/
callback delivery claims).

### Column 2 — Active Resolution Workspace

Shows the selected intake request: prominent patient name, phone, reason,
status, urgency, source, preferred time, created time, and the request id in
muted monospace. Contains the Audio Transcript & Call Recording engine, the
existing pre-appointment summary (View summary / Hide summary preserved), a
non-clinical safety note (staff or doctor review required), and the action
footprint: the existing Confirm button (behavior unchanged, teal `#008080`)
plus a disabled progressive CTA "Confirm Appointment & Create Patient Profile"
labeled "Profile creation automation coming next".

### Audio transcript / recording placeholder

Polished player shell with a disabled "Play Audio Call" button, mock waveform
track, transcript/summary box with the safe empty-state copy
"Recording/transcript review will appear here when Vapi recording ingestion is
enabled.", and a metadata row (Vapi source, `source_ref` when available,
"Recording ingestion pending"). No transcript content is invented; no
diagnosis-style content; demo-safe placeholder language only.

### Column 3 — Patient Registry & history

Search header ("Search Clinical Registries...") with icon, patient list from
the existing patients API (name, phone, status badge, patient id in tiny
monospace, selected state), and a profile card on selection (full name, phone,
email, patient id, linked request count). A chronological timeline is derived
only from appointment requests whose `patient_id` matches the selected patient
("YYYY-MM-DD: AI Phone Intake Request Logged" / status / safe reason). With no
linked records the safe placeholders render instead. When the patients array is
empty, clearly marked demo placeholder names ("Dr. Johann Huber",
"Anna Wallner") appear under a "Demo placeholder — not real patients" label;
they are scaffold-only values, never real records.

## Onboarding gateway flow

`frontend/app/onboarding/page.tsx` gained a gated access entry module on the
ink surface: "Start with PraxisMed", subtitle "AI intake and workflow
automation for Austrian private clinics", and two primary choices — "Existing
Clinic Login" and "Request Pilot Access Registration" (disabled scaffold). The
five-step wizard is Clinic Details → Doctor / Admin Account → Workflow
Preferences → AI Intake Setup → Review & Pilot Activation. The HTML rendering
bug is fixed: the step label renders as plain text "Review & Pilot Activation"
(no escaped `&amp;` entity in the visible label). The scaffold is
non-functional, collects no secrets and no Vapi secret keys, shows the
"STAGING SCAFFOLD — NOT FUNCTIONAL" badge, and states that pilot activation
requires security, legal, and production-readiness review before real patient
data can be processed.

## Dark developer console

`frontend/app/developer-console/page.tsx` uses an explicit dense dark-mode
command theme on `#0B132B` with white/slate text, teal `#008080` accents, red
`#E63946` guardrails, and amber `#FFB703` warnings — visually segregated from
the clinical UI to prevent accidental configuration. Panels: Tenant
Provisioning (disabled), Clinic ID Scope Injection (session scope shown,
override disabled), Vapi Machine Credential Binding (placeholders only — no
secret values, no token fields with real values), Environment Checklist
(DATABASE_URL, JWT_SECRET_KEY, VAPI_WEBHOOK_SECRET, INTERNAL_WEBHOOK_SECRET,
FRONTEND_CORS_ORIGINS shown as labels only, never values), and Safety
Guardrails ("Never paste secrets into browser UI", "Production PHI remains
NO-GO until hardening and legal review are complete", "Real tenant
provisioning requires backend admin endpoint and audit trail"). No live
mutation, no real provisioning.

## Preserved behavior

Login, dashboard load, appointment/patient/notification/consultation loading,
View summary / Hide summary, the Confirm handler and its API contract, logout,
cookie-based sessions with `credentials: "include"`, and all existing
`data-section` / `data-action` / `data-state` contract selectors. No
sessionStorage or localStorage token storage. No functionality removed. No API
contract changes.

## Safety boundaries

- Fake data only — staging fake clinic/user; no real patient data anywhere.
- No secrets in the frontend; env var names appear as labels only.
- No diagnosis, no medical advice; AI intake output is administrative
  scheduling information requiring staff or doctor review.
- No delivery claims for email/SMS/WhatsApp/phone callback — internal
  notifications only.
- Production PHI remains **NO-GO**; no production-readiness claim is made.

## Limitations

- Recording/transcript ingestion is a placeholder only — no audio or
  transcript pipeline exists yet.
- Onboarding gateway is a scaffold only — no submission wiring.
- Developer console is a scaffold only — no provisioning or scope mutation.
- External delivery (email/SMS/WhatsApp) remains pending.
- Production and legal hardening (C3–C8, DSGVO review) remain pending.

## Why this improves Austrian private clinic / Wahlarzt demos

Wahlarzt practices are small, premium, doctor-led businesses. The 3-column
workspace shows the complete story in one screen: the AI receptionist capturing
calls (left), the practice resolving a request with full context and a future
recording review (center), and the patient registry with linked history
(right). The calm, high-contrast clinical identity, tabular numerics, and
explicit safety boundaries signal a serious, trustworthy medical product rather
than a prototype — which is what an Austrian private-practice buyer expects to
see in a pilot demo, while the staging markers keep expectations honest.
