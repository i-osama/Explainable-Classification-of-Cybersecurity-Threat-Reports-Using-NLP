"""T3 (part 2): analyses that need model INFERENCE on CPU (no training). Pre-registrations 06, 07, 08.
Writes results/faithfulness*.csv, results/efficiency.csv, results/maxlen.csv, results/hardware.json.
Stops itself if the time budget (10 minutes per analysis) is exceeded and records that."""
import json, os, platform, sys, time
from pathlib import Path
import numpy as np, pandas as pd, torch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap import RESULTS, CLS_DIR, SHAP_DIR, EVIDENCE
from ttpmap.data import build_space
from ttpmap.explain import split_units, order_by_attribution, faithfulness_curves, comprehensiveness_sufficiency
from ttpmap.stats import paired_bootstrap, bootstrap_ci, mcnemar_exact
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModel
import psutil

BUDGET = 600.0
torch.set_grad_enabled(False)
S = build_space(); Y = S.Y["test"]; texts = S.test["text"].tolist()
ORDER100 = [int(r) for r in np.random.RandomState(42).permutation(725)[:100]]
json.dump({"cpu": platform.processor(), "logical_cpus": os.cpu_count(), "torch_threads": torch.get_num_threads(), "torch": torch.__version__,
           "ram_gb": round(psutil.virtual_memory().total / 2**30, 1), "os": platform.platform(), "python": platform.python_version(), "device": "cpu"},
          open(RESULTS / "hardware.json", "w"), indent=1)

def load(tag):
    d = CLS_DIR / f"{tag}_pw_s42"
    return AutoTokenizer.from_pretrained(str(d)), AutoModelForSequenceClassification.from_pretrained(str(d)).float().eval()
def logits(tok, model, tx, max_len=128, bs=32):
    out = []
    for i in range(0, len(tx), bs):
        enc = tok([str(t) for t in tx[i:i + bs]], truncation=True, max_length=max_len, padding=True, return_tensors="pt")
        out.append(model(**enc).logits.numpy())
    return np.concatenate(out)

tok_r, rob = load("roberta"); tok_s, sec = load("secbert")

# ---------------- prereg 06: faithfulness ----------------
t0 = time.time(); K = 10
stored = {}
for l in open(SHAP_DIR / "shap_v2_roberta_pw_s42.jsonl", encoding="utf-8"):
    if l.strip():
        r = json.loads(l); stored[r["row"]] = r
classes = np.load(CLS_DIR / "roberta_pw_s42" / "mlb_classes.npy", allow_pickle=True)
rows, curves, over = [], [], False
sig = lambda x: 1 / (1 + np.exp(-x))
for row in ORDER100:
    rec = stored[row]; parts = split_units(rec["text"]); nw = len(parts)
    if nw < 6 or rec["truncated"]:
        rows.append({"row": row, "used": False, "n_words": nw, "truncated": rec["truncated"]}); continue
    k = int(np.where(classes == rec["pred_label"])[0][0])
    f = lambda tx: logits(tok_r, rob, tx)[:, k]
    so = order_by_attribution(rec["shap_values"])
    rng = np.random.RandomState(1000 + row); ros = [rng.permutation(nw).tolist() for _ in range(5)]
    cs = faithfulness_curves(parts, so, f, tok_r.mask_token, K)
    cr = [faithfulness_curves(parts, o, f, tok_r.mask_token, K) for o in ros]
    kk = len(cs["deletion"]) - 1
    def auc(c):                       # mean probability along the curve (trapezoid), k = 0..kk
        p = sig(np.asarray(c)); return float(np.trapezoid(p, dx=1.0) / kk)
    r = {"row": row, "used": True, "n_words": nw, "truncated": False, "k_max": kk, "top1_correct": rec["top1_correct"],
         "del_auc_shap": auc(cs["deletion"]), "del_auc_random": float(np.mean([auc(c["deletion"]) for c in cr])),
         "ins_auc_shap": auc(cs["insertion"]), "ins_auc_random": float(np.mean([auc(c["insertion"]) for c in cr]))}
    for name, fn in (("logit", lambda x: x), ("prob", sig)):
        g = lambda tx: fn(f(tx))
        a = comprehensiveness_sufficiency(parts, so, g, tok_r.mask_token, 3)
        b = [comprehensiveness_sufficiency(parts, o, g, tok_r.mask_token, 3) for o in ros]
        r.update({f"comp_shap_{name}": a["comprehensiveness"], f"comp_random_{name}": float(np.mean([x["comprehensiveness"] for x in b])),
                  f"suff_shap_{name}": a["sufficiency"], f"suff_random_{name}": float(np.mean([x["sufficiency"] for x in b]))})
    rows.append(r)
    for kq in range(kk + 1):
        curves.append({"row": row, "k": kq, "del_shap": float(sig(cs["deletion"][kq])), "del_random": float(np.mean([sig(c["deletion"][kq]) for c in cr])),
                       "ins_shap": float(sig(cs["insertion"][kq])), "ins_random": float(np.mean([sig(c["insertion"][kq]) for c in cr]))})
    if time.time() - t0 > BUDGET: over = True; break
