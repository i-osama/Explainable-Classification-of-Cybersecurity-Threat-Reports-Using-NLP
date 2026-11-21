"""Q1 plan Task 3 / prereg 14: robustness and shortcut test on TEST (local CPU, saved classifier weights).
Clean probabilities are first checked against the saved test_probs.npy (max abs diff < 1e-3); only sentences a perturbation changes are re-scored.
Writes results/robustness.csv and results/robustness_family.csv. Run: python scripts/run_robustness.py   (about 30-60 min on CPU)"""
import json, sys, time
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap import RESULTS, SEEDS, CLS_DIR, EVIDENCE, zeroshot
from ttpmap.data import build_space, load_descriptions
from ttpmap.fusion import to_full, zrow, rank_space
from ttpmap.metrics import hit_at_1, rr_at_k
from ttpmap.stats import bootstrap_ci, paired_bootstrap, mcnemar_exact, holm
from ttpmap.robust import perturbations

MAX_LEN, BS = 128, 32
S = build_space(); te = S.test["text"].astype(str).tolist(); Y = S.Y["test"]; n, L = Y.shape
objs = json.load(open(EVIDENCE / "external" / "enterprise-attack-12.1.json", encoding="utf-8"))["objects"]
P = perturbations(objs)
TX = {"clean": te, **{k: [f(t, i) for i, t in enumerate(te)] for k, f in P.items()}}
CHG = {k: np.array([a != b for a, b in zip(v, te)]) for k, v in TX.items()}


def load(d):
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    return AutoTokenizer.from_pretrained(str(d)), AutoModelForSequenceClassification.from_pretrained(str(d)).float().eval()


def probs(tok, mdl, texts):
    import torch
    out = []
    with torch.no_grad():
        for i in range(0, len(texts), BS):
            e = tok(texts[i:i + BS], truncation=True, max_length=MAX_LEN, padding=True, return_tensors="pt")
            out.append(torch.sigmoid(mdl(**e).logits).numpy())
    return np.concatenate(out) if out else np.zeros((0, mdl.config.num_labels))


def rescore(fn, clean, k):
    """Scores for perturbation k: clean rows reused where the text did not change."""
    M = clean.copy(); idx = np.where(CHG[k])[0]
    if len(idx): M[idx] = fn([TX[k][i] for i in idx])
    return M


t0 = time.time(); SC = {k: {} for k in TX}                     # SC[perturbation][system] = (n, L) score matrix
svm_fn = lambda tx: S.svm.decision_function(S.vec.transform(tx))
svm_clean = svm_fn(te); assert np.allclose(svm_clean, S.svm_raw["test"]), "SVM refit differs"
cls = {}
for tag in ("roberta", "secbert"):
    for s in SEEDS:
        d = CLS_DIR / f"{tag}_pw_s{s}"; tok, mdl = load(d); fn = lambda tx, tok=tok, mdl=mdl: probs(tok, mdl, tx)
        clean = fn(te); diff = float(np.abs(clean - np.load(d / "test_probs.npy")).max())
        assert diff < 1e-3, f"{d.name}: clean probabilities differ from test_probs.npy by {diff}"     # Review Focus 5
        cls[tag, s] = {k: rescore(fn, clean, k) for k in TX}
        print(f"  {d.name}: clean max diff {diff:.2e}; {time.time() - t0:.0f}s", flush=True)
D = load_descriptions(); zs_clean = S.matcher_zero_test
zs_fn = lambda tx: zeroshot.scores(tx, D["description"].tolist())
for k in TX:
    sv = svm_clean if k == "clean" else rescore(svm_fn, svm_clean, k)
    rob = np.mean([to_full(cls["roberta", s][k], S.cls_cols["roberta", s], L, -1e9) for s in SEEDS], axis=0)
    sec = np.mean([to_full(cls["secbert", s][k], S.cls_cols["secbert", s], L, -1e9) for s in SEEDS], axis=0)
    zr = np.mean([to_full(cls["roberta", s][k], S.cls_cols["roberta", s], L) for s in SEEDS], axis=0)
    zc = np.mean([to_full(cls["secbert", s][k], S.cls_cols["secbert", s], L) for s in SEEDS], axis=0)
    SC[k] = {"TF-IDF + SVM": rank_space(sv, S.seen_idx, L), "RoBERTa (3-seed avg)": rob, "SecBERT (3-seed avg)": sec,
             "Matcher zero-shot": zs_clean if k == "clean" else rescore(zs_fn, zs_clean, k),
             "Classifiers-only ens.": zrow(to_full(sv, S.seen_idx, L)) + zrow(zr) + zrow(zc)}
    print(f"  scored {k}; {time.time() - t0:.0f}s", flush=True)

rows, fam = [], []
for sysn in SC["clean"]:
    hc = hit_at_1(SC["clean"][sysn], Y)
    for k in TX:
        h = hit_at_1(SC[k][sysn], Y); c = bootstrap_ci(h); m = rr_at_k(SC[k][sysn], Y).mean()
        ch = CHG[k]                                                              # descriptive: P@1 on the sentences this perturbation changed
        r = {"system": sysn, "perturbation": k, "P@1": c["mean"], "P@1_lo": c["lo"], "P@1_hi": c["hi"], "MRR@3": float(m), "changed_share": float(ch.mean()), "n": n,
             "n_changed": int(ch.sum()), "P@1_changed_clean": float(hc[ch].mean()) if ch.any() else np.nan, "P@1_changed_pert": float(h[ch].mean()) if ch.any() else np.nan}
        if k != "clean":
            pb = paired_bootstrap(h, hc); mc = mcnemar_exact(h, hc)
            r.update({"delta_P@1": pb["delta"], "delta_lo": pb["lo"], "delta_hi": pb["hi"], "p_mcnemar": mc["p"]})
            if sysn == "Classifiers-only ens.": fam.append({"system": sysn, "perturbation": k, "delta_P@1": pb["delta"], "ci_lo": pb["lo"], "ci_hi": pb["hi"], "p_mcnemar": mc["p"], "mcnemar_b": mc["b"], "mcnemar_c": mc["c"]})
        rows.append(r)
for r, p in zip(fam, holm([f["p_mcnemar"] for f in fam])):
    r["p_holm"] = p; r["family_size"] = len(fam)
    r["robust_rule"] = bool(abs(r["delta_P@1"]) < 0.02 and r["ci_lo"] > -0.04 and r["ci_hi"] < 0.04)
pd.DataFrame(rows).to_csv(RESULTS / "robustness.csv", index=False); pd.DataFrame(fam).to_csv(RESULTS / "robustness_family.csv", index=False)
print(pd.DataFrame(rows)[["system", "perturbation", "P@1", "delta_P@1", "delta_lo", "delta_hi", "changed_share"]].round(3).to_string(index=False))
print(pd.DataFrame(fam).round(4).to_string(index=False))
