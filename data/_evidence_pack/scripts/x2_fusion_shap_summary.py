"""EXTRA part 3: summarise x1 output -> 11_fusion_shap.md.  usage: python x2_fusion_shap_summary.py [--file 11_fusion_shap_partial.jsonl]"""
import argparse, json
import numpy as np
from scipy.stats import spearmanr
from common import PACK, SHAPD, w
ap = argparse.ArgumentParser(); ap.add_argument("--file", default="11_fusion_shap_partial.jsonl"); A = ap.parse_args()
recs = [json.loads(l) for l in open(PACK / A.file, encoding="utf-8") if l.strip()]
stored = {}
for l in open(SHAPD / "shap_v2_roberta_pw_s42.jsonl", encoding="utf-8"):
    if l.strip():
        r = json.loads(l); stored[r["row"]] = r
m = recs[0]["method"]
M = [f"# 11 SHAP of the fused score ({m['system']})\n",
     f"Source `{A.file}`: {len(recs)} test sentences = first {len(recs)} of `RandomState(42).permutation(725)` (same fixed sample as the stored SHAP run and the human sheet). "
     f"Method identical to Exp_3_0b except the explained function: {m['output']}; components {m['components']} with weights {m['weights']}. [RECOMPUTED, new]\n"]
same = [r for r in recs if r["same_label_as_roberta_shap"]]
M += [f"- additivity error (sum of SHAP + base vs. fused score): max {max(r['additivity_error'] for r in recs):.1e}",
      f"- fused top-1 correct: {sum(r['fused_top1_correct'] for r in recs)} of {len(recs)}; stored RoBERTa s42 top-1 correct on the same rows: {sum(stored[r['row']]['top1_correct'] for r in recs)}",
      f"- fused top-1 label equals the label the stored RoBERTa SHAP explains: {len(same)} of {len(recs)}\n"]
# agreement of explanations
rho, ov, rho_d = [], [], []
for r in recs:
    a = np.array(r["shap_fused"]); b = np.array(stored[r["row"]]["shap_values"])
    if len(a) != len(b) or len(a) < 3: continue
    c = spearmanr(a, b).statistic
    (rho if r["same_label_as_roberta_shap"] else rho_d).append(c)
    if r["same_label_as_roberta_shap"]:
        ov.append(len(set(np.argsort(-a, kind="stable")[:3]) & set(np.argsort(-b, kind="stable")[:3])))
M += ["## Do the fused explanations differ from the stored RoBERTa explanations?\n",
      f"- same label (n={len(rho)}): Spearman rank correlation of word scores, mean {np.mean(rho):.3f}, median {np.median(rho):.3f}, min {np.min(rho):.3f}; "
      f"top-3 word overlap: mean {np.mean(ov):.2f} of 3; all 3 identical in {sum(o == 3 for o in ov)} sentences, <=1 shared in {sum(o <= 1 for o in ov)}",
      (f"- different label (n={len(rho_d)}): Spearman mean {np.mean(rho_d):.3f} (the two explanations are about different techniques)" if rho_d else "- different label: none in this sample"), ""]
# component shares
names = m["components"]; wts = dict(zip(names, m["weights"]))
share = {c: [] for c in names}
for r in recs:
    tot = sum(wts[c] * np.abs(np.array(r["shap_by_component"][c])).sum() for c in names)
    for c in names: share[c].append(wts[c] * np.abs(np.array(r["shap_by_component"][c])).sum() / tot)
M += ["## Which component carries the attribution mass?\n", "Share of sum |SHAP| (weights applied), mean over sentences:\n", "| component | weight | mean share |", "|---|---|---|"]
M += [f"| {c} | {wts[c]} | {np.mean(share[c]):.3f} |" for c in names]
# cross-component agreement
pairs = [(a, b) for i, a in enumerate(names) for b in names[i + 1:]]
M += ["\nSpearman between components' word scores (same sentence, same label), mean: " +
      "; ".join(f"{a} vs {b} {np.mean([spearmanr(r['shap_by_component'][a], r['shap_by_component'][b]).statistic for r in recs if len(r['units']) >= 3]):.3f}" for a, b in pairs) + "\n"]
# deletion on the fused score
d = [r for r in recs if r.get("del_used")]
if d:
    f_ = np.array([r["drop_fusedSHAP_top3"] for r in d]); rb = np.array([r["drop_robertaSHAP_top3"] for r in d]); rn = np.array([r["drop_random3"] for r in d])
    rng = np.random.RandomState(42)
    def ci(x):
        b = [x[rng.randint(0, len(x), len(x))].mean() for _ in range(2000)]; return np.percentile(b, [2.5, 97.5])
    M += ["## Deletion test on the FUSED score (word removal, 3 words)\n",
          f"Eligible sentences: {len(d)} (>= 6 words, >= 3 positive words in both explanations). Drop = fused z-score sum of the fused top-1 label before minus after.\n",
          "| words removed | mean drop | 95% CI |", "|---|---|---|",
          f"| top-3 by SHAP of the fused score | {f_.mean():.3f} | [{ci(f_)[0]:.3f}, {ci(f_)[1]:.3f}] |",
          f"| top-3 by the stored RoBERTa-only SHAP | {rb.mean():.3f} | [{ci(rb)[0]:.3f}, {ci(rb)[1]:.3f}] |",
          f"| 3 random words (mean of 20 draws) | {rn.mean():.3f} | [{ci(rn)[0]:.3f}, {ci(rn)[1]:.3f}] |",
          f"\n- fused-SHAP minus RoBERTa-SHAP drop: mean {np.mean(f_ - rb):+.3f}, 95% CI [{ci(f_ - rb)[0]:+.3f}, {ci(f_ - rb)[1]:+.3f}]; fused-SHAP larger in {int((f_ > rb).sum())}, equal in {int((f_ == rb).sum())}, smaller in {int((f_ < rb).sum())} of {len(d)}",
          f"- RoBERTa-SHAP words recover {rb.mean() / f_.mean():.0%} of the drop that the fused-SHAP words achieve; random words {rn.mean() / f_.mean():.0%}",
          f"- restricted to sentences where the two explanations target the same label (n={sum(r['same_label_as_roberta_shap'] for r in d)}): fused {np.mean([r['drop_fusedSHAP_top3'] for r in d if r['same_label_as_roberta_shap']]):.3f}, "
          f"RoBERTa {np.mean([r['drop_robertaSHAP_top3'] for r in d if r['same_label_as_roberta_shap']]):.3f}"]
    diff = [r for r in d if not r["same_label_as_roberta_shap"]]
    if diff:
        M.append(f"- sentences where the labels differ (n={len(diff)}): fused {np.mean([r['drop_fusedSHAP_top3'] for r in diff]):.3f}, RoBERTa {np.mean([r['drop_robertaSHAP_top3'] for r in diff]):.3f}")
M += ["\nLimits: this is a faithfulness measurement (does hiding the words move the explained score), not a plausibility measurement; "
      + ("the matcher (weight 3, about 39% of the fused top-1 score) is NOT included because its weights were never saved." if "NO matcher" in m["system"] else "full fusion, retrained matcher.")]
w(PACK / ("11_fusion_shap_full.md" if "full" in A.file else "11_fusion_shap.md"), "\n".join(M)); print("\n".join(M))
