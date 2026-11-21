"""Q1 plan Task 1: every matcher variant in run_match_1/ scored with the same metric code, alone and inside the (3,1,1,1) fusion.
Variants: zero-shot; ft (8-epoch budget, seed 42 only); ft20 (20-epoch budget, seeds 42-44); ft20L256 (descriptions up to 256 tokens, seeds 42-44).
Reads saved score files only. Writes results/matcher_variants.csv. Run: python scripts/run_matcher_variants.py"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap import RESULTS, MATCH_DIR, SEEDS
from ttpmap.data import build_space
from ttpmap.metrics import hit_at_1, rr_at_k, recall_at_k_micro, rank_topk
from ttpmap.fusion import components, fuse, zrow
from ttpmap.stats import bootstrap_ci

S = build_space(); Y = S.Y["test"]; n = len(Y); un = Y & ~S.seen[None, :]
Z = components(S, "test", "avg")


def unseen_r5(Sc):
    it = np.zeros(Y.shape, bool); it[np.arange(n)[:, None], rank_topk(Sc, 5)] = True
    return float((it & un).sum() / un.sum())


def row(variant, seed, system, Sc, meta):
    h, rr = hit_at_1(Sc, Y), rr_at_k(Sc, Y)
    c = bootstrap_ci(h)
    return {"variant": variant, "seed": seed, "system": system, "P@1": c["mean"], "P@1_lo": c["lo"], "P@1_hi": c["hi"], "MRR@3": float(rr.mean()),
            "R@5_micro": recall_at_k_micro(Sc, Y, 5), "unseen_R@5": unseen_r5(Sc), **meta}


def meta_of(d):
    if d == "zeroshot":
        return {"epochs": 0, "patience": np.nan, "best_epoch": np.nan, "n_neg": np.nan, "label_max_len": np.nan}
    m = json.load(open(MATCH_DIR / d / "metrics.json")); c = m["config"]
    return {"epochs": c["epochs"], "patience": c["patience"], "best_epoch": m["best_epoch"], "n_neg": c["n_neg"], "label_max_len": c["label_max_len_train"]}


rows = []
for variant, dirs in (("zeroshot", ["zeroshot"]), ("ft8", ["ft_s42"]), ("ft20", [f"ft20_s{s}" for s in SEEDS]), ("ft20L256", [f"ft20L256_s{s}" for s in SEEDS])):
    mats = []
    for d in dirs:
        sc = np.load(MATCH_DIR / d / "test_scores.npy"); assert sc.shape == Y.shape, (d, sc.shape)
        mats.append(sc); seed = d.split("_s")[-1] if "_s" in d else "-"
        rows.append(row(variant, seed, "matcher", sc, meta_of(d)))
    if len(mats) > 1:
        ens = np.mean(mats, axis=0); mt = meta_of(dirs[0]); mt["best_epoch"] = " / ".join(str(meta_of(d)["best_epoch"]) for d in dirs)
        rows.append(row(variant, "ens", "matcher", ens, mt))
        Zv = dict(Z); Zv["matcher"] = zrow(ens)
        rows.append(row(variant, "ens", "fusion (3,1,1,1)", fuse(Zv, (3, 1, 1, 1)), mt))
df = pd.DataFrame(rows); df.to_csv(RESULTS / "matcher_variants.csv", index=False)
chk = df[(df.variant == "ft20") & (df.seed == "ens") & (df.system == "fusion (3,1,1,1)")]["P@1"].iloc[0]
assert abs(chk - 0.8027586206896552) < 1e-9, chk          # must reproduce B13a exactly
print(df[["variant", "seed", "system", "P@1", "MRR@3", "R@5_micro", "unseen_R@5", "best_epoch"]].round(4).to_string(index=False))
