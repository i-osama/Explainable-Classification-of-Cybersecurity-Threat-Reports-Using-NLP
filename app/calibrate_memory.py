"""Build-time threshold t for the example memory of "Train and check". Not a thesis number.

Simulates what a visitor does: for every technique with at least 4 thesis training sentences, a memory of 4 of them
(seed 42) is asked about every thesis dev sentence (never test). A (technique, dev sentence) pair "fires" when the cosine
of the matcher's sentence embeddings with the closest of the 4 is >= t; it is right when the technique is a gold label.
t = the smallest similarity in 0.50..0.99 at which at least 90% of the fired pairs are right (at least 20 pairs).

    python calibrate_memory.py [--out DIR]          (TTPMAP_ROOT = thesis folder or the portable data folder)
"""
import argparse
import json
import os
import time
from pathlib import Path

import numpy as np


def choose_t(sims, hits, target=0.90, min_matches=20) -> dict:
    sims, hits = np.asarray(sims, float), np.asarray(hits, bool)
    for t in np.round(np.arange(0.50, 0.995, 0.01), 2):
        m = sims >= t
        if m.sum() >= min_matches and hits[m].mean() >= target:
            return {"t": float(t), "precision": float(hits[m].mean()), "matches": int(m.sum())}
    return {"t": None, "precision": None, "matches": 0}


def small_bank_pairs(E_tr, Y_tr, E_dv, Y_dv, k=4, seed=42):
    """(similarity, right) for every (technique with >= k training sentences, dev sentence) pair, memory = k of its sentences."""
    rng = np.random.default_rng(seed)
    sims, hits = [], []
    for lab in np.where(Y_tr.sum(0) >= k)[0]:
        bank = E_tr[rng.choice(np.where(Y_tr[:, lab])[0], k, replace=False)]
        sims.append((E_dv @ bank.T).max(1))
        hits.append(Y_dv[:, lab])
    return np.concatenate(sims), np.concatenate(hits).astype(bool)


def main():
    import core
    import live
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).parent / "_build"))
    out = Path(ap.parse_args().out)
    out.mkdir(parents=True, exist_ok=True)
    R = core.load_replay(os.environ.get("TTPMAP_ROOT", r"E:\Osamas Paper"))
    t0 = time.perf_counter()
    cache = out / "memory_emb_cache.npz"  # embeddings of train/dev sentences, reused when the texts are the same
    tr, dv = R.art["train"]["texts"], R.art["dev"]["texts"]
    try:
        z = np.load(cache)
        assert z["n_tr"] == len(tr) and z["n_dv"] == len(dv)
        E_tr, E_dv = z["E_tr"], z["E_dv"]
    except (OSError, KeyError, AssertionError):
        m = live.MatcherComp(R.art)
        E_tr, E_dv = m._emb(tr, live.MAX_LEN), m._emb(dv, live.MAX_LEN)
        np.savez(cache, E_tr=E_tr, E_dv=E_dv, n_tr=len(tr), n_dv=len(dv))
    sims, hits = small_bank_pairs(E_tr, R.art["train"]["Y"], E_dv, R.art["dev"]["Y"])
    res = choose_t(sims, hits)
    res.update(pairs=int(len(sims)), dev_n=len(dv), bank_size=4, seconds=round(time.perf_counter() - t0, 1),
               note="build-time calibration on thesis train->dev (not test), memory of 4 examples per technique; not a thesis number")
    (out / "memory_calib.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps(res, indent=1))
    return 0 if res["t"] is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
