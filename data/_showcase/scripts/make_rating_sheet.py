"""Human study v2 materials (protocol: docs/HUMAN_STUDY_PROTOCOL.md). Generates, per rater, a blinded and
individually randomised rating sheet, plus a private key. NO results are produced here.

    python scripts/make_rating_sheet.py --raters 3          # writes human_study/sheets/, human_study/key_PRIVATE.csv
    python scripts/make_rating_sheet.py --power             # power simulation only -> results/human_power_simulation.csv

Items: 60 REAL (sentence + its 3 highest positive SHAP words) and 20 CONTROL (sentence + 3 words drawn at random from the
words that are NOT among its 5 highest SHAP words). Sentences are the eligible rows at positions 100.. of
numpy RandomState(42).permutation(725), i.e. sentences NOT used in the first study. Eligible = at least 8 words,
at least 3 positive SHAP words, not truncated at 128 tokens.
The sheets contain dataset sentences: they are for the raters only and are excluded from git and from the zip."""
import argparse, csv, json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap import SHOWCASE, SHAP_DIR, RESULTS, DATA

N_REAL, N_CONTROL, SEED = 60, 20, 20261116
ap = argparse.ArgumentParser(); ap.add_argument("--raters", type=int, default=3); ap.add_argument("--power", action="store_true"); A = ap.parse_args()


def power():
    """Simulation under STATED ASSUMPTIONS (not data): item quality on a 1-5 scale, real items ~ N(mu_real, 0.9), control ~ N(mu_ctrl, 0.9);
    rater rating = round(clip(quality + rater bias + N(0, noise))); biases ~ N(0, 0.4). 300 repetitions per cell."""
    import krippendorff
    rng = np.random.default_rng(SEED); rows = []
    for n_r in (3, 4, 5):
        for noise in (0.6, 1.0, 1.4):
            for gap, (mr, mc) in (("large (3.8 vs 2.2)", (3.8, 2.2)), ("small (3.4 vs 2.8)", (3.4, 2.8)), ("none (3.2 vs 3.2)", (3.2, 3.2))):
                al, lo_ok, det = [], [], []
                for _ in range(300):
                    q = np.concatenate([rng.normal(mr, 0.9, N_REAL), rng.normal(mc, 0.9, N_CONTROL)]); bias = rng.normal(0, 0.4, n_r)
                    X = np.clip(np.rint(q[None, :] + bias[:, None] + rng.normal(0, noise, (n_r, len(q)))), 1, 5)
                    a = krippendorff.alpha(X, level_of_measurement="ordinal"); al.append(a)
                    it = X.mean(0); d = it[:N_REAL].mean() - it[N_REAL:].mean()
                    se = np.sqrt(it[:N_REAL].var(ddof=1) / N_REAL + it[N_REAL:].var(ddof=1) / N_CONTROL)
                    det.append(d - 1.96 * se > 0 and d >= 1.0); lo_ok.append(a >= 0.667)
                rows.append({"raters": n_r, "rater_noise_sd": noise, "true_gap_real_vs_control": gap, "mean_alpha_ordinal": np.mean(al), "alpha_p05": np.quantile(al, 0.05), "alpha_p95": np.quantile(al, 0.95),
                             "share_alpha_ge_0.667": np.mean(lo_ok), "share_real_above_control_rule_met": np.mean(det), "n_real": N_REAL, "n_control": N_CONTROL, "repetitions": 300})
    pd.DataFrame(rows).to_csv(RESULTS / "human_power_simulation.csv", index=False)
    print("power simulation:", len(rows), "cells -> results/human_power_simulation.csv")


if A.power:
    power(); sys.exit(0)

recs = {}
for l in open(SHAP_DIR / "shap_v2_roberta_pw_s42.jsonl", encoding="utf-8"):
    if l.strip():
        r = json.loads(l); recs[r["row"]] = r
order = [int(r) for r in np.random.RandomState(42).permutation(725)]
elig = [r for r in order[100:] if len(recs[r]["units"]) >= 8 and (np.array(recs[r]["shap_values"]) > 0).sum() >= 3 and not recs[r]["truncated"]]
assert len(elig) >= N_REAL + N_CONTROL
rows_real, rows_ctrl = elig[:N_REAL], elig[N_REAL:N_REAL + N_CONTROL]
tech = pd.read_parquet(RESULTS / "tables" / "techniques.parquet").set_index("id")["name"].to_dict()
desc = pd.read_csv(DATA / "ttp-desc-mappings.csv", sep="\t"); desc["ttp"] = desc["ttp"].str.upper().str.strip()
import re
def first_sentence(t):
    t = re.sub(r"\(Citation:[^)]*\)", "", str(t)); t = re.sub(r"\s+", " ", t).strip(); m = re.search(r"(?<=[.!?])\s+(?=[A-Z])", t); s = t[:m.start()] if m else t
    return s if len(s) <= 300 else s[:300].rstrip() + "..."
dmap = dict(zip(desc["ttp"], desc["description"].map(first_sentence)))
rng = np.random.RandomState(SEED); items = []
for cond, rows in (("real", rows_real), ("control", rows_ctrl)):
    for row in rows:
        r = recs[row]; v = np.array(r["shap_values"]); top5 = set(np.argsort(-v, kind="stable")[:5].tolist())
        idx = np.argsort(-v, kind="stable")[:3].tolist() if cond == "real" else rng.choice([i for i in range(len(v)) if i not in top5], 3, replace=False).tolist()
        marked = "".join(u.replace(u.strip(), f"[[{u.strip()}]]", 1) if i in idx else u for i, u in enumerate(r["units"]))
        items.append({"item_id": f"I{rng.randint(10**6, 10**7)}", "test_row": row, "condition": cond, "predicted_technique": r["pred_label"], "technique_name": tech.get(r["pred_label"], "not found"),
                      "technique_description": dmap.get(r["pred_label"], "not found"), "sentence_with_marked_words": marked, "top1_correct": r["top1_correct"]})
assert len({i["item_id"] for i in items}) == len(items)
H = SHOWCASE / "human_study"; (H / "sheets").mkdir(parents=True, exist_ok=True); (H / "returned").mkdir(exist_ok=True)
pd.DataFrame(items)[["item_id", "test_row", "condition", "top1_correct"]].to_csv(H / "key_PRIVATE.csv", index=False)
for k in range(1, A.raters + 1):
    perm = np.random.RandomState(SEED + k).permutation(len(items))
    with open(H / "sheets" / f"rating_sheet_R{k}.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(["no", "item_id", "predicted_technique", "technique_name", "technique_description", "sentence_with_marked_words", "rating_1_to_5", "note"])
        for n, j in enumerate(perm, 1):
            it = items[j]; w.writerow([n, it["item_id"], it["predicted_technique"], it["technique_name"], it["technique_description"], it["sentence_with_marked_words"], "", ""])
with open(H / "returned" / "raters_TEMPLATE.csv", "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows([["rater_code", "role", "years_in_security", "threat_intel_experience_yes_no", "attack_framework_familiarity_1_to_5", "minutes_spent"]] + [[f"R{k}", "", "", "", "", ""] for k in range(1, A.raters + 1)])
print(f"items: {N_REAL} real + {N_CONTROL} control; sheets for {A.raters} raters in human_study/sheets/ (NOT committed); key in human_study/key_PRIVATE.csv")
power()
