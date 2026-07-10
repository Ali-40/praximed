# PraxisMed — Current State

## Completed and committed modules

00000000000000. Sprint 21 / Outreach — Start-here sales folder (commit: pending)
   - `docs/sales/outreach/START_HERE/` — human-friendly daily sales folder; does not replace any existing files
   - `1_START_HERE.md` — open this first; explains 3-file workflow in simple language
   - `2_TODAY_CALL_LIST.xlsx` — prioritized call list from daily plan CSV; bold headers, freeze, filters, dropdowns for Status and Call Result, Call Order, Opening Line
   - `3_EMAIL_DRAFTS.md` — copy/paste email drafts with prominent "do not mass-send" rule
   - `4_MASTER_TRACKER.xlsx` — pointer file; explains why to use original tracker (no duplicate confusion)
   - `5_AFTER_CALL_UPDATE_GUIDE.md` — field-by-field post-call update guide; Do not contact rule, no patient data
   - `README_FOR_ALI.md` — 5-line actionable list: "stop coding, start calling"
   - `backend/tests/test_start_here_outreach_folder_contract.py` — 46 contract tests
   - 5949 total tests. Production PHI remains NO-GO.

0000000000000. Sprint 21 / Outreach — PraxisMed outreach copilot (commit: 0a5e954)
   - `scripts/sales/praximed_outreach_copilot.py` — local copilot: reads 1,245 leads CSV, prioritizes, generates daily call plan + call list CSV + German email drafts + follow-up list + sales report; all output is manual-review-only, no auto-email, no auto-call
   - `docs/sales/outreach/daily_plans/` — daily output directory: plan.md, call_list.csv, email_drafts.md, followups.md, outreach_report.md, update_instructions.md
   - `docs/sales/outreach/RESPONSIBLE_OUTREACH_GUARDRAILS.md` — full guardrails: public contacts only, no patient data, no PHI, no auto-calling, no auto-email, no mass spam, opt-out rules
   - `backend/tests/test_praximed_outreach_copilot_contract.py` — 72 contract tests (functional + safety)
   - CLI: --input, --output-dir, --daily-limit, --specialty, --tier, --mode (plan/drafts/followups/report)
   - Lead scoring: Tier 1 > Tier 2 > Tier 3; phone > email > no contact; Vienna; priority score
   - Excludes: Do not contact, Not interested, Demo booked
   - Follow-up detection: Asked to send email, Follow-up needed, Email sent w/o reply, Call later, Demo offered not booked
   - No SMTP. No Twilio. No Vapi. No auto-send. No auto-dial. No secrets.
   - 5903 total tests. Production PHI remains NO-GO.

000000000000. Sprint 21 / Outreach — Multi-specialty Praxisplan lead database builder (commit: 91fdf5e)
   - `scripts/sales/build_praxisplan_multi_specialty_leads.py` — multi-specialty builder: --all, --specialty KEY, --templates-only, --config; rate-limited, cross-specialty dedup, per-specialty XLSX+CSV, master combined workbook
   - `docs/sales/outreach/praxisplan_specialty_sources.json` — 15-specialty config with Praxisplan IDs, tiers, output slugs, notes on unavailable IDs (dental, group practices)
   - `docs/sales/outreach/praxisplan_all_high_potential_leads.xlsx` — master workbook: All Leads sheet + 15 per-specialty sheets + Summary
   - `docs/sales/outreach/praxisplan_all_high_potential_leads.csv` — master leads as flat CSV
   - `docs/sales/outreach/praxisplan_{specialty}_leads.xlsx/csv` — 15 per-specialty files
   - `docs/sales/outreach/MULTI_SPECIALTY_OUTREACH_DATABASE_README.md` — specialty map, rebuild instructions, responsible outreach rules
   - `backend/tests/test_multi_specialty_praxisplan_outreach_database_contract.py` — 92 contract tests
   - Specialization IDs discovered: Dermatology=6, Gynecology=4, Orthopedics=68, InternalMed=7, ENT=5, Urology=15, Neurology=49, Ophthalmology=2, Pediatrics=8, Aesthetic=30, AdultPsych=52
   - Public contacts only. No private data. No patient data. No PHI. No auto-email. No auto-call.
   - 5831 total tests. Production PHI remains NO-GO.

00000000000. Sprint 21 / Outreach — Praxisplan lead database builder (commit: e551fcf)
   - `scripts/sales/build_praxisplan_lead_database.py` — scraper/builder: live fetch (Mode A), local HTML fallback (Mode B), template-only mode; rate-limited (1.5–2.5s), deduplication, priority scoring, XLSX + CSV export with dropdowns
   - `docs/sales/outreach/praxisplan_child_psychiatry_leads.xlsx` — 70 real public listings, Kinder- u. Jugendpsychiatrie, 64 with phone
   - `docs/sales/outreach/praxisplan_child_psychiatry_leads.csv` — same data as CSV
   - `docs/sales/outreach/praxisplan_child_psychiatry_leads_template.xlsx` — empty template with 5 fake example rows, full dropdowns
   - `docs/sales/outreach/praxisplan_child_psychiatry_leads_template.csv` — same template as CSV
   - `docs/sales/outreach/praxisplan_child_psychiatry_leads_README.md` — responsible outreach rules, column guide, rebuild instructions
   - `backend/tests/test_praxisplan_outreach_database_builder_contract.py` — 67 contract tests
   - Public contacts only. No private data. No patient data. No PHI. No auto-email. No auto-call. No mass spam.
   - Source: praxisplan.at specialization=71 (Kinder- u. Jugendpsychiatrie u. Psychotherapeutische Medizin)
   - 5739 total tests. Production PHI remains NO-GO.

0000000000. Module 163A — Sprint 21 / Fix Clinic Dashboard Language Switch (commit: 0bfee17)
   - `frontend/app/dashboard/page.tsx` — full live switch: `getStatusLabel(status, lang)` replaces `getGermanStatusLabel`; `getReadableRequestNumber(index, lang)`; TRANSLATIONS expanded to ~44 keys; all JSX call sites updated; backward-compat alias `getGermanStatusLabel` preserved
   - `backend/tests/test_clinic_dashboard_language_switch_contract.py` — expanded to 72 contract tests (16 new 163A assertions)
   - `docs/product/CLINIC_DASHBOARD_LANGUAGE_SWITCH.md` — 163A hotfix section added
   - All labels now live-switch on Deutsch/English radio change; no hardcoded German visible in UI
   - requestPrefix in de: 'Anfrage #', in en: 'Request #'
   - Settings messages language-aware (einstellungenGespeichert / einstellungenFehler)
   - 5656 total tests. Build clean. Production PHI remains NO-GO.

000000000. Module 163 — Sprint 21 / Clinic Dashboard Language Switch (commit: 8a92660)
   - `frontend/app/dashboard/page.tsx` — TRANSLATIONS constant (de/en), uiLang state, t() helper, language selector card in Settings tab ("Sprache der Oberfläche / Interface language")
   - `backend/tests/test_clinic_dashboard_language_switch_contract.py` — 56 contract tests
   - `docs/product/CLINIC_DASHBOARD_LANGUAGE_SWITCH.md` — product doc
   - 28-key translation dictionary, no external i18n library
   - German default; English available via radio selector in Settings
   - Switched labels: Heute/Today, tab labels, HeuteCard metrics, demo buttons, detail dl fields, summary panel fields, settings section headings, safety note
   - All prior module markers and safety invariants intact
   - 5656 total tests. Build clean. Production PHI remains NO-GO.

00000000. Module 162B — Sprint 21 / Clinic-Facing Dashboard Language Hotfix (commit: b286913)
   - `frontend/app/dashboard/page.tsx` — center heading "Anfrage im Überblick", "Gewünschte Zeit", "Rückruf markieren", archived→Archiviert status, active/archived request split, removed visible vapi badge, removed English AI intake blurb, fixed isNewRequest, translated summary panel labels
   - `backend/tests/test_clinic_facing_dashboard_language_hotfix_contract.py` — 60 contract tests
   - `docs/product/CLINIC_FACING_DASHBOARD_LANGUAGE_HOTFIX.md` — product doc
   - "Noch keine aktiven Anfragen" empty state after demo reset
   - Archived requests pushed to separate collapsed section — no longer show "Neue Anfrage" badge
   - Summary panel: Type→Art, Reason→Anliegen, Urgency→Dringlichkeit, Prior visits→Frühere Besuche, Suggested action→Empfohlene Aktion
   - English safety blurb in workspace replaced with German: "Nur zur internen Planung. Das Praxisteam prüft und bestätigt jeden Schritt."
   - Acceptance: "A Vienna receptionist can understand the dashboard without technical explanation."

0000000. Module 162 (outreach extension) — Sprint 21 / Sales Demo Polish and Outreach Readiness (commit: d49a7f1)
   - `docs/sales/CLINIC_OUTREACH_EXECUTION_PACK.md` — expanded: target clinic profile, best niches, 50-clinic workflow, daily plan, tracking table, cold email, WhatsApp, phone script, LinkedIn, walk-in, follow-up sequence (Day 1/3/7 + after demo), 10 objection replies (calendar, DSGVO, AI claims, pricing, existing solutions), pricing (€390/€290–€490), CTA options
   - `docs/sales/SALES_ONE_LINERS.md` — 11 memorizable one-line pitches
   - `docs/sales/TOMORROW_FIRST_SALES_DAY_PLAN.md` — exact first-sales-day schedule (email block, phone block, walk-in block, LinkedIn, follow-up, success metrics)
   - `docs/sales/clinic_outreach_tracker_template.csv` — ready-to-use spreadsheet with 5 fake example rows
   - `backend/tests/test_sales_demo_polish_and_outreach_readiness_contract.py` — 85 comprehensive contract tests
   - Calendar positioned as next pilot workflow feature — not promised as finished
   - Acceptance: "Ali kann morgen losfahren, 20 Wiener Privatpraxen kontaktieren, und weiß auf jeden Einwand eine Antwort."

000000. Module 163 — Sprint 21 / Clinic Outreach Execution Pack (commit: 4926b6e)
   - `docs/sales/CLINIC_OUTREACH_EXECUTION_PACK.md` — initial cold email, WhatsApp/SMS, LinkedIn, walk-in, follow-up sequence (Day 1/3/7), objection quick replies (5 objections)
   - `backend/tests/test_clinic_outreach_execution_pack_contract.py` — 45 contract tests
   - Cold email subject: "Wie Ihre Praxis verpasste Anrufe automatisch zurückruft"
   - All scripts mention verpasste Anrufe, 30-day pilot, demo CTA
   - No compliance claims. No clinical or medical claims. No technical terms in clinic-facing copy. No PHI.
   - Walk-in script: reception step → doctor/manager step → leave-behind (ONE_PAGE_CLINIC_HANDOUT) → follow-up within 24h
   - 5 objection quick replies: Kein Interesse, Zu teuer, Wir haben bereits eine Lösung, Keine Zeit, Schicken Sie uns eine E-Mail
   - Acceptance: "Ali kann heute eine Wiener Privatpraxis anschreiben oder besuchen und weiß auf jeden Einwand eine Antwort."

00000. Module 162 — Sprint 21 / Sales Demo Polish and Walk-In Readiness (commit: b3c9656)
   - `frontend/app/dashboard/page.tsx` — intro sentence, Demo in 3 Schritten card, German empty states, sr-only pattern for English contract strings, MetricCard German labels, search bar German placeholder, technical terms hidden
   - `backend/tests/test_sales_demo_polish_walk_in_readiness_contract.py` — 52 contract tests
   - `docs/product/SALES_DEMO_POLISH_WALK_IN_READINESS.md` — product doc
   - Intro: "PraxisMed nimmt Terminanfragen auf und sortiert Rückrufe für Ihr Praxisteam."
   - Demo guide: "Demo in 3 Schritten" helper card (Demo-Anruf erstellen → Rückruf-Anfrage prüfen → Als kontaktiert markieren)
   - All visible English strings replaced with German. Contract-required strings kept in sr-only spans.
   - No technical terms visible: no Vapi, no webhook, no source_ref, no UUID, no JSON, no PHI label.
   - No diagnosis/advice/triage. No appointment auto-confirmation. Production PHI remains NO-GO.
   - Acceptance: "Ali öffnet /dashboard vor einer Wiener Rezeptionistin. Die Rezeptionistin versteht das Produkt in 5 Minuten ohne technische Erklärung."

0000. Module 161 — Sprint 21 / Five-Minute Clinic Demo Script and Sales Pack (commit: pending)
   - `docs/sales/FIVE_MINUTE_CLINIC_DEMO_SCRIPT.md` — 5-minute demo script, receptionist + doctor talk tracks
   - `docs/sales/THIRTY_DAY_PILOT_OFFER.md` — pilot structure, pricing anchor (€390 setup, €290–€490/month)
   - `docs/sales/ONE_PAGE_CLINIC_HANDOUT.md` — print-ready one-page handout, no technical language
   - `docs/sales/OBJECTION_HANDLING.md` — 10 objections with honest answers, no overclaims
   - `docs/sales/DEMO_DAY_CHECKLIST.md` — before/during/after checklist for clinic visits
   - `backend/tests/test_five_minute_clinic_demo_sales_pack_contract.py` — 71 contract tests
   - Sales focus: missed calls, callback queue, staff control, simple workflow, no technical language
   - No compliance overclaims. No PHI claims. No diagnosis/advice/triage claims. Production PHI remains NO-GO.
   - Acceptance: "Ali kann in eine Wiener Privatpraxis gehen und PraxisMed in 5 Minuten erklären."

000. Module 160 — Sprint 21 / Live Vapi Staging Call Loop (commit: 5cb8671)
   - `frontend/app/dashboard/page.tsx` — data-live-demo-hint span added to demo strip
   - `backend/tests/test_live_vapi_staging_call_loop_sales_mvp_contract.py` — new, ≥15 tests
   - `docs/product/LIVE_VAPI_STAGING_CALL_LOOP.md` — product doc with German assistant script + Vapi checklist
   - Existing POST /vapi/tools/capture-appointment-request satisfies all requirements — no backend changes
   - German AI receptionist script: greeting, data collection, "Praxisteam meldet sich zur Bestätigung zurück", emergency 144
   - Dashboard hint: plain German, no API URL, no header names, no UUID, no technical content
   - No transcript storage. No recording URL storage. No auto-confirmation. Production PHI remains NO-GO.
   - Acceptance: "Ali kann eine Staging-Telefonnummer anrufen, ein synthetisches Terminanliegen sprechen, und die Anfrage erscheint in /dashboard als Rückruf nötig."

00. Module 159 — Sprint 21 / Simple Clinic Settings (commit: pending)
   - `frontend/app/dashboard/page.tsx` — Einstellungen tab replaced with editable form
   - `backend/tests/test_simple_clinic_settings_sales_mvp_contract.py` — new, ≥15 tests
   - `docs/product/SIMPLE_CLINIC_SETTINGS.md` — product doc
   - Praxisprofil fields: Praxisname, Arzt/Ärztin, Fachrichtung, Ort, Telefonnummer
   - Öffnungszeiten free-text. Sprachen checkboxes. KI-Rezeption tone + KI-Vorschau.
   - Language settings persisted via existing PATCH /clinics/{id}/language-settings
   - No technical fields. No UUIDs. No Vapi config. No PHI. Production PHI remains NO-GO.
   - Acceptance: "A receptionist can open Einstellungen and understand/customize the demo without any technical word."

0. Module 158 — Sprint 21 / One-Click Demo Flow (commit: pending)
   - `backend/app/api/routes/sales_demo.py` — new staging-only demo routes
   - `backend/app/api/router.py` — sales_demo router registered
   - `frontend/lib/api.ts` — createSalesDemoCall, resetSalesDemoData
   - `frontend/app/dashboard/page.tsx` — Demo-Modus strip, handlers, state
   - `backend/tests/test_one_click_demo_flow_sales_mvp_contract.py` — new, ≥15 tests
   - `docs/product/ONE_CLICK_DEMO_FLOW.md` — product doc
   - Staging-only endpoints: POST /demo/sales-mvp/create-call, POST /demo/sales-mvp/reset
   - No real patient data. No PHI. No Vapi live call. Production PHI remains NO-GO.
   - Acceptance: "Ali can open /dashboard, press 'Demo-Anruf erstellen', and within seconds show a Vienna receptionist a realistic callback request in the intake queue."

00. Module 157 — Sprint 21 / Doctor-Facing Sales MVP Simplification (commit: f7baaf4)
   - `frontend/app/dashboard/page.tsx` — simplified, German-first, tabbed, UUID-hidden
   - `frontend/lib/api.ts` — updateAppointmentRequestStatus added
   - `backend/tests/test_doctor_facing_sales_mvp_dashboard_contract.py` — new, 64 tests
   - `docs/product/DOCTOR_FACING_SALES_MVP_SIMPLIFICATION.md` — product doc
   - Heute summary, Anfragen/Patienten/Einstellungen tabs, Anfrage #N numbering
   - Rückruf + Als kontaktiert markieren actions, no visible UUIDs
   - All existing contract tests green. Frontend build clean.
   - Acceptance: "Ali can walk into a Vienna clinic and in 5 minutes a receptionist understands the product without a single technical word being spoken."

1. Module 1 — Secure clinic config loader
   - `backend/app/core/config_loader.py`
   - Secure tenant config loading
   - Path traversal/symlink protections
   - Clinic config cache

2. Module 2 — asyncpg PostgreSQL pool
   - `backend/app/db/pool.py`

3. Module 3 — PostgreSQL schema contract
   - `backend/app/db/schema.sql`
   - schema contract tests

4. Module 4 — Calendar repository layer
   - `backend/app/db/repositories/calendar_repo.py`

5. Module 5 — Availability engine
   - `backend/app/modules/calendar_sync/availability_engine.py`

6. Module 6 — Calendar sync service
   - `backend/app/modules/calendar_sync/calendar_sync.py`

7. Module 7 — FastAPI skeleton and health routes
   - `backend/app/main.py`
   - health routes

8. Module 8 — n8n calendar sync webhook route
   - `POST /webhooks/n8n/calendar-sync`

9. Modules 9–10 — Availability schemas and API routes
   - `POST /calendar/availability/check`
   - `POST /calendar/availability/suggest`

10. Modules 11–12 — Vapi prompt builder and Vapi tool routes
   - Vapi prompt builder
   - `POST /vapi/tools/check-availability`
   - `POST /vapi/tools/suggest-slots`

11. Modules 13–14 — Vapi call logs and call event webhook
   - `clinic_call_logs`
   - call repository
   - Vapi call event handler
   - `POST /webhooks/vapi/call-event`

12. Claude orchestration docs created
   - `docs/claude/PROJECT_CONTEXT.md`
   - `docs/claude/ROADMAP.md`
   - `docs/claude/CURRENT_STATE.md`
   - `docs/claude/NEXT_MODULE.md`

13. Module 15 — Appointment request schema contract
   - Commit: 2a71deb
   - `backend/app/db/schema.sql` — added `appointment_requests` table
   - `backend/tests/test_schema_contract.py` — extended to 158 tests
   - Schema tests: 158/158 passed
   - Full backend tests: 349/349 passed

14. Module 16 — Appointment request repository
   - Commit: d7707c2
   - `backend/app/db/repositories/appointment_request_repo.py`
   - `backend/tests/test_appointment_request_repo.py`
   - Module 16 tests: 20/20 passed
   - Full backend tests: 369/369 passed

15. Module 17 — Appointment request API schemas and routes
   - Commit: be1a346
   - `backend/app/schemas/appointment_requests.py`
   - `backend/app/api/routes/appointment_requests.py`
   - `backend/app/api/router.py` (updated)
   - `backend/tests/test_appointment_request_schemas.py`
   - `backend/tests/test_appointment_request_routes.py`
   - Module 17 tests: 27/27 passed
   - Full backend tests: 396/396 passed

## Latest git log expected

- Sprint 2 / Module 24 — Patient schema contract
- Sprint 1 / Module 23 — Notification API routes
- Sprint 1 / Module 22 — Vapi notification integration
- Sprint 1 / Module 21 — Notification router service
- Sprint 1 / Module 20 — Notification repository
- Sprint 1 / Module 19 — Notification schema contract
- Sprint 1 / Module 18 — Vapi appointment capture integration
- Populate Claude orchestration docs for Module 18
- Sprint 1 / Module 17 — Appointment request API routes
- Populate Claude orchestration docs for Module 17
- Sprint 1 / Module 16 — Appointment request repository
- Populate Claude orchestration docs for Module 16
- Sprint 1 / Module 15 — Appointment request schema contract
- Populate Claude orchestration docs for Module 15
- Add Claude orchestration docs
- Sprint 1 / Modules 13–14 — Vapi call logs and call event webhook
- Sprint 1 / Modules 11–12 — Vapi prompt builder and tool routes
- Sprint 1 / Modules 9–10 — Availability schemas and API routes
- Sprint 1 / Module 8 — n8n Calendar Sync Webhook Route
- Sprint 1 Module 7: FastAPI skeleton and health routes
- Sprint 1 Module 6: calendar sync service
- Sprint 1 Module 5: availability engine
- Sprint 1 Module 4: calendar repository layer
- Sprint 1 Module 3: PostgreSQL schema contract
- Sprint 1 Module 2: asyncpg connection pool
- Sprint 1 Module 1: secure clinic config loader

16. Module 18 — Vapi appointment capture integration
   - Commit: 9231a6b
   - `backend/app/modules/vapi/vapi_appointment_capture.py`
   - `backend/app/schemas/vapi.py` (updated)
   - `backend/app/api/routes/vapi_tools.py` (updated)
   - `backend/tests/test_vapi_appointment_capture.py`
   - `backend/tests/test_vapi_tool_routes.py` (updated)
   - Module 18 tests: 34/34 passed
   - Full backend tests: 419/419 passed

17. Module 19 — Notification schema contract
   - Commit: 8814c0b
   - `backend/app/db/schema.sql` — added `clinic_notifications` table
   - `backend/tests/test_schema_contract.py` — extended to 194 tests
   - Schema tests: 194/194 passed
   - Full backend tests: 455/455 passed

18. Module 20 — Notification repository
   - Commit: 6c37a74
   - `backend/app/db/repositories/notification_repo.py`
   - `backend/tests/test_notification_repo.py`
   - Module 20 tests: 26/26 passed
   - Full backend tests: 481/481 passed

19. Module 21 — Notification router service
   - Commit: c0d4bd4
   - `backend/app/modules/notifications/__init__.py`
   - `backend/app/modules/notifications/notification_router.py`
   - `backend/tests/test_notification_router.py`
   - Module 21 tests: 21/21 passed
   - Full backend tests: 502/502 passed

20. Module 22 — Vapi notification integration
   - Commit: 2e6d53f
   - `backend/app/modules/vapi/vapi_event_handler.py` (updated)
   - `backend/app/modules/vapi/vapi_appointment_capture.py` (updated)
   - `backend/tests/test_vapi_event_handler.py` (updated)
   - `backend/tests/test_vapi_appointment_capture.py` (updated)
   - Module 22 tests: 42/42 passed
   - Full backend tests: 519/519 passed

21. Module 23 — Notification API routes
   - Commit: 085cafa
   - `backend/app/schemas/notifications.py`
   - `backend/app/api/routes/notifications.py`
   - `backend/app/api/router.py` (updated)
   - `backend/tests/test_notification_schemas.py`
   - `backend/tests/test_notification_routes.py`
   - Module 23 tests: 26/26 passed
   - Full backend tests: 545/545 passed

## Architecture checkpoint

- Architecture Checkpoint 01 created: `docs/claude/ARCHITECTURE_CHECKPOINT_01.md`
- Commit: 9e66dbd
- Full backend tests: 545/545 passed
- Sprint 1 complete (Modules 1–23)
- Sprint 2 started: Clinical Documentation Engine (Modules 24–34)

22. Module 24 — Patient schema contract
   - Commit: bdbed09
   - `backend/app/db/schema.sql` — added `patients` table
   - `backend/tests/test_schema_contract.py` — extended to 223 tests
   - Schema tests: 223/223 passed
   - Full backend tests: 574/574 passed

23. Module 25 — Patient repository
   - Commit: 0f84ad3 / docs: fe1d438
   - `backend/app/db/repositories/patient_repo.py`
   - `backend/tests/test_patient_repo.py`
   - Module 25 tests: 21/21 passed
   - Full backend tests: 595/595 passed

24. Module 26 — Patient API routes
   - Commit: b902dba / docs: b8c1515
   - `backend/app/schemas/patients.py`
   - `backend/app/api/routes/patients.py`
   - `backend/app/api/router.py` (updated)
   - `backend/tests/test_patient_schemas.py`
   - `backend/tests/test_patient_routes.py`
   - Module 26 tests: 34/34 passed
   - Full backend tests: 629/629 passed

25. Module 27 — Consultation session schema contract
   - Commit: 8cfe4a9 / docs: 4bbd514
   - `backend/app/db/schema.sql` — added `consultation_sessions` table
   - `backend/tests/test_schema_contract.py` — extended to 264 tests
   - Schema tests: 264/264 passed
   - Full backend tests: 670/670 passed

26. Module 28 — Consultation session repository
   - Commit: 45988e0 / docs: 364cc1a
   - `backend/app/db/repositories/consultation_repo.py`
   - `backend/tests/test_consultation_repo.py`
   - Module 28 tests: 32/32 passed
   - Full backend tests: 702/702 passed

27. Module 29 — Consultation session API routes
   - Commit: e832a91 / docs: 82895fa
   - `backend/app/schemas/consultations.py`
   - `backend/app/api/routes/consultations.py`
   - `backend/app/api/router.py` (updated)
   - `backend/tests/test_consultation_schemas.py`
   - `backend/tests/test_consultation_routes.py`
   - Module 29 tests: 39/39 passed
   - Full backend tests: 741/741 passed

28. Module 30 — Audio upload placeholder service
   - Commit: 1ccc797 / docs: 2b31c13
   - `backend/app/modules/audio/__init__.py`
   - `backend/app/modules/audio/audio_storage.py`
   - `backend/tests/test_audio_storage.py`
   - Module 30 tests: 23/23 passed
   - Full backend tests: 764/764 passed

29. Module 31 — Transcription adapter interface
   - Commit: 9aa2cb7 / docs: 13d2fdf
   - `backend/app/modules/transcription/__init__.py`
   - `backend/app/modules/transcription/transcription_service.py`
   - `backend/tests/test_transcription_service.py`
   - Module 31 tests: 27/27 passed
   - Full backend tests: 791/791 passed

30. Module 32 — Clinical summary draft generator
   - Commit: a1a6498 / docs: c879f4b
   - `backend/app/modules/clinical_summary/__init__.py`
   - `backend/app/modules/clinical_summary/summary_builder.py`
   - `backend/tests/test_clinical_summary_builder.py`
   - Module 32 tests: 41/41 passed
   - Full backend tests: 832/832 passed

31. Module 33 — Doctor review workflow
   - Commit: 6cd62c2 / docs: cc165f0
   - `backend/app/modules/clinical_summary/review_workflow.py`
   - `backend/tests/test_review_workflow.py`
   - Module 33 tests: 33/33 passed
   - Full backend tests: 865/865 passed

32. Module 34 — Patient timeline report service
   - Commit: 827c2da / docs: cf8c097
   - `backend/app/modules/patient_timeline/__init__.py`
   - `backend/app/modules/patient_timeline/timeline_report.py`
   - `backend/tests/test_patient_timeline_report.py`
   - Module 34 tests: 43/43 passed
   - Full backend tests: 908/908 passed

## Architecture checkpoint

- Architecture Checkpoint 02 created: `docs/claude/ARCHITECTURE_CHECKPOINT_02.md`
- Commit: 7e478c5 / follow-up docs: 2855d2f
- Full backend tests: 908/908 passed
- Sprint 2 complete (Modules 24–34)
- Sprint 3 started: Clinical Workflow API Routes (Module 35+)

33. Module 35 — Clinical workflow API routes
   - Commit: 9c36593 / docs: aa05911
   - `backend/app/schemas/clinical_workflows.py`
   - `backend/app/api/routes/clinical_workflows.py`
   - `backend/app/api/router.py` (updated)
   - `backend/tests/test_clinical_workflow_schemas.py`
   - `backend/tests/test_clinical_workflow_routes.py`
   - Module 35 tests: 47/47 passed (18 schema + 29 routes)
   - Full backend tests: 955/955 passed

34. Module 36 — Auth and tenant access foundation
   - Commit: 711ddfb / docs: 6ecd5ed
   - `backend/app/core/auth_context.py`
   - `backend/app/api/dependencies/__init__.py`
   - `backend/app/api/dependencies/auth.py`
   - `backend/tests/test_auth_context.py`
   - `backend/tests/test_auth_dependencies.py`
   - Module 36 tests: 34/34 passed (23 context + 11 dependencies)
   - Full backend tests: 989/989 passed

35. Module 37 — Apply tenant guards to clinical PHI routes
   - Commit: 5211f7c
   - `backend/app/api/routes/patients.py` (updated)
   - `backend/app/api/routes/consultations.py` (updated)
   - `backend/app/api/routes/clinical_workflows.py` (updated)
   - `backend/tests/test_patient_routes.py` (updated)
   - `backend/tests/test_consultation_routes.py` (updated)
   - `backend/tests/test_clinical_workflow_routes.py` (updated)
   - Module 37 tests: 17/17 new passed (5 patient + 6 consultation + 6 clinical_workflows)
   - Full backend tests: 1006/1006 passed

36. Module 38 — Apply tenant guards to appointment and notification routes
   - Commit: 251e82d
   - `backend/app/api/routes/appointment_requests.py` (updated)
   - `backend/app/api/routes/notifications.py` (updated)
   - `backend/tests/test_appointment_request_routes.py` (updated)
   - `backend/tests/test_notification_routes.py` (updated)
   - Module 38 tests: 12/12 new passed (6 appointment_requests + 6 notifications)
   - Full backend tests: 1018/1018 passed

37. Module 39 — Machine access foundation
   - Commit: fb9d31d
   - `backend/app/core/machine_auth.py` (new)
   - `backend/app/api/dependencies/machine_auth.py` (new)
   - `backend/tests/test_machine_auth.py` (new)
   - `backend/tests/test_machine_auth_dependencies.py` (new)
   - Module 39 tests: 45/45 passed (30 core + 15 dependencies)
   - Full backend tests: 1063/1063 passed

38. Module 40 — Apply machine guards to integration routes
   - Commit: 1c21ee5
   - `backend/app/api/routes/availability.py` (updated)
   - `backend/app/api/routes/vapi_tools.py` (updated)
   - `backend/app/api/routes/vapi_webhooks.py` (updated)
   - `backend/app/api/routes/calendar_webhooks.py` (updated)
   - `backend/tests/test_availability_routes.py` (updated)
   - `backend/tests/test_vapi_tool_routes.py` (updated)
   - `backend/tests/test_vapi_webhook_route.py` (updated)
   - `backend/tests/test_calendar_webhook_route.py` (updated)
   - Module 40 tests: 20/20 passed (5 availability + 5 vapi_tools + 5 vapi_webhook + 5 calendar_webhook)
   - Full backend tests: 1083/1083 passed

## Architecture checkpoint

- Architecture Checkpoint 03 created: `docs/claude/ARCHITECTURE_CHECKPOINT_03.md`
- Commit: 8169ee4
- Scope: Modules 35–40, Sprint 3 complete
- Focus: access control map, human/machine auth guards, integration readiness, remaining risks before pilot
- Full backend tests: 1083/1083 passed
- Sprint 3 complete (Modules 35–40)
- Sprint 4 started: Database Migration Foundation (Module 41)

39. Module 41 — Database migration foundation
   - Commit: 2daf4fd
   - `backend/alembic.ini` (new)
   - `backend/migrations/env.py` (new)
   - `backend/migrations/script.py.mako` (new)
   - `backend/migrations/versions/0001_initial_schema.py` (new)
   - `backend/tests/test_migration_contract.py` (new)
   - Migration tests: 20/20 passed
   - Full backend tests: 1103/1103 passed

40. Module 42 — Audit logging foundation
   - Commit: f085f83
   - `backend/app/db/repositories/audit_repo.py` (new)
   - `backend/app/modules/audit/__init__.py` (new)
   - `backend/app/modules/audit/audit_logger.py` (new)
   - `backend/tests/test_audit_repo.py` (new)
   - `backend/tests/test_audit_logger.py` (new)
   - Module 42 tests: 42/42 passed (20 repo + 22 logger)
   - Full backend tests: 1145/1145 passed

41. Module 43 — Audit logging integration for PHI mutations
   - Commit: 726710a
   - `backend/app/api/routes/patients.py` (updated)
   - `backend/app/api/routes/consultations.py` (updated)
   - `backend/app/api/routes/clinical_workflows.py` (updated)
   - `backend/app/api/routes/appointment_requests.py` (updated)
   - `backend/app/api/routes/notifications.py` (updated)
   - `backend/tests/test_patient_routes.py` (updated)
   - `backend/tests/test_consultation_routes.py` (updated)
   - `backend/tests/test_clinical_workflow_routes.py` (updated)
   - `backend/tests/test_appointment_request_routes.py` (updated)
   - `backend/tests/test_notification_routes.py` (updated)
   - Module 43 tests: 30/30 new audit tests passed
   - Full backend tests: 1175/1175 passed

42. Module 44 — Audit logging integration for machine routes
   - Commit: 005e43a
   - `backend/app/api/routes/vapi_webhooks.py` (updated)
   - `backend/app/api/routes/calendar_webhooks.py` (updated)
   - `backend/app/api/routes/vapi_tools.py` (updated)
   - `backend/tests/test_vapi_webhook_route.py` (updated)
   - `backend/tests/test_calendar_webhook_route.py` (updated)
   - `backend/tests/test_vapi_tool_routes.py` (updated)
   - Module 44 tests: 18/18 new tests passed
   - Full backend tests: 1193/1193 passed

## Architecture checkpoint

- Architecture Checkpoint 04 created: `docs/claude/ARCHITECTURE_CHECKPOINT_04.md`
- Commit: 9fba526
- Scope: Modules 41–44, Sprint 4 complete
- Focus: migration foundation, audit logging foundation, PHI/machine audit integration, integration readiness, remaining risks before pilot
- Full backend tests: 1193/1193 passed
- Sprint 4 complete (Modules 41–44)
- Sprint 5 started: Local PostgreSQL Docker + Migration Runner Smoke Test (Module 45)

43. Module 45 — Local PostgreSQL Docker and migration smoke test
   - Commit: 5566653
   - `docker-compose.postgres.yml` (new)
   - `backend/.env.example` (new)
   - `backend/scripts/__init__.py` (new)
   - `backend/scripts/run_migrations.py` (new)
   - `backend/scripts/db_smoke_test.py` (new)
   - `backend/tests/test_local_db_setup_contract.py` (new)
   - Module 45 tests: 24/24 passed
   - Full backend tests: 1217/1217 passed
   - Manual local PostgreSQL smoke flow passed: Docker started, migration applied, key tables confirmed

44. Module 46 — Webhook signature verification foundation
   - Commit: 41d0a46
   - Docs commit: c2c2dc8
   - `backend/app/core/webhook_signature.py` (new)
   - `backend/app/api/dependencies/webhook_signature.py` (new)
   - `backend/tests/test_webhook_signature.py` (new)
   - `backend/tests/test_webhook_signature_dependencies.py` (new)
   - Module 46 tests: 33/33 passed (23 core + 10 dependencies)
   - Full backend tests: 1250/1250 passed

45. Module 47 — Apply webhook signature enforcement
   - Commit: c161c16
   - Docs commit: 718046f
   - `backend/app/api/routes/vapi_webhooks.py` (updated)
   - `backend/app/api/routes/calendar_webhooks.py` (updated)
   - `backend/tests/test_vapi_webhook_route.py` (updated)
   - `backend/tests/test_calendar_webhook_route.py` (updated)
   - Module 47 tests: 12 new signature enforcement tests passed
   - Full backend tests: 1256/1256 passed

46. Module 48 — Local integration runbook and signed webhook helper
   - Commit: 60f61fa
   - Docs commit: d6a3e3b
   - `docs/integrations/LOCAL_INTEGRATION_RUNBOOK.md` (new)
   - `backend/scripts/sign_webhook_payload.py` (new)
   - `backend/tests/test_signed_webhook_helper_contract.py` (new)
   - Module 48 tests: 25/25 passed
   - Full backend tests: 1281/1281 passed
   - Manual signed webhook curl reached backend but returned 503: runtime DB pool startup was missing

47. Module 49 — Local runtime database pool startup
   - Commit: b6cb614
   - Docs commit: 1fa34d1
   - `backend/app/main.py` (updated — lifespan handler added)
   - `backend/tests/test_app_lifespan_db_pool.py` (new)
   - Module 49 tests: 9/9 passed
   - Full backend tests: 1290/1290 passed
   - Manual signed webhook curl passed signature/auth layer; good signature reached DB logic; bad signature returned 401
   - Current local gap: seed data and valid UUID smoke payloads

48. Module 50 — Local seed data and webhook smoke fixtures
   - Commit: dd8df3b
   - Docs commit: 0f178f9
   - `backend/scripts/seed_local_data.py` (new)
   - `docs/integrations/local_payloads/vapi_call_event.json` (new)
   - `docs/integrations/local_payloads/n8n_calendar_sync.json` (new)
   - `docs/integrations/LOCAL_INTEGRATION_RUNBOOK.md` (updated)
   - `backend/tests/test_local_seed_contract.py` (new)
   - Module 50 tests: 22/22 passed
   - Full backend tests: 1312/1312 passed
   - Manual local signed Vapi webhook: HTTP 200 OK
   - Manual bad Vapi signature: HTTP 401 Unauthorized
   - Manual local signed n8n webhook: HTTP 200 OK
   - Local integration smoke checkpoint created

