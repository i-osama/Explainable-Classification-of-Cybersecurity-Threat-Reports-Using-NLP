"""Input perturbations for the robustness and shortcut test (Q1 plan Task 3, prereg 14).

Every perturbation is a pure function of (text, sentence index), so Colab can regenerate the exact same inputs.
"""
from __future__ import annotations

import re
from typing import Callable, Dict, List, Sequence

import numpy as np

ENT, IOC = "[ENT]", "[IOC]"
MIN_LEN = 4
TYPO_RATE, TYPO_SEED = 0.05, 20261114


def load_entity_names(objects: Sequence[dict], kinds: Sequence[str]) -> List[str]:
    """Names and aliases of non-revoked STIX objects of the given types, minus names shorter than 4 characters
    and names that occur (word boundary, case-insensitive) in any technique name. Longest first."""
    tech = " | ".join(o["name"] for o in objects if o.get("type") == "attack-pattern")
    names = set()
    for o in objects:
        if o.get("type") in kinds and not o.get("revoked") and not o.get("x_mitre_deprecated"):
            names.update([o["name"], *o.get("aliases", []), *o.get("x_mitre_aliases", [])])
    keep = [n for n in names if len(n) >= MIN_LEN and not re.search(rf"(?<!\w){re.escape(n)}(?!\w)", tech, re.I)]
    return sorted(keep, key=lambda n: (-len(n), n))


def _names_regex(names: Sequence[str]) -> re.Pattern:
    return re.compile(r"(?<!\w)(?:" + "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True)) + r")(?!\w)")


def mask_entities(text: str, names: Sequence[str], token: str = ENT, _cache: Dict = {}) -> str:
    key = tuple(names)
    if key not in _cache:
        _cache[key] = _names_regex(names)
    return _cache[key].sub(token, text)


_IOC_PATTERNS = [
    r"\bhxxps?://\S+|\bhttps?://[^\s,;\"')]+",
    r"\b[A-Za-z]:\\[^\s,;\"']+",
    r"%[A-Za-z_]+%\\[^\s,;\"']+",
    r"\b(?:HKLM|HKCU|HKCR|HKU|HKEY_[A-Z_]+)\\[^\s,;\"']+",
    r"(?<![\w.])/(?:etc|tmp|usr|var|bin|sbin|home|dev|opt|root|Library|Users|private)/[^\s,;\"']*",
    r"\b[a-fA-F0-9]{64}\b|\b[a-fA-F0-9]{40}\b|\b[a-fA-F0-9]{32}\b",
    r"\bCVE-\d{4}-\d{4,7}\b",
    r"\b(?:\d{1,3}(?:\.|\[\.\])){3}\d{1,3}\b",
    r"\b(?:[a-z0-9-]+(?:\.|\[\.\]))+(?:com|net|org|info|biz|ru|cn|io|top|xyz|club|online|site|tk|cc|me|co|uk|de|in|us|kr|jp|ir|su|pw|ws)\b",
]
_IOC = [re.compile(p, re.I) for p in _IOC_PATTERNS]


def mask_iocs(text: str, token: str = IOC) -> str:
    for p in _IOC:
        text = p.sub(token, text)
    return text


def typo(text: str, rate: float, seed: int) -> str:
    """Swap two adjacent letters inside a share `rate` of the words longer than 3 letters; deterministic for a seed."""
    if rate <= 0:
        return text
    rng = np.random.default_rng(seed); parts = re.split(r"(\W+)", text); out = []
    for w in parts:
        if len(w) > 3 and w.isalpha() and rng.random() < rate:
            j = int(rng.integers(0, len(w) - 1)); w = w[:j] + w[j + 1] + w[j] + w[j + 2:]
        out.append(w)
    return "".join(out)


def lower_nopunct(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", text.lower())).strip()


def perturbations(objects: Sequence[dict]) -> Dict[str, Callable[[str, int], str]]:
    """The five pre-registered perturbations; each takes (text, sentence index)."""
    groups = load_entity_names(objects, ("intrusion-set",)); soft = load_entity_names(objects, ("malware", "tool"))
    return {"mask_groups": lambda t, i: mask_entities(t, groups),
            "mask_software": lambda t, i: mask_entities(t, soft),
            "mask_iocs": lambda t, i: mask_iocs(t),
            "typo_5pct": lambda t, i: typo(t, TYPO_RATE, TYPO_SEED + i),
            "lower_nopunct": lambda t, i: lower_nopunct(t)}
