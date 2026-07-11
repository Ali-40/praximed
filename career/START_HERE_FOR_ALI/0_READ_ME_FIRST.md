# Job Application Copilot — Read Me First

**Vienna, July 2026**

---

## Daily target: 20–50 high-quality applications

Quality first. 20 strong, tailored applications beat 50 generic ones.

**Do not:**
- Send a generic letter
- Apply to jobs you do not qualify for
- Apply without reading the job description
- Apply automatically (no bots, no auto-submit)
- Fake experience or skills

---

## Recommended daily split

| Category | Count | Notes |
|---|---|---|
| Vienna full-time (Data/ML/Analytics) | 10 | Highest priority |
| Austria-wide full-time or internship | 10 | Strong fit only |
| Working student / Internship | 10 | If better than Hofer |
| Extra: fit score > 70 | 0–20 | If time allows |

---

## Daily workflow

### Morning (30 min)
1. Open `1_DAILY_JOB_PLAN.xlsx` — review today's target list
2. Run `python scripts/career/job_application_copilot.py --mode daily-plan --limit 30`
3. Open `career/job_search/daily_plans/YYYY-MM-DD_job_plan.md`
4. Check `3_TODAYS_APPLICATION_PACKETS/` — application packets are ready

### During the day
5. Review each application packet in `3_TODAYS_APPLICATION_PACKETS/`
6. Open the job URL and read carefully
7. Adjust the motivation letter — never send template as-is
8. Select correct CV: `Ali_Abdeltawab_CV_EN_ATS.md` or `Ali_Abdeltawab_CV_DE_ATS.md`
9. Submit manually on the company portal
10. Update `2_APPLICATION_TRACKER.xlsx` after each application

### Evening (15 min)
11. Run `python scripts/career/job_application_copilot.py --mode report`
12. Note any replies received
13. Update follow-up dates for applications sent

---

## Files in this folder

| File | When to use |
|---|---|
| `0_READ_ME_FIRST.md` | This file — overview |
| `1_DAILY_JOB_PLAN.xlsx` | Today's application plan |
| `2_APPLICATION_TRACKER.xlsx` | Track all applications |
| `3_TODAYS_APPLICATION_PACKETS/` | Ready-to-review application packets |
| `4_CV_AND_LINKEDIN_ACTIONS.md` | CV and LinkedIn action checklist |
| `5_MANUAL_SUBMISSION_GUIDE.md` | Step-by-step manual submission guide |

---

## Other career folders

| Folder | Purpose |
|---|---|
| `career/cv/` | ATS CV drafts (English + German) |
| `career/linkedin/` | LinkedIn profile rewrite + step-by-step |
| `career/github/` | GitHub profile README + repo recommendations |
| `career/templates/` | Motivation letter templates (EN + DE) |
| `career/job_search/` | Job tracker, daily plans, application packets |

---

## CV to use

- German job, German company: `career/cv/Ali_Abdeltawab_CV_DE_ATS.md` → convert to PDF
- English job, international company: `career/cv/Ali_Abdeltawab_CV_EN_ATS.md` → convert to PDF

---

## Rules (never break)

- No auto-apply
- No auto-email
- No LinkedIn automation
- No fake claims
- No invented experience
- Mark every application in the tracker
- Follow up after 7–10 days if no reply
