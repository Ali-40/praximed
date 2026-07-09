"""
Central API router — PraxisMed

All route modules are imported and included here so that main.py has a
single registration point.  Future Vapi and WhatsApp routers will be
added to this file.
"""

from __future__ import annotations

from fastapi import APIRouter

from backend.app.api.routes import auth
from backend.app.api.routes import health
from backend.app.api.routes import calendar_webhooks
from backend.app.api.routes import availability
from backend.app.api.routes import vapi_tools
from backend.app.api.routes import vapi_webhooks
from backend.app.api.routes import appointment_requests
from backend.app.api.routes import notifications
from backend.app.api.routes import patients
from backend.app.api.routes import consultations
from backend.app.api.routes import clinical_workflows
from backend.app.api.routes import clinic_onboarding
from backend.app.api.routes import clinic_language_settings
from backend.app.api.routes import vapi_assistant_config
from backend.app.api.routes import clinic_vapi_bindings
from backend.app.api.routes import consent_events
from backend.app.api.routes import patient_history
from backend.app.api.routes import anamnesis_templates
from backend.app.api.routes import patient_intake_links
from backend.app.api.routes import patient_history_structuring
from backend.app.api.routes import patient_history_review
from backend.app.api.routes import patient_timeline

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(health.router)
api_router.include_router(calendar_webhooks.router, prefix="/webhooks")
api_router.include_router(availability.router)
api_router.include_router(vapi_tools.router)
api_router.include_router(vapi_webhooks.router, prefix="/webhooks")
api_router.include_router(appointment_requests.router)
api_router.include_router(notifications.router)
api_router.include_router(patients.router)
api_router.include_router(consultations.router)
api_router.include_router(clinical_workflows.router)
api_router.include_router(clinic_onboarding.router)
api_router.include_router(clinic_language_settings.router)
api_router.include_router(vapi_assistant_config.router)
api_router.include_router(clinic_vapi_bindings.router)
api_router.include_router(consent_events.router)
api_router.include_router(patient_history.router)
api_router.include_router(anamnesis_templates.router)
api_router.include_router(patient_intake_links.router)
api_router.include_router(patient_history_structuring.router)
api_router.include_router(patient_history_review.router)
api_router.include_router(patient_timeline.router)
