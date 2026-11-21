"""Replay data and uncertainty logic for the TTP explainer.

Formulas are copied from notebooks 05/06 (zrow, to_full, fuse, UNIT_RE) and prereg 18/19
(split-conformal score rule, top-1 minus top-2 margin). Nothing here is tuned on TEST.
"""
from __future__ import annotations

import ast
import json
import math
import os
import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

ORDER = ("matcher", "svm", "roberta", "secbert")
W4 = (3, 1, 1, 1)
SEEDS = (42, 43, 44)
ALPHAS = (0.10, 0.20)
COVS = (0.5, 0.8, 0.9)
UNIT_RE = re.compile(r"(\s*)(\S+)(\s*)")  # SHAP unit = whitespace-delimited word, same as the stored run

# facts shown in the limits panel: (text, thesis_numbers ids). Values are read from the json, never typed here.
LIMITS = [
    ("Fusion P@1 (seed-averaged, test)", ["B13a"]),
    ("RoBERTa probabilities are over-confident (ECE)", ["G7.ece.roberta"]),
    ("Fusion P@1 when the rarest gold label is unseen / has train support 1-4", ["G4.fusion.unseen", "G4.fusion.1_4"]),
    ("Matcher P@1 for train support 1-4 (better than fusion there)", ["G4.matcher.1_4"]),
    ("Sentences where the explained model and the fusion disagree on top-1", ["E4"]),
    ("Faithfulness of SHAP order: deletion AUC (lower = better) / insertion AUC (higher = better)", ["E5.del_auc.shap", "E5.ins_auc.shap"]),
    ("Human agreement, Krippendorff alpha nominal / ordinal (no usable agreement)", ["D1", "D2"]),
    ("Fusion SHAP vs RoBERTa SHAP, deletion-test drop difference, seed 42, 100 sentences (logit-z units)", ["T2.full_fusion_shap"]),
]


def env_flag(name):
    """True only for 1/true/yes/on (any case): TTPMAP_DEMO=0 must not switch demo mode on."""
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


# ---------- score maths ----------
def zrow(F):
    m = np.nanmean(F, axis=1, keepdims=True)
    s = np.nanstd(F, axis=1, keepdims=True) + 1e-9
    return np.nan_to_num((F - m) / s, nan=0.0)


def to_full(scores, cols, L):
    F = np.full((scores.shape[0], L), np.nan)
    F[:, cols] = scores
    return F


def fuse(Z, w=W4):
    return sum(wi * Z[n] for wi, n in zip(w, ORDER) if wi)


def split_units(text):
    return [m.groups() for m in UNIT_RE.finditer(text)]


def margin(S):
    top2 = -np.sort(-S, axis=1)[:, :2]
    return top2[:, 0] - top2[:, 1]


def conformal_tau(S_dev, Y_dev, alpha):
    """Prereg 18, score rule: nonconformity = -(lowest score of a gold label); set = labels with score >= tau."""
    nc = -np.where(Y_dev, S_dev, np.inf).min(1)
    n = len(nc)
    k = math.ceil((n + 1) * (1 - alpha))
    return -np.inf if k > n else float(-np.sort(nc)[k - 1])  # k > n: full label set


def dev_threshold(m_dev, target):
    """Prereg 19 rule (ttpmap.selective.dev_threshold_for_coverage): an order statistic of the dev margins, no interpolation.
    np.quantile interpolates between order statistics and moved test coverage at 0.9 from 0.9145 to 0.9117."""
    c = np.sort(np.asarray(m_dev, float))[::-1]
    return float(c[max(1, int(round(target * len(c)))) - 1])


@dataclass
class Calib:
    """Thresholds fitted on DEV scores only."""
    tau: dict
    thr: dict

    @classmethod
    def fit(cls, S_dev, Y_dev):
        m = margin(S_dev)
        return cls({a: conformal_tau(S_dev, Y_dev, a) for a in ALPHAS}, {c: dev_threshold(m, c) for c in COVS})


