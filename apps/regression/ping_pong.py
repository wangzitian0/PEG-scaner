#!/usr/bin/env python3
"""
Smoke test for the backend GraphQL ping. This script lives under apps/regression/
per the requirement that end-to-end tests stay centralized.

Usage:
    python3 apps/regression/ping_pong.py

Environment Variables:
    PEGSCANNER_GRAPHQL_URL: Override the endpoint (default http://127.0.0.1:8000/graphql).
"""

from __future__ import annotations

import os
import sys
import json
import urllib.error
import urllib.request

GRAPHQL_URL = os.environ.get("PEGSCANNER_GRAPHQL_URL", "http://127.0.0.1:8000/graphql")
PING_QUERY = {"query": "query Ping { ping { message agent timestampMs } }"}


def main() -> int:
    body = json.dumps(PING_QUERY).encode("utf-8")
    req = urllib.request.Request(
        GRAPHQL_URL, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            status = resp.getcode()
            payload_bytes = resp.read()
    except urllib.error.URLError as exc:
        print(f"[ping-pong] FAILED: cannot reach {GRAPHQL_URL}: {exc}", file=sys.stderr)
        return 1

    if status != 200:
        print(f"[ping-pong] FAILED: HTTP {status} from {GRAPHQL_URL}", file=sys.stderr)
        return 1

    try:
        payload = json.loads(payload_bytes)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"[ping-pong] FAILED: invalid JSON payload: {exc}", file=sys.stderr)
        return 1

    if "errors" in payload:
        print(f"[ping-pong] FAILED: GraphQL errors: {payload['errors']}", file=sys.stderr)
        return 1

    data = payload.get("data", {}).get("ping", {})
    if data.get("message") != "pong":
        print(f"[ping-pong] FAILED: unexpected message {data}", file=sys.stderr)
        return 1

    agent = data.get("agent")
    timestamp = data.get("timestampMs")
    print(f"[ping-pong] OK: agent={agent} timestamp={timestamp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
