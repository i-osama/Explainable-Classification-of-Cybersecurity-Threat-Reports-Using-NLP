"""Prompt F: hardened Colab and Kaggle notebooks (no Drive dependency, fail-fast, resumable) + the upload zips.

Builds _showcase/COLAB_UPLOAD/:
  colab/04_train_matcher_save_HARDENED.ipynb    from notebooks/04_train_matcher_save.ipynb (matcher retrain, seed 42 first)
  colab/06_explainability_HARDENED.ipynb        from notebooks/06_explainability.ipynb (SHAP of the full fusion)
  colab/colab_fusion_shap_HARDENED.ipynb        from _evidence_pack/09_repro/colab_fusion_shap.ipynb (both steps in one runtime)
  kaggle/04_train_matcher_save_KAGGLE.ipynb, kaggle/06_explainability_KAGGLE.ipynb   (same code; platform is detected)
  thesis_inputs.zip (the 36 input files, Thesis layout, no weights, no checkpoints), thesis_weights_s42.zip (8 files, for 06 and
  colab_fusion_shap), inputs_sha256.json, RUN_COLAB.md, KAGGLE.md
The source notebooks are only read. Model, data and SHAP code is copied unchanged; the edits are: a new PREFLIGHT cell (replaces the setup
cell), outputs under /content/out (Kaggle: /kaggle/working/out), checkpoint mirroring to Drive when it is mounted, SMOKE = True by default,
a FINAL cell that zips and downloads the outputs. Every edit is an exact-match patch that fails loudly if the source changes.
Usage: python scripts/make_colab_hardened.py [--no-weights] [--no-zips]"""
import argparse, hashlib, json, shutil, sys, zipfile
from pathlib import Path
import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

SHOW = Path(__file__).resolve().parents[1]; ROOT = SHOW.parent; DST = SHOW / "COLAB_UPLOAD"
SRC04, SRC06 = SHOW / "notebooks" / "04_train_matcher_save.ipynb", SHOW / "notebooks" / "06_explainability.ipynb"
SRCCFS = ROOT / "_evidence_pack" / "09_repro" / "colab_fusion_shap.ipynb"
SEEDS = (42, 43, 44)
REQUIRED = (["Dataset/tram_dev.tsv", "Dataset/tram_test.tsv", "Dataset/ttp-desc-mappings.csv", "Dataset/combined_train.csv",
             "Exp_3_0_shap/shap_v2_roberta_pw_s42.jsonl", "run_match_1/zeroshot/test_scores.npy"]
            + [f"Exp_1_4_run_tram_2_epoc_30/{t}_pw_s{s}/{f}" for t in ("roberta", "secbert") for s in SEEDS
               for f in ("test_probs.npy", "dev_probs.npy", "metrics.json", "mlb_classes.npy")]
            + [f"run_match_1/ft20_s{s}/{sp}_scores.npy" for s in SEEDS for sp in ("dev", "test")])
WEIGHTS = [f"Exp_1_4_run_tram_2_epoc_30/{t}_pw_s42/{f}" for t in ("roberta", "secbert")
           for f in ("model.safetensors", "config.json", "tokenizer.json", "tokenizer_config.json")]
assert len(REQUIRED) == 36 and len(WEIGHTS) == 8
PINS = {"transformers": "5.22.1", "sentence-transformers": "5.7.0", "shap": "0.54.1", "scikit-learn": "1.6.1"}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()


