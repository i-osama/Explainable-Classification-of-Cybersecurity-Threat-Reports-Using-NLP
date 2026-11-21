"""Explanation utilities: word units, masking, and faithfulness measures for a sentence classifier.

Units are whitespace-delimited words, exactly as in the stored SHAP run (Exp_3_0b): a hidden word is replaced by the
model's mask token and whitespace is kept; a removed word is deleted with its trailing whitespace.
"""
from __future__ import annotations

import re
from typing import Callable, Dict, List, Sequence, Set, Tuple

import numpy as np

UNIT_RE = re.compile(r"(\s*)(\S+)(\s*)")
Parts = List[Tuple[str, str, str]]


def split_units(text: str) -> Parts:
    """(leading whitespace, word, trailing whitespace) triples that tile the text exactly."""
    parts = [m.groups() for m in UNIT_RE.finditer(text)]
    assert parts and "".join("".join(p) for p in parts) == text, "unit split does not reproduce the text"
    return parts


def mask_words(parts: Parts, hide: Set[int], mask_token: str) -> str:
    return "".join(l + (mask_token if i in hide else w) + t for i, (l, w, t) in enumerate(parts))


def keep_only(parts: Parts, keep: Set[int], mask_token: str) -> str:
    return "".join(l + (w if i in keep else mask_token) + t for i, (l, w, t) in enumerate(parts))


def remove_words(parts: Parts, hide: Set[int], original: str) -> str:
    s = "".join(l + w + t for i, (l, w, t) in enumerate(parts) if i not in hide)
    return s.rstrip() if (len(parts) - 1) in hide and not original[-1:].isspace() else s


def order_by_attribution(values: Sequence[float]) -> List[int]:
    """Word indices from most to least positive attribution (stable)."""
    return np.argsort(-np.asarray(values, dtype=float), kind="stable").tolist()


def faithfulness_curves(parts: Parts, order: List[int], score_fn: Callable[[List[str]], np.ndarray], mask_token: str,
                        max_k: int) -> Dict[str, np.ndarray]:
    """Deletion and insertion curves for one sentence and one word order.

    deletion[k]  = score with the first k words of ``order`` masked (k = 0 is the original sentence).
    insertion[k] = score with ONLY the first k words of ``order`` visible (k = 0 is the fully masked sentence).
    ``score_fn`` maps a list of texts to a 1-D array of scores for the explained label.
    """
    K = min(max_k, len(parts))
    texts = [mask_words(parts, set(order[:k]), mask_token) for k in range(K + 1)]
    texts += [keep_only(parts, set(order[:k]), mask_token) for k in range(K + 1)]
    sc = np.asarray(score_fn(texts), dtype=float)
    return {"deletion": sc[:K + 1], "insertion": sc[K + 1:]}


def comprehensiveness_sufficiency(parts: Parts, order: List[int], score_fn: Callable[[List[str]], np.ndarray], mask_token: str,
                                  k: int) -> Dict[str, float]:
    """ERASER-style measures with the top-k words as the rationale (mask-token variant).

    comprehensiveness = s(full) - s(full without rationale)   (higher = the rationale mattered)
    sufficiency       = s(full) - s(rationale only)           (lower = the rationale alone is enough)
    """
    r = set(order[:k])
    full, wo, only = score_fn(["".join("".join(p) for p in parts), mask_words(parts, r, mask_token), keep_only(parts, r, mask_token)])
    return {"comprehensiveness": float(full - wo), "sufficiency": float(full - only)}
