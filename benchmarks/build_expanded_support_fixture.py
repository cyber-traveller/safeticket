"""Build a larger labeled support fixture from authored paraphrase templates.

This is evaluation-only data. It must not be added to model-training files.
"""
import json
from pathlib import Path

from benchmarks.build_blind_support_fixture import cases as base_cases

ROOT = Path(__file__).resolve().parents[1]

PREFIXES = {
    "billing": ["For accounting, ", "Could you please ", "I need help to "],
    "shipping": ["Could you please ", "I would like you to ", "Please help me "],
    "returns": ["Could you please ", "I need help to ", "Please help me "],
    "access": ["Could you please ", "I need help to ", "Please help me "],
    "review": ["Please have a human ", "I need support to ", "Could someone "],
}


def expanded_cases():
    original = base_cases()
    extra = []
    for index, case in enumerate(original, start=1):
        prefix = PREFIXES[case["team"]][index % 3]
        text = case["ticket"]
        if text.endswith("."):
            text = text[:-1]
        extra.append({
            "id": f"e{index:03d}",
            "ticket": prefix + text[0].lower() + text[1:] + ".",
            "team": case["team"],
            "source_case": case["id"],
        })
    return original + extra


if __name__ == "__main__":
    out = ROOT / "benchmarks" / "support_expanded_v1.json"
    out.write_text(json.dumps(expanded_cases(), indent=2) + "\n")
    print(json.dumps({"path": str(out), "cases": len(expanded_cases())}, indent=2))
