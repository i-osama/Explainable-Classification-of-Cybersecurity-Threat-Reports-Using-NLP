"""Stacked (learned) late fusion, Q1 plan Task 4 / prereg 15.

One logistic regression scores every (sentence, label) pair from 7 features; it is fitted on DEV only.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence

import numpy as np

from .fusion import LeakageError, ORDER
from .metrics import rr_at_k

N_FEATURES = 7
FEATURES = ("z_matcher", "z_svm", "z_roberta", "z_secbert", "log1p_train_count", "seen", "log_matcher_rank")
SEED = 20261114


def pair_features(Z: Dict[str, np.ndarray], train_count: np.ndarray) -> np.ndarray:
    """(n, L, 7): the four z-scored components (ORDER), log1p(train support), seen flag, log of the matcher's rank (1 = top)."""
    n, L = Z["matcher"].shape
    rank = np.argsort(np.argsort(-Z["matcher"], axis=1), axis=1) + 1
    tc = np.broadcast_to(np.asarray(train_count, float)[None, :], (n, L))
    return np.stack([Z[k] for k in ORDER] + [np.log1p(tc), (tc > 0).astype(float), np.log(rank)], axis=-1)


def _rows(X: np.ndarray, Y: np.ndarray, idx: np.ndarray, n_neg: int, rng: np.random.Generator):
    xs, ys = [], []
    for i in idx:
        pos = np.where(Y[i])[0]; neg = np.where(~Y[i])[0]
        neg = rng.choice(neg, size=min(n_neg, len(neg)), replace=False)
        xs.append(X[i, np.concatenate([pos, neg])]); ys.append(np.r_[np.ones(len(pos)), np.zeros(len(neg))])
    return np.concatenate(xs), np.concatenate(ys)


@dataclass
class Stacker:
    model: object
    C: float
    cv: Dict[float, float] = field(default_factory=dict)

    def score(self, X: np.ndarray) -> np.ndarray:
        n, L, F = X.shape
        return self.model.decision_function(X.reshape(-1, F)).reshape(n, L)


def _fit(Xr, yr, C):
    from sklearn.linear_model import LogisticRegression
    return LogisticRegression(C=C, solver="lbfgs", max_iter=2000).fit(Xr, yr)             # L2 is the default penalty


def fit_stacker(X: np.ndarray, Y: np.ndarray, *, split: str, C_grid: Sequence[float] = (0.01, 0.1, 1, 10), folds: int = 5,
                seed: int = SEED, n_neg: int = 50) -> Stacker:
    """C by mean dev-fold MRR@3 (KFold by sentence, shuffled with `seed`), then a final fit on all dev sentences."""
    if split != "dev":
        raise LeakageError(f"the stacker may be fitted on dev only, got split={split!r}")
    from sklearn.model_selection import KFold
    keep = np.where(Y.any(1))[0]
    kf = list(KFold(n_splits=folds, shuffle=True, random_state=seed % (2 ** 32)).split(keep))
    cv: Dict[float, float] = {}
    for C in C_grid:
        rng = np.random.default_rng(seed); s: List[float] = []
        for tr, va in kf:
            m = _fit(*_rows(X, Y, keep[tr], n_neg, rng), C); n, L, F = X[keep[va]].shape
            s.append(float(rr_at_k(m.decision_function(X[keep[va]].reshape(-1, F)).reshape(n, L), Y[keep[va]], 3).mean()))
        cv[C] = float(np.mean(s))
    best = max(C_grid, key=lambda c: (round(cv[c], 4), -C_grid.index(c)))
    return Stacker(model=_fit(*_rows(X, Y, keep, n_neg, np.random.default_rng(seed)), best), C=best, cv=cv)
