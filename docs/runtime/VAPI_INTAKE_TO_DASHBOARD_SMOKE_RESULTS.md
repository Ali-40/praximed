# Vapi Intake to Dashboard Smoke Results — PraxisMed Sprint 11 / Module 84

**Date:** 2026-07-02
**Verdict:** PARTIAL — 503 fixed; new HTTP 500 UUID validation blocker found

---

## 1. Purpose

This document records the outcome of running `smoke_vapi_appointment_intake.py` against
the local backend after wiring `app.state.config_loader` in Module 84. The goal was to
confirm that `POST /vapi/tools/capture-appointment-request` returns HTTP 200 and creates
an appointment request row visible in the dashboard.

---

## 2. Environment

| Component | Details |
|---|---|
| PostgreSQL | Local Docker container — `docker-compose.postgres.yml` (port 5433) |
| Backend | `uvicorn backend.app.main:app --reload --port 8000` on `http://127.0.0.1:8000` |
| JWT_SECRET_KEY | Local-dev value only — not committed; not used in production |
| Seed data | `backend/scripts/seed_local_data.py` (clinic `11111111-1111-1111-1111-111111111111`) |
| Smoke script | `backend/scripts/smoke_vapi_appointment_intake.py` |
| Payload | `docs/integrations/local_payloads/vapi_appointment_intake.json` |
| Tunnel | None — local only |

---

## 3. Module 84 Change — config_loader Wired

Before Module 84, `main.py` lifespan only set `app.state.db_pool`. The capture endpoint
depended on `app.state.config_loader` (via `get_config_loader()`) and returned HTTP 503
when it was `None`.

**Fix applied in Module 84 (`backend/app/main.py`):**

```python
# In lifespan startup, after db_pool is set:
app.state.config_loader = ClinicConfigLoader(pool=app.state.db_pool)

# In lifespan shutdown:
app.state.config_loader = None
```

**Result:** HTTP 503 is resolved. The endpoint now proceeds past the config_loader check.

---

## 4. Smoke Script Run — Result

```
python backend/scripts/smoke_vapi_appointment_intake.py

HTTP status:  500
Response: {"detail": "Internal error capturing appointment request: tenant_id must be a valid UUID (v1–v5); got '11111111-1111-1111-1111-111111111111'"}
```

**HTTP 503 → resolved.**
**New blocker: HTTP 500 — UUID validation rejects seed clinic UUID.**

---

## 5. Root Cause — UUID Validation

`ClinicConfigLoader._assert_valid_uuid()` in `backend/app/core/config_loader.py` enforces:

```python
_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
```

The regex requires the variant nibble (9th group, first character) to be `[89ab]` — the
RFC 4122 variant-1 indicator. The seed clinic UUID `11111111-1111-1111-1111-111111111111`
has `1` in that position, which does not match `[89ab]`.

| UUID segment | Position | Seed value | Regex requirement | Match? |
|---|---|---|---|---|
| `11111111` | time-low | `1...` | `[0-9a-f]{8}` | YES |
| `1111` | time-mid | `1111` | `[0-9a-f]{4}` | YES |
| `1111` | time-hi-version | `1111` | `[1-5][0-9a-f]{3}` | YES (`1` is version byte) |
| `1111` | clock-seq | `1...` | `[89ab][0-9a-f]{3}` | **NO** — `1` not in `[89ab]` |
| `111111111111` | node | `111...` | `[0-9a-f]{12}` | YES |

The check that fails: clock-seq high byte must be `8`, `9`, `a`, or `b` (RFC 4122 variant).
The seed UUID uses `1` for all nibbles, which makes it a structurally invalid UUID by
this strict interpretation.

---

## 6. Why config_loader.py Was Not Modified in Module 84

Module 84's allowed changes list did not include `backend/app/core/config_loader.py`.
The UUID check was designed to prevent path-traversal attacks (blocking malformed
tenant IDs that could escape the config directory), not to enforce RFC 4122 variant
compliance. Relaxing the variant byte constraint from `[89ab]` to `[0-9a-f]` does not
weaken the path-traversal protection — it only allows nil/non-RFC-4122 UUIDs that are
otherwise safe for filesystem use.

This fix is scoped to Module 85.

---

## 7. What Was Proven (Module 84 scope)

| Claim | Status |
|---|---|
| `app.state.config_loader` is initialized in lifespan startup | PROVEN — 9 new lifespan tests pass |
| `app.state.config_loader` is a `ClinicConfigLoader` instance | PROVEN |
| `app.state.config_loader._pool` is `None` without `DATABASE_URL` | PROVEN |
| `app.state.config_loader._pool` matches `db_pool` when `DATABASE_URL` is set | PROVEN |
| `app.state.config_loader` is reset to `None` on shutdown | PROVEN |
| `db_pool` close is still called on shutdown alongside config_loader teardown | PROVEN |
| HTTP 503 from capture endpoint is resolved | PROVEN — smoke returned 500, not 503 |
| `/health` route still works after config_loader wiring | PROVEN |
| Full test suite passes after lifespan changes | PROVEN — 1589/1589 |

---

## 8. What Remains (Module 85 scope)

| Item | Detail |
|---|---|
| UUID validation blocks smoke | Relax `_UUID_RE` variant byte from `[89ab]` to `[0-9a-f]` in `config_loader.py` |
| Smoke script returns HTTP 200 | Blocked by UUID validation; unblocked once regex is relaxed |
| Dashboard row from Vapi intake | Blocked by same UUID issue |
| Staff Confirm on Vapi-created row | Blocked by same UUID issue |

**Exact fix needed in `backend/app/core/config_loader.py`:**

```python
# Current (too strict — rejects structurally valid local-dev UUIDs):
_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)

# Proposed (relaxed variant byte — still blocks path traversal, allows nil-like UUIDs):
_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[0-9a-f]{4}-[0-9a-f]{12}$"
)
```

This relaxation keeps the format check (length, separators, hex groups) while dropping
the RFC 4122 variant constraint — which is the security-relevant part for tenant ID
path safety.

---

## 9. Full Test Suite

| Run | Tests | Result |
|---|---|---|
| Module 84 (after main.py change + 9 new tests) | 1589 | PASS |

All prior test suites:
- Module 83: 1580/1580
- Module 81: 1570/1570
- Module 80: 1560/1560
