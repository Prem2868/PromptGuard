"""
Detects encoding-based obfuscation — attempts to hide malicious instructions
inside base64, hex, or unicode-escaped payloads to slip past keyword filters.
"""

import base64
import re

_BASE64_RE = re.compile(r"(?:[A-Za-z0-9+/]{20,}={0,2})")
_HEX_RE = re.compile(r"(?:\\x[0-9a-fA-F]{2}){6,}")
_UNICODE_ESCAPE_RE = re.compile(r"(?:\\u[0-9a-fA-F]{4}){4,}")

_SUSPICIOUS_KEYWORDS = [
    "ignore", "system prompt", "jailbreak", "bypass", "override", "disregard",
]


def _try_decode_base64(candidate: str) -> str:
    try:
        decoded = base64.b64decode(candidate + "==", validate=False)
        return decoded.decode("utf-8", errors="ignore")
    except Exception:
        return ""


def scan_encoding(text: str) -> list:
    """Scan text for encoded payloads that decode to suspicious content."""
    findings = []

    for match in _BASE64_RE.finditer(text):
        candidate = match.group(0)
        decoded = _try_decode_base64(candidate)
        if decoded and any(kw in decoded.lower() for kw in _SUSPICIOUS_KEYWORDS):
            findings.append({
                "category": "Base64 Obfuscation",
                "matched": candidate[:40] + ("..." if len(candidate) > 40 else ""),
                "weight": 5,
            })

    if _HEX_RE.search(text):
        findings.append({
            "category": "Hex Escape Obfuscation",
            "matched": _HEX_RE.search(text).group(0)[:40],
            "weight": 3,
        })

    if _UNICODE_ESCAPE_RE.search(text):
        findings.append({
            "category": "Unicode Escape Obfuscation",
            "matched": _UNICODE_ESCAPE_RE.search(text).group(0)[:40],
            "weight": 3,
        })

    return findings
