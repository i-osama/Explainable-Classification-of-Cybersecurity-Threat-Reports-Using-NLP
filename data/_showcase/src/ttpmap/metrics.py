"""The single metric implementation used for every system.

Conventions
-----------
* ``scores``: float array (n_sentences, n_labels); higher = more likely.
* ``Y``: bool array of the same shape; True where the label is gold.
* Ranking: descending score, ties broken by the LOWER label index (stable sort).
* A sentence whose gold labels are all outside a model's label set simply never scores a hit.
* Label granularity: exact id (sub-technique T1059.001 is not its parent T1059).
"""
from __future__ import annotations

from typing import Dict, Literal

import numpy as np

F1Variant = Literal["notebook", "seen_test", "all_test"]


def rank_topk(scores: np.ndarray, k: int) -> np.ndarray:
    """Indices of the k best labels per row; deterministic under ties."""
    return np.argsort(-scores, axis=1, kind="stable")[:, :k]


def hit_at_1(scores: np.ndarray, Y: np.ndarray) -> np.ndarray:
    """Per-sentence 0/1 vector: is the top-1 label a gold label? Mean of it = P@1."""
    top = rank_topk(scores, 1)[:, 0]
    return Y[np.arange(len(Y)), top].astype(float)


def precision_at_k(scores: np.ndarray, Y: np.ndarray, k: int) -> np.ndarray:
    """Per-sentence (number of gold labels in the top k) / k."""
    return np.take_along_axis(Y, rank_topk(scores, k), axis=1).sum(1) / float(k)


def rr_at_k(scores: np.ndarray, Y: np.ndarray, k: int = 3) -> np.ndarray:
    """Per-sentence reciprocal rank of the first gold label inside the top k; 0 if none. Mean = MRR@k."""
    hits = np.take_along_axis(Y, rank_topk(scores, k), axis=1)
    first = hits.argmax(1) + 1
    return np.where(hits.any(1), 1.0 / first, 0.0)


def recall_at_k_micro(scores: np.ndarray, Y: np.ndarray, k: int) -> float:
    """Gold (sentence, label) pairs found in the top k / all gold pairs (the notebooks' "R@k")."""
    return float(np.take_along_axis(Y, rank_topk(scores, k), axis=1).sum() / Y.sum())


def recall_at_k_per_sample(scores: np.ndarray, Y: np.ndarray, k: int) -> float:
    """Mean over sentences of hits/|gold| (the definition printed in Nguyen et al., App. D.1)."""
    hits = np.take_along_axis(Y, rank_topk(scores, k), axis=1).sum(1)
    return float((hits / np.maximum(Y.sum(1), 1)).mean())


def apply_threshold(scores: np.ndarray, thr: float) -> np.ndarray:
    """Multi-label decision: score >= thr; a row with no label gets its arg-max label (never predict nothing)."""
    P = scores >= thr
    empty = P.sum(1) == 0
    P[np.where(empty)[0], scores[empty].argmax(1)] = True
    return P


def _prf(P: np.ndarray, Y: np.ndarray) -> Dict[str, float]:
    tp = int((P & Y).sum()); fp = int((P & ~Y).sum()); fn = int((~P & Y).sum())
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    return {"precision": p, "recall": r, "f1": 2 * p * r / (p + r) if p + r else 0.0}


def f1_per_label(P: np.ndarray, Y: np.ndarray) -> np.ndarray:
    """Label-wise F1 with zero_division = 0."""
    tp = (P & Y).sum(0).astype(float); fp = (P & ~Y).sum(0); fn = (~P & Y).sum(0)
    den = 2 * tp + fp + fn
    return np.where(den > 0, 2 * tp / np.maximum(den, 1), 0.0)


def f1_scores(P: np.ndarray, Y: np.ndarray, seen: np.ndarray, variant: F1Variant) -> Dict[str, float]:
    """Micro and macro F1 in one of three explicit variants.

    P, Y: bool (n, n_labels) in the FULL label space; ``seen``: bool (n_labels,) = label occurs in training.

    * ``notebook``  : only the columns of labels seen in training are scored. Gold labels never seen in training are
      ignored (not counted as misses). Macro over seen labels that occur in this split. This is what the original
      notebooks report.
    * ``seen_test`` : micro counts unseen gold labels as false negatives; macro over seen labels that occur in this split.
    * ``all_test``  : micro as in ``seen_test``; macro over ALL labels that occur in this split (unseen labels score 0).
    """
    present = Y.sum(0) > 0
    f = f1_per_label(P, Y)
    if variant == "notebook":
        m = _prf(P[:, seen], Y[:, seen]); macro = f[present & seen].mean()
    elif variant == "seen_test":
        m = _prf(P, Y); macro = f[present & seen].mean()
    elif variant == "all_test":
        m = _prf(P, Y); macro = f[present].mean()
    else:
        raise ValueError(variant)
    return {"micro_f1": m["f1"], "micro_precision": m["precision"], "micro_recall": m["recall"], "macro_f1": float(macro),
            "n_macro_labels": int((present & seen).sum() if variant != "all_test" else present.sum())}


def ece(conf: np.ndarray, correct: np.ndarray, bins: int = 10):
    """Expected calibration error with equal-width bins; returns (ece, per-bin table rows)."""
    edges = np.linspace(0, 1, bins + 1); e = 0.0; rows = []
    for i, (a, b) in enumerate(zip(edges[:-1], edges[1:])):
        m = (conf >= a) & (conf <= b) if i == 0 else (conf > a) & (conf <= b)
        if m.any():
            e += m.mean() * abs(correct[m].mean() - conf[m].mean())
        rows.append({"bin_lo": a, "bin_hi": b, "n": int(m.sum()), "mean_conf": float(conf[m].mean()) if m.any() else np.nan,
                     "accuracy": float(correct[m].mean()) if m.any() else np.nan})
    return float(e), rows
