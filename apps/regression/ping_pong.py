#!/usr/bin/env python3
"""
Smoke test for the backend ping endpoint. This script lives under apps/regression/
per the requirement that end-to-end tests stay centralized.

Usage:
    python3 apps/regression/ping_pong.py

Environment Variables:
    PEGSCANNER_PING_URL: Override the ping endpoint (default http://127.0.0.1:8000/api/ping/).
"""

from __future__ import annotations

import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

BACKEND_PATH = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from stock_research.generated import stock_pb2  # noqa: E402

PING_URL = os.environ.get("PEGSCANNER_PING_URL", "http://127.0.0.1:8000/api/ping/")


def main() -> int:
    req = urllib.request.Request(PING_URL)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            status = resp.getcode()
            payload_bytes = resp.read()
    except urllib.error.URLError as exc:
        print(f"[ping-pong] FAILED: cannot reach {PING_URL}: {exc}", file=sys.stderr)
        return 1

    if status != 200:
        print(f"[ping-pong] FAILED: HTTP {status} from {PING_URL}", file=sys.stderr)
        return 1

    payload = stock_pb2.PingResponse()
    try:
        payload.ParseFromString(payload_bytes)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"[ping-pong] FAILED: invalid protobuf payload: {exc}", file=sys.stderr)
        return 1

    if payload.message != "pong":
        print(f"[ping-pong] FAILED: unexpected message {payload}", file=sys.stderr)
        return 1

    agent = payload.agent
    timestamp = payload.timestamp_ms
    print(f"[ping-pong] OK: agent={agent} timestamp={timestamp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
