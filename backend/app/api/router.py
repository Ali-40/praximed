"""
Central API router — PraxisMed Sprint 1 / Module 7

All route modules are imported and included here so that main.py has a
single registration point.  Future webhook, Vapi, and WhatsApp routers
will be added to this file.
"""

from __future__ import annotations

from fastapi import APIRouter

from backend.app.api.routes import health

api_router = APIRouter()

api_router.include_router(health.router)
