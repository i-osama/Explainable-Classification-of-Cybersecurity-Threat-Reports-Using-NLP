"""T6: explainability evidence -> 06_shap.md, fig_shap_ex1..3.png, 06_deletion_test_725.csv
Reuses Exp_3_0_shap/shap_v2_roberta_pw_s42.jsonl (read-only). Re-runs the deletion test on CPU with the saved
checkpoint (inference only) for (a) the original 100 sampled rows and (b) all 725 rows."""
import json, re, sys, time
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common import PACK, SHAPD, CLS, w

SKIP_MODEL = "--no-model" in sys.argv
recs = [json.loads(l) for l in open(SHAPD / "shap_v2_roberta_pw_s42.jsonl", encoding="utf-8") if l.strip()]
by = {r["row"]: r for r in recs}
order = [int(r) for r in np.random.RandomState(42).permutation(725)]
M = ["# 06 Explainability evidence\n"]
M += ["## Stored SHAP output  [VERIFIED from file]\n",
      f"- file `Exp_3_0_shap/shap_v2_roberta_pw_s42.jsonl`: {len(recs)} records, {len(by)} distinct test rows, all with identical method block: `{recs[0]['method']}`",
      f"- all records share one method: {all(r['method'] == recs[0]['method'] for r in recs)}; rows cover all 725 test ids: {sorted(by) == list(range(725))}",
      f"- stored order equals `RandomState(42).permutation(725)`: {[r['row'] for r in recs] == order}",
      f"- top-1 correct: {sum(r['top1_correct'] for r in recs)} of {len(recs)}; truncated (>128 tokens): {sum(r['truncated'] for r in recs)}; "
      f"max additivity error |sum(shap)+base-logit|: {max(r['additivity_error'] for r in recs):.1e}",
      f"- words per sentence: mean {np.mean([len(r['units']) for r in recs]):.1f}, median {int(np.median([len(r['units']) for r in recs]))}, max {max(len(r['units']) for r in recs)}",
      "- older files (not used in the thesis numbers): `shap_roberta_pw_s42.jsonl` (20 rows, token-level, no method block), `shap_v1_roberta_pw_s42.jsonl` (100 rows, n_perm=10).\n",
      "## Method  [VERIFIED: Exp_3_0b CELL 2, Exp_3_1_deletion_test CELL 0/2/3]\n",
      "- explained model: `Exp_1_4_run_tram_2_epoc_30/roberta_pw_s42` (RoBERTa-base, pos_weight, seed 42). It was the designated SHAP model before any test result existed "
      "(Exp_1_4 CELL 10 comment: 'RoBERTa + class weights first (this is the model SHAP needs)'), i.e. not picked by test score.",
      "- explainer: `shap.Explainer(f, shap.maskers.Independent(zeros(1,n)), algorithm='permutation', seed=42)`, shap 0.54.1; features = whitespace-delimited words; "
      "a hidden word is replaced by `<mask>` (whitespace kept); `max_evals = 40*(2n+1)` = 40 permutations; output explained = raw logit of the model's top-1 label.",
      "- sample: ALL 725 test sentences (the first 100 of the fixed permutation were computed first and are the ones used for the deletion test and the human sheet).",
      "- deletion test: for each sentence hide the K=3 words with the highest positive SHAP value and measure drop = logit(original) - logit(edited) of the top-1 label; "
      "compare with the mean drop over 20 random 3-word subsets (RandomState(42+row)). Two variants: *mask* (`<mask>` token) and *remove* (word deleted). "
      "Sentences need >= 6 words and >= 3 positive SHAP words; truncated sentences reported separately. CI: 1,000 bootstrap resamples of sentences, RandomState(42), percentile.",
      "- **10.19** = mean over 93 sentences of (drop top-3) - (mean drop random-3), *mask* variant, in logit units. **93/93** = number of those sentences where the top-3 drop exceeds the mean random drop. "
      "93 = 100 sampled - 3 skipped (short / <3 positive words) - 4 truncated.\n"]

# ---------- recompute from the saved CSV ----------
d = pd.read_csv(SHAPD / "deletion_test_v2_roberta_pw_s42.csv")
u = d[d.used & ~d.truncated]
def summ(u, tag):
    out = []
    rng = np.random.RandomState(42)
    for name in ("mask", "remove"):
        diff = (u[f"drop_top_{name}"] - u[f"drop_random_{name}"]).to_numpy()
        boots = [diff[rng.randint(0, len(diff), len(diff))].mean() for _ in range(1000)]
        lo, hi = np.percentile(boots, [2.5, 97.5])
        out.append(f"| {tag} | {name} | {len(u)} | {u[f'drop_top_{name}'].mean():.3f} | {u[f'drop_random_{name}'].mean():.3f} | {diff.mean():.3f} | [{lo:.3f}, {hi:.3f}] | {int((diff > 0).sum())} / {len(diff)} |")
    return out
