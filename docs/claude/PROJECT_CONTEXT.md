# PraxisMed — Claude Code Project Context

## Product
PraxisMed is a multi-tenant AI automation web application for private medical clinics in Austria.

Parent agency/brand: LiX.

Core product goal:
- AI phone receptionist
- appointment availability checking
- appointment request capture
- calendar sync safety
- doctor documentation assistant later
- consultation transcription and doctor-approved summaries later

## Stack
Backend:
- Python
- FastAPI
- asyncpg
- PostgreSQL
- Pydantic
- pytest

Frontend later:
- Next.js mobile-first responsive web app

Automation/integrations later:
- n8n for calendar sync workflows
- Vapi for AI phone agent
- WhatsApp later

## Architecture Rules
- Build one focused module at a time unless modules are tiny and tightly related.
- Never create massive all-in-one files.
- Keep files modular and testable.
- Unit tests must not use a real database.
- Mock external services.
- Do not build frontend unless explicitly requested.
- Do not build WhatsApp unless explicitly requested.
- Do not create real Vapi API calls unless explicitly requested.
- Do not add authentication until the roadmap reaches auth/security.
- Do not modify completed modules unless absolutely required by imports/tests.
- Every module must include tests.
- Run module tests first, then all backend tests.
- Commit only after all tests pass.

## Security Rules
- No patient diagnosis logic.
- No treatment advice.
- AI may draft or summarize; human/doctor stays in control.
- Patient-facing tools must not promise appointments before checking availability.
- Calendar availability must be checked before offering slots.
- Keep tenant separation through `clinic_id`.
- Do not store secrets inside tenant config JSON files.

## Current Project Folder
/Users/aliabdeltawab/Documents/praximed
