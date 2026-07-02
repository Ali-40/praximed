"""
Inspect a captured Vapi tool-call payload JSON — PraxisMed Sprint 11 / Module 87

Local developer tool that summarizes the structure of a Vapi tool-call body and
assesses whether it is directly compatible with VapiAppointmentCaptureRequest or
requires an adapter.

Safe to run without a running backend server. Uses stdlib only. Never prints full
patient text, phone numbers, transcripts, or secrets — only structural summaries
(key names, nesting, compatibility verdict).

Usage:
  python backend/scripts/inspect_vapi_tool_payload.py --payload-file <path>

Example:
  python backend/scripts/inspect_vapi_tool_payload.py \\
    --payload-file docs/integrations/local_payloads/vapi_real_tool_payload_sample.json

LOCAL DEVELOPMENT TOOL ONLY — do not use with real patient data.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Required fields for direct VapiAppointmentCaptureRequest compatibility.
_REQUIRED_FLAT_FIELDS = {"clinic_ref", "call_id", "patient_name"}

# Sensitive field names — values are never printed, only key presence is noted.
_SENSITIVE_KEYS = {
    "patient_name", "caller_phone", "patient_email", "date_of_birth",
    "reason", "number", "phoneNumber", "transcript", "summary",
    "customer", "name", "email", "phone",
}


def _redact(key: str, value: object) -> str:
    """Return '[redacted]' for sensitive keys; safe repr for safe keys."""
    if key.lower() in {k.lower() for k in _SENSITIVE_KEYS}:
        return "[redacted]"
    if isinstance(value, str):
        return repr(value[:60] + "..." if len(value) > 60 else value)
    if isinstance(value, (int, float, bool, type(None))):
        return repr(value)
    if isinstance(value, dict):
        return f"{{...{len(value)} keys...}}"
    if isinstance(value, list):
        return f"[...{len(value)} items...]"
    return repr(type(value).__name__)


def _print_keys(label: str, d: dict, indent: int = 2) -> None:
    pad = " " * indent
    print(f"{label}:")
    for k, v in d.items():
        print(f"{pad}{k!r}: {_redact(k, v)}")


def _detect_vapi_tool_call(data: dict) -> tuple[bool, dict | None, dict | None]:
    """
    Return (is_vapi_tool_call, first_tool_call, message).

    is_vapi_tool_call = True if message.toolCallList is present and non-empty.
    """
    message = data.get("message")
    if not isinstance(message, dict):
        return False, None, None
    tool_list = message.get("toolCallList")
    if not isinstance(tool_list, list) or not tool_list:
        return False, None, None
    return True, tool_list[0], message


def _detect_flat_capture(data: dict) -> bool:
    """Return True if data has the flat VapiAppointmentCaptureRequest fields."""
    return bool(_REQUIRED_FLAT_FIELDS & set(data.keys()))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect a Vapi tool-call payload JSON for capture-endpoint compatibility."
    )
    parser.add_argument(
        "--payload-file",
        required=True,
        help="Path to the JSON payload file to inspect.",
    )
    args = parser.parse_args()

    payload_path = Path(args.payload_file)
    if not payload_path.is_file():
        print(f"ERROR: file not found: {payload_path}", file=sys.stderr)
        return 1

    try:
        data = json.loads(payload_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: not valid JSON: {exc}", file=sys.stderr)
        return 1

    if not isinstance(data, dict):
        print("ERROR: payload must be a JSON object (dict)", file=sys.stderr)
        return 1

    print("=" * 60)
    print("PraxisMed — Vapi Tool Payload Inspector")
    print("=" * 60)
    print(f"File: {payload_path}")
    print()

    # --- Top-level keys -------------------------------------------------------
    top_keys = list(data.keys())
    print(f"Top-level keys ({len(top_keys)}): {top_keys}")
    print()

    # --- Shape detection -------------------------------------------------------
    is_vapi_tc, first_tool_call, message = _detect_vapi_tool_call(data)
    is_flat = _detect_flat_capture(data)

    if is_vapi_tc:
        print("Shape: REAL VAPI TOOL-CALL (message.toolCallList present)")
        print()

        msg_type = message.get("type", "(not set)")
        print(f"  message.type: {msg_type!r}")

        # --- Call ID from message.call -----------------------------------------
        call = message.get("call", {})
        call_id = call.get("id", "(not found)")
        print(f"  message.call.id: {call_id!r}  → maps to call_id in capture schema")

        # --- Customer phone (redacted) ------------------------------------------
        customer = call.get("customer", {})
        if "number" in customer:
            print("  message.call.customer.number: [redacted]  → maps to caller_phone")

        # --- Tool call details --------------------------------------------------
        print()
        print(f"  toolCallList[0].id: {first_tool_call.get('id', '(not set)')!r}")
        func = first_tool_call.get("function", {})
        func_name = func.get("name", "(not set)")
        print(f"  function.name: {func_name!r}")

        # --- Arguments ---------------------------------------------------------
        args_raw = func.get("arguments", {})
        if isinstance(args_raw, str):
            try:
                args_raw = json.loads(args_raw)
                print("  function.arguments: (JSON string — parsed to dict)")
            except json.JSONDecodeError:
                print("  function.arguments: (JSON string — could not parse)")
                args_raw = {}

        if isinstance(args_raw, dict):
            arg_keys = list(args_raw.keys())
            print(f"  function.arguments keys ({len(arg_keys)}): {arg_keys}")

            # Redact argument values
            print()
            print("  Argument values (sensitive fields redacted):")
            for k, v in args_raw.items():
                print(f"    {k!r}: {_redact(k, v)}")
        else:
            print("  function.arguments: (unexpected type — not a dict)")

        # --- Compatibility assessment ------------------------------------------
        print()
        print("Compatibility with VapiAppointmentCaptureRequest:")
        print("  clinic_ref   — NOT in arguments (expected via X-Vapi-Clinic-Id header)")
        print("  call_id      — NOT in arguments (resolved from message.call.id)")
        print("  patient_name — in arguments?", "YES" if isinstance(args_raw, dict) and "patient_name" in args_raw else "NO")
        print()
        print("Verdict: NEEDS ADAPTER")
        print("  This shape is not directly compatible with the current capture schema.")
        print("  An adapter is needed to extract arguments from message.toolCallList")
        print("  and resolve clinic_ref from X-Vapi-Clinic-Id / machine auth.")
        print()
        print("Suggested next action:")
        print("  1. Capture a real Vapi tool-call request body (see VAPI_TO_APPOINTMENT_WORKFLOW_PREP.md).")
        print("  2. Run this inspector on the captured payload.")
        print("  3. If shape matches this sample, implement an adapter in the capture route.")

    elif is_flat:
        flat_found = _REQUIRED_FLAT_FIELDS & set(data.keys())
        flat_missing = _REQUIRED_FLAT_FIELDS - set(data.keys())
        print("Shape: FLAT (local harness format — directly compatible)")
        print()
        print(f"  Required fields present: {sorted(flat_found)}")
        if flat_missing:
            print(f"  Required fields missing: {sorted(flat_missing)}")
        print()
        print("Compatibility with VapiAppointmentCaptureRequest:")
        if not flat_missing:
            print("  Verdict: COMPATIBLE — can be sent directly to capture endpoint.")
        else:
            print(f"  Verdict: INCOMPLETE — missing required fields: {sorted(flat_missing)}")
        print()
        print("Suggested next action:")
        print("  Run smoke_vapi_appointment_intake.py with this payload.")

    else:
        print("Shape: UNRECOGNISED")
        print("  Does not match the real Vapi tool-call shape (message.toolCallList)")
        print("  or the flat local harness shape (clinic_ref, call_id, patient_name).")
        print()
        _print_keys("All keys", data)
        print()
        print("Suggested next action:")
        print("  Capture a real Vapi tool-call request body and inspect again.")

    print()
    print("NOTE: Patient field values are redacted above. No PHI is printed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
