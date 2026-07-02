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
| `/consultations` | `get_auth_context` (header) | pending |
| `/clinical-workflows` | `get_auth_context` (header) | pending |
| `/appointment-requests` | `get_auth_context` (header) | pending |
| `/notifications` | `get_auth_context` (header) | pending |

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
2. **`/consultations`** — closely tied to patients; wire together or immediately after.

### Phase 2 — Mutation routes
3. **`/clinical-workflows`** — write-heavy; wire after patient/consultation auth is stable.
4. **`/appointment-requests`** — dual-path (machine callers from Vapi + human callers);
   requires coordination with machine auth layer.

### Phase 3 — External-facing
5. **`/notifications`** — may remain machine-only long-term (triggered by n8n/Vapi); evaluate
   whether human JWT is ever needed here before wiring.

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
