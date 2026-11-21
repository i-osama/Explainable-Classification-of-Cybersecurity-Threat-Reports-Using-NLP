"""Builds a fake thesis folder with the real shapes (3468/604/725 sentences, 733 labels, 180 seen) so load_replay runs end to end."""
import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

FX = Path(__file__).parent / "fixtures"
L, SEEN, SEEDS = 733, 180, (42, 43, 44)


def build(root, seed=0):
    rng = np.random.default_rng(seed)
    root = Path(root)
    ids = [f"t{1200 + i}" for i in range(L)]  # none of the four dropped ids (t1060, t1107, t1151, t1188)
    D = root / "Dataset"
    D.mkdir(parents=True)
    pd.DataFrame({"ttp": ids, "description": [f"citation: description of technique {i}   with   spaces" for i in ids]}).to_csv(D / "ttp-desc-mappings.csv", sep="\t", index=False)
    vocab = [f"w{i}" for i in range(400)]

    def split(n, name, seen_only):
        rows = []
        for k in range(n):
            g = k % SEEN if seen_only else int(rng.integers(0, SEEN + 3))
            g2 = [g] if rng.random() > 0.2 else sorted({g, int(rng.integers(0, SEEN))})
            words = list(rng.choice(vocab, 12)) + [f"key{g}", f"uniq{name}{k}"]
            rows.append({"text1": " ".join(words), "labels": str([ids[j] for j in g2])})
        pd.DataFrame(rows).to_csv(D / f"tram_{name}.tsv", sep="\t", index=False)

    split(3468, "train", True); split(604, "dev", False); split(725, "test", False)
    for tag in ("roberta", "secbert"):
        for s in SEEDS:
            d = root / "Exp_1_4_run_tram_2_epoc_30" / f"{tag}_pw_s{s}"
            d.mkdir(parents=True)
            np.save(d / "mlb_classes.npy", np.array([i.upper() for i in ids[:SEEN]], dtype=object), allow_pickle=True)
            np.save(d / "dev_probs.npy", rng.random((604, SEEN))); np.save(d / "test_probs.npy", rng.random((725, SEEN)))
    for s in SEEDS:
        d = root / "run_match_1" / f"ft20_s{s}"
        d.mkdir(parents=True)
        np.save(d / "dev_scores.npy", rng.random((604, L))); np.save(d / "test_scores.npy", rng.random((725, L)))
    test = pd.read_csv(D / "tram_test.tsv", sep="\t")
    (root / "Exp_3_0_shap").mkdir()
    with open(root / "Exp_3_0_shap" / "shap_v2_roberta_pw_s42.jsonl", "w") as fh:
        for r in range(10):
            n = len(test["text1"][r].split())
            fh.write(json.dumps({"row": r, "pred_label": ids[0].upper(), "shap_values": [float(x) for x in rng.normal(size=n)]}) + "\n")
    (root / "results").mkdir()
    for f in ("selective.csv", "confusions.csv", "attack_drift_ids.csv"):
        shutil.copy(FX / f, root / "results" / f)
    shutil.copy(FX / "thesis_numbers.json", root / "thesis_numbers.json")
    m = root / "results" / "colab" / "matcher_ft20_s42"  # retrained matcher (notebook 04): seed 42 only
    m.mkdir(parents=True)
    np.save(m / "dev_scores.npy", rng.random((604, L))); np.save(m / "test_scores.npy", rng.random((725, L)))
    f = root / "results" / "colab" / "fusion_shap"
    f.mkdir()
    with open(f / "fusion_shap_full_s42.jsonl", "w") as fh:
        for r in range(5):
            n = len(test["text1"][r].split())
            fh.write(json.dumps({"row": r, "fused_top1": ids[1].upper(), "fused_top1_correct": r % 2 == 0,
                                 "shap_fused": [float(x) for x in rng.normal(size=n)]}) + chr(10))
    return root
