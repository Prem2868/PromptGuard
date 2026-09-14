#!/usr/bin/env python3
"""Reproducible PromptGuard-AI-001 benchmark runner."""
from __future__ import annotations
import argparse, hashlib, json, platform, subprocess, sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from promptguard import analyze
from detectors.injection_patterns import scan_injection
from detectors.jailbreak_patterns import scan_jailbreak
from detectors.encoding_checks import scan_encoding


def metric(rows, threshold):
    tp = sum(r["expected"] and r["score"] >= threshold for r in rows)
    tn = sum(not r["expected"] and r["score"] < threshold for r in rows)
    fp = sum(not r["expected"] and r["score"] >= threshold for r in rows)
    fn = sum(r["expected"] and r["score"] < threshold for r in rows)
    n = len(rows)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {"n": n, "tp": tp, "tn": tn, "fp": fp, "fn": fn,
            "accuracy": (tp + tn) / n if n else 0.0,
            "precision": precision, "recall": recall,
            "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0.0,
            "fpr": fp / (fp + tn) if fp + tn else 0.0,
            "fnr": fn / (fn + tp) if fn + tp else 0.0}


def git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="dataset/heldout_test.jsonl")
    ap.add_argument("--output", default="results/baseline_v0.1.json")
    ap.add_argument("--thresholds", nargs="*", type=int, default=[2, 3, 4, 5, 6])
    args = ap.parse_args()
    dataset_path = ROOT / args.dataset
    records = [json.loads(line) for line in dataset_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    rows = []
    for rec in records:
        report = analyze(rec["text"])
        rows.append({"sample_id": rec["sample_id"], "category": rec["category"], "transformation": rec["transformation"], "language": rec["language"], "expected": rec["expected_behavior"] == "flag", "score": report["risk_score"], "findings": report["findings"]})

    def grouped(key, threshold=4):
        groups = defaultdict(list)
        for row in rows: groups[row[key]].append(row)
        return {name: metric(items, threshold) for name, items in sorted(groups.items())}

    detector_counts = {}
    for name, fn in [("injection", scan_injection), ("jailbreak", scan_jailbreak), ("encoding", scan_encoding)]:
        detector_counts[name] = {"samples_with_findings": sum(bool(fn(r["text"])) for r in records), "finding_count": sum(len(fn(r["text"])) for r in records)}

    source_hash = hashlib.sha256((ROOT / "dataset/dataset_v0.1.jsonl").read_bytes()).hexdigest()
    result = {
        "experiment": {"dataset_version": "PromptGuard-AI-001-v0.1", "dataset_file": str(args.dataset), "dataset_hash_sha256": source_hash, "git_commit": git_commit(), "baseline_reference_commit": "3fa7b7b", "python_version": platform.python_version(), "platform": platform.platform(), "dependency_versions": {"python": platform.python_version()}, "threshold": 4, "experiment_timestamp": datetime.now(timezone.utc).isoformat()},
        "overall": metric(rows, 4), "by_detector": detector_counts, "by_category": grouped("category"), "by_transformation": grouped("transformation"), "by_language": grouped("language"), "by_threshold": {str(t): metric(rows, t) for t in args.thresholds},
        "raw_results": rows,
    }
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "dataset": len(records), "overall": result["overall"], "sha256": source_hash}, indent=2))

if __name__ == "__main__": main()
