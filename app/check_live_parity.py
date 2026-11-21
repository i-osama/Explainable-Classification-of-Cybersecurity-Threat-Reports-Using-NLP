"""Real-data check of the live full fusion: live components vs the stored score files, plus a build-time test P@1.

    python check_live_parity.py [--out DIR] [--rows 20]      (TTPMAP_ROOT = thesis folder or the portable data folder)

Writes DIR/label_emb_ft20_s42.npy (matcher label cache) and DIR/live_parity.json. Exit code 1 when a tolerance fails.
The P@1 here is a build-time check of the seed-42 live system, NOT a thesis number (the registry holds B13a and T2.*).
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

import core
import live

TOL = {"matcher_max_abs_diff": 2e-3, "roberta_z_max_abs_diff": 1e-3, "secbert_z_max_abs_diff": 1e-3}


def p1_ci(hit, n_boot=2000, seed=20261114):
    rng = np.random.default_rng(seed)
    b = [hit[rng.integers(0, len(hit), len(hit))].mean() for _ in range(n_boot)]
    return float(hit.mean()), [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).parent / "_build"))
    ap.add_argument("--rows", type=int, default=20)
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    root = os.environ.get("TTPMAP_ROOT", r"E:\Osamas Paper")
    R = core.load_replay(root)
    cached = R.art["label_cache"]  # the folder's own cache when present (portable data/models); checked below via the matcher diff
    art = {**R.art, "label_cache": cached if cached.exists() else out / "label_emb_ft20_s42.npy"}
    mdir = art["matcher_state"].parent
    t0 = time.perf_counter()
    comps = live.load(art, full=True)
    load_s = time.perf_counter() - t0
    np.save(out / "label_emb_ft20_s42.npy", comps[0].E)  # the build copies it from here
    tx = R.texts[:a.rows]
    L, lab2i = len(R.labels), {l: i for i, l in enumerate(R.labels)}
    res = {"rows": a.rows, "load_s": round(load_s, 1)}
    res["matcher_max_abs_diff"] = float(np.abs(comps[0].raw(tx) - np.load(mdir / "test_scores.npy")[:a.rows]).max())
    for c, tag in zip(comps[2:], ("roberta", "secbert")):
        d = art["cls_root"] / f"{tag}_pw_s42"
        cols = np.array([lab2i[str(x).upper()] for x in np.load(d / "mlb_classes.npy", allow_pickle=True)])
        stored = core.zrow(core.to_full(np.load(d / "test_probs.npy")[:a.rows], cols, L))
        res[f"{tag}_z_max_abs_diff"] = float(np.abs(c.z(tx) - stored).max())

    # build-time test P@1 of the live system from the stored score files (seed 42, retrained matcher), sentence bootstrap
    Z = {"matcher": core.zrow(np.load(mdir / "test_scores.npy")), "svm": comps[1].z(R.texts)}
    for tag in ("roberta", "secbert"):
        d = art["cls_root"] / f"{tag}_pw_s42"
        cols = np.array([lab2i[str(x).upper()] for x in np.load(d / "mlb_classes.npy", allow_pickle=True)])
        Z[tag] = core.zrow(core.to_full(np.load(d / "test_probs.npy"), cols, L))
    S = core.fuse(Z)
    hit = np.array([R.labels[int(S[i].argmax())] in R.gold[i] for i in range(len(R.texts))], float)
    res["full_s42_test_p1"], res["full_s42_test_p1_ci"] = p1_ci(hit)
    res["note"] = "build-time check, seed 42, retrained matcher, stored scores; not a thesis number"

    # the live system must pick the same top-1 as notebook 06 (same system) on the stored fusion-SHAP rows
    rows = sorted(R.fshap)[:5]
    live_top = [R.labels[int(np.tensordot(live.FULL_W, np.stack([c.z([R.texts[r]])[0] for c in comps]), 1).argmax())] for r in rows]
    res["nb06_top1_agree"] = f"{sum(t == R.fshap[r]['label'] for t, r in zip(live_top, rows))}/{len(rows)}"

    ex = "The malware uses tasklist to enumerate running processes and sends the list to its C2 server."
    t0 = time.perf_counter()
    o = live.analyse(comps, ex, n_perm=10, weights=live.FULL_W)
    res["seconds_per_sentence_full_nperm10"] = round(time.perf_counter() - t0, 1)
    res["example_words"] = len(o["units"])  # the app scales this timing to estimate other sentences
    res["example_top1"] = R.name(R.labels[o["k"]])
    res["example_additivity_error"] = o["additivity_error"]

    fails = [k for k, t in TOL.items() if not res[k] <= t]
    if rows and res["nb06_top1_agree"] != f"{len(rows)}/{len(rows)}":
        fails.append("nb06_top1_agree")
    res["status"] = "PASS" if not fails else "FAIL: " + ", ".join(fails)
    (out / "live_parity.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps(res, indent=1))
    print(f"{res['status']}: matcher diff {res['matcher_max_abs_diff']:.1e}, nb06 top-1 {res['nb06_top1_agree']}, "
          f"{res['seconds_per_sentence_full_nperm10']} s per sentence")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
