"""
Notification API routes — PraxisMed Sprint 1 / Module 23

Exposes five endpoints under /notifications for creating, listing, fetching,
marking as read, and cancelling internal clinic notification records.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.app.api.deps import get_db_pool
from backend.app.db.repositories import notification_repo
from backend.app.db.repositories.notification_repo import InvalidNotificationError
from backend.app.schemas.notifications import (
    NotificationCreate,
    NotificationListResponse,
    NotificationResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("", response_model=NotificationResponse)
async def create_notification(
    body: NotificationCreate,
    pool: Any = Depends(get_db_pool),
) -> NotificationResponse:
    try:
        row = await notification_repo.create_notification(
            pool=pool,
            clinic_id=body.clinic_id,
            channel=body.channel,
            notification_type=body.notification_type,
            title=body.title,
            message=body.message,
            priority=body.priority,
            recipient_user_id=body.recipient_user_id,
            related_resource_type=body.related_resource_type,
            related_resource_id=body.related_resource_id,
            scheduled_for=body.scheduled_for,
            raw_payload=body.raw_payload,
        )
    except InvalidNotificationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error creating notification")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    return NotificationResponse(ok=True, notification=row)


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    clinic_id: str = Query(...),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    notification_type: Optional[str] = Query(None),
    recipient_user_id: Optional[str] = Query(None),
    limit: int = Query(50),
    pool: Any = Depends(get_db_pool),
) -> NotificationListResponse:
    try:
        rows = await notification_repo.list_notifications(
            pool=pool,
            clinic_id=clinic_id,
            status=status,
            priority=priority,
            notification_type=notification_type,
            recipient_user_id=recipient_user_id,
            limit=limit,
        )
    except InvalidNotificationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error listing notifications")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    return NotificationListResponse(ok=True, notifications=rows)


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: str,
    clinic_id: str = Query(...),
    pool: Any = Depends(get_db_pool),
) -> NotificationResponse:
    try:
        row = await notification_repo.get_notification_by_id(
            pool=pool,
            clinic_id=clinic_id,
            notification_id=notification_id,
        )
    except InvalidNotificationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error fetching notification")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    if row is None:
        raise HTTPException(status_code=404, detail="Notification not found")

    return NotificationResponse(ok=True, notification=row)


@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: str,
    clinic_id: str = Query(...),
    pool: Any = Depends(get_db_pool),
) -> NotificationResponse:
    try:
        row = await notification_repo.mark_notification_read(
            pool=pool,
            clinic_id=clinic_id,
            notification_id=notification_id,
        )
    except InvalidNotificationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error marking notification read")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    if row is None:
        raise HTTPException(status_code=404, detail="Notification not found")

    return NotificationResponse(ok=True, notification=row)


@router.post("/{notification_id}/cancel", response_model=NotificationResponse)
async def cancel_notification(
    notification_id: str,
    clinic_id: str = Query(...),
    pool: Any = Depends(get_db_pool),
) -> NotificationResponse:
    try:
        row = await notification_repo.cancel_notification(
            pool=pool,
            clinic_id=clinic_id,
            notification_id=notification_id,
        )
    except InvalidNotificationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error cancelling notification")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")

    if row is None:
        raise HTTPException(status_code=404, detail="Notification not found")

    return NotificationResponse(ok=True, notification=row)
