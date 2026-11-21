"""T4: paired bootstrap delta-P@1 (percentile CI) + exact McNemar -> 04_bootstrap.csv, 04_statistics.md"""
import numpy as np, pandas as pd
from scipy.stats import binomtest
from common import PACK, SEEDS, p_at_1, mrr_at_k, w
from systems import build, components, fuse, rank_full, to_full

S = build(); L = S.L; Y = S.Yte; n = len(Y)
Z = components(S, "test", "avg")
def cls_avg(tag): return np.mean([to_full(S.cls_raw[tag, s]["test"], S.cls_cols[tag, s], L, -1e9) for s in SEEDS], axis=0)
SYS = {"fusion(3,1,1,1) seed-avg": fuse(Z, (3, 1, 1, 1)), "classifiers-only": fuse(Z, (0, 1, 1, 1)), "matcher 3-seed ens": Z["matcher"],
       "RoBERTa 3-seed avg": cls_avg("roberta"), "SecBERT 3-seed avg": cls_avg("secbert"),
       "SVM": rank_full(S.svm_raw["test"], S.seen_idx, L)}
H = {k: p_at_1(v, Y) for k, v in SYS.items()}; R = {k: mrr_at_k(v, Y) for k, v in SYS.items()}

PAIRS = [("C1", "fusion(3,1,1,1) seed-avg", "classifiers-only", "+0.029 [0.017, 0.043]", "Exp_2.1 CELL 13: 1000 resamples, default_rng(0)"),
         ("C2", "fusion(3,1,1,1) seed-avg", "matcher 3-seed ens", "+0.026 [0.003, 0.051]", "Exp_2.1 CELL 11: 1000 resamples, default_rng(0), first comparison in loop"),
         ("C3", "RoBERTa 3-seed avg", "SVM", "+0.014 [-0.015, 0.040]", "NOT-FOUND in any notebook (number comes from an earlier audit note)"),
         ("C4", "RoBERTa 3-seed avg", "SecBERT 3-seed avg", "+0.001 [-0.022, 0.025]", "NOT-FOUND in any notebook (number comes from an earlier audit note)")]
B, SEED = 10000, 20261114
rows = []
for cid, a, b, claim, origin in PAIRS:
    d = H[a] - H[b]; dm = R[a] - R[b]
    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, n, (B, n))
    bs = d[idx].mean(1); bm = dm[idx].mean(1)
    lo, hi = np.percentile(bs, [2.5, 97.5]); lom, him = np.percentile(bm, [2.5, 97.5])
    # thesis/notebook setting: 1000 resamples, default_rng(0), one integers() call per resample
    rng0 = np.random.default_rng(0)
    nb = [d[rng0.integers(0, n, n)].mean() for _ in range(1000)]
    lo0, hi0 = np.percentile(nb, [2.5, 97.5])
    bcnt = int(((H[a] == 1) & (H[b] == 0)).sum()); ccnt = int(((H[a] == 0) & (H[b] == 1)).sum())
    p = binomtest(bcnt, bcnt + ccnt, 0.5).pvalue if bcnt + ccnt else 1.0
    rows.append({"id": cid, "A": a, "B": b, "P@1_A": H[a].mean(), "P@1_B": H[b].mean(), "delta_P@1": d.mean(),
                 "ci95_lo_10k": lo, "ci95_hi_10k": hi, "p_boot_two_sided": 2 * min((bs <= 0).mean(), (bs >= 0).mean()),
                 "resamples": B, "rng": f"numpy default_rng({SEED})", "unit": "test sentence (n=725), paired", "ci_method": "percentile",
                 "ci95_lo_nb1000": lo0, "ci95_hi_nb1000": hi0, "nb_setting": "1000 resamples, default_rng(0)",
                 "delta_MRR@3": dm.mean(), "mrr_ci_lo": lom, "mrr_ci_hi": him,
                 "mcnemar_b(A right,B wrong)": bcnt, "mcnemar_c(A wrong,B right)": ccnt, "mcnemar_exact_p": p,
                 "claimed": claim, "claim_origin": origin})
df = pd.DataFrame(rows); df.to_csv(PACK / "04_bootstrap.csv", index=False)
M = ["# 04 Statistics\n", f"Paired bootstrap over the 725 test sentences, {B:,} resamples, `numpy.random.default_rng({SEED})`, percentile 95% CI. "
     "Second CI column = notebook setting (1,000 resamples, `default_rng(0)`). McNemar = exact two-sided binomial on discordant pairs.\n",
     "Note: the bootstrap resamples test sentences only; it does not include training-seed variance.\n",
     "| ID | A minus B | dP@1 | 95% CI (10k) | 95% CI (nb 1k, rng 0) | claimed | McNemar b / c | exact p | dMRR@3 [CI] |", "|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    M.append(f"| {r['id']} | {r['A']} - {r['B']} | {r['delta_P@1']:+.4f} | [{r['ci95_lo_10k']:+.3f}, {r['ci95_hi_10k']:+.3f}] | "
             f"[{r['ci95_lo_nb1000']:+.3f}, {r['ci95_hi_nb1000']:+.3f}] | {r['claimed']} | {r['mcnemar_b(A right,B wrong)']} / {r['mcnemar_c(A wrong,B right)']} | "
             f"{r['mcnemar_exact_p']:.4f} | {r['delta_MRR@3']:+.3f} [{r['mrr_ci_lo']:+.3f}, {r['mrr_ci_hi']:+.3f}] |")
M.append("\nOrigin of the claimed intervals: " + "; ".join(f"{r['id']}: {r['claim_origin']}" for r in rows))
w(PACK / "04_statistics.md", "\n".join(M)); print("\n".join(M))
