"""Generate a trace-run manifest for Role E prompt-version evidence.

The script deliberately refuses to create an evidence file when the API
reports tracing disabled. This prevents local fallback requests from being
mistaken for Langfuse traces.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import httpx


def main() -> None:
    parser = argparse.ArgumentParser(description="Run repeated requests for Langfuse trace evidence")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--label", required=True, help="Label configured on the running API")
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--output", type=Path, default=Path("submission/evidence/role_e_trace_manifest.json"))
    args = parser.parse_args()
    if args.count < 10:
        raise SystemExit("Role E requires at least 10 requests")

    with httpx.Client(base_url=args.base_url, timeout=30.0) as client:
        health = client.get("/health").raise_for_status().json()
        if not health.get("tracing_enabled"):
            raise SystemExit(
                "Langfuse tracing is disabled; configure LANGFUSE_PUBLIC_KEY and "
                "LANGFUSE_SECRET_KEY on the API before collecting evidence."
            )
        requests = []
        for index in range(args.count):
            payload = {
                "user_id": f"role-e-{index + 1:02d}",
                "session_id": f"prompt-{args.label}",
                "feature": "monitoring",
                "message": "Explain how metrics, traces and logs work together.",
            }
            response = client.post("/chat", json=payload)
            response.raise_for_status()
            requests.append(
                {
                    "correlation_id": response.headers.get("x-request-id"),
                    "status_code": response.status_code,
                    "prompt_label": args.label,
                }
            )

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "prompt_label": args.label,
        "request_count": len(requests),
        "trace_ids": [],
        "requests": requests,
        "note": "Fill trace_ids from Langfuse UI after confirming prompt_name/version metadata.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Ran {len(requests)} traced requests for label={args.label}")
    print(f"Manifest: {args.output}")


if __name__ == "__main__":
    main()
