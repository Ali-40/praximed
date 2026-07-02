# Auth Wiring Plan — PraxisMed Sprint 7 / Module 60

## Current State (as of Module 61)

### What exists
- `POST /auth/login` — issues a JWT access token (Module 60)
- `get_current_user` FastAPI dependency (Module 59) — decodes and validates Bearer JWT, returns `AuthContext`
- `get_auth_context` FastAPI dependency (Module 36) — reads `X-Service-*` machine auth headers, returns `AuthContext`

### What PHI routes use today
| Route group | Auth dependency | Wired in |
|---|---|---|
| `/patients` | `get_current_user` (JWT Bearer) | Module 61 ✓ |
| `/consultations` | `get_current_user` (JWT Bearer) | Module 62 ✓ |
| `/clinical-workflows` | `get_current_user` (JWT Bearer) | Module 63 ✓ |
| `/appointment-requests` | `get_current_user` (JWT Bearer) | Module 64 ✓ |
| `/notifications` | `get_current_user` (JWT Bearer) | Module 65 ✓ |

---

## Why PHI Routes Are Not Wired Yet

Switching PHI routes from machine auth to JWT auth is a breaking change for all existing
machine integrations (Vapi, n8n, external scripts). The change must be coordinated:
- Machine callers must either obtain a service JWT or keep using `X-Service-*` headers
- The `get_auth_context` dependency may remain as an alternative, or be layered under a combined check
- Frontend clients must be built first so that JWT-issuing login exists in production

Wiring is deferred until the frontend login flow is in place and machine callers are updated.

---

## Planned Wiring Order

Wire `get_current_user` into PHI routes in this order (one module per route group):

### Phase 1 — Lowest risk
1. **`/patients`** ✓ Done (Module 61) — wired to `get_current_user`; tenant/role checks preserved.
2. **`/consultations`** ✓ Done (Module 62) — wired to `get_current_user`; clinical role guard preserved (staff/viewer denied).

### Phase 2 — Mutation routes
3. **`/clinical-workflows`** ✓ Done (Module 63) — wired to `get_current_user`; clinical role guard preserved; staff/viewer denied.
4. **`/appointment-requests`** ✓ Done (Module 64) — wired to `get_current_user`; staff-level role guard preserved; viewer denied.

### Phase 3 — External-facing
5. **`/notifications`** ✓ Done (Module 65) — wired to `get_current_user`; staff-level role guard preserved; viewer denied.

All PHI route JWT wiring complete (Modules 61–65).

---

## Wiring Pattern (reference for future modules)

```python
# Replace or layer with get_current_user
from backend.app.api.dependencies.current_user import get_current_user
from backend.app.core.auth_context import AuthContext

@router.get("/patients")
async def list_patients(
    auth: AuthContext = Depends(get_current_user),
    pool: Any = Depends(get_db_pool),
) -> ...:
    # auth.clinic_id is the verified tenant scope
    ...
```

The `AuthContext` dataclass is shared between both dependencies, so downstream logic that
reads `auth.clinic_id`, `auth.user_id`, and `auth.role` works unchanged after wiring.

---

## Security Notes

- Do **not** remove `get_auth_context` until all machine callers are migrated to JWT or a
  dedicated service-account token flow.
- PHI routes must always enforce `clinic_id` scoping regardless of auth method.
- The `get_current_user` dependency already rejects inactive users and expired tokens.
- Role enforcement (RBAC) is a separate future concern — not in scope for Modules 59–60.
