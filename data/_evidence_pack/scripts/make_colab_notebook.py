"""Build 09_repro/colab_fusion_shap.ipynb: matcher retrain WITH saved weights + full-fusion SHAP, for a Colab GPU kernel.
Code is ported from the locally tested x1_fusion_shap.py / x3_train_matcher_cpu.py and Exp_2.1 CELL 2-3."""
import nbformat as nbf
from common import PACK

C = []
def md(s): C.append(nbf.v4.new_markdown_cell(s.strip()))
def code(s): C.append(nbf.v4.new_code_cell(s.strip("\n")))

md("""
# Matcher retrain with saved weights + SHAP of the full fusion (Colab GPU)

Run the cells **top to bottom, one at a time**. Runtime type: **T4 GPU**.

| Cell | What it does | Time |
|---|---|---|
| 1 | Drive mount, paths, file check | seconds |
| 2 | Data, 733-label space, SVM, helpers | seconds |
| 3 | Train the matcher, seed 42, **save weights** | about 20-30 min |
| 4 | Check: retrained matcher and seed-42 fusion (3,1,1,1) on test | 1 min |
| 5 | Word-level permutation SHAP of the fused score, 100 fixed test sentences | about 30-60 min |
| 6 | Summary (agreement with the stored RoBERTa SHAP, deletion test on the fused score) | seconds |
| 7 | Optional: train matcher seeds 43 and 44 with saved weights | about 1 h |

Everything is written to **new** folders/files (`run_match_2_saved`, `Exp_3_0_shap/fusion_shap_full_s42.jsonl`). Nothing existing is overwritten.
""")

code(r'''
# Cell 1 - Drive, paths, file check
import os, re, ast, json, math, random, time
import numpy as np, pandas as pd, torch

BASE = "/content/drive/MyDrive/KDU/Thesis"
try:
    from google.colab import drive
    drive.mount("/content/drive")
except Exception as e:
    print(f"Drive mount failed or not available here: {type(e).__name__}: {e}")

DATA_DIR  = f"{BASE}/Dataset"
CLS_ROOT  = f"{BASE}/Exp_1_4_run_tram_2_epoc_30"
SHAP_DIR  = f"{BASE}/Exp_3_0_shap"
OUT2      = f"{BASE}/run_match_2_saved"            # NEW folder
SHAP_OUT  = f"{SHAP_DIR}/fusion_shap_full_s42.jsonl"   # NEW file
SEED      = 42
BASE_MODEL = "BAAI/bge-base-en-v1.5"

need = [f"{DATA_DIR}/tram_train.tsv", f"{DATA_DIR}/tram_dev.tsv", f"{DATA_DIR}/tram_test.tsv", f"{DATA_DIR}/ttp-desc-mappings.csv",
        f"{CLS_ROOT}/roberta_pw_s{SEED}/model.safetensors", f"{CLS_ROOT}/secbert_pw_s{SEED}/model.safetensors",
        f"{SHAP_DIR}/shap_v2_roberta_pw_s42.jsonl"]
missing = [p for p in need if not os.path.exists(p)]
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("device:", device, "|", torch.cuda.get_device_name(0) if device.type == "cuda" else "NO GPU - change the runtime type")
print("ALL FILES FOUND" if not missing else "MISSING (stop here and report):\n  " + "\n  ".join(missing))
if not missing: os.makedirs(OUT2, exist_ok=True)
''')