# ------------------------------------------------------------------------------------------------------------------------------
PREFLIGHT = r'''# ==== CELL 0 · PREFLIGHT (hardened run: Drive optional, stops on the first problem, resumable) ====
# FIRST RUN: leave SMOKE = True. The whole notebook then runs on 20 samples in under 5 minutes. Its outputs are a code check, NOT results.
# REAL RUN:  change the next line to  SMOKE = False , then  Runtime > Restart session and run all  (Kaggle: Save Version > Save & Run All).
SMOKE = True
EXTRA_SEEDS = False       # True: after seed 42, also train the optional extra matcher seeds (about 25 min each)
TRY_DRIVE = __TRY_DRIVE__          # try to mount Google Drive (60 s timeout). Never required: inputs come from the uploaded zip
PIN_STRICT = True         # stop if the pinned versions cannot be installed; False = run on the installed versions (recorded anyway)
NOTEBOOK, NEEDS_GPU, NEED_WEIGHTS, WRITES_MATCHER, MIN_FREE_GB = "__NOTEBOOK__", True, __NEED_WEIGHTS__, __WRITES_MATCHER__, __MIN_FREE_GB__
ZIP_PARTS = __ZIP_PARTS__      # folders under the output root that the FINAL cell zips
HF_MODELS = ["BAAI/bge-base-en-v1.5"]
PINS = __PINS__   # = the Colab environment that ran notebook 00 (showcase_runs/00_setup_and_verify/env_colab.json)

import os, sys, json, ast, time, hashlib, random, platform, subprocess, re, shutil, zipfile, threading, urllib.request
import importlib, importlib.metadata as _md
from pathlib import Path
T0, T_START = time.time(), time.strftime("%Y-%m-%dT%H:%M:%S")
SMOKE = {"1": True, "0": False}.get(os.environ.get("TTPMAP_SMOKE", ""), SMOKE)          # only the local test harness sets this
N_SMOKE = 20

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def set_seed(seed):
    random.seed(seed); np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True; torch.backends.cudnn.benchmark = False
    except ImportError:
        pass

# ---- where am I? (TTPMAP_* variables exist only for the local test harness) ----
_ENV = os.environ.get("TTPMAP_PLATFORM", "")
REAL_COLAB = "google.colab" in sys.modules or "COLAB_RELEASE_TAG" in os.environ
REAL_KAGGLE = "KAGGLE_KERNEL_RUN_TYPE" in os.environ or os.path.isdir("/kaggle/working")
IS_KAGGLE = _ENV == "kaggle" or (not _ENV and REAL_KAGGLE)
IS_COLAB = not IS_KAGGLE and (_ENV == "colab" or REAL_COLAB)
ON_CLOUD, IN_COLAB = REAL_COLAB or REAL_KAGGLE, IS_COLAB
PLATFORM_NAME = "kaggle" if IS_KAGGLE else "colab" if IS_COLAB else "local"
LOCAL_MODE = PLATFORM_NAME == "local"
if IS_KAGGLE:
    _K = Path(os.environ.get("TTPMAP_KAGGLE", "/kaggle")); WORK, INPUT = _K / "working", _K / "input"
    BASE = Path(os.environ.get("TTPMAP_TMP", "/tmp")) / "KDU" / "Thesis"
elif IS_COLAB:
    WORK = INPUT = Path(os.environ.get("TTPMAP_CONTENT", "/content")); BASE = WORK / "KDU" / "Thesis"
else:                                                   # local: read the project folder, write only under TTPMAP_OUT_ROOT
    WORK = INPUT = Path(os.environ.get("TTPMAP_OUT_ROOT", "out_local")).resolve(); BASE = Path(os.environ.get("TTPMAP_ROOT", r"E:\Osamas Paper"))
OUT_ROOT = WORK / ("out_smoke" if SMOKE else "out")          # smoke and real outputs never mix
OUT = OUT_ROOT / "showcase_runs" / NOTEBOOK
OUT.mkdir(parents=True, exist_ok=True); BASE.mkdir(parents=True, exist_ok=True)
DRIVE = Path(os.environ.get("TTPMAP_DRIVE", "/content/drive/MyDrive")); DRIVE_BASE = DRIVE / "KDU" / "Thesis"
SEEDS = (42, 43, 44)
REQUIRED = (["Dataset/tram_dev.tsv", "Dataset/tram_test.tsv", "Dataset/ttp-desc-mappings.csv", "Dataset/combined_train.csv",
             "Exp_3_0_shap/shap_v2_roberta_pw_s42.jsonl", "run_match_1/zeroshot/test_scores.npy"]
            + [f"Exp_1_4_run_tram_2_epoc_30/{t}_pw_s{s}/{f}" for t in ("roberta", "secbert") for s in SEEDS for f in ("test_probs.npy", "dev_probs.npy", "metrics.json", "mlb_classes.npy")]
            + [f"run_match_1/ft20_s{s}/{sp}_scores.npy" for s in SEEDS for sp in ("dev", "test")])
WEIGHTS = [f"Exp_1_4_run_tram_2_epoc_30/{t}_pw_s42/{f}" for t in ("roberta", "secbert") for f in ("model.safetensors", "config.json", "tokenizer.json", "tokenizer_config.json")]
FROM_04 = [f"run_match_2_saved/ft20_s42/{f}" for f in ("matcher_state.pt", "test_scores.npy", "dev_scores.npy", "metrics.json")]
EXPECTED_SHA = __EXPECTED_SHA__
ROWS = []
def row(check, status, detail, fix=""): ROWS.append({"check": check, "status": status, "detail": detail, "fix": fix})
row("platform", "INFO", f"{PLATFORM_NAME} | python {platform.python_version()} | SMOKE={SMOKE} | inputs {BASE} | outputs {OUT_ROOT}")

# ---- 1 GPU (a real CUDA operation, not only is_available) ----
GPU_NAME = "none"
try:
    import torch
    if not torch.cuda.is_available(): raise RuntimeError("torch.cuda.is_available() is False")
    _x = torch.ones(64, 64, device="cuda"); float((_x @ _x).sum().item())
    _g = torch.cuda.get_device_properties(0); GPU_NAME = f"{_g.name}, {_g.total_memory / 2**30:.0f} GB, torch {torch.__version__}"
    row("GPU", "PASS", GPU_NAME)
except Exception as e:
    row("GPU", "WARN" if (os.environ.get("TTPMAP_ALLOW_CPU") == "1" or not NEEDS_GPU) else "FAIL", f"no usable GPU ({type(e).__name__}: {str(e)[:100]})",
        "Kaggle: right panel > Session options > Accelerator > GPU T4 x2 (not P100: current PyTorch has no P100 kernels), then Run all again."
        if IS_KAGGLE else "Colab: Runtime > Change runtime type > T4 GPU > Save, then Runtime > Run all.")

# ---- 2 internet ----
try:
    urllib.request.urlopen("https://huggingface.co/api/models/BAAI/bge-base-en-v1.5", timeout=20).read(64); NET = True
    row("internet", "PASS", "huggingface.co reachable")
except Exception as e:
    NET = False
    row("internet", "FAIL", f"{type(e).__name__}: {str(e)[:100]}", "Kaggle: right panel > Session options > Internet on (needs a phone-verified account). "
        "Colab: Runtime > Disconnect and delete runtime, then reconnect.")

# ---- 3 pinned library versions (installed only when they differ; recorded in the run manifest) ----
def _ver(p):
    try: return _md.version(p)
    except _md.PackageNotFoundError: return None
_wrong, PIP_TAIL, RESTART = [p for p, v in PINS.items() if _ver(p) != v], "", False
if _wrong and ON_CLOUD and NET:
    _loaded = [m for m in ("transformers", "sentence_transformers", "shap", "sklearn") if m in sys.modules]
    _r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", *[f"{p}=={PINS[p]}" for p in _wrong]], capture_output=True, text=True)
    PIP_TAIL = (_r.stdout + _r.stderr)[-1500:]; importlib.invalidate_caches(); RESTART = bool(_loaded) and _r.returncode == 0
    print(f"pip install {' '.join(_wrong)}: exit {_r.returncode}")
VERSIONS = {p: _ver(p) for p in list(PINS) + ["torch", "numpy", "pandas", "scipy", "tokenizers", "safetensors", "huggingface-hub", "accelerate"]}
_bad = {p: VERSIONS[p] for p, v in PINS.items() if VERSIONS[p] != v}
if RESTART:
    row("pinned versions", "FAIL", "pins installed after the libraries were already imported", "Runtime > Restart session, then Runtime > Run all (the pins stay installed).")
elif not _bad:
    row("pinned versions", "PASS", ", ".join(f"{p} {v}" for p, v in PINS.items()))
else:
    row("pinned versions", "FAIL" if (ON_CLOUD and PIN_STRICT) else "WARN", "installed: " + ", ".join(f"{p} {v}" for p, v in _bad.items()) + ("" if ON_CLOUD else " (local run: nothing installed)"),
        f"pip said: {PIP_TAIL[-300:]!r}. Or set PIN_STRICT = False to run on the installed versions (recorded in the run manifest).")

# ---- 4 Hugging Face model download (also warms the cache for the training cells) ----
if NET:
    try:
        from huggingface_hub import snapshot_download
        for _m in HF_MODELS: snapshot_download(_m, allow_patterns=["*.json", "*.txt", "model.safetensors"])
        row("HF model download", "PASS", ", ".join(HF_MODELS))
    except Exception as e:
        row("HF model download", "FAIL", f"{type(e).__name__}: {str(e)[:100]}", "Run this cell again (Hugging Face hiccup); no token is needed for this public model.")
else:
    row("HF model download", "FAIL", "skipped: no internet", "Fix the internet row first.")

# ---- 5 Google Drive: optional, 60 s timeout, never required ----
DRIVE_OK, _dn = False, ("not tried (TRY_DRIVE = False)" if not TRY_DRIVE else "not available on this platform")
if TRY_DRIVE and IS_COLAB:
    if not DRIVE.is_dir() and REAL_COLAB:
        try:
            from google.colab import drive as _gd
            try: _gd.mount("/content/drive", timeout_ms=60_000)
            except TypeError: _gd.mount("/content/drive")
        except Exception as e:
            _dn = f"not mounted: {type(e).__name__}: {str(e)[:80]}"
    DRIVE_OK = DRIVE.is_dir()
    if DRIVE_OK: _dn = f"mounted at {DRIVE}"
row("Google Drive (optional)", "PASS" if DRIVE_OK else "WARN", _dn,
    "" if DRIVE_OK else "Not needed. Without Drive a resume survives a kernel restart, not a new runtime; the FINAL cell downloads the zip.")
MIRROR = (DRIVE_BASE / "_colab_runs" / ("smoke" if SMOKE else "real")) if DRIVE_OK else None

# ---- 6 input ladder: (a) uploaded zip -> BASE ; (b) Drive (or Kaggle datasets) ; (c) stop with the missing list ----
def _safe_extract(z, dest):
    """Extract members that are not there yet; refuses absolute paths and '..'. Returns the extracted names."""
    got = []
    with zipfile.ZipFile(z) as zf:
        for info in zf.infolist():
            n = info.filename
            if info.is_dir() or n.startswith(("/", "\\")) or ".." in Path(n).parts or (Path(dest) / n).exists(): continue
            (Path(dest) / n).parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as s, open(Path(dest) / n, "wb") as d: shutil.copyfileobj(s, d, 1 << 22)
            got.append(n)
    return got
FROM_ZIP, SRC, ROOTS = set(), {}, []
if not LOCAL_MODE:
    _find = (lambda pat: sorted(INPUT.glob(pat))) if IS_COLAB else (lambda pat: sorted(INPUT.rglob(pat)))
    for _z in _find("thesis_*.zip"):
        _got = _safe_extract(_z, BASE); FROM_ZIP |= set(_got); print(f"(a) {_z.name}: {len(_got)} new files -> {BASE}")
    _sfx = "_SMOKE" if SMOKE else ""                    # previous outputs: own zip (resume) + on Colab the matcher hand-off zip of 04 / colab_fusion_shap
    _take = [f"colab_out_{NOTEBOOK}{_sfx}.zip"] + ([] if WRITES_MATCHER or IS_KAGGLE else [f"colab_out_{n}{_sfx}.zip" for n in ("04_train_matcher_save", "colab_fusion_shap")])
    for _z in [z for z in _find("colab_out_*.zip") if z.name in _take]:
        print(f"previous outputs {_z.name}: {len(_safe_extract(_z, OUT_ROOT))} files -> {OUT_ROOT}")
    if IS_KAGGLE:                                       # (b) private Kaggle datasets / earlier notebook outputs added as inputs
        for _rel in (REQUIRED[0], WEIGHTS[0], FROM_04[0]):
            for _hit in INPUT.rglob(Path(_rel).name):
                if _hit.as_posix().endswith(_rel):
                    _r0 = _hit
                    for _ in Path(_rel).parts: _r0 = _r0.parent
                    if _r0 not in [r for _, r in ROOTS]: ROOTS.append(("kaggle input", _r0))
    if DRIVE_OK: ROOTS.append(("Drive", DRIVE_BASE))     # (b) Drive, if mounted
WANT = REQUIRED + (WEIGHTS if NEED_WEIGHTS else []) + ([] if WRITES_MATCHER else FROM_04)
for _rel in WANT:
    if _rel in FROM_ZIP: SRC[_rel] = "zip"; continue
    if (BASE / _rel).exists(): SRC[_rel] = "local"; continue
    SRC[_rel] = None
    for _lab, _r0 in ([] if LOCAL_MODE else ROOTS):
        if (_r0 / _rel).exists():
            (BASE / _rel).parent.mkdir(parents=True, exist_ok=True)
            try:
                if _lab == "Drive": raise OSError("copy from Drive")
                os.symlink(_r0 / _rel, BASE / _rel)
            except OSError:
                shutil.copy2(_r0 / _rel, BASE / _rel)
            SRC[_rel] = _lab; break
HASHES = {r: sha256(BASE / r) for r in WANT if SRC.get(r)}
def _src_counts(rels): return ", ".join(f"{k} {sum(SRC.get(r) == k for r in rels)}" for k in sorted({SRC.get(r) for r in rels if SRC.get(r)}))
_UP = ("Left pane > Files (folder icon) > Upload > pick {z} from E:\\Osamas Paper\\_showcase\\COLAB_UPLOAD (it lands in /content), then run this cell again."
       if IS_COLAB else "Right panel > Add Input > Datasets > Your Datasets > the private dataset made from {z}, then run this cell again." if IS_KAGGLE
       else "Local run: the file must exist under TTPMAP_ROOT.")
def _files_row(name, rels, zname, status_missing="FAIL"):
    miss = [r for r in rels if not SRC.get(r)]; diff = [r for r in rels if SRC.get(r) and EXPECTED_SHA.get(r) and HASHES[r] != EXPECTED_SHA[r]]
    if miss: row(name, status_missing, f"{len(rels) - len(miss)}/{len(rels)} present; missing: " + ", ".join(miss), _UP.format(z=zname))
    elif diff: row(name, "FAIL", "content differs from the PC copy: " + ", ".join(diff), f"Upload a fresh {zname} (do not edit files inside it).")
    else: row(name, "PASS", f"{len(rels)}/{len(rels)}, SHA-256 equal to the PC copy ({_src_counts(rels)})")
    return not miss and not diff
_files_row(f"input files ({len(REQUIRED)})", REQUIRED, "thesis_inputs.zip")
if NEED_WEIGHTS: _files_row("classifier weights seed 42 (8)", WEIGHTS, "thesis_weights_s42.zip")

# ---- where the seed-42 matcher lives (04 writes it; 06 reads it) ----
MATCH2 = OUT_ROOT / "run_match_2_saved"
if not WRITES_MATCHER:
    for _c in [OUT_ROOT / "run_match_2_saved", WORK / "out" / "run_match_2_saved", *([DRIVE_BASE / "_colab_runs" / "real" / "run_match_2_saved"] if DRIVE_OK else []), BASE / "run_match_2_saved"]:
        if (_c / "ft20_s42" / "matcher_state.pt").exists(): MATCH2 = _c; break
    _ok = (MATCH2 / "ft20_s42" / "matcher_state.pt").exists()
    row("matcher seed 42 (from 04)", "PASS" if _ok else "WARN", str(MATCH2 / "ft20_s42") if _ok else "not found: only the classifiers-only part of the fusion would be explained",
        "" if _ok else "Run 04 first. Then mount the same Drive here, or upload colab_out_04_train_matcher_save.zip like the inputs zip (Kaggle: Add Input > Your Work > the 04 notebook).")

# ---- 7 free disk ----
_free = shutil.disk_usage(WORK).free / 1e9
row("free disk", "PASS" if _free >= MIN_FREE_GB else "FAIL", f"{_free:.0f} GB free at {WORK} (need {MIN_FREE_GB})",
    "Colab: Runtime > Disconnect and delete runtime, reconnect. Kaggle: delete old files under /kaggle/working.")

# ---- 8 resume sources ----
RESTORE_ROOTS = ([MIRROR] if MIRROR else []) + ([r for r in INPUT.rglob("out_smoke" if SMOKE else "out") if r.is_dir() and ((r / "showcase_runs").is_dir() or (r / "run_match_2_saved").is_dir())]
                                                 if IS_KAGGLE else [])
_ck = sorted(str(p.relative_to(OUT_ROOT)) for p in OUT_ROOT.rglob("*") if p.name == "ckpt_last.pt" or p.suffix == ".jsonl")
row("resume", "INFO", ("local checkpoints: " + ", ".join(_ck) if _ck else "no local checkpoint (fresh start)") + (f" | also checks {len(RESTORE_ROOTS)} mirror/previous-output folder(s)" if RESTORE_ROOTS else ""))

# ---- helpers used by the copied cells ----
DATA_DIR, CLS_ROOT, MATCH_ROOT, SHAP_DIR = BASE / "Dataset", BASE / "Exp_1_4_run_tram_2_epoc_30", BASE / "run_match_1", BASE / "Exp_3_0_shap"
_gpu = GPU_NAME != "none"

def env_info():
    info = {"python": platform.python_version(), "platform": platform.platform(), "in_colab": IN_COLAB, "runner": PLATFORM_NAME, "smoke": SMOKE, "gpu": GPU_NAME}
    try:
        import torch
        info.update(torch=torch.__version__, cuda=torch.cuda.is_available())
    except ImportError:
        pass
    info.update({f"v_{k}": v for k, v in VERSIONS.items()})
    return info

def write_manifest(run_id, system, seed, config, inputs, outputs, metrics, status):
    """One manifest per run: what went in, what came out, with hashes. Read later by the ingest step."""
    m = {"run_id": run_id, "system": system, "seed": seed, "config_hash": hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:16], "config": config,
         "env": {k: str(v) for k, v in env_info().items()}, "input_sha256": {str(p): sha256(p) for p in inputs if Path(p).exists()},
         "output_sha256": {str(p): sha256(p) for p in outputs if Path(p).exists()}, "metrics": {k: float(v) for k, v in metrics.items()},
         "status": "SMOKE" if SMOKE else status, "written": time.strftime("%Y-%m-%dT%H:%M:%S")}
    (OUT / f"manifest_{run_id}.json").write_text(json.dumps(m, indent=1)); return m

RUN_MANIFEST = OUT / f"run_manifest_{NOTEBOOK}.json"
def write_run_manifest(extra):
    try: _pk = {d.metadata["Name"]: d.version for d in _md.distributions() if d.metadata["Name"]}
    except Exception: _pk = {}
    m = {"notebook": NOTEBOOK, "runner": PLATFORM_NAME, "smoke": SMOKE, "started": T_START, "pins": PINS, "versions": VERSIONS, "python": platform.python_version(),
         "gpu": GPU_NAME, "drive": _dn, "preflight": ROWS, "inputs": {r: {"source": SRC.get(r), "sha256": HASHES.get(r)} for r in WANT},
         "all_packages": dict(sorted(_pk.items())), **extra}
    RUN_MANIFEST.write_text(json.dumps(m, indent=1)); return m

def _rel(p):
    try: return Path(p).resolve().relative_to(OUT_ROOT.resolve())
    except ValueError: return None
SNAP, _MT = WORK / "_mirror_snapshot", [None]
def ckpt_wait():
    """Wait until the last background copy to Drive has finished."""
    if _MT[0] is not None: _MT[0].join(); _MT[0] = None

def ckpt_mirror(path):
    """Copy new or changed files under `path` (inside the output root) to the Drive mirror in the background. No-op without Drive.
    A local snapshot is taken first, so the next checkpoint can overwrite the file while the upload runs. SMOKE skips files > 50 MB."""
    if MIRROR is None or _rel(path) is None or not Path(path).exists(): return
    ckpt_wait(); jobs = []
    for q in ([Path(path)] if Path(path).is_file() else [x for x in Path(path).rglob("*") if x.is_file()]):
        if q.name.endswith(".part") or (SMOKE and q.stat().st_size > 50e6): continue
        d = MIRROR / _rel(q)
        if d.exists() and d.stat().st_size == q.stat().st_size and abs(d.stat().st_mtime - q.stat().st_mtime) < 2: continue
        s = SNAP / _rel(q); s.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(q, s); jobs.append((s, d))
    def _go():
        for s, d in jobs:
            try:
                d.parent.mkdir(parents=True, exist_ok=True); tmp = d.with_name(d.name + ".part"); shutil.copy2(s, tmp); os.replace(tmp, d)
            except Exception as e:
                print(f"  (Drive mirror skipped {d.name}: {type(e).__name__}; the run continues)")
    if jobs: _MT[0] = threading.Thread(target=_go, daemon=True); _MT[0].start()

def ckpt_restore(path):
    """Bring back checkpoint files (ckpt_last.pt, best weights, SHAP jsonl) from the Drive mirror or an earlier Kaggle output
    when they are missing locally or newer there. Returns the number of files copied."""
    rel0 = _rel(path)
    if rel0 is None: return 0
    for root in RESTORE_ROOTS:
        src, n = root / rel0, 0
        if not src.exists(): continue
        for q in ([src] if src.is_file() else [x for x in src.rglob("*") if x.is_file()]):
            d = OUT_ROOT / q.relative_to(root)
            if q.name.endswith(".part") or (d.exists() and d.stat().st_mtime >= q.stat().st_mtime - 2): continue
            d.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(q, d); n += 1
        if n: print(f"  resume: {n} file(s) restored from {root}"); return n
    return 0

def finish_run():
    """FINAL cell: zip the outputs (never ckpt_last.pt), record versions and hashes, copy to Drive if mounted, download, list what to bring back."""
    ckpt_wait(); files, skipped = [], []
    for part in ZIP_PARTS:
        p = OUT_ROOT / part
        for q in ([p] if p.is_file() else sorted(x for x in p.rglob("*") if x.is_file()) if p.is_dir() else []):
            if q.name == "ckpt_last.pt" or q.name.endswith(".part") or q == RUN_MANIFEST: continue
            (skipped if SMOKE and q.stat().st_size > 50e6 else files).append(q)
    outs = {_rel(q).as_posix(): {"bytes": q.stat().st_size, "sha256": sha256(q)} for q in files}
    write_run_manifest({"status": "SMOKE" if SMOKE else "FINISHED", "finished": time.strftime("%Y-%m-%dT%H:%M:%S"), "minutes": round((time.time() - T0) / 60, 1), "outputs": outs})
    files.append(RUN_MANIFEST)
    zp = WORK / f"colab_out_{NOTEBOOK}{'_SMOKE' if SMOKE else ''}.zip"
    with zipfile.ZipFile(zp, "w", allowZip64=True) as zf:
        for q in files: zf.write(q, _rel(q).as_posix(), compress_type=zipfile.ZIP_STORED if q.suffix in (".pt", ".npy") else zipfile.ZIP_DEFLATED)
    where = []
    if DRIVE_OK:
        try:
            (DRIVE_BASE / "_colab_out").mkdir(parents=True, exist_ok=True); shutil.copy2(zp, DRIVE_BASE / "_colab_out" / zp.name); where.append(f"Drive: MyDrive/KDU/Thesis/_colab_out/{zp.name}")
        except Exception as e:
            where.append(f"Drive copy failed ({type(e).__name__})")
    if REAL_COLAB:
        try:
            from google.colab import files as _gf
            _gf.download(str(zp)); where.append("browser download started (check the browser's download bar)")
        except Exception as e:
            where.append(f"download did not start ({type(e).__name__}): left pane > Files > {zp.name} > three dots > Download")
    elif IS_KAGGLE:
        where.append("Kaggle: after Save Version finishes, open the version > Output > download " + zp.name)
    print("\n==== BRING BACK ====")
    print(f"file: {zp.name}  ({zp.stat().st_size / 1e6:.1f} MB)  " + " | ".join(where))
    if SMOKE:
        print("This is a SMOKE zip: a code check, not a result (ingest rejects it). Next: set SMOKE = False in the PREFLIGHT cell, Runtime > Restart session and run all.")
    else:
        print("On the PC: unzip it into  E:\\Osamas Paper\\_colab_returned\\  (keep the folders), then run:  python scripts\\ingest_colab.py")
    print(f"contents ({len(files)} files):")
    for q in files: print(f"  {_rel(q).as_posix():<64} {q.stat().st_size / 1e6:9.2f} MB")
    for q in skipped: print(f"  (SMOKE: not zipped, > 50 MB) {_rel(q).as_posix()}")
    return zp

# ---- verdict ----
_wc = max(len(r["check"]) for r in ROWS)
print(f"PREFLIGHT  {NOTEBOOK}")
for r in ROWS:
    print(f"  {r['status']:<4}  {r['check']:<{_wc}}  {r['detail']}" + (f"\n        fix: {r['fix']}" if r["status"] == "FAIL" and r["fix"] else ""))
_failed = [r["check"] for r in ROWS if r["status"] == "FAIL"]
write_run_manifest({"status": "PREFLIGHT_FAILED" if _failed else "STARTED"})
if _failed:
    raise RuntimeError("PREFLIGHT FAILED (" + ", ".join(_failed) + "): fix the FAIL rows above (each has a 'fix:' line), then run this cell again.")
print("PREFLIGHT PASSED." + (" SMOKE run (20 samples): outputs are a code check. Real run: set SMOKE = False above, then Restart session and run all." if SMOKE else " REAL run."))
import numpy as np, pandas as pd
'''

