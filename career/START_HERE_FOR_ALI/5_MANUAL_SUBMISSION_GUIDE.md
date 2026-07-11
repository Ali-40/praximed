# Manual Submission Guide

**Every application is submitted manually. No automation.**

---

## Step-by-step submission process

### 1. Open the application packet
Go to: `career/job_search/application_packets/YYYY-MM-DD_company_role/`

Open all 5 files:
- `00_JOB_SUMMARY.md` — read the job summary
- `01_FIT_SCORE.md` — check your fit score and fit reason
- `02_TAILORED_CV_BULLETS.md` — review CV tailoring suggestions
- `03_MOTIVATION_LETTER.md` — read the draft letter
- `04_APPLICATION_CHECKLIST.md` — follow the checklist

### 2. Read the original job posting
Open the job URL from `00_JOB_SUMMARY.md`.
Read every section. Note: required vs. nice-to-have skills.

### 3. Tailor the motivation letter
Open `03_MOTIVATION_LETTER.md`.
Replace every {{PLACEHOLDER}} with real content specific to this job.
The letter must be specific. If it reads like a template, fix it.

### 4. Select the correct CV
- German posting → use DE CV: `career/cv/Ali_Abdeltawab_CV_DE_ATS.pdf`
- English posting → use EN CV: `career/cv/Ali_Abdeltawab_CV_EN_ATS.pdf`
- If you tailored CV bullets, apply them first and regenerate PDF

### 5. Check the company name in all documents
Search and verify: company name, job title, date, and your email are correct.

### 6. Go to the company's job portal
Open the application URL. Do not use third-party apply buttons that auto-fill.
Use the company's own portal.

### 7. Upload documents manually
- CV: upload PDF
- Cover letter / motivation letter: upload as PDF or paste in text box
- If they ask for GitHub or LinkedIn: https://github.com/Ali-40 / LinkedIn URL

### 8. Work authorization question (if asked)
Answer honestly:
> "I am currently based in Vienna with a student residence permit and am looking for a full-time role where the employment contract can support the appropriate Austrian work/residence route, such as Rot-Weiß-Rot (RWR) where applicable."

Do not fabricate citizenship or work authorization status.

### 9. Review before submitting
- [ ] Company name is correct
- [ ] Job title is correct
- [ ] CV version is correct (EN or DE)
- [ ] Motivation letter has no placeholder text remaining
- [ ] Your contact details are correct
- [ ] No false claims
- [ ] You have actually read the job description

### 10. Submit
Click submit on the company portal.
Do NOT use auto-apply services.

### 11. Update the tracker immediately
Open `2_APPLICATION_TRACKER.xlsx` or run:
```
python scripts/career/job_application_copilot.py --mode report
```
Update:
- Application Status → Applied
- Applied Date → today
- Follow-up Date → 7–10 days from now
- Notes → any important details (contact name, specific instructions, etc.)

---

## Where to find jobs (manual search only)

**Austrian job boards (public, no login required for search):**
- karriere.at — main Austrian job board
- stepstone.at — large Austrian/German job board
- jobs.at — Austrian jobs
- monster.at

**German job boards (for remote/hybrid Germany roles):**
- stepstone.de
- indeed.de
- linkedin.com/jobs (search only, no automation)

**Company career pages (direct):**
Search: "{{Company Name}} Karriere" or "{{Company Name}} Jobs"
Apply directly on the company portal — avoids recruiter middleman.

**LinkedIn:**
Search manually. Save job links to `career/job_search/saved_job_links.csv`.
Do NOT automate LinkedIn in any way.

---

## Follow-up after application

Wait 7–10 business days.
If no reply:
1. Find the recruiter or hiring manager on LinkedIn (manual search)
2. Check packet `05_LINKEDIN_MESSAGE_IF_USEFUL.md` for message template
3. Send a short, professional message — one message only
4. Update tracker: Follow-up Date, Follow-up Status

---

## What NOT to do

- Do NOT use Easy Apply bots or auto-apply browser extensions
- Do NOT send the same generic letter to every company
- Do NOT apply to jobs requiring skills you do not have
- Do NOT claim Austrian citizenship or EU citizenship if you do not have it
- Do NOT send applications automatically
- Do NOT email mass applications
- Do NOT use AI to bulk-generate and bulk-submit
