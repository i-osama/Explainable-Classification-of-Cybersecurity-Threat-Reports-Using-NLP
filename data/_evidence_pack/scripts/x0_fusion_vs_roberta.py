"""EXTRA (fusion-SHAP question, part 1): how far is the model that SHAP explains today (roberta_pw_s42)
from the fusion system that produces the headline number?  Uses saved scores only. -> 10_fusion_vs_roberta.csv + text"""
import numpy as np, pandas as pd
from common import PACK, SEEDS, p_at_1, rank_topk, w
from systems import build, components, fuse, rank_full, ORDER

S = build(); L = S.L; Y = S.Yte; n = len(Y); LAB = np.array(S.LABELS)
Z = components(S, "test", "avg")
F = fuse(Z, (3, 1, 1, 1)); R = rank_full(S.cls_raw["roberta", 42]["test"], S.cls_cols["roberta", 42], L)
tf, tr = rank_topk(F, 1)[:, 0], rank_topk(R, 1)[:, 0]
hf, hr = p_at_1(F, Y), p_at_1(R, Y)
same = tf == tr
rarest = np.where(Y, S.train_count[None, :], 10**9).min(1)
out = ["# 10 Fusion vs. the model SHAP currently explains (roberta_pw_s42)\n", "All from saved test scores. [RECOMPUTED]\n",
       f"- P@1: roberta_pw_s42 {hr.mean():.3f}, fusion (3,1,1,1) seed-averaged {hf.mean():.3f}",
       f"- same top-1 label: **{int(same.sum())} of {n} ({same.mean():.1%})**; different top-1: **{int((~same).sum())} ({(~same).mean():.1%})**",
       f"- of the {int((~same).sum())} sentences with a different top-1: fusion right & RoBERTa wrong {int(((hf == 1) & (hr == 0)).sum())}, "
       f"RoBERTa right & fusion wrong {int(((hf == 0) & (hr == 1) & ~same).sum())}, both right (different gold labels) {int(((hf == 1) & (hr == 1) & ~same).sum())}, "
       f"both wrong {int(((hf == 0) & (hr == 0) & ~same).sum())}",
       "- so for these sentences the stored SHAP words explain a label that the final system does not output.\n"]
# contribution of each component to the fused top-1 score and to the top1-top2 margin
top2 = rank_topk(F, 2)
rows = []
wv = dict(zip(ORDER, (3, 1, 1, 1)))
score_share = {k: [] for k in ORDER}; margin_c = {k: [] for k in ORDER}
for i in range(n):
    a, b = top2[i]
    tot = sum(wv[k] * Z[k][i, a] for k in ORDER); mar = sum(wv[k] * (Z[k][i, a] - Z[k][i, b]) for k in ORDER)
    for k in ORDER:
        score_share[k].append(wv[k] * Z[k][i, a] / tot); margin_c[k].append(wv[k] * (Z[k][i, a] - Z[k][i, b]) / mar)
out += ["## Where the fused decision comes from\n", "For each test sentence: share of the fused top-1 score, and share of the top-1 minus top-2 margin, contributed by each component (weights included).\n",
        "| component | weight | mean share of top-1 score | median share of top-1/top-2 margin | sentences where the component alone prefers the fused top-1 over the fused top-2 |", "|---|---|---|---|---|"]
for k in ORDER:
    pref = np.mean([Z[k][i, top2[i, 0]] > Z[k][i, top2[i, 1]] for i in range(n)])
    out.append(f"| {k} | {wv[k]} | {np.mean(score_share[k]):.3f} | {np.median(margin_c[k]):.3f} | {pref:.1%} |")
rob_alone = np.mean(score_share["roberta"])
out.append(f"\nRoBERTa (3-seed average) supplies on average {rob_alone:.1%} of the fused top-1 score; the single seed SHAP explains is one third of that component.\n")
# unseen / rare
out += ["## Does the fusion fix unseen and rare techniques? (premise check)\n", "| rarest gold label train support | n | RoBERTa s42 P@1 | matcher ens. P@1 | fusion P@1 | fusion top-1 == RoBERTa s42 top-1 |", "|---|---|---|---|---|---|"]
hm = p_at_1(Z["matcher"], Y)
for name, lo, hi in (("unseen (0)", 0, 0), ("1-4", 1, 4), ("5-9", 5, 9), ("10-19", 10, 19), ("20-49", 20, 49), ("50+", 50, 10**8)):
    m = (rarest >= lo) & (rarest <= hi)
    out.append(f"| {name} | {int(m.sum())} | {hr[m].mean():.3f} | {hm[m].mean():.3f} | {hf[m].mean():.3f} | {same[m].mean():.1%} |")
un = np.where(rarest == 0)[0]
top5 = rank_topk(F, 5)
out.append(f"\nUnseen-technique sentences (n={len(un)}): fusion top-1 correct in {int(hf[un].sum())}, gold in fusion top-5 in {int(sum(Y[i, top5[i]].any() for i in un))}; "
           f"matcher ensemble top-1 correct in {int(hm[un].sum())}. The fusion's top-1 label on these rows is a SEEN label in {int(sum(S.SEEN[tf[i]] for i in un))} of {len(un)} rows.")
pd.DataFrame({"test_id": np.arange(n), "roberta_s42_top1": LAB[tr], "fusion_top1": LAB[tf], "same_top1": same, "roberta_s42_hit": hr, "fusion_hit": hf,
              "rarest_gold_train_support": rarest}).to_csv(PACK / "10_fusion_vs_roberta.csv", index=False)
w(PACK / "10_fusion_vs_roberta.md", "\n".join(out)); print("\n".join(out))
