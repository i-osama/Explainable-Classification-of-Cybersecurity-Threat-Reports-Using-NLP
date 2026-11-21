"""Smoke test (< 5 min, CPU): reproduce headline numbers from SAVED predictions.
    "E:\\Osamas Paper\\.venv\\Scripts\\python.exe" smoke_test.py
Exit code 0 only if every number matches the expected value to 3 decimals."""
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
t0 = time.time()
from common import p_at_1, mrr_at_k
from systems import build, components, fuse, rank_full
S = build(); Y = S.Yte
Z = components(S, "test", "avg")
got = {"fusion (3,1,1,1) seed-averaged P@1": p_at_1(fuse(Z, (3, 1, 1, 1)), Y).mean(),
       "fusion (3,1,1,1) seed-averaged MRR@3": mrr_at_k(fuse(Z, (3, 1, 1, 1)), Y).mean(),
       "classifiers-only ensemble P@1": p_at_1(fuse(Z, (0, 1, 1, 1)), Y).mean(),
       "matcher 3-seed ensemble P@1": p_at_1(Z["matcher"], Y).mean(),
       "TF-IDF+LinearSVC P@1 (refit)": p_at_1(rank_full(S.svm_raw["test"], S.seen_idx, S.L), Y).mean()}
exp = {"fusion (3,1,1,1) seed-averaged P@1": 0.803, "fusion (3,1,1,1) seed-averaged MRR@3": 0.856, "classifiers-only ensemble P@1": 0.774,
       "matcher 3-seed ensemble P@1": 0.777, "TF-IDF+LinearSVC P@1 (refit)": 0.742}
ok = True
for k, v in got.items():
    good = abs(round(v, 3) - exp[k]) < 1e-9; ok &= good
    print(f"{'PASS' if good else 'FAIL'}  {k:40s} got {v:.4f}  expected {exp[k]:.3f}")
print(f"{'SMOKE TEST PASSED' if ok else 'SMOKE TEST FAILED'} in {time.time() - t0:.0f}s")
sys.exit(0 if ok else 1)
