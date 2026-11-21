"""T5: generate notebooks/00..10 (Colab-first, local fallback). The shared library cell is built from the SOURCE of
src/ttpmap (metrics, fusion, stats) so notebooks and package cannot drift apart. No result number is typed here.
Usage: python scripts/make_notebooks.py"""
import inspect, sys
from pathlib import Path
import nbformat as nbf
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap import metrics as M, fusion as F, stats as ST, SHOWCASE

NB = SHOWCASE / "notebooks"; NB.mkdir(exist_ok=True)
LIB = ("# ---- library cell: generated from src/ttpmap (metrics.py, fusion.py, stats.py); do not edit here ----\n"
       "import itertools, math\nfrom functools import reduce\nfrom typing import Dict, Iterable, List, Sequence, Tuple, Literal\nimport numpy as np\nfrom scipy.stats import binomtest\n"
       "F1Variant = Literal['notebook', 'seen_test', 'all_test']\nORDER = ('matcher', 'svm', 'roberta', 'secbert')\nBOOT_N, BOOT_SEED = 10_000, 20261114\n\n"
       + "\n\n".join(inspect.getsource(f) for f in (M.rank_topk, M.hit_at_1, M.precision_at_k, M.rr_at_k, M.recall_at_k_micro, M.recall_at_k_per_sample, M.apply_threshold, M._prf, M.f1_per_label, M.f1_scores,
                                                   F.LeakageError, F.to_full, F.zrow, F.fuse, F.coarse_grid, F.wide_grid, F.select_weights, F.select_threshold,
                                                   ST.bootstrap_ci, ST.paired_bootstrap, ST.mcnemar_exact, ST.holm)))

SETUP = r'''
# ---- setup (same in every notebook) ----
import os, sys, json, ast, time, hashlib, random, platform, subprocess, re
from pathlib import Path
import numpy as np, pandas as pd

SMOKE = os.environ.get("TTPMAP_SMOKE", "0") == "1"      # set SMOKE = True by hand for a 20-sample dry run
IN_COLAB = "google.colab" in sys.modules or os.path.exists("/content")
if IN_COLAB:
    try:
        from google.colab import drive
        drive.mount("/content/drive")
    except Exception as e:
        print("Drive mount failed:", type(e).__name__, e)
    if not os.path.isdir("/content/drive/MyDrive") and not SMOKE:
        raise RuntimeError("Google Drive is not mounted. The Colab extension for VS Code cannot mount Drive (known limitation of the extension), "
                           "and these notebooks read their inputs from and save their results to Drive. Open this notebook in the browser instead: "
                           "https://colab.research.google.com > File > Upload notebook (or open it from Drive). See notebooks/COLAB_RUNBOOK.md, section 0.")
BASE = Path("/content/drive/MyDrive/KDU/Thesis") if IN_COLAB else Path(os.environ.get("TTPMAP_ROOT", r"E:\Osamas Paper"))
DATA_DIR, CLS_ROOT, MATCH_ROOT, SHAP_DIR = BASE / "Dataset", BASE / "Exp_1_4_run_tram_2_epoc_30", BASE / "run_match_1", BASE / "Exp_3_0_shap"
MATCH2 = BASE / "run_match_2_saved"                      # NEW folder: matcher retrained WITH saved weights (notebook 04)
OUT = (Path(os.environ["TTPMAP_SMOKE_OUT"]) if os.environ.get("TTPMAP_SMOKE_OUT") else BASE / "showcase_runs") / NOTEBOOK
OUT.mkdir(parents=True, exist_ok=True)
SEEDS = (42, 43, 44)
if IN_COLAB and not SMOKE and not (BASE / "Dataset" / "tram_test.tsv").exists():
    _msg = (f"Project files not found under {BASE}. Upload the folder E:\\Osamas Paper\\_showcase\\drive_upload\\KDU into 'My Drive' "
            "(drive.google.com, same Google account as this Colab session), then run this cell again. See notebooks/COLAB_RUNBOOK.md, section 0.")
    if NOTEBOOK == "00_setup_and_verify": print("WARNING:", _msg)
    else: raise RuntimeError(_msg)

def set_seed(seed):
    random.seed(seed); np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True; torch.backends.cudnn.benchmark = False
    except ImportError:
        pass

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def env_info():
    info = {"python": platform.python_version(), "platform": platform.platform(), "in_colab": IN_COLAB, "smoke": SMOKE}
    try:
        import torch
        info.update(torch=torch.__version__, cuda=torch.cuda.is_available(), gpu=torch.cuda.get_device_name(0) if torch.cuda.is_available() else "none")
    except ImportError:
        pass
    return info

def write_manifest(run_id, system, seed, config, inputs, outputs, metrics, status):
    """One manifest per run: what went in, what came out, with hashes. Read later by the ingest step."""
    m = {"run_id": run_id, "system": system, "seed": seed, "config_hash": hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:16], "config": config,
         "env": {k: str(v) for k, v in env_info().items()}, "input_sha256": {str(p): sha256(p) for p in inputs if Path(p).exists()},
         "output_sha256": {str(p): sha256(p) for p in outputs if Path(p).exists()}, "metrics": {k: float(v) for k, v in metrics.items()},
         "status": "SMOKE" if SMOKE else status, "written": time.strftime("%Y-%m-%dT%H:%M:%S")}
    (OUT / f"manifest_{run_id}.json").write_text(json.dumps(m, indent=1)); return m

print(f"notebook={NOTEBOOK} | SMOKE={SMOKE} | IN_COLAB={IN_COLAB} | BASE={BASE} | OUT={OUT}")
print(env_info())
import importlib.metadata as _md
print("packages:", {p: (_md.version(p) if p in {d.metadata["Name"].lower() for d in _md.distributions() if d.metadata["Name"]} else "not installed")
                    for p in ("torch", "transformers", "scikit-learn", "numpy", "pandas", "shap", "scipy")})
_gpu = env_info().get("cuda", False)
if NEEDS_GPU and not _gpu and not SMOKE:
    raise RuntimeError("No GPU found. In Colab: Runtime > Change runtime type > T4 GPU > Save, then run this cell again. (Set SMOKE = True only for a dry run.)")
if not NEEDS_GPU and not _gpu:
    print("note: no GPU; this notebook runs on CPU in a few minutes")
'''

DATA = r'''
# ---- data, label space, gold matrices (same as Exp_1_4 CELL 4 and Exp_2.1 CELL 2) ----
def _labels(x): return sorted({str(t).strip().upper() for t in ast.literal_eval(x)})
def load_split(name):
    p = DATA_DIR / f"tram_{name}.tsv"
    if p.exists():
        df = pd.read_csv(p, sep="\t").rename(columns={"text1": "text"})
    elif name == "train":                                   # local fallback: the tram slice of combined_train.csv is the same data
        df = pd.read_csv(DATA_DIR / "combined_train.csv"); df = df[df["source_dataset"] == "tram"].rename(columns={"text1": "text"})
    else:
        raise FileNotFoundError(p)
    df = df[["text", "labels"]].copy(); df["labels"] = df["labels"].apply(_labels)
    return df.drop_duplicates(subset=["text"]).reset_index(drop=True) if name == "train" else df.reset_index(drop=True)

train, dev, test = (load_split(s) for s in ("train", "dev", "test"))
desc = pd.read_csv(DATA_DIR / "ttp-desc-mappings.csv", sep="\t")
desc["ttp"] = desc["ttp"].str.lower().str.strip()
desc["description"] = desc["description"].fillna("").str.replace(r"\s+", " ", regex=True).str.replace(r"\bcitation:\s*", "", regex=True).str.strip()
desc = desc.drop_duplicates("ttp"); desc = desc[~desc["ttp"].isin({"t1060", "t1107", "t1151", "t1188"})].reset_index(drop=True)
LABELS = [t.upper() for t in desc["ttp"]]; LABEL_TEXTS = desc["description"].tolist(); L = len(LABELS); lab2i = {l: i for i, l in enumerate(LABELS)}
def to_Y(df):
    Y = np.zeros((len(df), L), dtype=bool)
    for i, ys in enumerate(df["labels"]):
        for y in ys: Y[i, lab2i[y]] = True
    return Y
Y_train, Y_dev, Y_test = to_Y(train), to_Y(dev), to_Y(test)
train_count = Y_train.sum(0); SEEN = train_count > 0; seen_idx = np.where(SEEN)[0]
assert (len(train), len(dev), len(test), L, int(SEEN.sum())) == (3468, 604, 725, 733, 180), "unexpected data shape"
TEST_IDS = [f"test-{i:04d}" for i in range(len(test))]; DEV_IDS = [f"dev-{i:04d}" for i in range(len(dev))]
N_SMOKE = 20
print(f"train={len(train)} dev={len(dev)} test={len(test)} labels={L} seen={int(SEEN.sum())}")
'''

