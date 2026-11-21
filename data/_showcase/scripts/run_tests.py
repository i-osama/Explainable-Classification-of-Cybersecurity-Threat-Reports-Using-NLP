"""Dependency-free test runner (pytest is not installed in this environment; the same files run under pytest unchanged).
Usage: python scripts/run_tests.py     Exit code 0 only if no test fails. Writes results/test_report.json."""
import importlib.util, json, sys, time, traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
res = []
for f in sorted((ROOT / "tests").glob("test_*.py")):
    spec = importlib.util.spec_from_file_location(f.stem, f); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    for name in sorted(n for n in dir(mod) if n.startswith("test_") and callable(getattr(mod, n))):
        t = time.time()
        try:
            out = getattr(mod, name)(); status = "SKIP" if out == "SKIP" else "PASS"; err = ""
        except Exception:
            status, err = "FAIL", traceback.format_exc(limit=3)
        res.append({"file": f.name, "test": name, "status": status, "seconds": round(time.time() - t, 2), "error": err})
        if status == "FAIL": print(f"FAIL {f.name}::{name}\n{err}")
c = {s: sum(r["status"] == s for r in res) for s in ("PASS", "FAIL", "SKIP")}
(ROOT / "results").mkdir(exist_ok=True)
json.dump({"runner": "scripts/run_tests.py (pytest not installed)", "counts": c, "tests": res}, open(ROOT / "results" / "test_report.json", "w"), indent=1)
print(f"tests: {len(res)}  PASS {c['PASS']}  FAIL {c['FAIL']}  SKIP {c['SKIP']}")
sys.exit(1 if c["FAIL"] else 0)
