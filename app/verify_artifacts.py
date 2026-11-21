"""Check that this app reproduces the thesis numbers from the saved files. Run once on the thesis machine:

    set TTPMAP_ROOT=E:\\Osamas Paper
    python verify_artifacts.py

Every DIFF line means the loader does not match the notebooks: do not trust the app until it is explained.
Reference values come from results/*.csv (written by the thesis scripts), never typed here.
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import core


def checks(R, res):
    lab = {l: i for i, l in enumerate(R.labels)}
    G = [[lab[g] for g in gs] for gs in R.gold]
    S, top, out = R.S, R.S.argmax(1), []

    def add(name, mine, ref, tol):
        out.append((name, float(mine), float(ref), abs(float(mine) - float(ref)) <= tol))

    sel = pd.read_csv(res / "selective.csv")
    sel = sel[sel["system"].str.startswith("Fusion")].iloc[0]
    add("P@1 fusion (3,1,1,1), seed-averaged", np.mean([t in g for t, g in zip(top, G)]), sel["P@1_all"], 1e-9)
    cf = pd.read_csv(res / "conformal.csv")
    for _, r in cf[cf["system"].str.startswith("Fusion") & (cf["rule"] == "score")].iterrows():
        a = round(float(r["alpha"]), 2)
        sets = S >= R.cal.tau[a]
        add(f"conformal tau, alpha {a}", R.cal.tau[a], r["param"], 1e-3)
        add(f"conformal coverage_all, alpha {a}", np.mean([sets[i, g].all() for i, g in enumerate(G)]), r["coverage_all"], 1e-3)
        add(f"conformal mean set size, alpha {a}", sets.sum(1).mean(), r["size_mean"], 1e-2)
    m = core.margin(S)
    for c in core.COVS:
        ans = np.where(m >= R.cal.thr[c])[0]
        add(f"triage coverage at target {c}", len(ans) / len(S), sel[f"cov{c}_test"], 2e-3)
        add(f"triage selective P@1 at target {c}", np.mean([top[i] in G[i] for i in ans]), sel[f"selP@1_{c}"], 2e-3)
    ev = pd.read_csv(res / "explained_vs_fusion.csv").iloc[0]
    add("stored SHAP records", len(R.shap), ev["n"], 0)
    add("SHAP label differs from fusion top-1 (E4)", sum(R.labels[top[i]] != r["label"] for i, r in R.shap.items()), ev["different_top1"], 0)
    add("SHAP value count != word count (must be 0)", sum(len(r["values"]) != len(core.split_units(R.texts[i])) for i, r in R.shap.items()), 0, 0)
    return out


def main(root, res):
    R = core.load_replay(root)
    rows = checks(R, Path(res))
    for name, mine, ref, ok in rows:
        print(f"{'PASS' if ok else 'DIFF'}  {name:48s} app {mine:10.4f}  thesis {ref:10.4f}")
    bad = [r for r in rows if not r[3]]
    print(f"\n{len(rows) - len(bad)}/{len(rows)} match" + ("" if not bad else "  -> DO NOT TRUST THE APP YET"))
    return 1 if bad else 0


if __name__ == "__main__":
    root = os.environ.get("TTPMAP_ROOT", r"E:\Osamas Paper")
    res = os.environ.get("TTPMAP_RESULTS") or next((str(Path(root) / p) for p in ("results", "_showcase/results") if (Path(root) / p).exists()), None)
    if not res:
        sys.exit("results/ folder not found: set TTPMAP_RESULTS")
    sys.exit(main(root, res))
