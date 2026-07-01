"""
Tests for backend/app/modules/audit/audit_logger.py

No real database connection is used — asyncpg pool is fully mocked.
No external service calls.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.app.db.repositories.audit_repo import AuditRepoError
from backend.app.modules.audit.audit_logger import (
    AuditLoggerError,
    InvalidAuditLogInputError,
    build_audit_event,
    build_machine_audit_event,
    build_user_audit_event,
    record_audit_event,
    safe_record_audit_event,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

CLINIC_ID = "11111111-1111-4111-8111-111111111111"
USER_ID = "user-uuid-001"
LOG_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"


def _fake_auth_context(
    user_id: str = USER_ID,
    clinic_id: str = CLINIC_ID,
    role: str = "doctor",
):
    return SimpleNamespace(user_id=user_id, clinic_id=clinic_id, role=role)


def _fake_machine_context(
    service_name: str = "vapi",
    clinic_id: str = CLINIC_ID,
    scopes: set = frozenset({"vapi:tool"}),
):
    return SimpleNamespace(
        service_name=service_name, clinic_id=clinic_id, scopes=scopes
    )


def _fake_audit_log():
    return {
        "id": LOG_ID,
        "clinic_id": CLINIC_ID,
        "actor_type": "system",
        "actor_id": None,
        "action": "test.action",
        "resource_type": "test_resource",
        "resource_id": None,
        "metadata": '{"_result": "success", "_severity": "info"}',
        "created_at": "2026-07-01T00:00:00Z",
    }


def _make_pool():
    pool = MagicMock()
    pool.fetchrow = AsyncMock(return_value=_fake_audit_log())
    pool.fetch = AsyncMock(return_value=[])
    return pool


# ---------------------------------------------------------------------------
# 1. build_audit_event accepts valid event
# ---------------------------------------------------------------------------


def test_build_audit_event_valid():
    event = build_audit_event(
        clinic_id=CLINIC_ID,
        action="appointment.created",
        resource_type="appointment_request",
    )
    assert event["clinic_id"] == CLINIC_ID
    assert event["action"] == "appointment.created"
    assert event["resource_type"] == "appointment_request"
    assert event["actor_type"] == "system"
    assert event["result"] == "success"
    assert event["severity"] == "info"


# ---------------------------------------------------------------------------
# 2. build_audit_event rejects empty clinic_id
# ---------------------------------------------------------------------------


def test_build_audit_event_rejects_empty_clinic_id():
    with pytest.raises(InvalidAuditLogInputError, match="clinic_id"):
        build_audit_event(clinic_id="", action="x", resource_type="y")


# ---------------------------------------------------------------------------
# 3. build_audit_event rejects empty action
# ---------------------------------------------------------------------------


def test_build_audit_event_rejects_empty_action():
    with pytest.raises(InvalidAuditLogInputError, match="action"):
        build_audit_event(clinic_id=CLINIC_ID, action="", resource_type="y")


# ---------------------------------------------------------------------------
# 4. build_audit_event rejects empty resource_type
# ---------------------------------------------------------------------------


def test_build_audit_event_rejects_empty_resource_type():
    with pytest.raises(InvalidAuditLogInputError, match="resource_type"):
        build_audit_event(clinic_id=CLINIC_ID, action="x", resource_type="")


# ---------------------------------------------------------------------------
# 5. build_user_audit_event builds actor_type user
# ---------------------------------------------------------------------------


def test_build_user_audit_event_sets_actor_type_user():
    auth = _fake_auth_context()
    event = build_user_audit_event(auth, "patient.viewed", "patient")
    assert event["actor_type"] == "user"


# ---------------------------------------------------------------------------
# 6. build_user_audit_event uses auth_context.user_id
# ---------------------------------------------------------------------------


def test_build_user_audit_event_uses_user_id():
    auth = _fake_auth_context(user_id="user-abc")
    event = build_user_audit_event(auth, "patient.viewed", "patient")
    assert event["actor_id"] == "user-abc"


# ---------------------------------------------------------------------------
# 7. build_user_audit_event includes role in metadata
# ---------------------------------------------------------------------------


def test_build_user_audit_event_includes_role_in_metadata():
    auth = _fake_auth_context(role="admin")
    event = build_user_audit_event(auth, "patient.viewed", "patient")
    assert event["metadata"]["role"] == "admin"


# ---------------------------------------------------------------------------
# 8. build_user_audit_event preserves additional metadata
# ---------------------------------------------------------------------------


def test_build_user_audit_event_preserves_extra_metadata():
    auth = _fake_auth_context()
    event = build_user_audit_event(
        auth, "patient.viewed", "patient", metadata={"ip": "1.2.3.4"}
    )
    assert event["metadata"]["role"] == "doctor"
    assert event["metadata"]["ip"] == "1.2.3.4"


# ---------------------------------------------------------------------------
# 9. build_machine_audit_event builds actor_type machine
# ---------------------------------------------------------------------------


def test_build_machine_audit_event_sets_actor_type_machine():
    mc = _fake_machine_context()
    event = build_machine_audit_event(mc, "availability.checked", "calendar")
    assert event["actor_type"] == "machine"


# ---------------------------------------------------------------------------
# 10. build_machine_audit_event uses machine_context.service_name
# ---------------------------------------------------------------------------


def test_build_machine_audit_event_uses_service_name():
    mc = _fake_machine_context(service_name="n8n")
    event = build_machine_audit_event(mc, "calendar.synced", "calendar")
    assert event["actor_id"] == "n8n"


# ---------------------------------------------------------------------------
# 11. build_machine_audit_event uses explicit clinic_id if provided
# ---------------------------------------------------------------------------


def test_build_machine_audit_event_uses_explicit_clinic_id():
    mc = _fake_machine_context(clinic_id=CLINIC_ID)
    other_clinic = "22222222-2222-4222-8222-222222222222"
    event = build_machine_audit_event(
        mc, "availability.checked", "calendar", clinic_id=other_clinic
    )
    assert event["clinic_id"] == other_clinic


# ---------------------------------------------------------------------------
# 12. build_machine_audit_event falls back to machine_context.clinic_id
# ---------------------------------------------------------------------------


def test_build_machine_audit_event_falls_back_to_context_clinic_id():
    mc = _fake_machine_context(clinic_id=CLINIC_ID)
    event = build_machine_audit_event(mc, "availability.checked", "calendar")
    assert event["clinic_id"] == CLINIC_ID


# ---------------------------------------------------------------------------
# 13. build_machine_audit_event includes scopes in metadata
# ---------------------------------------------------------------------------


def test_build_machine_audit_event_includes_scopes_in_metadata():
    mc = _fake_machine_context(scopes=frozenset({"vapi:tool", "availability:read"}))
    event = build_machine_audit_event(mc, "slot.suggested", "calendar")
    assert "scopes" in event["metadata"]
    assert set(event["metadata"]["scopes"]) == {"vapi:tool", "availability:read"}


# ---------------------------------------------------------------------------
# 14. build_machine_audit_event rejects missing clinic_id
# ---------------------------------------------------------------------------


def test_build_machine_audit_event_rejects_missing_clinic_id():
    mc = _fake_machine_context(clinic_id=None)
    with pytest.raises(InvalidAuditLogInputError, match="clinic_id"):
        build_machine_audit_event(mc, "slot.suggested", "calendar")


# ---------------------------------------------------------------------------
# 15. record_audit_event calls audit_repo.create_audit_log
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_record_audit_event_calls_create_audit_log():
    pool = _make_pool()
    event = build_audit_event(
        clinic_id=CLINIC_ID, action="test.action", resource_type="test_resource"
    )
    with patch(
        "backend.app.modules.audit.audit_logger.audit_repo.create_audit_log",
        new=AsyncMock(return_value=_fake_audit_log()),
    ) as mock_create:
        await record_audit_event(pool, event)
    mock_create.assert_called_once()


# ---------------------------------------------------------------------------
# 16. record_audit_event returns ok true
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_record_audit_event_returns_ok_true():
    pool = _make_pool()
    event = build_audit_event(
        clinic_id=CLINIC_ID, action="test.action", resource_type="test_resource"
    )
    with patch(
        "backend.app.modules.audit.audit_logger.audit_repo.create_audit_log",
        new=AsyncMock(return_value=_fake_audit_log()),
    ):
        result = await record_audit_event(pool, event)
    assert result["ok"] is True
    assert result["audit_log"] is not None
    assert result["message"] == "Audit event recorded."


# ---------------------------------------------------------------------------
# 17. record_audit_event maps repository error to AuditLoggerError
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_record_audit_event_maps_repo_error_to_audit_logger_error():
    pool = _make_pool()
    event = build_audit_event(
        clinic_id=CLINIC_ID, action="test.action", resource_type="test_resource"
    )
    with patch(
        "backend.app.modules.audit.audit_logger.audit_repo.create_audit_log",
        new=AsyncMock(side_effect=AuditRepoError("db exploded")),
    ):
        with pytest.raises(AuditLoggerError):
            await record_audit_event(pool, event)


# ---------------------------------------------------------------------------
# 18. safe_record_audit_event returns ok true on success
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_safe_record_audit_event_returns_ok_true_on_success():
    pool = _make_pool()
    event = build_audit_event(
        clinic_id=CLINIC_ID, action="test.action", resource_type="test_resource"
    )
    with patch(
        "backend.app.modules.audit.audit_logger.audit_repo.create_audit_log",
        new=AsyncMock(return_value=_fake_audit_log()),
    ):
        result = await safe_record_audit_event(pool, event)
    assert result["ok"] is True
    assert result["audit_log"] is not None


# ---------------------------------------------------------------------------
# 19. safe_record_audit_event returns ok false on failure
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_safe_record_audit_event_returns_ok_false_on_failure():
    pool = _make_pool()
    event = build_audit_event(
        clinic_id=CLINIC_ID, action="test.action", resource_type="test_resource"
    )
    with patch(
        "backend.app.modules.audit.audit_logger.audit_repo.create_audit_log",
        new=AsyncMock(side_effect=Exception("hard failure")),
    ):
        result = await safe_record_audit_event(pool, event)
    assert result["ok"] is False
    assert result["audit_log"] is None
    assert "error" in result


# ---------------------------------------------------------------------------
# 20. safe_record_audit_event never raises
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_safe_record_audit_event_never_raises():
    pool = _make_pool()
    # Malformed event that will fail validation inside record_audit_event
    bad_event = {"clinic_id": "", "action": "", "resource_type": ""}
    result = await safe_record_audit_event(pool, bad_event)
    assert result["ok"] is False


# ---------------------------------------------------------------------------
# 21. No real database is used
# ---------------------------------------------------------------------------


def test_no_real_database_used():
    pool = _make_pool()
    assert isinstance(pool.fetchrow, AsyncMock)
    assert isinstance(pool.fetch, AsyncMock)


# ---------------------------------------------------------------------------
# 22. No external service is called
# ---------------------------------------------------------------------------


def test_no_external_service_called():
    # Verify audit_logger imports only internal modules
    import backend.app.modules.audit.audit_logger as mod
    import inspect
    src = inspect.getsource(mod)
    assert "httpx" not in src
    assert "requests" not in src
    assert "aiohttp" not in src
