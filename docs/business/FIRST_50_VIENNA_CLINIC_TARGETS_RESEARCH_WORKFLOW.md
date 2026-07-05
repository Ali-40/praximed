# First 50 Vienna Clinic Targets — Research Workflow

**Sprint:** Sprint 18 / Module 129
**Date:** 2026-07-05
**Status:** Workflow ready — manual research can begin immediately

---

## 1. Purpose

This document defines the safe, accurate workflow for manually researching and
entering the first 50 private clinic targets in Vienna into the outreach tracker
(`docs/business/CLINIC_OUTREACH_LIST_TRACKER.md`).

**Core rule:** Every field in the tracker must come from a real, publicly accessible
source. No guessing. No fabricating. No scraping automation.

---

## 2. Safe Research Rules

| Rule | Detail |
|---|---|
| **Public information only** | Use only data that a clinic has voluntarily published on its own website, a public directory, or a legally required Impressum |
| **No scraping automation** | All research is manual — open a page, read it, copy the relevant public field |
| **No fabricated data** | Never invent or guess a clinic name, phone, email, doctor name, or address |
| **Source URL required** | Every row must have a source URL logged in the Notes column so any field can be verified |
| **Email only if public** | Only log an email if it appears on the clinic's own website or directory listing |
| **Phone only if public** | Only log a phone if it appears on the clinic's own website or directory listing |
| **Doctor/owner only if public** | Only log a name if the clinic publishes it on its website (Team / Über uns / Impressum) |
| **Do not guess** | If a field is not found from a public source, leave it blank |
| **No patient data** | Never collect, record, or infer any patient information |
| **No secrets** | No passwords, API keys, or authentication data in any field |

---

## 3. Public Sources to Use

Research each clinic using one or more of the following **public** sources:

### 3.1 Google Maps
- Search: `"Privatarzt Wien [Specialty]"` or `"private [specialty] clinic Vienna"`
- Yields: clinic name, address, phone, website link, sometimes opening hours
- Click through to the clinic website for email and doctor name

### 3.2 Clinic Websites (Direct)
- Every Austrian clinic must publish an **Impressum** — a legally required page that
  lists the clinic owner, address, and contact information
- Navigate to the clinic's website → look for "Impressum", "Kontakt", or "Über uns"
- Record: doctor/owner name, email, phone, address, specialty

### 3.3 Herold (herold.at)
- Austrian business directory
- Search by category and district (e.g. "Arzt Wien 1010")
- Yields: clinic name, phone, address, sometimes website

### 3.4 DocFinder (docfinder.at)
- Austrian doctor and clinic directory
- Search by specialty and postcode
- Yields: doctor name, specialty, address, phone, sometimes rating

### 3.5 WKO (wko.at — Firmen A–Z)
- Austrian Chamber of Commerce business registry
- Search by trade code and district
- Yields: registered business name, address, sometimes contact

### 3.6 Ärzteliste (ärzteliste.at)
- Austrian medical council public register
- Search by specialty and canton/state
- Yields: doctor name, specialty, address — useful for verifying credentials

### 3.7 LinkedIn (public profiles only)
- Search: `"Dr [Name] Wien [Specialty]"`
- Only use if the profile is publicly visible without login
- Useful for: confirming doctor name, checking if they are a practice owner

---

## 4. Target Specialties and Distribution

Target this specialty mix across the 50 clinics:

| Specialty | Target count | Search term (German) |
|---|---|---|
| Private GP | 12 | Allgemeinmedizin privat Wien |
| Dermatology | 8 | Dermatologie / Hautarzt privat Wien |
| Gynecology | 8 | Gynäkologie / Frauenarzt privat Wien |
| Orthopedics | 6 | Orthopädie privat Wien |
| Dentistry | 6 | Zahnarzt privat Wien |
| Aesthetics / private medicine | 6 | Ästhetische Medizin / Privatarzt Wien |
| Physiotherapy / private rehab | 4 | Physiotherapie privat Wien |
| **Total** | **50** | |

---

## 5. Data Quality Rules

Before entering any field into the tracker, confirm:

| Field | Rule |
|---|---|
| Clinic name | Must appear verbatim on the clinic's website or directory listing |
| Specialty | Must match what the clinic advertises (not assumed from doctor name) |
| Website | Must be a real, working URL — verify it loads |
| Email | Must appear on the clinic's own website or directory; never guessed |
| Phone | Must appear on the clinic's own website or directory; never guessed |
| Address | Must be from the clinic's website Impressum or directory listing |
| Doctor/Owner | Must appear on the clinic's own website (Team, Über uns, Impressum) |
| Fit score | Assigned by researcher based on specialty, location, visible call workflow |
| Pain point guess | Honest estimate based on specialty and visible online presence |
| Source URL | Required — paste the URL where the clinic was found |

**If a field cannot be verified from a public source: leave it blank.**
Never fill a field with a guess, an approximation, or data from a non-public source.

---

## 6. Prioritization

### A-fit clinics (highest priority)

