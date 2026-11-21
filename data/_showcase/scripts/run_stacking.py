"""Q1 plan Task 4 / prereg 15: stacked fusion fitted on DEV, test once.
Writes results/stacking.csv, stacking_family.csv, stacking_buckets.csv, stacking_model.json. Run: python scripts/run_stacking.py"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap import RESULTS
from ttpmap.data import build_space
from ttpmap.fusion import components, fuse
from ttpmap.metrics import hit_at_1, rr_at_k, recall_at_k_micro, rank_topk
from ttpmap.stats import bootstrap_ci, paired_bootstrap, mcnemar_exact, holm
from ttpmap.stack import pair_features, fit_stacker, FEATURES

S = build_space(); Y = S.Y["test"]; n, L = Y.shape; un = Y & ~S.seen[None, :]
Zd, Z = components(S, "dev", "avg"), components(S, "test", "avg")
m = fit_stacker(pair_features(Zd, S.train_count), S.Y["dev"], split="dev")
SYS = {"Stacked fusion (LR)": m.score(pair_features(Z, S.train_count)), "Fusion (3,1,1,1)": fuse(Z, (3, 1, 1, 1)), "Fusion (4,1,1,1)": fuse(Z, (4, 1, 1, 1)),
       "Matcher (3-seed ens.)": Z["matcher"]}
H = {k: hit_at_1(v, Y) for k, v in SYS.items()}
rows = []
for k, Sc in SYS.items():
    c, r = bootstrap_ci(H[k]), bootstrap_ci(rr_at_k(Sc, Y)); it = np.zeros(Y.shape, bool); it[np.arange(n)[:, None], rank_topk(Sc, 5)] = True
    rows.append({"system": k, "P@1": c["mean"], "P@1_lo": c["lo"], "P@1_hi": c["hi"], "MRR@3": r["mean"], "MRR@3_lo": r["lo"], "MRR@3_hi": r["hi"],
                 "R@5_micro": recall_at_k_micro(Sc, Y, 5), "unseen_R@5": float((it & un).sum() / un.sum()), "n": n})
fam = []
for ref in ("Fusion (3,1,1,1)", "Fusion (4,1,1,1)"):
    pb = paired_bootstrap(H["Stacked fusion (LR)"], H[ref]); mc = mcnemar_exact(H["Stacked fusion (LR)"], H[ref])
    fam.append({"A": "Stacked fusion (LR)", "B": ref, "delta_P@1": pb["delta"], "ci_lo": pb["lo"], "ci_hi": pb["hi"], "p_mcnemar": mc["p"], "mcnemar_b": mc["b"], "mcnemar_c": mc["c"]})
for f, p in zip(fam, holm([f["p_mcnemar"] for f in fam])):
    f["p_holm"] = p; f["family_size"] = len(fam); f["success_rule_met"] = bool(f["B"] == "Fusion (3,1,1,1)" and p < 0.05 and f["ci_lo"] > 0)
rarest = np.where(Y, S.train_count[None, :], 10 ** 9).min(axis=1)
B = {"unseen": rarest == 0, "1-4": (rarest >= 1) & (rarest <= 4), "5-9": (rarest >= 5) & (rarest <= 9), "10-19": (rarest >= 10) & (rarest <= 19),
     "20-49": (rarest >= 20) & (rarest <= 49), "50+": rarest >= 50}
bk = [{"bucket": b, "system": k, "n_sentences": int(mk.sum()), "P@1": float(H[k][mk].mean()), **{x: bootstrap_ci(H[k][mk])[y] for x, y in (("lo", "lo"), ("hi", "hi"))}}
      for b, mk in B.items() for k in SYS]
pd.DataFrame(rows).to_csv(RESULTS / "stacking.csv", index=False); pd.DataFrame(fam).to_csv(RESULTS / "stacking_family.csv", index=False)
pd.DataFrame(bk).to_csv(RESULTS / "stacking_buckets.csv", index=False)
json.dump({"C": m.C, "cv_mrr3": {str(k): v for k, v in m.cv.items()}, "features": FEATURES, "coef": m.model.coef_[0].tolist(), "intercept": float(m.model.intercept_[0])},
          open(RESULTS / "stacking_model.json", "w"), indent=1)
print(pd.DataFrame(rows).round(4).to_string(index=False)); print(pd.DataFrame(fam).round(4).to_string(index=False))
print("C", m.C, "cv", {k: round(v, 4) for k, v in m.cv.items()}, "coef", dict(zip(FEATURES, np.round(m.model.coef_[0], 3))))