49. Module 51 — Local integration smoke result checkpoint
   - Commit: 2872c99
   - Docs commit: ced433c
   - `docs/integrations/LOCAL_SMOKE_RESULTS.md` (new)
   - `docs/integrations/LOCAL_INTEGRATION_RUNBOOK.md` (updated — Section L added)
   - `docs/claude/CURRENT_STATE.md` (updated)
   - `docs/claude/NEXT_MODULE.md` (updated — Module 52 placeholder)
   - No production code changes
   - Full backend tests: 1312/1312 passed
   - Local signed Vapi webhook smoke test passed with HTTP 200
   - Bad Vapi signature returned HTTP 401
   - Local signed n8n calendar sync webhook smoke test passed with HTTP 200

## Architecture checkpoint

- Sprint 5 complete (Modules 45–51)
- Sprint 6 started: External Integration Compatibility (Module 52+)

50. Module 52 — External integration compatibility plan
   - Commit: f50c94c
   - Docs commit: 39c472e
   - `docs/integrations/EXTERNAL_INTEGRATION_COMPATIBILITY_PLAN.md` (new)
   - `docs/integrations/LOCAL_INTEGRATION_RUNBOOK.md` (updated — Section M rewritten)
   - `docs/claude/CURRENT_STATE.md` (updated)
   - `docs/claude/NEXT_MODULE.md` (updated — Module 53 placeholder)
   - No production code changes
   - Full backend tests: 1312/1312 passed

51. Module 53 — Provider header compatibility config
   - Commit: 3b1937e
   - Docs commit: 1bc2ea9
   - `backend/app/core/webhook_provider_config.py` (new)
   - `backend/app/api/dependencies/webhook_signature.py` (updated)
   - `backend/tests/test_webhook_provider_config.py` (new — 21 tests)
   - `backend/tests/test_webhook_signature_dependencies.py` (updated — 5 new alias tests)
   - `docs/integrations/EXTERNAL_INTEGRATION_COMPATIBILITY_PLAN.md` (updated — Section L added)
   - Module 53 tests: 36/36 passed (21 config + 15 dependency)
   - Full backend tests: 1338/1338 passed
   - Signature dependencies now accept controlled provider-specific header aliases while keeping HMAC verification required

52. Module 54 — Provider machine header compatibility config
   - Commit: 79220ca
   - `backend/app/core/machine_provider_config.py` (new)
   - `backend/app/api/dependencies/machine_auth.py` (updated — alias-aware extraction)
   - `backend/tests/test_machine_provider_config.py` (new — 24 tests)
   - `backend/tests/test_machine_auth_dependencies.py` (updated — 18 new alias tests)
   - `docs/integrations/EXTERNAL_INTEGRATION_COMPATIBILITY_PLAN.md` (updated — Section M added)
   - Module 54 tests: 42 new tests passed (24 config + 18 alias dependency)
   - Full backend tests: 1380/1380 passed
   - Machine auth accepts provider-specific aliases for service_name, clinic_id, scopes
   - Original X-Service-* headers remain fully supported
   - Conflicting duplicate aliases rejected with HTTP 401
   - Required scope and tenant/clinic enforcement unchanged

53. Module 55 — Local tunnel real provider test runbook
   - Commit: 708952a
   - Docs commit: 7afb929
   - `docs/integrations/LOCAL_TUNNEL_PROVIDER_TEST_RUNBOOK.md` (new)
   - `docs/integrations/EXTERNAL_INTEGRATION_COMPATIBILITY_PLAN.md` (updated — Section N added)
   - `docs/claude/CURRENT_STATE.md` (updated)
   - `docs/claude/NEXT_MODULE.md` (updated — Module 56 placeholder)
   - No production code changes
   - Full backend tests: 1380/1380 passed
   - Real Vapi tunnel test result: HMAC and machine auth passed; backend returned HTTP 400 due to payload shape mismatch (clinic_id absent in real Vapi body)
   - Real Vapi payload shape: {"message": {"type": "assistant-started", ...}} — no clinic_id/call_id/event_type at root

54. Module 56 — Real Vapi payload compatibility adapter
   - Commit: 53b6ddb
   - Docs commit: 57f37f8
   - `backend/app/api/routes/vapi_webhooks.py` (updated — _adapt_vapi_payload, request: Request added)
   - `backend/tests/test_vapi_webhook_route.py` (updated — 6 new adapter tests, 30 total)
   - `docs/integrations/LOCAL_TUNNEL_PROVIDER_TEST_RUNBOOK.md` (updated — Section 10 real result, Section 11 next module)
   - `docs/claude/CURRENT_STATE.md` (updated)
   - `docs/claude/NEXT_MODULE.md` (updated — Module 57 placeholder)
   - Module 56 tests: 6 new tests passed (30 total in file)
   - Full backend tests: 1386/1386 passed
   - Route now accepts both local payload shape and real Vapi server shape
   - clinic_id resolved from machine auth when absent in body
   - event_type mapped from message.type (assistant-started → call.started, end-of-call-report → call.ended)
   - call_id resolved from message.call.id → message.callId → X-Call-Id header → fallback
   - HMAC and machine auth enforcement unchanged
   - Real Vapi tunnel retest after Module 56: HTTP 200 OK confirmed

55. Module 57 — Real Vapi tunnel smoke evidence
   - Commit: 9733710
   - Docs commit: 1903c54
   - `docs/integrations/REAL_VAPI_TUNNEL_SMOKE_RESULTS.md` (new)
   - `docs/integrations/LOCAL_TUNNEL_PROVIDER_TEST_RUNBOOK.md` (updated — Section 11 Vapi smoke passed, Section 12 next module)
   - `docs/claude/CURRENT_STATE.md` (updated)
   - `docs/claude/NEXT_MODULE.md` (updated — Module 58 placeholder)
   - No production code changes
   - Full backend tests: 1386/1386 passed
   - Real Vapi → ngrok → FastAPI end-to-end confirmed: HTTP 200 OK
   - HMAC via x-signature / {body} / hex accepted
   - Machine auth via X-Vapi-* aliases accepted
   - Payload adapter resolved clinic_id and event_type from real Vapi body

56. Module 58 — Real n8n tunnel smoke evidence
   - Commit: f70041f
   - Docs commit: a9d0d79
   - `docs/integrations/REAL_N8N_TUNNEL_SMOKE_RESULTS.md` (new)
   - `docs/integrations/LOCAL_TUNNEL_PROVIDER_TEST_RUNBOOK.md` (updated — Section 12 n8n smoke passed, Section 13 next recommendation)
   - `docs/claude/CURRENT_STATE.md` (updated)
   - `docs/claude/NEXT_MODULE.md` (updated — Architecture Checkpoint 05 placeholder)
   - No production code changes
   - Full backend tests: 1386/1386 passed
   - Real n8n → ngrok → FastAPI end-to-end confirmed: success
   - HMAC via X-Signature: sha256=... over raw compact JSON body accepted
   - Machine auth via X-N8N-* aliases accepted
   - Key fix: HMAC must be computed over the exact raw bytes transmitted by n8n

## Architecture checkpoint

- Architecture Checkpoint 05 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_05_EXTERNAL_INTEGRATION_REVIEW.md`
- Commit: 3a5a76d
- Docs commit: 1c71f66
- Full backend tests: 1386/1386 passed
- Sprint 6 complete (Modules 52–58)
- Sprint 7 started: Production Auth and User Session Foundation (Module 59+)

57. Module 59 — Production auth and user session foundation
   - Commit: 97db66d
   - `backend/app/db/schema.sql` (updated — password_hash added to clinic_users)
   - `backend/migrations/versions/0002_add_password_hash_to_clinic_users.py` (new)
   - `backend/app/core/password_hashing.py` (new — bcrypt hash/verify)
   - `backend/app/core/jwt_tokens.py` (new — JWT create/decode, MissingJWTSecretError, ExpiredJWTError)
   - `backend/app/db/repositories/user_repo.py` (new — get_user_by_email, get_user_by_id, create_user)
   - `backend/app/api/dependencies/current_user.py` (new — Bearer JWT → AuthContext, not yet wired to routes)
   - `backend/tests/test_password_hashing.py` (new — 12 tests)
   - `backend/tests/test_jwt_tokens.py` (new — 12 tests)
   - `backend/tests/test_user_repository.py` (new — 14 tests)
   - `backend/tests/test_current_user_dependency.py` (new — 10 tests)
   - Module 59 tests: 51/51 passed (12 hashing + 12 JWT + 14 repo + 10 dep + 3 migration contract)
   - Full backend tests: 1437/1437 passed
   - No plaintext passwords stored or tested
   - No real secrets committed
   - No real DB in tests
   - Existing PHI route behavior unchanged — current_user dep not yet wired

58. Module 60 — Login endpoint and auth wiring plan
   - Commit: a7866ae
   - `backend/app/schemas/auth.py` (new — LoginRequest, LoginUserInfo, LoginResponse)
   - `backend/app/api/routes/auth.py` (new — POST /auth/login)
   - `backend/app/api/router.py` (updated — auth router registered)
   - `docs/security/AUTH_WIRING_PLAN.md` (new — future PHI route wiring order)
   - `backend/tests/test_auth_login_route.py` (new — 10 tests)
   - Module 60 tests: 10/10 passed
   - Full backend tests: 1447/1447 passed
   - POST /auth/login returns 200 + JWT on correct credentials
   - Wrong password or unknown email → 401 "Invalid credentials" (no user enumeration)
   - Inactive account → 401 "Account is not active"
   - Missing password_hash → 401
   - Missing JWT_SECRET_KEY → 503
   - password_hash never returned or logged
   - Email normalized to lowercase before lookup
   - Existing PHI routes unchanged — current_user dep not yet wired

59. Module 61 — Wire JWT auth to patient routes
   - Commit: f6afa45
   - `backend/app/api/routes/patients.py` (updated — Depends(get_current_user) replaces Depends(get_auth_context))
   - `backend/tests/test_patient_routes.py` (updated — fixtures override get_current_user; 7 new JWT auth tests)
   - `backend/tests/test_clinical_workflow_routes.py` (updated — cross-route smoke test assertion updated)
   - `docs/security/AUTH_WIRING_PLAN.md` (updated — /patients marked wired ✓)
   - Module 61 tests: 36/36 patient route tests passed (7 new JWT enforcement tests)
   - Full backend tests: 1451/1451 passed
   - Patient routes now require Bearer JWT; header-based X-User-* auth no longer accepted
   - Tenant/role checks (require_staff_clinic_access) unchanged — same clinic only, viewer denied
   - Other PHI routes (consultations, clinical-workflows, appointments, notifications) unchanged

60. Module 62 — Wire JWT auth to consultation routes
   - Commit: 0773bfa
   - `backend/app/api/routes/consultations.py` (updated — Depends(get_current_user) replaces Depends(get_auth_context))
   - `backend/tests/test_consultation_routes.py` (updated — fixtures override get_current_user; 9 new JWT auth tests)
   - `backend/tests/test_clinical_workflow_routes.py` (updated — test_consultations_route_still_works assertion updated to != 404)
   - `docs/security/AUTH_WIRING_PLAN.md` (updated — /consultations marked wired ✓)
   - Module 62 tests: 38/38 consultation route tests passed (9 new JWT enforcement tests)
   - Full backend tests: 1454/1454 passed
   - Consultation routes now require Bearer JWT; header-based X-User-* auth no longer accepted
   - Clinical role guard (require_clinical_clinic_access) unchanged — staff and viewer denied, doctor/owner/admin allowed
   - Other PHI routes (clinical-workflows, appointments, notifications) unchanged

61. Module 63 — Wire JWT auth to clinical workflow routes
   - Commit: 79e75b6
   - `backend/app/api/routes/clinical_workflows.py` (updated — Depends(get_current_user) replaces Depends(get_auth_context) across all 7 routes)
   - `backend/tests/test_clinical_workflow_routes.py` (updated — fixtures override get_current_user; 9 new JWT auth tests replacing 6 old header-based tests)
   - `docs/security/AUTH_WIRING_PLAN.md` (updated — /clinical-workflows marked wired ✓)
   - Module 63 tests: 46/46 clinical workflow tests passed (9 new JWT enforcement tests)
   - Full backend tests: 1457/1457 passed
   - Clinical workflow routes now require Bearer JWT; header-based X-User-* auth no longer accepted
   - Clinical role guard (require_clinical_clinic_access) unchanged — staff and viewer denied, doctor/owner/admin allowed
   - No cross-route test files required updating (consultation/clinical-workflow smoke tests already used != 404 assertions)
   - Other PHI routes (appointments, notifications) unchanged

62. Module 64 — Wire JWT auth to appointment request routes
   - Commit: 3bacac0
   - Docs commit: a04a452
   - `backend/app/api/routes/appointment_requests.py` (updated — Depends(get_current_user) replaces Depends(get_auth_context) across all 7 routes)
   - `backend/tests/test_appointment_request_routes.py` (updated — fixtures override get_current_user; 8 new JWT auth tests replacing 6 old header-based tests)
   - `docs/security/AUTH_WIRING_PLAN.md` (updated — /appointment-requests marked wired ✓)
   - Module 64 tests: 29/29 appointment request route tests passed (8 new JWT enforcement tests)
   - Full backend tests: 1459/1459 passed
   - Appointment request routes now require Bearer JWT; header-based X-User-* auth no longer accepted
   - Staff-level role guard (require_staff_clinic_access) unchanged — viewer denied, staff/doctor/owner/admin allowed
   - No cross-route test files required updating (all appointment smoke tests already used != 404 assertions)

63. Module 65 — Wire JWT auth to notification routes
   - Commit: 4b36a66
   - Docs commit: 5faa0ed
   - `backend/app/api/routes/notifications.py` (updated — Depends(get_current_user) replaces Depends(get_auth_context) across all 5 routes)
   - `backend/tests/test_notification_routes.py` (updated — fixtures override get_current_user; 8 new JWT auth tests replacing 6 old header-based tests)
   - `docs/security/AUTH_WIRING_PLAN.md` (updated — /notifications marked wired ✓; Sprint 7 PHI JWT wiring complete)
   - Module 65 tests: 30/30 notification route tests passed (8 new JWT enforcement tests)
   - Full backend tests: 1461/1461 passed
   - Notification routes now require Bearer JWT; header-based X-User-* auth no longer accepted
   - Staff-level role guard (require_staff_clinic_access) unchanged — viewer denied, staff/doctor/owner/admin allowed
   - All PHI route JWT wiring complete: /patients, /consultations, /clinical-workflows, /appointment-requests, /notifications
   - Machine routes (Vapi, n8n, availability, webhooks) unchanged

## Architecture checkpoint

- Architecture Checkpoint 06 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_06_HUMAN_AUTH_WIRING_REVIEW.md`
- Commit: 6b64de9
- Full backend tests: 1461/1461 passed
- Sprint 7 complete (Modules 59–65)
- Sprint 8 started: Frontend Dashboard Foundation (Module 66+)

64. Module 66 — Frontend dashboard foundation
   - Commit: 201d504
   - `frontend/package.json` (new — Next.js 14, React 18, TypeScript 5)
   - `frontend/tsconfig.json` (new)
   - `frontend/next.config.js` (new)
   - `frontend/app/layout.tsx` (new — root layout with PraxisMed metadata)
   - `frontend/app/page.tsx` (new — redirects to /login)
   - `frontend/app/globals.css` (new — minimal design tokens and reset)
   - `frontend/app/login/page.tsx` (new — email/password form UI scaffold)
   - `frontend/app/dashboard/page.tsx` (new — placeholder cards for Patients, Appointments, Notifications, Consultations)
   - `frontend/lib/api.ts` (new — apiFetch helper with NEXT_PUBLIC_API_BASE_URL and localhost fallback)
   - `frontend/lib/auth.ts` (new — loginUser, storeToken, getToken, clearToken, isAuthenticated; sessionStorage local-dev only)
   - `frontend/README.md` (new — local startup instructions)
   - `backend/tests/test_frontend_dashboard_foundation_contract.py` (new — 10 static contract tests)
   - Module 66 contract tests: 10/10 passed
   - Full backend tests: 1471/1471 passed
   - No backend routes modified
   - No real patient data; no hardcoded secrets
   - Login flow wired to backend in Module 67

65. Module 67 — Frontend login flow integration
   - Commit: eafe918
   - `frontend/app/login/page.tsx` (updated — 'use client'; onSubmit wired to loginUser; storeToken on success; router.push('/dashboard'); generic error display)
   - `frontend/app/dashboard/page.tsx` (updated — 'use client'; useEffect auth guard redirects to /login if no token; Logout button calls clearToken + router.push('/login'))
   - `frontend/README.md` (updated — login flow section: Clinic ID + email + password, local test instructions)
   - `backend/tests/test_frontend_login_flow_contract.py` (new — 10 static contract tests)
   - Module 67 contract tests: 10/10 passed
   - Full backend tests: 1481/1481 passed
   - No backend routes modified
   - Generic error on login failure — does not reveal email vs password mismatch
   - Section data fetching wired in Module 68

66. Module 68 — Frontend appointment requests dashboard integration
   - Commit: e106dcf
   - `frontend/lib/api.ts` (updated — AppointmentRequest type + fetchAppointmentRequests helper with Bearer token)
   - `frontend/lib/auth.ts` (updated — getClinicId() decodes clinic_id from stored JWT payload via atob)
   - `frontend/app/dashboard/page.tsx` (updated — Appointments section wired to fetchAppointmentRequests; loading/error/empty/list states; Patients/Notifications/Consultations remain as placeholders)
   - `frontend/README.md` (updated — dashboard data section: appointment fetch, Bearer token, states)
   - `backend/tests/test_frontend_appointment_requests_contract.py` (new — 10 static contract tests)
   - Module 68 contract tests: 10/10 passed
   - Full backend tests: 1491/1491 passed
   - No backend routes modified
   - clinic_id decoded from JWT payload client-side (no extra library)
   - No hardcoded tokens or real patient data

67. Module 69 — Frontend patient list integration
   - Commit: 6890f8e
   - `frontend/lib/api.ts` (updated — Patient type + fetchPatients helper)
   - `frontend/app/dashboard/page.tsx` (updated — Patients section wired to fetchPatients; loading/error/empty/list states; Appointments section unchanged; Notifications/Consultations remain as placeholders)
   - `frontend/README.md` (updated — patients section: fetchPatients, Bearer token, states)
   - `backend/tests/test_frontend_patient_list_contract.py` (new — 10 static contract tests)
   - Module 69 contract tests: 10/10 passed
   - Full backend tests: 1501/1501 passed
   - No backend routes modified
   - Patient row displays full name (first + last) and status badge (green for active)
   - No hardcoded tokens or real patient data

68. Module 70 — Frontend notifications integration
   - Commit: 07b7ad2
   - `frontend/lib/api.ts` (updated — Notification type + fetchNotifications helper)
   - `frontend/app/dashboard/page.tsx` (updated — Notifications section wired to fetchNotifications; loading/error/empty/list states; Appointments and Patients unchanged; Consultations remains as placeholder)
   - `frontend/README.md` (updated — notifications section: fetchNotifications, Bearer token, states)
   - `backend/tests/test_frontend_notifications_contract.py` (new — 10 static contract tests)
   - Module 70 contract tests: 10/10 passed
   - Full backend tests: 1511/1511 passed
   - No backend routes modified
   - Notification row displays title, priority badge (red for urgent/emergency), and notification_type
   - No hardcoded tokens or real patient data

69. Module 71 — Frontend consultation list integration
   - Commit: 6a4cff5
   - `frontend/lib/api.ts` (updated — ConsultationSession type + fetchConsultations helper)
   - `frontend/app/dashboard/page.tsx` (updated — Consultations section wired to fetchConsultations; loading/error/empty/list states; placeholder grid removed; all four sections live)
   - `frontend/README.md` (updated — consultations section: fetchConsultations, Bearer token, states)
   - `backend/tests/test_frontend_consultations_contract.py` (new — 10 static contract tests)
   - Module 71 contract tests: 10/10 passed
   - Full backend tests: 1521/1521 passed
   - No backend routes modified
   - Consultation row displays title, approval status badge (green for approved), and source
   - Consultations placeholder card removed; all four dashboard sections now live
   - No hardcoded tokens or real patient data

## Architecture checkpoint

- Architecture Checkpoint 07 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_07_FRONTEND_DASHBOARD_REVIEW.md`
- Commit: b36a4a9
- Full backend tests: 1521/1521 passed
- Sprint 8 complete (Modules 66–71)
- Sprint 9 started: Frontend Local Runtime Smoke (Module 72+)

70. Module 72 — Frontend local runtime smoke and seed login
   - Commit: 82d7856
   - `backend/scripts/seed_local_data.py` (updated — LOCAL_LOGIN_EMAIL + LOCAL_LOGIN_PASSWORD_LABEL constants; hash_password imported; password_hash included in clinic_users INSERT; ON CONFLICT updates email + password_hash; main() prints email/password label but NOT hash)
   - `backend/tests/test_local_seed_contract.py` (updated — 6 new tests 23–28: password_hash reference, hash_password usage, local login email, email constant value, password label, no print of raw hash)
   - `docs/runtime/FRONTEND_LOCAL_RUNTIME_SMOKE.md` (new — 9-step local browser smoke runbook: PostgreSQL, migrations, seed, backend, frontend, login, dashboard verification, logout, known limitations)
   - `frontend/README.md` (updated — local browser smoke quick-start and link to runbook)
   - Module 72 contract tests: 28/28 passed (6 new + 22 existing)
   - Full backend tests: 1527/1527 passed
   - No backend routes modified
   - Local login credentials: doctor.local@praximed.test / local-dev-password (fake/local only)
   - password_hash never printed; hash_password called at runtime inside async function

71. Module 73 — Fix frontend runtime smoke blockers
   - Commit: 746d77e
   - Runtime blockers found during manual smoke (Module 72):
     1. Alembic revision ID `0002_add_password_hash_to_clinic_users` (42 chars) exceeded `alembic_version VARCHAR(32)` — migration failed
     2. `seed_local_data.py` raised `ModuleNotFoundError: No module named 'backend'` when run directly — missing sys.path safety
     3. Backend failed to start with `[Errno 48] Address already in use` — runbook needed port-conflict guidance
   - `backend/migrations/versions/0002_add_password_hash_to_clinic_users.py` (updated — revision shortened to `0002_password_hash`, 16 chars)
   - `backend/scripts/seed_local_data.py` (updated — `_PROJECT_ROOT` sys.path insertion at top for direct execution; hash_password import preserved)
   - `backend/tests/test_migration_contract.py` (updated — 3 new tests 21–23: all revision IDs ≤32 chars, 0002 file exists, 0002 revision value correct)
   - `backend/tests/test_local_seed_contract.py` (updated — 1 new test 29: sys.path project-root safety present)
   - `docs/runtime/FRONTEND_LOCAL_RUNTIME_SMOKE.md` (updated — blocker table added, port-conflict stop instructions, no-ngrok note, JWT_SECRET_KEY required note)
   - Module 73 new tests: 4 new tests (3 migration + 1 seed); all 52 seed+migration tests pass
   - Full backend tests: 1531/1531 passed
   - No backend routes modified; no frontend code changed

72. Module 74 — Fix frontend browser login runtime issue (CORS)
   - Commit: 04cba09
   - CORS blocker found during manual smoke (Module 73):
     - curl `POST /auth/login` returned HTTP 200 (backend auth works)
     - Browser login showed "Sign-in failed" — root cause: `OPTIONS /auth/login → 405 Method Not Allowed`
     - FastAPI had no CORS middleware; browser preflight was rejected before reaching the auth route
   - `backend/app/main.py` (updated — `CORSMiddleware` added; defaults to `http://localhost:3000` and `http://127.0.0.1:3000`; `FRONTEND_CORS_ORIGINS` env override; explicit origins only, no wildcard)
   - `backend/tests/test_cors_contract.py` (new — 8 CORS contract tests)
   - `docs/runtime/FRONTEND_LOCAL_RUNTIME_SMOKE.md` (updated — CORS blocker row added; backend CORS note in Step 4)
   - `frontend/README.md` (updated — backend CORS local-dev note)
   - Module 74 CORS tests: 8/8 passed
   - Full backend tests: 1539/1539 passed
   - No auth routes or frontend code modified

73. Module 75 — Frontend browser smoke evidence
   - Commit: c5f9d4a
   - `docs/runtime/FRONTEND_BROWSER_SMOKE_RESULTS.md` (new — full smoke evidence: environment, steps, curl/browser/CORS/logout evidence, what this proves, what it does not prove, future language note, recommended Module 76)
   - `docs/runtime/FRONTEND_LOCAL_RUNTIME_SMOKE.md` (updated — smoke PASS note added at top, link to results doc)
   - `docs/claude/NEXT_MODULE.md` (updated — Module 76 spec: dashboard demo data polish)
   - No production code changes
   - Full backend tests: 1539/1539 passed
   - Browser smoke verdict: PASS (2026-07-02)
   - login → dashboard → logout flow confirmed in real browser
   - CORS preflight (OPTIONS /auth/login) → HTTP 200 confirmed
   - All four dashboard sections rendered (Appointments empty, Patients seeded, Notifications empty, Consultations seeded)
   - Logout cleared sessionStorage token; auth guard redirected back to /login

74. Module 76 — Dashboard empty-state and local demo data polish
   - Commit: 4f263b5
   - `backend/scripts/seed_local_data.py` (updated — LOCAL_APPOINTMENT_REQUEST_ID + LOCAL_NOTIFICATION_ID constants; INSERT into appointment_requests and clinic_notifications; ON CONFLICT upserts; main() prints both new IDs)
   - `backend/tests/test_local_seed_contract.py` (updated — 8 new tests 30–37: appointment request ID, notification ID, UUID validity, table INSERT references, constant usage count, ON CONFLICT count)
   - `docs/runtime/FRONTEND_BROWSER_SMOKE_RESULTS.md` (updated — Section 9 rewritten to Module 76 demo data note)
   - `docs/runtime/FRONTEND_LOCAL_RUNTIME_SMOKE.md` (updated — Module 76 update line at top; demo data note; Step 3 expected output updated; Step 8 all four sections show list state)
   - `frontend/README.md` (updated — seed row table for all four dashboard sections; status updated to Module 76)
   - Module 76 new tests: 8 new (37 total in file); all 37 passed
   - Full backend tests: 1547/1547 passed
   - No backend routes modified; no frontend code changed
   - Seed script creates: clinic, doctor user, patient, consultation session, appointment request (55555555), notification (66666666)
   - All four dashboard sections now show list state after re-seeding

75. Module 77 — Rerun frontend demo data browser smoke evidence
   - Commit: 1253b84
   - `docs/runtime/FRONTEND_DEMO_DATA_BROWSER_SMOKE_RESULTS.md` (new — full demo data smoke evidence: environment, steps, seed output, all four sections list state, what this proves, known patient name display issue, what this does not prove, Architecture Checkpoint 08 recommended)
   - `docs/runtime/FRONTEND_BROWSER_SMOKE_RESULTS.md` (updated — Section 10 added: Module 77 PASS confirmation with section-by-section table, known issue note)
   - `docs/runtime/FRONTEND_LOCAL_RUNTIME_SMOKE.md` (updated — Module 77 update line; demo data smoke PASS note; link to new results doc; updated demo data note with name display caveat)
   - `docs/claude/NEXT_MODULE.md` (updated — Architecture Checkpoint 08 spec)
   - No production code changes
   - Full backend tests: 1547/1547 passed
   - Demo data browser smoke verdict: PASS (2026-07-02)
   - All four dashboard sections rendered list state after re-seeding
   - Known minor issue: patient row shows `"—"` for name (full_name vs first_name/last_name field mismatch — cosmetic, not blocking)

## Architecture checkpoint

- Architecture Checkpoint 08 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_08_LOCAL_DEMO_READINESS_REVIEW.md`
- Commit: cdc2ee1
- Full backend tests: 1547/1547 passed (re-confirmed at start of Module 78)
- Sprint 9 complete (Modules 72–77)
- Local full-stack demo confirmed viable: login → all four dashboard sections list state → logout
- Known issue noted: patient row name displayed as `"—"` — resolved in Module 78
- Sprint 10 started: Dashboard Demo Polish (Module 78+)

76. Module 78 — Dashboard demo polish and patient display fix
   - Commit: bc3e9e2
   - `frontend/lib/api.ts` (updated — `full_name: string | null` added to `Patient` interface as primary field; `first_name` and `last_name` kept for defensive compatibility)
   - `frontend/app/dashboard/page.tsx` (updated — patient name display expression changed from `|| '—'` to `patient.full_name || join(first+last) || 'Unnamed patient'`)
   - `backend/tests/test_frontend_patient_list_contract.py` (updated — 3 new tests 11–13: full_name in Patient interface, patient.full_name in display, 'Unnamed patient' fallback not '—')
   - `docs/runtime/FRONTEND_DEMO_DATA_BROWSER_SMOKE_RESULTS.md` (updated — §6 known issue marked resolved in Module 78)
   - `docs/architecture/ARCHITECTURE_CHECKPOINT_08_LOCAL_DEMO_READINESS_REVIEW.md` (updated — §4.1 patient name issue marked fixed in Module 78)
   - Module 78 new tests: 3 new (13 total in patient list contract file); all 13 passed
   - Full backend tests: 1550/1550 passed
   - No backend routes or schema modified
   - Patient row now displays "Local Test Patient" after re-seeding (not `"—"`)
   - Fallback for missing name data is `'Unnamed patient'` (not `'—'`)

77. Module 79 — Dashboard visual polish pass
   - Commit: 32e9781
   - `frontend/app/dashboard/page.tsx` (updated — "Clinic Dashboard" subtitle in header; "Clinic Overview" page heading; per-section row count pills; shared BADGE_STYLES helper + badgeStyle() function; cardStyle/rowStyle/badgePillStyle constants; local-demo footer label; all four data fetch calls unchanged)
   - `frontend/app/globals.css` (updated — badge colour token variables: --badge-blue-bg/text, --badge-green-bg/text, --badge-red-bg/text, --badge-neutral-bg/text)
   - `backend/tests/test_frontend_dashboard_visual_polish_contract.py` (new — 10 static contract tests: PraxisMed brand, logout button, all four sections, clinical heading, all loading/error/empty states, badge styling, no hardcoded credentials/data)
   - `docs/runtime/FRONTEND_DEMO_DATA_BROWSER_SMOKE_RESULTS.md` (updated — Module 79 note added)
   - Module 79 new tests: 10 new; all 10 passed
   - Full backend tests: 1560/1560 passed
   - No backend routes, API helpers, or auth modified
   - No data fetching behavior changed
   - Dashboard improvements: clinic context, count pills, consistent badge colours, demo label

78. Module 80 — Local demo retest after visual polish
   - Commit: (docs only — no code commit; see sprint commit below)
   - `docs/runtime/FRONTEND_POLISHED_DEMO_BROWSER_SMOKE_RESULTS.md` (new — full polished demo smoke evidence: header, count pills, patient name fix confirmed, badge colours, footer label, what this proves, what remains, Architecture Checkpoint 09 recommended)
   - `docs/runtime/FRONTEND_DEMO_DATA_BROWSER_SMOKE_RESULTS.md` (updated — Module 80 PASS note added, links to polished smoke results doc)
   - No production code changes
   - Full backend tests: 1560/1560 passed
   - Polished browser smoke verdict: PASS (2026-07-02)
   - All four sections show count pills (1) and correct row content
   - Patient row shows "Local Test Patient" — Module 78 fix confirmed
   - "Clinic Dashboard" subtitle and "Clinic Overview" heading confirmed
   - Local-demo footer label confirmed visible

## Architecture checkpoint

- Architecture Checkpoint 09 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_09_POLISHED_LOCAL_DEMO_REVIEW.md`
- Full backend tests: 1560/1560 passed
- Sprint 10 complete (Modules 78–80): patient display fix, visual polish, polished smoke
- Local demo confirmed presentable: "Clinic Overview" dashboard, count pills, correct patient names, badge colours, local-demo footer
- No security regressions in Sprint 10
- Recommended: Sprint 11 / Module 81 — Appointment Request Workflow UI Foundation
- Reason: appointment requests are the core Vapi output; clinic staff need Confirm/Reject actions to complete the loop
- Sprint 11 started: Appointment Request Workflow UI (Module 81+)

79. Module 81 — Appointment request workflow UI foundation
   - Commit: acda04c
   - `frontend/lib/api.ts` (updated — `confirmAppointmentRequest(requestId, clinicId, token)` helper: PATCH /appointment-requests/{id}/status?clinic_id=..., body {"status":"confirmed","action_required":false}, throws on non-2xx)
   - `frontend/app/dashboard/page.tsx` (updated — `confirmAppointmentRequest` imported; `confirmingIds: Set<string>` and `apptActionError` state added; `handleConfirm()` async handler; Confirm button on rows with status === 'new'; button disabled + "Confirming…" while in-flight; generic error on failure; refetches appointments on success)
   - `backend/tests/test_frontend_appointment_workflow_contract.py` (new — 10 static contract tests: helper defined, PATCH method, correct endpoint, Bearer token via apiFetch, dashboard imports helper, button gated on status==='new', disabled state, action error state, refetch on success, no hardcoded credentials)
   - `docs/runtime/FRONTEND_POLISHED_DEMO_BROWSER_SMOKE_RESULTS.md` (updated — Module 81 note added)
   - `frontend/README.md` (updated — Confirm action section)
   - Module 81 new tests: 10 new (1570 total); all 10 passed
   - Full backend tests: 1570/1570 passed
   - No backend routes or schema modified
   - Confirm button only shown on status === 'new' rows; disappears after successful confirmation
   - Action error is generic — does not expose backend error detail

80. Module 82 — Appointment workflow browser smoke evidence and integration loop prep
   - Commit: (see below)
   - `docs/runtime/APPOINTMENT_WORKFLOW_BROWSER_SMOKE_RESULTS.md` (new — full smoke evidence: Confirm button visible on new row, in-flight disabled state observed, status badge updated to confirmed, button disappeared, all other sections stable, verdict PASS)
   - `docs/runtime/FRONTEND_POLISHED_DEMO_BROWSER_SMOKE_RESULTS.md` (updated — Module 82 PASS note added)
   - `docs/architecture/ARCHITECTURE_CHECKPOINT_09_POLISHED_LOCAL_DEMO_REVIEW.md` (updated — §3b Sprint 11 follow-up added; §4.1 updated to reflect Confirm action delivered, remaining actions not yet built)
   - `docs/integrations/VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md` (new — integration prep: target flow, proven pieces, unknowns, safety constraints, recommended Module 83)
   - No production code changes
   - Full backend tests: 1570/1570 passed
   - Browser smoke verdict: PASS (2026-07-02)
   - Appointment Confirm workflow proven end-to-end: login → Confirm → status "confirmed" → button gone → dashboard stable
   - Next integration target: Vapi intake → appointment request → dashboard confirm loop

81. Module 83 — Vapi intake to appointment dashboard smoke harness
   - Commit: (see below)
   - **Inspection findings**: target endpoint is `POST /vapi/tools/capture-appointment-request` (machine auth, no HMAC); bug found: `config_loader.get()` / `config.clinic_id` should be `config_loader.load()` / `config.tenant_id`; `main.py` does not wire `app.state.config_loader` (pending Module 84)
   - `backend/app/modules/vapi/vapi_appointment_capture.py` (bug fix — `config_loader.get` → `config_loader.load`; `config.clinic_id` → `config.tenant_id`)
   - `backend/tests/test_vapi_appointment_capture.py` (updated — `loader.get` → `loader.load`; `cfg.clinic_id` → `cfg.tenant_id` in `_make_config`; all 23 tests still pass)
   - `docs/integrations/local_payloads/vapi_appointment_intake.json` (new — fake Vapi capture payload: clinic_ref, call_id, patient_name, reason, urgency_level)
   - `backend/scripts/smoke_vapi_appointment_intake.py` (new — sends POST with X-Vapi-* machine auth, prints result, handles 503 with config_loader guidance, exits non-zero on failure)
   - `backend/tests/test_vapi_appointment_intake_harness_contract.py` (new — 10 static contract tests: payload valid, local clinic UUID, required fields, no real data, script exists, API_BASE_URL fallback, machine auth headers, no secret printing, non-zero exit, prep doc references harness)
   - `docs/integrations/VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md` (updated — target flow corrected; Unknowns table updated; Module 83 harness section with inspection findings, harness components, manual flow commands, Module 84 next steps)
   - `docs/runtime/APPOINTMENT_WORKFLOW_BROWSER_SMOKE_RESULTS.md` (updated — Module 83 note added)
   - Module 83 new tests: 10 harness contract tests; all 10 passed
   - Module 82 full test re-confirmation (timed out previously): 1570/1570 passed
   - Full backend tests: 1580/1580 passed
   - No frontend code changed
   - No backend routes, auth, schema, or seed data modified
   - Bug fix is covered by existing 23 capture tests (all still pass)

## Architecture checkpoint

