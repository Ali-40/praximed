"""
Webhook payload signing helper — PraxisMed Sprint 5 / Module 48

CLI script for generating HMAC-SHA256 webhook signatures during local
integration testing.  Safe to import without side effects.

Usage:
    python backend/scripts/sign_webhook_payload.py \\
        --secret <secret> \\
        --payload '<json string>'

    python backend/scripts/sign_webhook_payload.py \\
        --secret <secret> \\
        --payload-file /path/to/payload.json

    # Plain hex digest without sha256= prefix
    python backend/scripts/sign_webhook_payload.py \\
        --secret <secret> \\
        --payload '<json string>' \\
        --prefix false
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import sys
from pathlib import Path
from typing import List, Optional


# ---------------------------------------------------------------------------
# Pure signing function
# ---------------------------------------------------------------------------


def sign_payload(payload_body: bytes, secret: str, prefix: bool = True) -> str:
    """Compute an HMAC-SHA256 signature for *payload_body* using *secret*.

    Returns ``sha256=<hex_digest>`` when *prefix* is True (default),
    otherwise returns the raw hex digest.

    Raises:
        TypeError: when *payload_body* is not bytes.
        ValueError: when *secret* is empty.
    """
    if not isinstance(payload_body, bytes):
        raise TypeError(
            f"'payload_body' must be bytes; got {type(payload_body).__name__}"
        )
    if not secret or not str(secret).strip():
        raise ValueError("'secret' must not be empty")

    digest = hmac.new(
        secret.encode("utf-8"),
        payload_body,
        hashlib.sha256,
    ).hexdigest()

    return f"sha256={digest}" if prefix else digest


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    """Entry point — parses args, prints signature to stdout, returns exit code."""
    parser = argparse.ArgumentParser(
        description="Compute an HMAC-SHA256 webhook signature for local testing.",
        add_help=True,
    )
    parser.add_argument(
        "--secret",
        required=True,
        help="Webhook secret (never logged).",
    )
    payload_group = parser.add_mutually_exclusive_group(required=True)
    payload_group.add_argument(
        "--payload",
        help="Payload string (UTF-8 encoded to bytes before signing).",
    )
    payload_group.add_argument(
        "--payload-file",
        metavar="FILE",
        help="Path to a file whose raw bytes are signed.",
    )
    parser.add_argument(
        "--prefix",
        default="true",
        choices=["true", "false"],
        help="Prepend 'sha256=' to the digest (default: true).",
    )

    args = parser.parse_args(argv)

    # Resolve payload bytes
    if args.payload is not None:
        payload_bytes = args.payload.encode("utf-8")
    else:
        path = Path(args.payload_file)
        if not path.exists():
            print(f"ERROR: payload file not found: {path}", file=sys.stderr)
            return 1
        payload_bytes = path.read_bytes()

    include_prefix = args.prefix.lower() == "true"

    try:
        signature = sign_payload(payload_bytes, args.secret, prefix=include_prefix)
    except (TypeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(signature)
    return 0


if __name__ == "__main__":
    sys.exit(main())
