"""Build a development-only BANKING77 sample from the training split."""
import csv
import json
from pathlib import Path

from benchmarks.build_banking77_external import team

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "work" / "external" / "banking77" / "train.csv"
OUT = ROOT / "benchmarks" / "banking77_dev_v1.json"


def main():
    rows = []
    counts = {}
    with SOURCE.open(newline="") as handle:
        for row in csv.DictReader(handle):
            category = row["category"]
            if counts.get(category, 0) >= 2:
                continue
            counts[category] = counts.get(category, 0) + 1
            rows.append({
                "id": f"banking77-dev-{category}-{counts[category]}",
                "ticket": row["text"],
                "source_category": category,
                "team": team(category),
            })
    OUT.write_text(json.dumps(rows, indent=2) + "\n")
    print(json.dumps({"cases": len(rows), "categories": len(counts), "path": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