FINAL = '''# ==== FINAL · zip the outputs, copy the zip to Drive if mounted, download it, and list exactly what to bring back ====
# Safe to run on its own after an interruption: it packages whatever has been written so far.
ZIP_PATH = finish_run()'''


def preflight(nb, need_weights, writes_matcher, min_gb, parts, try_drive, sha):
    s = PREFLIGHT
    for k, v in {"__NOTEBOOK__": nb, "__NEED_WEIGHTS__": repr(need_weights), "__WRITES_MATCHER__": repr(writes_matcher), "__MIN_FREE_GB__": str(min_gb),
                 "__ZIP_PARTS__": repr(parts), "__TRY_DRIVE__": repr(try_drive), "__PINS__": json.dumps(PINS), "__EXPECTED_SHA__": json.dumps(sha, indent=0)}.items():
        assert k in s, k; s = s.replace(k, v)
    return s


def patch(src, old, new):
    assert src.count(old) == 1, f"patch anchor found {src.count(old)} times: {old[:70]!r}"
    return src.replace(old, new)


def insert_after(src, anchor, text):
    lines = src.split("\n"); hits = [i for i, l in enumerate(lines) if anchor in l]
    assert len(hits) == 1, f"anchor line found {len(hits)} times: {anchor!r}"
    lines.insert(hits[0] + 1, text); return "\n".join(lines)


