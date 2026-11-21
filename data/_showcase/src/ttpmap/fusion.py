"""Score normalisation, late fusion and DEV-ONLY weight selection.

Fusion rule (Exp_2.1 CELL 8): each component's scores are z-scored per sentence over the labels the component knows;
labels it does not know get 0; the fused score is the weighted sum. Component order is fixed:
``ORDER = ("matcher", "svm", "roberta", "secbert")`` so the thesis weights (3, 1, 1, 1) mean matcher 3, the rest 1.
"""
from __future__ import annotations

import itertools
import math
from functools import reduce
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np

from . import SEEDS
from .data import Space
from .metrics import hit_at_1, rr_at_k

ORDER: Tuple[str, ...] = ("matcher", "svm", "roberta", "secbert")
THESIS_WEIGHTS: Tuple[int, ...] = (3, 1, 1, 1)


class LeakageError(RuntimeError):
    """Raised when a tuning function is handed anything other than the dev split."""


def to_full(scores: np.ndarray, cols: np.ndarray, L: int, fill: float = np.nan) -> np.ndarray:
    F = np.full((scores.shape[0], L), fill); F[:, cols] = scores
    return F


def zrow(F: np.ndarray) -> np.ndarray:
    """Per-row z-score over the non-NaN labels; NaN (unknown label) -> 0."""
    m = np.nanmean(F, axis=1, keepdims=True); s = np.nanstd(F, axis=1, keepdims=True) + 1e-9
    return np.nan_to_num((F - m) / s, nan=0.0)


def rank_space(scores: np.ndarray, cols: np.ndarray, L: int) -> np.ndarray:
    """Classifier scores in the full label space; labels the model never saw can never be ranked first."""
    return to_full(scores, cols, L, fill=-1e9)


def components(S: Space, split: str, mode: str = "avg", seed: int | None = None) -> Dict[str, np.ndarray]:
    """z-scored component matrices.

    mode ``avg``     : matcher = mean of 3 seeds, classifiers = mean probability of 3 seeds ("seed-averaged").
    mode ``nb_seed`` : matcher = one seed, classifiers = 3-seed mean (the notebook's per-seed fusion).
    mode ``paired``  : matcher, RoBERTa and SecBERT all from the same seed ("seed-paired").
    """
    L = S.L
    Z = {"svm": zrow(to_full(S.svm_raw[split], S.seen_idx, L))}
    for tag in ("roberta", "secbert"):
        if mode == "paired":
            Z[tag] = zrow(to_full(S.cls_raw[tag, seed][split], S.cls_cols[tag, seed], L))
        else:
            Z[tag] = zrow(np.mean([to_full(S.cls_raw[tag, s][split], S.cls_cols[tag, s], L) for s in SEEDS], axis=0))
    Z["matcher"] = zrow(np.mean([S.matcher_raw[s][split] for s in SEEDS], axis=0)) if mode == "avg" else zrow(S.matcher_raw[seed][split])
    return Z


def fuse(Z: Dict[str, np.ndarray], w: Sequence[float]) -> np.ndarray:
    return sum(wi * Z[n] for wi, n in zip(w, ORDER))


def coarse_grid() -> List[Tuple[int, ...]]:
    """{0,1,2,3}^4 without the all-zero setting: 255 settings (Exp_2.1 CELL 8)."""
    return [w for w in itertools.product([0, 1, 2, 3], repeat=4) if sum(w)]


def wide_grid() -> List[Tuple[int, ...]]:
    """{0,1,2,3,4,6,8}^4 reduced by gcd: 1,711 distinct settings (Exp_2.1 CELL 9)."""
    seen, out = set(), []
    for w in itertools.product([0, 1, 2, 3, 4, 6, 8], repeat=4):
        g = reduce(math.gcd, w)
        if g == 0:
            continue
        w = tuple(x // g for x in w)
        if w not in seen:
            seen.add(w); out.append(w)
    return out


def select_weights(Z_dev: Dict[str, np.ndarray], Y_dev: np.ndarray, grid: Iterable[Tuple[int, ...]], *, split: str,
                   sentence_ids: Sequence[str] | None = None, forbidden_ids: Sequence[str] = ()) -> Tuple[Tuple[int, ...], Tuple[float, float]]:
    """Pick fusion weights. Objective: DEV MRR@3 (4 d.p.), tie-break DEV P@1; first strictly better setting wins.

    Guard: ``split`` must be the string "dev", and if ``sentence_ids`` are given none may be in ``forbidden_ids``
    (pass the test-set ids there). Violations raise LeakageError.
    """
    if split != "dev":
        raise LeakageError(f"weights may be tuned on dev only, got split={split!r}")
    if sentence_ids is not None and set(sentence_ids) & set(forbidden_ids):
        raise LeakageError("test sentence ids reached a tuning function")
    best = None
    for w in grid:
        Sc = fuse(Z_dev, w)
        key = (round(float(rr_at_k(Sc, Y_dev, 3).mean()), 4), round(float(hit_at_1(Sc, Y_dev).mean()), 4))
        if best is None or key > best[0]:
            best = (key, tuple(w))
    return best[1], best[0]


def select_threshold(scores_dev: np.ndarray, Y_dev: np.ndarray, grid: Sequence[float], *, split: str) -> float:
    """Global decision threshold maximising DEV micro-F1 over the model's own label columns (first maximum wins)."""
    if split != "dev":
        raise LeakageError(f"thresholds may be tuned on dev only, got split={split!r}")
    def mf(t):
        P = scores_dev >= t
        tp = (P & Y_dev).sum(); d = 2 * tp + (P & ~Y_dev).sum() + (~P & Y_dev).sum()
        return 2.0 * tp / d if d else 0.0
    return float(grid[int(np.argmax([mf(t) for t in grid]))])
