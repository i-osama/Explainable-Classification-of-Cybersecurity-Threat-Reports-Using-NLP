"""Q1 wave 2 Task 3 / prereg 18: split-conformal prediction sets, calibrated on DEV, TEST once.
Writes results/conformal.csv, conformal_family.csv, conformal_buckets.csv. Run: python scripts/run_conformal.py"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import wilcoxon

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap import RESULTS
from ttpmap.data import build_space
from ttpmap.fusion import components, fuse
from ttpmap.stats import bootstrap_ci, paired_bootstrap, holm, wilson
from ttpmap import conformal as cp

S = build_space(); Yd, Y = S.Y["dev"], S.Y["test"]
Zd, Z = components(S, "dev", "avg"), components(S, "test", "avg")
NAMES = {"fusion": "Fusion (3,1,1,1)", "matcher": "Matcher (3-seed ens.)", "svm": "TF-IDF + SVM", "roberta": "RoBERTa (3-seed avg)", "secbert": "SecBERT (3-seed avg)"}
DEV = {"fusion": fuse(Zd, (3, 1, 1, 1)), **{k: Zd[k] for k in ("matcher", "svm", "roberta", "secbert")}}
TEST = {"fusion": fuse(Z, (3, 1, 1, 1)), **{k: Z[k] for k in ("matcher", "svm", "roberta", "secbert")}}

rows, per = [], {}
for alpha in (0.10, 0.20):
    for key in NAMES:
        for rule in ("score", "rank"):
            if rule == "score":
                par = cp.calibrate_threshold(DEV[key], Yd, alpha, split="dev"); sets = cp.sets_by_threshold(TEST[key], par)
            else:
                par = cp.calibrate_rank(DEV[key], Yd, alpha, split="dev"); sets = cp.sets_by_rank(TEST[key], par)
            r = cp.per_row(sets, Y); m = cp.set_metrics(sets, Y); per[alpha, key, rule] = r
            ok = r["covered_all"][~np.isnan(r["covered_all"])]; lo, hi = wilson(int(ok.sum()), len(ok)); sz = bootstrap_ci(r["size"])
            rows.append({"alpha": alpha, "system": NAMES[key], "rule": rule, "param": par, "coverage_all": m["coverage_all"], "cov_lo": lo, "cov_hi": hi,
                         "nominal": 1 - alpha, "nominal_in_ci": bool(lo <= 1 - alpha <= hi), "coverage_any": m["coverage_any"],
                         "size_mean": m["size_mean"], "size_lo": sz["lo"], "size_hi": sz["hi"], "size_median": m["size_median"], "size_p90": m["size_p90"],
                         "empty_rate": m["empty_rate"], "n": len(ok)})

fam = []
f = per[0.10, "fusion", "score"]["size"]
for key in ("matcher", "svm", "roberta", "secbert"):
    c = per[0.10, key, "score"]["size"]; pb = paired_bootstrap(f, c); d = f - c
    p = float(wilcoxon(d).pvalue) if np.any(d != 0) else 1.0
    fam.append({"A": NAMES["fusion"], "B": NAMES[key], "alpha": 0.10, "rule": "score", "size_A": float(f.mean()), "size_B": float(c.mean()),
                "delta_size": pb["delta"], "ci_lo": pb["lo"], "ci_hi": pb["hi"], "p_wilcoxon": p})
for x, p in zip(fam, holm([x["p_wilcoxon"] for x in fam])):
    x["p_holm"] = p; x["family_size"] = len(fam); x["supported"] = bool(p < 0.05 and x["ci_hi"] < 0)

rarest = np.where(Y, S.train_count[None, :], 10 ** 9).min(axis=1)
B = {"unseen": rarest == 0, "1-4": (rarest >= 1) & (rarest <= 4), "5-9": (rarest >= 5) & (rarest <= 9), "10-19": (rarest >= 10) & (rarest <= 19),
     "20-49": (rarest >= 20) & (rarest <= 49), "50+": (rarest >= 50) & (rarest < 10 ** 9)}
bk = []
for b, mk in B.items():
    for key in NAMES:
        r = per[0.10, key, "score"]; ok = r["covered_all"][mk]; ok = ok[~np.isnan(ok)]; lo, hi = wilson(int(ok.sum()), len(ok))
        bk.append({"bucket": b, "system": NAMES[key], "alpha": 0.10, "rule": "score", "n_sentences": int(mk.sum()),
                   "coverage_all": float(ok.mean()) if len(ok) else np.nan, "cov_lo": lo, "cov_hi": hi, "size_mean": float(r["size"][mk].mean()) if mk.any() else np.nan})

pd.DataFrame(rows).to_csv(RESULTS / "conformal.csv", index=False); pd.DataFrame(fam).to_csv(RESULTS / "conformal_family.csv", index=False)
pd.DataFrame(bk).to_csv(RESULTS / "conformal_buckets.csv", index=False)
pd.set_option("display.width", 250)
print(pd.DataFrame(rows).round(3).to_string(index=False)); print(pd.DataFrame(fam).round(4).to_string(index=False)); print(pd.DataFrame(bk).round(3).to_string(index=False))
