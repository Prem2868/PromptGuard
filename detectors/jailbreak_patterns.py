"""
Detects jailbreak attempts — roleplay/persona-based patterns commonly used
to coax a model into bypassing its safety behavior (e.g. DAN-style prompts).
"""

import re

_JAILBREAK_PATTERNS = [
    (r"\bDAN\b.*(mode|jailbreak)", "DAN-style Jailbreak", 6),
    (r"do anything now", "DAN-style Jailbreak", 6),
    (r"pretend (you are|to be) (an? )?(unfiltered|uncensored|unrestricted)", "Unfiltered Persona", 6),
    (r"respond as (an? )?(AI|assistant) with no (restrictions|filters|rules)", "Unfiltered Persona", 6),
    (r"roleplay as .* (with no|without) (rules|restrictions|filters|limits)", "Unfiltered Roleplay", 5),
    (r"hypothetically,? if you (had no|could ignore)", "Hypothetical Bypass", 4),
    (r"this is (just |only )?(a |for )?(fiction|story|simulation)", "Fictional Framing Bypass", 3),
    (r"stay in character no matter what", "Persistent Persona Lock", 4),
    (r"two ais? (talking|debating)", "Dual-Persona Bypass", 4),
    (r"opposite day", "Inversion Bypass", 3),
    (r"developer mode", "Developer Mode Bypass", 5),
]

_COMPILED = [(re.compile(p, re.IGNORECASE), cat, w) for p, cat, w in _JAILBREAK_PATTERNS]


def scan_jailbreak(text: str) -> list:
    """Scan text for jailbreak/persona-bypass patterns. Returns a list of finding dicts."""
    findings = []
    for pattern, category, weight in _COMPILED:
        match = pattern.search(text)
        if match:
            findings.append({"category": category, "matched": match.group(0), "weight": weight})
    return findings
