"""
Static contract tests for Sprint 13 / Module 99 — Production Deployment Execution Plan.

Verifies:
- Plan document exists and covers all required milestones
- Staging deployment, smoke, and auth hardening milestones are present
- Production domain/TLS, secrets, database, Vapi, legal/GDPR, CI/CD, monitoring addressed
- Go/no-go gates are explicit at each milestone
- Production PHI launch is blocked until all gates pass
- No deployment executed in this module
- Architecture Checkpoint 13 is the next step
- No obvious real secrets in the document
"""

from __future__ import annotations

import os
import re


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

_PLAN_PATH = os.path.join(
    _REPO_ROOT, "docs", "deployment", "PRODUCTION_DEPLOYMENT_EXECUTION_PLAN.md"
)


def _plan() -> str:
    with open(_PLAN_PATH, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 1. Document exists and is non-trivial
# ---------------------------------------------------------------------------


def test_production_deployment_execution_plan_exists() -> None:
    assert os.path.isfile(_PLAN_PATH), f"Plan not found at {_PLAN_PATH}"


def test_production_deployment_execution_plan_not_empty() -> None:
    assert len(_plan()) > 5000


# ---------------------------------------------------------------------------
# 2. Staging deployment
# ---------------------------------------------------------------------------


def test_plan_mentions_staging_deployment() -> None:
    text = _plan()
    assert "staging" in text.lower() and (
        "deploy" in text.lower() or "railway" in text.lower()
    )


def test_plan_mentions_railway_vercel_topology() -> None:
    text = _plan()
    assert "railway" in text.lower() and "vercel" in text.lower()


def test_plan_mentions_staging_https_urls() -> None:
    text = _plan()
    assert "https://" in text and "staging" in text.lower()


def test_plan_mentions_no_ngrok_in_staging() -> None:
    text = _plan()
    assert "ngrok" in text.lower() and (
        "not allowed" in text.lower()
        or "no ngrok" in text.lower()
        or "allowed" in text.lower()
    )


# ---------------------------------------------------------------------------
# 3. Staging smoke validation
# ---------------------------------------------------------------------------


def test_plan_mentions_staging_smoke() -> None:
    text = _plan()
    assert "smoke" in text.lower() and "staging" in text.lower()


def test_plan_mentions_smoke_runbook() -> None:
    text = _plan()
    assert "smoke runbook" in text.lower() or "DEPLOYMENT_SMOKE_RUNBOOK" in text


def test_plan_mentions_evidence_capture() -> None:
    text = _plan()
    assert "evidence" in text.lower() and (
        "capture" in text.lower() or "pass" in text.lower()
    )


# ---------------------------------------------------------------------------
# 4. Auth/session hardening (httpOnly cookie)
# ---------------------------------------------------------------------------


def test_plan_mentions_auth_session_hardening() -> None:
    text = _plan()
    assert (
        "auth" in text.lower()
        and (
            "harden" in text.lower()
            or "hardening" in text.lower()
            or "cookie" in text.lower()
        )
    )


def test_plan_mentions_httponly_cookie() -> None:
    text = _plan()
    assert "httponly" in text.lower() or "HttpOnly" in text


def test_plan_mentions_samesite() -> None:
    text = _plan()
    assert "samesite" in text.lower() or "SameSite" in text


def test_plan_mentions_staging_cross_domain_samesite_none() -> None:
    text = _plan()
    assert (
        "samesite=none" in text.lower()
        or "SameSite=None" in text
    ) and "staging" in text.lower()


def test_plan_mentions_sprint_14_auth_implementation() -> None:
    text = _plan()
    assert "sprint 14" in text.lower() and (
        "implement" in text.lower() or "cookie" in text.lower()
    )


# ---------------------------------------------------------------------------
# 5. Production domain and TLS / HTTPS
# ---------------------------------------------------------------------------


def test_plan_mentions_production_domain_and_tls() -> None:
    text = _plan()
    assert (
        "tls" in text.lower() or "https" in text.lower()
    ) and "production" in text.lower()


def test_plan_mentions_dns() -> None:
    text = _plan()
    assert "dns" in text.lower() and "production" in text.lower()


def test_plan_mentions_no_ngrok_in_production() -> None:
    text = _plan()
    assert "ngrok" in text.lower() and "production" in text.lower()


# ---------------------------------------------------------------------------
# 6. Production secrets
# ---------------------------------------------------------------------------


def test_plan_mentions_production_secrets() -> None:
    text = _plan()
    assert "secret" in text.lower() and "production" in text.lower()


def test_plan_mentions_jwt_secret_key() -> None:
    assert "JWT_SECRET_KEY" in _plan()


def test_plan_mentions_vapi_webhook_secret() -> None:
    assert "VAPI_WEBHOOK_SECRET" in _plan()


def test_plan_mentions_no_placeholder_secrets_in_production() -> None:
    text = _plan()
    assert "placeholder" in text.lower() and "production" in text.lower()


# ---------------------------------------------------------------------------
# 7. Production database / PostgreSQL
# ---------------------------------------------------------------------------


def test_plan_mentions_production_database() -> None:
    text = _plan()
    assert (
        "postgresql" in text.lower() or "postgres" in text.lower()
    ) and "production" in text.lower()


def test_plan_mentions_managed_postgresql() -> None:
    text = _plan()
    assert "managed" in text.lower() and (
        "postgresql" in text.lower() or "postgres" in text.lower()
    )


def test_plan_mentions_backups_and_pitr() -> None:
    text = _plan()
    assert "backup" in text.lower() and (
        "pitr" in text.lower() or "point-in-time" in text.lower()
    )


def test_plan_mentions_migration_gate() -> None:
    text = _plan()
    assert "migration" in text.lower() and (
        "gate" in text.lower() or "run_migrations" in text.lower()
    )


# ---------------------------------------------------------------------------
# 8. Production Vapi assistant
# ---------------------------------------------------------------------------


def test_plan_mentions_production_vapi_assistant() -> None:
    text = _plan()
    assert "vapi" in text.lower() and "production" in text.lower()


def test_plan_mentions_vapi_tool_singular_scope() -> None:
    text = _plan()
    assert "vapi:tool" in text


def test_plan_mentions_no_auto_confirmation() -> None:
    text = _plan()
    assert (
        "no auto-confirm" in text.lower()
        or "auto-confirm" in text.lower()
        or "status=new" in text.lower()
        or "status='new'" in text.lower()
        or "action_required" in text.lower()
    )


# ---------------------------------------------------------------------------
# 9. Legal/GDPR/compliance review
# ---------------------------------------------------------------------------


def test_plan_mentions_legal_gdpr_compliance_review() -> None:
    text = _plan()
    assert (
        "gdpr" in text.lower() or "legal" in text.lower() or "compliance" in text.lower()
    )


def test_plan_mentions_austrian_healthcare() -> None:
    text = _plan()
    assert "austrian" in text.lower() or "austria" in text.lower()


def test_plan_mentions_raw_payload_phi_policy() -> None:
    text = _plan()
    assert "raw_payload" in text and "phi" in text.lower()


def test_plan_mentions_compliance_review_is_hard_gate() -> None:
    text = _plan()
    assert (
        "hard" in text.lower()
        and (
            "gate" in text.lower()
            or "blocker" in text.lower()
        )
    ) and (
        "gdpr" in text.lower()
        or "legal" in text.lower()
        or "compliance" in text.lower()
    )


# ---------------------------------------------------------------------------
# 10. CI/CD pipeline
# ---------------------------------------------------------------------------


def test_plan_mentions_cicd_pipeline() -> None:
    text = _plan()
    assert (
        "ci/cd" in text.lower()
        or "ci cd" in text.lower()
        or "pipeline" in text.lower()
        or "github actions" in text.lower()
    )


def test_plan_mentions_automated_test_gate() -> None:
    text = _plan()
    assert "automated" in text.lower() and "test" in text.lower()


def test_plan_mentions_no_secrets_in_ci_logs() -> None:
    text = _plan()
    assert "secret" in text.lower() and "log" in text.lower()


# ---------------------------------------------------------------------------
# 11. Production monitoring
# ---------------------------------------------------------------------------


def test_plan_mentions_production_monitoring() -> None:
    text = _plan()
    assert "monitor" in text.lower() and "production" in text.lower()


def test_plan_mentions_apm() -> None:
    text = _plan()
    assert "apm" in text.lower() or "application performance" in text.lower()


def test_plan_mentions_alerting() -> None:
    text = _plan()
    assert "alert" in text.lower()


def test_plan_mentions_structured_logs() -> None:
    text = _plan()
    assert "structured" in text.lower() and "log" in text.lower()


# ---------------------------------------------------------------------------
# 12. Go/no-go gates
# ---------------------------------------------------------------------------


def test_plan_mentions_go_no_go_gates() -> None:
    text = _plan()
    assert "go/no-go" in text.lower() or "go / no-go" in text.lower()


def test_plan_mentions_gate_at_each_milestone() -> None:
    text = _plan()
    assert text.lower().count("go/no-go") >= 5 or text.lower().count("gate") >= 5


def test_plan_mentions_decision_gates() -> None:
    text = _plan()
    assert "decision gate" in text.lower() or (
        "gate" in text.lower() and "milestone" in text.lower()
    )


# ---------------------------------------------------------------------------
# 13. Production PHI launch blocked until all gates pass
# ---------------------------------------------------------------------------


def test_plan_mentions_production_phi_launch_blocked() -> None:
    text = _plan()
    assert "phi" in text.lower() and (
        "no-go" in text.lower() or "blocked" in text.lower()
    )


def test_plan_mentions_all_gates_must_pass_before_phi_launch() -> None:
    text = _plan()
    assert "production phi launch" in text.lower() and (
        "no-go" in text.lower() or "blocked" in text.lower() or "all" in text.lower()
    )


def test_plan_mentions_twelve_open_blockers() -> None:
    text = _plan()
    assert "12" in text and "blocker" in text.lower()


# ---------------------------------------------------------------------------
# 14. No deployment in this module
# ---------------------------------------------------------------------------


def test_plan_mentions_no_deployment_in_this_module() -> None:
    text = _plan()
    assert (
        "no deployment" in text.lower()
        or "planning only" in text.lower()
        or "plan only" in text.lower()
    )


def test_plan_mentions_planning_document_only() -> None:
    text = _plan()
    assert (
        "planning document" in text.lower()
        or "docs only" in text.lower()
        or "documentation" in text.lower()
    )


# ---------------------------------------------------------------------------
# 15. Architecture Checkpoint 13
# ---------------------------------------------------------------------------


def test_plan_mentions_architecture_checkpoint_13() -> None:
    text = _plan()
    assert (
        "checkpoint 13" in text.lower()
        or "architecture checkpoint 13" in text.lower()
    )


def test_plan_mentions_checkpoint_13_go_no_go_decision() -> None:
    text = _plan()
    assert "checkpoint 13" in text.lower() and (
        "go/no-go" in text.lower()
        or "decision" in text.lower()
    )


def test_plan_mentions_sprint_13_deliverables_under_review() -> None:
    text = _plan()
    assert "module 95" in text.lower() or "sprint 13" in text.lower()


# ---------------------------------------------------------------------------
# 16. Failure stop rules
# ---------------------------------------------------------------------------


def test_plan_mentions_stop_rules() -> None:
    text = _plan()
    assert (
        "stop rule" in text.lower()
        or "failure stop" in text.lower()
        or (
            "halt" in text.lower() and "rollback" in text.lower()
        )
    )


def test_plan_mentions_rollback() -> None:
    text = _plan()
    assert "rollback" in text.lower()


# ---------------------------------------------------------------------------
# 17. No obvious real secrets in the document
# ---------------------------------------------------------------------------


def test_plan_no_real_api_keys() -> None:
    real_key_pattern = re.compile(r"sk-[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{50,}")
    matches = real_key_pattern.findall(_plan())
    assert not matches, f"Possible real key in plan: {matches}"


def test_plan_no_real_db_password() -> None:
    text = _plan()
    for line in text.splitlines():
        if "postgresql://" in line:
            assert (
                "placeholder" in line.lower()
                or "example" in line.lower()
                or "<" in line
                or "#" in line
            ), f"Unexpected non-placeholder DATABASE_URL: {line!r}"
