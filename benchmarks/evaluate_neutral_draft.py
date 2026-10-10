"""Diagnostic for the pending neutral review queue; not an official benchmark."""
import json
import statistics
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "benchmarks" / "neutral_review_queue_v1.json"
OUT = ROOT / "outputs" / "neutral-draft-diagnostic-v1.json"


def main():
    queue = json.loads(QUEUE.read_text())
    rows = []
    for case in queue["cases"]:
        request = urllib.request.Request(
            "http://127.0.0.1:8009/v1/support/decide",
            data=json.dumps({"ticket": case["text"]}).encode(),
            headers={"content-type": "application/json"},
        )
        start = time.perf_counter()
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.load(response)
        decision = result.get("decision", {})
        predicted = decision.get("team") if decision.get("action") == "route" else "review"
        rows.append({**case, "predicted_team": predicted, "predicted_action": decision.get("action"), "reason": decision.get("reason"), "correct_against_draft": predicted == case["proposed_team"], "latency_ms": (time.perf_counter() - start) * 1000})
    latencies = [r["latency_ms"] for r in rows]
    report = {
        "status": "draft_diagnostic_only",
        "official_benchmark": False,
        "label_status": queue["status"],
        "summary": {
            "correct_against_proposed_labels": sum(r["correct_against_draft"] for r in rows),
            "total": len(rows),
            "median_latency_ms": round(statistics.median(latencies), 1),
        },
        "rows": rows,
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
