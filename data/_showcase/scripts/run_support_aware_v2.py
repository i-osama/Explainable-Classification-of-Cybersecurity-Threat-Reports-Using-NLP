"""Prereg 13: support-aware fusion with four label bands (unseen, 1-4, 5-19, 20+). Dev selection, test touched once.
Writes results/support_aware_v2.csv, results/support_aware_family.csv, results/support_aware_v2_dev_grid.csv."""
import itertools, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap import RESULTS
from ttpmap.data import build_space
from ttpmap.metrics import hit_at_1, rr_at_k
from ttpmap.fusion import components, fuse
from ttpmap.stats import paired_bootstrap, mcnemar_exact, holm

S = build_space(); Y, Yd = S.Y["test"], S.Y["dev"]; tc = S.train_count
Z, Zd = components(S, "test", "avg"), components(S, "dev", "avg")
band = np.where(tc == 0, 0, np.where(tc <= 4, 1, np.where(tc <= 19, 2, 3)))
def sa(Zx, wm): return np.array(wm, float)[band][None, :] * Zx["matcher"] + Zx["svm"] + Zx["roberta"] + Zx["secbert"]
best, rows = None, []
for wm in itertools.product([1, 2, 3, 4, 6, 8], repeat=4):
    fd = sa(Zd, wm); key = (round(float(rr_at_k(fd, Yd).mean()), 4), round(float(hit_at_1(fd, Yd).mean()), 4))
    rows.append({"w_unseen": wm[0], "w_rare": wm[1], "w_mid": wm[2], "w_frequent": wm[3], "dev_MRR@3": key[0], "dev_P@1": key[1]})
    if best is None or key > best[0]: best = (key, wm)
pd.DataFrame(rows).to_csv(RESULTS / "support_aware_v2_dev_grid.csv", index=False)
wm = best[1]; ft = sa(Z, wm); hs = hit_at_1(ft, Y)                                   # the single test evaluation
rarest = np.where(Y, tc[None, :], 10**9).min(1); rare = rarest <= 4
REF = {"(3,1,1,1)": fuse(Z, (3, 1, 1, 1)), "(4,1,1,1)": fuse(Z, (4, 1, 1, 1)), "equal (1,1,1,1)": fuse(Z, (1, 1, 1, 1))}
fam = []
for name, R in REF.items():
    hr = hit_at_1(R, Y); pb = paired_bootstrap(hs, hr); mc = mcnemar_exact(hs, hr)
    fam.append({"comparison": f"support-aware v2 vs {name}", "P@1_A": hs.mean(), "P@1_B": hr.mean(), "delta_P@1": pb["delta"], "ci_lo": pb["lo"], "ci_hi": pb["hi"],
                "mcnemar_b": mc["b"], "mcnemar_c": mc["c"], "p_mcnemar": mc["p"]})
v1 = pd.read_csv(RESULTS / "support_aware_fusion.csv").iloc[0]
band3 = np.where(tc <= 4, 0, np.where(tc <= 19, 1, 2))
h1 = hit_at_1(np.array([v1.selected_w_rare, v1.selected_w_mid, v1.selected_w_frequent], float)[band3][None, :] * Z["matcher"] + Z["svm"] + Z["roberta"] + Z["secbert"], Y)
hb = hit_at_1(REF["(3,1,1,1)"], Y); pb = paired_bootstrap(h1, hb); mc = mcnemar_exact(h1, hb)
fam.append({"comparison": "support-aware v1 (prereg 09) vs (3,1,1,1)", "P@1_A": h1.mean(), "P@1_B": hb.mean(), "delta_P@1": pb["delta"], "ci_lo": pb["lo"], "ci_hi": pb["hi"],
            "mcnemar_b": mc["b"], "mcnemar_c": mc["c"], "p_mcnemar": mc["p"]})
for r, a in zip(fam, holm([r["p_mcnemar"] for r in fam])):
    r["p_holm"] = a; r["family_size"] = len(fam)
pd.DataFrame(fam).to_csv(RESULTS / "support_aware_family.csv", index=False)
pr = paired_bootstrap(hs[rare], hb[rare]); un = rarest == 0
ok = bool(fam[0]["p_holm"] < 0.05 and fam[0]["ci_lo"] > 0 and hs[rare].mean() > hb[rare].mean())
pd.DataFrame([{"selected_w_unseen": wm[0], "selected_w_rare": wm[1], "selected_w_mid": wm[2], "selected_w_frequent": wm[3], "dev_MRR@3": best[0][0], "dev_P@1": best[0][1],
               "dev_baseline_MRR@3": round(float(rr_at_k(sa(Zd, (3, 3, 3, 3)), Yd).mean()), 4), "test_P@1": hs.mean(), "test_MRR@3": rr_at_k(ft, Y).mean(),
               "test_P@1_baseline": hb.mean(), "rare_n": int(rare.sum()), "rare_P@1": hs[rare].mean(), "rare_P@1_baseline": hb[rare].mean(), "rare_delta": pr["delta"],
               "rare_ci_lo": pr["lo"], "rare_ci_hi": pr["hi"], "unseen_n": int(un.sum()), "unseen_hits": int(hs[un].sum()), "unseen_hits_baseline": int(hb[un].sum()),
               "success_rule_met": ok, "test_evaluations": 1}]).to_csv(RESULTS / "support_aware_v2.csv", index=False)
print("selected", wm, "dev", best[0], "| test P@1", round(hs.mean(), 4), "baseline", round(hb.mean(), 4), "| rare", round(hs[rare].mean(), 3), "vs", round(hb[rare].mean(), 3), "| success:", ok)
for r in fam: print(f"  {r['comparison']}: {r['delta_P@1']:+.4f} [{r['ci_lo']:+.3f}, {r['ci_hi']:+.3f}] McNemar p={r['p_mcnemar']:.3f} Holm p={r['p_holm']:.3f}")