code(r'''
# Cell 2 - data, 733-label space, metrics, SVM (same as Exp_2.1 Cell 2 and Cell 7)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC

def load_split(name):
    df = pd.read_csv(f"{DATA_DIR}/tram_{name}.tsv", sep="\t").rename(columns={"text1": "text"})
    df["y"] = df["labels"].map(lambda x: sorted({s.lower() for s in ast.literal_eval(x)}))
    return df[["text", "y"]]
train, dev, test = (load_split(s) for s in ("train", "dev", "test"))
train = train.drop_duplicates(subset=["text"]).reset_index(drop=True)
assert len(train) == 3468 and len(dev) == 604 and len(test) == 725

desc = pd.read_csv(f"{DATA_DIR}/ttp-desc-mappings.csv", sep="\t")
desc["ttp"] = desc["ttp"].str.lower().str.strip()
desc["description"] = (desc["description"].fillna("").str.replace(r"\s+", " ", regex=True).str.replace(r"\bcitation:\s*", "", regex=True).str.strip())
desc = desc.drop_duplicates("ttp")
desc = desc[~desc["ttp"].isin({"t1060", "t1107", "t1151", "t1188"})].reset_index(drop=True)
LABELS = desc["ttp"].tolist(); LABEL_TEXTS = desc["description"].tolist(); L = len(LABELS); lab2i = {l: i for i, l in enumerate(LABELS)}
assert L == 733

def to_Y(df):
    Y = np.zeros((len(df), L), dtype=np.int64)
    for i, ys in enumerate(df["y"]):
        for y in ys: Y[i, lab2i[y]] = 1
    return Y
Y_train, Y_dev, Y_test = to_Y(train), to_Y(dev), to_Y(test)
SEEN = Y_train.sum(axis=0) > 0; seen_idx = np.where(SEEN)[0]
assert SEEN.sum() == 180

def rank_metrics(S, Y):
    n = len(S); top = np.argsort(-S, axis=1, kind="stable")[:, :5]
    hits = np.take_along_axis(Y, top, axis=1); h3 = hits[:, :3]
    first = np.where(h3.any(axis=1), h3.argmax(axis=1) + 1, np.inf)
    intop = np.zeros(Y.shape, dtype=bool); intop[np.arange(n)[:, None], top] = True
    un = Y.astype(bool) & ~SEEN[None, :]
    return {"P@1": float(hits[:, 0].mean()), "R@1": float(hits[:, 0].sum() / Y.sum()), "MRR@3": float(np.mean(1.0 / first)),
            "R@5": float(hits.sum() / Y.sum()), "unseen_R@5": float((intop & un).sum() / max(un.sum(), 1))}

def zrow(F_):
    m = np.nanmean(F_, axis=1, keepdims=True); s = np.nanstd(F_, axis=1, keepdims=True) + 1e-9
    return np.nan_to_num((F_ - m) / s, nan=0.0)
def to_full(S_seen, cols):
    F_ = np.full((S_seen.shape[0], L), np.nan); F_[:, cols] = S_seen; return F_

vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True).fit(train["text"])
svm = OneVsRestClassifier(LinearSVC(C=1.0, random_state=42)).fit(vec.transform(train["text"]), Y_train[:, seen_idx])
OOV = "zzzmaskzzz"; assert OOV not in vec.vocabulary_
m = rank_metrics(np.where(np.isnan(to_full(svm.decision_function(vec.transform(test["text"])), seen_idx)), -1e9,
                          to_full(svm.decision_function(vec.transform(test["text"])), seen_idx)), Y_test)
print("SVM test P@1 (expected 0.742):", round(m["P@1"], 4))
''')