def guard(src, cond, skipped_msg):
    return f"if {cond}:\n" + "\n".join("    " + l for l in src.split("\n")) + f"\nelse:\n    print({skipped_msg!r})"


def cells(p):
    return [c.source for c in nbformat.read(p, as_version=4).cells]


def notebook(md, codes, kaggle):
    nb = new_notebook(cells=[new_markdown_cell(md)] + [new_code_cell(c) for c in codes])
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python"},
                   "accelerator": "GPU", "colab": {"provenance": [], "gpuType": "T4"}}
    if kaggle: nb.metadata["kaggle"] = {"accelerator": "nvidiaTeslaT4", "isInternetEnabled": True, "isGpuEnabled": True, "language": "python"}
    nbformat.validate(nb); return nb


def header(title, source, body_rows, kaggle):
    run = ("Kaggle: Add Input > your private datasets (see KAGGLE.md); Session options > Accelerator GPU T4 x2, Internet on; Run all."
           if kaggle else "Runtime > Change runtime type > T4 GPU. Left pane > Files > Upload the zips below into `/content`. Runtime > Run all.")
    real = ("Set `SMOKE = False` in the PREFLIGHT cell, then Save Version > Save & Run All (runs in the background)." if kaggle
            else "Set `SMOKE = False` in the PREFLIGHT cell, then Runtime > Restart session and run all.")
    rows = [("How to run", run), ("First run", "`SMOKE = True` (default): 20 samples, under 5 min. Its outputs are a code check, never results."), ("Real run", real)] + body_rows
    return (f"# {title}\n\n**HARDENED {'KAGGLE ' if kaggle else ''}VARIANT, NOT RUN YET.** Generated by `scripts/make_colab_hardened.py` from `{source}`. "
            "Model, data and SHAP code are copied unchanged; only setup, output paths, checkpoint mirroring and packaging differ.\n\n"
            "| | |\n|---|---|\n" + "\n".join(f"| {a} | {b} |" for a, b in rows) +
            "\n\nThe PREFLIGHT cell prints one PASS/FAIL table (GPU, internet, Hugging Face download, the 36 input files with SHA-256, free disk, "
            "library versions) and stops on the first FAIL with the exact fix. Input ladder: (a) uploaded zip, (b) Google Drive if it mounts within 60 s "
            "(Kaggle: attached datasets), (c) stop with the list of missing files. Drive is never required.")


