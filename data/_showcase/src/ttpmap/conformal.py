"""Split-conformal prediction sets for multi-label technique ranking (prereg 18).

Two set rules, both calibrated on DEV only:
  score threshold : nonconformity s_i = -min_{y in Y_i} f(x_i, y); set C(x) = {y : f(x, y) >= tau}, tau = -q
  rank threshold  : nonconformity s_i = worst (1-based) rank of a gold label; set C(x) = top-k labels, k = q
with q = the ceil((n+1)(1-alpha))-th smallest nonconformity (n = calibration rows with at least one gold label).
If that index exceeds n the set is every label with a finite score. Marginal coverage of ALL gold labels is then
>= 1 - alpha for exchangeable test rows (Angelopoulos and Bates, arXiv 2107.07511), with one exception: NaN scores are
treated as -inf and are never inside a set, so a row whose gold label has no score (a label outside a classifier's
space) can never be covered. Such rows count as misses; report their share beside the coverage.
Rank ties are broken by label index (stable sort), so the rank rule depends on label order inside ties; the score rule
(primary in prereg 18) includes every tied label and has no such dependence.
"""
from __future__ import annotations

import math
from typing import Dict

import numpy as np

from .fusion import LeakageError


def _clean(scores: np.ndarray) -> np.ndarray:
    return np.where(np.isnan(scores), -np.inf, scores.astype(float))


def _positions(scores: np.ndarray) -> np.ndarray:
    """0-based rank position of every label per row (stable: ties broken by label index)."""
    order = np.argsort(-_clean(scores), axis=1, kind="stable")
    pos = np.empty_like(order); rows = np.arange(order.shape[0])[:, None]
    pos[rows, order] = np.arange(order.shape[1])[None, :]
    return pos


def _quantile_index(n: int, alpha: float) -> int:
    return math.ceil((n + 1) * (1 - alpha))


def _check(split: str) -> None:
    if split != "dev":
        raise LeakageError(f"conformal calibration must use the dev split, got {split!r}")


def calibrate_threshold(scores: np.ndarray, Y: np.ndarray, alpha: float, *, split: str) -> float:
    """tau for the score-threshold rule; -inf means the full label set."""
    _check(split)
    keep = Y.any(axis=1); F = _clean(scores)[keep]; G = Y[keep]
    s = np.sort(-np.where(G, F, np.inf).min(axis=1))
    k = _quantile_index(len(s), alpha)
    return -np.inf if k > len(s) else float(-s[k - 1])


def calibrate_rank(scores: np.ndarray, Y: np.ndarray, alpha: float, *, split: str) -> int:
    """k for the rank-threshold rule (set = top-k); the label count L means the full label set."""
    _check(split)
    keep = Y.any(axis=1); P = _positions(scores)[keep] + 1; G = Y[keep]
    s = np.sort(np.where(G, P, 0).max(axis=1))
    k = _quantile_index(len(s), alpha)
    return int(scores.shape[1]) if k > len(s) else int(s[k - 1])


def sets_by_threshold(scores: np.ndarray, tau: float) -> np.ndarray:
    F = _clean(scores)
    return np.isfinite(F) & (F >= tau)


def sets_by_rank(scores: np.ndarray, k: int) -> np.ndarray:
    return np.isfinite(_clean(scores)) & (_positions(scores) < k)


def per_row(sets: np.ndarray, Y: np.ndarray) -> Dict[str, np.ndarray]:
    """Per-row arrays for bootstrapping: covered_all / covered_any (NaN for rows without gold labels), size."""
    has = Y.any(axis=1); miss = (Y & ~sets).any(axis=1); hit = (Y & sets).any(axis=1)
    return {"covered_all": np.where(has, ~miss, np.nan).astype(float), "covered_any": np.where(has, hit, np.nan).astype(float),
            "size": sets.sum(axis=1).astype(float)}


def set_metrics(sets: np.ndarray, Y: np.ndarray) -> Dict[str, float]:
    r = per_row(sets, Y); size = r["size"]
    return {"coverage_all": float(np.nanmean(r["covered_all"])), "coverage_any": float(np.nanmean(r["covered_any"])),
            "size_mean": float(size.mean()), "size_median": float(np.median(size)), "size_p90": float(np.percentile(size, 90)),
            "empty_rate": float((size == 0).mean())}