code(r'''
# Cell 3 - train the matcher (seed 42) exactly as Exp_2.1 Cell 3/6.1, and SAVE the weights
import torch.nn as nn, torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel, get_linear_schedule_with_warmup

class Matcher(nn.Module):
    def __init__(self, name, pooling="cls"):
        super().__init__(); self.enc = AutoModel.from_pretrained(name); self.pooling = pooling
    def forward(self, **enc):
        h = self.enc(**enc).last_hidden_state
        return F.normalize(h[:, 0].float(), dim=-1)

def tok_batch(tok, texts, max_len):
    enc = tok(list(texts), padding=True, truncation=True, max_length=max_len, return_tensors="pt")
    return {k: v.to(device) for k, v in enc.items() if k in ("input_ids", "attention_mask", "token_type_ids")}

@torch.no_grad()
def embed_all(model, tok, texts, max_len, bs=64, amp=True):
    model.eval(); out = []
    for i in range(0, len(texts), bs):
        with torch.autocast(device_type=device.type, dtype=torch.float16, enabled=amp and device.type == "cuda"):
            out.append(model(**tok_batch(tok, texts[i:i + bs], max_len)).cpu())
    return torch.cat(out).numpy()

def run_eval(model, tok, label_max_len_eval=256):
    label_emb = embed_all(model, tok, LABEL_TEXTS, label_max_len_eval)
    S_dev = embed_all(model, tok, list(dev["text"]), 128) @ label_emb.T; S_te = embed_all(model, tok, list(test["text"]), 128) @ label_emb.T
    return S_dev, S_te, rank_metrics(S_dev, Y_dev), rank_metrics(S_te, Y_test)

def train_matcher_save(model_name, out_dir, seed=42, epochs=20, patience=4, batch_size=16, lr=2e-5, n_neg=64, scale=30.0,
                       text_max_len=128, label_max_len_train=128, label_max_len_eval=256):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
    os.makedirs(out_dir, exist_ok=True); rng = np.random.default_rng(seed); amp_on = device.type == "cuda"
    tok = AutoTokenizer.from_pretrained(model_name); model = Matcher(model_name).to(device)
    N = len(train); texts = train["text"].tolist(); label_texts = np.array(LABEL_TEXTS, dtype=object)
    pos_lists = [np.where(Y_train[i])[0] for i in range(N)]; pool = np.arange(L)
    steps_per_epoch = math.ceil(N / batch_size)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    sched = get_linear_schedule_with_warmup(opt, int(0.1 * steps_per_epoch * epochs), steps_per_epoch * epochs)
    scaler = torch.amp.GradScaler(enabled=amp_on)
    best, best_ep, best_state, bad, hist = -1.0, 0, None, 0, []
    for ep in range(1, epochs + 1):
        model.train(); perm = rng.permutation(N); tot = 0.0; t0 = time.time()
        for b in range(0, N, batch_size):
            idx = perm[b:b + batch_size]
            gold_u = np.unique(np.concatenate([pos_lists[i] for i in idx]))
            cand = np.setdiff1d(pool, gold_u)
            negs = rng.choice(cand, size=min(n_neg, len(cand)), replace=False)
            U = np.concatenate([gold_u, negs])
            with torch.autocast(device_type=device.type, dtype=torch.float16, enabled=amp_on):
                et = model(**tok_batch(tok, [texts[i] for i in idx], text_max_len))
                eu = model(**tok_batch(tok, label_texts[U].tolist(), label_max_len_train))
            S = (et @ eu.T) * scale
            pos = torch.tensor(Y_train[idx][:, U].astype(bool), device=device)
            neg_lse = torch.logsumexp(S.masked_fill(pos, -1e4), dim=1)
            rows = pos.nonzero()[:, 0]
            loss = F.softplus(neg_lse[rows] - S[pos]).mean()
            opt.zero_grad(); scaler.scale(loss).backward(); scaler.unscale_(opt)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(opt); scaler.update(); sched.step(); tot += loss.item() * len(idx)
        _, _, md_, _ = run_eval(model, tok, label_max_len_eval)
        hist.append({"epoch": ep, "train_loss": tot / N, **{f"dev_{k}": v for k, v in md_.items()}})
        print(f"  epoch {ep:2d}: train_loss={tot / N:.4f} dev P@1={md_['P@1']:.4f} MRR@3={md_['MRR@3']:.4f} R@5={md_['R@5']:.4f} ({time.time() - t0:.0f}s)")
        if md_["MRR@3"] > best:
            best, best_ep, bad = md_["MRR@3"], ep, 0
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            torch.save(best_state, f"{out_dir}/matcher_state.pt")            # <- the weights the old notebook never saved
        else:
            bad += 1
            if bad >= patience: print(f"  early stop (no dev improvement for {patience} epochs)"); break
    model.load_state_dict(best_state)
    S_dev, S_te, md_, mt = run_eval(model, tok, label_max_len_eval)
    np.save(f"{out_dir}/dev_scores.npy", S_dev); np.save(f"{out_dir}/test_scores.npy", S_te)
    json.dump({"model_name": model_name, "seed": seed, "best_epoch": best_ep, "dev": md_, "test": mt, "history": hist, "finished": True,
               "config": dict(epochs=epochs, patience=patience, batch_size=batch_size, lr=lr, n_neg=n_neg, scale=scale, text_max_len=text_max_len,
                              label_max_len_train=label_max_len_train, pooling="cls", neg_pool="all")}, open(f"{out_dir}/metrics.json", "w"), indent=2)
    print("  TEST:", {k: round(v, 4) for k, v in mt.items()}, f"| best epoch {best_ep} | saved to {out_dir}")
    del model, opt; import gc; gc.collect(); torch.cuda.empty_cache()

def train_seed(sd):
    out = f"{OUT2}/ft20_s{sd}"
    if os.path.exists(f"{out}/metrics.json"): print("skip (already done):", out)
    else: train_matcher_save(BASE_MODEL, out, seed=sd)
train_seed(SEED)
''')

