"""Rebuild every system's score matrix in the 733-label matching space from SAVED predictions.
Only the TF-IDF+SVM is refit (deterministic, seconds; its scores were never saved)."""
import json
import numpy as np, pandas as pd
from functools import lru_cache
from common import DATA, CLS, MATCH, SEEDS, parse_labels, load_split

DROP = {"t1060", "t1107", "t1151", "t1188"}


class Space:
    pass


@lru_cache(maxsize=1)
def build():
    S = Space()
    comb = pd.read_csv(DATA / "combined_train.csv")
    tr = comb[comb["source_dataset"] == "tram"].rename(columns={"text1": "text"}).reset_index(drop=True)
    tr["labels"] = tr["labels"].apply(parse_labels)
    tr = tr.drop_duplicates(subset=["text"]).reset_index(drop=True)
    assert len(tr) == 3468
    S.train, S.dev, S.test = tr, load_split("dev"), load_split("test")

    desc = pd.read_csv(DATA / "ttp-desc-mappings.csv", sep="\t")
    desc["ttp"] = desc["ttp"].str.lower().str.strip()
    desc = desc.drop_duplicates("ttp")
    desc = desc[~desc["ttp"].isin(DROP)].reset_index(drop=True)
    S.LABELS = [t.upper() for t in desc["ttp"]]
    S.L = len(S.LABELS); S.lab2i = {l: i for i, l in enumerate(S.LABELS)}
    assert S.L == 733

    def toY(df):
        Y = np.zeros((len(df), S.L), dtype=bool)
        for i, ys in enumerate(df["labels"]):
            for y in ys: Y[i, S.lab2i[y]] = True
        return Y
    S.Ytr, S.Ydev, S.Yte = toY(S.train), toY(S.dev), toY(S.test)
    S.train_count = S.Ytr.sum(0)
    S.SEEN = S.train_count > 0
    S.seen_idx = np.where(S.SEEN)[0]
    assert S.SEEN.sum() == 180

    # ---- SVM (refit; Exp_1_4 CELL 6 / Exp_2.1 CELL 8 settings)
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.multiclass import OneVsRestClassifier
    from sklearn.svm import LinearSVC
    S.vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True).fit(S.train["text"])
    S.svm = OneVsRestClassifier(LinearSVC(C=1.0, random_state=42)).fit(S.vec.transform(S.train["text"]), S.Ytr[:, S.seen_idx].astype(int))
    S.svm_raw = {sp: S.svm.decision_function(S.vec.transform(d["text"])) for sp, d in (("dev", S.dev), ("test", S.test))}

    # ---- classifiers (saved probabilities)
    S.cls_raw, S.cls_cols, S.cls_meta = {}, {}, {}
    for tag in ("roberta", "secbert"):
        for s in SEEDS:
            p = CLS / f"{tag}_pw_s{s}"
            classes = [str(c).upper() for c in np.load(p / "mlb_classes.npy", allow_pickle=True)]
            S.cls_cols[tag, s] = np.array([S.lab2i[c] for c in classes])
            S.cls_raw[tag, s] = {"dev": np.load(p / "dev_probs.npy"), "test": np.load(p / "test_probs.npy")}
            S.cls_meta[tag, s] = json.load(open(p / "metrics.json"))
            # saved gold labels must equal our rebuilt Y on the 180 seen columns
            assert (np.load(p / "test_labels.npy").astype(bool) == S.Yte[:, S.cls_cols[tag, s]]).all()

    # ---- matcher (saved scores over 733 labels)
    S.m_raw = {s: {"dev": np.load(MATCH / f"ft20_s{s}" / "dev_scores.npy"), "test": np.load(MATCH / f"ft20_s{s}" / "test_scores.npy")} for s in SEEDS}
    S.m_zero = np.load(MATCH / "zeroshot" / "test_scores.npy")
    assert S.m_zero.shape == (725, 733)
    return S


def to_full(Sc, cols, L, fill=np.nan):
    F = np.full((Sc.shape[0], L), fill); F[:, cols] = Sc; return F


def zrow(F):
    m = np.nanmean(F, axis=1, keepdims=True); s = np.nanstd(F, axis=1, keepdims=True) + 1e-9
    return np.nan_to_num((F - m) / s, nan=0.0)


def Y_of(S, sp):
    return S.Ydev if sp == "dev" else S.Yte


def components(S, sp, mode="avg", seed=None):
    """z-scored components in the notebook order ['matcher','svm','roberta','secbert'].
    mode='avg'      : matcher 3-seed avg, classifiers 3-seed avg  (thesis 'seed-averaged')
    mode='nb_seed'  : matcher seed s, classifiers 3-seed avg      (notebook Exp_2.1 CELL 11 'one matcher seed at a time')
    mode='paired'   : matcher seed s, roberta seed s, secbert seed s
    """
    L = S.L
    Z = {}
    Z["svm"] = zrow(to_full(S.svm_raw[sp], S.seen_idx, L))
    for tag in ("roberta", "secbert"):
        if mode == "paired":
            Z[tag] = zrow(to_full(S.cls_raw[tag, seed][sp], S.cls_cols[tag, seed], L))
        else:
            Z[tag] = zrow(np.mean([to_full(S.cls_raw[tag, s][sp], S.cls_cols[tag, s], L) for s in SEEDS], axis=0))
    if mode == "avg":
        Z["matcher"] = zrow(np.mean([S.m_raw[s][sp] for s in SEEDS], axis=0))
    else:
        Z["matcher"] = zrow(S.m_raw[seed][sp])
    return Z


ORDER = ["matcher", "svm", "roberta", "secbert"]


def fuse(Z, w):
    return sum(wi * Z[n] for wi, n in zip(w, ORDER))


def rank_full(Sc, cols, L):
    """Classifier scores placed in the 733 space; never-seen labels get -1e9 (cannot be ranked)."""
    return to_full(Sc, cols, L, fill=-1e9)