M += ["## Deletion test numbers\n", "| source | variant | n | mean drop top-3 | mean drop random-3 | difference | 95% CI | top-3 larger |", "|---|---|---|---|---|---|---|---|"]
M += summ(u, "saved CSV (100 sampled rows) [RECOMPUTED from file]")
M_note = [f"\nSaved CSV: {len(d)} rows, used {int(d.used.sum())}, skipped {int((~d.used).sum())}, used-and-truncated {int((d.used & d.truncated).sum())}."]

# ---------- full re-run with the checkpoint ----------
if not SKIP_MODEL:
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    MD = CLS / "roberta_pw_s42"
    classes = np.load(MD / "mlb_classes.npy", allow_pickle=True)
    tok = AutoTokenizer.from_pretrained(str(MD)); model = AutoModelForSequenceClassification.from_pretrained(str(MD)).float().eval()
    def logits_fn(texts):
        out = []
        with torch.no_grad():
            for s in range(0, len(texts), 32):
                enc = tok([str(t) for t in texts[s:s + 32]], truncation=True, max_length=128, padding=True, return_tensors="pt")
                out.append(model(**enc).logits.numpy())
        return np.concatenate(out)
    UNIT_RE = re.compile(r"(\s*)(\S+)(\s*)")
    def masked(parts, hide): return "".join(l + (tok.mask_token if i in hide else c) + t for i, (l, c, t) in enumerate(parts))
    def removed(parts, hide, original):
        s = "".join(l + c + t for i, (l, c, t) in enumerate(parts) if i not in hide)
        return s.rstrip() if (len(parts) - 1) in hide and not original[-1:].isspace() else s
    rows, t0, maxdiff, mism = [], time.time(), 0.0, 0
    for j, rec in enumerate(recs):
        parts = [UNIT_RE.fullmatch(x).groups() for x in rec["units"]]; text = "".join(rec["units"]); vals = np.array(rec["shap_values"])
        k = int(np.where(classes == rec["pred_label"])[0][0])
        row = {"row": rec["row"], "in_first_100": j < 100, "pred_label": rec["pred_label"], "top1_correct": rec["top1_correct"], "n_words": len(parts), "truncated": rec["truncated"]}
        if len(parts) < 6 or (vals > 0).sum() < 3:
            base = logits_fn([text])[0]; mism += int(base.argmax() != k); maxdiff = max(maxdiff, abs(float(base[k]) - rec["pred_logit"]))
            rows.append({**row, "used": False}); continue
        top = set(np.argsort(-vals, kind="stable")[:3].tolist())
        rng = np.random.RandomState(42 + rec["row"])
        draws = [set(rng.choice(len(parts), 3, replace=False).tolist()) for _ in range(20)]
        edits = [text, masked(parts, top)] + [masked(parts, x) for x in draws] + [removed(parts, top, text)] + [removed(parts, x, text) for x in draws]
        lg = logits_fn(edits); base = lg[0]; mism += int(base.argmax() != k); maxdiff = max(maxdiff, abs(float(base[k]) - rec["pred_logit"]))
        drop = float(base[k]) - lg[1:, k]
        rows.append({**row, "used": True, "drop_top_mask": drop[0], "drop_random_mask": drop[1:21].mean(), "drop_top_remove": drop[21], "drop_random_remove": drop[22:].mean()})
        if j % 100 == 0: print(f"deletion {j}/725 {time.time() - t0:.0f}s", flush=True)
    full = pd.DataFrame(rows); full.to_csv(PACK / "06_deletion_test_725.csv", index=False)
    f100 = full[full.in_first_100 & full.used & ~full.truncated.astype(bool)]
    fall = full[full.used.astype(bool) & ~full.truncated.astype(bool)]
    M += summ(f100, "CPU re-run, same 100 rows [RECOMPUTED with checkpoint]")
    M += summ(fall, "CPU re-run, ALL 725 rows [RECOMPUTED, new]")
    M += summ(fall[fall.top1_correct.astype(bool)], "  ALL rows, top-1 correct only")
    M += summ(fall[~fall.top1_correct.astype(bool)], "  ALL rows, top-1 wrong only")
    m100 = d.merge(full, on="row", suffixes=("_saved", "_cpu"))
    mu = m100[m100.used_saved & m100.used_cpu]
    M_note += [f"CPU re-run vs stored: max |stored logit - recomputed logit| over 725 rows = {maxdiff:.2e}; top-1 label differs in {mism} rows; "
               f"max |drop_top_mask saved - CPU| on the 100 rows = {np.abs(mu.drop_top_mask_saved - mu.drop_top_mask_cpu).max():.2e}.",
               f"All-725 run: used {int(full.used.sum())}, skipped {int((~full.used.astype(bool)).sum())}, used-and-truncated {int((full.used.astype(bool) & full.truncated.astype(bool)).sum())} (excluded from the table)."]
