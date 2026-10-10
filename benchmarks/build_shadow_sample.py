"""Build a fixed, stratified sample for bounded shadow-model evaluation."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "benchmarks" / "support_expanded_v1.json"
OUT = ROOT / "benchmarks" / "support_shadow_sample_v2.json"
PER_TEAM = 20


def main():
    cases = json.loads(SOURCE.read_text())
    selected = []
    counts = {}
    for case in cases:
        team = case["team"]
        if counts.get(team, 0) < PER_TEAM:
            selected.append(case)
            counts[team] = counts.get(team, 0) + 1
    OUT.write_text(json.dumps(selected, indent=2) + "\n")
    print(json.dumps({"path": str(OUT), "cases": len(selected), "by_team": counts}, indent=2))


if __name__ == "__main__":
    main()
