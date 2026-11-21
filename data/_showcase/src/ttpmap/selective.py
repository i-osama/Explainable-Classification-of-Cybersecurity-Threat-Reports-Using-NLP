"""Selective prediction (abstention) for analyst triage (prereg 19; Geifman and El-Yaniv, arXiv 1705.08500).

Confidence = top-1 minus top-2 score of a system (NaN as -inf). Sentences are accepted from the most confident down;
risk at coverage j/n = share of the j accepted sentences whose top-1 label is wrong. AURC = mean risk over j = 1..n;
E-AURC = AURC minus the AURC of a perfect confidence ordering (all correct sentences first).
"""
from __future__ import annotations

from typing import Tuple

import numpy as np

from .fusion import LeakageError


def margin(scores: np.ndarray) -> np.ndarray:
    F = np.where(np.isnan(scores), -np.inf, scores.astype(float))
    top2 = -np.sort(-F, axis=1)[:, :2]
    with np.errstate(invalid="ignore"):
        m = top2[:, 0] - top2[:, 1]
    m = np.where(np.isinf(top2[:, 1]) & np.isfinite(top2[:, 0]), np.inf, m)
    return np.where(np.isfinite(top2[:, 0]), m, -np.inf)          # no finite score at all: least confident


def _conf(conf: np.ndarray) -> np.ndarray:
    c = np.asarray(conf, float)
    return np.where(np.isnan(c), -np.inf, c)                       # NaN confidence is never "most confident"


def risk_coverage(conf: np.ndarray, correct: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    order = np.argsort(-_conf(conf), kind="stable")
    err = (~np.asarray(correct, bool)[order]).astype(float); j = np.arange(1, len(err) + 1)
    return j / len(err), np.cumsum(err) / j


def aurc(conf: np.ndarray, correct: np.ndarray) -> float:
    return float(risk_coverage(conf, correct)[1].mean())


def eaurc(conf: np.ndarray, correct: np.ndarray) -> float:
    ok = np.asarray(correct, bool)
    return aurc(conf, ok) - aurc(ok.astype(float), ok)


def dev_threshold_for_coverage(conf_dev: np.ndarray, target: float, *, split: str) -> float:
    """Smallest confidence t such that the share of dev sentences with conf >= t is about `target` (accept conf >= t)."""
    if split != "dev":
        raise LeakageError(f"abstention thresholds must be fitted on the dev split, got {split!r}")
    c = np.sort(_conf(conf_dev))[::-1]
    return float(c[max(1, int(round(target * len(c)))) - 1])
