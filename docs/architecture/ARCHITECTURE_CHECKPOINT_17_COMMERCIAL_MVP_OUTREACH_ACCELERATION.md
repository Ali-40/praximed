# Architecture Checkpoint 17 — Commercial MVP and Clinic Outreach Acceleration Plan

**Date:** 2026-07-05
**Sprint:** Sprint 17 / Architecture Checkpoint 17
**Mode:** Commercial acceleration — outreach starts now while product build continues
**Technical base commit:** 38e9234

---

## 1. Current Technical State

| Item | Status |
|---|---|
| Railway backend (HTTPS; health endpoints; machine auth; DB write) | **PASS** |
| Railway PostgreSQL (migrated schema; asyncpg pool; stable) | **PASS** |
| Vercel frontend (Next.js; HTTPS; login; protected dashboard) | **PASS** |
| Browser login (httpOnly cookie; SameSite=None; session survives refresh) | **PASS** |
| Vapi appointment capture (tool call → DB row; status=new) | **PASS** |
| Staff Confirm (dashboard Confirm button → status=confirmed; no auto-confirm) | **PASS** |
| Deployed auth/session browser smoke (Modules 120 + 120A + 120B) | **PASS** |
| Fake-data staging core | **PASS** |
| Production PHI readiness | **NO-GO** |
| Full test suite | **2570/2570 passed** |

The system is technically sound, deployed, and working end-to-end with fake data.
It is **not yet cleared for real patient data or production PHI use**.

---

## 2. What Can Be Shown to Doctors Now

The following can be demonstrated immediately to prospective clinic contacts using
the fake-data staging environment:

- **Live AI phone agent demo** — call Vapi, hear the assistant greet a fake patient,
  capture an appointment request via natural-language phone call
- **Real-time dashboard** — show the captured appointment appearing in the dashboard
  within seconds of the call ending
- **Staff Confirm workflow** — show the one-click Confirm action changing status from
  `new` to `confirmed` without automation
- **Secure login** — demonstrate the login flow and the protected clinic dashboard
- **Multi-tenant architecture** — explain that each clinic's data is fully isolated

All of this runs on real deployed infrastructure (Railway + Vercel) and is genuinely
functional, not a mock or mockup.

---

## 3. What Must Not Be Claimed Yet

The following claims are **not permitted** until the corresponding gaps are closed:

| Claim | Reason not yet permissible |
|---|---|
| "GDPR/HIPAA compliant" | No formal compliance review completed |
| "Ready for real patient data" | Production PHI readiness is NO-GO |
| "Your patient data is safe with us" (as a legal guarantee) | Security hardening C3–C8 not complete |
| "We have automated appointment confirmation" | System requires manual staff Confirm |
| "Full calendar integration" | n8n calendar sync is PENDING/DEFERRED |
| "Complete EMR/patient database" | Patient database linking not yet built |

**Safe claims that can be made now:**
- "We have a working AI phone agent that captures appointment requests"
- "Staff review and confirm every appointment manually"
- "Your data runs on HTTPS-only, isolated infrastructure"
- "We are actively hardening the system for full production use"
- "This is an early-access pilot — we are building with you"

---

## 4. Commercial MVP Feature Map

### Currently working (demo-ready)

| Feature | Status |
|---|---|
| AI phone agent captures appointment requests via Vapi | **WORKING** |
| Real-time dashboard showing new requests | **WORKING** |
| Staff Confirm/manage appointment requests | **WORKING** |
| Secure httpOnly cookie auth (login/logout/session) | **WORKING** |
| Multi-tenant data isolation (clinic_id scoping) | **WORKING** |
| HTTPS on all endpoints (Railway + Vercel) | **WORKING** |

### Must be built for commercial pilots (priority order)

| # | Feature | Module |
|---|---|---|
| 1 | **Patient database linking** — link appointment requests to patient records | Module 121 |
| 2 | **Appointment lifecycle** — scheduled → confirmed → completed → cancelled states | Module 122+ |
| 3 | **Doctor/reception notification** — push/email alert on new appointment | Module 123+ |
| 4 | **Pre-appointment summary** — patient history brief before the call | Module 124+ |
| 5 | **Consultation summary draft** — AI-generated post-consultation note | Module 125+ |
| 6 | **Follow-up/reminder workflow** — automated SMS/email reminder to patient | Module 126+ |
| 7 | **Clinic onboarding/settings** — self-serve clinic config, user management | Module 127+ |
| 8 | **Fabel 5 premium UI/UX polish** — doctor-grade interface design | Sprint 18 |

