# PraxisMed — Clinic Outreach and 30-Day Pilot Offer Pack

**Sprint:** Sprint 18 / Module 127
**Date:** 2026-07-05
**Version:** v1 — Initial outreach asset
**Status:** Active — immediate outreach can begin using this pack

---

## 1. Current Product Positioning

**PraxisMed is an AI receptionist and clinic workflow system for private clinics.**

It uses an AI phone assistant to capture appointment requests from missed or after-hours
calls, links each request to a patient record, prepares a structured pre-appointment
summary for the doctor or staff, creates an internal notification, and gives the clinic
team a dashboard to review and confirm requests.

**What PraxisMed does today (staging demo ready):**
- AI voice assistant answers calls and captures appointment intent
- Appointment request created and linked to patient record
- Pre-appointment summary prepared: patient type, reason, urgency, suggested action
- Internal clinic notification created for staff review
- Premium dashboard for clinic staff: metric cards, appointment rows, View summary, Confirm
- Staff or doctor confirms appointment — no auto-confirmation

**Who it is for:**
- Private doctors and specialists (GP, dermatologist, gynaecologist, orthopaedist, etc.)
- Small private clinics with 1–5 doctors
- Clinics with a real missed-call or after-hours appointment problem
- Reception teams that want to reduce manual call handling

---

## 2. What We Can Safely Show Now

The following can be demonstrated truthfully to any clinic contact:

| Capability | Demo status |
|---|---|
| AI voice assistant captures appointment request | LIVE in staging demo |
| Appointment request linked to patient record | LIVE in staging demo |
| Pre-appointment summary (structured, no diagnosis) | LIVE in staging demo |
| Internal notification for staff | LIVE in staging demo |
| Premium dashboard (metric cards, appointment list, summary panel) | LIVE in staging demo |
| View summary / Hide summary per appointment row | LIVE in staging demo |
| Staff Confirm action (no auto-confirmation) | LIVE in staging demo |
| Staging demo available at https://praximed.vercel.app | LIVE |

All demo data is fake/non-PHI. The dashboard can be shown in any demo call or video
without any real patient data ever appearing.

---

## 3. What We Must Not Claim Yet

The following must NOT be claimed until production hardening is complete:

| Claim | Why not yet |
|---|---|
| "Your real patient data is safe with us" | Production hardening (C3–C8) not complete |
| "We are DSGVO / GDPR compliant" | Legal/compliance review not done |
| "We are ready for live patient data" | Production PHI readiness: NO-GO |
| "We are live with [other clinic]" | No pilot clinic yet |
| "We have X paying customers" | No paying customers yet |
| "We are ISO 27001 certified" | No audit done |

**Safe framing instead:** "We are in an invite-only pilot phase with selected private
clinics. All current demos use synthetic data. Real patient-data activation requires
a signed agreement and our production hardening process."

---

## 4. 30-Day Pilot Offer

### Offer summary

**Free 30-day guided pilot** for the first 5 selected private clinics.

| Item | Detail |
|---|---|
| Duration | 30 days |
| Cost | Free (setup fee waived for first pilot clinics) |
| What clinic gets | Full system setup, staging demo access, weekly check-in calls, direct founder access |
| What we get | Real-world feedback on workflow fit, missed-call problem validation, testimonial if satisfied |
| Commitment | One 30-minute onboarding call, 2x15-minute feedback calls during pilot |
| No lock-in | No contract, no payment during pilot |

### Pilot deliverables to the clinic

1. Dedicated staging demo with clinic's specialty/workflow context
2. AI phone number configured for test calls
3. Dashboard access for 1–2 staff or doctor accounts
4. Pre-appointment summary tuned for their appointment types
5. Weekly 15-minute check-in during the 30 days
6. Written summary of findings and workflow recommendations

### After the pilot

If the clinic wants to continue:

| Plan | Monthly price | Setup fee |
|---|---|---|
| Starter (1 doctor, up to 200 req/month) | **€299/month** | €490 (waived for pilot clinics) |
| Growth (2–5 doctors, unlimited req) | **€499/month** | €790 |
| Custom (multi-location, custom workflow) | On request | €990–€1,190 |

*Pricing in EUR. Annual billing available with 2 months free. Pilot clinics lock in
pilot pricing for 12 months after go-live.*

---

## 5. Pricing Recommendation

**Anchor at €499/month for conversations.** Most private doctors spend more than this
on a single missed appointment or a single advertising placement. Frame value in terms
of recovered missed appointments and receptionist time saved.

**Setup fee psychology:** Waiving the setup fee for pilots removes the risk perception.
Reinstate it at go-live — it signals seriousness and commitment from both sides.

**Avoid hourly or per-call pricing** in initial conversations — it triggers cost scrutiny.
Flat monthly subscription is easier to justify in a private practice budget.

