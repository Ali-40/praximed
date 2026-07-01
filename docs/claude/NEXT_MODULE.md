# Sprint 6 / Module 53 — Provider Header Compatibility Config

Task scope:
Create provider-specific webhook header compatibility configuration and apply it to webhook signature dependencies.

Purpose:
Module 52 identified that real Vapi/n8n may not use exactly our local signature header names. Current local convention works with X-Vapi-Signature and X-N8N-Signature, but before real dashboard setup we need a controlled way to accept provider-specific header aliases without weakening HMAC verification.

Files created/updated:
- backend/app/core/webhook_provider_config.py (new)
- backend/app/api/dependencies/webhook_signature.py (updated)
- backend/tests/test_webhook_provider_config.py (new)
- backend/tests/test_webhook_signature_dependencies.py (updated)
- docs/integrations/EXTERNAL_INTEGRATION_COMPATIBILITY_PLAN.md (updated)

Commit message:
Sprint 6 / Module 53 — Provider header compatibility config
