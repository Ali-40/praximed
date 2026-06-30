"""
Central API router — PraxisMed

All route modules are imported and included here so that main.py has a
single registration point.  Future Vapi and WhatsApp routers will be
added to this file.
"""

from __future__ import annotations

from fastapi import APIRouter

from backend.app.api.routes import health
from backend.app.api.routes import calendar_webhooks
from backend.app.api.routes import availability
from backend.app.api.routes import vapi_tools
from backend.app.api.routes import vapi_webhooks

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(calendar_webhooks.router, prefix="/webhooks")
api_router.include_router(availability.router)
api_router.include_router(vapi_tools.router)
api_router.include_router(vapi_webhooks.router, prefix="/webhooks")