---

## 6. Ideal Clinic Types

**Best-fit clinics for the first 50 outreach contacts:**

| Specialty | Why it fits |
|---|---|
| General practitioner (Allgemeinmedizin) | High call volume, routine appointments, clear missed-call problem |
| Dermatologist (Hautklinik) | Often fully booked, patients call repeatedly, high intake friction |
| Gynaecologist (Gynäkologie) | Appointment requests vary in urgency, pre-summary useful |
| Orthopaedist (Orthopädie) | Strong after-hours demand, clear urgency triage benefit |
| Internist / specialist | Complex intake, pre-appointment summary saves consultation time |
| Private dental (Privatzahnarzt) | High no-show/rescheduling problem, AI intake improves planning |

**Disqualifiers (avoid for initial outreach):**
- Public/municipal hospitals (procurement too slow)
- Clinics with no missed-call problem ("we always answer")
- Clinics that never use tech tools for anything
- Chains that require multi-location enterprise contracts (not yet supported)

---

## 7. 50-Clinic Outreach List Schema

Use this schema to build and track the first 50 target clinics.

| Field | Type | Notes |
|---|---|---|
| `id` | Integer | 1–50 |
| `clinic_name` | String | Full clinic name |
| `doctor_name` | String | Decision-maker's name |
| `specialty` | String | e.g. GP, Dermatologist, Gynaecologist |
| `city` | String | City / district |
| `country` | String | AT / DE / CH |
| `phone` | String | Public contact phone (from clinic website) |
| `email` | String | Public contact email |
| `linkedin_url` | String | Doctor or clinic LinkedIn profile, if available |
| `website` | String | Clinic website URL |
| `outreach_channel` | Enum | email / phone / linkedin / whatsapp / in-person |
| `outreach_stage` | Enum | not_started / contacted / responded / demo_booked / pilot_agreed / declined |
| `first_contact_date` | Date | YYYY-MM-DD |
| `last_contact_date` | Date | YYYY-MM-DD |
| `next_followup_date` | Date | YYYY-MM-DD |
| `notes` | Text | Free-text observations, objections, fit signals |
| `fit_score` | 1–5 | Subjective fit assessment (5 = highest) |

No real patient data. Only publicly available clinic contact information.

---

## 8. Email Outreach Script (English)

**Subject:** Free 30-day AI receptionist pilot for private clinics

---

Dear Dr. [Name],

I'm the founder of PraxisMed — an AI-powered receptionist and appointment workflow
system built specifically for private clinics like yours.

We capture missed and after-hours calls, create structured appointment requests, and
give your team a clean dashboard to review and confirm — without replacing your staff.

I'd like to offer you a **free 30-day pilot** with no setup fee and no commitment.
You keep everything if you find it useful; we learn what actually matters in your
specific workflow.

Would you have 15 minutes this week to see a quick demo?

Best regards,
Ali Abdeltawab
Founder, PraxisMed
[phone] | [email] | https://praximed.vercel.app

*This is an invite-only pilot. All current demos use synthetic data. Real patient
data activation requires a signed agreement.*

---

## 9. German Outreach Script (Deutsch)

**Betreff:** Kostenloser 30-Tage-Pilot: KI-Rezeption für Ihre Privatpraxis

---

Sehr geehrte/r Frau/Herr Dr. [Name],

ich bin Gründer von PraxisMed — einem KI-gestützten Rezeptionssystem speziell für
Privatpraxen.

PraxisMed nimmt verpasste Anrufe außerhalb der Öffnungszeiten entgegen, erstellt
strukturierte Terminanfragen und gibt Ihrem Team ein übersichtliches Dashboard zum
Prüfen und Bestätigen — ohne Ihre Mitarbeiterinnen zu ersetzen.

Ich biete Ihnen einen **kostenlosen 30-Tage-Pilot ohne Einrichtungsgebühr und ohne
Vertragsbindung** an. Sie können das System in Ruhe testen und behalten es nur,
wenn es wirklich zu Ihrem Ablauf passt.

Hätten Sie diese Woche 15 Minuten für eine kurze Live-Demo?

Mit freundlichen Grüßen,
Ali Abdeltawab
Gründer, PraxisMed
[Telefon] | [E-Mail] | https://praximed.vercel.app

*Dies ist ein eingeschränktes Pilotprogramm. Alle aktuellen Demos verwenden
synthetische Daten. Die Aktivierung mit echten Patientendaten erfordert eine
gesonderte Vereinbarung.*

---

## 10. Phone Call Script

**Purpose:** Warm introduction — goal is to book a 15-minute demo, not to sell.

---

**Opening:**
"Good morning / afternoon, my name is Ali, I'm the founder of PraxisMed. I'm calling
to introduce a new AI appointment system built specifically for private practices.
Am I speaking with Dr. [Name], or can you let me know the best person to reach?"