def build(sha, outdir):
    c04, c06, cfs = cells(SRC04), cells(SRC06), cells(SRCCFS)
    assert c04[1].startswith('NOTEBOOK = "04_train_matcher_save"') and c06[1].startswith('NOTEBOOK = "06_explainability"') and c04[2] == c06[2]
    # ---- 04: matcher retrain (already checkpoints every epoch; add mirror/restore) ----
    t4 = patch(c04[4], 'ck = out_dir / "ckpt_last.pt"\n', 'ck = out_dir / "ckpt_last.pt"; ckpt_restore(out_dir)          # HARDENED: Drive mirror / earlier output\n')
    t4 = patch(t4, '"state": st}, ck)\n', '"state": st}, ck); ckpt_mirror(out_dir)   # HARDENED: checkpoint mirrored every epoch\n')
    t4 = patch(t4, 'json.dump(m, open(out_dir / "metrics.json", "w"), indent=1)\n', 'json.dump(m, open(out_dir / "metrics.json", "w"), indent=1); ckpt_mirror(out_dir)\n')
    t5 = patch(c04[5], 'out = MATCH2 / f"ft20_s{sd}"\n', 'out = MATCH2 / f"ft20_s{sd}"; ckpt_restore(out)\n')
    t6 = patch(c04[6], "if not SMOKE:\n    for sd in SEED_ORDER[1:]: run_seed(sd)",
               "if not SMOKE and EXTRA_SEEDS:\n    for sd in SEED_ORDER[1:]: run_seed(sd)\nelse:\n    print('extra seeds 43-46 skipped (set EXTRA_SEEDS = True in the PREFLIGHT cell; about 25 min per seed)')")
    rows04 = [("Inputs", "`thesis_inputs.zip` (36 files). Model `BAAI/bge-base-en-v1.5` from Hugging Face."),
              ("Outputs", "`<out>/run_match_2_saved/ft20_s42/` (`matcher_state.pt`, scores, `metrics.json`) and manifests, zipped to `colab_out_04_train_matcher_save.zip`. "
                          "`<out>` = `/content/out` (Kaggle `/kaggle/working/out`; smoke runs `out_smoke`)"),
              ("Runtime (T4, estimate)", "smoke under 5 min; seed 42: 20-30 min (estimate printed in the original notebook) plus about 1 min of Drive mirroring"),
              ("Resume", "`ckpt_last.pt` after every epoch; re-run all. Survives a kernel restart; with Drive mounted also a new runtime.")]
    parts04 = ["showcase_runs/04_train_matcher_save", "run_match_2_saved"]
    codes04 = lambda k: [preflight("04_train_matcher_save", False, True, 10, parts04, not k, sha), c04[2], c04[3], t4, t5, t6, c04[7], FINAL]
    # ---- 06: SHAP of the full fusion (appends one jsonl line per sentence; mirror every 5) ----
    s6 = patch(c06[6], "N_SHAP = 2 if SMOKE else 100", 'N_SHAP = (N_SMOKE if device.type == "cuda" else 2) if SMOKE else 100')
    s8 = patch(c06[8], "done = {json.loads(l)", "ckpt_restore(SHAP_OUT)                     # HARDENED: Drive mirror / earlier output\ndone = {json.loads(l)")
    s8 = insert_after(s8, 'with open(SHAP_OUT, "a", encoding="utf-8") as fh:', "    if j % 5 == 0: ckpt_mirror(SHAP_OUT)   # HARDENED: checkpoint every 5 sentences (the local file gets every sentence)")
    s8 += "\nckpt_mirror(SHAP_OUT); ckpt_wait()"
    rows06 = [("Inputs", "`thesis_inputs.zip` (36 files) + `thesis_weights_s42.zip` (RoBERTa and SecBERT seed 42) + the seed-42 matcher from 04 "
               "(Drive mirror, `colab_out_04_train_matcher_save.zip`, or the same output folder)"),
              ("Outputs", "`fusion_shap_full_s42.jsonl`, `fusion_shap_summary.json`, manifests, zipped to `colab_out_06_explainability.zip`"),
              ("Runtime (T4, estimate)", "smoke under 5 min; 100 sentences: 30-60 min (estimate)"),
              ("Resume", "one jsonl line per sentence; Drive copy every 5 sentences; re-run all and finished sentences are skipped.")]
    codes06 = lambda k: [preflight("06_explainability", True, False, 6, ["showcase_runs/06_explainability"], not k, sha), *c06[2:6], s6, c06[7], s8, c06[9], c06[10], FINAL]
    # ---- colab_fusion_shap: matcher + SHAP in one runtime ----
    compat = ('\n# ---- names of the original Cell 1, now pointing at the ladder inputs and the output root ----\n'
              'import math, torch\n'
              'DATA_DIR, CLS_ROOT, SHAP_DIR = f"{BASE}/Dataset", f"{BASE}/Exp_1_4_run_tram_2_epoc_30", f"{BASE}/Exp_3_0_shap"\n'
              'OUT2, SHAP_OUT = f"{OUT_ROOT}/run_match_2_saved", f"{OUT_ROOT}/Exp_3_0_shap/fusion_shap_full_s42.jsonl"\n'
              'os.makedirs(OUT2, exist_ok=True); os.makedirs(os.path.dirname(SHAP_OUT), exist_ok=True)\n'
              'SEED, BASE_MODEL = 42, "BAAI/bge-base-en-v1.5"\n'
              'device = torch.device("cuda" if torch.cuda.is_available() else "cpu")\n'
              'print("device:", device, "| outputs:", OUT2, SHAP_OUT)')
    k2 = patch(cfs[2], '    df = pd.read_csv(f"{DATA_DIR}/tram_{name}.tsv", sep="\\t").rename(columns={"text1": "text"})\n',
               '    p = f"{DATA_DIR}/tram_{name}.tsv"\n'
               '    if os.path.exists(p):\n'
               '        df = pd.read_csv(p, sep="\\t").rename(columns={"text1": "text"})\n'
               '    elif name == "train":     # HARDENED: tram_train.tsv is not in thesis_inputs.zip; the tram slice of combined_train.csv is the same data (as notebook 04; asserts below)\n'
               '        df = pd.read_csv(f"{DATA_DIR}/combined_train.csv"); df = df[df["source_dataset"] == "tram"].rename(columns={"text1": "text"})\n'
               '    else:\n'
               '        raise FileNotFoundError(p)\n')
    k3 = cfs[3]
    k3 = patch(k3, "# Cell 3 - train the matcher (seed 42) exactly as Exp_2.1 Cell 3/6.1, and SAVE the weights\n",
               "# Cell 3 - train the matcher (seed 42) exactly as Exp_2.1 Cell 3/6.1, and SAVE the weights\n"
               "# HARDENED: checkpoint after every epoch (ckpt_last.pt, mirrored to Drive if mounted) and resume from it; SMOKE = 1 epoch on 20 sentences.\n")
    k3 = patch(k3, "text_max_len=128, label_max_len_train=128, label_max_len_eval=256):\n",
               "text_max_len=128, label_max_len_train=128, label_max_len_eval=256, n_train=None):\n")
    k3 = patch(k3, '    N = len(train); texts = train["text"].tolist(); label_texts = np.array(LABEL_TEXTS, dtype=object)\n',
               '    N = len(train) if n_train is None else min(n_train, len(train)); texts = train["text"].tolist()[:N]; label_texts = np.array(LABEL_TEXTS, dtype=object)\n')
    k3 = patch(k3, "    best, best_ep, best_state, bad, hist = -1.0, 0, None, 0, []\n    for ep in range(1, epochs + 1):\n",
               "    best, best_ep, bad, hist, start = -1.0, 0, 0, [], 1\n"
               '    ck = f"{out_dir}/ckpt_last.pt"; ckpt_restore(out_dir)\n'
               "    if os.path.exists(ck):\n"
               '        c = torch.load(ck, map_location="cpu", weights_only=False)\n'
               '        model.load_state_dict(c["model"]); opt.load_state_dict(c["opt"]); sched.load_state_dict(c["sched"])\n'
               '        if c.get("scaler"): scaler.load_state_dict(c["scaler"])\n'
               '        rng.bit_generator.state = c["rng"]; torch.set_rng_state(c["torch_rng"])\n'
               '        if c.get("cuda_rng") is not None and torch.cuda.is_available(): torch.cuda.set_rng_state_all(c["cuda_rng"])\n'
               '        best, best_ep, bad, hist, start = c["best"], c["best_ep"], c["bad"], c["hist"], c["epoch"] + 1\n'
               '        print(f"  resumed after epoch {c[\'epoch\']} (best dev MRR@3 {best:.4f} at epoch {best_ep})")\n'
               "    for ep in range(start, epochs + 1):\n"
               "        if bad >= patience: break\n")
    k3 = patch(k3, "            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}\n"
                   '            torch.save(best_state, f"{out_dir}/matcher_state.pt")            # <- the weights the old notebook never saved\n'
                   "        else:\n"
                   "            bad += 1\n"
                   '            if bad >= patience: print(f"  early stop (no dev improvement for {patience} epochs)"); break\n'
                   "    model.load_state_dict(best_state)\n",
               '            torch.save({k: v.detach().cpu().clone() for k, v in model.state_dict().items()}, f"{out_dir}/matcher_state.pt")            # <- the weights the old notebook never saved\n'
               "        else:\n"
               "            bad += 1\n"
               '        torch.save({"model": model.state_dict(), "opt": opt.state_dict(), "sched": sched.state_dict(), "scaler": scaler.state_dict(), "rng": rng.bit_generator.state,\n'
               '                    "torch_rng": torch.get_rng_state(), "cuda_rng": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None,\n'
               '                    "epoch": ep, "best": best, "best_ep": best_ep, "bad": bad, "hist": hist}, ck); ckpt_mirror(out_dir)\n'
               '        if bad >= patience: print(f"  early stop (no dev improvement for {patience} epochs)"); break\n'
               '    model.load_state_dict(torch.load(f"{out_dir}/matcher_state.pt", map_location="cpu"))      # best epoch (same as the in-memory copy before)\n')
    k3 = patch(k3, 'open(f"{out_dir}/metrics.json", "w"), indent=2)\n', 'open(f"{out_dir}/metrics.json", "w"), indent=2)\n    ckpt_mirror(out_dir)\n')
    k3 = patch(k3, 'def train_seed(sd):\n    out = f"{OUT2}/ft20_s{sd}"\n    if os.path.exists(f"{out}/metrics.json"): print("skip (already done):", out)\n    else: train_matcher_save(BASE_MODEL, out, seed=sd)\n',
               'def train_seed(sd):\n    out = f"{OUT2}/ft20_s{sd}"; ckpt_restore(Path(out)); mp = f"{out}/metrics.json"\n'
               '    if os.path.exists(mp) and json.load(open(mp)).get("finished"): print("skip (already done):", out)\n'
               '    elif SMOKE: train_matcher_save(BASE_MODEL, out, seed=sd, epochs=1, n_train=N_SMOKE, n_neg=4, label_max_len_train=32, label_max_len_eval=32)\n'
               '    else: train_matcher_save(BASE_MODEL, out, seed=sd)\n')
    k5 = patch(cfs[5], "N_SHAP, N_PERM, SHAP_SEED, MAX_LEN, K_HIDE, N_RANDOM = 100, 40, 42, 128, 3, 20",
               "N_SHAP, N_PERM, SHAP_SEED, MAX_LEN, K_HIDE, N_RANDOM = (N_SMOKE if SMOKE else 100), (4 if SMOKE else 40), 42, 128, 3, 20   # SMOKE: 20 sentences, 4 permutations")
    k5 = patch(k5, "done = set()\n", "ckpt_restore(Path(SHAP_OUT)); done = set()      # HARDENED: Drive mirror / earlier output\n")
    k5 = insert_after(k5, 'with open(SHAP_OUT, "a", encoding="utf-8") as fh:', "    if j % 5 == 0: ckpt_mirror(Path(SHAP_OUT))   # HARDENED: checkpoint every 5 sentences (the local file gets every sentence)")
    k5 = patch(k5, 'print("stored:", SHAP_OUT)', 'print("stored:", SHAP_OUT); ckpt_mirror(Path(SHAP_OUT)); ckpt_wait()')
    k6 = patch(cfs[6], "def ci(x):\n", 'def ci(x):\n    if len(x) == 0: return [float("nan")] * 2\n')
    kman = ("# HARDENED: manifests for the ingest step (inputs and outputs with SHA-256, metrics, environment)\n"
            '_o = Path(OUT2) / f"ft20_s{SEED}"; _mt = json.load(open(_o / "metrics.json"))\n'
            'write_manifest(f"matcher_ft20_s{SEED}", "matcher", SEED, _mt["config"], [Path(DATA_DIR) / "tram_test.tsv"], [_o / "matcher_state.pt", _o / "test_scores.npy", _o / "dev_scores.npy", _o / "metrics.json"], _mt["test"], "DONE")\n'
            '_recs = [json.loads(l) for l in open(SHAP_OUT, encoding="utf-8") if l.strip()]\n'
            '_sm = {"n_sentences": len(_recs), "fused_top1_correct": float(np.mean([r["fused_top1_correct"] for r in _recs])), "max_additivity_error": max(r["additivity_error"] for r in _recs)}\n'
            'write_manifest("fusion_shap", "fusion-shap", SEED, METHOD, [_o / "matcher_state.pt"], [Path(SHAP_OUT)], _sm, "DONE" if len(_recs) >= N_SHAP else "PARTIAL")\n'
            'print("manifests:", sorted(p.name for p in OUT.glob("manifest_*.json")))')
    k7 = guard(cfs[7], "not SMOKE and EXTRA_SEEDS", "optional matcher seeds 43, 44 skipped (set EXTRA_SEEDS = True in the PREFLIGHT cell; about 1 h)")
    rowscfs = [("Inputs", "`thesis_inputs.zip` (36 files) + `thesis_weights_s42.zip`. Model `BAAI/bge-base-en-v1.5` from Hugging Face."),
               ("Outputs", "`/content/out/run_match_2_saved/ft20_s42/`, `/content/out/Exp_3_0_shap/fusion_shap_full_s42.jsonl`, manifests, zipped to `colab_out_colab_fusion_shap.zip` (smoke runs: `/content/out_smoke`)"),
               ("Runtime (T4, estimate)", "smoke under 5 min; matcher 20-30 min + SHAP 30-60 min (estimates of the original notebook)"),
               ("Use", "One runtime does what 04 (seed 42) + 06 do, so no hand-off is needed without Drive. Run either this notebook or 04 + 06, never both."),
               ("Resume", "`ckpt_last.pt` after every epoch, SHAP jsonl after every sentence (Drive copy every 5); re-run all.")]
    codescfs = [preflight("colab_fusion_shap", True, True, 10, ["showcase_runs/colab_fusion_shap", "run_match_2_saved", "Exp_3_0_shap"], True, sha) + compat,
                k2, k3, cfs[4], k5, k6, kman, k7, FINAL]
    out = {}
    for k in (False, True):
        d = outdir / ("kaggle" if k else "colab"); d.mkdir(parents=True, exist_ok=True); suf = "KAGGLE" if k else "HARDENED"
        out[d / f"04_train_matcher_save_{suf}.ipynb"] = notebook(header("04 Train the matcher and SAVE the weights", "notebooks/04_train_matcher_save.ipynb", rows04, k), codes04(k), k)
        out[d / f"06_explainability_{suf}.ipynb"] = notebook(header("06 Explainability of the full fusion", "notebooks/06_explainability.ipynb", rows06, k), codes06(k), k)
    out[outdir / "colab" / "colab_fusion_shap_HARDENED.ipynb"] = notebook(header("Matcher retrain with saved weights + SHAP of the full fusion (one runtime)",
                                                                                   "_evidence_pack/09_repro/colab_fusion_shap.ipynb", rowscfs, False), codescfs, False)
    for p, nb in out.items():
        for c in nb.cells:
            if c.cell_type == "code": compile(c.source, str(p), "exec")
        nbformat.write(nb, p)
    return list(out)