SCORES = r'''
# ---- saved model outputs + deterministic SVM refit ----
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC
vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True).fit(train["text"])
svm = OneVsRestClassifier(LinearSVC(C=1.0, random_state=42)).fit(vec.transform(train["text"]), Y_train[:, seen_idx].astype(int))
svm_raw = {"dev": svm.decision_function(vec.transform(dev["text"])), "test": svm.decision_function(vec.transform(test["text"]))}
cls_raw, cls_cols, cls_thr = {}, {}, {}
for tag in ("roberta", "secbert"):
    for s in SEEDS:
        p = CLS_ROOT / f"{tag}_pw_s{s}"
        cls_cols[tag, s] = np.array([lab2i[str(c).upper()] for c in np.load(p / "mlb_classes.npy", allow_pickle=True)])
        cls_raw[tag, s] = {"dev": np.load(p / "dev_probs.npy"), "test": np.load(p / "test_probs.npy")}
        cls_thr[tag, s] = json.load(open(p / "metrics.json"))["threshold"]
def matcher_dir(s):
    """Prefer the retrained matcher (with saved weights) when it exists; otherwise the original score files."""
    d = MATCH2 / f"ft20_s{s}"
    return d if (d / "test_scores.npy").exists() else MATCH_ROOT / f"ft20_s{s}"
m_raw = {s: {sp: np.load(matcher_dir(s) / f"{sp}_scores.npy") for sp in ("dev", "test")} for s in SEEDS}
MATCHER_SOURCE = {s: str(matcher_dir(s).parent.name) for s in SEEDS}
def components(split, mode="avg", seed=None):
    Z = {"svm": zrow(to_full(svm_raw[split], seen_idx, L))}
    for tag in ("roberta", "secbert"):
        Z[tag] = zrow(to_full(cls_raw[tag, seed][split], cls_cols[tag, seed], L)) if mode == "paired" else zrow(np.mean([to_full(cls_raw[tag, s][split], cls_cols[tag, s], L) for s in SEEDS], axis=0))
    Z["matcher"] = zrow(np.mean([m_raw[s][split] for s in SEEDS], axis=0)) if mode == "avg" else zrow(m_raw[seed][split])
    return Z
print("matcher scores from:", MATCHER_SOURCE)
'''

MATCHER = r'''
# ---- bi-encoder matcher: model, training WITH saved weights (Exp_2.1 CELL 3 settings) ----
import math, torch, torch.nn as nn, torch.nn.functional as Fnn
from transformers import AutoTokenizer, AutoModel, get_linear_schedule_with_warmup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
BASE_MODEL = "BAAI/bge-base-en-v1.5"

class Matcher(nn.Module):
    def __init__(self, name):
        super().__init__(); self.enc = AutoModel.from_pretrained(name)
    def forward(self, **enc):
        return Fnn.normalize(self.enc(**enc).last_hidden_state[:, 0].float(), dim=-1)

def tok_batch(tok, texts, max_len):
    enc = tok(list(texts), padding=True, truncation=True, max_length=max_len, return_tensors="pt")
    return {k: v.to(device) for k, v in enc.items() if k in ("input_ids", "attention_mask", "token_type_ids")}

@torch.no_grad()
def embed_all(model, tok, texts, max_len, bs=64, amp=True):
    model.eval(); out = []
    for i in range(0, len(texts), bs):
        with torch.autocast(device_type=device.type, dtype=torch.float16, enabled=amp and device.type == "cuda"):
            out.append(model(**tok_batch(tok, texts[i:i + bs], max_len)).float().cpu())
    return torch.cat(out).numpy()

def matcher_metrics(S, Y):
    return {"P@1": float(hit_at_1(S, Y).mean()), "MRR@3": float(rr_at_k(S, Y, 3).mean()), "R@5": recall_at_k_micro(S, Y, 5)}

def train_matcher_save(out_dir, seed, epochs=20, patience=4, batch_size=16, lr=2e-5, n_neg=64, scale=30.0, text_max_len=128, label_max_len_train=128, label_max_len_eval=256,
                       tr=None, Ytr=None, dv=None, Ydv=None, te=None, Yte=None):
    """Resumable per epoch: best weights -> matcher_state.pt ; last state -> ckpt_last.pt (both on Drive)."""
    tr = train if tr is None else tr; Ytr = Y_train if Ytr is None else Ytr; dv = dev if dv is None else dv; Ydv = Y_dev if Ydv is None else Ydv; te = test if te is None else te; Yte = Y_test if Yte is None else Yte
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True); set_seed(seed); rng = np.random.default_rng(seed); amp_on = device.type == "cuda"
    tok = AutoTokenizer.from_pretrained(BASE_MODEL); model = Matcher(BASE_MODEL).to(device)
    N = len(tr); texts = tr["text"].tolist(); label_texts = np.array(LABEL_TEXTS, dtype=object); pos_lists = [np.where(Ytr[i])[0] for i in range(N)]; pool = np.arange(L)
    steps = math.ceil(N / batch_size); opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    sched = get_linear_schedule_with_warmup(opt, int(0.1 * steps * epochs), steps * epochs); scaler = torch.amp.GradScaler(enabled=amp_on)
    st = {"epoch": 0, "best": -1.0, "best_ep": 0, "bad": 0, "hist": []}; ck = out_dir / "ckpt_last.pt"
    if ck.exists():
        c = torch.load(ck, map_location="cpu", weights_only=False); model.load_state_dict(c["model"]); opt.load_state_dict(c["opt"]); sched.load_state_dict(c["sched"])
        rng.bit_generator.state = c["rng"]; st = c["state"]; print("  resumed after epoch", st["epoch"])
    def evaluate():
        le = embed_all(model, tok, LABEL_TEXTS, label_max_len_eval)
        Sd = embed_all(model, tok, list(dv["text"]), text_max_len) @ le.T; St = embed_all(model, tok, list(te["text"]), text_max_len) @ le.T
        return Sd, St, matcher_metrics(Sd, Ydv), matcher_metrics(St, Yte)
    for ep in range(st["epoch"] + 1, epochs + 1):
        if st["bad"] >= patience: break
        model.train(); perm = rng.permutation(N); tot = 0.0; t0 = time.time()
        for b in range(0, N, batch_size):
            idx = perm[b:b + batch_size]; gold_u = np.unique(np.concatenate([pos_lists[i] for i in idx])); cand = np.setdiff1d(pool, gold_u)
            U = np.concatenate([gold_u, rng.choice(cand, size=min(n_neg, len(cand)), replace=False)])
            with torch.autocast(device_type=device.type, dtype=torch.float16, enabled=amp_on):
                et = model(**tok_batch(tok, [texts[i] for i in idx], text_max_len)); eu = model(**tok_batch(tok, label_texts[U].tolist(), label_max_len_train))
            S = (et @ eu.T) * scale; pos = torch.tensor(Ytr[idx][:, U], device=device)
            neg_lse = torch.logsumexp(S.masked_fill(pos, -1e4), dim=1); rows = pos.nonzero()[:, 0]
            loss = Fnn.softplus(neg_lse[rows] - S[pos]).mean()
            opt.zero_grad(); scaler.scale(loss).backward(); scaler.unscale_(opt); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(opt); scaler.update(); sched.step(); tot += loss.item() * len(idx)
        Sd, St, md, mt = evaluate(); st["hist"].append({"epoch": ep, "train_loss": tot / N, **{f"dev_{k}": v for k, v in md.items()}})
        print(f"  epoch {ep:2d}: loss={tot / N:.4f} dev P@1={md['P@1']:.4f} MRR@3={md['MRR@3']:.4f} ({time.time() - t0:.0f}s)")
        if md["MRR@3"] > st["best"]:
            st.update(best=md["MRR@3"], best_ep=ep, bad=0)
            torch.save({k: v.detach().cpu() for k, v in model.state_dict().items()}, out_dir / "matcher_state.pt")
            np.save(out_dir / "dev_scores.npy", Sd); np.save(out_dir / "test_scores.npy", St)
            cfg = dict(epochs=epochs, patience=patience, batch_size=batch_size, lr=lr, n_neg=n_neg, scale=scale, text_max_len=text_max_len, label_max_len_train=label_max_len_train, pooling="cls", neg_pool="all")
            json.dump({"model_name": BASE_MODEL, "seed": seed, "best_epoch": ep, "dev": md, "test": mt, "history": st["hist"], "config": cfg, "finished": False}, open(out_dir / "metrics.json", "w"), indent=1)
        else:
            st["bad"] += 1
        st["epoch"] = ep
        torch.save({"model": model.state_dict(), "opt": opt.state_dict(), "sched": sched.state_dict(), "rng": rng.bit_generator.state, "state": st}, ck)
    m = json.load(open(out_dir / "metrics.json")); m["finished"] = True; m["history"] = st["hist"]; json.dump(m, open(out_dir / "metrics.json", "w"), indent=1)
    del model, opt; import gc; gc.collect(); torch.cuda.empty_cache()
    return m
'''