code(r'''
# Cell 4 - check the retrained matcher and the seed-42 fusion (3,1,1,1) on test
mt = json.load(open(f"{OUT2}/ft20_s{SEED}/metrics.json"))
print(f"retrained matcher s{SEED}: best epoch {mt['best_epoch']}, test P@1 {mt['test']['P@1']:.4f} MRR@3 {mt['test']['MRR@3']:.4f}  (original run_match_1 s42: P@1 0.7559)")
Zt = {"matcher": zrow(np.load(f"{OUT2}/ft20_s{SEED}/test_scores.npy")), "svm": zrow(to_full(svm.decision_function(vec.transform(test["text"])), seen_idx))}
CLS_COLS = {}
for tag in ("roberta", "secbert"):
    p = f"{CLS_ROOT}/{tag}_pw_s{SEED}"
    CLS_COLS[tag] = np.array([lab2i[str(c).lower()] for c in np.load(f"{p}/mlb_classes.npy", allow_pickle=True)])
    Zt[tag] = zrow(to_full(np.load(f"{p}/test_probs.npy"), CLS_COLS[tag]))
W = {"matcher": 3.0, "svm": 1.0, "roberta": 1.0, "secbert": 1.0}
fz = sum(W[k] * Zt[k] for k in W)
print("seed-42 fusion (3,1,1,1) with the RETRAINED matcher:", {k: round(v, 4) for k, v in rank_metrics(fz, Y_test).items()}, "(original seed-paired s42: P@1 0.790)")
print("classifiers-only part (0,1,1,1):", round(rank_metrics(sum(Zt[k] for k in ("svm", "roberta", "secbert")), Y_test)["P@1"], 4))
''')