Assign **A** and prioritise for Week 1 outreach when a clinic shows:
- Operates as a fully private practice (not public/Kassenarzt)
- Specialty with high appointment volume (GP, dermatology, gynecology)
- Has a public phone number prominently listed (signals phone-heavy workflow)
- Has 1–5 doctors (small enough that the owner is reachable, large enough to have workload)
- Website mentions "Termin" (appointment) or "Termin online" without a fully automated system

### B-fit clinics

Assign **B** when:
- Private practice confirmed but call volume unclear
- Less common specialty or less appointment-intensive
- Larger group practice or works partly with Kasse

### C-fit clinics

Assign **C** and deprioritise when:
- Mixed Kasse/private model (primary revenue from public health fund)
- Large group practice with a dedicated admin team (harder to reach decision-maker)
- No visible appointment booking friction
- Already fully automated online booking with no obvious missed-call problem

---

## 7. First Batch Execution

Follow this sequence for the first research session:

### Step 1 — Research first 10 clinics (before any outreach)
1. Open Google Maps, search `"Privatarzt Wien Allgemeinmedizin"`
2. Pick the first 10 results that are clearly private practices
3. For each: open their website, find Impressum/Kontakt, record all available public fields
4. Log source URL in Notes column
5. Assign fit score (A/B/C)
6. Fill rows 1–10 in the tracker

### Step 2 — Contact first 5 (highest fit score)
1. Pick the 5 with the best fit score from rows 1–10
2. Send email using the script from Module 127 (English or German depending on clinic)
3. Log: Contact method = Email, Outreach status = Email sent, Last contacted = today's date
4. Set: Next follow-up = 3 business days from today

### Step 3 — Set follow-up reminder
- Mark a calendar reminder for the follow-up date of each of the first 5 contacts
- After 3 business days with no reply: follow up using the follow-up script from Module 127

### Step 4 — Continue research
- Add 10 more clinics per day until all 50 rows are filled
- Continue contacting 5 per day (mix of new contacts and follow-ups)

---

## 8. Safe Outreach Wording

Every outreach message must use language consistent with these boundaries:

| What to say | What not to say |
|---|---|
| "We are in an invite-only pilot phase with selected private clinics" | "We are live with [clinic name]" |
| "All current demos use a fake-data staging environment" | "Your patient data will be handled securely from day one" |
| "Real patient data activation requires a signed agreement and our production hardening process" | "We are DSGVO compliant" |
| "Free 30-day pilot — no setup fee, no commitment" | "We are already processing real patient records" |
| "Early pilot clinics lock in pricing" | Any specific revenue, valuation, or funding claim |

Use the email/phone/WhatsApp scripts and objection responses from Module 127
(`docs/business/CLINIC_OUTREACH_30_DAY_PILOT_PACK.md`) verbatim.

Key boundary reminders:
- **Fake-data demo** — staging dashboard at https://praximed.vercel.app uses synthetic data only
- **Early pilot** — this is an invite-only pilot, not a fully launched product
- **No production PHI** — production PHI readiness: NO-GO until C3–C8 hardening complete
- **No DSGVO readiness claim** — do not claim DSGVO or Austrian data protection compliance yet

---

## 9. Manual Tracker Filling Instructions

Open: `docs/business/CLINIC_OUTREACH_LIST_TRACKER.md`

For each clinic row:
1. Enter the clinic name in the **Clinic name** column (verbatim from source)
2. Enter specialty in **Specialty** (match to one of the 7 target types)
3. Paste the clinic's website URL in **Website**
4. Enter public email in **Email** (if listed on clinic website — leave blank if not)
5. Enter public phone in **Phone** (if listed — leave blank if not)
6. Enter address in **Address** (from website Impressum or directory)
7. Enter doctor/owner name in **Doctor / Owner** (from website — leave blank if not public)
8. Assign **Fit score**: A, B, or C
9. Enter **Pain point guess** (e.g. "Likely misses after-hours calls", "High appointment volume, small team")
10. Set **Contact method**: email / phone / linkedin
11. Set **Outreach status**: Not contacted
12. Leave **Last contacted** and **Next follow-up** blank until first contact is made
13. Set **Demo booked?**: No
14. In **Notes**: paste the source URL where you found this clinic

---

## 10. Next Action Checklist

Use this checklist before the first outreach session:

- [ ] Open `docs/business/CLINIC_OUTREACH_LIST_TRACKER.md`
- [ ] Open Google Maps in a browser
- [ ] Search: `"Privatarzt Wien Allgemeinmedizin"` — open first result
- [ ] Navigate to clinic website → Impressum or Kontakt
- [ ] Fill row 1 with public data; paste source URL in Notes
- [ ] Repeat for rows 2–10 (10 clinics total in first session)
- [ ] Assign fit score A/B/C to all 10
- [ ] Pick top 5 by fit score
- [ ] Send email to each using Module 127 German or English script
- [ ] Update tracker: Email sent, Last contacted = today, Next follow-up = +3 business days
- [ ] Set calendar reminder for follow-up dates

---

*No real patient data. No secrets. No fabricated clinic information.*
*Public-source-only research. Production PHI: NO-GO.*
