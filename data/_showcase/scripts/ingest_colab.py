"""Q1 plan Task 8: bring Colab results back. Download the Drive folders `KDU/Thesis/showcase_runs/` and `KDU/Thesis/run_match_2_saved/`
into `E:\\Osamas Paper\\_colab_returned\\` (keep the folder names), then run:
    python scripts/ingest_colab.py [--src <folder>]
Exit 1 (nothing copied) if any manifest output is missing, differs by SHA-256, or is a SMOKE run.
On success the files go to results/colab/<run_id>/ and build_numbers.py fills the TODO-COLAB ids it can."""
import argparse, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap import ROOT, RESULTS
from ttpmap.ingest import ingest

ap = argparse.ArgumentParser(); ap.add_argument("--src", default=str(ROOT / "_colab_returned")); a = ap.parse_args()
r = ingest(Path(a.src), RESULTS / "colab")
if not r["ok"]:
    print("INGEST: FAIL (nothing copied)"); [print("  -", b) for b in r["bad"]]; sys.exit(1)
print(f"INGEST: PASS, {r['copied']} files -> results/colab/")
sys.exit(subprocess.run([sys.executable, "-X", "utf8", str(Path(__file__).parent / "build_numbers.py")]).returncode)