code(r'''
# Cell 5 - SHAP of the FUSED score (same method as Exp_3_0b: words, mask token, 40 permutations, seed 42). Resumable.
import importlib.util, subprocess, sys
if importlib.util.find_spec("shap") is None: subprocess.run([sys.executable, "-m", "pip", "install", "-q", "shap"])
import shap
from transformers import AutoModelForSequenceClassification
N_SHAP, N_PERM, SHAP_SEED, MAX_LEN, K_HIDE, N_RANDOM = 100, 40, 42, 128, 3, 20
texts_te = test["text"].tolist(); LAB = np.array([l.upper() for l in LABELS]); Yb = Y_test.astype(bool)

class Clf:
    def __init__(self, tag):
        d = f"{CLS_ROOT}/{tag}_pw_s{SEED}"
        self.tok = AutoTokenizer.from_pretrained(d); self.model = AutoModelForSequenceClassification.from_pretrained(d).float().to(device).eval()
        self.cols = CLS_COLS[tag]; self.mask = self.tok.mask_token; self.name = f"{tag}_s{SEED}"
    @torch.no_grad()
    def z(self, tx):
        out = []
        for s in range(0, len(tx), 64):
            enc = self.tok(tx[s:s + 64], truncation=True, max_length=MAX_LEN, padding=True, return_tensors="pt").to(device)
            out.append(torch.sigmoid(self.model(**enc).logits).cpu().numpy())
        return zrow(to_full(np.concatenate(out), self.cols))
class SvmC:
    name, mask = "svm", OOV
    def z(self, tx): return zrow(to_full(svm.decision_function(vec.transform(tx)), seen_idx))
class MatcherC:
    name = "matcher"
    def __init__(self):
        self.tok = AutoTokenizer.from_pretrained(BASE_MODEL); self.model = Matcher(BASE_MODEL)
        self.model.load_state_dict(torch.load(f"{OUT2}/ft20_s{SEED}/matcher_state.pt", map_location="cpu")); self.model = self.model.float().to(device).eval()
        self.mask = self.tok.mask_token
        self.label_emb = embed_all(self.model, self.tok, LABEL_TEXTS, 256, amp=False)
    def z(self, tx): return zrow(embed_all(self.model, self.tok, list(tx), MAX_LEN, amp=False) @ self.label_emb.T)

comps = [MatcherC(), SvmC(), Clf("roberta"), Clf("secbert")]; weights = [3.0, 1.0, 1.0, 1.0]
# sanity: the SHAP-time fused scores must reproduce Cell 4
chk = sum(w * c.z(texts_te) for w, c in zip(weights, comps))
print("fusion P@1 recomputed inside the SHAP pipeline:", round(rank_metrics(chk, Y_test)["P@1"], 4), "| max |z diff| vs Cell 4:", float(np.abs(chk - fz).max()))

METHOD = {"unit": "whitespace-delimited word", "masking": "word replaced by each model's own mask token (SVM: OOV placeholder)", "algorithm": "permutation",
          "n_perm": N_PERM, "shap_seed": SHAP_SEED, "output": "weighted sum of per-row z-scores for the fused top-1 label", "max_length": MAX_LEN,
          "system": f"fusion (3,1,1,1) seed-paired, seed {SEED}, RETRAINED matcher (run_match_2_saved)", "components": [c.name for c in comps], "weights": weights}
UNIT_RE = re.compile(r"(\s*)(\S+)(\s*)")
stored = {}
for l in open(f"{SHAP_DIR}/shap_v2_roberta_pw_s42.jsonl", encoding="utf-8"):
    if l.strip():
        r = json.loads(l); stored[r["row"]] = r

def comp_scores(parts, keeps, k):
    cols = []
    for c in comps:
        tx = ["".join(lead + (word if kp else c.mask) + trail for (lead, word, trail), kp in zip(parts, keep)) for keep in keeps]
        cols.append(c.z(tx)[:, k])
    return np.stack(cols, axis=1)
def removed(parts, hide, original):
    s = "".join(l + c + t for i, (l, c, t) in enumerate(parts) if i not in hide)
    return s.rstrip() if (len(parts) - 1) in hide and not original[-1:].isspace() else s
def fused_plain(tx, k): return sum(w * c.z(tx)[:, k] for w, c in zip(weights, comps))

done = set()
if os.path.exists(SHAP_OUT):
    for l in open(SHAP_OUT, encoding="utf-8"):
        if l.strip(): done.add(json.loads(l)["row"])
order = [int(r) for r in np.random.RandomState(42).permutation(725)[:N_SHAP]]
t0 = time.time()
for j, row in enumerate(order, 1):
    if row in done: continue
    text = str(texts_te[row]); parts = [m_.groups() for m_ in UNIT_RE.finditer(text)]; n = len(parts)
    full = sum(w * c.z([text])[0] for w, c in zip(weights, comps)); k = int(full.argmax())
    f = lambda M: comp_scores(parts, np.asarray(M) > 0.5, k)
    ex = shap.Explainer(f, shap.maskers.Independent(np.zeros((1, n))), algorithm="permutation", seed=SHAP_SEED)
    sv = ex(np.ones((1, n)), max_evals=N_PERM * (2 * n + 1), batch_size=64, silent=True)[0]
    V = np.asarray(sv.values); fused = V @ np.array(weights)
    rec = {"row": row, "text": text, "units": ["".join(p) for p in parts], "fused_top1": str(LAB[k]), "fused_score": float(full[k]),
           "gold_labels": LAB[Yb[row]].tolist(), "fused_top1_correct": bool(Yb[row, k]), "shap_fused": fused.tolist(),
           "shap_by_component": {c.name: V[:, i].tolist() for i, c in enumerate(comps)}, "base_by_component": np.asarray(sv.base_values).tolist(),
           "additivity_error": float(abs(fused.sum() + np.asarray(sv.base_values) @ np.array(weights) - full[k])),
           "roberta_s42_top1": stored[row]["pred_label"], "same_label_as_roberta_shap": stored[row]["pred_label"] == str(LAB[k]), "method": METHOD}
    rv = np.array(stored[row]["shap_values"])
    if n >= 6 and (fused > 0).sum() >= K_HIDE and (rv > 0).sum() >= K_HIDE and len(rv) == n:
        topf = set(np.argsort(-fused, kind="stable")[:K_HIDE].tolist()); topr = set(np.argsort(-rv, kind="stable")[:K_HIDE].tolist())
        rng = np.random.RandomState(42 + row); draws = [set(rng.choice(n, K_HIDE, replace=False).tolist()) for _ in range(N_RANDOM)]
        sc = fused_plain([text, removed(parts, topf, text), removed(parts, topr, text)] + [removed(parts, d, text) for d in draws], k)
        rec.update({"del_used": True, "drop_fusedSHAP_top3": float(sc[0] - sc[1]), "drop_robertaSHAP_top3": float(sc[0] - sc[2]),
                    "drop_random3": float(sc[0] - sc[3:].mean()), "top3_overlap": len(topf & topr)})
    else:
        rec["del_used"] = False
    with open(SHAP_OUT, "a", encoding="utf-8") as fh: fh.write(json.dumps(rec) + "\n"); fh.flush()
    if j % 5 == 0 or j == len(order):
        print(f"[{j}/{len(order)}] row {row} words={n} top1={LAB[k]} same_as_roberta={rec['same_label_as_roberta_shap']} add_err={rec['additivity_error']:.1e} {time.time() - t0:.0f}s")
print("stored:", SHAP_OUT)
''')

