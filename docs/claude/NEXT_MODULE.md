# Sprint 6 / Module 54 — Provider Machine Header Compatibility Config

Task scope:
Create controlled provider-specific machine auth header compatibility configuration and apply it to machine auth dependencies.

Purpose:
Module 53 made webhook signature headers compatible with provider-specific aliases. The next real-integration risk is machine auth headers. Current local backend requires X-Service-Name, X-Service-Clinic-Id, X-Service-Scopes, but real Vapi/n8n may use different header names. This module adds a controlled compatibility layer for machine auth headers.

Files created/updated:
- backend/app/core/machine_provider_config.py (new)
- backend/app/api/dependencies/machine_auth.py (updated)
- backend/tests/test_machine_provider_config.py (new)
- backend/tests/test_machine_auth_dependencies.py (updated)
- docs/integrations/EXTERNAL_INTEGRATION_COMPATIBILITY_PLAN.md (updated)

Commit message:
Sprint 6 / Module 54 — Provider machine header compatibility config
