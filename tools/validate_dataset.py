#!/usr/bin/env python3
import json
from collections import Counter
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "dataset/dataset_v0.1.jsonl"
rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
assert len(rows) == 250
assert len({r["sample_id"] for r in rows}) == 250
assert Counter(r["label"] for r in rows) == {"benign": 150, "attack": 100}
print("category_counts", dict(Counter(r["category"] for r in rows)))
assert Counter(r["category"] for r in rows)["B02"] == 25
assert Counter(r["category"] for r in rows)["B03"] == 25
assert Counter(r["transformation"] for r in rows)["multilingual"] == 9
for row in rows:
    assert row["expected_behavior"] == ("flag" if row["label"] == "attack" else "do_not_flag")
print({"records": len(rows), "labels": dict(Counter(r["label"] for r in rows)), "categories": dict(Counter(r["category"] for r in rows)), "transformations": dict(Counter(r["transformation"] for r in rows))})
