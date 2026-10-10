"""Measure SafeTicket's persistent-connection client against the same baseline fixture."""

from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

from safeticket.client import SystemOneClient
from benchmarks.run_baseline import FIXTURE, validate_response


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8008")
    parser.add_argument("--model", default="safeticket-baseline")
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    fixture = json.loads(FIXTURE.read_text())
    payload = {**fixture, "model": args.model}
    latencies: list[float] = []
    responses: list[dict] = []
    with SystemOneClient(args.base_url) as client:
        for _ in range(args.repetitions):
            start = time.perf_counter()
            response = client.system_one(payload)
            latencies.append((time.perf_counter() - start) * 1000)
            validate_response(response)
            responses.append(response)
    result = {
        "schema_version": 1,
        "variant": "safeticket-persistent-http-client",
        "endpoint": args.base_url.rstrip("/") + "/v1/systemone",
        "model_request": args.model,
        "repetitions": args.repetitions,
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

