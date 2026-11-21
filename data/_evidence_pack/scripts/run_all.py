"""Re-run the whole evidence pack. Usage (from this folder):
    "E:\\Osamas Paper\\.venv\\Scripts\\python.exe" run_all.py [--fast]
--fast skips the CPU deletion-test re-run (T6 uses the saved CSV only) and the fusion-SHAP extra.
Every script only READS project files and writes inside _evidence_pack\\."""
import subprocess, sys, time
from pathlib import Path
HERE = Path(__file__).parent
fast = "--fast" in sys.argv
STEPS = [("T0 inventory", ["t0_inventory.py"]), ("notebook dump", ["nb_dump.py"]), ("T1 dataset", ["t1_dataset.py"]),
         ("T3 results", ["t3_results.py"]), ("T4 statistics", ["t4_bootstrap.py"]), ("T5 errors", ["t5_errors.py"]),
         ("T6 SHAP", ["t6_shap.py"] + (["--no-model"] if fast else [])), ("T7 human", ["t7_human.py"]),
         ("X0 fusion vs roberta", ["x0_fusion_vs_roberta.py"])]
if not fast:
    STEPS += [("X1 fusion SHAP (partial)", ["x1_fusion_shap.py", "--n", "40"]), ("X2 fusion SHAP summary", ["x2_fusion_shap_summary.py"])]
STEPS += [("T9 smoke test", [str(HERE.parent / "09_repro" / "smoke_test.py")]), ("T10 report", ["t10_report.py"])]
for name, cmd in STEPS:
    t = time.time()
    r = subprocess.run([sys.executable, "-X", "utf8"] + cmd, cwd=HERE, capture_output=True, text=True, encoding="utf-8")
    print(f"{'OK  ' if r.returncode == 0 else 'FAIL'} {name:28s} {time.time() - t:6.0f}s")
    if r.returncode: print(r.stderr[-1500:]); sys.exit(1)
print("T2 (02_settings.md) and T8 (08_baseline.md) are hand-written citation tables and are not regenerated.")
