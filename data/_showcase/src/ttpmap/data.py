"""Loading of splits, label space and saved model outputs. Nothing here writes to the project data."""
from __future__ import annotations

import ast
import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from . import CLS_DIR, DATA, EVIDENCE, MATCH_DIR, SEEDS

log = logging.getLogger("ttpmap.data")
REVOKED = {"t1060", "t1107", "t1151", "t1188"}   # revoked ids whose description duplicates the active id (Exp_2.1 CELL 2)


def norm_text(s: str) -> str:
    """Lower-case and collapse whitespace (duplicate detection)."""
    return re.sub(r"\s+", " ", str(s).lower()).strip()


def dedup_against(df: pd.DataFrame, ref_texts, near: bool = True, jaccard: float = 0.90):
    """Drop rows of `df` whose text is an exact (norm_text) or near duplicate (token-set Jaccard >= `jaccard`, tokens [a-z0-9]+
    of the lower-cased text, the A6 definition) of any reference text. Returns (kept rows, {"exact": n, "near": m})."""
    from scipy import sparse
    ref = [str(t) for t in ref_texts]; txt = df["text"].astype(str).tolist()
    exact = np.isin([norm_text(t) for t in txt], list({norm_text(t) for t in ref}))
    near_m = np.zeros(len(txt), bool)
    if near and len(txt) and len(ref):
        toks = lambda s: set(re.findall(r"[a-z0-9]+", s.lower()))
        A, B = [toks(t) for t in txt], [toks(t) for t in ref]; voc = {w: i for i, w in enumerate(sorted(set().union(*A, *B)))}
        def mat(sets):
            r = [i for i, s in enumerate(sets) for _ in s]; c = [voc[w] for s in sets for w in s]
            return sparse.csr_matrix((np.ones(len(c)), (r, c)), shape=(len(sets), len(voc)))
        inter = (mat(A) @ mat(B).T).tocoo(); la = np.array([len(s) for s in A]); lb = np.array([len(s) for s in B])
        jac = inter.data / (la[inter.row] + lb[inter.col] - inter.data)
        near_m[np.unique(inter.row[jac >= jaccard])] = True
        near_m &= ~exact
    return df[~(exact | near_m)].copy(), {"exact": int(exact.sum()), "near": int(near_m.sum())}


def text_sha(s: str) -> str:
    return hashlib.sha256(str(s).encode("utf-8")).hexdigest()


def file_sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _labels(x) -> List[str]:
    return sorted({str(t).strip().upper() for t in (ast.literal_eval(x) if isinstance(x, str) else x)})


def load_split(name: str) -> pd.DataFrame:
    """Columns: text, labels (sorted unique upper-case ids). Train = tram slice of combined_train.csv, exact-text dedup."""
    if name == "train":
        df = pd.read_csv(DATA / "combined_train.csv")
        df = df[df["source_dataset"] == "tram"].rename(columns={"text1": "text"})
        df = df.drop_duplicates(subset=["text"])
    elif name in ("dev", "test"):
        df = pd.read_csv(DATA / f"tram_{name}.tsv", sep="\t").rename(columns={"text1": "text"})
    else:
        raise ValueError(name)
    df = df[["text", "labels"]].reset_index(drop=True)
    df["labels"] = df["labels"].apply(_labels)
    return df


def load_descriptions() -> pd.DataFrame:
    """ATT&CK descriptions in matching-space order (733 rows): columns ttp (upper), description."""
    d = pd.read_csv(DATA / "ttp-desc-mappings.csv", sep="\t")
    d["ttp"] = d["ttp"].str.lower().str.strip()
    d["description"] = (d["description"].fillna("").str.replace(r"\s+", " ", regex=True)
                        .str.replace(r"\bcitation:\s*", "", regex=True).str.strip())
    d = d.drop_duplicates("ttp")
    d = d[~d["ttp"].isin(REVOKED)].reset_index(drop=True)
    d["ttp"] = d["ttp"].str.upper()
    return d