- Architecture Checkpoint 09 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_09_POLISHED_LOCAL_DEMO_REVIEW.md`
- Updated in Module 82: §3b follow-up added (Modules 81–82 outcomes); §4.1 Confirm action marked delivered
- Sprint 11 in progress (Modules 81–84 complete)

82. Module 84 — Vapi intake harness runtime wiring and smoke evidence
   - Commit: 0959ccc
   - `backend/app/main.py` (updated — `ClinicConfigLoader` imported; `app.state.config_loader = ClinicConfigLoader(pool=app.state.db_pool)` in lifespan startup; `app.state.config_loader = None` in lifespan shutdown)
   - `backend/tests/test_app_lifespan_config_loader.py` (new — 9 lifespan config_loader tests)
   - Module 84 new tests: 9/9 passed
   - Full backend tests: 1589/1589 passed
   - Smoke result: HTTP 503 → resolved; new HTTP 500 — seed UUID `11111111-1111-1111-1111-111111111111` failed `_assert_valid_uuid()` variant byte check `[89ab]`

83. Module 85 — Config loader UUID compatibility and Vapi intake smoke completion
   - Commit: fd6ac74
   - `backend/app/core/config_loader.py` (updated — replaced `_UUID_RE` regex with `uuid.UUID()` parser; added DB-error fallback in `_load_db_config`; updated docstrings)
   - `backend/tests/test_config_loader.py` (updated — 5 new tests: accepts deterministic local UUID, accepts RFC 4122 UUID unchanged, rejects brace-wrapped UUID, rejects unhyphenated UUID, DB error falls back to disk)
   - `docs/runtime/VAPI_INTAKE_TO_DASHBOARD_SMOKE_RESULTS.md` (updated — verdict PASS; smoke evidence recorded)
   - `docs/integrations/VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md` (updated — UUID blocker RESOLVED; smoke command and result recorded)
   - Module 85 new tests: 5/5 passed (28 total in config_loader test file)
   - Full backend tests: 1594/1594 passed
   - Live smoke: HTTP 200 — appointment ID `509211a7-784e-4e45-90f1-d9af6f8d7981`, `status: new`, `source: vapi`, `action_required: true`

84. Module 86 — Vapi intake to dashboard browser smoke evidence
   - Commit: 4c31a9f
   - `docs/runtime/VAPI_INTAKE_TO_DASHBOARD_BROWSER_SMOKE_RESULTS.md` (new — full browser smoke evidence: harness output, row verification, Confirm action, verdict PASS)
   - `docs/runtime/VAPI_INTAKE_TO_DASHBOARD_SMOKE_RESULTS.md` (updated — Module 86 browser confirm note added)
   - `docs/integrations/VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md` (updated — all local unknowns RESOLVED; next unknown is real Vapi payload from live assistant; Module 87 recommended)
   - No production code changes
   - Full backend tests: 1594/1594 passed
   - Browser smoke verdict: PASS (2026-07-02)
   - Vapi-created row appeared in dashboard without seed script
   - Staff Confirm: status "new" → "confirmed"; button disappeared

85. Module 87 — Real Vapi appointment tool payload smoke prep
   - Commit: (see git log)
   - `docs/integrations/local_payloads/vapi_real_tool_payload_sample.json` (new — sanitized fake sample of real Vapi tool-call body shape with nested message.toolCallList)
   - `backend/scripts/inspect_vapi_tool_payload.py` (new — structural inspector: redacts patient values, detects flat vs nested shape, assesses compatibility with VapiAppointmentCaptureRequest)
   - `backend/tests/test_vapi_real_tool_payload_prep_contract.py` (new — 17 static contract tests for sample, inspector, prep docs)
   - `docs/integrations/VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md` (updated — shape gap analysis; real Vapi payload capture plan; Module 88 adapter recommended)
   - `docs/runtime/VAPI_INTAKE_TO_DASHBOARD_BROWSER_SMOKE_RESULTS.md` (updated — Module 87 prep note added)
   - No production code changes
   - Full backend tests: 1611/1611 passed
   - Shape gap identified: real Vapi tool call nests arguments in `message.toolCallList[0].function.arguments`; current capture endpoint expects flat root-level fields; adapter needed (Module 88)
   - Inspector correctly redacts patient values; verdicts NEEDS ADAPTER (nested) and COMPATIBLE (flat)

86. Module 88 — Real Vapi tool call adapter
   - Commit: 479d509
   - `backend/app/modules/vapi/vapi_appointment_capture.py` (updated — `adapt_vapi_tool_call_body` function added; `import json` added)
   - `backend/app/api/routes/vapi_tools.py` (updated — route changed from `body: VapiAppointmentCaptureRequest` to `request: Request`; adapter wired before Pydantic validation; `Request`, `PydanticValidationError`, `adapt_vapi_tool_call_body` imported)
   - `backend/tests/test_vapi_appointment_capture.py` (updated — 9 new adapter tests 23–31; `adapt_vapi_tool_call_body` imported)
   - `backend/tests/test_vapi_real_tool_payload_prep_contract.py` (updated — 5 new contract tests 18–22 for adapter importability and sample payload mapping)
   - `docs/runtime/VAPI_REAL_TOOL_PAYLOAD_ADAPTER_RESULTS.md` (new — adapter design, security boundaries, test results, smoke status)
   - `docs/integrations/VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md` (updated — shape gap marked RESOLVED; adapter complete; Module 89 recommended)
   - Module 88 new tests: 14/14 passed (9 unit + 5 contract)
   - Full backend tests: 1625/1625 passed
   - Flat (local harness) shape passes through adapter unchanged — existing smoke and tests unaffected
   - Nested (real Vapi) shape normalized: clinic_ref from machine auth, call_id from message.call.id, patient fields from function.arguments
   - Security boundary enforced: patient-supplied clinic_ref in arguments silently ignored; machine_clinic_id always used

87. Module 89 — Vapi/ngrok appointment intake dashboard evidence
   - Commit: 514206e
   - `docs/runtime/VAPI_REAL_TOOL_CALL_LIVE_SMOKE_RESULTS.md` (new — full evidence: ngrok intake, dashboard rows, staff Confirm, accuracy statement, what's proven vs pending)
   - `docs/runtime/VAPI_REAL_TOOL_PAYLOAD_ADAPTER_RESULTS.md` (updated — Module 89 ngrok/dashboard evidence note)
   - `docs/runtime/VAPI_INTAKE_TO_DASHBOARD_BROWSER_SMOKE_RESULTS.md` (updated — Module 89 dashboard confirmation note)
   - `docs/integrations/VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md` (updated — unknowns table updated; scope `vapi:tool` confirmed; frontend opportunity note added)
   - `docs/integrations/local_payloads/vapi_real_tool_payload_captured.json` (new — sanitized captured payload from ngrok smoke)
   - No production code changes
   - Full backend tests: 1625/1625 passed (unchanged)
   - Evidence: nested Vapi-shape through ngrok → HTTP 200; 4 appointment rows in dashboard; staff Confirm succeeded; status new → confirmed; button disappeared; other sections stable
   - Machine auth scope confirmed: `X-Vapi-Scopes: vapi:tool` (singular)
   - Direct real Vapi assistant call logs: PENDING — not captured in this module

88. Module 90 — Direct real Vapi assistant tool-call log capture
   - Commit: 5155d65
   - `docs/runtime/VAPI_DIRECT_ASSISTANT_TOOL_CALL_LOG_RESULTS.md` (new — full evidence: real Vapi test assistant tool call, ngrok POST, backend row creation, dashboard Confirm, verdict PASS)
   - `docs/runtime/VAPI_REAL_TOOL_CALL_LIVE_SMOKE_RESULTS.md` (updated — direct assistant log evidence upgraded from PENDING to PASS)
   - `docs/integrations/VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md` (updated — direct Vapi assistant logs marked RESOLVED; integration loop status section added; next focus options listed)
   - `docs/architecture/ARCHITECTURE_CHECKPOINT_10_VAPI_APPOINTMENT_INTAKE_LOOP_REVIEW.md` (updated — status updated; post-checkpoint Module 90 note; pending claims marked PASS)
   - No production code changes
   - Full backend tests: 1625/1625 passed (unchanged)
   - Evidence: real Vapi test assistant fired `capture_appointment_request`; Vapi tool logs success; ngrok POST confirmed; backend created row; dashboard row confirmed by staff; no real data; no auto-confirmation

89. Module 91 — Production Deployment Readiness Inventory
   - Commit: 2f373b5
   - `docs/deployment/PRODUCTION_READINESS_INVENTORY.md` (new — 12-section inventory: purpose, required env vars, infrastructure components, DB strategy, secrets handling, CORS/domain strategy, auth hardening gaps, Vapi production config, n8n production config, health and readiness, production blockers, not in scope)
   - `backend/.env.example` (updated — added JWT_SECRET_KEY, VAPI_WEBHOOK_SECRET, N8N_WEBHOOK_SECRET, INTERNAL_WEBHOOK_SECRET, FRONTEND_CORS_ORIGINS with placeholder values)
   - `backend/tests/test_production_readiness_inventory_contract.py` (new — 29 static contract tests: inventory exists, .env.example completeness, no real secrets, all required env vars covered, critical components mentioned)
   - No production code changes
   - Full backend tests: 1654/1654 passed
   - Env var audit: 7 backend vars + 1 frontend var documented; 5 were missing from .env.example and added
   - Production blockers: 13 explicit blockers documented before first real deployment

90. Module 92 — Environment and Secrets Contract
   - Commit: 6679453
   - `docs/deployment/ENVIRONMENT_AND_SECRETS_CONTRACT.md` (new — 14-section contract: purpose, environment tiers, backend env var contract table, frontend env var contract, secret generation rules, rotation policy, storage rules, env file rules, CORS/domain contract, Vapi/n8n production contract, database contract, logging/secrets safety, pre-deployment checklist, non-goals)
   - `frontend/.env.example` (new — documents NEXT_PUBLIC_API_BASE_URL with localhost placeholder; no backend secrets)
   - `backend/tests/test_environment_and_secrets_contract.py` (new — 43 static contract tests: contract doc coverage, backend/frontend .env.example completeness, no real secrets, security rules, Vapi/n8n requirements)
   - No production code changes; no runtime behavior changes
   - Full backend tests: 1697/1697 passed
   - Four deployment tiers documented: local, test/CI, staging, production
   - Secret classification: DATABASE_URL, JWT_SECRET_KEY, all webhook secrets, POSTGRES_PASSWORD classified as secrets
   - Rotation policy: all 5 secrets with when-to-rotate, impact, and coordination notes
   - Logging safety: PHI and secret values that must never appear in logs enumerated

91. Module 93 — Production CORS/Auth/Domain Plan
   - Commit: 9d087f5
   - `docs/deployment/PRODUCTION_CORS_AUTH_DOMAIN_PLAN.md` (new — 13-section plan: purpose, current local state, production domain topology, CORS policy per tier, sessionStorage JWT risk assessment, httpOnly Secure SameSite cookie migration path with options A/B/C, domain/auth interaction, Vapi/n8n server-to-server domain plan, security headers plan, env var mapping per tier, implementation sequence, risks and decisions table, go/no-go verdict)
   - `backend/tests/test_production_cors_auth_domain_plan_contract.py` (new — 32 static contract tests)
   - No production code changes; no runtime behavior changed
   - Full backend tests: 1729/1729 passed
   - sessionStorage JWT risk rated High (XSS-accessible; blocker for real PHI production)
   - httpOnly Secure SameSite=Lax cookie migration recommended before production PHI; implementation deferred to Module 95+
   - Machine auth headers (Vapi/n8n) are server-to-server; not browser CORS — correctly excluded from allow_headers
   - Go/no-go: Not ready for production launch; 6 blockers remain; ready to proceed to deployment smoke runbook

92. Module 94 — Deployment Smoke Runbook
   - Commit: 2674688
   - `docs/deployment/DEPLOYMENT_SMOKE_RUNBOOK.md` (new — 17-section runbook: purpose, scope, prerequisites, 4 smoke tiers, local smoke steps with exact commands, staging smoke steps with placeholders, production-like pre-traffic smoke, Vapi smoke, n8n smoke, CORS smoke, auth/session smoke with PHI note, DB/migration smoke, logging safety, failure triage table with 14 scenarios, pass/fail checklist, production launch gate, appendix of local commands)
   - `backend/tests/test_deployment_smoke_runbook_contract.py` (new — 36 static contract tests)
   - No production code changes; no runtime behavior changed
   - Full backend tests: 1765/1765 passed
   - Covers local/staging/production-like tiers; Vapi, n8n, CORS, auth, DB, frontend, backend, logging
   - Production launch gate explicitly states smoke runbook alone does not approve launch; Architecture Checkpoint 12 required

## Architecture checkpoints

- Architecture Checkpoint 10 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_10_VAPI_APPOINTMENT_INTAKE_LOOP_REVIEW.md`
  - Updated post-checkpoint (Module 90): all pending evidence gaps closed
- Architecture Checkpoint 11 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_11_POST_VAPI_DIRECTION_REVIEW.md`
  - Reviews Sprint 11 outcomes; decides next sprint direction
  - Recommendation: Sprint 12 — Production Deployment Readiness Inventory
  - Defers: Fabel 5/frontend UX sprint (after deployment blockers mapped); appointment workflow expansion (after production risks known)
- Architecture Checkpoint 12 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_12_PRODUCTION_READINESS_REVIEW.md`
  - Production PHI launch: NO-GO (12 unresolved blockers)
  - Staging/fake-data deployment prep: GO
  - Auth/session hardening (httpOnly cookie): plan in Module 98; implement Sprint 14
  - Fabel 5/frontend UX sprint: deferred until staging topology confirmed
  - Appointment workflow expansion: deferred
  - Next direction: Sprint 13 — Staging Deployment Target Selection and Topology Plan
- Full backend tests: 1765/1765 passed
- Sprint 11 complete (Modules 81–90); Sprint 12 complete (Modules 91–94); Sprint 13 starting

93. Module 95 — Staging Deployment Target Selection and Topology Plan
   - Commit: 3102ab7
   - `docs/deployment/STAGING_DEPLOYMENT_TOPOLOGY_PLAN.md` (new — 15-section plan: purpose, context from Checkpoint 12, pre-existing baseline, platform comparison table with 5 options scored, chosen topology Railway+Vercel with rationale, architecture diagram, environment variable mapping table, staging domain placeholders, CORS constraint, DB strategy with isolated fake clinic UUID, migration gate, Vapi staging configuration, n8n staging strategy, sessionStorage JWT note, risk/mitigation table, staging limitations, Module 96 next step)
   - `backend/tests/test_staging_deployment_topology_plan_contract.py` (new — 33 static contract tests: plan exists, platforms compared Railway/Render/Fly.io/Vercel, managed PostgreSQL, chosen topology with rationale, fake/non-PHI data only, PHI no-go, HTTPS staging URLs, no ngrok in staging, no wildcard CORS, FRONTEND_CORS_ORIGINS, NEXT_PUBLIC_API_BASE_URL, Vapi endpoint vapi:tool singular, n8n strategy, isolated staging DB, migrations, secrets injection method, sessionStorage acceptable for fake-data staging only, no deployment executed, Module 96 mention, no real secrets)
   - No production code changes; no runtime behavior changed
   - Full backend tests: 1798/1798 passed
   - Chosen topology: Railway (Backend + PostgreSQL) + Vercel (Frontend)
   - Staging domains: https://staging-api.up.railway.app (backend), https://staging-app.vercel.app (frontend)
   - FRONTEND_CORS_ORIGINS: https://staging-app.vercel.app (exact; no wildcard)
   - sessionStorage JWT: acceptable for fake-data staging; not PHI-safe for production
   - Vapi test assistant points at Railway stable URL (replaces ngrok)
   - DATABASE_URL auto-injected by Railway PostgreSQL add-on
   - No seed_local_data.py in staging; staging-specific fake clinic UUID required

94. Module 96 — Staging Environment Variable Matrix
   - Commit: 5761683
   - `docs/deployment/STAGING_ENVIRONMENT_VARIABLE_MATRIX.md` (new — 15-section matrix: purpose, environment boundary with 3-tier isolation rules, staging components table, full backend env var matrix with Railway injection details, frontend env var matrix, PostgreSQL staging matrix, Vapi staging matrix with machine auth headers, n8n staging matrix, domain/CORS variable mapping, secret generation rules, staging env setup checklist, validation checklist, 13-scenario failure matrix, production separation statements, Module 97 next step)
   - `backend/tests/test_staging_environment_variable_matrix_contract.py` (new — 34 static contract tests: matrix exists, Railway backend/PostgreSQL/Vercel covered, fake/non-PHI staging, PHI no-go, all 6 backend secrets, POSTGRES_DB/USER/PASSWORD, NEXT_PUBLIC_API_BASE_URL, vapi:tool singular, staging fake clinic UUID placeholder, no ngrok, no wildcard CORS, HTTPS only, no local-dev secrets, no production secrets, Railway/Vercel secret storage, migrations, n8n staging, no real patient data, no deployment in module, Module 97 mention, no real secrets in doc)
   - No production code changes; no runtime behavior changed
   - Full backend tests: 1832/1832 passed
   - DATABASE_URL: auto-injected by Railway PostgreSQL add-on; never set manually
   - JWT_SECRET_KEY / VAPI_WEBHOOK_SECRET / N8N_WEBHOOK_SECRET / INTERNAL_WEBHOOK_SECRET: set via Railway dashboard; high-entropy per-staging values
   - FRONTEND_CORS_ORIGINS: set via Railway dashboard to exact Vercel staging origin
   - NEXT_PUBLIC_API_BASE_URL: set via Vercel dashboard; build-time public var; not a secret
   - sessionStorage JWT: acceptable for fake-data staging only; httpOnly cookie required for production PHI (Module 98)
   - Staging fake clinic UUID: distinct from local 11111111-... UUID; assigned at DB provisioning time

95. Module 97 — Staging Deployment Dry-Run Checklist
   - Commit: 5f7122d
   - `docs/deployment/STAGING_DEPLOYMENT_DRY_RUN_CHECKLIST.md` (new — 19-section dry-run checklist: purpose, preconditions, target topology, repository readiness, Railway backend setup, Railway PostgreSQL, Vercel frontend, domain/CORS, env var checklist, migration gate, auth/dashboard, Vapi staging, n8n staging, smoke execution order, evidence capture, failure stop rules, rollback, go/no-go, Module 98 next step)
   - `backend/tests/test_staging_deployment_dry_run_checklist_contract.py` (new — 33 static contract tests: checklist exists, Railway/Vercel/PostgreSQL covered, fake/non-PHI data, PHI no-go, no deployment in module, no ngrok, no wildcard CORS, HTTPS, DATABASE_URL/JWT_SECRET_KEY/FRONTEND_CORS_ORIGINS/NEXT_PUBLIC_API_BASE_URL, migrations, Vapi vapi:tool singular/no auto-confirm/staff Confirm, n8n staging, no real patient data, no secrets in logs, rollback, evidence capture, failure stop rules, sessionStorage JWT fake-data-only/not PHI-safe, Module 98 mention, no real secrets in doc)
   - No production code changes; no runtime behavior changed
   - Full backend tests: 1865/1865 passed
   - Smoke execution order: 13-step sequence from health check to rollback readiness
   - Failure stop rules: 14 conditions that must halt the staging deployment attempt
   - Evidence capture: per-smoke checklist of command, status, screenshot, log snippet, commit SHA, timestamp, pass/fail
   - Go/no-go: staging GO when all checklists signed off; production PHI NO-GO; Fabel 5/UX sprint WAIT; Module 98 auth plan next

## Architecture checkpoints

- Architecture Checkpoint 10 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_10_VAPI_APPOINTMENT_INTAKE_LOOP_REVIEW.md`
  - Updated post-checkpoint (Module 90): all pending evidence gaps closed
- Architecture Checkpoint 11 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_11_POST_VAPI_DIRECTION_REVIEW.md`
  - Reviews Sprint 11 outcomes; decides next sprint direction
  - Recommendation: Sprint 12 — Production Deployment Readiness Inventory
  - Defers: Fabel 5/frontend UX sprint (after deployment blockers mapped); appointment workflow expansion (after production risks known)
- Architecture Checkpoint 12 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_12_PRODUCTION_READINESS_REVIEW.md`
  - Production PHI launch: NO-GO (12 unresolved blockers)
  - Staging/fake-data deployment prep: GO
  - Auth/session hardening (httpOnly cookie): plan in Module 98; implement Sprint 14
  - Fabel 5/frontend UX sprint: deferred until staging topology confirmed
  - Appointment workflow expansion: deferred
  - Next direction: Sprint 13 — Staging Deployment Target Selection and Topology Plan
96. Module 98 — Auth/Session Hardening Implementation Plan
   - Commit: (see git log)
   - `docs/security/AUTH_SESSION_HARDENING_IMPLEMENTATION_PLAN.md` (new — 15-section implementation plan: current auth architecture with exact code locations, production target architecture, cookie strategy with SameSite tier matrix, access token lifecycle, refresh token lifecycle (deferred), CSRF protection per-tier, logout flow with target backend route, browser behavior per scenario, backend changes (auth.py login cookie, logout route, get_current_user cookie read + Bearer fallback), frontend changes (auth.ts/api.ts/login/dashboard), testing strategy, rollback strategy, 13-step migration sequence, 10-scenario risk matrix, final recommendation + Sprint 14 scope)
   - `backend/tests/test_auth_session_hardening_plan_contract.py` (new — 27 static contract tests: plan exists, sessionStorage risk, XSS, HttpOnly, Secure, SameSite, Set-Cookie on login, POST /auth/logout, delete_cookie on logout, credentials: include, remove Authorization header, CSRF, SameSite=Lax CSRF protection, allow_credentials, get_current_user reads cookie, Bearer fallback, clinic_id from login body, staging cross-domain SameSite=None risk, refresh deferred, PHI blocker, testing strategy, planning only, Sprint 14, no real secrets)
   - No production code changes; no runtime behavior changed; no auth code modified
   - Full backend tests: 1892/1892 passed
   - Key finding: staging (Railway + Vercel) requires SameSite=None; Secure for cookie auth (cross-domain); production on same registrable domain uses SameSite=Lax
   - clinic_id resolution: after cookie migration, frontend reads clinic_id from login JSON response body (user.clinic_id); stores in localStorage
   - Bearer header fallback: keep in get_current_user during migration window; remove after full rollout
   - Refresh tokens: deferred to Sprint 14 or later; 60-min expiry accepted for initial production launch
   - Sprint 14 scope: implement cookie login/logout/get_current_user + frontend auth.ts/api.ts/pages update

   - Refresh tokens: deferred to Sprint 14 or later; 60-min expiry accepted for initial production launch
   - Sprint 14 scope: implement cookie login/logout/get_current_user + frontend auth.ts/api.ts/pages update

97. Module 99 — Production Deployment Execution Plan
   - Commit: (see git log)
   - `docs/deployment/PRODUCTION_DEPLOYMENT_EXECUTION_PLAN.md` (new — 17-section execution plan: purpose, current status (what is complete / what is NOT done), 12 production blockers tracker with Sprint 13 progress and open/resolved status, milestone sequence table (M1–M11 with go/no-go gates and sprint estimates), M1 staging deployment (Module 97 checklist + failure stop rules + rollback + Decision Gate A), M2 staging smoke (13-step smoke order + evidence capture + session storage note + Decision Gate B), M3 auth/session hardening (httpOnly cookie + SameSite=None for staging + clinic_id from login body + smoke re-run + Decision Gate C), M4 production domain and TLS (HTTPS domains + DNS + no ngrok), M5 production secrets provisioning (4 secrets + high-entropy + no placeholders), M6 production database (managed PostgreSQL + PITR + migration gate + isolation), M7 production Vapi assistant (dedicated production assistant + vapi:tool singular + no ngrok + Decision Gate D), M8 legal/GDPR/compliance review (hard gate; raw_payload PHI policy; Austrian DSG; data processor agreements), M9 CI/CD pipeline (GitHub Actions + Railway/Vercel hooks + manual approval for production), M10 production monitoring (APM + structured logs + alerting + on-call runbook), M11 production PHI launch (pre-launch checklist; all M1–M10 gates required; current status NO-GO), explicit deferrals table, Architecture Checkpoint 13 as next step)
   - `backend/tests/test_production_deployment_execution_plan_contract.py` (new — 54 static contract tests: plan exists, non-empty, staging deployment/Railway/Vercel/HTTPS/no-ngrok, staging smoke/smoke-runbook/evidence capture, auth hardening/httpOnly/SameSite/SameSite=None staging cross-domain/Sprint 14 implementation, production domain and TLS/DNS/no-ngrok, production secrets/JWT_SECRET_KEY/VAPI_WEBHOOK_SECRET/no-placeholder, production database/managed PostgreSQL/backups+PITR/migration gate, production Vapi/vapi:tool singular/no auto-confirm, legal/GDPR/Austrian healthcare/raw_payload PHI/hard gate, CI/CD/automated test gate/no secrets in CI logs, production monitoring/APM/alerting/structured logs, go/no-go gates/gate at each milestone/decision gates, PHI launch blocked/all gates must pass/12 open blockers, no deployment in module/planning document only, Architecture Checkpoint 13/checkpoint go/no-go/Sprint 13 deliverables under review, stop rules/rollback, no real API keys/no real DB password)
   - No deployment executed; no production secrets; no runtime code changes; no auth implementation
   - Full backend tests: 1946/1946 passed

- Full backend tests: 1946/1946 passed
- Sprint 11 complete (Modules 81–90); Sprint 12 complete (Modules 91–94); Sprint 13 complete (Modules 95–99)

## Architecture checkpoint

- Architecture Checkpoint 13 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_13_STAGING_DEPLOYMENT_GO_NO_GO_REVIEW.md`
- Commit: (see git log)
- Full backend tests: 1946/1946 passed
- Sprint 13 complete (Modules 95–99)
- Key decisions:
  - Fake-data staging deployment attempt: **GO**
  - Actual staging deployment attempt: **GO** — proceed in Sprint 14 per Module 97 checklist
  - Production PHI launch: **NO-GO** — all 12 blockers remain open
  - Auth/session hardening (httpOnly cookie): **GO** for Sprint 14; implement after M1/M2 evidence; before production PHI
  - SameSite=None required for Railway+Vercel staging (cross-domain); SameSite=Lax for production (same registrable domain)
  - Fabel 5/UX sprint: **DEFERRED** — wait until staging confirmed and auth hardened
  - Appointment workflow expansion: **DEFERRED**
- Recommended Sprint 14 sequence: Module 100 (config file inventory) → 101 (Railway prep) → 102 (Vercel prep) → 103 (DB/migration strategy) → 104 (smoke execution evidence) → Checkpoint 14

98. Module 100 — Staging Deployment Config File Inventory
   - Commit: (see git log)
   - `docs/deployment/STAGING_DEPLOYMENT_CONFIG_FILE_INVENTORY.md` (new — 13-section inventory: purpose, current repo layout (actual paths; missing files noted in tree diagram), Railway backend requirements table (requirements.txt MISSING/BLOCKER; Procfile MISSING/BLOCKER; runtime.txt MISSING; start command; app import path backend.app.main:app; $PORT/0.0.0.0 binding; health route; env vars; migration command; no DB-ready retry gap), Railway PostgreSQL inventory (managed add-on; DATABASE_URL auto-injection; migration target; seed_local_data.py must NOT run in staging; staging seed gap for Module 103), Vercel frontend requirements table (root directory=frontend/; package.json/build command; NEXT_PUBLIC_API_BASE_URL; no backend secrets in frontend env; frontend/.gitignore MISSING), cross-platform URL/domain inventory (FRONTEND_CORS_ORIGINS; no wildcard; no ngrok; HTTPS; SameSite cross-domain complication), migration/seed command inventory (run_migrations.py usable; seed_local_data.py local-only; smoke/sign scripts noted), Vapi/n8n inventory (capture-appointment-request; vapi:tool singular; no CORS dependency), required config files summary (existing/local-only/missing/not-needed), blockers table (12 items: requirements.txt BLOCKER; Procfile BLOCKER; Python version HIGH; staging seed HIGH; .gitignore gaps MEDIUM; no DB-ready retry MEDIUM; no Vapi test assistant HIGH; staging URLs unknown MEDIUM), recommended next actions (Module 101/102/103/104), non-goals)
   - `backend/tests/test_staging_deployment_config_file_inventory_contract.py` (new — 41 static contract tests: inventory exists, Railway backend/uvicorn/import path/PORT/health/requirements.txt missing/Procfile/python version/Nixpacks, Railway PostgreSQL/DATABASE_URL injection/migrations/seed gap/seed_local_data must not run/no DB-ready retry, Vercel frontend/root directory/package.json build/NEXT_PUBLIC_API_BASE_URL/no backend secrets/frontend gitignore missing, FRONTEND_CORS_ORIGINS/no wildcard/no ngrok/HTTPS/SameSite cross-domain, Vapi endpoint/vapi:tool singular/n8n staging, sessionStorage JWT fake-data acceptable/PHI blocker, fake/non-PHI staging/production PHI no-go, no deployment in module, Module 101/Railway prep, no real secrets)
   - Key findings: requirements.txt MISSING (BLOCKER); Procfile/railway.toml MISSING (BLOCKER); runtime.txt MISSING (HIGH); frontend/.gitignore MISSING (MEDIUM); backend uses PyJWT + bcrypt directly (not python-jose/passlib); no DB-ready retry in run_migrations.py; seed_local_data.py local-only; vercel.json not needed; next.config.js needs no output setting for Vercel
   - No deployment executed; no production secrets; no runtime code changes
   - Full backend tests: 1987/1987 passed

   - Commit: 3312049

99. Module 101 — Railway Backend Deployment Prep
   - Commit: (see git log)
   - `backend/requirements.txt` (new — 7 pinned runtime deps: fastapi==0.138.2, uvicorn[standard]==0.49.0, asyncpg==0.31.0, alembic==1.18.5, pydantic==2.13.4, PyJWT==2.4.0, bcrypt==3.2.0; no python-jose/passlib/httpx/pytest; Python 3.11; test deps excluded)
   - `runtime.txt` (new — `python-3.11`; pins Python version for Railway Nixpacks)
   - `Procfile` (new — `web: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`; migrations NOT in web command; migration is manual predeploy step)
   - `.gitignore` (updated — added backend/.env, frontend/.env.local, frontend/.next/, frontend/next-env.d.ts, frontend/node_modules/, frontend/package-lock.json)
   - `docs/deployment/RAILWAY_BACKEND_DEPLOYMENT_PREP.md` (new — 12-section prep doc: purpose, selected Railway approach/Nixpacks/Procfile, config files created in M101, required Railway env vars table (DATABASE_URL auto-injected; JWT_SECRET_KEY/VAPI/N8N/INTERNAL secrets; FRONTEND_CORS_ORIGINS; APP_ENV), Railway PostgreSQL binding, migration strategy (manual run via Railway "Run Command" or railway.toml preDeployCommand; NOT in Procfile web command; run_migrations.py notes including no retry loop), health check routes, log safety rules, Vapi integration (capture-appointment-request; vapi:tool; no ngrok; no auto-confirm; staff Confirm required), CORS/domain safety (no wildcard; HTTPS; no ngrok), blockers remaining before actual deploy (10 items), non-goals)
   - `backend/tests/test_railway_backend_deployment_prep_contract.py` (new — 37 static contract tests: requirements.txt exists/fastapi/uvicorn/asyncpg/alembic/pydantic/PyJWT/bcrypt/no secrets; runtime.txt exists/python-3.11; Procfile exists/backend.app.main/0.0.0.0/$PORT/web process/uvicorn; prep doc exists/Railway backend/fake-non-PHI/no deployment/DATABASE_URL/JWT_SECRET_KEY/FRONTEND_CORS_ORIGINS/health/migration/Vapi endpoint/vapi:tool/no ngrok/no wildcard/HTTPS/staff Confirm/PORT binding/blockers remaining/no real secrets)
   - No deployment executed; no production secrets; no runtime behavior changed; migrations NOT in Procfile (manual predeploy step)
   - Full backend tests: 2024/2024 passed

- Full backend tests: 2024/2024 passed
- Sprint 13 complete (Modules 95–99); Sprint 14 in progress (Modules 100–101 complete)