---

## 5. Product Build Track

### Immediate (Modules 121–126, Sprint 17)

Focus: build the commercial MVP features that pilot clinics will need most.

1. **Module 121** — Patient and Appointment Data Linking Foundation
2. **Module 122** — Appointment lifecycle states and workflow
3. **Module 123** — Doctor/reception notification (email or push)
4. **Module 124** — Pre-appointment patient summary
5. **Module 125** — Consultation summary draft generator
6. **Module 126** — Follow-up and reminder workflow

### Sprint 18

- **Fabel 5 premium UI/UX polish** — transform the functional dashboard into a
  premium, doctor-facing product; high priority for demo quality and sales conversion

### Sprint 19+

- Clinic onboarding/settings self-serve
- n8n calendar sync
- Full EMR integration (deferred)

---

## 6. Production Hardening Track

The following security hardening modules are **still required before real patient data**:

| Module | Title | Closes |
|---|---|---|
| Module 121 | Secrets and environment hardening review | C3 |
| Module 122 | PHI logging/redaction and audit hardening | C4, C6 |
| Module 123 | Tenant isolation and access-control verification | C5 |
| Module 124 | Backup/restore and rollback runbook | C7, C8 |
| Module 125 | Monitoring/alerts/rate-limit plan | H1–H4 |

**These can run in parallel with the product build track.** They do not block demos or
pilot qualification — they block real patient data ingestion only.

---

## 7. Clinic Outreach Track

### Start immediately

Clinic outreach starts now. The fake-data staging core is PASS and the demo is
compelling enough for first discovery/qualification calls.

### Target profile (initial outreach)

- **Geography:** Private clinics in Vienna (Austria) — high density, high willingness
  to pay for premium tooling, close for in-person demo if needed
- **Specialty focus:** General practitioners (Allgemeinmedizin), specialists with high
  phone appointment volume (dermatology, orthopedics, ophthalmology)
- **Size:** Solo practitioners and small practices (2–10 staff) — fastest to decide,
  lowest compliance overhead, highest impact from AI phone handling
- **Pain point match:** Receptionist overload from appointment calls; missed calls
  outside office hours; manual scheduling errors

### First 50 private clinics in Vienna

Build the first outreach list of 50 private clinics in Vienna immediately. Sources:
- Docfinder.at (largest Austrian doctor directory)
- WKO Ärzteliste (Chamber of Commerce doctor register)
- Google Maps / local search ("Privatarzt Wien", "Privatordination Wien")
- LinkedIn (clinic owners, practice managers)

Target: 50 clinics identified, with contact name, phone, email, and specialty noted.
Goal: 10–15 first-contact messages or calls within 14 days.

### Outreach message framing

Position as a **founding clinic partner**, not a cold sales call:

> "We are building an AI phone assistant for private clinics in Vienna.
> It captures appointment requests 24/7, shows them to your reception staff for
> one-click confirmation, and handles missed calls automatically.
> We are looking for one or two founding clinics to pilot this with us —
> you get it free or heavily discounted, and we build around your feedback.
> Would you have 15 minutes for a quick call or demo?"

---

## 8. 30-Day Pilot Offer

### Offer structure

A 30-day pilot can be offered to qualifying clinics under the following conditions:

| Item | Condition |
|---|---|
| Data used | Fake/test data only, OR clinic's own non-PHI data with written consent |
| Patient data | No real patient PHI until production hardening C3–C8 is complete |
| Price | Free for founding clinics; or €0 for 30 days, then €X/month |
| What they get | Working AI phone agent + staff dashboard + onboarding support |
| What we get | Feedback, testimonial, case study, conversion to paid |
| Legal | Pilot agreement with explicit data-use scope; no PHI clause until cleared |

### Pilot qualification criteria

