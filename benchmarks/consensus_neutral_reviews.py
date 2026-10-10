"""Create a frozen neutral fixture only after two complete reviews agree."""
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "benchmarks" / "neutral_review_queue_v1.json"
REVIEW_A = ROOT / "benchmarks" / "neutral_review_a.json"
REVIEW_B = ROOT / "benchmarks" / "neutral_review_b.json"
OUT = ROOT / "benchmarks" / "neutral_final_v1.json"
TEAMS = {"billing", "shipping", "returns", "access", "review"}


def main():
    queue = json.loads(QUEUE.read_text())
    a = json.loads(REVIEW_A.read_text()).get("labels", {})
    b = json.loads(REVIEW_B.read_text()).get("labels", {})
    ids = [case["id"] for case in queue["cases"]]
    missing = [case_id for case_id in ids if case_id not in a or case_id not in b or not a[case_id] or not b[case_id]]
    disagreements = [case_id for case_id in ids if case_id in a and case_id in b and a[case_id] != b[case_id]]
    invalid = []
    for reviewer, labels in (("A", a), ("B", b)):
        for case_id, label in labels.items():
            if case_id not in ids:
                invalid.append(f"{reviewer}:{case_id}:unknown_case")
                continue
            if not isinstance(label, dict) or label.get("team") not in TEAMS:
                invalid.append(f"{reviewer}:{case_id}:invalid_team")
            if not isinstance(label, dict) or type(label.get("human_review")) is not bool:
                invalid.append(f"{reviewer}:{case_id}:invalid_human_review")
            if not isinstance(label, dict) or not isinstance(label.get("rationale"), str) or not label["rationale"].strip():
                invalid.append(f"{reviewer}:{case_id}:missing_rationale")
    if missing or disagreements or invalid:
        print(json.dumps({"ready": False, "missing": missing, "disagreements": disagreements, "invalid": invalid}, indent=2))
        raise SystemExit(2)
    cases = []
    for case in queue["cases"]:
        label = a[case["id"]]
        cases.append({"id": case["id"], "text": case["text"], **label})
    payload = {"status": "frozen_after_two_reviewer_agreement", "source_queue": str(QUEUE.relative_to(ROOT)), "cases": cases}
    serialized = json.dumps(payload, indent=2) + "\n"
    payload["fixture_sha256"] = hashlib.sha256(serialized.encode()).hexdigest()
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"ready": True, "cases": len(cases), "fixture_sha256": payload["fixture_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
