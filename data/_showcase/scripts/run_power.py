"""Q1 plan Task 6: minimum detectable effect (MDE) of each comparison in results/comparisons.csv.
Design-based sensitivity analysis, not post-hoc power of the observed effect: n = 725 paired sentences, the observed discordant share
d = (b + c) / n, exact two-sided McNemar at the Holm alpha of the comparison's observed rank in its family of 8.
For delta in 0.001 steps: b ~ (d + delta) / 2, c ~ (d - delta) / 2, 10,000 multinomial draws (default_rng(20261114)); MDE = smallest delta with power >= 0.8.
Writes results/power_mde.csv. Run: python scripts/run_power.py"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import binom

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap import RESULTS

N_SIM, POWER, SEED, ALPHA = 10_000, 0.8, 20261114, 0.05
cm = pd.read_csv(RESULTS / "comparisons.csv"); n = 725; m = len(cm)
order = np.argsort(cm["p_mcnemar"].to_numpy(), kind="stable"); rank = np.empty(m, int); rank[order] = np.arange(1, m + 1)
rng = np.random.default_rng(SEED); rows = []
for (_, r), k in zip(cm.iterrows(), rank):
    d = (r.mcnemar_b + r.mcnemar_c) / n; a = ALPHA / (m - k + 1); mde = np.nan
    for delta in np.arange(0.001, d + 1e-12, 0.001):
        draws = rng.multinomial(n, [(d + delta) / 2, (d - delta) / 2, 1 - d], size=N_SIM); b, c = draws[:, 0], draws[:, 1]
        p = np.minimum(1.0, 2 * binom.cdf(np.minimum(b, c), b + c, 0.5)); p[b + c == 0] = 1.0
        if (p < a).mean() >= POWER:
            mde = round(float(delta), 3); break
    rows.append({"id": r.id, "A": r.A, "B": r.B, "observed_delta": r["delta_P@1"], "discordant_share": d, "holm_rank": int(k), "alpha": a, "mde": mde,
                 "observed_below_mde": bool(abs(r["delta_P@1"]) < mde) if mde == mde else True})
pd.DataFrame(rows).to_csv(RESULTS / "power_mde.csv", index=False)
print(pd.DataFrame(rows).round(4).to_string(index=False))