def assess(S_row, cal, alpha=0.10):
    """Top-5, conformal set, margin and triage tier (0 high .. 2 low) for one score row."""
    order = np.argsort(-S_row, kind="stable")
    m = float(S_row[order[0]] - S_row[order[1]])
    tier = 0 if m >= cal.thr[0.5] else 1 if m >= cal.thr[0.9] else 2
    return {"order": order, "top5": order[:5], "set": [int(i) for i in order if S_row[i] >= cal.tau[alpha]], "margin": m, "tier": tier}


# ---------- new text and new labelled data (report and teach modes) ----------
SENT_RE = re.compile(r"(?<=[.!?])\s+|\n+")


def split_sentences(text, max_n=300):
    """Sentences of a pasted report: split at . ! ? + space and at line breaks; pieces under 3 words are dropped."""
    out = [s.strip() for s in SENT_RE.split(text or "") if len(s.split()) >= 3]
    return out[:max_n]


def _ids(s):
    s = str(s).strip()
    if s.startswith("["):
        return sorted({str(t).strip().upper() for t in ast.literal_eval(s)})
    return sorted({t.upper() for t in re.split(r"[,;\s]+", s) if t})


def validate_rows(rows, labels, first_line=1):
    """Keep (sentence, ids) rows whose IDs are all in the label space; an error message per rejected row."""
    known, ok, errs = set(labels), [], []
    for n, (text, ids) in enumerate(rows, first_line):
        bad = [i for i in ids if i not in known]
        if bad:
            errs.append(f"line {n}: unknown technique ID(s) {', '.join(bad)} (not in the ATT&CK v12.1 label space of this app)")
        elif not ids or len(text.split()) < 3:
            errs.append(f"line {n}: needs at least one technique ID and a sentence of 3+ words")
        else:
            ok.append((text, ids))
    return ok, errs


def parse_labelled(text, labels):
    """Lines 'T1486: sentence' or 'T1059, T1105: sentence' -> ([(sentence, ids)], [error messages])."""
    rows, errs = [], []
    for n, line in enumerate((text or "").splitlines(), 1):
        if not line.strip():
            continue
        head, sep, body = line.partition(":")
        if not sep or not re.fullmatch(r"\s*T\d{4}(\.\d{3})?(\s*[,;\s]\s*T\d{4}(\.\d{3})?)*\s*", head, re.I):
            errs.append(f"line {n}: expected 'T1234: sentence' or 'T1234, T1059.001: sentence'")
            continue
        ok, e = validate_rows([(body.strip(), _ids(head))], labels, n)
        rows += ok
        errs += e
    return rows, errs


def _csv(data):
    import io
    df = pd.read_csv(io.BytesIO(data))
    tcol = next((c for c in df.columns if str(c).lower() in ("text", "text1", "sentence")), df.columns[0])
    return df, tcol


def read_upload(name, data):
    """Text of an uploaded report: .csv -> its text column (one sentence per row), else the file decoded as UTF-8."""
    if str(name).lower().endswith(".csv"):
        df, tcol = _csv(data)
        return "\n".join(df[tcol].dropna().astype(str))
    return data.decode("utf-8-sig", errors="replace")


def read_labelled_csv(data):
    """[(sentence, ids)] from a CSV with a text column and a labels column (list literal or IDs split by , ; or space)."""
    df, tcol = _csv(data)
    lcol = next(c for c in df.columns if str(c).lower() in ("labels", "label", "technique", "techniques", "ttp"))
    return [(str(t).strip(), _ids(l)) for t, l in zip(df[tcol], df[lcol]) if pd.notna(t) and pd.notna(l)]


def _fit_svm(texts, Y):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.multiclass import OneVsRestClassifier
    from sklearn.svm import LinearSVC

    seen = np.where(Y.sum(0) > 0)[0]
    vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True).fit(texts)
    return vec, OneVsRestClassifier(LinearSVC(C=1.0, random_state=42)).fit(vec.transform(texts), Y[:, seen].astype(int)), seen


