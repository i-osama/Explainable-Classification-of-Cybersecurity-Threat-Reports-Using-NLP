"""Q1 wave 2 Task 3, POST-HOC sensitivity (not part of prereg 18; recorded in DECISIONS.md D27).
Why: in the pre-registered run the classifier components are z-scored rows in which the 553 labels outside a classifier's
180-label space are filled with z = 0 (ttpmap.fusion.zrow). Those labels then sit above the classifier's own low-probability
labels, so a conformal set that must cover the classifier's misses swallows all of them (sets of about 558 labels).
Here the classifiers are scored with their raw mean probabilities; labels outside their space are NaN (never in a set).
Writes results/conformal_posthoc_raw.csv. Run: python scripts/run_conformal_posthoc.py"""
import sys
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap import RESULTS, SEEDS
from ttpmap.data import build_space
from ttpmap.fusion import to_full
from ttpmap.stats import bootstrap_ci, wilson
from ttpmap import conformal as cp

S = build_space(); Yd, Y = S.Y["dev"], S.Y["test"]


def raw(tag, split):
    if tag == "svm":
        return to_full(S.svm_raw[split], S.seen_idx, S.L)
    return np.mean([to_full(S.cls_raw[tag, s][split], S.cls_cols[tag, s], S.L) for s in SEEDS], axis=0)


NAMES = {"svm": "TF-IDF + SVM (raw decision score)", "roberta": "RoBERTa (3-seed mean probability)", "secbert": "SecBERT (3-seed mean probability)"}
rows = []
for alpha in (0.10, 0.20):
    for tag, name in NAMES.items():
        D, T = raw(tag, "dev"), raw(tag, "test")
        for rule in ("score", "rank"):
            if rule == "score":
                par = cp.calibrate_threshold(D, Yd, alpha, split="dev"); sets = cp.sets_by_threshold(T, par)
            else:
                par = cp.calibrate_rank(D, Yd, alpha, split="dev"); sets = cp.sets_by_rank(T, par)
            r = cp.per_row(sets, Y); m = cp.set_metrics(sets, Y); ok = r["covered_all"][~np.isnan(r["covered_all"])]
            lo, hi = wilson(int(ok.sum()), len(ok)); sz = bootstrap_ci(r["size"])
            rows.append({"analysis": "POST-HOC", "alpha": alpha, "system": name, "rule": rule, "param": par, "coverage_all": m["coverage_all"],
                         "cov_lo": lo, "cov_hi": hi, "nominal_in_ci": bool(lo <= 1 - alpha <= hi), "size_mean": m["size_mean"], "size_lo": sz["lo"],
                         "size_hi": sz["hi"], "size_median": m["size_median"], "size_p90": m["size_p90"], "empty_rate": m["empty_rate"], "n": len(ok)})
pd.DataFrame(rows).to_csv(RESULTS / "conformal_posthoc_raw.csv", index=False)
print(pd.DataFrame(rows).drop(columns=["analysis"]).round(3).to_csv(index=False))