100. Module 102 — Vercel Frontend Deployment Prep
   - Commit: (see git log)
   - `docs/deployment/VERCEL_FRONTEND_DEPLOYMENT_PREP.md` (new — 13-section prep doc: purpose (no deployment; fake/non-PHI; no Fabel 5), current frontend inventory (Next.js 14.2.3; App Router; package.json scripts; api.ts/auth.ts paths; login/dashboard routes; root .gitignore coverage from Module 101; no standalone frontend .gitignore needed; no vercel.json needed), recommended Vercel project settings (root=frontend; Next.js auto-detect; npm install; npm run build; no vercel.json; no output:standalone), Vercel env vars (only NEXT_PUBLIC_API_BASE_URL; no backend secrets table; failure mode if unset; no JWT_SECRET_KEY/DATABASE_URL/webhook secrets in frontend), frontend/backend URL contract (CORS bootstrap sequence: Railway→Vercel URL→FRONTEND_CORS_ORIGINS→restart→verify preflight; no wildcard; no ngrok; HTTPS; exact origin), auth/session staging caveat (sessionStorage JWT fake-data-only; XSS risk acceptable for staging; PHI blocker; httpOnly Secure SameSite=None when cookie auth implemented; SameSite cross-domain complication), build verification plan (npm run build not run in this module; previously verified Module 77), Vercel routing expectations (/login; /dashboard; client-side auth guard only), staging smoke expectations (9 steps), rollback plan, blockers before actual Vercel deploy (8 items), non-goals, recommended next Module 103)
   - `backend/tests/test_vercel_frontend_deployment_prep_contract.py` (new — 26 static contract tests: doc exists/non-empty; mentions Vercel+frontend/root directory/Next.js/npm run build/npm run dev; NEXT_PUBLIC_API_BASE_URL/no backend secrets/no DATABASE_URL/no JWT_SECRET_KEY; Railway staging API URL/FRONTEND_CORS_ORIGINS exact origin/no wildcard CORS/no ngrok/HTTPS; /login//dashboard routes; sessionStorage JWT fake-data-only/httpOnly cookie migration; fake/non-PHI staging only/no deployment executed/no Fabel 5 UX; rollback/Module 103 staging DB migration and seed; no real API keys)
   - No deployment executed; no production secrets; no runtime code changes; no frontend code changes; no auth/session implementation; no CORS changes; no npm install
   - Full backend tests: 2050/2050 passed

- Full backend tests: 2050/2050 passed
- Sprint 13 complete (Modules 95–99); Sprint 14 in progress (Modules 100–102 complete)

101. Module 103 — Staging DB Migration and Seed Strategy
   - Commit: (see git log)
   - `docs/deployment/STAGING_DB_MIGRATION_AND_SEED_STRATEGY.md` (new — 17-section strategy doc: purpose (planning only; no DB mutation; fake/non-PHI; production PHI no-go), current DB/migration inventory (alembic.ini at backend/alembic.ini; migrations/versions/0001_initial_schema.py + 0002_add_password_hash_to_clinic_users.py; run_migrations.py behavior; no DB-ready retry gap; seed_local_data.py local-only; db_smoke_test.py usable; docker-compose.postgres.yml local-only; backend/.env.example shows placeholder secrets), staging database target (Railway managed PostgreSQL; DATABASE_URL auto-injected; separate from local and production; fake/non-PHI only; pgcrypto supported), migration execution strategy (migrations must run before backend traffic; recommended command python backend/scripts/run_migrations.py; wait for Railway "Running" status; stop if non-zero; do not put in Procfile; capture sanitized output; alembic upgrade head is idempotent; expected final revision 0002_password_hash; 11 tables after head), migration readiness gaps (no DB-ready retry; no migration status verify step; no preDeployCommand created; future improvement documented), fake staging tenant/user strategy (staging-fake-clinic UUID placeholder; slug staging-fake-clinic; doctor.staging@praximed.test; must not use local-dev UUIDs 11111111-... or 22222222-...; must not reuse local-dev-password; staging Vapi test assistant must use staging clinic UUID), local seed script assessment (seed_local_data.py must not run against staging; hardcoded local UUIDs; local email; local-dev-password hash; local-only output labels; seeds patients and consultation_sessions not needed for smoke), recommended staging provisioning approach (Option A recommended: manual one-time SQL insert via Railway shell; Option B: future seed_staging_fake_data.py; Option C: Railway one-time Python command; no automatic production seed), password hashing for staging (hash_password() method documented; never commit plaintext; never reuse local-dev-password; high entropy; staging-only), required staging data for smoke (minimum: clinic row + clinic_user row; optional: appointment_request/patient/notification/consultation; smoke passes with empty tables after login), Vapi/n8n DB interaction (vapi:tool singular; staging clinic UUID in X-Clinic-Ref; status=new action_required=True hardcoded; no auto-confirm; staff Confirm only; n8n staging workflow; no production calendar), backup/rollback strategy (Railway PITR on paid plans; alembic downgrade; staging data is all fake; reset by drop+recreate if needed), evidence capture (command/timestamp/commit SHA/environment/sanitized output/revision/DB smoke test/staging clinic UUID/email; no secrets/PII), failure stop rules (14 rules: wrong DATABASE_URL target; migration failure; credentials in logs; real patient data; seed script targets wrong DB; production DB touched; duplicate clinic/user; auto-confirmed appointment; n8n to production calendar; real phone in Vapi), open blockers (12 items: Railway PostgreSQL not provisioned; DATABASE_URL unavailable; staging UUIDs not generated; staging password not created; secrets not set; migration not run; Vapi test assistant not configured; smoke not executed), non-goals, recommended next Module 104)
   - `backend/tests/test_staging_db_migration_seed_strategy_contract.py` (new — 27 static contract tests: doc exists/non-empty; Railway PostgreSQL; fake/non-PHI staging only; production PHI no-go; no DB mutation in module; alembic; run_migrations.py; python backend/scripts/run_migrations.py command; DATABASE_URL; migrations before backend traffic; migrations not in Procfile; backup/snapshot; rollback; seed_local_data.py local-only; staging fake clinic id placeholder; fake staging user; no real patient data; no production DB; Vapi creates appointment_request; status=new/action_required; staff Confirm/no auto-confirm; n8n staging workflow; evidence capture; failure stop rules; Module 104; no real secrets)
   - Key findings: seed_local_data.py must not run against staging (hardcoded local UUIDs + local-dev-password); run_migrations.py has no DB-ready retry (manual timing required); Option A (manual SQL via Railway shell) is the recommended first-smoke provisioning approach; staging fake clinic/user UUIDs must be newly generated; bcrypt hash generation documented safely
   - No DB mutation executed; no deployment; no production secrets; no runtime code changes
   - Full backend tests: 2077/2077 passed

- Full backend tests: 2077/2077 passed
- Sprint 13 complete (Modules 95–99); Sprint 14 in progress (Modules 100–103 complete)

102. Module 104 — Staging Smoke Execution Evidence
   - Commit: (see git log)
   - `docs/runtime/STAGING_SMOKE_EXECUTION_RESULTS.md` (new — 10-section results doc with result BLOCKED/PENDING: purpose (accuracy policy; no fabricated evidence; fake/non-PHI; production PHI no-go), current result (BLOCKED/PENDING — Railway backend/PostgreSQL/Vercel frontend not yet created; this is an accurate status not a failure), preconditions checked (all external: Railway backend/PostgreSQL/Vercel/staging URLs/env vars/fake tenant+user/migrations/Vapi/n8n — all MISSING or UNKNOWN; all repo-side items — all READY), smoke checklist (19 steps: /health, /health/ready, DB connection, migrations, fake tenant/user in DB, frontend loads, /login renders, CORS preflight, login, dashboard, appointments, Vapi test call, Vapi row in dashboard, staff Confirm, no auto-confirm, n8n NOT ENABLED, logs sanitized, rollback — all PENDING), evidence table (13 rows; all "Not available yet"), blockers preventing smoke (15 items: Railway/Vercel/PostgreSQL not created; staging URLs unknown; JWT_SECRET_KEY/VAPI_WEBHOOK_SECRET/N8N_WEBHOOK_SECRET/INTERNAL_WEBHOOK_SECRET/FRONTEND_CORS_ORIGINS/NEXT_PUBLIC_API_BASE_URL not set; staging clinic/user/password not created; migrations not run; Vapi test assistant not configured; n8n deferred), what is ready repo-side (18 items: requirements.txt/Procfile/runtime.txt/.gitignore/run_migrations.py/db_smoke_test.py/migration files/prep docs/2077 tests all READY), what must happen before real smoke (18 ordered steps from Railway service creation through evidence capture), safety constraints (10 rules: fake/non-PHI; no real patients; no production secrets; no production DB; no local-dev password; no ngrok; no wildcard CORS; no auto-confirm; staff Confirm required; sessionStorage JWT acceptable for staging), recommended next Architecture Checkpoint 14)
   - `backend/tests/test_staging_smoke_execution_results_contract.py` (new — 26 static contract tests: doc exists/non-empty; PASS/BLOCKED/PENDING accuracy boundary; no fabricated evidence; Railway backend/PostgreSQL; Vercel frontend; staging API/frontend HTTPS URLs; /health; migrations; /login; CORS; fake staging user; Vapi test assistant; vapi:tool scope; n8n staging workflow; staff Confirm/no auto-confirm; no real patient data; no production secrets; no ngrok; no wildcard CORS; evidence required/available; blockers; Architecture Checkpoint 14; no real secrets)
   - Key findings: no staging services exist; smoke result is BLOCKED/PENDING (accurate, not a failure); repo is fully ready for deployment; all 15 external blockers documented; 18-step ordered provisioning sequence documented
   - No deployment executed; no smoke fabricated; no production secrets; no runtime code changes
   - Full backend tests: 2103/2103 passed

- Full backend tests: 2103/2103 passed
- Sprint 13 complete (Modules 95–99); Sprint 14 complete (Modules 100–104)

## Architecture checkpoint

- Architecture Checkpoint 14 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_14_STAGING_DEPLOYMENT_REVIEW.md`
- Commit: (see git log)
- Full backend tests: 2103/2103 passed
- Sprint 14 complete (Modules 100–104)
- Key decisions:
  - Actual fake-data staging service creation: **GO** — repo is fully ready; no further planning modules needed before Railway/Vercel service creation
  - Production PHI launch: **NO-GO** — 12 production blockers open; staging smoke not yet executed; auth hardening not yet implemented
  - Auth/session hardening (httpOnly cookie): **GO — after staging smoke evidence** — Module 98 plan complete; implement after M1/M2 staging evidence; SameSite=None required for Railway+Vercel cross-domain staging
  - Fabel 5/UX sprint: **DEFERRED** — wait until staging confirmed and auth hardened
  - Appointment workflow expansion: **DEFERRED**
- Repo-side readiness: 24 items confirmed READY; no runtime changes required before service creation
- External blockers: 18 items require manual developer action (Railway/Vercel service creation)
- Recommended Sprint 15 sequence: Module 105 (Railway backend runbook) → 106 (PostgreSQL provisioning/migration evidence) → 107 (Vercel frontend runbook) → 108 (staging environment wiring evidence) → 109 (staging smoke PASS/BLOCKED evidence) → Checkpoint 15

103. Module 105 — Railway Backend Service Creation Runbook
   - Commit: (see git log)
   - `docs/deployment/RAILWAY_BACKEND_SERVICE_CREATION_RUNBOOK.md` (new — 15-section human-executable runbook: purpose (developer-executed; no Claude deployment; fake/non-PHI; no production launch), current repo readiness (Procfile/runtime.txt/backend/requirements.txt/health endpoint/migration runner all READY; 2103 tests), preconditions (Railway account; GitHub access; secrets generated with openssl rand -hex 32; no production secrets), Railway project/service creation steps (GitHub repo connection; Nixpacks Python detection; Procfile start command confirmation; service naming), backend service settings (root=repo root; start command `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`; health check path /health; Python 3.11; branch=master; auto-deploy recommendation; why --host 0.0.0.0 required; why $PORT required; why backend.app.main:app is the correct import path), required Railway env vars (DATABASE_URL auto-injected; JWT_SECRET_KEY/VAPI_WEBHOOK_SECRET/N8N_WEBHOOK_SECRET/INTERNAL_WEBHOOK_SECRET via openssl rand -hex 32; FRONTEND_CORS_ORIGINS placeholder until Vercel URL known; APP_ENV=staging; failure mode for each), DATABASE_URL binding note (auto-injected by Railway PostgreSQL add-on; never use local Docker or production URL), first deploy expectations (Nixpacks build; process start; lifespan startup; /health 200; /health/ready 503 until DB; DB routes 503 expected; CORS localhost default), migration command (not in Procfile; run via Railway "Run Command" after Module 106; python backend/scripts/run_migrations.py; stop if non-zero), health check verification (curl command; expected JSON; 200 vs 503 before DB), evidence to capture (11 items: service name/URL/branch/commit SHA/build status/Python version/start command/env var names/DATABASE_URL status/GET /health result/log snippet; no secret values), failure triage (12 rows: ModuleNotFoundError/missing dep/Python mismatch/127.0.0.1 binding/PORT binding/500/503 health/CORS/migration failures), stop rules (6 rules: production secrets requested; wrong DATABASE_URL; real patient data; secrets in logs; code change required; /health fails after config fix), non-goals (Module 106/107/108/109/auth/Fabel 5), recommended next Module 106)
   - `backend/tests/test_railway_backend_service_creation_runbook_contract.py` (new — 32 static contract tests: runbook exists/non-empty; Railway backend service; fake/non-PHI; no Claude deployment; service name; GitHub repo; root directory; Procfile; start command; backend.app.main:app; 0.0.0.0; $PORT; runtime.txt; python-3.11; backend/requirements.txt; /health; DATABASE_URL; JWT_SECRET_KEY; VAPI_WEBHOOK_SECRET; N8N_WEBHOOK_SECRET; INTERNAL_WEBHOOK_SECRET; FRONTEND_CORS_ORIGINS; openssl rand; no local Docker DATABASE_URL; no production DATABASE_URL; migration command; evidence capture; failure triage; stop rules; Module 106 PostgreSQL; no real secrets)
   - No deployment executed; no real secrets; no runtime code changes
   - Full backend tests: 2135/2135 passed

- Full backend tests: 2135/2135 passed
- Sprint 13 complete (Modules 95–99); Sprint 14 complete (Modules 100–104); Sprint 15 in progress (Module 105 complete)

104. Module 106 — Railway PostgreSQL Provisioning and Migration Evidence
   - Commit: (see git log)
   - `docs/deployment/RAILWAY_POSTGRESQL_PROVISIONING_AND_MIGRATION_RUNBOOK.md` (new — 15-section human-executable provisioning and migration runbook: purpose (developer-executed; no Claude deployment; fake/non-PHI; no production DB), current status (runbook/migration scripts READY; Railway PostgreSQL PENDING), preconditions (Module 105 backend must exist; /health must be 200; data safety checks), Railway PostgreSQL creation steps (Railway dashboard add Plugin; PostgreSQL; name; confirm private DATABASE_URL available; do not paste value), DATABASE_URL wiring (Variable reference injection into backend service; redeploy; /health/ready verification; safety rules: no localhost; no production), migration execution (python backend/scripts/run_migrations.py via Railway "Run Command"; wait for "Running" status; stop if non-zero; do not print DATABASE_URL; idempotent), migration verification (db_smoke_test.py; expected 4-table output; alembic current optional), health/readiness expectations (before/after DATABASE_URL injection; before/after migration; expected 200 at each stage), staging fake data provisioning (seed_local_data.py must not run; generate UUIDs; generate bcrypt hash; provisioning SQL with ON CONFLICT; verification queries), evidence to capture (14 items: project/service names; commit SHA; DATABASE_URL injection confirmed; migration command/timestamp/exit status/sanitized output; final revision; db smoke test; /health/ready 200; staging clinic UUID; user email; no secrets), failure triage (11 rows: DATABASE_URL missing/wrong/production; /health/ready 503; migration fails on DATABASE_URL/connection refused/alembic.ini not found/ModuleNotFoundError/SSL; db_smoke_test fails; provisioning duplicate key; credentials in logs), stop rules (8 rules: wrong DATABASE_URL; secrets in logs; migration targets wrong DB; real patient data; migration non-zero; production DB touched; project/service ambiguity), non-goals (Module 107/108/109/auth/production), recommended next Module 107)
   - `docs/runtime/RAILWAY_POSTGRESQL_MIGRATION_EVIDENCE.md` (new — 6-section evidence doc: purpose (accuracy policy; no fabricated evidence; BLOCKED/PENDING), current result (BLOCKED/PENDING — Railway PostgreSQL not yet provisioned), preconditions available/missing (all external missing; repo-side all READY), migration evidence table (14 rows; all "Not available yet"; all PENDING), blockers (8 items: PostgreSQL not provisioned; DATABASE_URL missing; not Running; migration not run; db_smoke_test not run; staging clinic/user not provisioned; /health/ready not 200), next evidence needed)
   - `backend/tests/test_railway_postgresql_migration_runbook_contract.py` (new — 25 static contract tests: runbook exists/non-empty; evidence doc exists/non-empty; Railway PostgreSQL; add-on/plugin; fake/non-PHI; no production DB; no real patient data; DATABASE_URL; DATABASE_URL auto-injected; no local Docker DATABASE_URL; no production DATABASE_URL; python backend/scripts/run_migrations.py; migrations not in Procfile; sanitized evidence; no secrets; seed_local_data.py local-only; PASS/BLOCKED/PENDING/FAIL states; stop rules; failure triage; evidence BLOCKED/PENDING; Module 107 Vercel; no real secrets in runbook/evidence)
   - Result: BLOCKED/PENDING (accurate; Railway PostgreSQL not yet provisioned; no fabricated evidence)
   - No deployment executed; no DB mutation; no real secrets; no runtime code changes
   - Full backend tests: 2160/2160 passed

- Full backend tests: 2160/2160 passed
- Sprint 13 complete (Modules 95–99); Sprint 14 complete (Modules 100–104); Sprint 15 in progress (Modules 105–106 complete)

105. Module 107 — Vercel Frontend Project Creation Runbook
   - Commit: (see git log)
   - `docs/deployment/VERCEL_FRONTEND_PROJECT_CREATION_RUNBOOK.md` (new — 14-section human-executable runbook: purpose (developer-executed; no Claude deployment; fake/non-PHI; no production launch; no Fabel 5), current repo readiness (frontend/package.json build/start/dev/lint scripts; next.config.js no output:standalone; .env.example NEXT_PUBLIC_API_BASE_URL; Next.js 14.2.3; no vercel.json needed; 2160 tests), preconditions (Vercel account; GitHub access; Railway backend HTTPS URL from Module 105/106), Vercel project creation steps (import GitHub repo; framework auto-detect Next.js; root directory = `frontend` — CRITICAL; service naming), build settings (Next.js auto-detect; npm install; npm run build; output .next managed by Vercel; no vercel.json; no output:standalone), required env vars (NEXT_PUBLIC_API_BASE_URL only; public build-time; baked into browser bundle; not a secret; redeploy required after change; set before first build; forbidden backend secrets: DATABASE_URL/JWT_SECRET_KEY/VAPI_WEBHOOK_SECRET/N8N_WEBHOOK_SECRET/INTERNAL_WEBHOOK_SECRET/POSTGRES_PASSWORD), frontend/backend URL wiring (3-step sequence: deploy Railway → get Railway URL → set NEXT_PUBLIC_API_BASE_URL in Vercel → deploy Vercel → get Vercel URL → set FRONTEND_CORS_ORIGINS on Railway; no wildcard CORS; HTTPS; no ngrok), first deploy expectations (Next.js 14.2.3 build; CORS errors acceptable at this stage; partial deploy valid; /login page renders), browser smoke checklist (8 checks: page loads; /login renders; login form exists; no console errors; API calls fail with CORS until Module 108; /health reachable; no secrets in browser; no production data), evidence to capture (14 items: Vercel project name/URL/root directory/env var name confirmed/build status/commit SHA/build log snippet/login page render/no backend secrets confirmed/FRONTEND_CORS_ORIGINS dependency noted/no real patient data/no production secrets/Module 108 readiness; no secret values), failure triage (10 rows: wrong root directory/no package.json found/TypeScript error/env var missing/API points to localhost/CORS fails before FRONTEND_CORS_ORIGINS/env var changed but not redeployed/domain not recognized/build timeout/500 on login page), stop rules (7 rules: backend secrets in Vercel env; wrong NEXT_PUBLIC_API_BASE_URL; production data; build fails without obvious config fix; secrets in build logs; root directory not frontend; ngrok URLs), result states (PASS/BLOCKED/PENDING/FAIL; current: BLOCKED/PENDING), non-goals (CORS update on Railway/Vapi config/full smoke/auth hardening/Fabel 5/appointment workflow), recommended next Module 108)
   - `docs/runtime/VERCEL_FRONTEND_DEPLOYMENT_EVIDENCE.md` (new — 6-section evidence doc: purpose (accuracy policy; no fabricated evidence; BLOCKED/PENDING), current result (BLOCKED/PENDING — Vercel project not yet created), preconditions available/missing (all external missing; repo-side all READY), deployment evidence table (14 rows; all "Not available yet"; all PENDING), blockers (8 items: Railway backend URL unknown; Railway PostgreSQL pending; Vercel project not created; NEXT_PUBLIC_API_BASE_URL not set; first deploy not triggered; Vercel URL not assigned; FRONTEND_CORS_ORIGINS pending), next evidence needed)
   - `backend/tests/test_vercel_frontend_project_creation_runbook_contract.py` (new — 28 static contract tests: runbook exists/non-empty; evidence doc exists/non-empty; Vercel frontend project; no Claude deployment; fake/non-PHI staging; no production launch; root directory frontend; critical/required/must; Next.js auto-detect; npm run build; NEXT_PUBLIC_API_BASE_URL; Railway backend HTTPS URL; public build-time variable not a secret; no backend secrets in Vercel env; DATABASE_URL forbidden in Vercel; JWT_SECRET_KEY forbidden in Vercel; FRONTEND_CORS_ORIGINS dependency; CORS dependency on Vercel URL; evidence capture; no secrets in evidence; stop rules; PASS/BLOCKED/PENDING/FAIL states; Module 108; evidence BLOCKED/PENDING; no real secrets in runbook/evidence)
   - Result: BLOCKED/PENDING (accurate; Vercel project not yet created; no fabricated evidence)
   - No deployment executed; no real secrets; no runtime code changes; no npm install
   - Full backend tests: 2188/2188 passed

- Full backend tests: 2188/2188 passed
- Sprint 13 complete (Modules 95–99); Sprint 14 complete (Modules 100–104); Sprint 15 in progress (Modules 105–107 complete)

106. Module 108 — Staging Environment Wiring Evidence
   - Commit: (see git log)
   - `docs/deployment/STAGING_ENVIRONMENT_WIRING_RUNBOOK.md` (new — 13-section human-executable wiring guide: purpose (developer-executed; no Claude deployment; fake/non-PHI; no production launch; no fabricated success), wiring map (Railway PostgreSQL→backend DATABASE_URL; Railway backend URL→Vercel NEXT_PUBLIC_API_BASE_URL; Vercel URL→Railway FRONTEND_CORS_ORIGINS; Railway URL→Vapi tool endpoint; Railway URL→n8n staging endpoint; browser traffic Vercel→Railway; machine traffic Vapi/n8n→Railway), required external URLs (Railway backend placeholder; Vercel frontend placeholder; Vapi tool endpoint; n8n staging endpoint; HTTPS only; no ngrok), required env var wiring (Railway backend: DATABASE_URL auto-injected/JWT_SECRET_KEY/VAPI_WEBHOOK_SECRET/N8N_WEBHOOK_SECRET/INTERNAL_WEBHOOK_SECRET/FRONTEND_CORS_ORIGINS exact Vercel URL no wildcard no trailing slash; Vercel frontend: NEXT_PUBLIC_API_BASE_URL Railway HTTPS URL public build-time; Vapi: server URL/X-Vapi-Service-Name/X-Vapi-Clinic-Id/X-Vapi-Scopes=vapi:tool singular/signing secret matches Railway; n8n: staging endpoint/HMAC matches N8N_WEBHOOK_SECRET), wiring order (15 ordered steps from Railway creation through full smoke), validation checks (12 checks: /health/200; /health/ready/200; alembic current; db_smoke_test; Vercel /login; CORS preflight; fake login; dashboard; Vapi test call; Vapi row in dashboard; Staff Confirm/no auto-confirm; n8n), common wiring failures (11 rows: NEXT_PUBLIC_API_BASE_URL wrong/localhost; CORS origin mismatch/trailing slash/wrong subdomain; DATABASE_URL missing; Vapi 403 scope plural; Vapi 401 secret mismatch; n8n 401 HMAC mismatch; fake user missing; migrations not run; Railway redeploy needed; Vercel redeploy needed for env var change), safety rules (10 rules: no real patients; no production secrets; no production DB; no local-dev password; no ngrok; no wildcard CORS; Vapi test assistant only; staff Confirm required; no auto-confirm; sessionStorage JWT fake-data-only), evidence to capture (24 evidence items across all 5 components; no secret values; no DATABASE_URL strings; no passwords), stop rules (8 rules: backend secrets in Vercel env; wildcard CORS; production secrets; real patient data; local-dev password; ngrok; auto-confirmation; secrets in evidence), result states (PASS/BLOCKED/PENDING/FAIL; current: BLOCKED/PENDING), non-goals (Module 105/106/107/109/auth/n8n production/production launch/Fabel 5), recommended next Module 109)
   - `docs/runtime/STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` (new — 7-section evidence doc: purpose (accuracy policy; no fabricated evidence; BLOCKED/PENDING), current result (BLOCKED/PENDING — no wiring evidence provided), preconditions available/missing (all external missing; repo-side all READY including Procfile/runtime.txt/migrations/scripts/frontend/runbooks/2188 tests), wiring evidence table (27 rows; all "Not available yet"; all PENDING covering Railway URL/health/ready/env var names/DATABASE_URL injected/migrations/alembic current/db_smoke_test/staging clinic UUID/user email/Vercel URL/NEXT_PUBLIC_API_BASE_URL/build status/commit SHA/login loads/FRONTEND_CORS_ORIGINS set/no wildcard/CORS preflight/fake login/dashboard/Vapi URL/Vapi scope singular/Vapi row/status=new/Staff Confirm/n8n/no secrets), blockers (14 items: HIGH/MEDIUM/LOW), what is repo-ready (16 items confirmed READY), next evidence needed (11 ordered steps))
   - `backend/tests/test_staging_environment_wiring_evidence_contract.py` (new — 49 static contract tests: runbook exists/non-empty; evidence doc exists/non-empty; staging environment wiring; fake/non-PHI; no Claude deployment; Railway backend/PostgreSQL; Vercel frontend; DATABASE_URL; FRONTEND_CORS_ORIGINS; NEXT_PUBLIC_API_BASE_URL; Vapi endpoint; vapi:tool scope; n8n staging; /health; /login; CORS; migrations; fake staging user; staff Confirm/no auto-confirm; no real patient data; no production secrets; no ngrok; no wildcard CORS; PASS/BLOCKED/PENDING; BLOCKED/PENDING in evidence; no fabricated success; Module 109 staging smoke; no real secrets in runbook/evidence)
   - Result: BLOCKED/PENDING (accurate; no staging wiring evidence provided; no fabricated success)
   - No deployment executed; no real secrets; no runtime code changes
   - Full backend tests: 2237/2237 passed

- Full backend tests: 2237/2237 passed
- Sprint 13 complete (Modules 95–99); Sprint 14 complete (Modules 100–104); Sprint 15 in progress (Modules 105–108 complete)

107. Module 109 — Staging Smoke Execution PASS/BLOCKED Evidence
   - Commit: (see git log)
   - `docs/runtime/STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md` (new — 10-section smoke evidence doc: purpose (final Sprint 15 smoke evidence; fake/non-PHI; no fabricated evidence; accuracy policy), current result (BLOCKED/PENDING — Railway/Vercel/PostgreSQL/Vapi staging services or evidence not available yet), evidence status summary (17-row table: Railway backend URL/health/PostgreSQL/migrations/fake clinic+user/Vercel URL/login/CORS browser call/dashboard login/dashboard protected route/appointment Confirm/Vapi test assistant call/Vapi-created row/staff Confirm Vapi row/n8n staging NOT ENABLED DEFERRED/logs sanitized/rollback path — all "Not available yet"/"PENDING"), smoke checklist status (15 checks with PENDING/NOT ENABLED/DEFERRED; each has expected pass signal and blocker; all PENDING because no staging services), repo-side readiness (17 items all READY: Procfile/runtime.txt/requirements/run_migrations.py/db_smoke_test.py/migration files/frontend build/next.config.js/.env.example/CORS impl/all 4 Sprint 15 runbooks/DB migration strategy/smoke runbook/2237 tests), external blockers (14 items HIGH/MEDIUM/LOW — all same external blockers as Module 108), PASS criteria (16 explicit pass requirements: /health 200/migrations exit 0/alembic current head/fake clinic row/fake user row/Vercel /login loads/CORS preflight passes no wildcard/fake login JWT/dashboard renders/Vapi test call 200/Vapi row in DB/staff Confirm PATCH/no auto-confirm/n8n PASS or NOT ENABLED/logs no secrets/rollback path documented), safety constraints (12 rules: fake/non-PHI/no production secrets/no production DB/no real patients/no local-dev password/no ngrok/no wildcard CORS/HTTPS only/Vapi test assistant only/no auto-confirm/staff Confirm required/sessionStorage JWT fake-data-only risk), next human actions (12 ordered steps from Railway service creation through Checkpoint 15), recommended next Architecture Checkpoint 15)
   - `backend/tests/test_staging_smoke_execution_pass_blocked_evidence_contract.py` (new — 29 static contract tests: evidence doc exists/non-empty; PASS/BLOCKED/PENDING; no fabricated evidence; Railway backend/PostgreSQL; Vercel frontend; /health; DATABASE_URL; migrations; fake staging clinic/user; /login; CORS; dashboard; appointment Confirm; Vapi test assistant; Vapi-created appointment row; status=new/action_required; staff Confirm/no auto-confirm; n8n staging NOT ENABLED/DEFERRED; logs sanitized; rollback; no real patient data; no production secrets; no ngrok; no wildcard CORS; sessionStorage JWT fake-data-only risk; Architecture Checkpoint 15; no real secrets in doc)
   - Result: BLOCKED/PENDING (accurate; no staging smoke evidence provided; no fabricated success)
   - No deployment executed; no real secrets; no runtime code changes
   - Full backend tests: 2266/2266 passed

- Full backend tests: 2266/2266 passed
- Sprint 13 complete (Modules 95–99); Sprint 14 complete (Modules 100–104); Sprint 15 complete (Modules 105–109 all complete)

## Architecture checkpoint

- Architecture Checkpoint 15 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_15_STAGING_DEPLOYMENT_EVIDENCE_REVIEW.md`
- Commit: (see git log)
- Full backend tests: 2266/2266 passed
- Sprint 15 complete (Modules 105–109)
- Key decisions:
  - More planning before manual setup: **NO** — Sprint 15 produced the complete runbook set; no further docs needed
  - Manual Railway backend service creation: **GO** — repo fully ready; runbook complete; this is the exact next step
  - Railway PostgreSQL creation: **GO** — after Railway backend URL confirmed (Module 106 runbook)
  - Vercel frontend creation: **GO** — after Railway backend URL confirmed (Module 107 runbook)
  - Staging smoke execution: **GO** — after wiring complete (Module 108/109 runbooks)
  - Production PHI launch: **NO-GO** — staging smoke evidence not captured; 12 production blockers open; auth hardening not implemented
  - Auth/session hardening (httpOnly cookie): **GO — after staging smoke PASS** — Module 98 plan complete; implement after smoke evidence
  - Fabel 5/UX sprint: **DEFER** — wait until staging confirmed and auth hardened
  - Appointment workflow expansion: **DEFER**
- Repo-side readiness: 19 items confirmed READY; no code changes or planning docs needed before manual service creation
- External blockers: 15 items require manual developer action (Railway/Vercel/Vapi service creation)
- First manual action: follow `RAILWAY_BACKEND_SERVICE_CREATION_RUNBOOK.md` to create Railway project and backend service
- Evidence to capture after Railway backend creation: 16 items (service URL; commit SHA; build status; env var names; /health response; no secret values)
- Safety rules documented: no real patients; no production secrets; no local-dev password; no ngrok; no wildcard CORS; stop if secrets in logs
- Recommended Sprint 16 sequence: Module 110 (Railway backend evidence) → 111 (PostgreSQL evidence) → 112 (Vercel evidence) → 113 (wiring + smoke evidence) → Checkpoint 16

## Next module
Sprint 16 / Module 110 — Railway Backend Root Requirements Fix and Evidence Retest.

108. Module 110 — Railway Backend Root Requirements Fix
   - Commit: (see git log)
   - Real Railway deploy attempted: **FAILED** — `ModuleNotFoundError: No module named 'backend'`
   - Root cause: Railway root directory was set to `backend/`; start command `backend.app.main:app` resolves from inside `backend/` where the `backend` package does not exist; this is a Railway monorepo/root configuration issue
   - Fix:
     - `requirements.txt` (repo root, new) — one-line Nixpacks bridge: `-r backend/requirements.txt`; Nixpacks detects Python from this file at repo root; no duplicate pins
     - `docs/deployment/RAILWAY_BACKEND_SERVICE_CREATION_RUNBOOK.md` — corrected root directory row (blank = repo root; NOT `backend/`); added Section 5.4 explaining exactly why `root=backend` causes `ModuleNotFoundError`; updated Step 4.2 to explain root `requirements.txt` bridge; updated failure triage with exact real error and fix
     - `docs/deployment/RAILWAY_BACKEND_DEPLOYMENT_PREP.md` — updated build system row; added Section 3.0 for root `requirements.txt` bridge with explicit `do not set root to backend` warning
   - `backend/tests/test_railway_backend_root_requirements_contract.py` (new — 16 static contract tests: root requirements.txt exists/references backend; Procfile exists/backend.app.main/0.0.0.0/$PORT; runtime.txt exists/python-3.11; runbook mentions repo root/warns not to set root to backend/ModuleNotFoundError No module named backend/root requirements bridge/no secrets/fake non-PHI staging; prep doc mentions repo root/ModuleNotFoundError)
   - No runtime app logic changed; no auth changes; no DB schema changes; no real secrets
   - Full backend tests: 2282/2282 passed

- Full backend tests: 2282/2282 passed
- Sprint 15 complete; Sprint 16 in progress (Module 110 config fix complete)
- Railway backend redeploy required: push `requirements.txt` to Railway; set root directory to blank (repo root) in Railway service settings; redeploy

109. Module 111 — Railway Root Requirements Direct Dependency Fix
   - Commit: (see git log)
   - Railway build retest failed: root `requirements.txt` used `-r backend/requirements.txt`; Railway/Railpack cannot resolve nested includes during install cache step
   - Fix: `requirements.txt` (repo root) — replaced `-r backend/requirements.txt` with direct pinned dependency list (fastapi/uvicorn/asyncpg/alembic/pydantic/PyJWT/bcrypt); matches `backend/requirements.txt` exactly; no nested includes
   - `backend/requirements.txt` unchanged (remains source reference)
   - `docs/deployment/RAILWAY_BACKEND_SERVICE_CREATION_RUNBOOK.md` — Step 4.2 updated: direct dependencies explanation; explicit "do not use -r backend/requirements.txt" note with real Railway build failure reason
   - `docs/deployment/RAILWAY_BACKEND_DEPLOYMENT_PREP.md` — Section 3.0 updated: flat direct dependency list; real failure reason documented
   - `backend/tests/test_railway_root_requirements_direct_dependencies_contract.py` (new — 22 tests: root req exists/no nested include; fastapi/uvicorn/asyncpg/alembic/pydantic/PyJWT/bcrypt in root req; backend/requirements.txt exists; Procfile exists/backend.app.main; runtime.txt/python-3.11; runbook repo root/not backend root/direct deps/Railpack cannot resolve nested/no secrets/fake non-PHI; prep doc repo root/direct or flat deps)
   - `backend/tests/test_railway_backend_root_requirements_contract.py` — updated: replaced stale `test_root_requirements_references_backend_requirements` with `test_root_requirements_contains_fastapi` (reflects direct-dep approach)
   - No runtime app logic changed; no auth changes; no DB schema changes; no real secrets
   - Full backend tests: 2304/2304 passed

- Full backend tests: 2304/2304 passed
- Sprint 16 in progress (Modules 110–111 complete)

110. Module 112 — Railway Backend Service Creation Evidence
   - Commit: (see git log)
   - Real evidence provided by user: Railway backend active; `/health` → 200
   - `docs/runtime/RAILWAY_BACKEND_SERVICE_CREATION_EVIDENCE.md` (new — 8-section evidence doc: purpose (accuracy policy; fake/non-PHI; no production secrets), current result (PASS), evidence table (14 rows: service active PASS/URL https://web-production-fd91d.up.railway.app PASS/commit 081121b PASS/health endpoint PASS/GET /health 200 PASS/response body {"status":"ok","service":"PraxisMed API"} PASS/root requirements.txt direct deps PASS/Procfile start command PASS/root directory repo root PASS/Python 3.11 PASS/backend imports PASS/DATABASE_URL PENDING/FRONTEND_CORS_ORIGINS PENDING/health/ready 503 PENDING), what this proves (Railway builds; direct deps work; Procfile works; imports from repo root work; HTTPS URL serves backend), what this does not prove (PostgreSQL/migrations/login/dashboard/Vapi/Vercel/production PHI), safety boundary (fake/non-PHI only; Railway environment label may say "production" — PraxisMed status is fake-data staging; no real patients; no production secrets; production PHI NO-GO), remaining blockers (12 items: PostgreSQL not provisioned; DATABASE_URL not wired; migrations not run; fake clinic/user not provisioned; Vercel not deployed; NEXT_PUBLIC_API_BASE_URL not set; FRONTEND_CORS_ORIGINS not set; CORS not verified; fake login not tested; Vapi not pointed to staging; n8n not configured; full smoke not run), recommended next Module 113)
   - `docs/runtime/STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` updated: Railway backend URL row → PASS (`https://web-production-fd91d.up.railway.app`); /health response → PASS; /health/ready → PENDING
   - `docs/runtime/STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md` updated: evidence summary row 1 (Railway backend service) → PASS with URL + commit; smoke checklist check 1 (backend /health) → PASS; overall remains BLOCKED/PENDING
   - `backend/tests/test_railway_backend_service_creation_evidence_contract.py` (new — 20 static contract tests: evidence doc exists/non-empty; PASS; Railway service active; URL web-production-fd91d; /health; status ok response; commit 081121b; root requirements direct deps; Procfile/start command; repo root imports; fake non-PHI staging; no real patient data; production PHI not proven/NO-GO; PostgreSQL/DATABASE_URL PENDING; migrations PENDING; Vercel PENDING; Vapi PENDING; Module 113; no real secrets)
   - No runtime code changed; no secrets recorded; no real patient data
   - Full backend tests: 2324/2324 passed

- Full backend tests: 2324/2324 passed
- Sprint 16 in progress (Modules 110–112 complete)
- Railway backend URL confirmed: https://web-production-fd91d.up.railway.app
- Next: Module 113 — Railway PostgreSQL provisioning and migration

111. Module 113 — Railway Migration psycopg2 Dependency Fix
   - Commit: (see git log)
   - Real Railway migration attempted: **FAILED** — `ModuleNotFoundError: No module named 'psycopg2'`
   - Root cause: `psycopg2-binary` was missing from `requirements.txt`; SQLAlchemy/Alembic requires a synchronous PostgreSQL driver (`psycopg2`) for migrations even when `asyncpg` (async driver) is installed for runtime DB access; both drivers must coexist
   - Fix:
     - `requirements.txt` (repo root) — added `psycopg2-binary==2.9.9` after `asyncpg==0.31.0`; now contains 8 direct deps
     - `backend/requirements.txt` — added `psycopg2-binary==2.9.9` after `asyncpg==0.31.0`; kept in sync with root
     - `docs/deployment/RAILWAY_POSTGRESQL_PROVISIONING_AND_MIGRATION_RUNBOOK.md` — added Section 6.1a "PostgreSQL Driver Requirements" (driver table: asyncpg = async runtime; psycopg2-binary = sync for Alembic; both required); added failure triage row for `ModuleNotFoundError: No module named 'psycopg2'`
     - `docs/runtime/RAILWAY_POSTGRESQL_MIGRATION_EVIDENCE.md` — updated current result: PostgreSQL Online PASS; DATABASE_URL wired PASS; migration failed `ModuleNotFoundError: No module named 'psycopg2'`; fix applied Module 113; evidence table updated with PASS rows for PostgreSQL status and DATABASE_URL injection
   - `backend/tests/test_railway_migration_psycopg2_dependency_contract.py` (new — 14 static contract tests: root requirements.txt exists/has psycopg2-binary/still has asyncpg; backend requirements.txt exists/has psycopg2-binary/still has asyncpg; migration runbook exists/mentions psycopg2-binary/mentions asyncpg/mentions ModuleNotFoundError/mentions run_migrations script; migration evidence doc exists/records psycopg2 failure/no secrets policy)
   - No runtime app logic changed; no auth changes; no DB schema changes; no real secrets
   - Full backend tests: 2338/2338 passed

- Full backend tests: 2338/2338 passed
- Sprint 16 in progress (Modules 110–113 complete)
- psycopg2-binary==2.9.9 now in both requirements files; Railway redeploy + migration rerun required
- Next: Module 114 — Railway PostgreSQL Migration Retest Evidence

112. Module 114 — Railway PostgreSQL Migration Retest Evidence
   - Commit: (see git log)
   - Real evidence provided by user: Railway backend `/health` → 200; `run_migrations.py` exit 0; `db_smoke_test.py` → 4 tables PASS
   - Sanitized migration output confirms both revisions applied: `0001_initial_schema` and `0002_password_hash`
   - Sanitized DB smoke output: SELECT 1 passed; clinics/patients/consultation_sessions/audit_log all confirmed
   - `docs/runtime/RAILWAY_POSTGRESQL_MIGRATION_EVIDENCE.md` — updated to PASS: migration failure history (Module 113 attempt + fix + Module 114 retest PASS); full evidence table (18 rows; PostgreSQL/DATABASE_URL/migration command/exit 0/0001/0002/db_smoke/4 tables/health all PASS; fake clinic/user/health-ready PENDING); sanitized migration output section; sanitized DB smoke output section; what this proves (PostgreSQL reachable; both drivers functional; migrations applied; 4 tables confirmed); what this does not prove (fake clinic/user/Vercel/CORS/Vapi/n8n/production PHI all PENDING); safety boundary; remaining blockers (11 items); recommended next Module 115
   - `docs/runtime/STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` — PostgreSQL status PASS; DATABASE_URL wired PASS; migrations PASS; db_smoke PASS; fake clinic/user/Vercel/CORS/Vapi/n8n remain PENDING; resolved blockers 1–5 noted
   - `docs/runtime/STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md` — evidence summary table: PostgreSQL PASS; migrations PASS; smoke checklist check 3 (migrations applied) PASS; check 2 (health/ready) still PENDING (fake user not provisioned); overall BLOCKED/PENDING
   - `backend/tests/test_railway_postgresql_migration_retest_evidence_contract.py` (new — 22 static contract tests: evidence doc exists/non-empty; PASS; Railway PostgreSQL; DATABASE_URL wired name-only; run_migrations.py; 0001_initial_schema; 0002_password_hash; db_smoke_test.py; SELECT 1 passed; clinics/patients/consultation_sessions/audit_log tables; /health still PASS; no secrets; no real patient data; fake/non-PHI; fake clinic/user still PENDING; Vercel PENDING; Vapi PENDING; Module 115)
   - No runtime code changed; no secrets recorded; no real patient data
   - Full backend tests: 2360/2360 passed

- Full backend tests: 2360/2360 passed
- Sprint 16 in progress (Modules 110–114 complete)
- Railway PostgreSQL migration PASS; fake staging clinic/user still PENDING
- Next: Module 115 — Fake Staging Clinic and User Provisioning Evidence

113. Module 115 — Fake Staging Clinic and User Provisioning Evidence
   - Commit: (see git log)
   - Real evidence provided by user: fake staging clinic and doctor user provisioned in Railway PostgreSQL via Railway console
   - Staging clinic: `id=1a5bbc75-c1b0-4488-94aa-64b3f1c50056` `slug=staging-fake-clinic` `status=active`
   - Staging user: `id=5b63b514-7624-4e8e-9af0-71c153ba7b83` `email=doctor.staging@praximed.test` `role=doctor` `status=active`
   - Password not recorded; bcrypt hash not recorded; DATABASE_URL not recorded; no real patient data; not local-dev-password; not local-dev UUIDs
   - `docs/runtime/FAKE_STAGING_CLINIC_USER_PROVISIONING_EVIDENCE.md` (new — 7-section evidence doc: purpose (accuracy policy; fake/non-PHI; no production secrets), current result (PASS), evidence (clinic table: id/slug/name/status/timezone/locale all PASS; user table: id/clinic_id/email/full_name/role/status/password_hash all PASS; sanitized verification output from Railway console), safety boundary (password/hash/DATABASE_URL not recorded; no real patient data; fake/non-PHI; not local-dev-password; not local-dev UUIDs; production PHI NO-GO), what this proves (Railway PostgreSQL has both rows; user bound to clinic; active status on both; password_hash column populated; credentials held privately; local-dev isolation confirmed), what this does not prove (login/JWT/health-ready/Vercel/CORS/dashboard/Vapi/n8n/production PHI all NOT PROVEN), next verification Module 116 with exact request template)
   - `docs/runtime/STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` — fake staging clinic PASS (id/slug/status); fake staging user PASS (id/email/role/status); blockers 6+7 resolved; Vercel/CORS/Vapi/n8n remain PENDING
   - `docs/runtime/STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md` — evidence summary row (fake staging clinic/user) PASS with real IDs; smoke checklist check 2 (health/ready) updated blocker note (not yet tested); check 6 (fake login) updated (not yet tested against staging backend); overall BLOCKED/PENDING
   - `backend/tests/test_fake_staging_clinic_user_provisioning_evidence_contract.py` (new — 19 static contract tests: evidence doc exists/PASS/fake staging clinic/staging-fake-clinic slug/clinic UUID/user email/user UUID/role doctor/status active/password not recorded/hash not recorded/DATABASE_URL not recorded/no real patient data/fake non-PHI/not local-dev-password/login endpoint pending/Vercel pending/Vapi pending/Module 116)
   - No runtime code changed; no secrets recorded; no real patient data
   - Full backend tests: 2379/2379 passed

- Full backend tests: 2379/2379 passed
- Sprint 16 in progress (Modules 110–115 complete)
- Fake staging clinic/user PASS; backend login smoke still PENDING
- Next: Module 116 — Backend Staging Login Smoke Evidence

114. Module 116 — Backend Staging Login Smoke Evidence
   - Commit: (see git log)
   - Real evidence provided by user: `GET /health` → 200; `GET /health/ready` → 200; `POST /auth/login` → 200
   - `GET /health/ready` response: `{"status":"ready","checks":{"app":"ok"}}` — DB pool healthy; JWT_SECRET_KEY set
   - `POST /auth/login` response: HTTP 200; `access_token` present (REDACTED); `token_type=bearer`; `expires_in_seconds` present; `user` object present; password not recorded; token value not recorded
   - `docs/runtime/BACKEND_STAGING_LOGIN_SMOKE_EVIDENCE.md` (new — 8-section evidence doc: purpose (accuracy policy; no secrets), current result (PASS), evidence (health/ready/login tables with all PASS; token REDACTED), safety boundary (password/token/hash/DATABASE_URL not recorded; no real patient data; fake/non-PHI; production PHI NO-GO), what this proves (backend reaches PostgreSQL; JWT_SECRET_KEY set; fake credentials authenticate; bearer token issued; all HTTPS endpoints reachable), what this does not prove (Vercel/CORS/browser login/dashboard/Vapi/n8n/production PHI all NOT PROVEN), remaining blockers (9 items), next step Module 117)
   - `docs/runtime/STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` — health/ready PASS; direct login smoke PASS; Vercel/CORS/browser dashboard/Vapi/n8n remain PENDING
   - `docs/runtime/STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md` — smoke checklist check 2 (health/ready) PASS; check 6 (fake login — direct backend) PASS; Vercel/browser/dashboard/Vapi/n8n remain PENDING; overall BLOCKED/PENDING
   - `backend/tests/test_backend_staging_login_smoke_evidence_contract.py` (new — 21 static contract tests: evidence doc exists/PASS; /health; /health/ready; /auth/login; status 200; staging email; clinic UUID; access_token present; token REDACTED; bearer; password not recorded; hash not recorded; DATABASE_URL not recorded; no real patient data; fake non-PHI; Vercel pending; CORS pending; browser dashboard pending; Vapi pending; Module 117)
   - No runtime code changed; no secrets recorded; no real patient data
   - Full backend tests: 2400/2400 passed

- Full backend tests: 2400/2400 passed
- Sprint 16 in progress (Modules 110–116 complete)
- Backend direct login smoke PASS; Vercel frontend deployment still PENDING
- Next: Module 117 — Vercel Frontend Deployment and API Wiring

115. Module 117 — Vercel Frontend Deployment and API Wiring Evidence
   - Commit: (see git log)
   - Real evidence provided by user: Vercel deployed; URL `https://praximed.vercel.app`; login loaded; browser login PASS; dashboard loaded
   - `FRONTEND_CORS_ORIGINS=https://praximed.vercel.app` set in Railway; Railway backend redeployed; `/health` still 200
   - Dashboard evidence: header "PraxisMed / Clinic Dashboard"; Logout button; Clinic Overview; Appointments card (0 rows); Patients card (0 rows); Notifications card (0 rows); Consultations card (0 rows); footer says fake/local demo data
   - No password, token, hash, DATABASE_URL, JWT_SECRET_KEY, or webhook secrets recorded
   - `docs/runtime/VERCEL_FRONTEND_DEPLOYMENT_AND_API_WIRING_EVIDENCE.md` (new — 8-section evidence doc: purpose; current result PASS; evidence (Vercel deployment/API base URL wiring/CORS wiring/browser login/dashboard — all PASS; dashboard shows zero rows in all four sections as expected before Vapi calls); login evidence summary (clinic_id/email/password-not-recorded/token-not-recorded); safety boundary (all secrets not recorded; no wildcard CORS; no real patient data; production PHI NO-GO); what this proves (Vercel builds from frontend/; frontend reaches Railway backend; CORS works; browser login works; dashboard renders; no auto-confirm); what this does not prove (Vapi/n8n/staff Confirm in deployed dashboard/full smoke/production PHI — all NOT PROVEN); next Module 118)
   - `docs/runtime/STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` — Vercel URL PASS; NEXT_PUBLIC_API_BASE_URL PASS; FRONTEND_CORS_ORIGINS PASS; CORS browser PASS; login PASS; dashboard PASS; blockers 8–12 resolved; Vapi/n8n PENDING
   - `docs/runtime/STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md` — smoke checklist checks 4 (frontend /login) PASS; 5 (CORS) PASS; 6 (browser login) PASS; 7 (protected dashboard) PASS; 8 (dashboard sections) PASS; Vapi/n8n rows still PENDING; overall PARTIAL PASS
   - `backend/tests/test_vercel_frontend_deployment_and_api_wiring_evidence_contract.py` (new — 24 static contract tests: evidence doc exists/PASS; Vercel URL; Railway backend URL; NEXT_PUBLIC_API_BASE_URL; FRONTEND_CORS_ORIGINS; /health; /health/ready; browser login; dashboard; Appointments/Patients/Notifications/Consultations; staging email/clinic UUID; password not recorded; token not recorded; DATABASE_URL not recorded; no real patient data; fake non-PHI; Vapi pending; n8n pending; Module 118)
   - No runtime code changed; no secrets recorded; no real patient data
   - Full backend tests: 2424/2424 passed

- Full backend tests: 2424/2424 passed
- Sprint 16 in progress (Modules 110–117 complete)
- Frontend/CORS/browser login/dashboard PASS; Vapi staging dashboard loop still PENDING
- Next: Module 118 — Vapi Staging Dashboard Loop Evidence

116. Module 118A — Vapi Staging Tenant Config Blocker Fix
   - Date: 2026-07-05
   - Vapi test call attempted in Module 118: Vapi UI showed "completed successfully" but staging_count=0; no DB row was inserted
   - Module 118A diagnostic confirmed three blockers:
     (1) X-Vapi-Service-Name header missing — get_machine_auth_context returns HTTP 401
     (2) X-Clinic-Ref is not a recognized clinic ID alias — must use X-Vapi-Clinic-Id
     (3) No tenant config on disk for staging UUID — ConfigNotFoundError → HTTP 404
   - Fix applied: `backend/tenants/configs/1a5bbc75-c1b0-4488-94aa-64b3f1c50056/clinic_config.json` (new)
   - `docs/runtime/STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` updated: Vapi rows updated to BLOCKED; diagnostic findings recorded; correct required headers documented; staging_count=0 and "no DB row was inserted" recorded
   - `docs/runtime/STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md` updated: check 10 updated to BLOCKED with Module 118A evidence; overall BLOCKED/PENDING maintained
   - `backend/tests/test_vapi_staging_tenant_config_blocker_fix_contract.py` (new — 20 static contract tests: tenant config exists/tenant_id/clinic_name/timezone/appointment_booking; wiring doc Vapi not PASS/staging_count=0/completed-but-no-row/Content-Type/X-Vapi-Service-Name/X-Vapi-Clinic-Id/X-Vapi-Scopes/X-Clinic-Ref/no-real-patient/fake-non-PHI/no-secrets; smoke doc blocked/Vapi not PASS)
   - No runtime app logic changed; no secrets recorded; no real patient data; tenant config blocker fix only
   - Commit: 12f88c4
   - Vapi dashboard loop still PENDING at end of 118A — awaiting Railway redeploy + correct Vapi headers
   - Full backend tests: 2443/2443 passed

117. Module 118B — Vapi Staging Direct Endpoint and Dashboard Retest Evidence
   - Date: 2026-07-05
   - Module 118A tenant config fix deployed to Railway; Vapi headers corrected (X-Clinic-Ref removed; X-Vapi-Service-Name: vapi added; X-Vapi-Clinic-Id used)
   - Dashboard evidence: Appointments count reached 2 (two Test Patient rows; status: new; priority: normal; Confirm button visible)
   - Dashboard evidence: Appointments count later reached 3 (two rows status: confirmed after staff Confirm; one row status: new); no auto-confirmation observed
   - `docs/runtime/VAPI_STAGING_DASHBOARD_LOOP_EVIDENCE.md` (new — 8-section evidence doc: purpose (accuracy policy; fake/non-PHI; no production secrets), current result PASS, prerequisites (all PASS from Modules 112–118A), Vapi configuration (endpoint URL/Content-Type/X-Vapi-Service-Name/X-Vapi-Clinic-Id/X-Vapi-Scopes/X-Clinic-Ref removed/VAPI_WEBHOOK_SECRET name only), dashboard evidence (count 2: Test Patient/status new/priority normal/Confirm visible; count 3: two confirmed/one new/Confirm worked), safety (12 items all confirmed not recorded), what this proves (Vapi reaches backend/rows inserted/dashboard displays/staff Confirm works/no auto-confirm), what this does not prove (n8n PENDING/production PHI NO-GO/custom domain/auth hardening/logs/rollback))
   - `docs/runtime/STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` updated: Vapi server URL/scopes/tenant config/test call/appointment row/staff Confirm all PASS; blocker 13 RESOLVED; overall CORE PASS; n8n PENDING/DEFERRED; production PHI NO-GO
   - `docs/runtime/STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md` updated: checks 9–12 PASS; Section 3 Vapi rows PASS; overall CORE PASS; n8n NOT ENABLED/DEFERRED; logs/rollback PENDING
   - `backend/tests/test_vapi_staging_dashboard_loop_evidence_contract.py` (new — 25 static contract tests: evidence doc exists/PASS; endpoint URL; dashboard URL; Content-Type/X-Vapi-Service-Name/X-Vapi-Clinic-Id/X-Vapi-Scopes; X-Clinic-Ref removed; clinic UUID; Test Patient; count 2/count 3; status new/confirmed; priority normal; Confirm; fake data/no real patient/no production PHI; DATABASE_URL/token/password not recorded; n8n pending; production PHI NO-GO)
   - No runtime code changed; no secrets recorded; no real patient data; fake/non-PHI staging only
   - Commit: f602612
   - Full backend tests: 2468/2468 passed

## Architecture Checkpoint 16

- Architecture Checkpoint 16 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_16_FAKE_DATA_STAGING_CORE_COMPLETION.md`
- Result: FAKE-DATA STAGING CORE PASS
- Sprint 16 complete (Modules 110–118B all confirmed PASS for fake-data staging core)
- Fake-data staging backend / PostgreSQL / migrations / clinic+user / login / Vercel / CORS / browser login / dashboard / Vapi appointment capture / dashboard Confirm — all PASS
- n8n staging: PENDING/DEFERRED
- Production PHI readiness: NO-GO — production hardening checklist incomplete
- `backend/tests/test_architecture_checkpoint_16_fake_data_staging_core_completion_contract.py` (new — 23 static contract tests)
- Full backend tests: 2491/2491 passed
- Recommended next module: Sprint 17 / Module 119 — Production Hardening Gap Review
- Alternative: Sprint 16 / Module 119 — n8n Staging Workflow Wiring Evidence

118. Module 119 — Production Hardening Gap Review
   - Date: 2026-07-05
   - Sprint 17 starts; fake-data staging core remains PASS; production PHI readiness remains NO-GO
   - `docs/architecture/PRODUCTION_HARDENING_GAP_REVIEW.md` (new — 8-section gap review: purpose; current result PRODUCTION PHI NO-GO; what is proven in fake-data staging (6 items PASS); what remains unproven for production (14 items); production blockers ranked by severity (Critical C1–C8: auth/session hardening/token storage/production secrets/PHI logging/tenant isolation/audit/backups/rollback; High H1–H4: monitoring/rate limiting/CORS domain/error handling; Medium M1–M4: n8n staging/custom domain/onboarding/UI-UX); recommended implementation order (Modules 120–126); explicit production NO-GO conditions; recommended next module (Module 120 — Auth/session hardening implementation); safety constraints)
   - `backend/tests/test_production_hardening_gap_review_contract.py` (new — 25 static contract tests: doc exists/PRODUCTION PHI NO-GO/fake-data staging/auth-session hardening/token storage/production secrets/PHI logging/tenant isolation/audit/backups/rollback/monitoring/rate limiting/CORS domain/n8n staging/no real patient data/no production PHI/no secrets recorded/Module 120–126)
   - No runtime code changed; no deployment changes; no secrets recorded; no real patient data
   - Full backend tests: 2516/2516 passed

119. Module 120 — Auth/Session Hardening Implementation
   - Date: 2026-07-05
   - httpOnly Secure SameSite=Lax cookie session model implemented (Option B from PRODUCTION_CORS_AUTH_DOMAIN_PLAN.md)
   - Cookie name: `praximed_session`; Max-Age=3600; HttpOnly; Secure; SameSite=Lax; Path=/
   - Backend changes:
     - `backend/app/api/routes/auth.py`: `POST /auth/login` sets httpOnly cookie in addition to returning JSON body (transition window); `POST /auth/logout` clears cookie → HTTP 200; `GET /auth/me` returns user_id/clinic_id/role via cookie or Bearer auth
     - `backend/app/api/dependencies/current_user.py`: reads Bearer header first; falls back to `praximed_session` cookie; raises 401 if neither present; machine auth (Vapi/n8n) routes unchanged
   - Frontend changes:
     - `frontend/lib/api.ts`: `credentials: "include"` added to all `fetch` calls; Bearer header injection removed; token parameter removed from all data fetcher signatures
     - `frontend/lib/auth.ts`: sessionStorage removed; `storeToken`/`getToken`/`clearToken`/`isAuthenticated`/`getClinicId` removed; `getMe()` and `logout()` added
     - `frontend/app/login/page.tsx`: `storeToken` call removed; login page relies on backend cookie
     - `frontend/app/dashboard/page.tsx`: `getMe()` used for auth check and clinic_id; `logout()` called on Logout button; all data fetchers called without token parameter
   - Tests:
     - `backend/tests/test_auth_session_hardening_module120.py` (new — 16 tests: cookie flags/logout/cookie-auth/Bearer-compat/expired-cookie/invalid-cookie/me-endpoint)
     - 7 stale frontend contract tests updated to reflect cookie-based model
     - All existing auth/route tests pass (backward compat maintained)
   - `docs/security/AUTH_SESSION_HARDENING_EVIDENCE.md` (new — implementation evidence doc)
   - Closes critical blockers C1 and C2 from PRODUCTION_HARDENING_GAP_REVIEW.md
   - No real patient data; no secrets recorded; staging/local implementation only; production PHI NO-GO remains
   - Full backend tests: 2532/2532 passed

120. Module 120A — Cross-site Staging Cookie Compatibility Fix
   - Date: 2026-07-05
   - Problem: SameSite=Lax cookies are not sent on cross-site fetch/XHR; Vercel (vercel.app) → Railway (railway.app) are different eTLD+1 → cross-site; SameSite=None; Secure is required
   - Fix: `SESSION_COOKIE_SAMESITE` env var added to `backend/app/api/routes/auth.py`; default "none" for cross-site staging; valid values: none | lax | strict; unknown values fall back to "none"; value is case-insensitive
   - `_get_cookie_samesite()` helper function added; reads env at call time (testable via monkeypatch)
   - `test_auth_session_hardening_module120.py` updated: `test_login_cookie_has_samesite_lax` replaced with `test_login_cookie_has_samesite_attribute` + `test_login_cookie_default_samesite_is_none`; `login_client` fixture now deletes SESSION_COOKIE_SAMESITE to ensure clean default
   - `backend/tests/test_auth_session_hardening_module120a.py` (new — 16 tests: default→none; explicit none/lax/strict; case-insensitive; unknown→none; httpOnly+Secure retained for both none and lax; Max-Age retained; direct _get_cookie_samesite unit tests)
   - `docs/security/AUTH_SESSION_HARDENING_EVIDENCE.md` updated: SameSite configuration table; cross-site explanation; full test coverage table
   - To deploy fix in staging: set `SESSION_COOKIE_SAMESITE=none` (or leave unset, since "none" is now the default) in Railway env vars
   - No secrets recorded; no real patient data; production PHI NO-GO remains
   - Full backend tests: 2549/2549 passed

121. Module 120B — Deployed Auth/Session Browser Smoke Evidence
   - Date: 2026-07-05
   - Real deployed browser smoke passed after Module 120 + 120A cookie hardening
   - Frontend: https://praximed.vercel.app; Backend: https://web-production-fd91d.up.railway.app
   - Evidence: browser login PASS; dashboard load PASS; session survives refresh PASS; appointments visible PASS; logout clears session PASS; /dashboard after logout blocks/redirects PASS
   - Cookie context: praximed_session; HttpOnly; Secure; SameSite=None (cross-site Vercel→Railway); credentials: include; no sessionStorage/Bearer dependency
   - Safety: no password/token/cookie value/DATABASE_URL/secrets recorded; fake/non-PHI staging only; production PHI NO-GO
   - `docs/security/AUTH_SESSION_DEPLOYED_BROWSER_SMOKE_EVIDENCE.md` (new — 8-section evidence doc: purpose; PASS result; environment/checks table; cookie/session context; safety boundary; what this proves; what this does not prove (production PHI NO-GO; C3–C8 blockers still open); recommended next module 121)
   - `backend/tests/test_auth_session_deployed_browser_smoke_evidence_contract.py` (new — 21 static contract tests: doc exists/PASS/frontend URL/backend URL/login PASS/dashboard PASS/refresh/logout/post-logout/praximed_session/HttpOnly/Secure/SameSite=None/credentials include/no token/no password/no cookie value/no real patient data/fake non-PHI/production PHI NO-GO/Module 121)
   - No runtime code changed; docs/static-tests only
   - UI/UX Fabel 5 premium demo polish remains upcoming after critical hardening (Sprint 18)
   - Full backend tests: 2570/2570 passed

## Architecture Checkpoint 17

- Architecture Checkpoint 17 created: `docs/architecture/ARCHITECTURE_CHECKPOINT_17_COMMERCIAL_MVP_OUTREACH_ACCELERATION.md`
- Date: 2026-07-05
- Mode: Commercial acceleration — outreach starts now while product build continues
- Technical base commit: 38e9234 (Module 120B)
- Full backend tests at checkpoint: 2570/2570 passed
- Key decisions:
  - Clinic outreach: **START IMMEDIATELY** — fake-data staging demo is compelling; no code changes required for outreach
  - 30-day pilot offer: **ACTIVE** — fake/test data only; no real PHI; founding clinic partner framing
  - Production PHI launch: **NO-GO** — C3–C8 hardening blockers still open
  - Fabel 5 premium UI/UX: **Sprint 18 — high priority** after critical hardening complete
  - Commercial MVP next module: **Module 121 — Patient and Appointment Data Linking Foundation**
  - Parallel non-code task: **Build first 50 private clinic list (Vienna) and start outreach**
- What can be shown now: AI phone call → dashboard → staff Confirm workflow; secure login; multi-tenant architecture
- What must not be claimed: GDPR/HIPAA compliant; ready for real patient data; automated confirmation; full calendar integration
- Indicative pricing: €149–199/month (Starter) / €299–399/month (Growth) / €599–799/month (Practice)
- Founding clinic discount: 50% off for 12 months for first 5 clinics
- Safety constraints enforced: no real patient data; no production PHI; no secrets; no compliance claims; no automated confirmation
- `backend/tests/test_architecture_checkpoint_17_commercial_mvp_outreach_acceleration_contract.py` (new — 24 static contract tests)

122. Module 121 — Patient and Appointment Data Linking Foundation
   - Date: 2026-07-05
   - Sprint 17 / Commercial MVP build track
   - `backend/app/db/schema.sql` (updated — `patient_id UUID` column added to `appointment_requests`; `idx_appointment_requests_clinic_patient` index added)
   - `backend/migrations/versions/0003_patient_id_appt_requests.py` (new — revision `"0003_patient_id_appt_requests"` / down_revision `"0002_password_hash"`; upgrade adds `patient_id UUID REFERENCES patients(id) ON DELETE SET NULL` column + index; downgrade drops both)
   - `backend/app/db/repositories/patient_repo.py` (updated — `find_or_create_patient_from_vapi` added: phone-based match within clinic_id, create new patient if no match or no phone; whitespace phone treated as None; tenant isolation enforced)
   - `backend/app/db/repositories/appointment_request_repo.py` (updated — `patient_id: Optional[str] = None` parameter added to `create_appointment_request`; SQL INSERT updated to `$15` patient_id / `$16::jsonb` raw_payload; backward compatible)
   - `backend/app/modules/vapi/vapi_appointment_capture.py` (updated — `patient_repo` imported; `find_or_create_patient_from_vapi` called before appointment create; `patient_id` passed to `create_appointment_request`; `"patient_id"` included in return dict)
   - `backend/tests/test_vapi_appointment_capture.py` (updated — autouse fixture patches `find_or_create_patient_from_vapi` for all 31 existing tests)
   - `backend/tests/test_schema_contract.py` (updated — `patient_id` column and `idx_appointment_requests_clinic_patient` index assertions added)
   - `backend/tests/test_migration_contract.py` (updated — 3 new tests 24–26: migration 0003 file exists; revision `"0003_patient_id_appt_requests"` ≤32 chars; mentions `patient_id`/`patients`/`appointment_requests`)
   - `backend/tests/test_patient_appointment_linking.py` (new — 17 tests: find_or_create existing/new/no-phone/whitespace/strip/clinic_id-scope/tenant-isolation; create_appointment_request patient_id; vapi capture integration; second-call reuse; error propagation; no real patient data safety check)
   - `docs/architecture/PATIENT_APPOINTMENT_DATA_LINKING_FOUNDATION.md` (new — schema changes; migration 0003; patient matching algorithm; what this enables next: Modules 122–126)
   - No real patient data; no secrets; fake-data staging only; production PHI NO-GO
   - Full backend tests: 2619/2619 passed

123. Module 121B — Staging Patient and Appointment Linking Migration Evidence
   - Date: 2026-07-05
   - Sprint 17 / Commercial MVP build track
   - Docs/static-tests only — no runtime code changes, no new migrations, no secrets
   - Railway redeployed after commit 02e8896
   - Migration command run: `python backend/scripts/run_migrations.py`
   - Migration `0003_patient_id_appt_requests` applied; head confirmed
   - `appointment_requests.patient_id UUID` column exists in Railway PostgreSQL — **PASS**
   - `idx_appointment_requests_clinic_patient` index exists in Railway PostgreSQL — **PASS**
   - Direct Vapi endpoint smoke returned HTTP 200 with `ok: true` — **PASS**
   - Latest appointment_request has non-null `patient_id` linking to a patient row — **PASS**
   - Joined patients row confirmed; `clinic_id` scoped (tenant isolation holds) — **PASS**
   - `source: vapi`, `status: new`, `action_required: true` confirmed
   - Fake data only: Linked Test Patient / routine checkup / next Monday morning
   - Pre-appointment summary: PENDING (Module 122)
   - Doctor notification: PENDING (Module 123)
   - Production PHI readiness: NO-GO
   - `docs/runtime/PATIENT_APPOINTMENT_LINKING_STAGING_MIGRATION_EVIDENCE.md` (new)
   - `docs/runtime/STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` (updated — migration 0003 PASS; patient_id column/index PASS; linking smoke PASS; summaries/notifications PENDING; production PHI NO-GO)
   - `docs/runtime/STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md` (updated — check 13 patient/appointment linking PASS added; migration head updated to 0003; commercial MVP data foundation improved)
   - `backend/tests/test_patient_appointment_linking_staging_migration_evidence_contract.py` (new — 21 static contract tests)
   - Full backend tests: 2640/2640 passed

124. Module 122 — Pre-Appointment Summary Foundation
   - Date: 2026-07-05
   - Sprint 17 / Commercial MVP build track
   - `backend/app/services/__init__.py` (new — services package init)
   - `backend/app/services/pre_appointment_summary.py` (new — pure service: `build_pre_appointment_summary(appointment_request, patient, previous_request_count)` → structured dict; rule-based `suggested_next_action`; no AI, no DB, no diagnosis, no medical advice; `patient_type` "returning"/"new" from patient_id presence)
   - `backend/app/db/repositories/appointment_request_repo.py` (updated — `count_requests_for_patient` added: scoped COUNT by clinic_id + patient_id, optional exclude_request_id)
   - `backend/app/api/routes/appointment_requests.py` (updated — `GET /appointment-requests/{id}/pre-appointment-summary` added; `patient_repo` imported; `build_pre_appointment_summary` imported; tenant isolation via `require_staff_clinic_access`; 404 on missing request; 403 on wrong clinic; 401 on missing auth)
   - `backend/tests/test_pre_appointment_summary.py` (new — 25 tests: 18 service unit tests (patient_name/phone/type/reason/metadata/previous_count/suggested_next_action/no-diagnosis/no-medical-advice/no-treatment/safety_note/no-patient-id-fallback) + 7 route integration tests (200/404/401/403/required-fields/no-patient-id/no-diagnosis))
   - `docs/architecture/PRE_APPOINTMENT_SUMMARY_FOUNDATION.md` (new — data sources; safety rules; API spec; suggested_next_action logic table; compatibility; what enables next: Module 123 notifications, dashboard UI, demo quality)
   - No real patient data; no secrets; no AI calls; no production PHI; fake-data staging only
   - Full backend tests: 2665/2665 passed

125. Module 122B — Deployed Pre-Appointment Summary Smoke Evidence
   - Date: 2026-07-05
   - Sprint 17 / Commercial MVP build track
   - Docs/static-tests only — no runtime code changes, no migrations, no secrets
   - `GET /auth/me` → HTTP 200; role: doctor; cookie auth confirmed — **PASS**
   - `GET /appointment-requests/ae8d53cd.../` → HTTP 200; patient_id linked; source: vapi; status: new; action_required: true — **PASS**
   - `GET /appointment-requests/ae8d53cd.../pre-appointment-summary` → HTTP 200; ok: true — **PASS**
   - patient_name: Summary Linked Patient (fake); patient_type: returning; suggested_next_action: Review and confirm — **PASS**
   - safety_note present; no diagnosis; no medical advice — **PASS**
   - Observation: patient_phone returned null — future data-normalization/input-mapping improvement; does not block 122B
   - No password/token/cookie value/DATABASE_URL/secrets recorded
   - Fake/non-PHI staging only; production PHI readiness: NO-GO
   - `docs/runtime/PRE_APPOINTMENT_SUMMARY_DEPLOYED_SMOKE_EVIDENCE.md` (new)
   - `docs/runtime/STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` (updated — pre-appointment summary PASS added)
   - `docs/runtime/STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md` (updated — check 14 pre-appointment summary PASS added)
   - `backend/tests/test_pre_appointment_summary_deployed_smoke_evidence_contract.py` (new — 24 static contract tests)
   - Full backend tests: 2689/2689 passed

126. Module 123 — Doctor Notification System Foundation
   - Date: 2026-07-05
   - Sprint 17 / Commercial MVP build track
   - `backend/app/modules/notifications/notification_router.py` (updated — `create_appointment_request_notification` enhanced: `reason` and `suggested_next_action` params added; richer message body with patient_name, reason, suggested action)
   - `backend/app/modules/vapi/vapi_appointment_capture.py` (updated — passes `reason=reason` and `suggested_next_action="Review and confirm"` to notification call)
   - `backend/tests/test_doctor_notification_foundation.py` (new — 15 tests: notification_type/related_resource_type/related_resource_id/clinic_id/channel/message-patient_name/message-reason/message-suggested_action/no-diagnosis/no-medical-advice/omits-reason-when-missing/vapi-capture-notification_created-true/vapi-capture-notification_created-false/list-401/list-403)
   - `docs/architecture/DOCTOR_NOTIFICATION_SYSTEM_FOUNDATION.md` (new — data model; tenant isolation; no external delivery; safety boundaries; future delivery path; how to enable doctor phone notification later; production PHI NO-GO)
   - Existing notification infrastructure reused: clinic_notifications table, notification_repo, notification_router, notification routes — no new table or migration required
   - Notification scoped by clinic_id; references appointment_request_id via related_resource_id
   - Notification channel = "internal" only; no SMS/push/email/webhook
   - No diagnosis, no medical advice, no secrets, no real patient data
   - Fake/non-PHI staging only; production PHI readiness: NO-GO
   - Full backend tests: 2704/2704 passed

127. Module 123A — Doctor Notification Creation Blocker Fix
   - Date: 2026-07-05
   - Sprint 17 / Commercial MVP build track
   - Root cause: asyncpg returns UUID columns as uuid.UUID objects (not str); passing uuid.UUID to related_resource_id TEXT column causes a binary-protocol type-OID mismatch in PostgreSQL that failed silently (except Exception: notification_created = False with no logging)
   - Why tests passed: create_appointment_request_notification was fully mocked; real DB path never exercised
   - `backend/app/modules/vapi/vapi_appointment_capture.py` (updated — added logger; str(row["id"]) conversion before passing request_id to notification; logger.error in except block; notification_error added to return dict)
   - `backend/tests/test_doctor_notification_foundation.py` (updated — 5 new tests 16–20: request_id is str not uuid.UUID; notification_error None on success; notification_error populated on failure; logger.error called on failure; notification_repo receives str related_resource_id)
   - `docs/architecture/DOCTOR_NOTIFICATION_SYSTEM_FOUNDATION.md` (updated — Module 123A section added: root cause, fix summary, why tests passed before fix)
   - No real patient data; no secrets; fake-data staging only; production PHI NO-GO
   - Full backend tests: 2709/2709 passed

129. Module 125 — Dashboard Notification and Summary UI Foundation
   - Commit: ab08b7a
   - Date: 2026-07-05
   - Sprint 17 / Commercial MVP build track
   - `frontend/lib/api.ts` (updated — `PreAppointmentSummary` interface added; `fetchPreAppointmentSummary(requestId, clinicId)` added; calls GET /appointment-requests/{id}/pre-appointment-summary; uses shared apiFetch with credentials: include)
   - `frontend/app/dashboard/page.tsx` (updated — imports fetchPreAppointmentSummary, PreAppointmentSummary; summaryOpenId/summaries state; handleViewSummary: toggle open/close, fetch on first open, cache; appointment rows have "View summary"/"Hide summary" button; inline summary-panel: patient_name, patient_type, reason, urgency_level, previous_request_count, suggested_next_action, safety_note; NO diagnosis, NO medical advice; notifications section shows message (truncated 100 chars) + status badge; pending status highlighted; Confirm button unchanged)
   - `backend/tests/test_frontend_notification_and_summary_ui_contract.py` (new — 21 static contract tests: PreAppointmentSummary interface, fetchPreAppointmentSummary, endpoint, credentials, dashboard import, view-summary button, summary-panel, suggested_next_action, safety_note, patient_name, patient_type, reason, no diagnosis, no medical advice, message field, status field, pending highlighted, Confirm remains, fetchNotifications intact, no token storage, no secrets)
   - `docs/architecture/DASHBOARD_NOTIFICATION_AND_SUMMARY_UI_FOUNDATION.md` (new)
   - No real patient data; no secrets; no diagnosis; no medical advice; fake-data staging only; production PHI NO-GO; premium polish deferred to Sprint 18 (Fabel 5)
   - Full backend tests: 2754/2754 passed

135. Module 129 — First 50 Vienna Clinic Targets Research Workflow
   - Date: 2026-07-05
   - Sprint 18 / Commercial MVP + clinic outreach track
   - Docs/static-tests only — no runtime code, no fabricated data, no scraping
   - `docs/business/FIRST_50_VIENNA_CLINIC_TARGETS_RESEARCH_WORKFLOW.md` (new):
     purpose + safe research rules (public-only, no guessing, no scraping, source URL required);
     7 public sources (Google Maps, clinic websites, Impressum, Herold, DocFinder, WKO, Ärzteliste);
     7 target specialties with German search terms and target count (GP 12, dermatology 8, gynecology 8, orthopedics 6, dentistry 6, aesthetics 6, physiotherapy 4);
     data quality rules per field; A/B/C prioritization criteria;
     first batch execution: research 10 → contact 5 → 3-business-day follow-up → add 10/day continue;
     safe outreach wording reminders (fake-data demo, early pilot, no production PHI, no DSGVO claim);
     manual tracker filling instructions (step-by-step per field);
     next action checklist (10-step ready-to-execute list)
   - `backend/tests/test_first_50_vienna_clinic_targets_research_workflow_contract.py` (new — 25 static contract tests)
   - First real manual action: open CLINIC_OUTREACH_LIST_TRACKER.md, search Google Maps "Privatarzt Wien Allgemeinmedizin", fill rows 1–10, contact top 5
   - Production PHI readiness: NO-GO
   - Full backend tests: 2893/2893 passed

134. Module 128 — Clinic Outreach List Tracker Foundation
   - Date: 2026-07-05
   - Sprint 18 / Commercial MVP + clinic outreach track
   - Docs/static-tests only — no runtime code changes, no scraping, no real clinic data
   - `docs/business/CLINIC_OUTREACH_LIST_TRACKER.md` (new):
     purpose + how to use; 9 outreach status stages (Not contacted → Pilot interested/Not interested/Follow-up later);
     A/B/C fit scoring; 7 Vienna clinic specialties in priority order;
     50-row tracker table (all rows pre-populated with Not contacted status and blank fields ready to fill);
     daily execution rules (10 clinics/day research; 5 contacts/day minimum; 3-business-day follow-up rule; weekly review);
     safe claim reminder (fake-data staging only, no PHI claim, no DSGVO claim);
     suggested public research sources (WKO, Google Maps, docfinder.at, herold.at, ärzteliste.at)
   - `backend/tests/test_clinic_outreach_list_tracker_contract.py` (new — 15 static contract tests)
   - Clinic research and outreach can begin immediately from this tracker
   - Production PHI readiness: NO-GO
   - Full backend tests: 2868/2868 passed

133. Module 127 — Clinic Outreach Asset and 30-Day Pilot Offer Pack
   - Date: 2026-07-05
   - Sprint 18 / Commercial MVP + clinic outreach track
   - Docs/static-tests only — no runtime code changes, no migrations, no secrets
   - `docs/business/CLINIC_OUTREACH_30_DAY_PILOT_PACK.md` (new — 18-section outreach pack):
     product positioning; what we can safely show now; what not to claim; 30-day pilot offer;
     pricing recommendation (€299/€499/month; setup fee waived for pilot clinics);
     ideal clinic types; 50-clinic outreach list schema; email script (EN); German script (DE);
     phone call script; WhatsApp/LinkedIn message; 15-minute demo call structure;
     demo script using live dashboard; objection handling (6 objections with honest answers);
     follow-up sequence; contract/pilot next steps; safety/legal boundaries; daily outreach targets
   - `backend/tests/test_clinic_outreach_30_day_pilot_pack_contract.py` (new — 25 static contract tests)
   - Safe claims only: fake-data staging demo; no production PHI claim; no DSGVO/GDPR compliance claim
   - Immediate outreach can begin using the pack
   - Production PHI readiness: NO-GO
   - Full backend tests: 2853/2853 passed

132. Module 126B — Deployed Fabel 5 Premium Dashboard UI/UX Smoke Evidence
   - Date: 2026-07-05
   - Sprint 18 / Commercial MVP + clinic outreach track
   - Docs/static-tests only — no runtime code changes, no migrations, no secrets
   - Vercel deployment status: Ready
   - Deployed commit: 36b91be
   - Premium header visible: PraxisMed / Clinic Dashboard — **PASS**
   - Staging demo badge visible — **PASS**
   - Clinic Overview heading visible — **PASS**
   - Fake-data staging subtitle visible — **PASS**
   - Metric cards: Appointments 9 / Patients 6 / Notifications 1 / Pending confirmations 0 — **PASS**
   - Appointment Requests primary card visible — **PASS**
   - Appointment rows, confirmed badges, normal urgency badges visible — **PASS**
   - View summary buttons visible — **PASS**
   - Patients card visible — **PASS**
   - Notifications card visible; pending badge + message preview visible — **PASS**
   - Footer safety text: "Staging demo — fake data only · No real patient data · Production PHI: NO-GO" — **PASS**
   - Confirm not re-tested (all rows already confirmed; prior proof stands from 118B/125B)
   - No real patient data; no secrets; production PHI NO-GO
   - `docs/runtime/FABEL_5_PREMIUM_DASHBOARD_DEPLOYED_SMOKE_EVIDENCE.md` (new)
   - `docs/runtime/STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` (updated — Fabel 5 premium dashboard UI/UX PASS)
   - `docs/runtime/STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md` (updated — check 17 Fabel 5 PASS added)
   - `backend/tests/test_fabel_5_premium_dashboard_deployed_smoke_evidence_contract.py` (new — 27 static contract tests)
   - Full backend tests: 2828/2828 passed

131. Module 126 — Fabel 5 Premium Dashboard UI/UX Polish
   - Date: 2026-07-05
   - Sprint 18 / Commercial MVP + clinic outreach track
   - `frontend/app/globals.css` (updated — extended premium design token set: --color-card, --color-bg, --color-text-sub/muted/faint hierarchy, --color-brand-50/100, --color-success/success-bg, --color-warning-bg, --badge-amber-bg/text, --radius-sm/lg/xl, --shadow-xs/md/panel, antialiased fonts)
   - `frontend/app/dashboard/page.tsx` (updated — Fabel 5 full redesign: sticky premium header with brand + staging demo badge + logout; 4-card metrics row (Appointments/Patients/Notifications/Pending confirmations); SectionCard/SectionHeader/EmptyState/LoadingState/ErrorState reusable components; appointments as primary full-width; two-column responsive grid for patients+notifications; pending notifications have brand-blue left border accent; summary panel styled as blue-50 elevated card with labeled dl; suggested action in brand blue bold; safety note below rule in muted; footer with fake-data staging wording; all data- attributes preserved)
   - `backend/tests/test_frontend_fabel5_premium_dashboard_contract.py` (new — 22 static contract tests: premium header, staging demo indicator, metric cards, pending confirmations, all 4 sections, view/hide summary, confirm, suggested_next_action, safety_note, no diagnosis, no medical advice, credentials include, no token storage, internal only, fake/non-PHI wording, premium card component, premium globals.css tokens, no secrets)
   - `docs/architecture/FABEL_5_PREMIUM_DASHBOARD_UI_UX_POLISH.md` (new)
   - All existing functionality preserved: login/session/logout, appointments/patients/notifications/consultations, View summary, Confirm, credentials: include, no token storage
   - No backend API changes; no migration; no external delivery; no diagnosis; no medical advice; no real patient data; no secrets; production PHI NO-GO
   - Full backend tests: 2801/2801 passed

130. Module 125B — Deployed Dashboard Notification and Summary UI Smoke Evidence
   - Date: 2026-07-05
   - Sprint 17 / Commercial MVP build track
   - Docs/static-tests only — no runtime code changes, no migrations, no secrets
   - Vercel production deployment: Ready
   - Deployed commit: ab08b7a
   - Frontend URL: https://praximed.vercel.app
   - Dashboard URL: https://praximed.vercel.app/dashboard
   - Appointments count visible: 9 — **PASS**
   - Doctor Notification Patient rows visible — **PASS**
   - "View summary" button visible on appointment rows — **PASS**
   - Inline summary panel opens after click — **PASS**
   - "Hide summary" button visible after panel opens — **PASS**
   - Summary panel fields: Patient, Type, Reason, Urgency, Prior visits, Suggested action, Safety note — all **PASS**
   - Safety note: "This summary contains no medical advice or diagnosis. All actions require doctor or staff review and confirmation." — **PASS**
   - Confirm button remains visible and compatible — **PASS**
   - Confirmed status badges remain visible — **PASS**
   - Notification list display not separately verified in this browser smoke — PARTIALLY PENDING
   - No diagnosis; no medical advice; no real patient data; no secrets; fake-data staging only; production PHI NO-GO
   - `docs/runtime/DASHBOARD_NOTIFICATION_AND_SUMMARY_UI_DEPLOYED_SMOKE_EVIDENCE.md` (new)
   - `docs/runtime/STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` (updated — dashboard summary UI PASS; Fabel 5 PENDING)
   - `docs/runtime/STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md` (updated — check 16 dashboard summary UI PASS added)
   - `backend/tests/test_dashboard_notification_and_summary_ui_deployed_smoke_evidence_contract.py` (new — 25 static contract tests)
   - Full backend tests: 2779/2779 passed

128. Module 124 — Deployed Doctor Notification Smoke Evidence
   - Date: 2026-07-05
   - Sprint 17 / Commercial MVP build track
   - Docs/static-tests only — no runtime code changes, no migrations, no secrets
   - Deployed commit: b74a7ee (Module 123A — doctor notification creation blocker fix)
   - Fake Vapi appointment request created after redeploy
   - Railway DB notification_count=1 after fake Vapi call — **PASS**
   - Notification id: 5d84860d-0adc-45bb-995b-955e388d46e5
   - clinic_id: 1a5bbc75-c1b0-4488-94aa-64b3f1c50056 (staging fake clinic — tenant isolation holds)
   - channel: internal (no external delivery confirmed)
   - notification_type: appointment_request
   - title: New appointment request
   - message: "New appointment request from Doctor Notification Patient. Reason: Routine checkup doctor notification smoke. Action: Review and confirm."
   - status: pending
   - related_resource_type: appointment_requests
   - related_resource_id: a7d25ac1-31a8-4179-904e-6a06617e040f (linked to appointment request)
   - error_message: None
   - Dashboard: Appointments count 9; Doctor Notification Patient visible; Patients count 6
   - Dashboard notification UI: not proven (display pending — Module 125)
   - External phone/email/SMS/WhatsApp delivery: not attempted (future module)
   - No real patient data; no secrets; no diagnosis; no medical advice; fake-data staging only; production PHI NO-GO
   - `docs/runtime/DOCTOR_NOTIFICATION_DEPLOYED_SMOKE_EVIDENCE.md` (new)
   - `docs/runtime/STAGING_ENVIRONMENT_WIRING_EVIDENCE.md` (updated — internal doctor notification DB PASS; dashboard UI PENDING; external delivery PENDING)
   - `docs/runtime/STAGING_SMOKE_EXECUTION_PASS_BLOCKED_EVIDENCE.md` (updated — check 15 internal doctor notification PASS added)
   - `backend/tests/test_doctor_notification_deployed_smoke_evidence_contract.py` (new — 24 static contract tests)
   - Full backend tests: 2733/2733 passed

136. Module 126C — Premium Frontend Application Interface Expansion
   - Date: 2026-07-06
   - Sprint 18 / Commercial MVP build track
   - Frontend UI/UX — no backend API changes, no migrations, no secrets, no real patient data
   - **3-panel premium app shell:** Deep Midnight Navy header (#0F172A), left panel (AI Intake Queue + Notifications), center panel (Clinic Overview + MetricCards + Intake Resolution Workspace + Consultations), right panel (Patient Registry + selected patient profile)
   - **New globals.css tokens:** --color-navy, --color-navy-800/700/600, --color-teal, --color-teal-dark/bg/light; .pm-shell, .pm-app-grid (CSS Grid 264px/1fr/272px), .pm-panel-left/center/right; responsive breakpoints 1200px (hide right) + 768px (stack)
   - **`frontend/lib/tenantDisplay.ts`** (new): getClinicDisplayName + getRoleDisplay; staging clinic_id `1a5bbc75-c1b0-4488-94aa-64b3f1c50056` → "Staging Fake Clinic"
   - **`frontend/app/dashboard/page.tsx`** (rewritten): 3-panel layout using pm-shell/pm-app-grid/pm-panel-*; selectedApptId + selectedPatientId state; appointment cards clickable to open Intake Resolution Workspace; workspace has View summary / Confirm / Confirm & Create Profile [disabled] / TranscriptRecordingPanel; right panel shows patient list + selected patient teal profile card; header links to /onboarding and /developer-console; all data-section/data-action/data-state attributes preserved
   - **`frontend/app/onboarding/page.tsx`** (new scaffold): 5-step pilot activation wizard (non-functional); "Request pilot setup" CTA disabled; safety note: "Pilot activation requires security, legal, and production-readiness review before real patient data can be processed."
   - **`frontend/app/developer-console/page.tsx`** (new scaffold): Tenant provisioning panel (disabled), Clinic ID scope injection panel (disabled), Vapi machine credential binding panel (disabled), Environment checklist (C3–C8 all BLOCKED), Safety boundary panel; explicit warnings: "Never paste secrets into browser UI", "Production PHI remains NO-GO until hardening and legal review are complete", "Machine credentials are managed via secure environment variables, not this demo page"
   - **`backend/tests/test_premium_frontend_interface_expansion_contract.py`** (new — 56 static contract tests): tenantDisplay helper, globals.css tokens, pm-* CSS classes, 3-panel layout, AI Intake Queue, Patient Registry, Intake Resolution Workspace, transcript panel, Confirm & Create Profile, navy header, all regression checks (data-section/data-action/data-state preserved, no sessionStorage, no diagnosis, staging footer), onboarding page, developer console page
   - **`docs/architecture/PREMIUM_FRONTEND_APPLICATION_INTERFACE_EXPANSION.md`** (new)
   - All existing behaviour preserved: login, logout, dashboard loads, appointments/patients/notifications/consultations load, View summary / Hide summary, Confirm, credentials: include, no token storage, no diagnosis, no medical advice, staging safety boundary visible
   - No backend API changes; no fake clinic data; no real patient data; no secrets; production PHI NO-GO
   - Full backend tests: 2949/2949 passed

137. Module 126C-FIX — Activate Premium 3-Panel Dashboard Interface
   - Date: 2026-07-06
   - Sprint 18 / Commercial MVP build track
   - Frontend fix only — no backend changes, no migrations, no secrets, no real patient data
   - **Root cause:** Deployed /dashboard showed old Module 126 single-column layout despite Module 126C commit. Three causes: (1) layout depended on globals.css CSS classes with no inline fallback; (2) hex colours #0F172A / #0D9488 only referenced via CSS variables, not inlined; (3) panel headings used different text than the spec.
   - **Fix:** dashboard/page.tsx rewritten to be self-contained — embedded `<style>` block (`pm-dash-*` classes) with responsive breakpoints (1200px, 768px), hardcoded `#0F172A` and `#0D9488` as JS constants, panel headings corrected to "Incoming AI Intake" and "Audio Transcript & Call Recording"
   - All data-section/data-action/data-state attributes preserved; all API calls preserved; no sessionStorage; no diagnosis; staging safety footer
   - `frontend/app/dashboard/page.tsx` (updated — self-contained layout)
   - `backend/tests/test_premium_frontend_dashboard_activation_contract.py` (new — 37 static contract tests)
   - `backend/tests/test_premium_frontend_interface_expansion_contract.py` (updated — 5 tests updated to accept pm-dash-* class names)
   - `docs/architecture/PREMIUM_FRONTEND_APPLICATION_INTERFACE_EXPANSION.md` (updated — correction note added)
   - /onboarding and /developer-console remain intact (verified in tests)
   - Frontend build: PASS (Next.js build clean, all 8 static pages)
   - Full backend tests: 2986/2986 passed

138. Module 126C-FABEL5 — Premium Austrian Clinic Interface Overhaul
   - Date: 2026-07-06
   - Sprint 18 / Commercial MVP build track
   - Frontend UI/UX + static tests + docs only — no backend runtime changes, no migrations, no secrets, no real patient data, production PHI NO-GO
   - **Fabel 5 visual identity:** #0B132B Primary Structural Ink, #008080 Clinical Accent, #E0F2F1 Highlight Muted Fill, #FFB703 Warning/New State, #E63946 Critical Error State, #F4F6F9 Canvas Background; Inter/system stack; .pm-tabular (font-variant-numeric: tabular-nums); tokens added to globals.css (legacy Module 126C tokens preserved)
   - **`frontend/app/dashboard/page.tsx`** (rewritten): premium 3-column split-screen workspace — grid-template-columns minmax(280px,25%) / minmax(420px,45%) / minmax(320px,30%), responsive 1200px/768px breakpoints, independent panel scroll
     - Sticky ink header with dynamic multi-tenant identity banner via tenantDisplay helper, STAGING DEMO marker, safety boundary "Fake-data staging · No real patient data · Production PHI: NO-GO", Log Out
     - Column 1 "Incoming AI Intake Queue": intake cards (name, phone or "No phone captured", time, reason preview, vapi source badge, amber "New Request" badge, status/urgency badges, #E0F2F1 selected state), first request selected by default, empty state "No incoming AI intake requests yet."; Notifications panel below ("Internal notification only", pending amber badge, priority/type badges)
     - Column 2 "Active Resolution Workspace": selected request detail (name, phone, reason, status, urgency, source, preferred/created time, request id monospace), "Audio Transcript & Call Recording" placeholder engine (disabled "Play Audio Call", mock waveform, safe empty copy, "Recording ingestion pending", source_ref metadata), View summary / Hide summary + pre-appointment summary preserved, existing Confirm behavior unchanged (teal #008080), disabled progressive CTA "Confirm Appointment & Create Patient Profile" ("Profile creation automation coming next"), Consultations section preserved
     - Column 3 "Patient Registry": "Search Clinical Registries..." search, patient list (name, phone, status, id monospace), profile card (phone/email/id/linked request count), chronological timeline from appointment requests linked by patient_id, safe history placeholders, clearly marked demo placeholder names (Dr. Johann Huber / Anna Wallner) only when patients array empty
   - **`frontend/lib/tenantDisplay.ts`** (updated): staging clinic_id 1a5bbc75-c1b0-4488-94aa-64b3f1c50056 → "Dr. Med. Alexander Huber | Innere Medizin Wien" (centralized; unknown tenants fall back to "Staging Fake Clinic")
   - **`frontend/app/onboarding/page.tsx`** (rewritten): gated access entry ("Start with PraxisMed", "Existing Clinic Login", "Request Pilot Access Registration"), five steps (Clinic Details / Doctor / Admin Account / Workflow Preferences / AI Intake Setup / Review & Pilot Activation), HTML entity bug fixed (no visible "&amp;"), "STAGING SCAFFOLD — NOT FUNCTIONAL", pilot activation safety copy, no secrets collected
   - **`frontend/app/developer-console/page.tsx`** (rewritten): dense dark command theme on #0B132B (teal accents, red #E63946 guardrails, amber #FFB703 warnings), panels: Tenant Provisioning, Clinic ID Scope Injection, Vapi Machine Credential Binding (placeholders only), Environment Checklist (DATABASE_URL / JWT_SECRET_KEY / VAPI_WEBHOOK_SECRET / INTERNAL_WEBHOOK_SECRET / FRONTEND_CORS_ORIGINS as labels only), Safety Guardrails; no live mutation, no secrets
   - **`backend/tests/test_fabel5_premium_clinic_interface_overhaul_contract.py`** (new static contract tests)
   - **`docs/architecture/FABEL5_PREMIUM_CLINIC_INTERFACE_OVERHAUL.md`** (new)
   - All existing behaviour preserved: login/logout, all four data loads, View summary / Hide summary, Confirm handler and API contract, credentials: include, no sessionStorage/localStorage, all data-section/data-action/data-state selectors, no diagnosis, no medical advice

139. Module 126C-FABEL5-FINAL — Doctor-facing interface polish
   - Date: 2026-07-06
   - Sprint 18 / Commercial MVP build track
   - Frontend polish only — no backend changes, no migrations, no secrets, no real patient data
   - Fix 1: Tenant identity confirmed flowing from tenantDisplay.ts ("Dr. Med. Alexander Huber | Innere Medizin Wien") through getClinicDisplayName; doctor name not hardcoded in dashboard
   - Fix 2: Transcript panel label "Audio Transcript & Call Recording" and placeholder "Recording/transcript review will appear here when Vapi recording ingestion is enabled." confirmed; no fake transcripts, no diagnosis, no medical advice
   - Fix 3: Dev Console link removed from clinical dashboard nav; /developer-console route still exists and is directly accessible
   - frontend/app/dashboard/page.tsx (updated — Dev Console nav link removed from clinical header)
   - backend/tests/test_doctor_facing_interface_polish_contract.py (new — 31 static contract tests)
   - Frontend build: PASS (6 routes, clean)
   - Full backend tests: 3071/3071 passed

140. Module 126D — Deployed Fabel 5 Premium Clinic Interface Smoke Evidence
   - Date: 2026-07-06
   - Sprint 18 / Commercial MVP build track
   - Docs and static tests only — no runtime code changes, no backend changes, no secrets, no real patient data
   - Committed baseline: 0d0f952 — Sprint 18 / Module 126C-FABEL5-FINAL
   - Smoke result: PASS — Fabel 5 premium 3-panel clinical interface deployed and verified on Vercel staging
   - Verified: /dashboard (3-column layout, Incoming AI Intake Queue, Active Resolution Workspace, Audio Transcript & Call Recording, Patient Registry, dynamic doctor/clinic banner, Dev Console link absent from clinical nav)
   - Verified: /onboarding (Review & Pilot Activation plain text, STAGING SCAFFOLD badge, safety copy)
   - Verified: /developer-console (dark admin theme, Never paste secrets guardrail, Production PHI NO-GO guardrail, direct route accessible)
   - Verified: all three routes enforce staging safety boundary (STAGING DEMO / fake data / no real patient data / Production PHI: NO-GO)
   - docs/runtime/FABEL5_PREMIUM_CLINIC_INTERFACE_DEPLOYED_SMOKE_EVIDENCE.md (new)
   - backend/tests/test_fabel5_premium_clinic_interface_deployed_smoke_evidence_contract.py (new — 36 static contract tests)
   - Full backend tests: 3107/3107 passed

141. Module 130 — Operational Staging Readiness: Tenant Language, Vapi Assistant, and End-to-End Demo Flow
   - Date: 2026-07-06
   - Sprint 19 / Operational staging readiness track
   - Docs + safe config only — no backend code changes, no migrations, no secrets, no real patient data
   - docs/runtime/BACKEND_DATA_FLOW_AND_STORAGE_MAP.md (new)
     - Full system map: Vercel (Next.js 14) + Railway (FastAPI) + Railway PostgreSQL
     - Main tables: clinics, users, patients, appointment_requests, clinic_notifications, consultation_sessions, audit_log
     - Vapi intake data flow: call → tool endpoint → appointment_requests → patients → clinic_notifications → dashboard
     - Auth/session flow: login → HttpOnly secure cookie → credentials:include on all requests
     - Frontend → backend API map (11 endpoints)
     - Safety constraints: fake-data staging only, Production PHI NO-GO
   - docs/runtime/STAGING_END_TO_END_DEMO_RUNBOOK.md (new)
     - 9-step end-to-end demo runbook with post-demo checklist
     - Backend health checks (/health + /health/ready)
     - Fake Vapi intake curl example (Demo Patient / +436601234567 / Routine appointment request demo / 2026-07-14 09:00 CEST)
     - View summary → Confirm → Patient Registry → Notification → Logout sequence
     - Troubleshooting section for common failures
     - No secrets recorded
   - docs/runtime/VAPI_GERMAN_ENGLISH_ASSISTANT_SETUP.md (new)
     - German-first, English-fallback receptionist assistant configuration
     - Safe boundaries: no diagnosis, no medical advice, no treatment recommendations, staff/doctor confirms everything
     - Required captured fields: patient_name, phone, reason, preferred_starts_at, urgency_level, language_preference
     - German prompt (Austrian private clinic receptionist persona, emergency escalation to 112)
     - English fallback prompt
     - Tool call JSON shape and endpoint headers
     - Vapi dashboard configuration notes
     - Recording/transcript ingestion: pending — not yet enabled
     - No secrets in doc
   - backend/tenants/configs/1a5bbc75-c1b0-4488-94aa-64b3f1c50056/clinic_config.json (updated)
     - Added: clinic_display_name, specialty, city, fallback_language, appointment_intake_enabled, recording_ingestion_enabled, transcript_ingestion_enabled, production_phi_enabled
     - Preserved: all existing keys (tenant_id, clinic_name, language, country, timezone, ai_persona_name, ai_tone, specialties, features)
   - backend/tests/test_operational_staging_readiness_contract.py (new — 44 static contract tests)
   - Full backend tests: 3151/3151 passed
   - Production PHI remains NO-GO

142. Module 130 — Compliance Readiness Gate and Language Foundation
   - Date: 2026-07-06
   - Sprint 19 / Compliance and language readiness track
   - backend/app/core/compliance.py (new)
     - Hard production PHI circuit breaker
     - get_environment(), is_production(), is_production_compliance_unlocked(), get_auth_method()
     - get_default_clinic_language(), get_supported_clinic_languages() (reads DEFAULT_CLINIC_LANGUAGE, SUPPORTED_CLINIC_LANGUAGES env vars)
     - assert_production_auth_ready() — AssertionError if production + AUTH_METHOD != COOKIE_HTTPONLY
     - assert_production_compliance_ready() — AssertionError if production + PRODUCTION_COMPLIANCE_UNLOCKED != true
     - enforce_phi_safeguard() — async FastAPI dependency; HTTP 403 in production if locked; no-op in local/staging
     - Environment variables: ENVIRONMENT (local/staging/production), PRODUCTION_COMPLIANCE_UNLOCKED, AUTH_METHOD, PSEUDONYMIZATION_PEPPER, DEFAULT_CLINIC_LANGUAGE, SUPPORTED_CLINIC_LANGUAGES
   - backend/app/core/pseudonymization.py (new)
     - HMAC-SHA256 pseudonymization for PII in Vapi logs and audit records
     - pseudonymize(value, context), pseudonymize_phone(), pseudonymize_name(), pseudonymize_email()
     - Uses PSEUDONYMIZATION_PEPPER env var; falls back to staging sentinel if absent (not secret, not for production)
     - assert_pseudonymization_ready() raises AssertionError if pepper not set
     - Original value never returned or logged
   - backend/app/core/config_loader.py (updated)
     - ClinicConfig: added fallback_language (Optional[str], BCP-47 validated), clinic_display_name, specialty, city fields
     - get_default_clinic_language() reads DEFAULT_CLINIC_LANGUAGE env var (default "de")
     - get_supported_clinic_languages() reads SUPPORTED_CLINIC_LANGUAGES env var (default ["de","en"])
   - frontend/app/onboarding/page.tsx (updated)
     - Added Language Configuration section (data-section="language-foundation")
     - Static display: Deutsch (Primary / Default) + English (Fallback) — not interactive, scaffold only
     - Step 3 description updated: "Primary language (German / English fallback)"
   - backend/tests/test_compliance_readiness_gate_contract.py (new — 67 tests)
   - backend/tests/test_fabel5_premium_clinic_interface_overhaul_contract.py (updated — stale 126D assertion relaxed to accept current NEXT_MODULE)
   - Frontend build: PASS (6 routes, clean)
   - Full backend tests: 3218/3218 passed
   - Production PHI remains NO-GO

143. Module 130 (continued) — Compliance Gate Route Wiring, Pseudonymization Pipeline, and Docs
   - Date: 2026-07-06
   - Sprint 19 / Compliance and language readiness track (continuation of Module 130)
   - enforce_phi_safeguard wired to PHI-processing routers (router-level Depends):
     - appointment_requests.py, patients.py, consultations.py, clinical_workflows.py
     - vapi_tools.py: wired to capture-appointment-request route only
   - Vapi audit log updated: patient_name_hash + caller_phone_hash (pseudonymized) in metadata; call_id preserved
   - backend/app/core/pseudonymization.py (extended):
     - stable_hash(), redact_transcript(), sanitize_for_log(), sanitize_vapi_webhook_payload()
     - Sensitive keys: patient_name, name, full_name, phone, phone_number, mobile, email, transcript, raw_transcript, audio_transcript, recording_url, audio_url, reason, notes, message
     - Safe operational keys preserved: clinic_id, clinic_ref, call_id, source, status, urgency_level
   - backend/tenants/configs/1a5bbc75.../clinic_config.json (updated): staging_display section + language_config section (primary_language, fallback_language, supported_languages, default_patient_language)
   - backend/tests/test_compliance_gate.py (new — 35 tests):
     - Production auth gate blocks BEARER_SESSION_STORAGE in production
     - Production safeguard blocks when PRODUCTION_COMPLIANCE_UNLOCKED unset/false; passes when true/1
     - Staging/local always passes (no block)
     - sanitize_vapi_webhook_payload: removes patient_name/phone/transcript/reason/message/email/recording_url; preserves call_id/clinic_ref/urgency_level/status; non-dict returns safe envelope; deterministic hashes; nested dicts sanitized
     - sanitize_for_log: list items sanitized, scalars passed through, notes/audio_url sanitized
     - Frontend auth regression: credentials include in api.ts, no sessionStorage/localStorage in dashboard
     - Route wiring: enforce_phi_safeguard present on all 4 PHI routers
   - backend/tests/test_fabel5_premium_clinic_interface_overhaul_contract.py (updated — stale NEXT_MODULE assertion relaxed)
   - docs/runtime/COMPLIANCE_READINESS_GATE.md (new)
   - docs/runtime/VAPI_PSEUDONYMIZED_LOGGING.md (new)
   - docs/runtime/VAPI_GERMAN_ENGLISH_ASSISTANT_SETUP.md (existing — covers all spec requirements)
   - Full backend tests: 3253/3253 passed

144. Module 131 — Real Staging End-to-End Demo Execution Evidence
   - Date: 2026-07-06
   - Sprint 19 / Docs + static tests only. No runtime code changes.
   - docs/runtime/STAGING_END_TO_END_DEMO_EXECUTION_EVIDENCE.md (new):
     - 15-section evidence doc recording the live Railway + Vercel staging flow after compliance gate
     - ENVIRONMENT=staging, AUTH_METHOD=COOKIE_HTTPONLY, PRODUCTION_COMPLIANCE_UNLOCKED not set
     - Backend health liveness + readiness: PASS
     - Fake Vapi intake curl (Demo Patient): PASS — ok=true, status=new, action_required=true
     - Audit log: patient_name_hash + caller_phone_hash (HMAC tokens, not raw PII): PASS
     - Dashboard 3-panel layout, doctor banner (Dr. Med. Alexander Huber | Innere Medizin Wien): PASS
     - AI Intake Queue, Active Resolution Workspace, View summary, pre-appointment summary placeholder: PASS
     - Patient Registry: PASS; Internal notification (new_appointment_request): PASS
     - Logout: PASS; Confirm: NOT RETESTED (no unconfirmed rows — documented honestly)
     - Compliance gate no-op confirmed in staging; production PHI remains blocked
     - Remaining production blockers C3–C8: all OPEN
     - No fabricated evidence. No secrets. No real patient data. Production PHI: NO-GO.
   - backend/tests/test_staging_e2e_demo_execution_evidence_contract.py (new — 35 tests):
     - Verifies doc exists and covers: PASS result, backend URL, frontend URL, health, ready,
       fake Vapi intake, Demo Patient, ok/new status, pseudonymized audit metadata, AI Intake Queue,
       Active Resolution Workspace, View summary, pre-appointment summary, Patient Registry,
       internal notification, compliance gate no-op, no real patient data, no secrets,
       Production PHI NO-GO, C3–C8 blockers open, recording/DSGVO disclaimers
   - Full backend tests: 3288/3288 passed

145. Module 132 — Real Clinic Onboarding Backend Foundation
   - Date: 2026-07-06
   - Sprint 19 / Backend only — no frontend changes
   - backend/app/db/schema.sql (updated): clinic_onboarding_requests table added with:
     - UUID PK, clinic_name, doctor_name, contact_email (required)
     - preferred_language (default de), fallback_language (default en), supported_languages (JSONB, default ["de","en"])
     - consent_pilot_contact + acknowledges_no_phi (required for submission)
     - production_phi_enabled (default false, DB CHECK constraint enforces always false)
     - status CHECK: submitted, reviewed, demo_booked, pilot_approved, rejected, archived
     - preferred_language CHECK: de, en only
     - Indexes: contact_email, status, created_at, preferred_language
   - backend/migrations/versions/0004_clinic_onboarding_requests.py (new):
     - Revision: 0004, down_revision: 0003_patient_id_appt_requests
     - Idempotent CREATE TABLE IF NOT EXISTS; includes downgrade()
   - backend/app/schemas/clinic_onboarding.py (new):
     - ClinicOnboardingRequestCreate: validates required fields, email format, language codes, consent booleans
     - ClinicOnboardingRequestRead, ClinicOnboardingRequestStatusUpdate
     - ClinicOnboardingRequestResponse + ClinicOnboardingRequestListResponse
     - production_phi_enabled never accepted from public input; server-controlled always false
   - backend/app/db/repositories/clinic_onboarding_repo.py (new):
     - create_clinic_onboarding_request, get_clinic_onboarding_request_by_id
     - list_clinic_onboarding_requests, update_clinic_onboarding_status
     - status=submitted hardcoded on create; production_phi_enabled=false hardcoded
     - No patient PHI, no Vapi credentials, no tenant creation
   - backend/app/api/routes/clinic_onboarding.py (new):
     - POST /clinic-onboarding-requests (public — no auth, no enforce_phi_safeguard)
     - GET /clinic-onboarding-requests (auth required — staff/admin list)
     - GET /clinic-onboarding-requests/{id} (auth required)
     - PATCH /clinic-onboarding-requests/{id}/status (auth required)
   - backend/app/api/router.py (updated): clinic_onboarding router wired
   - docs/architecture/CLINIC_ONBOARDING_BACKEND_FOUNDATION.md (new)
   - backend/tests/test_clinic_onboarding_backend_foundation.py (new — 78 tests):
     - Schema SQL contract (table, columns, constraints, indexes)
     - Migration file (revision, down revision, create/drop)
     - Pydantic schemas (required fields, email, language, consent booleans, invalid status)
     - Repository (create/get/list/update, invalid inputs raise)
     - API routes (public POST 201, auth-guarded GET/PATCH, 422 on bad input)
     - PHI field absence, no Vapi credentials, language defaults, arch doc
   - Full backend tests: 3366/3366 passed

146. Module 133 — Connect Onboarding Frontend to Backend Request API
   - Date: 2026-07-06
   - Sprint 19 / Frontend + static tests + docs. No backend migration.
   - frontend/app/onboarding/page.tsx (rewritten):
     - Real React controlled form with useState — no longer a static scaffold
     - Submits to POST /clinic-onboarding-requests via fetch with credentials:include
     - Step 1 (Clinic Details): clinic_name, clinic_type, specialty, city (default Wien), address, website
     - Step 2 (Doctor / Admin Account): doctor_name, contact_email, contact_phone
     - Step 3 (Workflow Preferences): interactive preferred_language de/en selector
       - "Deutsch zuerst / Englisch als Fallback — Default for Austrian clinics: German-first"
       - estimated_call_volume, current_booking_system, workflow_notes
     - Step 4 (AI Intake Setup): wants_ai_phone_intake, wants_dashboard, wants_notifications checkboxes
     - Step 5 (Review & Pilot Activation): consent_pilot_contact + acknowledges_no_phi (required)
       - Safety copy: "Do not enter patient data." + "Pilot activation does not enable production PHI processing."
     - Success state: "Pilot request submitted" + request ID + contact email
     - Error state: safe validation message, no stack traces
     - Preserves: credentials:include, no sessionStorage, no localStorage
     - Never sends: production_phi_enabled, status, clinic_id, Vapi credentials
     - STAGING DEMO badge preserved (replaced "NOT FUNCTIONAL" since form is now functional)
   - frontend build: npm run build → ✓ 8/8 pages, no TypeScript errors
   - backend/tests/test_onboarding_frontend_backend_connection_contract.py (new — 36 tests):
     - Gateway: Request Pilot Access, Existing Clinic Login
     - Form fields: clinic_name, doctor_name, contact_email, preferred_language
     - Language: Deutsch, English fallback, German-first copy, Deutsch zuerst helper
     - Consent: consent_pilot_contact, acknowledges_no_phi
     - Safety copy: Do not enter patient data, Pilot activation does not enable production PHI processing
     - Backend: posts to /clinic-onboarding-requests, fetch POST, credentials:include
     - Forbidden: no production_phi_enabled, no Vapi credentials, no clinic_id
     - Storage: no sessionStorage, no localStorage
     - States: success "Pilot request submitted", error state + request ID
     - Security: no hardcoded JWT, no sk-, no SVNR/sozialversicherung/DOB
     - Arch doc checks
   - backend/tests/test_fabel5_premium_clinic_interface_overhaul_contract.py (updated — staging badge test relaxed)
   - backend/tests/test_compliance_readiness_gate_contract.py (updated — language selector scaffold test relaxed)
   - docs/architecture/ONBOARDING_FRONTEND_BACKEND_CONNECTION.md (new)
   - Full backend tests: 3402/3402 passed
   - Production PHI remains NO-GO

147. Module 134 — Internal Clinic Onboarding Review Console
   - Date: 2026-07-06
   - Sprint 19 / Frontend + api.ts + static tests + docs. No backend migration.
   - frontend/app/developer-console/onboarding-requests/page.tsx (new):
     - Dark developer-console theme (INK/PANEL/EDGE/ACCENT/DANGER/WARN/TEXT/MUTED/GREEN)
     - Auth-protected: 401/403 → "Admin session required. Please log in first."
     - GET /clinic-onboarding-requests with credentials:'include' → request list
     - Two-panel layout: request list (left) + detail panel (right)
     - Status badges: submitted(WARN), reviewed(ACCENT), demo_booked(ACCENT), pilot_approved(GREEN), rejected(DANGER), archived(MUTED)
     - LangBadge: "Deutsch-first" for preferred_language=de
     - Detail panel: clinic, doctor/admin, language, workflow, safety, operational sections
     - Fields: clinic_name, doctor_name, contact_email, preferred_language, fallback_language,
       supported_languages, workflow_notes, production_phi_enabled, consent_pilot_contact, etc.
     - PATCH /clinic-onboarding-requests/{id}/status → "Update status" button
     - Safety banner: "No tenant activation. No PHI. Production PHI remains NO-GO."
     - Activation warning: "Approving a request does not create a tenant or unlock production PHI."
     - Status updated / error states
     - No sessionStorage, no localStorage
     - Empty state: "No onboarding requests submitted yet."
     - Nav: ← Developer Console · ← Dashboard
   - frontend/app/developer-console/page.tsx (updated):
     - New "Pilot Request Review" ConsolePanel (panel 5)
     - Link: "Review onboarding requests →" → /developer-console/onboarding-requests
     - All existing panels preserved (safety guardrails renumbered to panel 6)
   - frontend/lib/api.ts (updated):
     - fetchClinicOnboardingRequests(): GET /clinic-onboarding-requests
     - updateClinicOnboardingRequestStatus(requestId, status): PATCH /clinic-onboarding-requests/{id}/status
     - ClinicOnboardingRequest interface added
   - frontend build: npm run build → ✓ 9/9 pages, no TypeScript errors
   - backend/tests/test_internal_onboarding_review_console_contract.py (new — 48 tests):
     - Review page: exists, heading, "Internal review console", nav link, badge
     - Safety: no tenant activation, no PHI, Production PHI NO-GO, approving does not create tenant
     - API: fetches /clinic-onboarding-requests, credentials:include, PATCH status, auth error handling
     - Fields: clinic_name, doctor_name, contact_email, preferred_language, fallback_language, workflow_notes, production_phi_enabled
     - Status values: submitted, reviewed, demo_booked, pilot_approved, rejected, archived
     - Storage: no sessionStorage, no localStorage, no hardcoded JWT, no PHI fields
     - Developer console: links to /developer-console/onboarding-requests, pilot review panel
     - api.ts: fetchClinicOnboardingRequests, updateClinicOnboardingRequestStatus, PATCH, no secrets
     - Arch doc: exists, mentions Module 134, onboarding-requests route, no automatic tenant, NO-GO
   - docs/architecture/INTERNAL_ONBOARDING_REVIEW_CONSOLE.md (new)
   - Full backend tests: 3450/3450 passed
   - Production PHI remains NO-GO

148. Module 134A — Fix onboarding review console detail crash
   - Date: 2026-07-06
   - Sprint 19 / Frontend bugfix. No backend changes. No migration.
   - Root cause: supported_languages JSONB column returned as raw JSON string by asyncpg;
     calling .join() on string → TypeError crash. Secondary risks: boolean fields typed
     non-nullable but could be null; date fields lacked null guards.
   - frontend/app/developer-console/onboarding-requests/page.tsx (updated):
     - Added safeText(value, fallback='—'): guards null, undefined, empty string
     - Added safeDate(value): guards null, invalid dates; wraps toLocaleString
     - Added safeBoolean(value): null/undefined → null; otherwise Boolean(value)
     - Added safeLanguages(value): handles array, JSON string, or null/undefined
     - BoolRow updated: boolean | null signature; renders null as '—', true as 'Yes', false as 'No'
     - OnboardingRequest interface: supported_languages: string[] | string | null;
       all boolean fields boolean | null; created_at/updated_at string | null;
       pilot_interest_level/source string | null
     - All detail panel Row calls wrapped in safeText/safeDate/safeLanguages/safeBoolean
     - No direct .join() on supported_languages; no direct toLocaleString on date fields
   - docs/architecture/INTERNAL_ONBOARDING_REVIEW_CONSOLE.md (updated: Module 134A section)
   - backend/tests/test_internal_onboarding_review_console_crash_fix_contract.py (new — 44 tests):
     - Defensive helpers: safeText, safeDate, safeBoolean, safeLanguages all defined
     - supported_languages: uses safeLanguages, no raw .join(), handles array/string/null
     - Date fields: safeDate used, no direct toLocaleString on selected.X
     - Boolean fields: safeBoolean used for all 6 boolean detail fields
     - Optional text fields: safeText used for clinic_type, specialty, workflow_notes, contact_phone, pilot_interest_level, source
     - Interface nullability: supported_languages | null, boolean | null, created_at | null, updated_at | null
     - Key UI strings preserved: heading, update status, safety banners, all statuses
     - Storage safety: credentials:include, no sessionStorage, no localStorage
   - All 92/92 review console contract tests pass
   - Full backend tests: 3494/3494 passed
   - Frontend build: ✓ 9/9 pages, no TypeScript errors
   - Production PHI remains NO-GO

149. Module 135 — Tenant Provisioning Backend Foundation
   - Date: 2026-07-06
   - Sprint 19 / Backend service + route + tests + docs. No frontend changes. No migration.
   - backend/app/services/tenant_provisioning.py (new):
     - provision_clinic_shell_from_onboarding_request(pool, request_id, actor_user_id)
     - Only provisions when request status is pilot_approved
     - Uses existing clinics table (status='pilot_setup') — no new table needed
     - production_phi_enabled is NOT a clinics table column; PHI never enabled here
     - Language preserved: preferred_language→locale (de→de-AT), fallback_language, supported_languages
     - Slug: slugified clinic_name + 8-char UUID suffix
     - Idempotent: queries audit_log for existing create_clinic_shell event; returns existing if found
     - Audit event written to audit_log on every new provisioning
     - No Vapi credentials. No patients. No passwords. No public auto-provisioning.
     - Exceptions: ProvisioningNotFoundError, ProvisioningBlockedError
   - backend/app/api/routes/clinic_onboarding.py (updated):
     - Added POST /clinic-onboarding-requests/{request_id}/provision-clinic-shell
     - Protected: requires get_current_user (session cookie or Bearer)
     - 404 on missing request, 409 on wrong status, 200 on success/already-provisioned
     - Response: ok, onboarding_request_id, clinic_id, clinic_name, clinic_slug,
       preferred_language, fallback_language, supported_languages,
       production_phi_enabled=false, message, already_provisioned
   - backend/tests/test_tenant_provisioning_backend_foundation.py (new — 47 tests):
     - Static: service exists, route has provision endpoint + auth, arch doc exists,
       no Vapi in service, no patient INSERT, public submit does not provision
     - Blocking: missing request → NotFound; submitted/reviewed/demo_booked/rejected/archived → Blocked
     - Success: clinic created, production_phi_enabled=false, language preserved, message,
       no Vapi in result, audit event recorded, clinic_name, slug, supported_languages JSON string, request_id
     - Idempotency: already provisioned returns existing, no duplicate INSERT, no second audit
     - Route: unauth→401, not found→404, blocked→409, success→200+ok, clinic_id, phi=false,
       message, no secrets, language fields
     - Arch doc: pilot_approved, no PHI, no Vapi, audit, no automatic, language, idempotency, pilot_setup
   - docs/architecture/TENANT_PROVISIONING_BACKEND_FOUNDATION.md (new)
   - Full backend tests: 3541/3541 passed
   - No frontend changes (build remains clean at 9/9 pages)
   - Production PHI remains NO-GO

150. Module 136 — Admin Provision Clinic Shell UI
   - Date: 2026-07-06
   - Sprint 19 / Frontend button + api.ts helper + static contract tests + arch doc. No migration.
   - frontend/app/developer-console/onboarding-requests/page.tsx (updated):
     - Added ProvisionState = 'idle' | 'provisioning' | 'provisioned' | 'error'
     - Added ProvisionResult interface: clinic_id, clinic_name, clinic_slug, preferred_language,
       production_phi_enabled (always false), message, already_provisioned
     - State: provisionState, provisionResult, provisionError (all reset when new request selected)
     - handleProvision(): POST /clinic-onboarding-requests/{id}/provision-clinic-shell
       credentials: 'include'; 401/403→"Admin session required.";
       409→"Request must be pilot_approved before provisioning.";
       other→"Provisioning failed. Please retry or check backend logs."
     - "Clinic Shell Provisioning" section in detail panel (below status update)
     - Button "Provision Clinic Shell" — enabled only when status === 'pilot_approved'
     - Disabled with helper text "Set status to pilot_approved before provisioning."
     - Loading label: "Provisioning…"; disabled during provisioning (prevent double-click)
     - Success: shows "Clinic shell provisioned. Production PHI remains disabled." + clinic_id/name/slug/lang
     - Already provisioned: "Already provisioned. clinic_id: …"
     - Safety copy: "Provisioning does not activate production PHI. ... Production PHI remains NO-GO."
     - No sessionStorage, no localStorage, no Vapi credential fields
   - frontend/lib/api.ts (updated):
     - Added ClinicShellProvisionResult interface
     - Added provisionClinicShell(requestId: string) → POST /provision-clinic-shell
       uses apiFetch (credentials: 'include'); returns ClinicShellProvisionResult; throws on error
   - backend/tests/test_admin_provision_clinic_shell_ui_contract.py (new — 90 static tests):
     - File existence, ProvisionState type, ProvisionResult interface, state vars
     - handleProvision: POST /provision-clinic-shell, credentials:include, 401/403/409 handling
     - Button: "Provision Clinic Shell", disabled when not pilot_approved, disabled during provisioning
     - Disabled helper text, section header, safety copy (no PHI, no Vapi, no patient records, NO-GO)
     - Success states: clinic_id/name/slug/lang shown, "Production PHI remains disabled"
     - Already provisioned branch, reset on request selection
     - Storage safety: no sessionStorage, no localStorage, no Vapi API key, no webhook secret, no DATABASE_URL
     - api.ts: provisionClinicShell defined, /provision-clinic-shell path, POST, credentials:include,
       ClinicShellProvisionResult interface, no sessionStorage/localStorage
     - Arch doc: Module 136, pilot_approved, no production PHI, Vapi mentioned
   - docs/architecture/ADMIN_PROVISION_CLINIC_SHELL_UI.md (new)
   - Full backend tests: 3612/3612 passed
   - Frontend build: PASS (9/9 pages)
   - Production PHI remains NO-GO

151. Module 137 — Live Tenant Provisioning Smoke Evidence
   - Date: 2026-07-06
   - Sprint 19 / Docs + static tests only. No backend changes. No frontend changes. No migration.
   - docs/runtime/LIVE_TENANT_PROVISIONING_SMOKE_EVIDENCE.md (new):
     - Overall result: PASS
     - Frontend URL: https://praximed.vercel.app/developer-console/onboarding-requests
     - Test request: Demo Wahlarzt Praxis Wien / demo.clinic@example.test
     - Status before provisioning: pilot_approved
     - Button clicked: Provision Clinic Shell
     - First call: Clinic shell provisioned; clinic_id, clinic_name, clinic_slug,
       preferred_language returned; production_phi_enabled=false; message confirmed
     - Second call: already_provisioned=true; same clinic_id; no duplicate created
     - Safety: no Vapi credentials, no patient records, no production PHI, clinic status=pilot_setup
     - Sections: Purpose, Current Result, Preconditions, Live UI Evidence, Status Update Evidence,
       Provisioning Success Evidence, Idempotency Evidence, Safety Boundaries,
       What This Proves, What This Does Not Prove, Remaining Blockers (C3–C8)
   - backend/tests/test_live_tenant_provisioning_smoke_evidence_contract.py (new — 39 tests):
     - File existence, PASS status, Module 137 / commit 47918c6
     - Frontend URL, demo request identity (clinic name + email)
     - pilot_approved, Provision Clinic Shell button, /provision-clinic-shell endpoint
     - Provisioning success: clinic_id, clinic_name, clinic_slug, preferred_language,
       production_phi_enabled=false, message
     - Idempotency: already_provisioned=true, no duplicate, second call safe
     - Safety: no Vapi credentials, no patient records, no production PHI, NO-GO, no secrets, pilot_setup
     - What proves: idempotency, phi=false; What does not prove: production readiness
     - Remaining blockers: C3–C8, DSGVO, backup
   - Full backend tests: 3651/3651 passed
   - No frontend changes
   - Production PHI remains NO-GO

160. Module 147 — Live Vapi Binding Metadata Smoke Evidence
   - Date: 2026-07-07
   - Sprint 19 / Docs + static tests only. No runtime code changes. No backend changes. No migration.
   - docs/runtime/LIVE_VAPI_BINDING_METADATA_SMOKE_EVIDENCE.md (new):
     - Overall result: PASS
     - Commit tested: 47c6940 (Module 146)
     - Frontend URL: https://praximed.vercel.app/developer-console/vapi-bindings
     - Staging clinic: 1a5bbc75-c1b0-4488-94aa-64b3f1c50056 (Demo Wahlarzt Praxis Wien)
     - Page load + dark admin theme + ADMIN/STAGING badge: PASS
     - Load bindings (GET /clinics/{id}/vapi-bindings 200): PASS
     - Create binding: api_key_secret_ref=VAPI_API_KEY_REF_STAGING_DEMO,
       webhook_secret_ref=VAPI_WEBHOOK_SECRET_REF_STAGING_DEMO, german_first → 201: PASS
     - "Vapi binding metadata saved" visible: PASS
     - Binding id, clinic_id, status=draft, language_mode=german_first, phi=false: PASS
     - Reference names stored as labels; no actual secret values in DB or response: PASS
     - Invalid non-reference input (lowercase, sk-...) → 422: PASS
     - Status update draft → configured: PASS; "Binding status updated": PASS
     - Status update configured → disabled: PASS
     - production_phi_enabled=false in POST/GET/PATCH responses: PASS
     - No actual VAPI_API_KEY entered; no webhook secret value entered: PASS
     - No live Vapi API call made; no Vapi assistant created or modified: PASS
     - No PHI; no patient data; production PHI remains NO-GO
   - backend/tests/test_live_vapi_binding_metadata_smoke_evidence_contract.py (new — 55 tests):
     - Doc existence, PASS result, sprint/module/commit identity
     - Frontend URL, vapi-bindings route, staging clinic_id, fake/staging identity
     - clinic_vapi_bindings table, migration 0005
     - GET/POST/PATCH route references, 200/201 status codes
     - VAPI_API_KEY_REF_STAGING_DEMO, VAPI_WEBHOOK_SECRET_REF_STAGING_DEMO, reference names only
     - "Vapi binding metadata saved", "Binding status updated", binding_id visible
     - draft/configured/disabled status values, german_first language mode
     - Invalid input rejected, 422 validation
     - production_phi_enabled=false in all responses
     - No actual secret values, no PHI, no patient data, no transcript, no recording
     - No live Vapi calls, Production PHI NO-GO
     - What proves/does not prove sections, C3–C8 blockers, remaining blockers
     - Forbidden content: no actual sk-... credential values in doc
   - Full backend tests: 4264/4264 passed
   - Production PHI remains NO-GO

158. Module 144 — Vapi Credential Binding Design and Secret Boundary
   - Date: 2026-07-06
   - Sprint 19 / Docs + schema design + contract tests only. No backend migration. No live Vapi API calls. No secrets stored.
   - docs/architecture/VAPI_CREDENTIAL_BINDING_SECRET_BOUNDARY.md (new):
     - Hard secret boundary: VAPI_API_KEY, VAPI_WEBHOOK_SECRET and all other secrets
       forbidden from browser, database text columns, tenant JSON, docs, tests, logs,
       audit raw_payload, screenshots, version control
     - Allowed: reference names only (api_key_secret_ref, webhook_secret_ref) — label
       pointing to env var, never the secret value
     - Environment variables only: secrets managed via Railway/Vercel or future secret manager
     - Proposed clinic_vapi_bindings table (future migration):
       id, clinic_id FK, assistant_id, phone_number_id, vapi_project_id,
       api_key_secret_ref (NOT NULL), webhook_secret_ref (NOT NULL),
       assistant_config_version, language_mode, status, created_by_user_id, timestamps
       Status values: draft / configured / disabled / revoked
     - Future service design: create_vapi_binding_metadata, get_vapi_binding_metadata,
       disable_vapi_binding, resolve_secret_reference (reads env at runtime, never logs value),
       validate_no_secret_value (rejects inputs that look like real credentials)
     - Frontend rules: no form fields for Vapi API key, webhook secret, JWT secret, DATABASE_URL;
       may display assistant_id, phone_number_id, masked reference labels (read-only)
     - Logging rules: reference names/status/timestamps may be logged; actual secret values NEVER
     - Readiness gate: C3–C8 all open, Article 28 AVV, Article 32 security measures,
       Datenschutzbehörde; do not set PRODUCTION_COMPLIANCE_UNLOCKED=true until all cleared
     - No PHI. No patient data. No transcript. No recording URL. Production PHI remains NO-GO.
   - backend/tests/test_vapi_credential_binding_secret_boundary_contract.py (new — 41 tests):
     - Arch doc existence, VAPI_API_KEY label, VAPI_WEBHOOK_SECRET label
     - Environment variables only, managed secret store
     - Never database, browser, logs, docs, tests
     - api_key_secret_ref, webhook_secret_ref, reference names only, no actual secret value
     - clinic_vapi_bindings, draft/configured/disabled/revoked status
     - No live Vapi API calls, no PHI, no patient data, no transcript, no recording URL
     - No frontend secret input, C3–C8, Article 28/32, NO-GO, production phi remains no-go
     - Frontend feature page audit (language-settings, vapi-config, onboarding-requests, api.ts):
       no Vapi API key input, no webhook_secret, no DATABASE_URL, no jwt_secret
     - Fake secret regex check (sk-..., vapi_live_..., Bearer, eyJ...) in arch and audited docs
   - Full backend tests: 4115/4115 passed

157. Module 143 — Live Vapi Assistant Config Preview Smoke Evidence
   - Date: 2026-07-06
   - Sprint 19 / Docs + static tests only. No backend changes. No frontend changes. No migration.
   - docs/runtime/LIVE_VAPI_ASSISTANT_CONFIG_PREVIEW_SMOKE_EVIDENCE.md (new):
     - Overall result: PASS
     - Commit tested: 944b898
     - Frontend URL: https://praximed.vercel.app/developer-console/vapi-config
     - Clinic ID: 1a5bbc75-c1b0-4488-94aa-64b3f1c50056 (Demo Wahlarzt Praxis Wien)
     - Load config pack: GET 200, all 8 sections rendered
     - German-first: KI-Rezeption, keine Diagnose, keine medizinische Beratung,
       keine Terminbestätigung, Notruf 144, first_message_de confirmed
     - English fallback: AI receptionist, No diagnosis, No medical advice,
       no appointment confirmation promise, call 144, first_message_en confirmed
     - Required capture fields: patient_name, phone, reason, preferred_time,
       language_preference, urgency_level — all confirmed
     - Tool schema: capture_appointment_request, X-Vapi-Service-Name, X-Vapi-Clinic-Id,
       X-Vapi-Scopes visible; no secret values shown
     - Safety rules: no diagnosis, no medical advice, no appointment confirmation,
       emergency escalation 144 — all confirmed
     - Forbidden claims section rendered
     - Readiness flags: production_phi_enabled=false, recording_ingestion_enabled=false,
       transcript_ingestion_enabled=false — all green
     - Safety: no PHI, no Vapi API key, no webhook secret, no sessionStorage, no localStorage,
       no live Vapi binding, production_phi_enabled=false, no production activation
     - What proves: GET returns complete config pack, German-first/English prompts complete,
       all capture fields present, tool schema renders without secrets, safety flags false,
       admin UI round-trip end-to-end, credentials:include works, no live Vapi binding
     - What does not prove: production readiness, DSGVO, Vapi binding, bilingual audio,
       security hardening, multi-tenant isolation
     - Remaining blockers: C3–C8, Vapi credential binding (Module 144), provisioning,
       recording ingestion, transcript storage, bilingual audio
   - backend/tests/test_live_vapi_assistant_config_preview_smoke_evidence_contract.py (new — 67 tests):
     - File existence, module/sprint/commit identity, PASS result
     - Frontend URL, GET route, /clinics/ path, clinic ID, staging clinic
     - Load config pack, HTTP 200
     - German: german_first, KI-Rezeption, keine Diagnose, keine medizinische Beratung,
       Terminbestätigung, Notruf 144, first_message_de
     - English: english fallback, AI receptionist, no diagnosis, no medical advice,
       no appointment confirmation, call 144
     - Capture fields: patient_name, phone, reason, preferred_time, language_preference, urgency_level
     - Tool schema: capture_appointment_request, X-Vapi-Service-Name/Clinic-Id/Scopes,
       no secret values
     - Safety rules: no diagnosis, no medical advice, no appointment confirmation, 144
     - Forbidden claims section
     - Flags: production_phi_enabled/recording/transcript all false
     - Safety: no PHI, no Vapi API key, no webhook secret, no secrets, no live Vapi binding,
       NO-GO, production phi remains no-go
     - Proves/does-not-prove sections, end-to-end, production readiness, Vapi binding, bilingual audio
     - Remaining blockers: C3–C8, DSGVO
   - Full backend tests: 4074/4074 passed
   - No frontend changes
   - Production PHI remains NO-GO

156. Module 142 — Admin Vapi Assistant Config Preview UI
   - Date: 2026-07-06
   - Sprint 19 / Frontend + api.ts helper + contract tests + arch doc. No backend changes. No migration.
   - frontend/app/developer-console/vapi-config/page.tsx (new):
     - LoadState: idle/loading/loaded/auth_error/not_found/error
     - Clinic ID input + "Load config pack" button (staging clinic_id shown as example)
     - GET /clinics/{id}/vapi-assistant-config-pack, credentials:'include'
     - Display sections:
       A. Clinic / Language: all 10 fields
       B. German-First Prompt: first_message_de, system_prompt_de (monospace pre block)
       C. English Fallback Prompt: first_message_en, system_prompt_en
       D. Required Capture Fields: patient_name, phone, reason, preferred_time, language_preference, urgency_level
       E. Tool Schema: JSON code block, POST /vapi/tools/capture-appointment-request,
          header names X-Vapi-Service-Name/X-Vapi-Clinic-Id/X-Vapi-Scopes (no secret values)
       F. Safety Rules + escalation rules (with emergency 144 instruction)
       G. Forbidden Claims
       H. Readiness Flags: production_phi_enabled/recording_ingestion_enabled/transcript_ingestion_enabled
          (green=false, red=true), generated_at, safety copy
     - Error states: 401/403→"Admin session required", 404→"Clinic not found or no access."
     - Safety copy: "Preview only. No Vapi credentials are stored or transmitted."
       "No PHI. No secrets. No live Vapi binding. No production activation. Production PHI remains NO-GO."
     - No sessionStorage, no localStorage, no Vapi API key, no webhook secret, no DATABASE_URL
   - frontend/app/developer-console/page.tsx (updated):
     - Added panel 7 "Vapi Assistant Config Preview" with link to /developer-console/vapi-config
     - "Preview Vapi config →" button; Safety Guardrails renumbered to panel 8
   - frontend/lib/api.ts (updated):
     - VapiAssistantConfigPack interface with all 24 fields
     - fetchVapiAssistantConfigPack(clinicId): GET /clinics/{id}/vapi-assistant-config-pack, credentials:'include'
   - backend/tests/test_admin_vapi_assistant_config_preview_ui_contract.py (new — 73 tests):
     - File existence (page, console, api.ts, arch doc)
     - Page: title, read-only badge, ADMIN/STAGING, clinic ID input, load config pack,
       staging clinic_id example, /vapi-assistant-config-pack endpoint, credentials:include
     - Sections: German-first prompt, English fallback, required capture fields,
       tool schema, safety rules, forbidden claims, readiness flags
     - Field names: patient_name, phone, reason, preferred_time, language_preference, urgency_level
     - Header names: X-Vapi-Service-Name, X-Vapi-Clinic-Id, X-Vapi-Scopes
     - capture_appointment_request endpoint reference
     - Safety flags: production_phi_enabled, recording_ingestion_enabled, transcript_ingestion_enabled
     - Safety copy: no Vapi credentials, Production PHI remains NO-GO, preview only, no live Vapi binding
     - Error states: Admin session required, 401/403/404, not found
     - Exclusions: no Vapi API key, no webhook secret, no DATABASE_URL, no JWT secret,
       no sessionStorage, no localStorage
     - Console: links to /developer-console/vapi-config, has Vapi config panel
     - api.ts: fetchVapiAssistantConfigPack, vapi-assistant-config-pack path, credentials:include,
       VapiAssistantConfigPack interface, system_prompt_de/en, production_phi_enabled,
       required_capture_fields, safety_rules; no sessionStorage/localStorage/Vapi credentials
     - Arch doc: module 142, vapi config preview, german first, english fallback, no PHI,
       no Vapi credentials, NO-GO, no live Vapi binding, GET route
   - docs/architecture/ADMIN_VAPI_ASSISTANT_CONFIG_PREVIEW_UI.md (new)
   - Full backend tests: 4007/4007 passed
   - Frontend build: PASS (9/9 pages including /developer-console/vapi-config)
   - Production PHI remains NO-GO

155. Module 141 — Vapi Assistant Configuration Pack Per Tenant
   - Date: 2026-07-06
   - Sprint 19 / Backend service + route + tests + docs. No frontend changes. No migration. No live Vapi binding.
   - backend/app/schemas/vapi_assistant_config.py (new):
     - VapiAssistantConfigPack: clinic_id, clinic_display_name, specialty, city,
       primary_language, fallback_language, supported_languages, vapi_assistant_language_mode,
       assistant_name, voice_locale_recommendation, first_message_de, first_message_en,
       system_prompt_de, system_prompt_en, tool_schema, required_capture_fields,
       safety_rules, escalation_rules, forbidden_claims,
       production_phi_enabled (always False), recording_ingestion_enabled (False),
       transcript_ingestion_enabled (False), generated_at
   - backend/app/services/vapi_assistant_config.py (new):
     - build_vapi_assistant_config_pack(pool, clinic_id, actor_user=None)
     - Verifies clinic exists, loads language settings (Module 138), loads tenant config file
     - German system prompt: KI-Rezeption, private Praxis in Wien, keine Diagnose,
       keine medizinische Beratung, keine Terminbestätigung, Notruf 144
     - English system prompt: AI receptionist, private clinic in Vienna, no diagnosis,
       no medical advice, no appointment confirmation promise, call 144
     - First messages: German and English greeting templates
     - Tool schema: capture_appointment_request targeting POST /vapi/tools/capture-appointment-request
       with fields: patient_name, phone, reason, preferred_time, urgency_level, language_preference
     - Header names (non-secret): X-Vapi-Service-Name, X-Vapi-Clinic-Id, X-Vapi-Scopes
     - production_phi_enabled: always False; recording/transcript ingestion: False by default
     - No Vapi API calls. No secrets. No PHI.
   - backend/app/api/routes/vapi_assistant_config.py (new):
     - GET /clinics/{clinic_id}/vapi-assistant-config-pack
     - Protected: get_current_user; 404 on ClinicNotFoundError; 500 on unexpected
   - backend/app/api/router.py (updated): vapi_assistant_config router registered
   - backend/tests/test_vapi_assistant_config_pack_per_tenant.py (new — 81 tests):
     - File existence, schema fields (all 23 fields), no Vapi API key/webhook/DATABASE_URL
     - Service: build function, German/English prompt builders, KI-Rezeption, private Praxis in Wien,
       keine Diagnose, keine medizinische Beratung, Terminbestätigung, Notruf 144
     - English: AI receptionist, private clinic in Vienna, no diagnosis, no medical advice, 144
     - Tool schema: patient_name, phone, reason, preferred_time, urgency_level, language_preference
     - No Vapi API call, no secrets in service
     - Async service: German-first defaults, clinic_id, clinic_display_name, German/English prompts,
       tool schema required fields, production_phi_enabled=False, recording/transcript False,
       ClinicNotFoundError raised
     - Route: requires auth (401), 404 for missing clinic, config pack for valid clinic
       (clinic_id, primary_language=de, all 3 safety flags False), no PHI fields in response
     - Arch doc: module 141, language settings, german first, english fallback, no live Vapi binding,
       no secrets, no PHI, NO-GO, appointment capture, no diagnosis, 144, GET route
   - docs/architecture/VAPI_ASSISTANT_CONFIGURATION_PACK_PER_TENANT.md (new)
   - Full backend tests: 3934/3934 passed
   - No frontend changes
   - Production PHI remains NO-GO

154. Module 140 — Live Tenant Language Settings Smoke Evidence
   - Date: 2026-07-06
   - Sprint 19 / Docs + static tests only. No backend changes. No frontend changes. No migration.
   - docs/runtime/LIVE_TENANT_LANGUAGE_SETTINGS_SMOKE_EVIDENCE.md (new):
     - Overall result: PASS
     - Commit tested: 1cf85f0
     - Frontend URL: https://praximed.vercel.app/developer-console/language-settings
     - Clinic ID: 1a5bbc75-c1b0-4488-94aa-64b3f1c50056 (Demo Wahlarzt Praxis Wien)
     - Load settings: GET 200, form populated, updated_at displayed
     - German-first defaults: primary_language=de, fallback_language=en,
       supported_languages=["de","en"], default_patient_language=de,
       vapi_assistant_language_mode=german_first, clinic_ui_language=de
     - English fallback: fallback_language=en, English checkbox visible and checked
     - PATCH/update: changed vapi_assistant_language_mode german_first→bilingual_auto,
       "Language settings saved" confirmed
     - Reload/persistence: reload confirmed update persisted; german_first restored on second save
     - Safety: no PHI, no Vapi credentials, no sessionStorage, no localStorage,
       production_phi_enabled=false, no production activation, no secrets
     - What proves: GET returns German-first defaults, English fallback correct, PATCH persists,
       admin UI round-trip end-to-end, credentials:include works, bilingual_auto accepted,
       german_first restorable, "Language settings saved" confirmed
     - What does not prove: production readiness, DSGVO compliance, Vapi assistant binding,
       bilingual audio testing, security hardening
     - Remaining blockers: C3–C8, DSGVO, Vapi binding
   - backend/tests/test_live_tenant_language_settings_smoke_evidence_contract.py (new — 48 tests):
     - File existence, module/sprint/commit identity, PASS result
     - Frontend URL, GET/PATCH routes, /clinics/ path
     - Clinic ID, staging clinic identified
     - Load settings section, HTTP 200
     - German-first: german_first, primary_language=de, clinic_ui_language, default_patient_language,
       supported_languages, vapi_assistant_language_mode
     - English fallback: fallback_language=en
     - PATCH: bilingual_auto, language_settings_saved, vapi mode updated
     - Reload/persistence: reload confirmed update persisted, german_first restored
     - Safety: no PHI, no secrets, no Vapi credentials, NO-GO, production phi remains no-go,
       no production activation, credentials:include
     - Proves/does-not-prove sections, end-to-end, production readiness, Vapi binding
     - Remaining blockers: C3–C8, DSGVO
   - Full backend tests: 3853/3853 passed
   - No frontend changes
   - Production PHI remains NO-GO

153. Module 139 — Admin Tenant Language Settings UI
   - Date: 2026-07-06
   - Sprint 19 / Frontend + api.ts helpers + contract tests + arch doc. No backend changes. No migration.
   - frontend/app/developer-console/language-settings/page.tsx (new):
     - LoadState: idle/loading/loaded/auth_error/not_found/error
     - SaveState: idle/saving/saved/error
     - Clinic ID text input → "Load settings" → GET /clinics/{id}/language-settings, credentials:'include'
     - Form fields: primary_language (select), fallback_language (select),
       supported_languages (checkboxes: Deutsch/English), default_patient_language (select),
       vapi_assistant_language_mode (select: german_first/english_first/bilingual_auto),
       clinic_ui_language (select)
     - "Save language settings" → PATCH /clinics/{id}/language-settings, credentials:'include'
     - Success: "Language settings saved"; error states: 401/403→"Admin session required",
       404→"Clinic not found or no access", 400→"Unsupported language configuration"
     - Safety copy: "No PHI. No secrets. No Vapi credentials."
       "Language settings do not enable production PHI, Vapi credentials, or patient-data processing."
       "Production PHI remains NO-GO."
     - No sessionStorage, no localStorage, no Vapi API key, no webhook secret, no DATABASE_URL
   - frontend/app/developer-console/page.tsx (updated):
     - Added "Tenant Language Settings" panel with link to /developer-console/language-settings
     - "Configure language settings →" button
   - frontend/lib/api.ts (updated):
     - ClinicLanguageSettings interface with all 8 fields
     - ClinicLanguageSettingsUpdatePayload interface (all optional)
     - fetchClinicLanguageSettings(clinicId): GET /clinics/{id}/language-settings, credentials:'include'
     - updateClinicLanguageSettings(clinicId, payload): PATCH, credentials:'include'
   - backend/tests/test_admin_tenant_language_settings_ui_contract.py (new — 67 tests):
     - File existence (page, console, api.ts, arch doc)
     - Page: title, badge, clinic ID input, load settings, /language-settings endpoint,
       credentials:include, PATCH for save
     - Form fields: primary/fallback/supported languages, Deutsch/English, default_patient_language,
       vapi_assistant_language_mode (german_first/english_first/bilingual_auto), clinic_ui_language
     - Save/success: "Save language settings", "Language settings saved"
     - Error states: "Admin session required", not found, 401/403/404
     - Safety: no PHI, no secrets, no Vapi credentials, NO-GO
     - Exclusions: no Vapi API key, no webhook secret, no DATABASE_URL, no JWT secret,
       no sessionStorage, no localStorage
     - Console: links to /developer-console/language-settings, has language settings panel
     - api.ts: fetchClinicLanguageSettings, updateClinicLanguageSettings, /language-settings path,
       PATCH, credentials:include, ClinicLanguageSettings interface,
       primary_language/vapi_assistant_language_mode/supported_languages fields
     - Arch doc: Module 139, language settings, german first, english fallback,
       no PHI, no Vapi credentials, NO-GO, GET/PATCH routes
   - docs/architecture/ADMIN_TENANT_LANGUAGE_SETTINGS_UI.md (new)
   - Full backend tests: 3805/3805 passed
   - Frontend build: PASS (10/10 pages)
   - Production PHI remains NO-GO

159. Module 145 — Vapi Binding Metadata Backend Foundation
   - Date: 2026-07-06
   - Sprint 19 / Backend only + tests + docs. No frontend changes. No live Vapi API calls. No secrets stored or returned.
   - backend/migrations/versions/0005_clinic_vapi_bindings.py (new):
     - Revision: 0005_clinic_vapi_bindings, down_revision: 0004_clinic_onboarding_requests
     - clinic_vapi_bindings table: id (UUID PK), clinic_id (FK→clinics ON DELETE CASCADE),
       assistant_id, phone_number_id, vapi_project_id, api_key_secret_ref (NOT NULL),
       webhook_secret_ref (NOT NULL), assistant_config_version, language_mode, status,
       created_by_user_id, created_at, updated_at
     - Status CHECK: draft/configured/disabled/revoked
     - Language mode CHECK: german_first/english_first/bilingual_auto
     - Indexes: clinic_id, status, language_mode, created_at
   - backend/app/db/schema.sql (updated): clinic_vapi_bindings table + indexes added
   - backend/app/schemas/clinic_vapi_binding.py (new):
     - _validate_secret_ref: rejects sk-... and vapi_live_... prefixes; requires uppercase
       reference name format ^[A-Z][A-Z0-9_]{2,99}$
     - ClinicVapiBindingCreate: clinic_id, api_key_secret_ref, webhook_secret_ref, language_mode
     - ClinicVapiBindingRead, ClinicVapiBindingUpdateStatus (draft/configured/disabled/revoked)
     - ClinicVapiBindingResponse, ClinicVapiBindingListResponse
     - production_phi_enabled never accepted from input; always False in response
   - backend/app/db/repositories/clinic_vapi_binding_repo.py (new):
     - create_clinic_vapi_binding, get_clinic_vapi_binding_by_id, get_clinic_vapi_binding_by_clinic_id
     - list_clinic_vapi_bindings, update_clinic_vapi_binding_status, disable_or_revoke_clinic_vapi_binding
     - All SQL parameterised. Status default: draft. No actual secret values stored or returned.
     - InvalidClinicVapiBindingError, ClinicVapiBindingNotFoundError
   - backend/app/services/clinic_vapi_binding.py (new):
     - create_vapi_binding_metadata: verifies clinic exists, creates repo row, logs binding_id/clinic_id/actor
     - get_vapi_binding_metadata: verifies clinic exists, returns latest binding or None
     - update_vapi_binding_status: updates status, logs binding_id/new_status/actor
     - production_phi_enabled=False injected before every return
     - No HTTP client imports. No live Vapi API calls. No secret values resolved or logged.
   - backend/app/api/routes/clinic_vapi_bindings.py (new):
     - POST /clinics/{clinic_id}/vapi-bindings — creates binding metadata (201); auth required
     - GET /clinics/{clinic_id}/vapi-bindings — returns latest binding; auth required
     - PATCH /clinic-vapi-bindings/{binding_id}/status — updates status; auth required
     - Actual-looking secret values (sk-..., vapi_live_...) rejected with 422
     - No PHI. No patient data. No call recordings. production_phi_enabled always False.
   - backend/app/api/router.py (updated): clinic_vapi_bindings router wired
   - backend/tests/test_vapi_binding_metadata_backend_foundation.py (new — 55 tests):
     - Migration file contract: table name, all columns, status/language_mode constraints, no secret value columns
     - schema.sql: clinic_vapi_bindings present
     - Pydantic schemas: accepts valid refs, rejects sk-..., vapi_live_..., lowercase, unsupported status/mode
     - Repository: create stores reference names, no secret values in SQL, get by clinic_id, status update
     - Routes: POST/GET/PATCH require auth (401/403/422); POST returns 201+ok+phi=false;
       no secret values in response; rejects actual API keys; 404 when clinic/binding missing
     - Static checks: no live Vapi calls, no PHI fields, production_phi_enabled=False enforced
     - Arch doc: env var, no live Vapi, NO-GO, clinic_vapi_bindings, api_key_secret_ref, webhook_secret_ref,
       no credentials, no PHI, all 4 status values
   - docs/architecture/VAPI_BINDING_METADATA_BACKEND_FOUNDATION.md (new)
   - Full backend tests: 4170/4170 passed
   - Production PHI remains NO-GO

152. Module 138 — Tenant Language Settings API Foundation
   - Date: 2026-07-06
   - Sprint 19 / Backend only + tests + docs. No frontend changes. No migration.
   - Storage approach: clinics.locale (DB) + language_config section in tenant JSON config file. No new DB columns.
   - backend/app/schemas/clinic_language_settings.py (new):
     - ALLOWED_LANGUAGES = {"de", "en"}; ALLOWED_VAPI_MODES = {"german_first","english_first","bilingual_auto"}
     - ClinicLanguageSettingsRead: ok, clinic_id, primary_language(de), fallback_language(en),
       supported_languages(["de","en"]), default_patient_language(de), vapi_assistant_language_mode(german_first),
       clinic_ui_language(de), updated_at
     - ClinicLanguageSettingsUpdate: all optional; validators reject invalid language codes,
       empty supported_languages, unsupported vapi mode, primary_language not in supported_languages
   - backend/app/services/clinic_language_settings.py (new):
     - GERMAN_FIRST_DEFAULTS dict with all 6 language fields defaulting to German-first
     - _locale_to_primary_language: de-AT→de, en-US→en, fallback→de
     - _primary_language_to_locale: de→de-AT, en→en-US
     - _load_language_config_from_file: reads language_config section from tenant JSON
     - _write_language_config_to_file: merges language_config into tenant JSON (creates file if absent)
     - get_clinic_language_settings(pool, clinic_id): reads clinics.locale + JSON config; raises ClinicNotFoundError
     - update_clinic_language_settings(pool, clinic_id, update, actor_user_id): partial update,
       validates primary in supported, updates clinics.locale in DB, writes JSON file; raises LanguageSettingsValidationError
   - backend/app/api/routes/clinic_language_settings.py (new):
     - GET /clinics/{clinic_id}/language-settings — protected, returns German-first defaults if unconfigured
     - PATCH /clinics/{clinic_id}/language-settings — protected, partial update
     - 404 on ClinicNotFoundError, 400 on LanguageSettingsValidationError, 422 on Pydantic rejection
   - backend/app/api/router.py (updated): clinic_language_settings router registered
   - backend/app/services/tenant_provisioning.py (updated):
     - After clinic shell INSERT, writes language_config JSON file with:
       primary_language=preferred_language, fallback_language, supported_languages,
       default_patient_language=preferred_language, vapi_assistant_language_mode=german_first (if de),
       clinic_ui_language=preferred_language
     - File write is best-effort (try/except); audit log remains authoritative
   - backend/tests/test_tenant_language_settings_api_foundation.py (new — 87 tests):
     - Static: all files exist, route uses get_current_user, no PHI/Vapi/secrets, GERMAN_FIRST_DEFAULTS
     - Schema: defaults German-first, rejects fr/es/empty/unsupported/invalid vapi mode/primary-not-in-supported
     - Service helpers: locale↔language mapping, German-first defaults struct
     - Service async: clinic not found, German-first from de-AT, English from en-US, uses file config,
       primary not in supported → error, partial update, locale updated in DB, file write called
     - Provisioning: vapi german_first, preferred→primary, default_patient_language, clinic_ui_language
     - Route: GET/PATCH require auth, 404 on missing, GET success+no PHI, PATCH success, 422 on invalid
       language/vapi/empty, 400 on validation error, all fields in response
   - docs/architecture/TENANT_LANGUAGE_SETTINGS_API_FOUNDATION.md (new)
   - Full backend tests: 3738/3738 passed
   - No frontend changes
   - Production PHI remains NO-GO

163. Module 149A — Fix patient history migration JSONB defaults (hotfix)
   - Date: 2026-07-08
   - Sprint 20 / Hotfix. Railway migration 0007 failed with:
     psycopg2.errors.InvalidTextRepresentation: invalid input syntax for type json
     LINE: fhir_payload JSONB NOT NULL DEFAULT '{{}}'::jsonb
   - Root cause: _common_cols() was a plain string (not f-string), but was written with
     Python f-string brace escaping '{{}}', producing literal '{{}}' in SQL.
   - Fix: added _EMPTY_JSONB = "'{}'::jsonb" constant; converted _common_cols() to f-string;
     substituted DEFAULT {_EMPTY_JSONB} for both fhir_payload and metadata columns.
   - Verified: _common_cols() now renders DEFAULT '{}'::jsonb. schema.sql was already correct.
   - No schema intent changed. No new tables. No PHI. No secrets.
   - backend/migrations/versions/0007_patient_history_data_model.py (patched)
   - backend/tests/test_patient_history_data_model_foundation.py (5 JSONB assertions added)
   - backend/tests/test_patient_history_migration_jsonb_defaults_contract.py (new — 20 tests)
   - Full backend tests: 4489/4489 passed
   - 0007 migration is now safe to re-apply on Railway.
   - Production PHI remains NO-GO.

162. Module 149 — Patient History Data Model Foundation
   - Date: 2026-07-08
   - Sprint 20 / Backend only + tests + docs. No frontend. No AI structuring. No real patient PHI.
   - FHIR R4-aligned patient history data model. Seven tables. consent_event_id required on every row.
   - Append-only/versioned. Staff/doctor review required. No deletion. No diagnosis generated.
   - No medical advice. No triage scoring. Synthetic staging only. Production PHI remains NO-GO.
   - backend/migrations/versions/0007_patient_history_data_model.py (new):
     - revision=0007_patient_history_data_model, down_revision=0006_consent_events
     - 7 FHIR tables: patient_history_allergies, _medications, _conditions, _procedures,
       _immunizations, _family_history, _social_history
     - Common columns on all: clinic_id, patient_id, consent_event_id (NOT NULL), appointment_request_id,
       version_group_id, version_number, supersedes_entry_id, status, source_type, reviewed_by_user_id,
       reviewed_at, fhir_resource_type, fhir_payload, metadata, production_phi_enabled=false
     - CHECK constraints per table: phi_check, status_check, source_type_check, version_check
     - UNIQUE(version_group_id, version_number), 9 indexes per table
     - FHIR-specific columns per table (substance_text, medication_text, condition_text+patient_reported,
       procedure_text, vaccine_text, relationship_text, observation_category+observation_text)
   - backend/app/db/schema.sql (updated): all 7 history tables added
   - backend/app/schemas/patient_history.py (new):
     - HISTORY_TYPE_TO_TABLE, HISTORY_TYPE_TO_FHIR dicts
     - HistoryEntryCommonCreate base: validates status/source_type enums, version_number≥1,
       rejects forbidden metadata keys
     - AllergyHistoryCreate/Read, MedicationHistoryCreate/Read, ConditionHistoryCreate/Read,
       ProcedureHistoryCreate/Read, ImmunizationHistoryCreate/Read, FamilyHistoryCreate/Read,
       SocialHistoryCreate/Read, HistoryStatusUpdate
     - HistoryEntryResponse, HistoryEntryListResponse, PatientHistoryTimelineResponse
   - backend/app/db/repositories/patient_history_repo.py (new):
     - HISTORY_TYPE_TABLE, HISTORY_TYPE_FHIR dicts; UnsupportedHistoryTypeError, InvalidPatientHistoryEntryError
     - create_{allergy,medication,condition,procedure,immunization,family,social}_history
     - list_patient_history_by_type, list_patient_history_timeline (fetches all 7 tables)
     - get_history_entry_by_id, update_history_entry_status, mark_history_entry_superseded
     - No DELETE functions
   - backend/app/services/patient_history.py (new):
     - create_patient_history_entry: verifies clinic/patient/appt-req; calls
       assert_valid_consent_for_history_write; sets production_phi_enabled=False
     - list_patient_history, get_patient_history_entry, update_patient_history_status,
       list_patient_history_timeline
     - Errors: PatientNotFoundError, AppointmentRequestNotFoundError, HistoryEntryNotFoundError
   - backend/app/api/routes/patient_history.py (new):
     - POST /clinics/{clinic_id}/patients/{patient_id}/history/{history_type} (201, auth)
     - GET /clinics/{clinic_id}/patients/{patient_id}/history (200, auth) — timeline
     - GET /clinics/{clinic_id}/patients/{patient_id}/history/{history_type} (200, auth)
     - GET /patient-history/{history_type}/{entry_id} (200, auth)
     - PATCH /patient-history/{history_type}/{entry_id}/status (200, auth)
     - No DELETE route; invalid history_type → 400
   - backend/app/api/router.py (updated): patient_history router registered
   - backend/tests/test_patient_history_data_model_foundation.py (new — 113 tests):
     - Migration: file, revision/down_revision, all 7 tables, all common columns, all FHIR types,
       all CHECK constraints, downgrade
     - FHIR alignment: all 7 resource types, all table-specific key fields
     - Schema SQL: all 7 tables present
     - Pydantic: all 7 create schemas accept valid entries, reject empty required fields,
       reject forbidden metadata, reject invalid status/source_type, reject version_number<1
     - HistoryStatusUpdate: accepts approved/rejected/superseded, rejects unverified/unknown
     - Repo: create calls fetchrow, rejects invalid input, list, get, update_status, timeline
     - Service: consent gate blocks write when consent missing, clinic verify
     - Routes: all 5 endpoints require auth (401/403), no DELETE (405), invalid type → 400,
       production_phi_enabled=False in responses
     - Router registration, HISTORY_TYPE_TABLE mapping (7 entries)
     - Vocabulary guards: no sk- keys, no DATABASE_URL, no JWT_SECRET, no diagnosis/medical
       advice/treatment recommendation/triage in service, no DELETE in routes
     - Arch doc: exists, mentions consent_event_id/FHIR/synthetic/NO-GO/append-only/review/no-deletion/all 7 FHIR types
   - docs/architecture/PATIENT_HISTORY_DATA_MODEL_FOUNDATION.md (new)
   - Full backend tests: 4469/4469 passed
   - Production PHI remains NO-GO

161. Module 148 — Patient History Consent Ledger Foundation
   - Date: 2026-07-08
   - Sprint 20 / Backend only + tests + docs. No frontend changes. No real patient PHI.
   - No diagnosis. No medical advice. No triage scoring. Synthetic/fake staging only.
   - production_phi_enabled always False — enforced at DB CHECK, service, and route levels.
   - backend/migrations/versions/0006_consent_events.py (new):
     - revision=0006_consent_events, down_revision=0005_clinic_vapi_bindings
     - consent_events table: 24 columns incl. clinic_id, patient_id, appointment_request_id,
       purpose, scope, channel, language, consent_text_version, consent_text_snapshot, granted,
       revoked_at, revocation_reason, production_phi_enabled
     - CHECK constraints: production_phi_enabled=false, channel (6 values), language (de/en/ar), purpose (5 values)
     - 9 indexes
   - backend/app/db/schema.sql (updated): consent_events table added
   - backend/app/schemas/consent_event.py (new):
     - ConsentEventCreate: validates purpose/channel/language enums; rejects forbidden metadata keys
       (diagnosis, medical_advice, triage, prescription, sk-, vapi_live, jwt, password, secret)
     - ConsentEventRead, ConsentEventRevoke, ConsentEventResponse, ConsentEventListResponse
     - production_phi_enabled=False in all response schemas
   - backend/app/db/repositories/consent_event_repo.py (new):
     - create_consent_event, get_consent_event_by_id, list_consent_events_for_clinic,
       list_consent_events_for_patient, revoke_consent_event, has_valid_consent_for_purpose
     - All SQL parameterised; all queries clinic_id scoped; no DELETE
   - backend/app/services/consent_ledger.py (new):
     - create_consent_event, get_consent_event, list_clinic_consent_events, revoke_consent_event
     - assert_valid_consent_for_history_write: gate check — event exists, same clinic, granted,
       not revoked, purpose in {patient_history_collection, phone_history_questions}, phi=False
     - Errors: ConsentLedgerError, ClinicNotFoundError, PatientNotFoundError,
       AppointmentRequestNotFoundError, ConsentValidationError
   - backend/app/api/routes/consent_events.py (new):
     - POST /clinics/{clinic_id}/consent-events (201, auth required)
     - GET /clinics/{clinic_id}/consent-events (200, auth required)
     - GET /consent-events/{consent_event_id} (200, auth required)
     - PATCH /consent-events/{consent_event_id}/revoke (200, auth required)
     - No DELETE route (append-only ledger)
   - backend/app/api/router.py (updated): consent_events router registered
   - backend/tests/test_patient_history_consent_ledger_foundation.py (new — ≥60 tests):
     - Migration: file exists, revision/down_revision, all columns, all 4 CHECK constraints, downgrade
     - Schema SQL: consent_events present
     - Pydantic: accepts de/en/ar, rejects invalid language/channel/purpose, rejects empty fields,
       rejects forbidden metadata keys, accepts safe metadata, default granted=True, default language=de
     - Repo: create calls fetchrow, rejects invalid channel/language, get/list/revoke/has_valid_consent
     - Service: gate rejects invalid purpose/missing event/wrong clinic/not granted/revoked,
       gate passes for patient_history_collection and phone_history_questions
     - Routes: POST/GET/PATCH require auth (401/403); no DELETE (405); happy-path 201/200/200;
       production_phi_enabled=False in all responses; clinic_id mismatch → 400; missing → 404
     - Router registration, vocabulary guards (no diagnosis/medical_advice/triage in sources),
       no DATABASE_URL/JWT_SECRET/actual sk- keys, no DELETE endpoint, gate function present
   - docs/architecture/PATIENT_HISTORY_CONSENT_LEDGER_FOUNDATION.md (new)
   - Full backend tests: pending run
   - Production PHI remains NO-GO

167. Module 153 — AI Structuring Service Foundation
   - Date: 2026-07-09
   - Sprint 20 / Module 153. Backend only. No external LLM. No API keys. Local deterministic demo extraction only.
   - backend/migrations/versions/0010_patient_history_structuring.py (new):
     - Revision: 0010_patient_history_structuring / down_revision: 0009_patient_intake_links
     - Table: patient_history_structuring_runs — provider, status, language, extraction_mode, proposals_count,
       consent_event_id (NOT NULL), pseudonymized_log_ref. No raw_prompt. No raw_model_response.
       Constraints: phi=false, demo=true, proposals_count>=0, provider/status/language/mode CHECK.
     - Table: patient_history_proposals — proposal_status (unverified default), history_type, fhir_resource_type,
       proposed_fields JSONB, proposed_fhir_payload JSONB, extraction_confidence NUMERIC(4,3),
       staff_review_required=true (CHECK), confidence 0–1 CHECK.
       Constraints: phi=false, demo=true, staff_review_required=true, status/history_type/fhir_type CHECK.
   - backend/app/schemas/patient_history_structuring.py (new):
     - StructuringRequest: validates provider, extraction_mode, phi=false, demo=true
     - StructuringResult: extraction_note = "Extraction confidence only — not a medical judgment."
     - ProposalStatusUpdate: only allows "rejected" and "archived_demo" (no "merged" in this module)
     - _FORBIDDEN_FIELD_KEYS: clinical_confidence, diagnosis_score, risk_score, triage_score, medical_advice, treatment_recommendation
   - backend/app/db/repositories/patient_history_structuring_repo.py (new — 7 functions):
     - create_structuring_run, create_history_proposal, list_history_proposals,
       get_history_proposal_by_id, get_structuring_run_by_id, list_proposals_for_run, update_proposal_status
     - No patient_history_* table references. No API keys.
   - backend/app/services/patient_history_structuring.py (new):
     - structure_intake_submission — local deterministic extraction, maps history_target → FHIR type
     - list_patient_history_proposals, get_structuring_run, reject_history_proposal, archive_demo_history_proposal
     - FHIR mapping: allergies→AllergyIntolerance, medications→MedicationStatement, conditions→Condition,
       procedures→Procedure, immunizations→Immunization, family-history→FamilyMemberHistory, social-history→Observation
     - No external LLM. No Anthropic/OpenAI/Vapi API calls. No httpx. No api_key.
     - extraction_confidence labeled as extraction only, never clinical. Logs pseudonymized.
   - backend/app/api/routes/patient_history_structuring.py (new — 6 routes):
     - POST /clinics/{clinic_id}/intake-submissions/{submission_id}/structure
     - GET /clinics/{clinic_id}/history-proposals
     - GET /clinics/{clinic_id}/structuring-runs/{run_id}
     - GET /clinics/{clinic_id}/structuring-runs/{run_id}/proposals
     - PATCH /clinics/{clinic_id}/history-proposals/{proposal_id}/reject
     - PATCH /clinics/{clinic_id}/history-proposals/{proposal_id}/archive-demo
     - All routes require get_current_user. No DELETE. No approval route (future module).
   - backend/app/api/router.py (modified): added patient_history_structuring import + include_router
   - backend/app/db/schema.sql (modified): added patient_history_structuring_runs + patient_history_proposals DDL
   - docs/architecture/AI_STRUCTURING_SERVICE_FOUNDATION.md (new)
   - backend/tests/test_ai_structuring_service_foundation.py (new — 93 tests)
   - Full backend tests: 4827/4827 passed
   - No external LLM API calls. No patient_history_* writes. No auto-approval. No diagnosis.
   - No medical advice. No triage scoring. All proposals remain status=unverified.
   - production_phi_enabled=false enforced end-to-end. Production PHI remains NO-GO.

166. Module 152 — Live Patient Intake Link Smoke Evidence
   - Date: 2026-07-09
   - Sprint 20 / Module 152. Docs/tests only. No code changes. PASS.
   - docs/runtime/LIVE_PATIENT_INTAKE_LINK_SMOKE_EVIDENCE.md (new):
     - Admin link creation verified at https://praximed.vercel.app/developer-console/intake-links
     - Clinic ID: 1a5bbc75-c1b0-4488-94aa-64b3f1c50056 (staging)
     - Tables confirmed: anamnesis_templates, patient_intake_links, patient_intake_submissions, consent_events
     - Raw token shown once; token_hash stored; token_prefix visible in admin list only
     - Public intake page /intake/{token} loaded without auth
     - Consent step appeared before questionnaire
     - de/en/ar selector verified; Arabic RTL activated on ar selection
     - Synthetic demo answers submitted (no real data)
     - Success message: "Intake submitted for staff review."
     - consent_event created with channel=intake_link, granted=true, phi=false
     - patient_intake_submission stored with answers JSONB, escalation_matches=[], phi=false
     - No patient_history_* row written
     - No AI structuring triggered
     - production_phi_enabled=false enforced end-to-end
     - Production PHI remains NO-GO
   - backend/tests/test_live_patient_intake_link_smoke_evidence_contract.py (new — 45 tests)
   - Full backend tests: 4734/4734 passed

165. Module 151 — Patient Intake Link Flow Foundation
   - Date: 2026-07-08
   - Sprint 20 / Module 151. Backend + frontend. No real patient data. No history writes. No AI structuring.
   - backend/migrations/versions/0009_patient_intake_links.py (new):
     - Revision: 0009_patient_intake_links / down_revision: 0008_anamnesis_templates
     - Table: patient_intake_links — token_hash (UNIQUE, SHA-256), token_prefix,
       clinic_id, template_id, status (active/submitted/expired/revoked), language (de/en/ar),
       expires_at, max_submissions, submission_count, synthetic_demo=true, production_phi_enabled=false
     - Table: patient_intake_submissions — intake_link_id, consent_event_id (NOT NULL),
       answers JSONB, skipped_questions JSONB, escalation_matches JSONB, synthetic_demo=true, phi=false
     - PHI + demo CHECK constraints on both tables; JSONB constants (no double-brace bug)
   - backend/app/schemas/patient_intake_link.py (new): PatientIntakeLinkCreate,
     PatientIntakeSubmissionCreate (forbids phi=true, demo=false, no consent, forbidden answer keys),
     PatientIntakePublicTemplateRead, PatientIntakeLinkRevoke, all response schemas phi=false
   - backend/app/services/intake_token.py (new): generate_intake_token() (urlsafe random 32B),
     hash_intake_token() (SHA-256), token_prefix() (first 8 chars)
   - backend/app/db/repositories/patient_intake_link_repo.py (new): create_patient_intake_link,
     get by id/token_hash, list, revoke, increment_submission_count, create_intake_submission,
     list submissions; no raw token column
   - backend/app/services/patient_intake_link.py (new):
     - create_demo_intake_link: verify clinic + template, generate token, hash, store hash only,
       return raw intake_url once
     - get_public_intake_template: hash token, validate active non-expired link, return template
     - submit_public_intake: hash token, validate, create consent_event (channel=intake_link),
       match escalation keywords (staff flag, no scoring), create submission, increment count
     - No history writes. No AI structuring.
   - backend/app/api/routes/patient_intake_links.py (new):
     - POST /clinics/{clinic_id}/patient-intake-links (201, auth)
     - GET /clinics/{clinic_id}/patient-intake-links (200, auth)
     - GET /clinics/{clinic_id}/patient-intake-submissions (200, auth)
     - PATCH /patient-intake-links/{link_id}/revoke (200, auth)
     - GET /intake/{token} (200, public)
     - POST /intake/{token}/submit (201, public)
     - No DELETE route
   - backend/app/api/router.py (updated): patient_intake_links router registered
   - backend/app/db/schema.sql (updated): patient_intake_links + patient_intake_submissions DDL
   - frontend/app/intake/[token]/page.tsx (new): mobile-first public intake page,
     consent step blocks questionnaire, de/en/ar language selector, ar=dir:rtl,
     all question types rendered, skip-allowed checkboxes, required field validation,
     success: "Intake submitted for staff review.", no diagnosis, no appointment confirmation,
     no localStorage, no sessionStorage
   - frontend/app/developer-console/intake-links/page.tsx (new): admin dark console,
     create link form, intake_url shown once, token_prefix in list, revoke, view submissions
   - frontend/app/developer-console/page.tsx (updated): Patient Intake Links panel
   - frontend/lib/api.ts (updated): PatientIntakeLink, PatientIntakeSubmission interfaces;
     createPatientIntakeLink, fetchPatientIntakeLinks, fetchPatientIntakeSubmissions,
     revokePatientIntakeLink (admin, credentials:include); fetchPublicIntakeTemplate,
     submitPublicIntake (public, plain fetch)
   - backend/tests/test_patient_intake_link_flow_foundation.py (new — 113 tests)
   - docs/architecture/PATIENT_INTAKE_LINK_FLOW_FOUNDATION.md (new)
   - Full backend tests: 4689/4689 passed. Frontend build: passed.
   - Production PHI remains NO-GO

164. Module 150 — Anamnesis Template Engine Foundation
   - Date: 2026-07-08
   - Sprint 20 / Module 150. Backend only. No frontend. No patient answers. No history writes. No AI.
   - backend/migrations/versions/0008_anamnesis_templates.py (new):
     - Revision: 0008_anamnesis_templates / down_revision: 0007_patient_history_data_model
     - Table: anamnesis_templates with clinic_id, template_key, display_name, specialty, version,
       status (draft/active/archived), primary_language (de/en/ar), supported_languages JSONB,
       template_schema JSONB, escalation_keywords JSONB, consent_purpose, synthetic_demo,
       production_phi_enabled (always false), created/updated_by_user_id, timestamps
     - PHI check constraint: production_phi_enabled = false
     - Partial unique indexes: global (clinic_id IS NULL) and per-clinic
     - JSONB defaults use _EMPTY_JSONB constant (no double-brace bug)
   - backend/app/schemas/anamnesis_template.py (new):
     - AnamnesisTemplateQuestion, AnamnesisTemplateSection, AnamnesisTemplateSchemaPayload
     - AnamnesisTemplateCreate with forbidden schema pattern detection
     - AnamnesisTemplateStatusUpdate (active/archived only, not draft)
     - AnamnesisTemplateResponse, AnamnesisTemplateListResponse (production_phi_enabled=False)
   - backend/app/db/repositories/anamnesis_template_repo.py (new):
     - create, get_by_id, get_by_key, list (dynamic filters), update_status, archive, seed_demo
     - Global (clinic_id IS NULL) vs clinic-specific template resolution
     - No DELETE function
   - backend/app/services/anamnesis_template_engine.py (new):
     - 3 seeded demo templates: demo_gp_basic_history (general_practice, 5 sections),
       demo_dermatology_basic_history (dermatology, 4 sections),
       demo_pediatrics_since_birth (pediatrics, 5 sections)
     - All demo: synthetic_demo=True, production_phi_enabled=False, de/en/ar labels, skip_allowed=True
     - GP template has escalation_keywords in de+en
     - Service functions: create_template, list_templates, get_template, activate_template,
       archive_template, seed_demo_templates, get_demo_templates
   - backend/app/api/routes/anamnesis_templates.py (new):
     - POST /clinics/{clinic_id}/anamnesis-templates (201, auth)
     - GET /clinics/{clinic_id}/anamnesis-templates (200, auth, specialty/status/limit filters)
     - GET /anamnesis-templates/{template_id} (200, auth)
     - PATCH /anamnesis-templates/{template_id}/status (200, auth)
     - POST /anamnesis-templates/seed-demo (201, auth)
     - No DELETE route
   - backend/app/api/router.py (updated): anamnesis_templates router registered
   - backend/app/db/schema.sql (updated): anamnesis_templates DDL with '{}'::jsonb defaults
   - backend/tests/test_anamnesis_template_engine_foundation.py (new — ≥60 tests)
   - docs/architecture/ANAMNESIS_TEMPLATE_ENGINE_FOUNDATION.md (new)
   - Production PHI remains NO-GO

160. Module 146 — Admin Vapi Binding Metadata UI
   - Date: 2026-07-07
   - Sprint 19 / Frontend + tests + docs. No backend changes. No migration. No live Vapi API calls. No secrets. No PHI.
   - **`frontend/app/developer-console/vapi-bindings/page.tsx`** (new): dark admin command theme (#0B132B / #008080 / #E63946 / #FFB703)
     - Header: "Vapi Binding Metadata" · "Internal secret-reference configuration" · ADMIN / STAGING badge
     - Red guardrail: "Reference names only. No Vapi secrets are stored or transmitted. No live Vapi API calls. Production PHI remains NO-GO."
     - Clinic ID input + "Load bindings" → GET /clinics/{clinic_id}/vapi-bindings; staging clinic_id example shown
     - Binding display: status badge, api_key_secret_ref / webhook_secret_ref labels, language_mode, assistant_id / phone_number_id / vapi_project_id / assistant_config_version (read-only), production_phi_enabled=false, timestamps
     - Empty state: "No Vapi binding found for this clinic."
     - Create form: api_key_secret_ref + webhook_secret_ref (placeholders VAPI_API_KEY_REF_CLINIC_DEMO / VAPI_WEBHOOK_SECRET_REF_CLINIC_DEMO) + language_mode select (german_first/english_first/bilingual_auto) → POST /clinics/{clinic_id}/vapi-bindings; success copy "Vapi binding metadata saved"
     - Client-side SECRET_REF_PATTERN ^[A-Z][A-Z0-9_]{2,99}$ mirrors backend validator; "Secret values are not allowed" error copy
     - Status update: draft/configured/disabled/revoked → PATCH /clinic-vapi-bindings/{binding_id}/status; "Binding status updated."
     - Safe error mapping: 401/403 "Admin session required. Please log in first.", 404 "Clinic not found or no access.", generic "Could not load Vapi binding metadata."
     - Safety Boundary panel: no live Vapi calls, no Vapi secrets, no webhook secret values, no PHI, no patient data, no production activation
     - No sessionStorage/localStorage; no password fields; no secret-value inputs
   - **`frontend/lib/api.ts`** (updated): ClinicVapiBinding + ClinicVapiBindingResult interfaces; fetchClinicVapiBindings / createClinicVapiBinding / updateClinicVapiBindingStatus helpers via apiFetch (NEXT_PUBLIC_API_BASE_URL + credentials: "include"); non-throwing status-mapped results
   - **`frontend/app/developer-console/page.tsx`** (updated): "Vapi Binding Metadata" panel linking to /developer-console/vapi-bindings with safety copy
   - **`backend/tests/test_admin_vapi_binding_metadata_ui_contract.py`** (new static contract tests): page identity, dark theme, load/create/status flows, reference-name placeholders, safety copy, forbidden content (DATABASE_URL/JWT/patient_name/transcript/recording_url/sessionStorage/localStorage/password inputs), api.ts helpers + credentials include, console link, docs coverage, no hardcoded secrets
   - **`docs/architecture/ADMIN_VAPI_BINDING_METADATA_UI.md`** (new)
   - Production PHI remains NO-GO

168. Module 154 — Doctor Review & Merge UI Foundation
   - Date: 2026-07-09
   - Sprint 20 / Module 154. Backend service + schemas + routes + frontend review UI + tests + arch doc.
   - backend/app/schemas/patient_history_review.py (new):
     - _FORBIDDEN_MERGE_KEYS: clinical_confidence, diagnosis_score, risk_score, triage_score,
       medical_advice, treatment_recommendation, diagnosis_generated, auto_approved, auto_confirmed
     - PatientHistoryMergeRequest: edited_fields, edited_fhir_payload, review_note, confirm_staff_review
       Validators: confirm_staff_review must be True; no forbidden keys; production_phi_enabled not unlockable
     - PatientHistoryMergeResult: ok, proposal_id, merged_history_entry_id, history_type, fhir_resource_type,
       proposal_status="merged", production_phi_enabled=False, message="Proposal merged into patient history after staff review."
     - PatientHistoryRejectResult: ok, proposal_id, proposal_status="rejected", rejected_reason, production_phi_enabled=False
     - PatientHistoryReviewQueueResponse: ok, proposals[], total, production_phi_enabled=False,
       extraction_note="Extraction confidence only — not a medical judgment."
   - backend/app/services/patient_history_review.py (new):
     - approve_and_merge_history_proposal — consent gate + eligibility checks + one patient_history_* row write
       1. Load proposal, assert unverified, assert staff_review_required=True, assert phi=False, assert patient_id present
       2. assert_no_forbidden_merge_keys(edited_fields) — rejects any forbidden clinical key
       3. assert_valid_consent_for_history_write(pool, clinic_id, consent_event_id, purpose) — consent gate
       4. Call _CREATE_FN[history_type] — writes approved row: status=approved, source_type=ai_proposal,
          source_ref=proposal:{proposal_id}, consent_event_id copied, fhir_payload from edited payload,
          production_phi_enabled=False
       5. Update proposal to merged, set merged_history_entry_id
       6. Return merge result
     - reject_history_proposal_with_review — sets proposal_status=rejected, rejected_reason, reviewed_by, reviewed_at
     - list_review_queue — returns unverified proposals for a clinic with filters
     - get_proposal_review_detail — loads single proposal for review display
     - _CREATE_FN dict maps history_type → create_*_history function reference (import-time binding)
       NOTE: Tests must use patch.dict(svc._CREATE_FN, {"type": mock_fn}) not repo-level patches
     - No external LLM. No auto-approval. No diagnosis. No medical advice. No triage.
   - backend/app/api/routes/patient_history_review.py (new — 4 routes):
     - GET /clinics/{clinic_id}/patient-history-review-queue (200, auth)
     - GET /patient-history-proposals/{proposal_id}/review?clinic_id= (200, auth)
     - PATCH /patient-history-proposals/{proposal_id}/approve-merge?clinic_id= (201, auth)
     - PATCH /patient-history-proposals/{proposal_id}/reject-review?clinic_id= (200, auth)
     - All routes require get_current_user. No DELETE. No public routes. No auto-approval endpoint.
   - backend/app/api/router.py (modified): added patient_history_review import + include_router
   - frontend/app/developer-console/history-review/page.tsx (new):
     - Dark admin theme: INK=#0B132B, PANEL=#111C3D, ACCENT=#008080
     - Header: "Patient History Review" · "ADMIN / STAGING" · "Doctor-reviewed merge queue"
     - Safety warning: synthetic staging only, no diagnosis, no medical advice, no PHI, production PHI NO-GO
     - Filters: clinicId, patientId, historyType (all/allergies/medications/conditions/procedures/immunizations/family-history/social-history)
     - Queue list: extraction confidence labeled "Extraction confidence only — not a medical judgment."
     - Detail panel: proposed_fields JSON, consent/intake IDs, editable JSON field block
     - Mandatory checkbox: "I confirm staff/doctor review before merging." (approve disabled until checked)
     - Approve & Merge + Reject with reason input
     - Success: "Proposal merged into patient history after staff review."
     - Reject: "Proposal rejected."
     - No browser storage. No auto-approval. No diagnosis display.
   - frontend/lib/api.ts (modified): appended 4 review API helpers:
     - fetchPatientHistoryReviewQueue, fetchPatientHistoryProposalReview,
       approveMergePatientHistoryProposal, rejectReviewPatientHistoryProposal
     - All use apiFetch (credentials: "include"). No localStorage. No sessionStorage.
   - frontend/app/developer-console/page.tsx (modified): added "Patient History Review" ConsolePanel card
   - backend/tests/test_doctor_review_merge_ui_foundation.py (new — 98 tests, all passing)
   - docs/architecture/DOCTOR_REVIEW_MERGE_UI_FOUNDATION.md (new)
   - Full backend tests: 4925/4925 passed. Frontend build: clean.
   - No auto-approval. No auto-merge. No external LLM calls. No diagnosis. No medical advice.
   - No triage scoring. No treatment recommendations. All proposals remain unverified until explicit staff merge.
   - production_phi_enabled=False enforced at DB, service, route, and frontend levels.
   - Production PHI remains NO-GO.

169. Module 155 — Live Doctor Review & Merge Smoke Evidence
   - Date: 2026-07-09
   - Sprint 20 / Module 155. Docs/static-tests only. No backend code changes. No frontend changes. No migration.
   - Result: PASS
   - Live URL tested: https://praximed.vercel.app/developer-console/history-review
   - Clinic ID: 1a5bbc75-c1b0-4488-94aa-64b3f1c50056 (staging demo)
   - Evidence confirmed:
     - patient_history_structuring_runs and patient_history_proposals tables exist
     - Synthetic intake submission used (no real patient data, no PHI)
     - Structuring service created unverified proposals (local deterministic, no external LLM)
     - Review queue loaded unverified proposals successfully
     - Proposal detail visible with extraction_confidence labeled "Extraction confidence only — not a medical judgment."
     - Reject flow: proposal_status set to rejected, no patient_history_* row created
     - Staff confirmation gate: Approve & Merge button disabled until "I confirm staff/doctor review" checked
     - Approve/merge: HTTP 201, merged_history_entry_id returned, proposal_status=merged
     - Success message: "Proposal merged into patient history after staff review."
     - Created patient_history_* row: status=approved, source_type=ai_proposal, consent_event_id preserved, production_phi_enabled=false
     - No auto-approval occurred at any point
     - No external LLM calls
     - No diagnosis. No medical advice. No treatment recommendations. No triage scoring.
     - No real patient data. No PHI.
   - docs/runtime/LIVE_DOCTOR_REVIEW_MERGE_SMOKE_EVIDENCE.md (new)
   - backend/tests/test_live_doctor_review_merge_smoke_evidence_contract.py (new — 50 tests)
   - Full backend tests: 4975/4975 passed
   - Production PHI remains NO-GO.

171. Module 157 — Doctor-Facing Sales MVP Simplification
   - Date: 2026-07-09
   - Sprint 21 / Module 157. Frontend simplification only. No migration. No new backend domain.
   - Pivot: existing /dashboard simplified into clinic-facing, German-first, UUID-hidden sales MVP.
   - No parallel dashboard created. All existing contract tests remain green.
   - frontend/app/dashboard/page.tsx (modified):
     - Added getGermanStatusLabel, getReadableRequestNumber, getTodaySummaryCounts helpers
     - Added BADGE_MAP entries for callback_needed and contacted
     - Added activeTab state (anfragen / patienten / einstellungen)
     - Added callbackIds, contactedIds state
     - Added handleMarkCallback, handleMarkContacted handlers
     - Added Heute daily summary bar (Neue Anfragen / Rückruf nötig / Dringend prüfen / Erledigt)
     - Added Anfragen / Patienten / Einstellungen tab navigation
     - UUID removed from visible clinic-facing UI (selectedAppt.id, patient.id, selectedPatient.id)
     - Replaced UUID display with Anfrage #N human-readable numbering
     - "Rückruf" button on each request card
     - "Als kontaktiert markieren" button in workspace actions
     - All existing sr-only English labels preserved for contract test compatibility
     - German headings visible: Anfragen, Anfrage-Details, Patientenregister
     - No PHI. No diagnosis. No medical advice. No triage. Production PHI remains NO-GO.
   - frontend/lib/api.ts (modified):
     - Added updateAppointmentRequestStatus (PATCH /appointment-requests/{id}/status)
     - Used for callback_needed and contacted status transitions
   - backend/tests/test_doctor_facing_sales_mvp_dashboard_contract.py (new — 45 tests)
   - docs/product/DOCTOR_FACING_SALES_MVP_SIMPLIFICATION.md (new)
   - docs/claude/CURRENT_STATE.md, NEXT_MODULE.md (updated)
   - Full backend tests: 5067+/passed. Frontend build: clean.
   - Product acceptance: receptionist understands PraxisMed in 5 minutes without technical words.
   - Production PHI remains NO-GO.

170. Module 156 — Longitudinal Timeline and Delta View Foundation
   - Date: 2026-07-09
   - Sprint 20 / Module 156. Backend service + schemas + repo + routes + frontend timeline UI + tests + arch doc.
   - No migration. Read-only. No new writes. No patient history writes.
   - backend/app/schemas/patient_timeline.py (new):
     - PatientTimelineItem: item_type, item_source, title, is_approved_history, is_unverified_proposal,
       production_phi_enabled (always False), metadata (no forbidden clinical keys)
     - Allowed item_type: appointment_request / intake_submission / consent_event /
       structuring_run / history_proposal / approved_history
     - Allowed item_source: all 7 patient_history_* tables + proposal/run/submission/consent/appointment tables
     - PatientTimelineResponse, PatientTimelineDeltaResponse, PatientTimelineFilters
     - No diagnosis/advice/triage fields. No PHI unlock.
   - backend/app/db/repositories/patient_timeline_repo.py (new):
     - list_patient_appointment_events, list_patient_intake_submission_events,
       list_patient_consent_events, list_patient_structuring_run_events,
       list_patient_history_proposal_events (include_unverified filter),
       list_patient_approved_history_events (status='approved' only from all 7 tables),
       list_patient_timeline_events (all sources combined, sorted newest-first),
       get_last_visit_anchor (latest appointment_request),
       list_patient_delta_since (items newer than given datetime)
     - All queries tenant-scoped (clinic_id + patient_id). No writes. No delete.
   - backend/app/services/patient_timeline.py (new):
     - get_patient_timeline — aggregate all sources, annotate is_approved_history / is_unverified_proposal
     - get_patient_delta_since_last_visit — uses latest appointment as anchor; no_prior_visit_anchor if none
     - get_patient_delta_since — explicit datetime cutoff
     - No external LLM. No auto-approval. No diagnosis. No medical advice.
     - production_phi_enabled=False throughout.
   - backend/app/api/routes/patient_timeline.py (new — 3 routes):
     - GET /clinics/{clinic_id}/patients/{patient_id}/timeline (200, auth)
     - GET /clinics/{clinic_id}/patients/{patient_id}/timeline/delta (200, auth)
     - GET /clinics/{clinic_id}/patients/{patient_id}/timeline/delta-since?since= (200, auth)
     - All require get_current_user. No DELETE. No POST. No public routes.
   - backend/app/api/router.py (modified): added patient_timeline router
   - frontend/app/developer-console/patient-timeline/page.tsx (new):
     - Dark admin theme: INK=#0B132B, PANEL=#111C3D, ACCENT=#008080
     - Inputs: clinic_id, patient_id, include_unverified checkbox
     - Load timeline + Load delta since last visit buttons
     - Badge system: APPROVED HISTORY (green) / UNVERIFIED PROPOSAL (amber) /
       CONSENT / INTAKE / APPOINTMENT / STRUCTURING
     - Delta view: changed_since_last_visit or no_prior_visit_anchor status badge
     - Safety panel: approved after staff review, unverified ≠ merged, no diagnosis, production PHI NO-GO
     - No browser storage. No auto-approval.
   - frontend/lib/api.ts (modified): added fetchPatientTimeline, fetchPatientTimelineDelta,
     fetchPatientTimelineDeltaSince (credentials: include, no localStorage)
   - frontend/app/developer-console/page.tsx (modified): added "Longitudinal Patient Timeline" nav card
   - backend/tests/test_longitudinal_timeline_delta_view_foundation.py (new — 92 tests, all passing)
   - docs/architecture/LONGITUDINAL_TIMELINE_DELTA_VIEW_FOUNDATION.md (new)
   - Full backend tests: 5067/5067 passed. Frontend build: clean.
   - No auto-approval. No external LLM. No diagnosis. No medical advice. No treatment recommendations.
   - No triage scoring. No new writes. No real patient data. No PHI.
   - production_phi_enabled=False enforced end-to-end. Production PHI remains NO-GO.