**If gatekeeper / receptionist:**
"Could I ask — does the clinic sometimes miss calls after hours or when the line is
busy? [pause] That's exactly what PraxisMed helps with. Could I send Dr. [Name] a
quick email and perhaps schedule a 15-minute call?"

**If doctor answers:**
"I won't take more than 2 minutes. PraxisMed is an AI assistant that captures
appointment requests from missed calls, creates a summary for you before each
appointment, and gives your team a dashboard to review and confirm — without
replacing your receptionist. I'd love to show you a 15-minute live demo this week.
Is that something that could be useful for your practice?"

**If interested:**
"Fantastic — I'll send you a calendar link right now. We're offering the first pilot
clinics a completely free 30-day trial, no setup fee, no commitment."

**If not interested / busy:**
"Completely understood. Would it be OK if I sent you a short email with the key
details? No spam — just a one-pager so you have it when the timing is right."

---

## 11. WhatsApp / LinkedIn Short Message

**LinkedIn (connection request note):**
> "Hi Dr. [Name] — founder of PraxisMed here. We help private clinics handle
> missed-call appointment requests with AI. Running a free 30-day pilot for selected
> practices. Happy to share a 2-minute demo video if it's relevant."

**WhatsApp (if number is public/shared):**
> "Hi Dr. [Name], this is Ali from PraxisMed. We've built an AI receptionist for
> private clinics — captures missed calls, creates appointment summaries, lets your
> team confirm from a dashboard. Free 30-day pilot for the first clinics. 15-min demo
> this week? Happy to send a link."

*Only message doctors on channels where they have made their contact public.*
*Do not use WhatsApp cold if the number was obtained from a data broker or aggregator.*

---

## 12. 15-Minute Demo Call Structure

| Minute | Content |
|---|---|
| 0–2 | Intro: who is PraxisMed, what problem it solves (missed calls → lost appointments) |
| 2–5 | Live demo: login to https://praximed.vercel.app, show dashboard overview, metric cards |
| 5–8 | Appointment flow: show appointment row, click View summary, walk through summary fields |
| 8–10 | Notifications: show notification row, explain internal-only, no diagnosis, staff review |
| 10–12 | Value framing: "How many calls do you miss per week? What's an appointment worth?" |
| 12–14 | Pilot offer: free 30 days, no setup fee, what the clinic gets |
| 14–15 | Next step: schedule onboarding call or send follow-up email |

**Always end with a specific next step — never end with "I'll send you some info."**

---

## 13. Demo Script Using Current Product Flow

Use this when sharing screen on https://praximed.vercel.app/dashboard.

---

**Step 1 — Dashboard overview (30 seconds):**
"This is the PraxisMed clinic dashboard. You can see at the top: 9 appointment
requests, 6 linked patients, 1 notification, 0 pending confirmations right now.
Your staff sees this the moment they open the dashboard — no scrolling, no digging."

**Step 2 — Appointment row (1 minute):**
"Each row shows the patient name, their status, and urgency level. For any new request,
the Confirm button appears. Staff reviews and confirms — never automatic."

**Step 3 — View summary (2 minutes):**
"Here's the key feature — click View summary. This panel shows: the patient type
(new or returning), reason for the appointment, urgency level, prior visit count,
and a suggested action. This is generated without any diagnosis or medical advice —
it's a structured factual brief to help staff or the doctor prepare in seconds.
And the safety note here makes it clear: this is informational, doctor review required."

**Step 4 — Notifications (1 minute):**
"The Notifications section shows internal alerts — in this case, a new appointment
request came in, notification status is pending, and the message is right there.
No external SMS or email yet — this is the internal queue for your team."

**Step 5 — What the AI did (30 seconds):**
"All of this happened because a test caller spoke to our AI assistant. It captured the
appointment intent, linked the caller to a patient record, created the summary, and
sent the notification — all in seconds, without your receptionist picking up."

---

## 14. Objection Handling

### "Is it secure? What about patient data?"

> "Great question — and the honest answer is: right now, all demos run on synthetic
> data only. Real patient data activation requires a signed data processing agreement,
> our production security hardening, and full DSGVO review. We don't skip that step.
> The pilot is designed to validate the workflow with your team before any real data
> is involved."

### "Do you have other clients / clinics using this?"

> "We're in an invite-only pilot phase — you'd be among the first clinics to pilot it.
> That means direct founder access, your feedback shapes the product, and you lock in
> early pricing. We're not trying to sell to 100 clinics tomorrow — we want 5 clinics
> that we can serve really well."

### "What does it cost?"

> "The 30-day pilot is completely free — no setup fee, no contract. If you want to
> continue after the pilot, it's €299/month for a single-doctor practice. We waive
> the setup fee for pilot clinics. Annual billing saves you two months."