@dataclass
class Space:
    """Everything needed to score systems: splits, label space, gold matrices, saved outputs."""
    train: pd.DataFrame
    dev: pd.DataFrame
    test: pd.DataFrame
    labels: List[str]
    Y: Dict[str, np.ndarray]
    train_count: np.ndarray
    seen: np.ndarray
    svm_raw: Dict[str, np.ndarray] = field(default_factory=dict)
    cls_raw: Dict[Tuple[str, int], Dict[str, np.ndarray]] = field(default_factory=dict)
    cls_cols: Dict[Tuple[str, int], np.ndarray] = field(default_factory=dict)
    cls_meta: Dict[Tuple[str, int], dict] = field(default_factory=dict)
    matcher_raw: Dict[int, Dict[str, np.ndarray]] = field(default_factory=dict)
    matcher_zero_test: np.ndarray | None = None
    vec: object = None
    svm: object = None

    @property
    def L(self) -> int:
        return len(self.labels)

    @property
    def seen_idx(self) -> np.ndarray:
        return np.where(self.seen)[0]

    @property
    def lab2i(self) -> Dict[str, int]:
        return {l: i for i, l in enumerate(self.labels)}


@lru_cache(maxsize=1)
def build_space() -> Space:
    """Load splits and every saved prediction file; refit the deterministic TF-IDF + LinearSVC (its scores were never saved)."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.multiclass import OneVsRestClassifier
    from sklearn.svm import LinearSVC

    tr, dv, te = load_split("train"), load_split("dev"), load_split("test")
    labels = load_descriptions()["ttp"].tolist()
    lab2i = {l: i for i, l in enumerate(labels)}

    def toY(df):
        Y = np.zeros((len(df), len(labels)), dtype=bool)
        for i, ys in enumerate(df["labels"]):
            for y in ys:
                Y[i, lab2i[y]] = True
        return Y
    Y = {"train": toY(tr), "dev": toY(dv), "test": toY(te)}
    tc = Y["train"].sum(0)
    S = Space(train=tr, dev=dv, test=te, labels=labels, Y=Y, train_count=tc, seen=tc > 0)
    assert (len(tr), len(dv), len(te), S.L, int(S.seen.sum())) == (3468, 604, 725, 733, 180), "unexpected data shape"

    S.vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True).fit(tr["text"])
    S.svm = OneVsRestClassifier(LinearSVC(C=1.0, random_state=42)).fit(S.vec.transform(tr["text"]), Y["train"][:, S.seen_idx].astype(int))
    S.svm_raw = {sp: S.svm.decision_function(S.vec.transform(d["text"])) for sp, d in (("dev", dv), ("test", te))}

    for tag in ("roberta", "secbert"):
        for s in SEEDS:
            p = CLS_DIR / f"{tag}_pw_s{s}"
            cols = np.array([lab2i[str(c).upper()] for c in np.load(p / "mlb_classes.npy", allow_pickle=True)])
            S.cls_cols[tag, s] = cols
            S.cls_raw[tag, s] = {"dev": np.load(p / "dev_probs.npy"), "test": np.load(p / "test_probs.npy")}
            S.cls_meta[tag, s] = json.load(open(p / "metrics.json"))
            assert (np.load(p / "test_labels.npy").astype(bool) == Y["test"][:, cols]).all(), "saved gold labels differ from rebuilt gold"
    for s in SEEDS:
        S.matcher_raw[s] = {sp: np.load(MATCH_DIR / f"ft20_s{s}" / f"{sp}_scores.npy") for sp in ("dev", "test")}
    S.matcher_zero_test = np.load(MATCH_DIR / "zeroshot" / "test_scores.npy")
    log.info("space built: %d labels, %d seen", S.L, int(S.seen.sum()))
    return S


def load_tactics() -> pd.DataFrame:
    """Technique id -> name, tactics, from ATT&CK v12.1 STIX (downloaded copy in the evidence pack) or the shipped table."""
    from . import RESULTS
    shipped = RESULTS / "tables" / "techniques.parquet"
    if shipped.exists():
        return pd.read_parquet(shipped)
    stix = json.load(open(EVIDENCE / "external" / "enterprise-attack-12.1.json", encoding="utf-8"))
    rows = {}
    for o in stix["objects"]:
        if o.get("type") != "attack-pattern":
            continue
        ext = [x for x in o.get("external_references", []) if x.get("source_name") == "mitre-attack"]
        if not ext:
            continue
        tid = ext[0]["external_id"].upper()
        if tid in rows and (o.get("revoked") or o.get("x_mitre_deprecated")):
            continue
        rows[tid] = {"id": tid, "name": o["name"],
                     "tactics": sorted(p["phase_name"] for p in o.get("kill_chain_phases", []) if p.get("kill_chain_name") == "mitre-attack")}
    return pd.DataFrame(rows.values())