code(r'''
# Cell 6 - summary
from scipy.stats import spearmanr
recs = [json.loads(l) for l in open(SHAP_OUT, encoding="utf-8") if l.strip()]
names = recs[0]["method"]["components"]; wts = dict(zip(names, recs[0]["method"]["weights"]))
print(f"{len(recs)} sentences | fused top-1 correct {sum(r['fused_top1_correct'] for r in recs)} | stored RoBERTa s42 correct {sum(stored[r['row']]['top1_correct'] for r in recs)}"
      f" | same label as stored RoBERTa SHAP {sum(r['same_label_as_roberta_shap'] for r in recs)} | max additivity error {max(r['additivity_error'] for r in recs):.1e}")
rho = [spearmanr(r["shap_fused"], stored[r["row"]]["shap_values"]).statistic for r in recs if r["same_label_as_roberta_shap"] and len(r["units"]) >= 3]
ov = [r["top3_overlap"] for r in recs if r.get("del_used") and r["same_label_as_roberta_shap"]]
print(f"same label: Spearman fused vs RoBERTa SHAP mean {np.mean(rho):.3f} median {np.median(rho):.3f} | top-3 overlap mean {np.mean(ov):.2f} of 3")
share = {c: np.mean([wts[c] * np.abs(r["shap_by_component"][c]).sum() / sum(wts[x] * np.abs(r["shap_by_component"][x]).sum() for x in names) for r in recs]) for c in names}
print("share of |SHAP| mass per component:", {c: round(float(v), 3) for c, v in share.items()})
d = [r for r in recs if r.get("del_used")]
f_ = np.array([r["drop_fusedSHAP_top3"] for r in d]); rb = np.array([r["drop_robertaSHAP_top3"] for r in d]); rn = np.array([r["drop_random3"] for r in d])
rg = np.random.RandomState(42)
def ci(x):
    b = [x[rg.randint(0, len(x), len(x))].mean() for _ in range(2000)]; return np.percentile(b, [2.5, 97.5]).round(3).tolist()
print(f"deletion test on the fused score, n={len(d)}: fused-SHAP top-3 {f_.mean():.3f} {ci(f_)} | RoBERTa-SHAP top-3 {rb.mean():.3f} {ci(rb)} | random-3 {rn.mean():.3f} {ci(rn)}")
print(f"fused minus RoBERTa: {np.mean(f_ - rb):+.3f} {ci(f_ - rb)} | fused larger {int((f_ > rb).sum())}, equal {int((f_ == rb).sum())}, smaller {int((f_ < rb).sum())}")
sm = np.array([r["same_label_as_roberta_shap"] for r in d])
print(f"same label (n={sm.sum()}): fused {f_[sm].mean():.3f} RoBERTa {rb[sm].mean():.3f} | different label (n={(~sm).sum()}): fused {f_[~sm].mean():.3f} RoBERTa {rb[~sm].mean():.3f}")
''')

code(r'''
# Cell 7 - OPTIONAL: matcher seeds 43 and 44 with saved weights (about 1 h); then the 3-seed check
for sd in (43, 44): train_seed(sd)
p1 = [json.load(open(f"{OUT2}/ft20_s{s}/metrics.json"))["test"]["P@1"] for s in (42, 43, 44)]
print(f"retrained matcher, 3 seeds: P@1 {np.mean(p1):.3f} +- {np.std(p1, ddof=1):.3f} {[round(x, 3) for x in p1]}  (original: 0.756 +- 0.015)")
M_avg = zrow(np.mean([np.load(f"{OUT2}/ft20_s{s}/test_scores.npy") for s in (42, 43, 44)], axis=0))
print("retrained matcher 3-seed ensemble P@1:", round(rank_metrics(M_avg, Y_test)["P@1"], 4), "(original 0.777)")
''')

nb = nbf.v4.new_notebook(cells=C, metadata={"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "accelerator": "GPU"})
out = PACK / "09_repro" / "colab_fusion_shap.ipynb"
nbf.write(nb, out); print("wrote", out, len(C), "cells")