def svm_scores(art, texts):
    """Raw SVM decision values over the full label space; labels the SVM never saw get -inf."""
    F = to_full(art["svm"].decision_function(art["vec"].transform(list(texts))), art["seen_idx"], len(art["labels"]))
    return np.where(np.isnan(F), -np.inf, F)


def retrain_svm(art, rows):
    """Same SVM recipe as load_replay, refit on train + the added (sentence, ids) rows. Nothing is written to disk."""
    lab2i = {l: i for i, l in enumerate(art["labels"])}
    Yn = np.zeros((len(rows), len(art["labels"])), dtype=bool)
    for r, (_, ids) in enumerate(rows):
        Yn[r, [lab2i[i] for i in ids]] = True
    texts = art["train"]["texts"] + [t for t, _ in rows]
    vec, svm, seen = _fit_svm(texts, np.vstack([art["train"]["Y"], Yn]))
    return {**art, "vec": vec, "svm": svm, "seen_idx": seen, "n_added": len(rows)}


def calib_for(art, full):
    """Dev-only calibration of a live system (full fusion W4 or classifier-only) with the SVM held in `art`."""
    d = art["dev"]
    Z = {**d["z"], "svm": zrow(to_full(art["svm"].decision_function(art["vec"].transform(d["texts"])), art["seen_idx"], len(art["labels"])))}
    if full and "matcher" not in Z:
        raise ValueError("full fusion needs the retrained matcher's dev scores")
    return Calib.fit(fuse(Z, W4 if full else (0, 1, 1, 1)), d["Y"])


# ---------- replay container ----------
@dataclass
class Replay:
    labels: list
    names: dict
    texts: list
    gold: list
    S: np.ndarray                 # fused test scores (n, L)
    cal: Calib                    # fusion calibration (dev)
    train_count: np.ndarray
    shap: dict                    # test row -> {"values": [...], "label": explained label id}
    desc: dict = field(default_factory=dict)  # label -> ATT&CK description
    drift: dict = field(default_factory=dict)
    conf: dict = field(default_factory=dict)
    sel: dict = field(default_factory=dict)
    numbers: dict = field(default_factory=dict)
    cis: dict = field(default_factory=dict)  # id -> [lo, hi] 95% CI from thesis_numbers.json
    cal_cls: Calib | None = None  # classifier-only (seed 42) calibration for live mode
    cal_full: Calib | None = None  # full fusion seed 42 (retrained matcher) calibration for live mode; None without that matcher
    fshap: dict = field(default_factory=dict)  # test row -> full-fusion SHAP of notebook 06 {"values", "label", "correct"}
    art: dict = field(default_factory=dict)  # vec, svm, seen_idx, cls_root, labels for live mode
    banner: str = ""

    def name(self, lab):
        return f"{lab} {self.names.get(lab, '')}".strip()

    def num(self, id_):
        v = self.numbers.get(id_)
        return f"[PENDING: {id_}]" if v is None else str(v)

    def flags(self, lab):
        """(level, message) warnings for a predicted label, all from the thesis' own error analysis."""
        out, i = [], self.labels.index(lab)
        sup = int(self.train_count[i])
        if sup <= 4:
            out.append(("warn", f"Rare label: only {sup} training sentence(s). Fusion P@1 for support 1-4 is {self.num('G4.fusion.1_4')} "
                                f"(matcher {self.num('G4.matcher.1_4')}); unseen: {self.num('G4.fusion.unseen')}."))
        if lab in self.drift:
            out.append(("warn", f"Not active in the latest ATT&CK: {self.drift[lab]}"))
        for gold, n in self.conf.get(lab, [])[:2]:
            out.append(("info", f"Known confusion: fusion predicted this when gold was {gold} ({n}x on test)."))
        return out

    def set_drift(self, set_idx, top):
        """(label, drift message) for conformal-set labels other than the top-1 that are not active in the latest ATT&CK."""
        return [(self.labels[j], self.drift[self.labels[j]]) for j in set_idx if self.labels[j] != top and self.labels[j] in self.drift]


