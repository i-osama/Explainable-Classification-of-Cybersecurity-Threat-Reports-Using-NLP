"""EXTRA (fusion-SHAP question, part 2): word-level permutation SHAP of the FUSED score, same method as Exp_3_0b
(whitespace words, mask-token replacement, 40 permutations, seed 42), on CPU, inference only.

The fused score is  sum_c w_c * z_c(text)[k]  with z_c = per-row z-score of component c over its known labels,
exactly as in Exp_2.1 CELL 8.  Shapley values are linear, so SHAP(fusion) = sum_c w_c * SHAP(z_c[k]); the script
therefore explains every component in ONE permutation run (vector output) and stores the per-component values.

Components with weights on disk: SVM (refit), RoBERTa seed s, SecBERT seed s.
The matcher has NO saved weights (Exp_2.1 `train_matcher` saves only scores).  If a retrained matcher is supplied
with --matcher-dir (folder holding `matcher_state.pt` written by 09_repro/colab_train_matcher_with_save.py) it is
added with weight 3 and the result is the full (3,1,1,1) seed-paired fusion; otherwise the script explains the
classifiers-only part (0,1,1,1) and says so in every record.

usage: python x1_fusion_shap.py [--n 40] [--seed 42] [--matcher-dir DIR] [--out NAME]
"""
import argparse, json, os, re, time
import numpy as np, torch, shap
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModel
from common import PACK, CLS, SHAPD
from systems import build

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=40); ap.add_argument("--seed", type=int, default=42)
ap.add_argument("--matcher-dir", default=None); ap.add_argument("--matcher-base", default="BAAI/bge-base-en-v1.5")
ap.add_argument("--out", default=None); ap.add_argument("--selftest", action="store_true")
A = ap.parse_args()
N_PERM, SHAP_SEED, MAX_LEN, K_HIDE, N_RANDOM = 40, 42, 128, 3, 20
S = build(); L = S.L; LAB = np.array(S.LABELS)
texts = S.test["text"].tolist()
OOV = "zzzmaskzzz"                                   # TF-IDF placeholder that is guaranteed out of vocabulary
assert OOV not in S.vec.vocabulary_
torch.set_grad_enabled(False)


def zrow(F):
    m = np.nanmean(F, axis=1, keepdims=True); s = np.nanstd(F, axis=1, keepdims=True) + 1e-9
    return np.nan_to_num((F - m) / s, nan=0.0)


class Clf:
    def __init__(self, tag, seed):
        d = CLS / f"{tag}_pw_s{seed}"
        self.tok = AutoTokenizer.from_pretrained(str(d)); self.model = AutoModelForSequenceClassification.from_pretrained(str(d)).float().eval()
        self.cols = S.cls_cols[tag, seed]; self.mask = self.tok.mask_token; self.name = f"{tag}_s{seed}"
    def probs(self, tx):
        out = []
        for s in range(0, len(tx), 32):
            enc = self.tok(tx[s:s + 32], truncation=True, max_length=MAX_LEN, padding=True, return_tensors="pt")
            out.append(torch.sigmoid(self.model(**enc).logits).numpy())
        return np.concatenate(out)
    def z(self, tx):
        F = np.full((len(tx), L), np.nan); F[:, self.cols] = self.probs(tx); return zrow(F)


class Svm:
    name, mask = "svm", OOV
    def z(self, tx):
        F = np.full((len(tx), L), np.nan); F[:, S.seen_idx] = S.svm.decision_function(S.vec.transform(tx)); return zrow(F)


class MatcherC:
    """Bi-encoder of Exp_2.1 CELL 3 (CLS pooling, L2-normalised, cosine); label embeddings at max_len 256."""
    def __init__(self, base, state=None, name="matcher"):
        import pandas as pd
        from common import DATA
        self.tok = AutoTokenizer.from_pretrained(base); self.enc = AutoModel.from_pretrained(base).float().eval()
        if state is not None:
            sd = torch.load(state, map_location="cpu"); sd = {k[4:] if k.startswith("enc.") else k: v for k, v in sd.items()}
            self.enc.load_state_dict(sd)
        desc = pd.read_csv(DATA / "ttp-desc-mappings.csv", sep="\t")
        desc["ttp"] = desc["ttp"].str.lower().str.strip()
        desc["description"] = (desc["description"].fillna("").str.replace(r"\s+", " ", regex=True).str.replace(r"\bcitation:\s*", "", regex=True).str.strip())
        desc = desc.drop_duplicates("ttp"); desc = desc[~desc["ttp"].isin({"t1060", "t1107", "t1151", "t1188"})].reset_index(drop=True)
        assert [t.upper() for t in desc["ttp"]] == S.LABELS
        self.mask = self.tok.mask_token; self.name = name
        self.label_emb = self.embed(desc["description"].tolist(), 256)
    def embed(self, tx, max_len, bs=32):
        out = []
        for i in range(0, len(tx), bs):
            enc = self.tok(list(tx[i:i + bs]), padding=True, truncation=True, max_length=max_len, return_tensors="pt")
            out.append(torch.nn.functional.normalize(self.enc(**enc).last_hidden_state[:, 0].float(), dim=-1).numpy())
        return np.concatenate(out)
    def raw(self, tx): return self.embed(tx, MAX_LEN) @ self.label_emb.T
    def z(self, tx): return zrow(self.raw(tx))


if A.selftest:
    # validates the matcher scoring path against the saved zero-shot scores (needs the public bge checkpoint)
    m = MatcherC(A.matcher_base)
    Sc = m.raw(texts); ref = S.m_zero
    top = Sc.argmax(1); print(f"zero-shot P@1 recomputed {S.Yte[np.arange(725), top].mean():.4f} | saved-score P@1 {S.Yte[np.arange(725), ref.argmax(1)].mean():.4f} | "
                              f"max|score diff| {np.abs(Sc - ref).max():.2e} | same top-1 in {(top == ref.argmax(1)).mean():.1%}")
    raise SystemExit

