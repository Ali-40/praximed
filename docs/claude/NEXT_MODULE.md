# Sprint 3 / Module 36 — Auth and Tenant Access Foundation

## Current project folder
`/Users/aliabdeltawab/Documents/praximed`

## Completed modules
- Sprint 1, Modules 1–23: all committed.
- Sprint 2, Modules 24–34: all committed.
- Sprint 3, Module 35: committed.
- Architecture Checkpoint 02: committed.

Do not modify completed modules unless absolutely required.

## Task scope
Create the shared authentication and tenant access foundation.

## Purpose
Architecture Checkpoint 02 identified the biggest current risk: PHI routes are open and `clinic_id` is caller-supplied without tenant ownership enforcement. This module creates the auth/tenant access primitives; route enforcement follows in Module 37.

## Create or update only

1. `backend/app/core/auth_context.py`
2. `backend/app/api/dependencies/auth.py`
3. `backend/tests/test_auth_context.py`
4. `backend/tests/test_auth_dependencies.py`
5. `docs/claude/CURRENT_STATE.md`
6. `docs/claude/NEXT_MODULE.md`

Do not modify existing route files. Do not modify router.py. Do not use a real database in tests.

## Tests (context: 23, dependencies: 11 = 34 total)

## Acceptance criteria

- All Module 36 tests pass.
- All previous tests still pass.
- Existing route behavior is not changed.
- No external auth provider is called.
- Commit all changes only if tests pass.

## Commit message

`Sprint 3 / Module 36 — Auth and tenant access foundation`