def header(num, title, purpose, inputs, outputs, runtime, fills, extra=""):
    return (f"# {num} {title}\n\n**Status: NOT RUN ON COLAB.** Generated by `scripts/make_notebooks.py`. Any output cells in the repository copy come from a local CPU "
            f"smoke run (`SMOKE=True`, {'20'} samples), never from a real run.\n\n| | |\n|---|---|\n| Purpose | {purpose} |\n| Inputs | {inputs} |\n| Outputs | {outputs} |\n"
            f"| Runtime (T4 GPU, estimate) | {runtime} |\n| Fills in `thesis_numbers.json` | {fills} |\n\nRun the cells top to bottom. Set `SMOKE = True` in the setup cell for a dry run on 20 samples. "
            f"Every run writes a manifest with input and output hashes; the last cell prints an evidence table read from the saved files.\n{extra}")


def build(name, cells):
    nb = nbf.v4.new_notebook(metadata={"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "accelerator": "GPU"})
    for kind, src in cells:
        nb.cells.append(nbf.v4.new_markdown_cell(src.strip()) if kind == "md" else nbf.v4.new_code_cell(src.strip("\n")))
    nbf.validate(nb); nbf.write(nb, NB / f"{name}.ipynb")


GPU_NOTEBOOKS = {"02_baselines", "03_train_classifiers", "04_train_matcher_save", "06_explainability", "08_extension_cross_dataset"}


def setup(name, pip=""):
    pre = f'NOTEBOOK = "{name}"\nNEEDS_GPU = {name in GPU_NOTEBOOKS}      # True: the notebook stops at once if Colab gave no GPU\n'
    if pip:
        pre += ("import sys, subprocess\nif 'google.colab' in sys.modules:      # pinned installs, Colab only\n"
                f"    subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', {pip}], check=False)\n")
    return pre + SETUP


EVID = r'''
# ---- evidence table: read back from the files this notebook wrote (no typed numbers) ----
rows = []
for p in sorted(OUT.glob("*.json")):
    d = json.loads(p.read_text())
    flat = d.get("metrics", d) if isinstance(d, dict) else {}
    for k, v in flat.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool): rows.append({"file": p.name, "key": k, "value": round(float(v), 4)})
ev = pd.DataFrame(rows)
print(f"status: {'SMOKE (not a result)' if SMOKE else 'RUN'} | files in {OUT}: {len(list(OUT.glob('*')))}")
print(ev.to_string(index=False) if len(ev) else "no numeric outputs")
'''

# ============================== 00 ==============================
build("00_setup_and_verify", [("md", header("00", "Setup and verification", "Mount Drive, check every input file, record the environment and GPU.", "`MyDrive/KDU/Thesis/` (Dataset, run folders)",
      "`showcase_runs/00_setup_and_verify/env_colab.json`, `input_hashes.json`", "1 min", "T7.env_colab")),
    ("code", setup("00_setup_and_verify")),
    ("code", r'''
need = [DATA_DIR / "tram_dev.tsv", DATA_DIR / "tram_test.tsv", DATA_DIR / "ttp-desc-mappings.csv", DATA_DIR / "combined_train.csv", SHAP_DIR / "shap_v2_roberta_pw_s42.jsonl",
        MATCH_ROOT / "zeroshot" / "test_scores.npy"] + [CLS_ROOT / f"{t}_pw_s{s}" / f for t in ("roberta", "secbert") for s in SEEDS for f in ("test_probs.npy", "dev_probs.npy", "metrics.json", "mlb_classes.npy")] \
       + [MATCH_ROOT / f"ft20_s{s}" / f"{sp}_scores.npy" for s in SEEDS for sp in ("dev", "test")]
optional = [DATA_DIR / "tram_train.tsv"] + [CLS_ROOT / f"{t}_pw_s42" / "model.safetensors" for t in ("roberta", "secbert")] + [MATCH2 / "ft20_s42" / "matcher_state.pt"]
missing = [str(p) for p in need if not p.exists()]
print("required files:", len(need), "| missing:", len(missing)); [print("  MISSING", m) for m in missing]
for p in optional: print(("  present " if p.exists() else "  absent  ") + str(p))
hashes = {str(p.relative_to(BASE)): sha256(p) for p in need if p.exists() and p.stat().st_size < 50e6}
(OUT / "input_hashes.json").write_text(json.dumps(hashes, indent=1))
'''),
    ("code", r'''
pkgs = {}
try:
    import importlib.metadata as md
    pkgs = {d.metadata["Name"]: d.version for d in md.distributions() if d.metadata["Name"]}
except Exception as e:
    print("package listing failed:", e)
gpu = ""
try:
    gpu = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"], capture_output=True, text=True, timeout=30).stdout.strip()
except Exception:
    gpu = "nvidia-smi not available"
env = {**env_info(), "nvidia_smi": gpu, "n_packages": len(pkgs), "packages": dict(sorted(pkgs.items())), "missing_required_files": missing}
(OUT / ("env_colab.json" if IN_COLAB else "env_local.json")).write_text(json.dumps(env, indent=1))
print({k: v for k, v in env.items() if k != "packages"})
'''), ("code", EVID)])

# ============================== 01 ==============================
build("01_data_audit", [("md", header("01", "Data audit", "Recompute split sizes, label counts, seen/unseen labels, exact overlap and token lengths from the raw files.",
      "Dataset files", "`data_audit.json`", "2 min (CPU is enough)", "re-checks A1-A8")),
    ("code", setup("01_data_audit")), ("code", DATA),
    ("code", r'''
norm = lambda s: re.sub(r"\s+", " ", str(s).lower()).strip()
nset = {k: set(map(norm, d["text"])) for k, d in (("train", train), ("dev", dev), ("test", test))}
audit = {"n_train": len(train), "n_dev": len(dev), "n_test": len(test), "train_labels": int(SEEN.sum()), "test_labels": int((Y_test.sum(0) > 0).sum()),
         "test_labels_seen": int(((Y_test.sum(0) > 0) & SEEN).sum()), "test_labels_unseen": int(((Y_test.sum(0) > 0) & ~SEEN).sum()),
         "exact_overlap_train_test": len(nset["train"] & nset["test"]), "exact_overlap_train_dev": len(nset["train"] & nset["dev"]), "exact_overlap_dev_test": len(nset["dev"] & nset["test"]),
         "multi_label_test": int((Y_test.sum(1) > 1).sum()), "gold_pairs_test": int(Y_test.sum()), "labels_in_space": L}
try:
    from transformers import AutoTokenizer
    for nm, src in (("roberta", CLS_ROOT / "roberta_pw_s42"), ("secbert", CLS_ROOT / "secbert_pw_s42")):
        tk = AutoTokenizer.from_pretrained(str(src) if (src / "tokenizer.json").exists() else {"roberta": "roberta-base", "secbert": "jackaduma/SecBERT"}[nm])
        tx = list(test["text"])[:N_SMOKE] if SMOKE else list(test["text"])
        ln = np.array([len(x) for x in tk(tx, truncation=False)["input_ids"]])
        audit[f"test_over_128_{nm}"] = int((ln > 128).sum()); audit[f"test_mean_tokens_{nm}"] = float(ln.mean())
except Exception as e:
    print("token lengths skipped:", type(e).__name__, e)
(OUT / "data_audit.json").write_text(json.dumps({"metrics": audit}, indent=1))
write_manifest("data_audit", "data", "-", {"smoke": SMOKE}, [DATA_DIR / "tram_test.tsv", DATA_DIR / "tram_dev.tsv"], [OUT / "data_audit.json"], audit, "DONE")
'''), ("code", EVID)])

# ============================== 02 ==============================
build("02_baselines", [("md", header("02", "Baselines", "Frequency prior, TF-IDF + linear SVM, zero-shot bge matcher, all scored with the shared metric code.",
      "Dataset files; `BAAI/bge-base-en-v1.5` from the Hugging Face hub", "`baselines.json`, `zeroshot_test_scores.npy`", "5 min", "re-checks B0, B3, B6, B10a")),
    ("code", setup("02_baselines")), ("code", DATA), ("code", LIB), ("code", MATCHER),
    ("code", r'''
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC
res = {}
te = test.iloc[:N_SMOKE] if SMOKE else test; Yt = Y_test[:len(te)]
prior = np.tile(train_count.astype(float), (len(te), 1)); res["prior_P@1"] = float(hit_at_1(prior, Yt).mean()); res["prior_MRR@3"] = float(rr_at_k(prior, Yt).mean())
vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True).fit(train["text"])
svm = OneVsRestClassifier(LinearSVC(C=1.0, random_state=42)).fit(vec.transform(train["text"]), Y_train[:, seen_idx].astype(int))
sd, st_ = svm.decision_function(vec.transform(dev["text"])), svm.decision_function(vec.transform(te["text"]))
thr = select_threshold(sd, Y_dev[:, seen_idx], np.arange(-0.6, 0.31, 0.05), split="dev")
P = np.zeros((len(te), L), bool); P[:, seen_idx] = apply_threshold(st_.copy(), thr)
res["svm_threshold"] = thr; res["svm_P@1"] = float(hit_at_1(to_full(st_, seen_idx, L, -1e9), Yt).mean()); res["svm_MRR@3"] = float(rr_at_k(to_full(st_, seen_idx, L, -1e9), Yt).mean())
for v in ("notebook", "seen_test", "all_test"):
    f = f1_scores(P, Yt, SEEN, v); res[f"svm_micro_f1_{v}"] = f["micro_f1"]; res[f"svm_macro_f1_{v}"] = f["macro_f1"]
'''),
    ("code", r'''
# zero-shot matcher (no training). CPU works but is slow for all 733 descriptions; in SMOKE mode descriptions are cut to 64 tokens.
tok0 = AutoTokenizer.from_pretrained(BASE_MODEL); m0 = Matcher(BASE_MODEL).to(device)
le = embed_all(m0, tok0, LABEL_TEXTS, 64 if SMOKE else 256); S0 = embed_all(m0, tok0, list(te["text"]), 128) @ le.T
res["zeroshot_P@1"] = float(hit_at_1(S0, Yt).mean()); res["zeroshot_MRR@3"] = float(rr_at_k(S0, Yt).mean())
np.save(OUT / "zeroshot_test_scores.npy", S0); del m0
(OUT / "baselines.json").write_text(json.dumps({"metrics": res}, indent=1))
write_manifest("baselines", "prior+svm+zeroshot", "-", {"smoke": SMOKE, "label_max_len": 64 if SMOKE else 256}, [DATA_DIR / "tram_test.tsv"], [OUT / "baselines.json", OUT / "zeroshot_test_scores.npy"], res, "DONE")
'''), ("code", EVID)])

# ============================== 03 ==============================
build("03_train_classifiers", [("md", header("03", "Train classifiers (new seeds 45 and 46)", "Train RoBERTa and SecBERT with the unchanged settings of `Exp_1_4` for the pre-registered new seeds; save probabilities AND weights. Seeds 42-44 are never touched.",
      "Dataset files (needs `tram_train.tsv` or `combined_train.csv`)", "`showcase_runs/03_train_classifiers/<model>_pw_s<seed>/` (probabilities, metrics, weights), manifests", "about 15-25 min per run, 4 runs (estimate; the original notebooks print no timing)",
      "T4.seeds_45_46", "\nPre-registration: `experiments/prereg/10_new_seeds_45_46.md`. Optional switch `MAX_LENGTH = 256` trains the 256-token variant into a separate folder.")),
    ("code", setup("03_train_classifiers")), ("code", DATA), ("code", LIB),
    ("code", r'''
import torch, torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification, get_linear_schedule_with_warmup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODELS = {"roberta": "roberta-base", "secbert": "jackaduma/SecBERT"}
NEW_SEEDS = (45, 46); MAX_LENGTH = 128; PROB_GRID = np.arange(0.1, 0.9, 0.05)
Ytr, Ydv, Yte = (Y[:, seen_idx].astype(np.float32) for Y in (Y_train, Y_dev, Y_test))      # the classifiers' 180-label space

class DS(Dataset):
    def __init__(self, texts, Y, tok, max_length): self.enc = tok(list(texts), truncation=True, max_length=max_length); self.Y = Y
    def __len__(self): return len(self.Y)
    def __getitem__(self, i): return {**{k: v[i] for k, v in self.enc.items()}, "labels": self.Y[i]}
def collate_fn(tok):
    def f(batch):
        enc = tok.pad([{k: v for k, v in b.items() if k != "labels"} for b in batch], return_tensors="pt"); enc["labels"] = torch.tensor(np.stack([b["labels"] for b in batch])); return enc
    return f
def run_epoch(model, loader, loss_fn, opt=None, sched=None):
    model.train() if opt else model.eval(); probs = []
    with torch.set_grad_enabled(opt is not None):
        for batch in loader:
            batch = {k: v.to(device) for k, v in batch.items()}; y = batch.pop("labels"); logits = model(**batch).logits; loss = loss_fn(logits, y)
            if opt: opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step(); sched.step()
            probs.append(torch.sigmoid(logits).detach().cpu().numpy())
    return np.concatenate(probs)

def train_model(tag, seed, out_dir, epochs=30, patience=5, batch_size=16, lr=2e-5, head_lr=1e-3, max_length=128, pos_weight_cap=20.0, tr_idx=None, dv_idx=None, te_idx=None):
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True); set_seed(seed)
    tri = np.arange(len(train)) if tr_idx is None else tr_idx; dvi = np.arange(len(dev)) if dv_idx is None else dv_idx; tei = np.arange(len(test)) if te_idx is None else te_idx
    tok = AutoTokenizer.from_pretrained(MODELS[tag]); col = collate_fn(tok)
    mk = lambda df, Y, idx, sh: DataLoader(DS(df["text"].iloc[idx], Y[idx], tok, max_length), batch_size=batch_size if sh else 2 * batch_size, shuffle=sh, collate_fn=col)
    trl, dvl, tel = mk(train, Ytr, tri, True), mk(dev, Ydv, dvi, False), mk(test, Yte, tei, False)
    model = AutoModelForSequenceClassification.from_pretrained(MODELS[tag], num_labels=Ytr.shape[1], problem_type="multi_label_classification").to(device)
    pos = np.clip(Ytr[tri].sum(0), 1, None); pw = torch.tensor(np.clip((len(tri) - pos) / pos, None, pos_weight_cap), dtype=torch.float, device=device)
    loss_fn = nn.BCEWithLogitsLoss(pos_weight=pw)
    head = [p for n_, p in model.named_parameters() if n_.startswith("classifier.")]; body = [p for n_, p in model.named_parameters() if not n_.startswith("classifier.")]
    opt = torch.optim.AdamW([{"params": body, "lr": lr}, {"params": head, "lr": head_lr}]); total = len(trl) * epochs
    sched = get_linear_schedule_with_warmup(opt, int(0.1 * total), total)
    st = {"ep": 0, "best": -1.0, "best_ep": 0, "bad": 0, "hist": []}; ck, bk = out_dir / "ckpt_last.pt", out_dir / "best_state.pt"
    if ck.exists():                                                          # resume after a disconnect: state is on Drive
        c = torch.load(ck, map_location="cpu", weights_only=False); model.load_state_dict(c["model"]); opt.load_state_dict(c["opt"]); sched.load_state_dict(c["sched"]); st = c["st"]
        print("  resumed after epoch", st["ep"])
    for ep in range(st["ep"] + 1, epochs + 1):
        if st["bad"] >= patience: break
        run_epoch(model, trl, loss_fn, opt, sched); dp = run_epoch(model, dvl, loss_fn)
        t = select_threshold(dp, Ydv[dvi].astype(bool), PROB_GRID, split="dev"); Pd = apply_threshold(dp.copy(), t)
        tp = (Pd & Ydv[dvi].astype(bool)).sum(); f1 = 2 * tp / max(Pd.sum() + Ydv[dvi].sum(), 1); st["hist"].append({"epoch": ep, "dev_micro_f1": float(f1)}); print(f"  epoch {ep:2d}: dev micro-F1 {f1:.4f}")
        if f1 > st["best"]: st.update(best=float(f1), best_ep=ep, bad=0); torch.save({k: v.detach().cpu() for k, v in model.state_dict().items()}, bk)
        else: st["bad"] += 1
        st["ep"] = ep; torch.save({"model": model.state_dict(), "opt": opt.state_dict(), "sched": sched.state_dict(), "st": st}, ck)      # written to Drive every epoch
    best_ep, hist = st["best_ep"], st["hist"]
    model.load_state_dict(torch.load(bk, map_location="cpu")); dp = run_epoch(model, dvl, loss_fn); tp_ = run_epoch(model, tel, loss_fn)
    thr = select_threshold(dp, Ydv[dvi].astype(bool), PROB_GRID, split="dev")
    Pf = np.zeros((len(tei), L), bool); Pf[:, seen_idx] = apply_threshold(tp_.copy(), thr); Yt = Y_test[tei]
    met = {**{f"{k}_{v}": f1_scores(Pf, Yt, SEEN, v)[k] for v in ("notebook", "all_test") for k in ("micro_f1", "macro_f1")},
           "P@1": float(hit_at_1(to_full(tp_, seen_idx, L, -1e9), Yt).mean()), "MRR@3": float(rr_at_k(to_full(tp_, seen_idx, L, -1e9), Yt).mean()), "threshold": thr, "best_epoch": best_ep}
    np.save(out_dir / "dev_probs.npy", dp); np.save(out_dir / "test_probs.npy", tp_); np.save(out_dir / "mlb_classes.npy", np.array(LABELS, dtype=object)[seen_idx])
    cfg = dict(epochs=epochs, patience=patience, batch_size=batch_size, lr=lr, head_lr=head_lr, max_length=max_length, use_pos_weight=True, pos_weight_cap=pos_weight_cap)
    json.dump({"model_name": MODELS[tag], "seed": seed, "best_epoch": best_ep, "threshold": thr, "test": met, "history": hist, "config": cfg}, open(out_dir / "metrics.json", "w"), indent=1)
    model.save_pretrained(out_dir); tok.save_pretrained(out_dir)                         # weights saved
    ck.unlink(missing_ok=True)                                                           # run finished: drop the resume checkpoint (best weights stay)
    write_manifest(f"{tag}_pw_s{seed}", tag, seed, cfg, [DATA_DIR / "tram_test.tsv"], [out_dir / "test_probs.npy", out_dir / "dev_probs.npy", out_dir / "metrics.json"], met, "DONE")
    del model, opt; import gc; gc.collect(); torch.cuda.empty_cache(); return met
'''),
    ("code", r'''
if SMOKE and device.type != "cuda":
    print("SMOKE on CPU: training is GPU-only and is skipped here. Data, label space and the training function were defined without error.")
    (OUT / "smoke_note.json").write_text(json.dumps({"metrics": {"training_cells_skipped": 1}}))
else:
    for seed in ((45,) if SMOKE else NEW_SEEDS):
        for tag in MODELS:
            out = OUT / (f"{tag}_pw_s{seed}" + ("" if MAX_LENGTH == 128 else f"_L{MAX_LENGTH}"))
            if (out / "metrics.json").exists(): print("skip (result file exists):", out); continue
            kw = dict(epochs=1, tr_idx=np.arange(N_SMOKE), dv_idx=np.arange(N_SMOKE), te_idx=np.arange(N_SMOKE)) if SMOKE else {}
            print(f">>> {tag} seed {seed}"); print("  TEST:", train_model(tag, seed, out, max_length=MAX_LENGTH, **kw))
'''), ("code", EVID)])

# ============================== 04 ==============================
build("04_train_matcher_save", [("md", header("04", "Train the matcher and SAVE the weights", "Retrain the bge bi-encoder with the unchanged settings of `Exp_2.1` and save the weights the original notebook never saved. Seed 42 first (needed by notebooks 05 and 06), then 43-46.",
      "Dataset files; `BAAI/bge-base-en-v1.5`", "`MyDrive/KDU/Thesis/run_match_2_saved/ft20_s<seed>/` (`matcher_state.pt`, score files, `metrics.json`), manifests", "20-30 min per seed (the original notebook's own estimate)",
      "T1.matcher_retrained_p1; with seeds 45-46: T4.seeds_45_46", "\nGPU nondeterminism means the retrained scores are not bit-identical to `run_match_1`; the retrained matcher's own test P@1 is reported next to the original. Resumable: a checkpoint is written to Drive after every epoch.")),
    ("code", setup("04_train_matcher_save")), ("code", DATA), ("code", LIB), ("code", MATCHER),
    ("code", r'''
SEED_ORDER = (42, 43, 44, 45, 46)          # 42 first: it unblocks notebooks 05 and 06
def run_seed(sd):
    out = MATCH2 / f"ft20_s{sd}"
    if (out / "metrics.json").exists() and json.load(open(out / "metrics.json")).get("finished"): print("skip (done):", out); return
    m = train_matcher_save(out, sd)
    write_manifest(f"matcher_ft20_s{sd}", "matcher", sd, m["config"], [DATA_DIR / "tram_test.tsv"], [out / "matcher_state.pt", out / "test_scores.npy", out / "dev_scores.npy", out / "metrics.json"], m["test"], "DONE")
    print("  TEST", m["test"], "best epoch", m["best_epoch"])
if SMOKE:
    k = N_SMOKE if device.type == "cuda" else 8                      # tiny run that exercises training, evaluation, saving and resuming
    m = train_matcher_save(OUT / "smoke_matcher", 42, epochs=1, batch_size=4, n_neg=4, label_max_len_train=32, label_max_len_eval=32,
                           tr=train.iloc[:k], Ytr=Y_train[:k], dv=dev.iloc[:k], Ydv=Y_dev[:k], te=test.iloc[:k], Yte=Y_test[:k])
    write_manifest("smoke_matcher", "matcher", 42, m["config"], [], [OUT / "smoke_matcher" / "matcher_state.pt", OUT / "smoke_matcher" / "test_scores.npy"], m["test"], "SMOKE")
    (OUT / "smoke_matcher" / "matcher_state.pt").unlink(missing_ok=True); (OUT / "smoke_matcher" / "ckpt_last.pt").unlink(missing_ok=True)     # do not keep 400 MB smoke weights
else:
    run_seed(SEED_ORDER[0])
'''),
    ("code", r'''
# remaining seeds (run after notebooks 06 and 05 if time is short)
if not SMOKE:
    for sd in SEED_ORDER[1:]: run_seed(sd)
'''), ("code", EVID)])

# ============================== 05 ==============================
build("05_fusion_and_ablation", [("md", header("05", "Fusion and ablation (replication with the retrained matcher)", "Recompute the fusion with dev-tuned weights on both grids, the three headline definitions and the ablation. Uses the retrained matcher where `run_match_2_saved` exists, the original score files otherwise, and says which.",
      "saved classifier probabilities; matcher score files", "`fusion_replication.json`, `weight_grid_dev.csv`", "1 min (CPU)", "T3.fusion_replication")),
    ("code", setup("05_fusion_and_ablation")), ("code", DATA), ("code", LIB), ("code", SCORES),
    ("code", r'''
res = {}; Zd42, Zt42 = components("dev", "nb_seed", 42), components("test", "nb_seed", 42)
rows = []
for gname, grid in (("coarse", coarse_grid()), ("wide", wide_grid())):
    w, key = select_weights(Zd42, Y_dev, grid, split="dev", sentence_ids=DEV_IDS, forbidden_ids=TEST_IDS)        # dev only; test ids are rejected by the guard
    res[f"{gname}_n_settings"] = len(grid); res[f"{gname}_dev_MRR@3"] = key[0]
    for i, n_ in enumerate(ORDER): res[f"{gname}_w_{n_}"] = w[i]
    res[f"{gname}_test_P@1"] = float(hit_at_1(fuse(Zt42, w), Y_test).mean())
    rows += [{"grid": gname, "w": str(g), "dev_MRR@3": round(float(rr_at_k(fuse(Zd42, g), Y_dev).mean()), 4)} for g in (grid[:50] if SMOKE else grid)]
pd.DataFrame(rows).to_csv(OUT / "weight_grid_dev.csv", index=False)
Za = components("test", "avg"); W = (3, 1, 1, 1)
res["fusion_seed_averaged_P@1"] = float(hit_at_1(fuse(Za, W), Y_test).mean()); res["fusion_seed_averaged_MRR@3"] = float(rr_at_k(fuse(Za, W), Y_test).mean())
for mode, nm in (("paired", "fusion_seed_paired"), ("nb_seed", "fusion_matcher_seed_varied")):
    v = [float(hit_at_1(fuse(components("test", mode, s), W), Y_test).mean()) for s in SEEDS]; res[f"{nm}_P@1_mean"] = float(np.mean(v)); res[f"{nm}_P@1_sd"] = float(np.std(v, ddof=1))
res["classifiers_only_P@1"] = float(hit_at_1(fuse(Za, (0, 1, 1, 1)), Y_test).mean()); res["matcher_ensemble_P@1"] = float(hit_at_1(Za["matcher"], Y_test).mean())
full = hit_at_1(fuse(Za, W), Y_test); ps = []
for i, n_ in enumerate(ORDER):
    h = hit_at_1(fuse(Za, tuple(0 if j == i else x for j, x in enumerate(W))), Y_test); res[f"without_{n_}_P@1"] = float(h.mean()); ps.append(mcnemar_exact(full, h)["p"])
for n_, p in zip(ORDER, holm(ps)): res[f"without_{n_}_holm_p"] = p
res["matcher_is_retrained"] = float(all(v == "run_match_2_saved" for v in MATCHER_SOURCE.values()))
(OUT / "fusion_replication.json").write_text(json.dumps({"metrics": res, "matcher_source": MATCHER_SOURCE}, indent=1))
write_manifest("fusion_replication", "fusion", "avg", {"weights": W, "matcher_source": MATCHER_SOURCE}, [matcher_dir(s) / "test_scores.npy" for s in SEEDS], [OUT / "fusion_replication.json"], res, "DONE")
'''), ("code", EVID)])

# ============================== 06 ==============================
build("06_explainability", [("md", header("06", "Explainability of the full fusion", "Word-level permutation SHAP of the fused score (same method as the stored RoBERTa run: whitespace words, mask token, 40 permutations, seed 42) and a deletion test on the fused score.",
      "classifier checkpoints seed 42; retrained matcher weights from notebook 04; stored RoBERTa SHAP file", "`fusion_shap_full_s42.jsonl`, `fusion_shap_summary.json`", "30-60 min for 100 sentences (estimate)", "T2.full_fusion_shap",
      "\nPre-registration: `experiments/prereg/12_full_fusion_shap.md`.\n\n**Why no linearity shortcut over stored SHAP values.** The fused score is a weighted sum of per-sentence z-scores. The z-score mean and standard deviation are recomputed for every "
      "perturbed sentence, so they are *not* constants and SHAP values of raw model outputs cannot simply be rescaled. The notebook first asserts this (cell 'z statistics'), then explains each component's **z-scored output** in one permutation run "
      "and sums the per-component values with the fusion weights, which is exact because Shapley values are linear in the explained output.")),
    ("code", setup("06_explainability", "'shap==0.54.1'")), ("code", DATA), ("code", LIB), ("code", SCORES), ("code", MATCHER),
    ("code", r'''
import shap
from transformers import AutoModelForSequenceClassification
SEED = 42; N_SHAP = 2 if SMOKE else 100; N_PERM, SHAP_SEED, MAX_LEN, K_HIDE, N_RANDOM = 40, 42, 128, 3, 20
texts_te = test["text"].tolist(); LAB = np.array(LABELS); OOV = "zzzmaskzzz"; assert OOV not in vec.vocabulary_
class Clf:
    def __init__(self, tag):
        d = CLS_ROOT / f"{tag}_pw_s{SEED}"; self.tok = AutoTokenizer.from_pretrained(str(d)); self.model = AutoModelForSequenceClassification.from_pretrained(str(d)).float().to(device).eval()
        self.cols = cls_cols[tag, SEED]; self.mask = self.tok.mask_token; self.name = f"{tag}_s{SEED}"
    @torch.no_grad()
    def raw(self, tx):
        out = []
        for s in range(0, len(tx), 64):
            enc = self.tok(tx[s:s + 64], truncation=True, max_length=MAX_LEN, padding=True, return_tensors="pt").to(device); out.append(torch.sigmoid(self.model(**enc).logits).cpu().numpy())
        return to_full(np.concatenate(out), self.cols, L)
    def z(self, tx): return zrow(self.raw(tx))
class SvmC:
    name, mask = "svm", OOV
    def raw(self, tx): return to_full(svm.decision_function(vec.transform(tx)), seen_idx, L)
    def z(self, tx): return zrow(self.raw(tx))
class MatcherC:
    name = "matcher"
    def __init__(self, state):
        self.tok = AutoTokenizer.from_pretrained(BASE_MODEL); self.model = Matcher(BASE_MODEL); self.model.load_state_dict(torch.load(state, map_location="cpu")); self.model = self.model.float().to(device).eval()
        self.mask = self.tok.mask_token; self.label_emb = embed_all(self.model, self.tok, LABEL_TEXTS, 256, amp=False)
    def raw(self, tx): return embed_all(self.model, self.tok, list(tx), MAX_LEN, amp=False) @ self.label_emb.T
    def z(self, tx): return zrow(self.raw(tx))
comps = [SvmC(), Clf("roberta"), Clf("secbert")]; weights = [1.0, 1.0, 1.0]
state = MATCH2 / f"ft20_s{SEED}" / "matcher_state.pt"
if state.exists(): comps.insert(0, MatcherC(state)); weights.insert(0, 3.0)
FULL = state.exists()
SYSTEM = ("fusion (3,1,1,1) seed-paired, retrained matcher" if FULL else "classifiers-only part (0,1,1,1): matcher weights not found, run notebook 04 first") + f", seed {SEED}"
print("explaining:", SYSTEM)
'''),
    ("code", r'''
# z statistics: are the per-row mean and sd constant under masking? (prereg 12 requires this check before any linearity shortcut)
UNIT_RE = re.compile(r"(\s*)(\S+)(\s*)")
order = [int(r) for r in np.random.RandomState(42).permutation(725)[:N_SHAP]]
probe = str(texts_te[order[0]]); parts0 = [m.groups() for m in UNIT_RE.finditer(probe)]
c0 = comps[-1]; masked0 = "".join(l + (c0.mask if i == 0 else w) + t for i, (l, w, t) in enumerate(parts0))
r_full, r_mask = c0.raw([probe])[0], c0.raw([masked0])[0]
Z_CONSTANT = bool(np.isclose(np.nanmean(r_full), np.nanmean(r_mask), atol=1e-9) and np.isclose(np.nanstd(r_full), np.nanstd(r_mask), atol=1e-9))
print(f"z-score statistics constant under masking: {Z_CONSTANT} (mean {np.nanmean(r_full):.5f} -> {np.nanmean(r_mask):.5f}, sd {np.nanstd(r_full):.5f} -> {np.nanstd(r_mask):.5f})")
print("=> " + ("stored raw-output SHAP values could be rescaled" if Z_CONSTANT else "no rescaling shortcut: each component's z-scored output is explained directly and summed with the weights"))
'''),
    ("code", r'''
stored = {}
if (SHAP_DIR / "shap_v2_roberta_pw_s42.jsonl").exists():
    for l in open(SHAP_DIR / "shap_v2_roberta_pw_s42.jsonl", encoding="utf-8"):
        if l.strip():
            r = json.loads(l); stored[r["row"]] = r
SHAP_OUT = OUT / ("fusion_shap_full_s42.jsonl" if FULL else "fusion_shap_partial_s42.jsonl")
def comp_scores(parts, keeps, k):
    return np.stack([c.z(["".join(l + (w if kp else c.mask) + t for (l, w, t), kp in zip(parts, keep)) for keep in keeps])[:, k] for c in comps], axis=1)
def removed(parts, hide, original):
    s = "".join(l + w + t for i, (l, w, t) in enumerate(parts) if i not in hide); return s.rstrip() if (len(parts) - 1) in hide and not original[-1:].isspace() else s
def fused_plain(tx, k): return sum(w * c.z(tx)[:, k] for w, c in zip(weights, comps))
done = {json.loads(l)["row"] for l in open(SHAP_OUT, encoding="utf-8") if l.strip()} if SHAP_OUT.exists() else set()
if SMOKE: order = sorted(order, key=lambda r: len(str(texts_te[r]).split()))[:N_SHAP]      # shortest sentences only, to stay fast on CPU
t0 = time.time()
for j, row in enumerate(order, 1):
    if row in done: continue
    text = str(texts_te[row]); parts = [m.groups() for m in UNIT_RE.finditer(text)]; n = len(parts)
    full = sum(w * c.z([text])[0] for w, c in zip(weights, comps)); k = int(full.argmax())
    ex = shap.Explainer(lambda M_: comp_scores(parts, np.asarray(M_) > 0.5, k), shap.maskers.Independent(np.zeros((1, n))), algorithm="permutation", seed=SHAP_SEED)
    sv = ex(np.ones((1, n)), max_evals=(4 if SMOKE else N_PERM) * (2 * n + 1), batch_size=64, silent=True)[0]
    V = np.asarray(sv.values); fused = V @ np.array(weights)
    rec = {"row": row, "units": ["".join(p) for p in parts], "fused_top1": str(LAB[k]), "fused_score": float(full[k]), "fused_top1_correct": bool(Y_test[row, k]), "shap_fused": fused.tolist(),
           "shap_by_component": {c.name: V[:, i].tolist() for i, c in enumerate(comps)}, "additivity_error": float(abs(fused.sum() + np.asarray(sv.base_values) @ np.array(weights) - full[k])),
           "system": SYSTEM, "n_perm": 4 if SMOKE else N_PERM, "weights": weights}
    if row in stored:
        rv = np.array(stored[row]["shap_values"]); rec["roberta_s42_top1"] = stored[row]["pred_label"]; rec["same_label_as_roberta_shap"] = stored[row]["pred_label"] == str(LAB[k])
        if n >= 6 and (fused > 0).sum() >= K_HIDE and (rv > 0).sum() >= K_HIDE and len(rv) == n:
            topf = set(np.argsort(-fused, kind="stable")[:K_HIDE].tolist()); topr = set(np.argsort(-rv, kind="stable")[:K_HIDE].tolist())
            rng = np.random.RandomState(42 + row); draws = [set(rng.choice(n, K_HIDE, replace=False).tolist()) for _ in range(N_RANDOM)]
            sc = fused_plain([text, removed(parts, topf, text), removed(parts, topr, text)] + [removed(parts, d, text) for d in draws], k)
            rec.update(del_used=True, drop_fusedSHAP_top3=float(sc[0] - sc[1]), drop_robertaSHAP_top3=float(sc[0] - sc[2]), drop_random3=float(sc[0] - sc[3:].mean()), top3_overlap=len(topf & topr))
    with open(SHAP_OUT, "a", encoding="utf-8") as fh: fh.write(json.dumps(rec) + "\n")
    print(f"[{j}/{len(order)}] row {row} words={n} top1={LAB[k]} add_err={rec['additivity_error']:.1e} {time.time() - t0:.0f}s")
'''),
    ("code", r'''
recs = [json.loads(l) for l in open(SHAP_OUT, encoding="utf-8") if l.strip()]; d = [r for r in recs if r.get("del_used")]
summ = {"n_sentences": len(recs), "full_fusion": float(FULL), "z_statistics_constant": float(Z_CONSTANT), "max_additivity_error": max(r["additivity_error"] for r in recs),
        "fused_top1_correct": float(np.mean([r["fused_top1_correct"] for r in recs])), "explained_label_equals_fused_label": 1.0}
if d:
    f_ = np.array([r["drop_fusedSHAP_top3"] for r in d]); rb = np.array([r["drop_robertaSHAP_top3"] for r in d]); rn = np.array([r["drop_random3"] for r in d]); pb = paired_bootstrap(f_, rb)
    summ.update(n_deletion=len(d), drop_fusedSHAP_top3=float(f_.mean()), drop_robertaSHAP_top3=float(rb.mean()), drop_random3=float(rn.mean()), fused_minus_roberta=pb["delta"], fused_minus_roberta_lo=pb["lo"], fused_minus_roberta_hi=pb["hi"],
                same_label_share=float(np.mean([r["same_label_as_roberta_shap"] for r in d])))
(OUT / "fusion_shap_summary.json").write_text(json.dumps({"metrics": summ, "system": SYSTEM}, indent=1))
write_manifest("fusion_shap", "fusion-shap", SEED, {"n_perm": 4 if SMOKE else N_PERM, "weights": weights, "system": SYSTEM}, [state] if FULL else [], [SHAP_OUT, OUT / "fusion_shap_summary.json"], summ, "DONE" if FULL else "PARTIAL")
if SMOKE: SHAP_OUT.unlink(missing_ok=True)          # smoke records carry sentence text: do not keep them
'''), ("code", EVID)])

# ============================== 07 ==============================
build("07_extension_support_aware_fusion", [("md", header("07", "Extension: support-aware fusion", "Let the matcher's weight depend on the train support of the candidate label (bands: unseen, 1-4, 5-19, 20+). Dev-only selection; the test split is evaluated once with the selected setting. "
      "This is a no-training analysis; it was already run locally (`results/support_aware_v2.csv`). The notebook repeats it so it can be re-run with extra seeds or the retrained matcher.",
      "saved scores", "`support_aware.json`", "1 min (CPU)", "re-checks G9.*", "\nPre-registrations: `experiments/prereg/09_support_aware_fusion.md`, `13_support_aware_fusion_v2.md`. A failed extension is reported as failed.")),
    ("code", setup("07_extension_support_aware_fusion")), ("code", DATA), ("code", LIB), ("code", SCORES),
    ("code", r'''
Zd, Zt = components("dev", "avg"), components("test", "avg")
band = np.where(train_count == 0, 0, np.where(train_count <= 4, 1, np.where(train_count <= 19, 2, 3)))
def sa(Z, wm): return np.array(wm, float)[band][None, :] * Z["matcher"] + Z["svm"] + Z["roberta"] + Z["secbert"]
grid = list(itertools.product([1, 2, 3, 4, 6, 8], repeat=4)); grid = grid[:60] if SMOKE else grid
best = None
for wm in grid:                                                            # DEV only
    fd = sa(Zd, wm); key = (round(float(rr_at_k(fd, Y_dev).mean()), 4), round(float(hit_at_1(fd, Y_dev).mean()), 4))
    if best is None or key > best[0]: best = (key, wm)
wm = best[1]; hs = hit_at_1(sa(Zt, wm), Y_test)                            # the single test evaluation
rarest = np.where(Y_test, train_count[None, :], 10**9).min(1); rare = rarest <= 4
res = {"w_unseen": wm[0], "w_rare": wm[1], "w_mid": wm[2], "w_frequent": wm[3], "dev_MRR@3": best[0][0], "test_P@1": float(hs.mean()), "rare_P@1": float(hs[rare].mean()), "n_dev_settings": len(grid)}
ps = []
for nm, w in (("3111", (3, 1, 1, 1)), ("4111", (4, 1, 1, 1)), ("equal", (1, 1, 1, 1))):
    hb = hit_at_1(fuse(Zt, w), Y_test); pb = paired_bootstrap(hs, hb); mc = mcnemar_exact(hs, hb); ps.append(mc["p"])
    res.update({f"delta_vs_{nm}": pb["delta"], f"ci_lo_vs_{nm}": pb["lo"], f"ci_hi_vs_{nm}": pb["hi"], f"p_mcnemar_vs_{nm}": mc["p"], f"rare_P@1_{nm}": float(hb[rare].mean())})
for nm, p in zip(("3111", "4111", "equal"), holm(ps)): res[f"p_holm_vs_{nm}"] = p
res["success_rule_met"] = float(res["p_holm_vs_3111"] < 0.05 and res["ci_lo_vs_3111"] > 0 and res["rare_P@1"] > res["rare_P@1_3111"])
(OUT / "support_aware.json").write_text(json.dumps({"metrics": res, "matcher_source": MATCHER_SOURCE}, indent=1))
write_manifest("support_aware", "fusion-support-aware", "avg", {"bands": "0 | 1-4 | 5-19 | 20+", "weights_grid": [1, 2, 3, 4, 6, 8]}, [matcher_dir(s) / "test_scores.npy" for s in SEEDS], [OUT / "support_aware.json"], res, "DONE")
print("extension", "SUCCEEDED" if res["success_rule_met"] else "FAILED the pre-registered rule (reported as such)")
'''), ("code", EVID)])

# ============================== 08 ==============================
build("08_extension_cross_dataset", [("md", header("08", "Extension: objective (b), sibling datasets to TRAM test", "Train on (b) the sibling sources of `combined_train.csv` only and (c) TRAM + siblings, select on TRAM dev, test once on TRAM test. The sibling data IS in the folder "
      "(`source_dataset` = procedure, derived_procedure).", "`Dataset/combined_train.csv`, TRAM dev/test", "`cross_dataset_prep.json`; trained runs under `showcase_runs/08_extension_cross_dataset/`", "matcher: about 4x the TRAM run per configuration and seed (estimate: 1.5-2 h); kill-switch candidate",
      "T6.cross_dataset", "\nPre-registration: `experiments/prereg/11_cross_dataset.md`. Sibling rows that duplicate a TRAM dev or test sentence are removed before training; the count is recorded. Only the matcher is trained here: it is the one component whose label space already covers the sibling labels.")),
    ("code", setup("08_extension_cross_dataset")), ("code", DATA), ("code", LIB), ("code", MATCHER),
    ("code", r'''
comb = pd.read_csv(DATA_DIR / "combined_train.csv").rename(columns={"text1": "text"}); comb["labels"] = comb["labels"].apply(_labels)
norm = lambda s: re.sub(r"\s+", " ", str(s).lower()).strip()
heldout = set(map(norm, dev["text"])) | set(map(norm, test["text"]))
sib = comb[comb["source_dataset"] != "tram"].drop_duplicates(subset=["text"]).reset_index(drop=True)
leak = sib["text"].map(norm).isin(heldout); in_space = sib["labels"].apply(lambda ys: all(y in lab2i for y in ys))
sib_clean = sib[~leak & in_space].reset_index(drop=True)
prep = {"sibling_rows": len(sib), "removed_duplicates_of_dev_or_test": int(leak.sum()), "removed_labels_outside_space": int((~in_space & ~leak).sum()), "sibling_rows_used": len(sib_clean),
        "sibling_labels": len({y for ys in sib_clean["labels"] for y in ys}), "test_labels_covered_by_siblings": int(sum(l in {y for ys in sib_clean["labels"] for y in ys} for l in np.array(LABELS)[Y_test.sum(0) > 0])),
        "unseen_test_labels_covered_by_siblings": int(sum(l in {y for ys in sib_clean["labels"] for y in ys} for l in np.array(LABELS)[(Y_test.sum(0) > 0) & ~SEEN]))}
(OUT / "cross_dataset_prep.json").write_text(json.dumps({"metrics": prep}, indent=1)); print(prep)
'''),
    ("code", r'''
CONFIGS = {"b_siblings_only": sib_clean[["text", "labels"]], "c_tram_plus_siblings": pd.concat([train[["text", "labels"]], sib_clean[["text", "labels"]]], ignore_index=True).drop_duplicates(subset=["text"]).reset_index(drop=True)}
if SMOKE and device.type != "cuda":
    print("SMOKE on CPU: training skipped (GPU-only). Data preparation above ran in full.")
else:
    for name, df in CONFIGS.items():
        for sd in ((42,) if SMOKE else SEEDS):
            out = OUT / f"matcher_{name}_s{sd}"
            if (out / "metrics.json").exists() and json.load(open(out / "metrics.json")).get("finished"): print("skip", out); continue
            d = df.iloc[:N_SMOKE] if SMOKE else df
            m = train_matcher_save(out, sd, epochs=1 if SMOKE else 20, tr=d, Ytr=to_Y(d))
            St = np.load(out / "test_scores.npy"); rarest = np.where(Y_test, train_count[None, :], 10**9).min(1)
            met = {**m["test"], "P@1_unseen_in_tram": float(hit_at_1(St, Y_test)[rarest == 0].mean()), "P@1_support_1_4": float(hit_at_1(St, Y_test)[(rarest >= 1) & (rarest <= 4)].mean()), "train_rows": len(d)}
            write_manifest(f"matcher_{name}_s{sd}", f"matcher-{name}", sd, m["config"], [DATA_DIR / "combined_train.csv"], [out / "test_scores.npy", out / "metrics.json"], met, "DONE"); print(name, sd, met)
'''), ("code", EVID)])

# ============================== 09 ==============================
build("09_baseline_same_protocol", [("md", header("09", "Published baseline under one protocol", "(1) Implement the metric definitions of Nguyen et al. (arXiv:2401.10337, App. D.1) exactly and score OUR systems with them, so that R@1 and F1@3 are compared like with like. "
      "(2) Document why their model was not re-run and give the commands to do it.", "saved scores; (optional) a clone of `github.com/tumeteor/mitre-ttp-mapping`", "`baseline_protocol.json`", "1 min for part 1 (CPU); part 2 about 24 h per run on a V100 according to the paper",
      "T5.baseline_same_protocol", "\nThe paper's numbers are NOT typed into this notebook. They are read from `run_match_1/final_results_table.csv` (the row the original notebook copied from the paper) so that the comparison table has a traceable source.")),
    ("code", setup("09_baseline_same_protocol")), ("code", DATA), ("code", LIB), ("code", SCORES),
    ("code", r'''
# Metric definitions exactly as printed in the paper (App. D.1):
#   P@k   = (1/k) * sum_{i<=k} 1[l_i in gold]                     per sample, then averaged over samples
#   R@k   = (1/|Q|) * sum_{i<=k} 1[l_i in gold], |Q| = number of gold labels of the sample; averaged over samples
#   F1@k  = 2 P@k R@k / (P@k + R@k)                               computed from the averaged P@k and R@k
#   MRR@k = (1/S) * sum_i 1/rank_i, rank of the first gold label inside the top k (a sample without a hit contributes 0: not stated in the paper, assumed)
def paper_metrics(S, Y):
    out = {}
    for k in (1, 3):
        hits = np.take_along_axis(Y, rank_topk(S, k), axis=1).sum(1); p = float((hits / k).mean()); r = float((hits / np.maximum(Y.sum(1), 1)).mean())
        out[f"P@{k}"] = p; out[f"R@{k}"] = r; out[f"F1@{k}"] = 2 * p * r / (p + r) if p + r else 0.0
    out["MRR@3"] = float(rr_at_k(S, Y, 3).mean()); out["R@1_micro_as_in_our_notebooks"] = recall_at_k_micro(S, Y, 1)
    return out
par = np.array([l.split(".")[0] for l in LABELS]); up = sorted(set(par)); PM = np.zeros((L, len(up))); PM[np.arange(L), [up.index(p) for p in par]] = 1
def technique_level(S, Y):                                                 # "resolve sub-techniques to their super-techniques" (paper Table 3)
    St = np.full((len(S), len(up)), -np.inf)
    for j in range(L): St[:, up.index(par[j])] = np.maximum(St[:, up.index(par[j])], S[:, j])
    return paper_metrics(St, (Y @ PM) > 0)
Za = components("test", "avg"); n_ = N_SMOKE if SMOKE else len(test)
systems = {"svm": to_full(svm_raw["test"], seen_idx, L, -1e9), "matcher_ensemble": Za["matcher"], "fusion_3111": fuse(Za, (3, 1, 1, 1))}
res = {}
for nm, S in systems.items():
    for k, v in paper_metrics(S[:n_], Y_test[:n_]).items(): res[f"{nm}_{k}"] = v
    for k, v in technique_level(S[:n_], Y_test[:n_]).items(): res[f"{nm}_techlevel_{k}"] = v
ref = {}
p = MATCH_ROOT / "final_results_table.csv"
if p.exists():
    fr = pd.read_csv(p); row = fr[fr["model"].str.startswith("Paper")].iloc[0]
    ref = {"published_P@1": float(row["P@1"]), "published_R@1": float(row["R@1"]), "published_MRR@3": float(row["MRR@3"])}
(OUT / "baseline_protocol.json").write_text(json.dumps({"metrics": {**res, **ref}, "note": "published_* values are constants copied by the original notebook from the paper; not re-run"}, indent=1))
write_manifest("baseline_protocol", "paper-metric-definitions", "avg", {"definitions": "arXiv:2401.10337 App. D.1"}, [p], [OUT / "baseline_protocol.json"], res, "DONE")
'''),
    ("md", r'''
## Part 2: why the published model was not re-run, and how to do it

- Their code, weights, predictions and split files are **not** in the project folder. Only two of their data files are (`ttp-desc-mappings.csv` and, by its three source values, `combined_train.csv`).
- Open points that a re-run would settle (see `_evidence_pack/08_baseline.md`): whether their TRAM test split is row-identical to ours; whether their Table 2 was trained in "separate" or "combined" mode.
- The paper states an average training time of 24 hours on one V100 (Limitations section). This is outside a free Colab session.

To run it when compute is available (NOT RUN; the repository layout was not inspected, so the commands after the clone are placeholders to adapt):

```
git clone https://github.com/tumeteor/mitre-ttp-mapping
# 1. compare their TRAM test file with ours:  sha256 of each normalised sentence, then set difference
# 2. train their "Asymmetric" model in SEPARATE mode on TRAM train only
# 3. save its score matrix over the 733 labels as test_scores.npy
# 4. score it with paper_metrics() above and with scripts/verify_claims.py conventions
```
'''), ("code", EVID)])

# ============================== 10 ==============================
build("10_llm_baseline", [("md", header("10", "LLM baseline (protocol only, optional, NOT RUN)", "Fix, in advance, how a large language model would be evaluated on the same test set, so that a later run cannot be tuned on the test set.",
      "test sentences, ATT&CK descriptions; an API key supplied by the author at run time", "`llm_predictions.jsonl`, `llm_baseline.json` (only if run)", "depends on the provider; 725 requests per configuration", "none until run",
      "\nNo API key is stored or requested by this notebook. Nothing here has been executed against a model.")),
    ("md", r'''
## Protocol

1. **Model and settings** are written down before the first request: provider, exact model id, temperature 0, maximum output tokens, date of the run. Record them in the manifest.
2. **Two prompts, both fixed in advance, no prompt tuning on test:**
   - *closed-set:* the sentence plus the list of the 180 training technique ids and names; the model returns up to three ids, best first.
   - *retrieve-then-rank:* the sentence plus the 20 technique descriptions ranked highest by the zero-shot bge matcher; the model returns up to three ids, best first.
3. **Prompt development uses dev sentences only** (at most 50), and the dev sentences used are listed in the manifest.
4. **Output handling:** ids that are not valid technique ids, or not in the offered list, are dropped; an empty answer counts as a miss. Report the share of invalid answers.
5. **Metrics:** P@1, MRR@3 with the shared metric code; paired bootstrap and exact McNemar against the fusion; the LLM comparisons are a new family for Holm.
6. **Data-leak caveat to state in the thesis:** TRAM and ATT&CK are public, so a model may have seen test sentences during training; a high score is therefore weaker evidence than for the trained systems.
7. **Cost and privacy:** the test sentences are public CTI text; no rater or personal data is sent.
'''),
    ("code", setup("10_llm_baseline")), ("code", DATA), ("code", LIB),
    ("code", r'''
RUN_LLM = False            # stays False in the repository; the author sets it to True after supplying a client
def build_prompt_closed(sentence, ids, names):
    lines = "\n".join(f"{i}: {n}" for i, n in zip(ids, names))
    return ("You map a sentence from a cyber threat report to MITRE ATT&CK techniques.\nChoose from this list only:\n" + lines +
            f"\n\nSentence: {sentence}\nAnswer with up to three technique ids, best first, separated by commas. No other text.")
def parse_answer(text, allowed):
    out = []
    for t in re.findall(r"T\d{4}(?:\.\d{3})?", str(text).upper()):
        if t in allowed and t not in out: out.append(t)
    return out[:3]
def to_scores(pred_lists):
    S = np.zeros((len(pred_lists), L))
    for i, ids in enumerate(pred_lists):
        for r, t in enumerate(ids): S[i, lab2i[t]] = 3 - r
    return S
# self-test of the parsing and scoring path with a made-up answer string (not a model output)
allowed = set(np.array(LABELS)[seen_idx]); demo = parse_answer("T1059.001, t1105 and T9999", allowed)
assert demo == [t for t in ["T1059.001", "T1105"] if t in allowed], demo
S_demo = to_scores([demo]); print("parser and scorer OK; prompt length for one sentence:", len(build_prompt_closed(test["text"].iloc[0], list(np.array(LABELS)[seen_idx]), ["name"] * int(SEEN.sum()))), "characters")
if RUN_LLM:
    raise NotImplementedError("Supply a client call here; write each raw answer to OUT / 'llm_predictions.jsonl' before parsing.")
(OUT / "llm_protocol_check.json").write_text(json.dumps({"metrics": {"run_llm": float(RUN_LLM), "parser_selftest_passed": 1.0}}))
'''), ("code", EVID)])

print("notebooks written:", len(list(NB.glob("*.ipynb"))))