comps = [Svm(), Clf("roberta", A.seed), Clf("secbert", A.seed)]; weights = [1.0, 1.0, 1.0]
if A.matcher_dir:
    comps.insert(0, MatcherC(A.matcher_base, os.path.join(A.matcher_dir, "matcher_state.pt"))); weights.insert(0, 3.0)
SYSTEM = ("fusion (3,1,1,1) seed-paired" if A.matcher_dir else "classifiers-only part of the fusion (0,1,1,1), NO matcher") + f", seed {A.seed}"
OUT = PACK / (A.out or ("11_fusion_shap_full.jsonl" if A.matcher_dir else "11_fusion_shap_partial.jsonl"))
METHOD = {"unit": "whitespace-delimited word", "masking": "word replaced by each model's own mask token (SVM: OOV placeholder)", "algorithm": "permutation",
          "n_perm": N_PERM, "shap_seed": SHAP_SEED, "output": "weighted sum of per-row z-scores for the fused top-1 label", "max_length": MAX_LEN,
          "system": SYSTEM, "components": [c.name for c in comps], "weights": weights}
UNIT_RE = re.compile(r"(\s*)(\S+)(\s*)")
rob = next(c for c in comps if c.name.startswith("roberta"))
stored = {}
for l in open(SHAPD / "shap_v2_roberta_pw_s42.jsonl", encoding="utf-8"):
    if l.strip():
        r = json.loads(l); stored[r["row"]] = r


def comp_scores(parts, keeps, k):
    """(len(keeps), n_components) matrix of z_c[k] for the masked variants."""
    cols = []
    for c in comps:
        tx = ["".join(lead + (word if kp else c.mask) + trail for (lead, word, trail), kp in zip(parts, keep)) for keep in keeps]
        cols.append(c.z(tx)[:, k])
    return np.stack(cols, axis=1)


def removed(parts, hide, original):
    s = "".join(l + c + t for i, (l, c, t) in enumerate(parts) if i not in hide)
    return s.rstrip() if (len(parts) - 1) in hide and not original[-1:].isspace() else s


def fused_plain(tx, k): return sum(wt * c.z(tx)[:, k] for wt, c in zip(weights, comps))


done = set()
if OUT.exists():
    for l in open(OUT, encoding="utf-8"):
        if l.strip(): done.add(json.loads(l)["row"])
order = [int(r) for r in np.random.RandomState(42).permutation(725)[:A.n]]       # same fixed sample as SHAP / human sheet
t0 = time.time()
for j, row in enumerate(order, 1):
    if row in done: continue
    text = str(texts[row]); parts = [m.groups() for m in UNIT_RE.finditer(text)]; n = len(parts)
    full = sum(wt * c.z([text])[0] for wt, c in zip(weights, comps)); k = int(full.argmax())
    f = lambda M: comp_scores(parts, np.asarray(M) > 0.5, k)
    ex = shap.Explainer(f, shap.maskers.Independent(np.zeros((1, n))), algorithm="permutation", seed=SHAP_SEED)
    sv = ex(np.ones((1, n)), max_evals=N_PERM * (2 * n + 1), batch_size=64, silent=True)[0]
    V = np.asarray(sv.values)                                   # n words x n_components
    fused = V @ np.array(weights)
    rec = {"row": row, "text": text, "units": ["".join(p) for p in parts], "fused_top1": LAB[k], "fused_score": float(full[k]),
           "gold_labels": LAB[S.Yte[row]].tolist(), "fused_top1_correct": bool(S.Yte[row, k]),
           "shap_fused": fused.tolist(), "shap_by_component": {c.name: V[:, i].tolist() for i, c in enumerate(comps)},
           "base_by_component": np.asarray(sv.base_values).tolist(),
           "additivity_error": float(abs(fused.sum() + np.asarray(sv.base_values) @ np.array(weights) - full[k])),
           "roberta_s42_top1": stored[row]["pred_label"], "same_label_as_roberta_shap": stored[row]["pred_label"] == LAB[k], "method": METHOD}
    # deletion test ON THE FUSED SCORE: fused-SHAP top-3 vs stored RoBERTa-SHAP top-3 vs random-3 (word removal variant)
    rv = np.array(stored[row]["shap_values"])
    if n >= 6 and (fused > 0).sum() >= K_HIDE and (rv > 0).sum() >= K_HIDE and len(rv) == n:
        topf = set(np.argsort(-fused, kind="stable")[:K_HIDE].tolist()); topr = set(np.argsort(-rv, kind="stable")[:K_HIDE].tolist())
        rng = np.random.RandomState(42 + row); draws = [set(rng.choice(n, K_HIDE, replace=False).tolist()) for _ in range(N_RANDOM)]
        sc = fused_plain([text, removed(parts, topf, text), removed(parts, topr, text)] + [removed(parts, d, text) for d in draws], k)
        rec.update({"del_used": True, "drop_fusedSHAP_top3": float(sc[0] - sc[1]), "drop_robertaSHAP_top3": float(sc[0] - sc[2]),
                    "drop_random3": float(sc[0] - sc[3:].mean()), "top3_overlap": len(topf & topr)})
    else:
        rec["del_used"] = False
    with open(OUT, "a", encoding="utf-8") as fh: fh.write(json.dumps(rec) + "\n")
    print(f"[{j}/{len(order)}] row {row} words={n} top1={LAB[k]} same_as_roberta={rec['same_label_as_roberta_shap']} add_err={rec['additivity_error']:.1e} {time.time() - t0:.0f}s", flush=True)
print("done ->", OUT)
