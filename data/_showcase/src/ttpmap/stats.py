"""Uncertainty and significance: paired bootstrap, exact McNemar, Holm correction, Wilson interval."""
from __future__ import annotations

from typing import Dict, List, Sequence

import numpy as np
from scipy.stats import binomtest

BOOT_N = 10_000
BOOT_SEED = 20261114


def bootstrap_ci(x: np.ndarray, n_boot: int = BOOT_N, seed: int = BOOT_SEED, level: float = 0.95) -> Dict[str, float]:
    """Percentile CI of the mean of a per-sentence vector (unit of resampling = sentence)."""
    x = np.asarray(x, dtype=float)
    if len(x) == 0:
        return {"mean": np.nan, "lo": np.nan, "hi": np.nan, "n": 0}
    rng = np.random.default_rng(seed)
    means = x[rng.integers(0, len(x), (n_boot, len(x)))].mean(1)
    a = (1 - level) / 2
    return {"mean": float(x.mean()), "lo": float(np.quantile(means, a)), "hi": float(np.quantile(means, 1 - a)), "n": int(len(x))}


def paired_bootstrap(a: np.ndarray, b: np.ndarray, n_boot: int = BOOT_N, seed: int = BOOT_SEED) -> Dict[str, float]:
    """Paired bootstrap of mean(a - b) with a percentile 95% CI and a two-sided bootstrap p-value."""
    d = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    rng = np.random.default_rng(seed)
    bs = d[rng.integers(0, len(d), (n_boot, len(d)))].mean(1)
    return {"delta": float(d.mean()), "lo": float(np.quantile(bs, 0.025)), "hi": float(np.quantile(bs, 0.975)),
            "p_boot": float(min(1.0, 2 * min((bs <= 0).mean(), (bs >= 0).mean())))}


def mcnemar_exact(a: np.ndarray, b: np.ndarray) -> Dict[str, float]:
    """Exact two-sided McNemar on two 0/1 hit vectors. b_ = a right & b wrong, c_ = a wrong & b right."""
    a = np.asarray(a).astype(bool); b = np.asarray(b).astype(bool)
    b_ = int((a & ~b).sum()); c_ = int((~a & b).sum())
    p = binomtest(b_, b_ + c_, 0.5).pvalue if b_ + c_ else 1.0
    return {"b": b_, "c": c_, "p": float(p)}


def holm(pvalues: Sequence[float]) -> List[float]:
    """Holm step-down adjusted p-values, returned in the input order."""
    p = np.asarray(pvalues, dtype=float); m = len(p)
    order = np.argsort(p); adj = np.empty(m); running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (m - rank) * p[i]); adj[i] = min(1.0, running)
    return adj.tolist()


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a proportion."""
    if n == 0:
        return (np.nan, np.nan)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)