M += M_note
M += ["\nClaims: E1 SHAP permutation / 40 permutations / roberta_pw_s42 -> VERIFIED. E2 10.19 -> RECOMPUTED 10.189 (mask). E3 93/93 -> RECOMPUTED.\n",
      "Caveats to state in the thesis: (1) the *mask* variant uses the same perturbation as SHAP, so it tests internal consistency; the *remove* variant is the more independent check. "
      "(2) The explained model is ONE seed of ONE component (RoBERTa); it is not the fusion system that gives the headline P@1. "
      "(3) The number is on the top-1 logit, so it says nothing about whether the prediction is right.\n"]

# ---------- three example figures ----------
RULE = ("Rule (written before looking at any attribution): among the 725 test sentences, take the LOWEST test sentence id that is "
        "(ex1) single-label gold and top-1 correct; (ex2) multi-label gold (>=2 distinct labels) and top-1 correct; (ex3) top-1 wrong. Model: roberta_pw_s42.")
def pick(cond): return min(r["row"] for r in recs if cond(r))
ids = [pick(lambda r: len(set(r["gold_labels"])) == 1 and r["top1_correct"]),
       pick(lambda r: len(set(r["gold_labels"])) >= 2 and r["top1_correct"]),
       pick(lambda r: not r["top1_correct"])]
names = json.load(open(SHAPD / "attack_technique_names.json"))["techniques"]
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"], "font.size": 10, "savefig.facecolor": "white"})
M += ["## Example figures\n", RULE + " Long sentences: the 20 words with the largest |SHAP| are drawn, in sentence order (all words if <= 25).\n",
      "| figure | test id | gold | predicted | prob | correct | words | sum(SHAP)+base = logit |", "|---|---|---|---|---|---|---|---|"]
for n_, rid in enumerate(ids, 1):
    r = by[rid]; v = np.array(r["shap_values"]); words = [x.strip() for x in r["units"]]
    keep = np.arange(len(v)) if len(v) <= 25 else np.sort(np.argsort(-np.abs(v))[:20])
    fig, ax = plt.subplots(figsize=(6.5, 0.27 * len(keep) + 1.3))
    y = np.arange(len(keep))[::-1]
    ax.barh(y, v[keep], color=["#0072B2" if x >= 0 else "#D55E00" for x in v[keep]], edgecolor="black", linewidth=0.4)
    ax.set_yticks(y); ax.set_yticklabels([(words[i][:28] + "…") if len(words[i]) > 29 else words[i] for i in keep])
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("SHAP value (contribution to the logit of the predicted technique)"); ax.set_ylabel("Word (sentence order, top to bottom)")
    ax.text(0.99, 0.02, f"test id {rid} | gold: {', '.join(sorted(set(r['gold_labels'])))} | predicted: {r['pred_label']} (p = {r['pred_prob']:.2f})",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=8, bbox=dict(facecolor="white", edgecolor="#999999", linewidth=0.5))
    ax.spines[["top", "right"]].set_visible(False); ax.xaxis.grid(True, linewidth=0.4, color="#cccccc"); ax.set_axisbelow(True)
    fig.tight_layout(); fig.savefig(PACK / f"fig_shap_ex{n_}.png", dpi=300); plt.close(fig)
    M.append(f"| fig_shap_ex{n_}.png | {rid} | {', '.join(sorted(set(r['gold_labels'])))} | {r['pred_label']} ({names.get(r['pred_label'], {}).get('name', '?')}) | {r['pred_prob']:.3f} | "
             f"{r['top1_correct']} | {len(v)}{' (20 drawn)' if len(v) > 25 else ''} | {v.sum() + r['base_value']:.3f} = {r['pred_logit']:.3f} |")
    M.append(f"|  | sentence | {r['text'][:260].replace('|', '/')} |  |  |  |  |  |")
w(PACK / "06_shap.md", "\n".join(M)); print("\n".join(M))