Ideal first pilot clinic:
- Willing to use fake/test patient names during pilot period
- Has a receptionist who will interact with the dashboard daily
- English or German speaking (both supported by Vapi)
- Open to weekly feedback calls

---

## 9. Recommended Pricing Range

Based on value delivery (receptionist call handling, 24/7 availability, appointment
capture) and Austrian private clinic market:

| Tier | Monthly | What's included |
|---|---|---|
| Starter | €149–199/month | 1 Vapi phone number; dashboard; up to 200 calls/month |
| Growth | €299–399/month | 2 numbers; notifications; priority support; up to 500 calls |
| Practice | €599–799/month | Unlimited numbers; full feature set; SLA; onboarding |

**Founding clinic discount:** First 5 clinics get 50% off for 12 months in exchange
for structured feedback and a public testimonial.

These are indicative ranges. Validate with first discovery calls before committing
to public pricing.

---

## 10. 14-Day Execution Timeline

| Day | Action |
|---|---|
| Day 1–2 | Build first 50-clinic outreach list (Vienna private clinics) |
| Day 2–3 | Write outreach email/message templates (German + English) |
| Day 3–5 | Send first 15–20 outreach messages |
| Day 5–7 | Module 121: Patient and Appointment Data Linking Foundation |
| Day 7–10 | Follow up on outreach; book first discovery calls |
| Day 10–12 | Module 122: Appointment lifecycle states |
| Day 12–14 | First discovery/demo calls with interested clinics |
| Day 14 | Review: leads in pipeline, product gaps from calls, adjust roadmap |

---

## 11. Outreach Readiness Checklist

| Item | Status |
|---|---|
| Live demo environment (Vercel + Railway + Vapi) | **READY** |
| Demo script (AI call → dashboard → Confirm) | **Ready to prepare** |
| Outreach message templates (German + English) | **Ready to prepare** |
| First 50-clinic target list (Vienna) | **To do — Day 1** |
| LinkedIn/email outreach setup | **To do** |
| Pilot agreement template (no-PHI clause) | **To do — Day 3** |
| Pricing deck or one-pager | **To do — Day 3** |
| Calendly or booking link for discovery calls | **To do — Day 1** |
| Fabel 5 premium UI/UX (for demo quality) | **Sprint 18 — high priority** |

---

## 12. Safety and Legal Boundaries

The following constraints apply throughout the outreach and pilot phase:

| Constraint | Status |
|---|---|
| No real patient data in staging or demo environment | **ENFORCED** |
| No production PHI until C3–C8 hardening complete | **ENFORCED** |
| No GDPR/HIPAA compliance claims until formal review | **ENFORCED** |
| No secrets recorded (JWT_SECRET_KEY, DATABASE_URL, etc.) | **ENFORCED** |
| Pilot agreement must include explicit no-PHI clause | **Required before any pilot starts** |
| Founding clinic data scope must be documented in writing | **Required before any pilot starts** |
| Demo calls use fake patient names only | **ENFORCED** |

---

## 13. Recommended Next Technical Module

**Sprint 17 / Module 121 — Patient and Appointment Data Linking Foundation**

This module should:
- Define the data model linking `appointment_requests` to `patients` (or a new
  `appointments` table with lifecycle states)
- Implement the repository and schema changes
- Add API routes for the linked data
- Full test suite must pass

This is the highest-leverage technical step for commercial readiness, directly enabling
the appointment lifecycle, notification, and summary features that pilot clinics will need.

---

## 14. Parallel Non-Code Task

**Build first list of 50 private clinics in Vienna and start outreach immediately.**

This runs in parallel with Module 121. No code changes required for outreach —
the demo is already working.

Start with Docfinder.at and Google Maps. Build the list in a spreadsheet with:
clinic name, specialty, contact name (if findable), phone, email, Google Maps link,
notes. Prioritize solo practitioners and small practices with high phone volume.

---

## 15. Fake-Data Staging and Safety Summary

| Constraint | Status |
|---|---|
| No secrets recorded | **CONFIRMED — no secrets recorded** |
| No real patient data | **CONFIRMED — fake/non-PHI staging only** |
| No production PHI | **CONFIRMED — production PHI NO-GO** |
| Fake-data staging core | **PASS** |
| Production PHI readiness | **NO-GO until C3–C8 closed** |
