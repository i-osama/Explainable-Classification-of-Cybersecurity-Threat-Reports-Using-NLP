"""Shared paths + the ONE metric implementation used for every system."""
import ast, json, os, re, sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"E:\Osamas Paper")
PACK = ROOT / "_evidence_pack"
DATA = ROOT / "Dataset"
CLS = ROOT / "Exp_1_4_run_tram_2_epoc_30"      # 30-epoch classifier runs (final)
MATCH = ROOT / "run_match_1"
SHAPD = ROOT / "Exp_3_0_shap"
SEEDS = [42, 43, 44]
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def norm_text(s):
    return re.sub(r"\s+", " ", str(s).lower()).strip()


def parse_labels(x):
    v = ast.literal_eval(x) if isinstance(x, str) else x
    return [str(t).strip().upper() for t in v]


def load_split(name):
    """dev/test from TSV; train = tram slice of combined_train.csv."""
    if name in ("dev", "test"):
        df = pd.read_csv(DATA / f"tram_{name}.tsv", sep="\t")
        df = df.rename(columns={"text1": "text"})
        df["labels"] = df["labels"].apply(parse_labels)
        return df[["text", "labels"]].reset_index(drop=True)
    raise ValueError(name)


# ---------------- metrics (single implementation) ----------------
def rank_topk(scores, k):
    """Deterministic ranking: descending score, ties broken by lower column index
    (stable argsort on negated scores)."""
    return np.argsort(-scores, axis=1, kind="stable")[:, :k]


def p_at_1(scores, Y):
    top = rank_topk(scores, 1)[:, 0]
    return Y[np.arange(len(Y)), top].astype(float)          # per-sentence hit vector


def mrr_at_k(scores, Y, k=3):
    top = rank_topk(scores, k)
    out = np.zeros(len(Y))
    for i in range(len(Y)):
        for r, c in enumerate(top[i]):
            if Y[i, c]:
                out[i] = 1.0 / (r + 1)
                break
    return out


def p_at_k(scores, Y, k=3):
    top = rank_topk(scores, k)
    return np.take_along_axis(Y, top, axis=1).sum(1) / float(k)


def r_at_k(scores, Y, k=5):
    top = rank_topk(scores, k)
    hit = np.take_along_axis(Y, top, axis=1).sum(1)
    return hit / np.maximum(Y.sum(1), 1)


def prf_micro(P, Y):
    tp = int((P & Y).sum()); fp = int((P & ~Y).sum()); fn = int((~P & Y).sum())
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return p, r, f


def f1_per_label(P, Y):
    tp = (P & Y).sum(0).astype(float); fp = (P & ~Y).sum(0); fn = (~P & Y).sum(0)
    den = 2 * tp + fp + fn
    return np.where(den > 0, 2 * tp / np.maximum(den, 1), 0.0)   # zero_division=0


def w(path, text):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