# ---------- loading from the thesis folder ----------
def _find(root, *cands):
    for c in cands:
        p = Path(c) if os.path.isabs(str(c)) else Path(root) / c
        if p.exists():
            return p
    return None


def _claims(p):
    d = json.loads(Path(p).read_text(encoding="utf-8"))
    items = d if isinstance(d, list) else d.get("claims", list(d.values()))
    return [c for c in items if isinstance(c, dict) and "id" in c]


def load_numbers(p):
    return {c["id"]: c.get("display", c.get("value")) for c in _claims(p)}


def load_cis(p):
    return {c["id"]: c["ci"] for c in _claims(p) if isinstance(c.get("ci"), list) and len(c["ci"]) == 2}


def _drift_msg(r):
    fin = str(r["final_id_latest"]).strip().upper() if pd.notna(r["final_id_latest"]) else ""
    if not fin or fin == str(r["id"]).upper():  # deprecated objects have no revoked-by link: final id is the id itself
        return f"status {r['status_latest']}, no replacement"
    return f"status {r['status_latest']}, successor {fin} ({r['final_status_latest']})"


def load_drift(p):
    df = pd.read_csv(p)
    df = df[df["status_latest"].astype(str).str.lower() != "active"]
    return {r["id"].upper(): _drift_msg(r) for _, r in df.iterrows()}


def load_stix_names(p):
    """Technique names from an ATT&CK STIX bundle; a live object wins over a revoked or deprecated one with the same id."""
    best = {}
    for o in json.loads(Path(p).read_text(encoding="utf-8")).get("objects", []):
        if o.get("type") != "attack-pattern":
            continue
        tid = next((r["external_id"] for r in o.get("external_references", []) if r.get("source_name") == "mitre-attack"), None)
        if not tid or not o.get("name"):
            continue
        rank = 2 if o.get("revoked") else 1 if o.get("x_mitre_deprecated") else 0
        if tid.upper() not in best or rank < best[tid.upper()][0]:
            best[tid.upper()] = (rank, o["name"])
    return {k: v for k, (_, v) in best.items()}


def load_names(p):
    """ATT&CK technique names from the local attack_technique_names.json ({"techniques": {id: {"name": ...}}})."""
    t = json.loads(Path(p).read_text(encoding="utf-8")).get("techniques", {})
    return {k.upper(): v["name"] for k, v in t.items() if isinstance(v, dict) and v.get("name")}


def load_confusions(p):
    df = pd.read_csv(p)
    df = df[df["system"].str.startswith("Fusion") & (df["count"] >= 2)].sort_values("count", ascending=False)
    out = {}
    for _, r in df.iterrows():
        out.setdefault(r["predicted"].upper(), []).append((r["gold"].upper(), int(r["count"])))
    return out


def load_selective(p):
    df = pd.read_csv(p)
    r = df[df["system"].str.startswith("Fusion")].iloc[0]
    return {c: {"cov": float(r[f"cov{c}_test"]), "p1": float(r[f"selP@1_{c}"])} for c in COVS}


def _labels(x):
    return sorted({str(t).strip().upper() for t in ast.literal_eval(x)})


def _split(D, name):
    p = D / f"tram_{name}.tsv"
    if p.exists():
        df = pd.read_csv(p, sep="\t").rename(columns={"text1": "text"})
    elif name == "train":  # same fallback as the notebooks: the tram slice of combined_train.csv
        df = pd.read_csv(D / "combined_train.csv")
        df = df[df["source_dataset"] == "tram"].rename(columns={"text1": "text"})
    else:
        raise FileNotFoundError(p)
    df = df[["text", "labels"]].copy()
    df["labels"] = df["labels"].apply(_labels)
    return df.drop_duplicates(subset=["text"]).reset_index(drop=True) if name == "train" else df.reset_index(drop=True)