RUN_COLAB = r"""# Run on Colab (hardened notebooks: Drive optional, SMOKE first)
1. colab.research.google.com > File > Upload notebook > `colab\04_train_matcher_save_HARDENED.ipynb`. Runtime > Change runtime type > T4 GPU > Save.
2. Left pane > Files (folder icon) > Upload `thesis_inputs.zip` into `/content` (06 and colab_fusion_shap: also `thesis_weights_s42.zip`).
3. Runtime > Run all. `SMOKE = True` (default) runs 20 samples in under 5 min. Every PREFLIGHT row must be PASS; a FAIL row prints its fix.
4. Real run: set `SMOKE = False` in the PREFLIGHT cell, Runtime > Restart session and run all. Allow Drive if asked (optional: lets a new runtime resume).
5. The FINAL cell zips `/content/out` to `colab_out_<notebook>.zip`, copies it to Drive (if mounted), downloads it, and lists the files to bring back.
6. Then `colab\06_explainability_HARDENED.ipynb` the same way. It finds 04's matcher on Drive; without Drive, also upload `colab_out_04_train_matcher_save.zip`.
   One-runtime alternative to 04 + 06: `colab\colab_fusion_shap_HARDENED.ipynb`. Run one of the two paths, never both.
7. Bring back: unzip every `colab_out_*.zip` (not `*_SMOKE.zip`) into `E:\Osamas Paper\_colab_returned\`, then `python scripts\ingest_colab.py`.
Order and minutes (T4, estimates): 04 smoke 5 > 04 seed 42 25-35 > 06 smoke 5 > 06 real 30-60 (about 1.5 h). Or: colab_fusion_shap smoke 5 > real 55-95.
"""

