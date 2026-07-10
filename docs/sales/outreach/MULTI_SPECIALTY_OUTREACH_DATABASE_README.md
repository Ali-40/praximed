# Multi-Specialty Praxisplan Outreach Database — README

**Purpose:** Manual B2B outreach tracker across all high-potential doctor/practice specialties.
**Source:** Public listings on [praxisplan.at](https://www.praxisplan.at)
**Owner:** Ali (PraxisMed sales)
**Last updated:** 2026-07-10

---

## Specialties Included

| Tier | Specialty Key | Label DE | Praxisplan ID | Approx. Entries |
|---|---|---|---|---|
| 1 | child_adolescent_psychiatry | Kinder- u. Jugendpsychiatrie u. Psychotherapeutische Medizin | 71 | ~70 |
| 1 | dermatology | Haut- u. Geschlechtskrankheiten / Dermatologie | 6 | ~298 |
| 1 | gynecology | Frauenheilkunde u. Geburtshilfe / Gynäkologie | 4 | ~432 |
| 1 | orthopedics | Orthopädie und Traumatologie | 68 | ~494 |
| 1 | internal_medicine | Innere Medizin | 7 | ~799 |
| 2 | ent | Hals-, Nasen- u. Ohrenheilkunde (HNO) | 5 | ~195 |
| 2 | urology | Urologie | 15 | ~170 |
| 2 | neurology | Neurologie | 49 | ~227 |
| 2 | ophthalmology | Augenheilkunde u. Optometrie | 2 | ~299 |
| 2 | pediatrics | Kinder- u. Jugendheilkunde / Pädiatrie | 8 | ~334 |
| 3 | private_dental | Zahnarzt privat | — | *(no Praxisplan ID)* |
| 3 | aesthetic_medicine | Ästhetische Medizin / Plastische Chirurgie | 30 | ~111 |
| 3 | plastic_surgery | Plastische u. Rekonstruktive Chirurgie | — | *(covered by aesthetic_medicine)* |
| 3 | adult_psychiatry | Psychiatrie u. Psychotherapeutische Medizin | 52 | ~477 |
| 3 | private_group_practices | Privatpraxis / Gruppenpraxis | — | *(no Praxisplan ID)* |

**Note:** Praxisplan.at covers registered Austrian medical doctors only. Dentists
are listed separately by the Österreichische Zahnärztekammer, not on Praxisplan.

---

## Files in this folder

| File | Description |
|---|---|
| `praxisplan_all_high_potential_leads.xlsx` | Master workbook — all specialties, all sheets. **Start here.** |
| `praxisplan_all_high_potential_leads.csv` | Master leads as flat CSV. |
| `praxisplan_{specialty}_leads.xlsx` | Per-specialty workbook (e.g. `praxisplan_dermatology_leads.xlsx`) |
| `praxisplan_{specialty}_leads.csv` | Per-specialty CSV |
| `praxisplan_specialty_sources.json` | Config file — edit to change source URLs or add specialties |
| `MULTI_SPECIALTY_OUTREACH_DATABASE_README.md` | This file |
| `praxisplan_child_psychiatry_leads_README.md` | Original single-specialty README (still valid) |

---

## How to run the builder

### Build all specialties at once

```bash
python scripts/sales/build_praxisplan_multi_specialty_leads.py --all
```

### Build one specialty only

```bash
python scripts/sales/build_praxisplan_multi_specialty_leads.py --specialty dermatology
python scripts/sales/build_praxisplan_multi_specialty_leads.py --specialty gynecology
python scripts/sales/build_praxisplan_multi_specialty_leads.py --specialty orthopedics
```

### Template mode only (no internet required)

```bash
python scripts/sales/build_praxisplan_multi_specialty_leads.py --templates-only
```

### Use custom config file

```bash
python scripts/sales/build_praxisplan_multi_specialty_leads.py --all \
    --config docs/sales/outreach/praxisplan_specialty_sources.json
```

---

## How to add a new specialty or source URL

1. Open `docs/sales/outreach/praxisplan_specialty_sources.json`
2. Find the entry with the `specialty_key` you want to activate
3. Paste the Praxisplan search URL into the `source_url` field
4. Save the file
5. Run the builder again for that specialty

**Example:** To activate `private_dental`, find a dental listing source URL
(e.g. from zahnarztsuche.at or a dental listing) and paste it into the
`private_dental` entry's `source_url`.

---

## How to find a Praxisplan source URL

1. Go to [https://www.praxisplan.at/suche](https://www.praxisplan.at/suche)
2. Select the specialty from the filters
3. Copy the full URL from your browser address bar
4. Paste it into the `source_url` field in `praxisplan_specialty_sources.json`

---

## How to use the Excel tracker

1. Open `praxisplan_all_high_potential_leads.xlsx`
2. Use the **All Leads** sheet for bulk filtering and review
3. Use the per-specialty sheets to focus on one specialty at a time
4. Use the **Summary** sheet to track progress overall
5. Update **Outreach Status** using the dropdown for every contact attempt
6. Log call attempts in **Call Attempt 1 Date / Result**, **Call Attempt 2 Date / Result**
7. Log emails in **Email Sent Date / Email Result**
8. Log walk-ins in **Walk-in Date / Walk-in Result**
9. Set **Demo Offered**, **Demo Booked**, **Pilot Interest** as conversations progress
10. Set **Outreach Status = Do not contact** if a clinic declines outreach

---

## Outreach Status Definitions

| Status | When to use |
|---|---|
| Not contacted | Default — not yet reached out |
| Called | Attempted a call |
| No answer | Called, nobody answered |
| Reception reached | Spoke to receptionist |
| Asked to send email | They said to email them |
| Email sent | Email has been sent |
| Follow-up needed | Needs a follow-up call/email |
| Demo offered | Demo was offered in conversation |
| Demo booked | Demo appointment confirmed |
| Interested | Shows interest, no demo yet |
| Not interested | Explicitly not interested |
| Wrong target | Not the right type of practice |
| Do not contact | Requested no further contact |

---

## Priority Score

| Score | Meaning |
|---|---|
| 5 | Ideal: phone + contact info + Vienna + high-callback specialty |
| 4 | Strong: Vienna + phone, or email/website available |
| 3 | Average: some contact info, needs manual review |
| 2 | Weak: missing phone or not in Vienna |
| 1 | Low: very limited public contact info |

---

## Responsible outreach rules

- **Public contacts only.** Use only the phone numbers and emails listed publicly on
  Praxisplan.at or the practice's own public website. No private data.
- **No mass-emailing.** Do not send automated bulk emails. Every email is individual, personal, and written by you.
- **No auto-calling.** Do not use auto-dialers. Every call is a manual, personal phone call.
- **No patient data.** This is a B2B sales tracker. Never record patient names, health data,
  appointment details, or any PHI here. This is not a product database.
- **No PHI.** Production PHI is NO-GO. This tracker is for practice contact details only.
- **Respect opt-outs.** If a clinic says they are not interested or asks not to be contacted again,
  immediately set **Outreach Status = Do not contact** and do not contact them again, ever.
- **Professional notes only.** The Notes column is for outreach context. No personal remarks.
- **No medical claims.** Do not promise clinical outcomes when pitching PraxisMed.
- **No DSGVO overclaims.** Do not promise "full DSGVO compliance" without legal review.
  Use: *"Wir legen großen Wert auf Datenschutz — gerne schicken wir Ihnen unsere Datenschutzunterlagen."*
- **No auto-confirmation.** PraxisMed does not auto-confirm appointments. Say so honestly.
- **Respect rate limits.** The build script is rate-limited. Do not modify it to send parallel requests.

---

## Legal note

This database was built from publicly available information on praxisplan.at, operated by
the Ärztekammer Wien.

All use must comply with:
- Austrian data protection law (DSG 2018)
- EU GDPR (DSGVO)
- The terms of service of praxisplan.at
- Applicable Austrian UWG provisions on B2B commercial outreach

This is a manual, individual B2B outreach tool. It is not an automated marketing system
and must never be used as one.

---

## Column guide

| Column | What to enter |
|---|---|
| Lead ID | Auto-assigned — do not change |
| Specialty Tier | 1, 2, or 3 (auto-set by script) |
| Specialty Key | Internal key (e.g. "dermatology") |
| Specialty Label DE | German specialty name |
| Specialty Label EN | English specialty name |
| Doctor Name | Full name as listed on Praxisplan |
| Title | Academic title |
| Practice Name | Practice name if known |
| Specialty | Specialty as listed on Praxisplan |
| Sub-specialty / Notes from Listing | Additional listing info |
| Address | Street address |
| Postal Code | Austrian postal code |
| City | City (usually Wien) |
| District | Vienna district |
| Phone | Practice phone (public) |
| Email | Practice email (public only) |
| Website | Practice website (public) |
| Praxisplan Profile URL | Direct Praxisplan link |
| Existing System Mentioned | Note if clinic mentions another system |
| Likely LATIDO / Online Booking | Unknown / Yes / No |
| Priority Score | 1–5 |
| Priority Reason | Why this score |
| Outreach Status | Use dropdown |
| Call Attempt 1/2 Date | YYYY-MM-DD |
| Call Attempt 1/2 Result | Use dropdown |
| Email Sent Date | YYYY-MM-DD |
| Email Result | Use dropdown |
| Walk-in Date | YYYY-MM-DD |
| Walk-in Result | Use dropdown |
| Contact Person | Person you spoke with |
| Best Time to Call | As noted by clinic |
| Follow-up Date | YYYY-MM-DD |
| Demo Offered | Yes / No |
| Demo Booked | Yes / No |
| Demo Date | YYYY-MM-DD |
| Pilot Interest | Unknown / Low / Medium / High / Not interested |
| Objection | Main objection raised |
| Next Action | What to do next |
| Notes | Free text — professional context only |
| Last Updated | YYYY-MM-DD |
