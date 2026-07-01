# Sprint 5 / Module 47 — Apply Webhook Signature Enforcement to Existing Routes

Task scope:
Apply the webhook signature verification dependencies from Module 46 to existing Vapi and n8n webhook routes.

Purpose:
PraxisMed already protects integration routes with MachineAuthContext. Module 46 added HMAC-based webhook signature verification. This module wires signature verification into real webhook routes so external webhook calls require both:

1. valid machine access headers
2. valid provider-specific webhook signature

Routes protected in this module:

1. POST /webhooks/vapi/call-event
2. POST /webhooks/n8n/calendar-sync

Files created/updated:
- backend/app/api/routes/vapi_webhooks.py
- backend/app/api/routes/calendar_webhooks.py
- backend/tests/test_vapi_webhook_route.py
- backend/tests/test_calendar_webhook_route.py

Commit message:
Sprint 5 / Module 47 — Apply webhook signature enforcement
