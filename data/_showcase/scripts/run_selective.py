"""Q1 wave 2 Task 4 / prereg 19: selective prediction (abstention) for analyst triage. Thresholds on DEV, TEST once.
Writes results/selective.csv, selective_family.csv, risk_coverage.csv and (POST-HOC, D27) selective_posthoc_raw.csv.
Run: python scripts/run_selective.py"""
import sys
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap import RESULTS, SEEDS
from ttpmap.data import build_space
from ttpmap.fusion import components, fuse, to_full
from ttpmap.metrics import hit_at_1
from ttpmap.stats import bootstrap_ci, holm, BOOT_N, BOOT_SEED
from ttpmap import selective as sel

S = build_space(); Yd, Y = S.Y["dev"], S.Y["test"]; n = len(Y)
Zd, Z = components(S, "dev", "avg"), components(S, "test", "avg")
NAMES = {"fusion": "Fusion (3,1,1,1)", "matcher": "Matcher (3-seed ens.)", "svm": "TF-IDF + SVM", "roberta": "RoBERTa (3-seed avg)", "secbert": "SecBERT (3-seed avg)"}
DEV = {"fusion": fuse(Zd, (3, 1, 1, 1)), **{k: Zd[k] for k in ("matcher", "svm", "roberta", "secbert")}}
TEST = {"fusion": fuse(Z, (3, 1, 1, 1)), **{k: Z[k] for k in ("matcher", "svm", "roberta", "secbert")}}


def evaluate(dev, test, names, tag):
    rows, curves, C, H = [], [], {}, {}
    for k, name in names.items():
        cd, ct = sel.margin(dev[k]), sel.margin(test[k]); h = hit_at_1(test[k], Y).astype(bool); C[k], H[k] = ct, h
        row = {"analysis": tag, "system": name, "P@1_all": float(h.mean()), "AURC": sel.aurc(ct, h), "E-AURC": sel.eaurc(ct, h), "n": n}
        for tgt in (0.5, 0.8, 0.9):
            t = sel.dev_threshold_for_coverage(cd, tgt, split="dev"); acc = ct >= t; ci = bootstrap_ci(h[acc].astype(float))
            row.update({f"cov{tgt}_test": float(acc.mean()), f"selP@1_{tgt}": ci["mean"], f"selP@1_{tgt}_lo": ci["lo"], f"selP@1_{tgt}_hi": ci["hi"]})
        rows.append(row)
        cov, risk = sel.risk_coverage(ct, h)
        curves += [{"analysis": tag, "system": name, "coverage": float(c), "risk": float(r)} for c, r in zip(cov[4::5], risk[4::5])]
    return rows, curves, C, H


rows, curves, C, H = evaluate(DEV, TEST, NAMES, "PREREG-19")
rng = np.random.default_rng(BOOT_SEED); idx = rng.integers(0, n, (BOOT_N, n))
fam = []
for k in ("matcher", "svm", "roberta", "secbert"):
    d0 = sel.aurc(C["fusion"], H["fusion"]) - sel.aurc(C[k], H[k])
    bs = np.array([sel.aurc(C["fusion"][i], H["fusion"][i]) - sel.aurc(C[k][i], H[k][i]) for i in idx])
    fam.append({"A": NAMES["fusion"], "B": NAMES[k], "delta_AURC": float(d0), "ci_lo": float(np.quantile(bs, 0.025)), "ci_hi": float(np.quantile(bs, 0.975)),
                "p_boot": float(min(1.0, 2 * min((bs <= 0).mean(), (bs >= 0).mean())))})
for x, p in zip(fam, holm([x["p_boot"] for x in fam])):
    x["p_holm"] = p; x["family_size"] = len(fam); x["supported"] = bool(p < 0.05 and x["ci_hi"] < 0)


def raw(tag, split):
    if tag == "svm":
        return to_full(S.svm_raw[split], S.seen_idx, S.L)
    return np.mean([to_full(S.cls_raw[tag, s][split], S.cls_cols[tag, s], S.L) for s in SEEDS], axis=0)


RAWN = {"svm": "TF-IDF + SVM (raw decision score)", "roberta": "RoBERTa (3-seed mean probability)", "secbert": "SecBERT (3-seed mean probability)"}
prow, pcur, _, _ = evaluate({k: raw(k, "dev") for k in RAWN}, {k: raw(k, "test") for k in RAWN}, RAWN, "POST-HOC")

pd.DataFrame(rows).to_csv(RESULTS / "selective.csv", index=False); pd.DataFrame(fam).to_csv(RESULTS / "selective_family.csv", index=False)
pd.DataFrame(curves + pcur).to_csv(RESULTS / "risk_coverage.csv", index=False); pd.DataFrame(prow).to_csv(RESULTS / "selective_posthoc_raw.csv", index=False)
print(pd.DataFrame(rows + prow).round(4).to_csv(index=False)); print(pd.DataFrame(fam).round(4).to_csv(index=False))