KAGGLE = r"""# Run on Kaggle (free T4 GPU; a saved version runs in the background, so no disconnects)

One-time: kaggle.com > sign in > your profile > Settings > Phone verification (needed for GPU and internet).

1. Datasets: kaggle.com > Create > New Dataset > drag `thesis_inputs.zip` > title `thesis-inputs` > visibility Private > Create.
   Repeat with `thesis_weights_s42.zip` > title `thesis-weights-s42` (needed by 06). Kaggle unzips them; the notebooks find the files anywhere under `/kaggle/input`.
2. Notebook 04: Create > New Notebook > File > Import Notebook > `kaggle\04_train_matcher_save_KAGGLE.ipynb`.
3. Right panel: Add Input > Datasets > Your Datasets > `thesis-inputs` > Add. Session options: Accelerator **GPU T4 x2** (not P100), Internet **On**.
4. Run all. `SMOKE = True` (default) takes under 5 min. Every PREFLIGHT row must be PASS; a FAIL row prints its fix.
5. Real run: set `SMOKE = False` in the PREFLIGHT cell > Save Version (top right) > Save & Run All (Commit) > Save. You can close the browser.
6. When the version is done (Your Work > the notebook > Versions): open it > Output > download `colab_out_04_train_matcher_save.zip`.
7. Notebook 06: import `kaggle\06_explainability_KAGGLE.ipynb`; Add Input: `thesis-inputs`, `thesis-weights-s42`, and Your Work > the 04 notebook
   (its output holds the matcher). Then steps 4-6; the zip is `colab_out_06_explainability.zip`.

Resume: if a version stops early, add that version's output as an input (Add Input > Your Work) and save a new version. The notebook restores
`ckpt_last.pt` (matcher, every epoch) and the SHAP jsonl (every sentence) from it and skips the finished part.
Outputs go to `/kaggle/working/out` (smoke runs: `/kaggle/working/out_smoke`). Limits: 12 h per session, about 30 GPU hours per week.

Bring back: unzip each `colab_out_*.zip` (not `*_SMOKE.zip`) into `E:\Osamas Paper\_colab_returned\`, then run `python scripts\ingest_colab.py`.
Order and minutes (T4, estimates): 04 smoke 5 > 04 real 20-30 > 06 smoke 5 > 06 real 30-60.
"""


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--no-weights", action="store_true"); ap.add_argument("--no-zips", action="store_true"); a = ap.parse_args()
    DST.mkdir(parents=True, exist_ok=True)
    missing = [r for r in REQUIRED + WEIGHTS if not (ROOT / r).is_file()]
    if missing: sys.exit("missing source files: " + ", ".join(missing))
    sha = {r: sha256(ROOT / r) for r in REQUIRED + WEIGHTS}
    (DST / "inputs_sha256.json").write_text(json.dumps({"required_36": {r: sha[r] for r in REQUIRED}, "weights_s42_8": {r: sha[r] for r in WEIGHTS}}, indent=1), encoding="utf-8")
    nbs = build(sha, DST)
    if not a.no_zips:
        need = sum((ROOT / r).stat().st_size for r in REQUIRED + ([] if a.no_weights else WEIGHTS))
        if need * 1.2 > shutil.disk_usage(DST).free: sys.exit(f"not enough disk space for the zips: need {need / 1e9:.2f} GB")
        for name, rels, mode in [("thesis_inputs.zip", REQUIRED, zipfile.ZIP_DEFLATED)] + ([] if a.no_weights else [("thesis_weights_s42.zip", WEIGHTS, zipfile.ZIP_STORED)]):
            tmp = DST / (name + ".part")
            with zipfile.ZipFile(tmp, "w", mode, allowZip64=True) as zf:
                for r in rels: zf.write(ROOT / r, r)
            with zipfile.ZipFile(tmp) as zf:                       # read back: names and CRCs
                assert sorted(zf.namelist()) == sorted(rels) and zf.testzip() is None, name
            tmp.replace(DST / name); print(f"{name}: {len(rels)} files, {(DST / name).stat().st_size / 1e6:.1f} MB")
    (DST / "RUN_COLAB.md").write_text(RUN_COLAB, encoding="utf-8"); (DST / "KAGGLE.md").write_text(KAGGLE, encoding="utf-8")
    assert len(RUN_COLAB.strip().splitlines()) <= 12, "RUN_COLAB.md must stay within 12 lines"
    for p in nbs: print("notebook:", p.relative_to(SHOW))
    print("\nRUN ORDER (T4, expected minutes; estimates, not measured):")
    for s in ["1  colab/04_train_matcher_save_HARDENED   SMOKE=True     ~5",
              "2  colab/04_train_matcher_save_HARDENED   SMOKE=False    25-35  (seed 42; EXTRA_SEEDS=True adds ~25 per seed)",
              "3  colab/06_explainability_HARDENED       SMOKE=True     ~5     (needs thesis_weights_s42.zip; matcher from step 2)",
              "4  colab/06_explainability_HARDENED       SMOKE=False    30-60  (100 sentences)",
              "   alternative to 1-4 in one runtime: colab/colab_fusion_shap_HARDENED  SMOKE=True ~5, then SMOKE=False 55-95",
              "   Kaggle: kaggle/04_..._KAGGLE then kaggle/06_..._KAGGLE, same minutes (see KAGGLE.md)",
              "5  PC: unzip colab_out_*.zip into _colab_returned/, python scripts/ingest_colab.py   ~1"]:
        print("  " + s)


if __name__ == "__main__":
    main()
