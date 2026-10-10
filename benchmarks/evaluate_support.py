"""Authored development smoke suite; no training or generalization claims."""
import json
from pathlib import Path
from safeticket.client import SystemOneClient
from safeticket.support import QUESTIONS, decide


def main():
    cases = json.loads(Path(__file__).with_name("support_cases.json").read_text())
    rows = []
    with SystemOneClient("http://127.0.0.1:8008") as client:
        for case in cases:
            result = client.system_one({"state": case["ticket"], "model": "kev-latest", "questions": QUESTIONS})
            decision = decide(result["answers"])
            raw = result["answers"]["team"]["choice"]
            rows.append({**case, "raw_choice": raw, "decision": decision, "answers": result["answers"]})
    accepted = [r for r in rows if r["decision"]["action"] == "route"]
    report = {"suite": "authored-development-smoke-v1", "limitations": "16 authored examples, no held-out production data; threshold fixed at 0.70; no tuning or training performed.",
              "count": len(rows), "raw_route_accuracy": sum(r["raw_choice"] == r["team"] for r in rows)/len(rows),
              "automatic_routes": len(accepted), "coverage": len(accepted)/len(rows),
              "automatic_route_errors": sum(r["decision"]["team"] != r["team"] for r in accepted),
              "review_required_cases": sum(r["team"] == "review" for r in rows),
              "review_required_caught": sum(r["team"] == "review" and r["decision"]["action"] == "human_review" for r in rows), "rows": rows}
    output = Path("outputs/support-evaluation.json")
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k:v for k,v in report.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()