def find_bge(models):
    """bge-base-en-v1.5 config + tokenizer dir: bundled copy, TTPMAP_BGE, else the local Hugging Face cache snapshot."""
    for c in (models / "bge-base-en-v1.5", os.environ.get("TTPMAP_BGE")):
        if c and (Path(c) / "config.json").exists():
            return Path(c)
    hub = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface")) / "hub" / "models--BAAI--bge-base-en-v1.5" / "snapshots"
    return next((d for d in sorted(hub.glob("*")) if (d / "config.json").exists()), models / "bge-base-en-v1.5")


def load_replay(root):
    """Rebuild the 3-seed fusion test scores from the saved files and attach the stored SHAP. No model is run."""
    root = Path(root)
    D, CLS, MATCH = root / "Dataset", root / "Exp_1_4_run_tram_2_epoc_30", root / "run_match_1"
    MATCH2 = root / "run_match_2_saved"
    train, dev, test = (_split(D, s) for s in ("train", "dev", "test"))
    desc = pd.read_csv(D / "ttp-desc-mappings.csv", sep="\t")
    desc["ttp"] = desc["ttp"].str.lower().str.strip()
    desc["description"] = desc["description"].fillna("").str.replace(r"\s+", " ", regex=True).str.replace(r"\bcitation:\s*", "", regex=True).str.strip()
    desc = desc.drop_duplicates("ttp")
    desc = desc[~desc["ttp"].isin({"t1060", "t1107", "t1151", "t1188"})].reset_index(drop=True)
    labels = [t.upper() for t in desc["ttp"]]
    L, lab2i = len(labels), {l: i for i, l in enumerate(labels)}

    def to_Y(df):
        Y = np.zeros((len(df), L), dtype=bool)
        for i, ys in enumerate(df["labels"]):
            for y in ys:
                Y[i, lab2i[y]] = True
        return Y

    Y_train, Y_dev = to_Y(train), to_Y(dev)
    train_count = Y_train.sum(0)
    seen_idx = np.where(train_count > 0)[0]
    assert (len(train), len(dev), len(test), L, len(seen_idx)) == (3468, 604, 725, 733, 180), "unexpected data shape"

    vec, svm, seen_idx = _fit_svm(train["text"].tolist(), Y_train)  # same recipe that teach mode refits
    svm_raw = {"dev": svm.decision_function(vec.transform(dev["text"])), "test": svm.decision_function(vec.transform(test["text"]))}
    cls_raw, cols = {}, {}
    for tag in ("roberta", "secbert"):
        for s in SEEDS:
            p = CLS / f"{tag}_pw_s{s}"
            cols[tag, s] = np.array([lab2i[str(c).upper()] for c in np.load(p / "mlb_classes.npy", allow_pickle=True)])
            cls_raw[tag, s] = {"dev": np.load(p / "dev_probs.npy"), "test": np.load(p / "test_probs.npy")}

    # the retrained runs replace run_match_1 only as a full 3-seed set: mixing one retrained seed into B13a would change it
    m2_all = all((MATCH2 / f"ft20_s{s}" / "test_scores.npy").exists() for s in SEEDS)

    def mdir(s):
        return (MATCH2 if m2_all else MATCH) / f"ft20_s{s}"

    m_raw = {s: {sp: np.load(mdir(s) / f"{sp}_scores.npy") for sp in ("dev", "test")} for s in SEEDS}

    def comps(split):  # mode "avg" of the notebooks
        Z = {"svm": zrow(to_full(svm_raw[split], seen_idx, L))}
        for tag in ("roberta", "secbert"):
            Z[tag] = zrow(np.mean([to_full(cls_raw[tag, s][split], cols[tag, s], L) for s in SEEDS], axis=0))
        Z["matcher"] = zrow(np.mean([m_raw[s][split] for s in SEEDS], axis=0))
        return Z

    S, S_dev = fuse(comps("test")), fuse(comps("dev"))
    Zc = {"svm": zrow(to_full(svm_raw["dev"], seen_idx, L))}  # classifier-only seed 42, for live mode
    for tag in ("roberta", "secbert"):
        Zc[tag] = zrow(to_full(cls_raw[tag, 42]["dev"], cols[tag, 42], L))
    S_dev_cls = fuse(Zc, (0, 1, 1, 1))

    shap_p = _find(root, "Exp_3_0_shap/shap_v2_roberta_pw_s42.jsonl")
    shap = {}
    if shap_p:
        for line in shap_p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                shap[int(r["row"])] = {"values": r["shap_values"], "label": str(r["pred_label"]).upper()}

    env_res, env_num = os.environ.get("TTPMAP_RESULTS"), os.environ.get("TTPMAP_NUMBERS")
    res = _find(root, *([env_res] if env_res else []), "results", "_showcase/results")
    m42 = next((d for d in (MATCH2 / "ft20_s42", *([res / "colab" / "matcher_ft20_s42"] if res else [])) if (d / "dev_scores.npy").exists()), None)
    cal_full = None
    dev_z = {k: Zc[k] for k in ("roberta", "secbert")}  # seed 42; teach mode recalibrates with a refit SVM
    if m42 is not None:  # live full fusion = retrained matcher s42 + SVM + RoBERTa s42 + SecBERT s42, weights W4 (notebook 06)
        dev_z["matcher"] = zrow(np.load(m42 / "dev_scores.npy"))
        cal_full = Calib.fit(fuse({**Zc, "matcher": dev_z["matcher"]}), Y_dev)
    fshap = {}
    fp = res / "colab" / "fusion_shap" / "fusion_shap_full_s42.jsonl" if res else None
    if fp is not None and fp.exists():
        for line in fp.read_text(encoding="utf-8").splitlines():
            if line.strip():
                o = json.loads(line)
                fshap[int(o["row"])] = {"values": o["shap_fused"], "label": str(o["fused_top1"]).upper(), "correct": bool(o["fused_top1_correct"])}
    models = root / "models"
    nums = _find(root, *([env_num] if env_num else []), "thesis_numbers.json", "_showcase/thesis_numbers.json", *([res.parent / "thesis_numbers.json"] if res else []))
    names = {}
    r = Replay(labels, names, test["text"].tolist(), test["labels"].tolist(), S, Calib.fit(S_dev, Y_dev), train_count, shap,
               desc=dict(zip(labels, desc["description"])), cal_cls=Calib.fit(S_dev_cls, Y_dev), cal_full=cal_full, fshap=fshap,
               art={"vec": vec, "svm": svm, "seen_idx": seen_idx, "cls_root": CLS, "labels": labels, "label_texts": desc["description"].tolist(),
                    "train": {"texts": train["text"].tolist(), "Y": Y_train}, "dev": {"texts": dev["text"].tolist(), "Y": Y_dev, "z": dev_z},
                    "matcher_state": (m42 or MATCH2 / "ft20_s42") / "matcher_state.pt", "base_model": find_bge(models),
                    "label_cache": (models if models.exists() else Path(tempfile.gettempdir())) / "label_emb_ft20_s42.npy"})
    if nums:
        r.numbers, r.cis = load_numbers(nums), load_cis(nums)
    if res:
        for fn, attr, f in (("attack_drift_ids.csv", "drift", load_drift), ("confusions.csv", "conf", load_confusions), ("selective.csv", "sel", load_selective)):
            if (res / fn).exists():
                setattr(r, attr, f(res / fn))
        if (res / "confusions.csv").exists():
            c = pd.read_csv(res / "confusions.csv")
            for a, b in (("gold", "gold_name"), ("predicted", "predicted_name")):
                names.update({k.upper(): v for k, v in zip(c[a], c[b])})
    v12 = _find(root, "_evidence_pack/external/enterprise-attack-12.1.json")
    if v12:  # names of the label space's own release (v12.1) win; the others only fill gaps
        names.update(load_stix_names(v12))
    nm = _find(root, "Exp_3_0_shap/attack_technique_names.json")  # latest-release names, fetched 2026-11-11
    if nm:
        names.update({k: v for k, v in load_names(nm).items() if k not in names})
    return r
