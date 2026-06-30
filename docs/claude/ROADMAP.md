# PraxisMed — Roadmap

## Milestone 1 — Scheduling & Availability Core
Status: mostly complete.

Completed:
- Config loader
- DB pool
- Schema contract
- Calendar repository
- Availability engine
- Calendar sync service
- n8n calendar sync webhook
- Availability API routes

Purpose:
The backend can know whether a clinic slot is available before Vapi or WhatsApp offers it.

## Milestone 2 — Vapi Phone Agent Backend
Status: mostly complete.

Completed:
- Vapi prompt builder
- Vapi availability tool routes
- Vapi call event webhook
- Vapi call logs

Purpose:
The phone agent can ask PraxisMed before offering appointment times and can send call events/transcripts to the backend.

## Milestone 3 — Appointment Request System
Next.

Modules:
- Module 15: Appointment request schema
- Module 16: Appointment request repository
- Module 17: Appointment request API schemas/routes
- Module 18: Vapi appointment capture integration

Purpose:
Convert AI phone calls into structured appointment requests for clinic staff.

## Milestone 4 — Notification Engine
Later.

Modules:
- notification schema/repository
- notification router
- fake SMS/push adapters first
- real SMS/push later

## Milestone 5 — Doctor Documentation Assistant
Later.

Modules:
- patient schema/repository
- consultation session schema/repository
- audio upload
- transcription adapter
- summary generator
- doctor approve/save flow

## Milestone 6 — Reports & Exports
Later.

Modules:
- PDF export
- Excel export
- patient timeline report

## Milestone 7 — WhatsApp Intake
Later, after phone flow is stable.

## Milestone 8 — Frontend MVP
Later.

Pages:
- receptionist inbox
- calls
- appointment requests
- calendar
- patients
- consultation notes
- settings

## Milestone 9 — Auth, Tenant Isolation & Security
Later.

Includes:
- login
- roles
- tenant isolation tests
- audit log service
- consent and retention rules

## Milestone 10 — Real Integrations
Later.

Includes:
- local PostgreSQL Docker setup
- real n8n calendar sync workflow
- real Vapi assistant
- tunnel testing
- real SMS/push only later

## MVP Definition
AI phone receptionist
+ availability checking
+ appointment request capture
+ consultation recording
+ AI draft summary
+ doctor approval
+ PDF export
