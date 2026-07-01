# Sprint 5 / Module 50 — Local Seed Data and Real Webhook Smoke Fixtures

Task scope:
Create local seed data and valid UUID smoke-test fixtures for local integration testing.

Purpose:
Local signed webhook testing reaches real DB logic, but payloads using fake IDs like "clinic-1" fail because PostgreSQL expects UUIDs. This module adds a seed script, UUID payload fixtures, and updated runbook.

Files created/updated:
- backend/scripts/seed_local_data.py (new)
- docs/integrations/local_payloads/vapi_call_event.json (new)
- docs/integrations/local_payloads/n8n_calendar_sync.json (new)
- docs/integrations/LOCAL_INTEGRATION_RUNBOOK.md (updated)
- backend/tests/test_local_seed_contract.py (new)

Commit message:
Sprint 5 / Module 50 — Local seed data and webhook smoke fixtures
