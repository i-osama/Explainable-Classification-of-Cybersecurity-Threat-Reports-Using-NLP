"""Smoke-execute the notebooks locally on CPU with SMOKE=True (20 samples; GPU-only cells guard themselves).
Outputs go to results/smoke_runs/ (never to the project data). Writes results/smoke_logs/<notebook>.json.
The executed copy is NOT saved back: the notebooks in notebooks/ stay output-free.
Usage: python scripts/smoke_notebooks.py [name-substring ...]"""
import json, os, sys, time, traceback
from pathlib import Path
import nbformat
from nbclient import NotebookClient

SHOW = Path(__file__).resolve().parents[1]; NB = SHOW / "notebooks"; LOG = SHOW / "results" / "smoke_logs"; LOG.mkdir(parents=True, exist_ok=True)
os.environ.update(TTPMAP_SMOKE="1", TTPMAP_ROOT=str(SHOW.parent), TTPMAP_SMOKE_OUT=str(SHOW / "results" / "smoke_runs"), TOKENIZERS_PARALLELISM="false", HF_HUB_OFFLINE="1")
sel = sys.argv[1:]
for p in sorted(NB.glob("*.ipynb")):
    if sel and not any(s in p.name for s in sel): continue
    nb = nbformat.read(p, 4); nbformat.validate(nb); t0 = time.time(); err = ""; tail = []
    try:
        NotebookClient(nb, timeout=1500, kernel_name="python3", resources={"metadata": {"path": str(NB)}}).execute()
        status = "PASS"
    except Exception as e:
        status = "FAIL"; err = "".join(traceback.format_exception_only(type(e), e))[-1500:]
    for c in nb.cells:
        for o in c.get("outputs", []):
            if o.get("output_type") == "stream": tail += o["text"].splitlines()
    skipped = [l for l in tail if "skipped" in l.lower()]
    json.dump({"notebook": p.name, "mode": "local CPU smoke run, SMOKE=True; NOT a Colab run", "status": status, "seconds": round(time.time() - t0, 1), "nbformat_valid": True,
               "gpu_only_cells_skipped": skipped, "last_output_lines": [l[:200] for l in tail[-6:]], "error": err}, open(LOG / f"{p.stem}.json", "w"), indent=1)
    print(f"{status} {p.name} {time.time() - t0:.0f}s" + (f" | skipped: {len(skipped)}" if skipped else "") + (f"\n   {err.strip().splitlines()[-1][:300]}" if err else ""))
