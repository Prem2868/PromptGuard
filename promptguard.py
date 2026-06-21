#!/usr/bin/env python3
"""
PromptGuard - CLI entry point
Detects prompt injection, jailbreak attempts, and LLM security risks in text input.

Author: Pramod Jogdand (PremLabs Security Lab)
"""

import argparse
import json
import sys

from detectors.injection_patterns import scan_injection
from detectors.jailbreak_patterns import scan_jailbreak
from detectors.encoding_checks import scan_encoding


def analyze(text: str) -> dict:
    """Run all detectors on a piece of text and return an aggregated risk report."""
    findings = []
    findings.extend(scan_injection(text))
    findings.extend(scan_jailbreak(text))
    findings.extend(scan_encoding(text))

    # Risk score: sum of individual finding weights, capped at 10
    score = min(10, sum(f["weight"] for f in findings))

    return {
        "text_preview": text[:80] + ("..." if len(text) > 80 else ""),
        "risk_score": score,
        "flagged": score >= 4,
        "findings": findings,
    }


def print_human_readable(report: dict) -> None:
    if not report["findings"]:
        print("[OK] No suspicious patterns detected. Risk score: 0/10")
        return

    status = "RISK DETECTED" if report["flagged"] else "LOW RISK"
    print(f"[!] {status} \u2014 Score: {report['risk_score']}/10")
    for f in report["findings"]:
        print(f"  Category: {f['category']}")
        print(f"  Matched pattern: \"{f['matched']}\"")
        print(f"  Weight: {f['weight']}")
        print("  ---")
    if report["flagged"]:
        print("Recommendation: Flag for manual review before sending to LLM.")


def main():
    parser = argparse.ArgumentParser(
        description="PromptGuard - detect prompt injection & jailbreak attempts in text input."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", type=str, help="A single string to scan.")
    group.add_argument("--file", type=str, help="A file with one prompt per line to scan.")
    parser.add_argument("--json", action="store_true", help="Output results as JSON.")

    args = parser.parse_args()

    reports = []
    if args.text:
        reports.append(analyze(args.text))
    elif args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as fh:
                lines = [line.strip() for line in fh if line.strip()]
        except OSError as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
        for line in lines:
            reports.append(analyze(line))

    if args.json:
        print(json.dumps(reports if args.file else reports[0], indent=2))
    else:
        for report in reports:
            print_human_readable(report)
            print()

    # Exit code 1 if anything was flagged — useful for CI pipelines
    if any(r["flagged"] for r in reports):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
