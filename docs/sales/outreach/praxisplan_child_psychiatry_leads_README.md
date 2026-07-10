# Praxisplan Child Psychiatry Leads — README

**Purpose:** Manual B2B outreach tracker for PraxisMed sales.
**Source:** Public listings on [praxisplan.at](https://www.praxisplan.at)
**Specialty:** Kinder- u. Jugendpsychiatrie u. Psychotherapeutische Medizin (specialization=71)
**Created:** 2026-07-10

---

## Files in this folder

| File | Description |
|---|---|
| `praxisplan_child_psychiatry_leads.xlsx` | Live scrape — real public listings. Use this for outreach. |
| `praxisplan_child_psychiatry_leads.csv` | Same data as CSV for filtering/import. |
| `praxisplan_child_psychiatry_leads_template.xlsx` | Empty template with 5 fake example rows. Use to understand column structure. |
| `praxisplan_child_psychiatry_leads_template.csv` | Same template as CSV. |
| `praxisplan_child_psychiatry_leads_README.md` | This file. |

---

## How to rebuild the database

```bash
# Full live scrape (no profile enrichment — fast):
python scripts/sales/build_praxisplan_lead_database.py \
    --url "https://www.praxisplan.at/suche?name=&specialization=71&zip=&gender=&diploma=&specialty=&insurance=&vaccine=&locale=" \
    --output docs/sales/outreach/praxisplan_child_psychiatry_leads.xlsx \
    --no-enrich

# Full live scrape WITH profile enrichment (slower — attempts to collect website URLs):
python scripts/sales/build_praxisplan_lead_database.py \
    --url "https://www.praxisplan.at/suche?name=&specialization=71&zip=&gender=&diploma=&specialty=&insurance=&vaccine=&locale="

# From a locally saved HTML page (Mode B — no network required):
python scripts/sales/build_praxisplan_lead_database.py \
    --input-html docs/sales/outreach/praxisplan_saved_page.html \
    --output docs/sales/outreach/praxisplan_child_psychiatry_leads.xlsx

# Template only (no network):
python scripts/sales/build_praxisplan_lead_database.py --template-only
```

---

## What data this contains

Only **publicly visible practice contact details** from Praxisplan.at:

- Doctor name and title (as shown publicly on Praxisplan)
- Specialty listed on Praxisplan
- Ordination address (as listed publicly)
- Phone number (as listed publicly)
- Praxisplan profile URL
- Website URL (if visible on the public profile page)
- Email (only if displayed visibly as a mailto link on the public profile or practice website)

**This does NOT contain:**
- Private email addresses
- Patient data of any kind
- Medical records or health information
- Personal phone numbers (only practice/ordination lines)
- Data obtained by bypassing any login, paywall, or captcha
- Data from non-public sources

---

## How to use this tracker

1. Open `praxisplan_child_psychiatry_leads.xlsx`
2. Use the **Outreach Status** dropdown column to track where each lead is
3. Log each call attempt in **Call Attempt 1 Date** / **Call Attempt 1 Result**
4. Log emails in **Email Sent Date** / **Email Result**
5. Log walk-ins in **Walk-in Date** / **Walk-in Result**
6. Set **Demo Offered**, **Demo Booked**, **Pilot Interest** as you progress
7. If a clinic asks not to be contacted again: set **Outreach Status = Do not contact**
8. Use **Notes** for anything that doesn't fit the structured columns
9. Update **Last Updated** whenever you make contact

---

## Priority Scores

| Score | Meaning |
|---|---|
| 5 | Strong target — phone + email/website + Vienna + high callback specialty |
| 4 | Good target — phone + Vienna, or email available |
| 3 | Average — Vienna, some contact info, needs review |
| 2 | Weaker — missing phone or not in Vienna |
| 1 | Low priority — very limited public contact info |

---

## Responsible outreach rules

- **Public contacts only.** Use only the phone numbers and emails listed publicly on Praxisplan or the practice's own public website.
- **No mass-emailing.** Do not send automated bulk emails. All outreach is individual and manual.
- **No auto-calling.** Do not use auto-dialers. Each call is a manual, personal call.
- **Respect opt-outs.** If a clinic says they are not interested or asks not to be contacted again, immediately set **Outreach Status = Do not contact** and do not contact them again.
- **No patient data.** This tracker is for practice contact information only. Never record patient names, health data, appointment records, or any PHI here.
- **No PHI.** Production PHI is NO-GO. This is a sales lead tracker, not a product database.
- **No medical claims.** Do not make medical claims, clinical decision support claims, or diagnostic claims when pitching PraxisMed.
- **No DSGVO overclaims.** Do not promise full DSGVO compliance without legal review. Say: "Wir legen großen Wert auf Datenschutz — gerne schicken wir Ihnen unsere Datenschutzunterlagen."
- **Professional notes only.** The Notes column is for outreach context (e.g. "Reception said to call back Thursday"). Never write negative personal comments about clinic staff.
- **Keep data current.** Remove or mark leads that have closed, moved, or explicitly opted out.

---

## Legal note

This database was built from publicly available information on praxisplan.at, a public doctor listing service operated by the Ärztekammer Wien.

All use of this data must comply with:
- Austrian data protection law (DSG 2018)
- EU GDPR (DSGVO)
- The robots.txt and terms of service of praxisplan.at
- Applicable UWG (Gesetz gegen den unlauteren Wettbewerb) provisions on commercial outreach

This tracker is for **manual, individual B2B outreach to medical practices** only.
It is not an automated marketing tool and must not be used as one.

---

## Column guide

| Column | What to enter |
|---|---|
| Lead ID | Auto-assigned. Do not change. |
| Doctor Name | Full name as listed on Praxisplan. |
| Title | Academic title (Dr., Prof. Dr., etc.) |
| Practice Name | Practice name if known (leave blank if same as doctor name) |
| Specialty | Specialty as listed on Praxisplan |
| Sub-specialty / Notes from Listing | Additional specialty info or ordination notes |
| Address | Street address |
| Postal Code | Austrian postal code |
| City | City (usually Wien) |
| District | Vienna district (inferred from postal code) |
| Phone | Practice phone number (public) |
| Email | Practice email (public only) |
| Website | Practice website (public) |
| Praxisplan Profile URL | Direct link to Praxisplan listing |
| Source URL | The search URL that produced this listing |
| Source | Always "Praxisplan" |
| Existing System Mentioned | Note if clinic mentions another booking system |
| Likely LATIDO / Online Booking | Unknown / Yes / No — does the practice likely already use LATIDO or an online booking tool? |
| Priority Score | 1–5 (5 = highest priority) |
| Priority Reason | Short reason for score |
| Outreach Status | Use dropdown |
| Call Attempt 1/2 Date | Date of call (YYYY-MM-DD) |
| Call Attempt 1/2 Result | Use dropdown |
| Email Sent Date | Date email was sent |
| Email Result | Use dropdown |
| Walk-in Date | Date of walk-in visit |
| Walk-in Result | Use dropdown |
| Contact Person | Name of person you spoke with (reception, doctor, etc.) |
| Best Time to Call | Time preference noted by clinic |
| Follow-up Date | When to follow up |
| Demo Offered | Yes / No |
| Demo Booked | Yes / No |
| Demo Date | Scheduled demo date |
| Pilot Interest | Unknown / Low / Medium / High / Not interested |
| Objection | Main objection raised |
| Next Action | What you plan to do next |
| Notes | Free text |
| Last Updated | Date you last updated this row |
