"""Evaluate the experimental domain-aware banking endpoint."""
import json
import os
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = Path(os.environ.get("SAFETICKET_BANKING_FIXTURE", str(ROOT / "benchmarks" / "banking77_dev_v1.json"))).resolve()
OUT = Path(os.environ.get("SAFETICKET_BANKING_OUT", str(ROOT / "outputs" / "banking-taxonomy-dev-v1.json")))
URL = os.environ.get("SAFETICKET_BANKING_URL", "http://127.0.0.1:8009/v1/banking/intent")


def main():
    rows = []
    for case in json.loads(FIXTURE.read_text()):
        request = urllib.request.Request(URL, data=json.dumps({"ticket": case["ticket"]}).encode(), headers={"content-type": "application/json"})
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.load(response)
        predicted = result.get("legacy_team")
        rows.append({**case, "predicted_domain": result.get("domain"), "predicted_legacy_team": predicted, "correct": predicted == case["team"], "result": result})
    summary = {"correct": sum(row["correct"] for row in rows), "total": len(rows), "accuracy": sum(row["correct"] for row in rows) / len(rows), "by_expected": Counter(row["team"] for row in rows)}
    OUT.write_text(json.dumps({"fixture": str(FIXTURE), "summary": summary, "rows": rows}, indent=2) + "\n")
    print(json.dumps(summary, indent=2, default=dict))
    for row in rows:
        if not row["correct"]:
            print(row["source_category"], row["team"], "=>", row["predicted_domain"], "|", row["ticket"])


if __name__ == "__main__":
    main()