### "We already have a receptionist."

> "Perfect — PraxisMed isn't a replacement. It handles the calls your receptionist
> can't — after hours, during lunch, when the line is busy. Your receptionist focuses
> on patients in front of them; PraxisMed handles everything that would otherwise
> go to voicemail or be missed entirely."

### "Is it compliant with DSGVO / Austrian privacy law?"

> "We are building the compliance layer now — data processing agreements, audit logs,
> access controls. The pilot uses only synthetic data, so no DSGVO questions apply
> during the pilot. We will provide a full DSGVO-ready version before any real patient
> data is ever activated. We won't rush that — it has to be right."

### "We don't use technology in our practice."

> "Understood. I'd just ask: do you ever miss calls? Do patients leave voicemails that
> get returned the next day? If yes, PraxisMed can help with that specific problem
> without changing anything else in your workflow. The demo is 15 minutes — no
> commitment."

---

## 15. Follow-Up Sequence

| Day | Action |
|---|---|
| Day 0 | Initial outreach (email / phone / LinkedIn) |
| Day 3 | Follow-up if no response: "Just checking in — did my note land OK?" |
| Day 7 | Second follow-up: share a short demo video or dashboard screenshot |
| Day 14 | Final follow-up: "Closing the loop — let me know if timing is better later." |
| Day 30+ | Re-engage if new feature or milestone (e.g. "We've just added [X]...") |

**After demo call:**
- Same day: send summary email with pilot offer details
- Day 3: follow up with "Any questions from the team?"
- Day 7 (if no reply): gentle nudge, ask if they want to loop in another decision-maker

**If declined:**
- Thank them, ask for the core reason
- Ask if they know another clinic that might benefit (referral)
- Add to re-engagement list for 60 days later

---

## 16. Contract / Pilot Next Steps

When a clinic agrees to the pilot:

1. **Onboarding call (30 min):**
   - Understand their specialty, call volume, appointment types
   - Agree on test call scenarios
   - Set up their staging demo account

2. **Week 1 check-in (15 min):**
   - Walk through the dashboard together
   - Make any workflow adjustments

3. **Week 2–3 (async):**
   - Clinic team uses the dashboard
   - AI phone test calls continue

4. **Week 4 debrief (30 min):**
   - Review: did it solve the missed-call problem?
   - Would they continue?
   - If yes: sign a lightweight service agreement + data processing agreement
   - Agree on go-live date for real patient data activation (requires hardening completion)

**No real patient data until:**
- Production hardening complete (C3–C8)
- DSGVO / Austrian data protection legal review complete
- Data processing agreement (DPA) signed
- Clinic staff trained

---

## 17. Safety / Legal Boundaries

| Boundary | Rule |
|---|---|
| Fake/synthetic data only in demo and pilot | CONFIRMED — no real patient data in any demo |
| No PHI production readiness claim | CONFIRMED — production PHI: NO-GO until hardening complete |
| No DSGVO/GDPR compliance claim | Must not claim compliance until legal review done |
| No "HIPAA compliant" claim | PraxisMed is EU-based; HIPAA not applicable; do not mention |
| No medical advice or diagnosis | CONFIRMED — summary display is factual only; safety note present |
| No auto-confirmation | CONFIRMED — doctor/staff Confirm action required |
| Doctor/staff approval always required | CONFIRMED — no automated clinical decisions |
| No competitor disparagement | Do not mention competitor names or make negative claims |
| No fabricated testimonials | Do not invent clinic quotes or case studies |
| No revenue or valuation claims | Do not mention ARR, valuation, or funding status |

---

## 18. Outreach Daily Targets

**To reach 50 clinics in the first 4 weeks:**

| Week | Daily target | Channel mix | Goal |
|---|---|---|---|
| Week 1 | 3–4 contacts/day | Email primary; LinkedIn secondary | 15–20 clinics contacted |
| Week 2 | 3–4 contacts/day | Follow-up calls; new LinkedIn | 15–20 more; 2–3 demo calls booked |
| Week 3 | 2–3 contacts/day + 2 demo calls | Demo calls + follow-up sequence | 1–2 pilot agreements |
| Week 4 | 2 contacts/day + pilot onboarding | Onboarding + continued outreach | First pilot clinic onboarded |

**Minimum viable outreach per day:**
- 1 email (new or follow-up)
- 1 LinkedIn connection or message
- 1 phone call attempt (even if gatekeeper)

**Track everything in the 50-clinic outreach list schema (Section 7).**

---

*This pack uses fake/non-PHI data only. No real patient data is referenced anywhere.*
*Production PHI readiness: NO-GO until C3–C8 hardening is complete.*
*All pricing is indicative and subject to change before formal agreements.*
