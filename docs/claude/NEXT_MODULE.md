# Sprint 5 / Module 46 — Webhook Signature Verification Foundation

Task scope:
Create a shared webhook signature verification foundation.

Purpose:
PraxisMed currently protects machine routes with internal X-Service-* headers. This module creates
reusable HMAC-based webhook signature verification helpers and FastAPI dependencies.

Route-by-route enforcement will be Module 47.

Files created:
- backend/app/core/webhook_signature.py
- backend/app/api/dependencies/webhook_signature.py
- backend/tests/test_webhook_signature.py
- backend/tests/test_webhook_signature_dependencies.py

Commit message:
Sprint 5 / Module 46 — Webhook signature verification foundation
