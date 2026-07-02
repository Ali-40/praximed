"""
Local Vapi appointment intake smoke script — PraxisMed Sprint 11 / Module 83

Sends a fake Vapi appointment capture request to the local backend to prove the
intake→appointment-request loop: Vapi-like tool call → appointment_requests row →
dashboard displays it → staff can confirm it.

No real Vapi connection, no ngrok, no real patient data.

Prerequisites (run in this order before this script):
  1. docker-compose -f docker-compose.postgres.yml up -d
  2. export DATABASE_URL=postgresql://praxismed:praxismed_local_password@localhost:5433/praxismed_local
  3. cd backend && alembic upgrade head && cd ..
  4. python backend/scripts/seed_local_data.py
  5. uvicorn backend.app.main:app --reload --port 8000

  IMPORTANT — config_loader prerequisite (Module 84):
  main.py must wire app.state.config_loader before the capture endpoint works.
  Until that is done, POST /vapi/tools/capture-appointment-request returns HTTP 503.
  This script handles 503 gracefully and prints what is needed to fix it.

Usage:
  python backend/scripts/smoke_vapi_appointment_intake.py
  python backend/scripts/smoke_vapi_appointment_intake.py /path/to/custom_payload.json

  Override API base URL:
  PRAXIMED_API_BASE_URL=http://127.0.0.1:8000 python backend/scripts/smoke_vapi_appointment_intake.py

LOCAL FAKE DATA ONLY — never use real patient data or real credentials.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

_SCRIPT_DIR = Path(__file__).parent
_PROJECT_ROOT = _SCRIPT_DIR.parents[1]

_DEFAULT_PAYLOAD = (
    _PROJECT_ROOT
    / "docs"
    / "integrations"
    / "local_payloads"
    / "vapi_appointment_intake.json"
)

# Endpoint: POST /vapi/tools/capture-appointment-request
# Uses machine auth (no HMAC/signature — that is only required for the webhook endpoint
# POST /webhooks/vapi/call-event).  The tool endpoint uses X-Vapi-* machine auth headers.
ENDPOINT = "/vapi/tools/capture-appointment-request"

LOCAL_CLINIC_ID = "11111111-1111-1111-1111-111111111111"


def main() -> int:
    api_base = os.environ.get("PRAXIMED_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

    payload_path = Path(sys.argv[1]) if len(sys.argv) > 1 else _DEFAULT_PAYLOAD

    if not payload_path.is_file():
        print(f"ERROR: payload file not found: {payload_path}", file=sys.stderr)
        return 1

    try:
        payload_bytes = payload_path.read_bytes()
        payload_data = json.loads(payload_bytes)
    except json.JSONDecodeError as exc:
        print(f"ERROR: payload file is not valid JSON: {exc}", file=sys.stderr)
        return 1

    url = f"{api_base}{ENDPOINT}"

    # Machine auth headers for the Vapi tool endpoint.
    # Required scope: vapi:tool — accepted via X-Vapi-Scopes alias.
    # No HMAC signature is needed for tool routes (only for POST /webhooks/vapi/call-event).
    headers = {
        "Content-Type": "application/json",
        "X-Vapi-Service-Name": "vapi",
        "X-Vapi-Clinic-Id": LOCAL_CLINIC_ID,
        "X-Vapi-Scopes": "vapi:tool",
    }

    print("=" * 60)
    print("PraxisMed — Vapi Appointment Intake Smoke")
    print("=" * 60)
    print(f"Endpoint:     {url}")
    print(f"Payload file: {payload_path}")
    print(f"clinic_ref:   {payload_data.get('clinic_ref', '(not set)')}")
    print(f"patient_name: {payload_data.get('patient_name', '(not set)')}")
    print(f"call_id:      {payload_data.get('call_id', '(not set)')}")
    print()

    req = urllib.request.Request(
        url,
        data=payload_bytes,
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        status = exc.code
        raw = exc.read().decode("utf-8")
    except urllib.error.URLError as exc:
        print(f"ERROR: could not connect to {url}", file=sys.stderr)
        print(f"Reason: {exc.reason}", file=sys.stderr)
        print(file=sys.stderr)
        print("Is the backend running? Start with:", file=sys.stderr)
        print("  uvicorn backend.app.main:app --reload --port 8000", file=sys.stderr)
        return 1

    try:
        body = json.loads(raw)
    except json.JSONDecodeError:
        body = {"raw": raw}

    print(f"HTTP status:  {status}")

    if status == 503:
        detail = body.get("detail", "")
        if "config_loader" in detail.lower() or "not initialised" in detail.lower():
            print()
            print("NOTE: HTTP 503 — app.state.config_loader is not initialized.")
            print("Wire ClinicConfigLoader in main.py lifespan (Module 84):")
            print("  from backend.app.core.config_loader import ClinicConfigLoader")
            print("  app.state.config_loader = ClinicConfigLoader(pool=pool)")
            print("Then restart the backend and re-run this script.")
    elif status == 401:
        print("NOTE: HTTP 401 — machine auth headers were rejected.")
        print(f"Sent: X-Vapi-Service-Name=vapi, X-Vapi-Clinic-Id={LOCAL_CLINIC_ID}, X-Vapi-Scopes=vapi:tool")
    elif status == 403:
        print("NOTE: HTTP 403 — clinic ID mismatch or scope denied.")
        print(f"Ensure X-Vapi-Clinic-Id matches clinic_ref in the payload ({LOCAL_CLINIC_ID}).")

    print(f"Response:     {json.dumps(body, indent=2, ensure_ascii=False)}")

    if 200 <= status < 300:
        request_row = body.get("request") or {}
        appt_id     = request_row.get("id", "(not returned)")
        appt_status = request_row.get("status", "(not returned)")
        notif_ok    = body.get("notification_created", "(not returned)")

        print()
        print("Appointment request created:")
        print(f"  ID:                   {appt_id}")
        print(f"  Status:               {appt_status}  (must be 'new' — not auto-confirmed)")
        print(f"  Notification created: {notif_ok}")
        print()
        print("Next steps — close the intake→confirm loop:")
        print("  1. Open http://localhost:3000/dashboard")
        print("  2. Check Appointments section — new row should appear")
        print("  3. Click Confirm on the new row")
        print("  4. Verify status updates to 'confirmed' in the UI")
        return 0
    else:
        print(f"\nERROR: non-2xx response ({status})", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
