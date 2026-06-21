"""
Detects prompt injection attempts — patterns where input text tries to
override, ignore, or manipulate the system/model instructions.
"""

import re

_INJECTION_PATTERNS = [
    (r"ignore (all |any )?(previous|prior|above|preceding) instructions?", "Instruction Override", 5),
    (r"disregard (all |any )?(previous|prior|above) (instructions?|rules?|prompts?)", "Instruction Override", 5),
    (r"forget (everything|all|your instructions)", "Instruction Override", 4),
    (r"you are now\b", "Role Override", 3),
    (r"new instructions?:", "Instruction Injection", 4),
    (r"system\s*:\s*", "Fake System Tag", 4),
    (r"assistant\s*:\s*", "Fake Assistant Tag", 3),
    (r"reveal (your |the )?(system prompt|instructions|rules)", "Prompt Leakage Attempt", 5),
    (r"what (are|is) your (system prompt|instructions)", "Prompt Leakage Attempt", 4),
    (r"repeat (the words|everything) above", "Prompt Leakage Attempt", 4),
    (r"print (your |the )?(initial|original) prompt", "Prompt Leakage Attempt", 4),
    (r"act as if (you have no|there are no) (restrictions|rules|filters)", "Restriction Bypass", 5),
    (r"bypass (your |all )?(filters?|restrictions?|safety)", "Restriction Bypass", 5),
]

_COMPILED = [(re.compile(p, re.IGNORECASE), cat, w) for p, cat, w in _INJECTION_PATTERNS]


def scan_injection(text: str) -> list:
    findings = []
    for pattern, category, weight in _COMPILED:
        match = pattern.search(text)
        if match:
            findings.append({"category": category, "matched": match.group(0), "weight": weight})
    return findings
