"""Run a reproducible latency/response-shape baseline against a local endpoint."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import statistics
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "benchmarks" / "fixtures" / "systemone.json"


def request(url: str, payload: dict) -> tuple[float, dict]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"content-type": "application/json"},
        method="POST",
    )
    start = time.perf_counter()
    with urllib.request.urlopen(req, timeout=300) as response:
        result = json.load(response)
    return (time.perf_counter() - start) * 1000, result


def validate_response(response: dict) -> None:
    if not isinstance(response, dict) or not isinstance(response.get("answers"), dict):
        raise ValueError("response is missing an answers object")
    for key in ("department", "escalate", "frustration"):
        if key not in response["answers"]:
            raise ValueError(f"response is missing answer: {key}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8008")
    parser.add_argument("--model", default="safeticket-baseline")
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.repetitions < 1:
        parser.error("--repetitions must be positive")

    fixture = json.loads(FIXTURE.read_text())
    payload = {**fixture, "model": args.model}
    fixture_hash = hashlib.sha256(
        json.dumps(fixture, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    latencies: list[float] = []
    responses: list[dict] = []
    endpoint = args.base_url.rstrip("/") + "/v1/systemone"
    for _ in range(args.repetitions):
        latency, response = request(endpoint, payload)
        validate_response(response)
        latencies.append(latency)
        responses.append(response)

    result = {
        "schema_version": 1,
        "measured_at": datetime.now(timezone.utc).isoformat(),
        "endpoint": endpoint,
        "model_request": args.model,
        "fixture_sha256": fixture_hash,
        "repetitions": args.repetitions,
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
            "machine": platform.machine(),
        },
        "latency_ms": {
            "samples": latencies,
            "median": statistics.median(latencies),
            "min": min(latencies),
            "max": max(latencies),
        },
        "response_examples": responses[:2],
    }
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