df = pd.DataFrame(rows); df.to_csv(RESULTS / "faithfulness.csv", index=False)
cv = pd.DataFrame(curves)
agg = cv[cv.k <= 10].groupby("k").agg(n=("row", "count"), del_shap=("del_shap", "mean"), del_random=("del_random", "mean"), ins_shap=("ins_shap", "mean"), ins_random=("ins_random", "mean")).reset_index()
agg.to_csv(RESULTS / "faithfulness_curves.csv", index=False)
u = df[df.used == True]
summ = []
for name, a, b, better in (("deletion AUC (mean prob., lower = more faithful)", "del_auc_shap", "del_auc_random", "lower"), ("insertion AUC (mean prob., higher = more faithful)", "ins_auc_shap", "ins_auc_random", "higher"),
                           ("comprehensiveness top-3, probability", "comp_shap_prob", "comp_random_prob", "higher"), ("sufficiency top-3, probability (lower = better)", "suff_shap_prob", "suff_random_prob", "lower"),
                           ("comprehensiveness top-3, logit", "comp_shap_logit", "comp_random_logit", "higher"), ("sufficiency top-3, logit (lower = better)", "suff_shap_logit", "suff_random_logit", "lower")):
    pb = paired_bootstrap(u[a].to_numpy(), u[b].to_numpy())
    ok = pb["hi"] < 0 if better == "lower" else pb["lo"] > 0
    summ.append({"measure": name, "n": len(u), "shap": u[a].mean(), "random": u[b].mean(), "delta": pb["delta"], "ci_lo": pb["lo"], "ci_hi": pb["hi"], "expected_direction": better,
                 "supported": bool(ok), "shap_better_in": int(((u[a] < u[b]) if better == "lower" else (u[a] > u[b])).sum())})
pd.DataFrame(summ).to_csv(RESULTS / "faithfulness_summary.csv", index=False)
print(f"faithfulness: sampled {len(df)}, used {len(u)}, {time.time() - t0:.0f}s, budget exceeded: {over}", flush=True)

# ---------------- prereg 08: 128 vs 256 on truncated sentences ----------------
t0 = time.time()
tr = pd.read_csv(EVIDENCE / "01_truncated_test_ids.csv"); ids = tr[tr.tokenizer.str.startswith("roberta")]["test_id"].to_numpy()
rows = []
for tag, tok, model in (("roberta", tok_r, rob), ("secbert", tok_s, sec)):
    cols = S.cls_cols[tag, 42]; tx = [texts[i] for i in ids]
    h = {}
    for ml in (128, 256):
        top = logits(tok, model, tx, ml, bs=8).argmax(1); h[ml] = Y[ids][:, cols][np.arange(len(ids)), top].astype(float)
    mc = mcnemar_exact(h[256], h[128])
    n_over = int(sum(len(tok(t)["input_ids"]) > 256 for t in tx))
    rows.append({"model": f"{tag}_pw_s42", "n": len(ids), "P@1_128": h[128].mean(), "P@1_256": h[256].mean(), "hits_128": int(h[128].sum()), "hits_256": int(h[256].sum()),
                 "gained": mc["b"], "lost": mc["c"], "p_mcnemar": mc["p"], "still_truncated_at_256": n_over})
pd.DataFrame(rows).to_csv(RESULTS / "maxlen.csv", index=False)
print(f"maxlen: {time.time() - t0:.0f}s", flush=True)

# ---------------- prereg 07: efficiency ----------------
t0 = time.time(); proc = psutil.Process(); sample = [texts[i] for i in ORDER100]
def timeit(fn):
    for t in sample[:5]: fn(t)
    ts = []
    for t in sample:
        a = time.perf_counter(); fn(t); ts.append(time.perf_counter() - a)
    return float(np.median(ts) * 1000), float(np.percentile(ts, 90) * 1000)
eff = []
nnz = int(sum((e.coef_ != 0).sum() for e in S.svm.estimators_)); nco = int(sum(e.coef_.size for e in S.svm.estimators_))
m, p90 = timeit(lambda t: S.svm.decision_function(S.vec.transform([t])))
eff.append({"system": "TF-IDF + SVM", "parameters": nco, "note": f"{len(S.vec.vocabulary_)} n-gram features x 180 labels; {nnz} non-zero weights", "median_ms": m, "p90_ms": p90, "timed_with": "refit model"})
for nm, tok, model in (("RoBERTa", tok_r, rob), ("SecBERT", tok_s, sec)):
    m, p90 = timeit(lambda t: logits(tok, model, [t]))
    eff.append({"system": nm, "parameters": int(sum(p.numel() for p in model.parameters())), "note": "one seed; the 3-seed average costs 3 forward passes", "median_ms": m, "p90_ms": p90, "timed_with": "saved checkpoint seed 42"})
try:
    tb = AutoTokenizer.from_pretrained("BAAI/bge-base-en-v1.5", local_files_only=True); mb = AutoModel.from_pretrained("BAAI/bge-base-en-v1.5", local_files_only=True).float().eval()
    lab = np.random.default_rng(0).standard_normal((733, 768)).astype(np.float32)
    def mfn(t):
        e = tb([t], truncation=True, max_length=128, return_tensors="pt"); v = torch.nn.functional.normalize(mb(**e).last_hidden_state[:, 0], dim=-1).numpy(); return v @ lab.T
    m, p90 = timeit(mfn)
    eff.append({"system": "Matcher (bge-base)", "parameters": int(sum(p.numel() for p in mb.parameters())), "median_ms": m, "p90_ms": p90,
                "note": "sentence encoding + dot product with 733 pre-computed label vectors; label vectors are a one-off cost", "timed_with": "PUBLIC base checkpoint (fine-tuned weights were never saved; same architecture)"})
except Exception as e:
    eff.append({"system": "Matcher (bge-base)", "parameters": np.nan, "median_ms": np.nan, "p90_ms": np.nan, "note": f"not timed: {type(e).__name__}", "timed_with": "-"})
ed = pd.DataFrame(eff); ed["process_rss_gb_all_models_loaded"] = round(proc.memory_info().rss / 2**30, 2)
ed.to_csv(RESULTS / "efficiency.csv", index=False)
print(f"efficiency: {time.time() - t0:.0f}s", flush=True)
