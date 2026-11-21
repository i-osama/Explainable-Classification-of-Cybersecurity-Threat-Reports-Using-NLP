"""T3: recompute every result from saved predictions with ONE metric implementation.
-> 03_results_recomputed.csv, 03_results.md, 03_fusion_grid_dev.csv"""
import itertools, math, json
from functools import reduce
import numpy as np, pandas as pd
from common import PACK, SEEDS, p_at_1, mrr_at_k, p_at_k, r_at_k, prf_micro, f1_per_label, rank_topk, w
from systems import build, components, fuse, rank_full, to_full, zrow, ORDER, Y_of

S = build(); L = S.L; Yte, Ydev = S.Yte, S.Ydev
test_lab = Yte.sum(0) > 0                       # 127 test labels
seen_test = test_lab & S.SEEN                   # 117
assert test_lab.sum() == 127 and seen_test.sum() == 117
unseen_gold = Yte & ~S.SEEN[None, :]
rows = []


def rank_row(name, group, seed, Sc, src, Y=Yte, split="test"):
    top5 = rank_topk(Sc, 5)
    intop = np.zeros(Y.shape, bool); intop[np.arange(len(Y))[:, None], top5] = True
    un = Y & ~S.SEEN[None, :]
    # ties at the top
    srt = np.sort(Sc, axis=1)
    return {"system": name, "group": group, "seed": seed, "split": split,
            "P@1": p_at_1(Sc, Y).mean(), "MRR@3": mrr_at_k(Sc, Y, 3).mean(), "P@3": p_at_k(Sc, Y, 3).mean(),
            "R@1": p_at_1(Sc, Y).sum() / Y.sum(), "R@5": (intop & Y).sum() / Y.sum(),
            "unseen_R@5": (intop & un).sum() / max(un.sum(), 1), "top1_ties": int((srt[:, -1] == srt[:, -2]).sum()),
            "source_file": src}


def thr_metrics(scores180, thr, cols):
    """scores over the model's 180 seen labels -> micro/macro F1 with the dev threshold + argmax fallback."""
    P = scores180 >= thr
    empty = P.sum(1) == 0
    P[np.where(empty)[0], scores180[empty].argmax(1)] = True
    Pf = np.zeros((len(P), L), bool); Pf[:, cols] = P
    mp, mr, mf = prf_micro(Pf, Yte)                          # micro over ALL 733 labels: unseen gold = FN
    mp180, mr180, mf180 = prf_micro(Pf[:, cols], Yte[:, cols])   # notebook convention: 180 seen columns only
    f = f1_per_label(Pf, Yte)
    return {"micro_F1_180cols(nb)": mf180, "micro_F1_all_labels": mf, "micro_P": mp180, "micro_R": mr180,
            "macro_F1_117": f[seen_test].mean(), "macro_F1_127": f[test_lab].mean(), "macro_F1_180": f[S.SEEN].mean(),
            "threshold": thr, "n_empty_before_fallback": int(empty.sum()),
            "subset_acc_180cols": float((Pf[:, cols] == Yte[:, cols]).all(1).mean())}


# ---------- SVM (refit) ----------
grid = np.arange(-0.6, 0.31, 0.05)
def mf_dev(t):
    P = S.svm_raw["dev"] >= t
    return prf_micro(P, Ydev[:, S.seen_idx])[2]
t_svm = float(grid[int(np.argmax([mf_dev(t) for t in grid]))])
r = rank_row("TF-IDF+LinearSVC", "svm", "-", rank_full(S.svm_raw["test"], S.seen_idx, L), "REFIT from Dataset/combined_train.csv[tram] (scores never saved)")
r.update(thr_metrics(S.svm_raw["test"].copy(), t_svm, S.seen_idx)); rows.append(r)

# ---------- classifiers per seed ----------
for tag, nice in (("roberta", "RoBERTa-base"), ("secbert", "SecBERT")):
    for s in SEEDS:
        m = S.cls_meta[tag, s]
        r = rank_row(nice, tag, s, rank_full(S.cls_raw[tag, s]["test"], S.cls_cols[tag, s], L), f"Exp_1_4_run_tram_2_epoc_30/{tag}_pw_s{s}/test_probs.npy")
        r.update(thr_metrics(S.cls_raw[tag, s]["test"].copy(), m["threshold"], S.cls_cols[tag, s]))
        r["stored_micro_f1"] = m["test"]["micro_f1"]; r["stored_macro_f1"] = m["test"]["macro_f1"]
        r["stored_hit@1"] = m["test"]["hit@1"]; r["stored_mrr@3"] = m["test"]["mrr@3"]; r["best_epoch"] = m["best_epoch"]
        rows.append(r)
    avg = np.mean([to_full(S.cls_raw[tag, s]["test"], S.cls_cols[tag, s], L, -1e9) for s in SEEDS], axis=0)
    rows.append(rank_row(f"{nice} 3-seed prob-average", tag + "_ens", "avg", avg, f"{tag}_pw_s42/43/44 test_probs.npy (mean)"))

# ---------- matcher ----------
rows.append(rank_row("Matcher zero-shot bge-base-en-v1.5", "matcher_zs", "-", S.m_zero, "run_match_1/zeroshot/test_scores.npy"))
for s in SEEDS:
    rows.append(rank_row("Matcher ft20", "matcher", s, S.m_raw[s]["test"], f"run_match_1/ft20_s{s}/test_scores.npy"))
Zavg = components(S, "test", "avg")
rows.append(rank_row("Matcher 3-seed ensemble (mean score)", "matcher_ens", "avg", Zavg["matcher"], "run_match_1/ft20_s42/43/44/test_scores.npy (mean)"))

# ---------- ensembles / fusion ----------
src_f = "matcher ft20 scores + SVM refit + roberta/secbert test_probs"
rows.append(rank_row("Classifiers-only ensemble (SVM+RoBERTa+SecBERT, equal z)", "cls_only", "avg", fuse(Zavg, (0, 1, 1, 1)), src_f))
rows.append(rank_row("Fusion equal weights (1,1,1,1), matcher 3-seed avg", "fusion_eq", "avg", fuse(Zavg, (1, 1, 1, 1)), src_f))
Z42 = components(S, "test", "nb_seed", 42)
rows.append(rank_row("Fusion equal weights (1,1,1,1), matcher s42 [as Exp_2.1 CELL 8]", "fusion_eq_nb", 42, fuse(Z42, (1, 1, 1, 1)), src_f))
rows.append(rank_row("Fusion (3,1,1,1) seed-averaged", "fusion_avg", "avg", fuse(Zavg, (3, 1, 1, 1)), src_f))
rows.append(rank_row("Fusion (4,1,1,1) seed-averaged [wide-grid dev winner]", "fusion_4111", "avg", fuse(Zavg, (4, 1, 1, 1)), src_f))
for s in SEEDS:
    rows.append(rank_row("Fusion (3,1,1,1) matcher seed s + 3-seed-avg classifiers [Exp_2.1 CELL 11]", "fusion_nb_seed", s,
                         fuse(components(S, "test", "nb_seed", s), (3, 1, 1, 1)), src_f))
for s in SEEDS:
    rows.append(rank_row("Fusion (3,1,1,1) seed-paired (matcher s, RoBERTa s, SecBERT s)", "fusion_paired", s,
                         fuse(components(S, "test", "paired", s), (3, 1, 1, 1)), src_f))
for drop_i, nm in enumerate(ORDER):
    wv = [3, 1, 1, 1]; wv[drop_i] = 0
    rows.append(rank_row(f"Ablation: fusion without {nm}", "ablation", "avg", fuse(Zavg, wv), src_f))
# dev rows for the selected systems (leakage context)
Zdev_avg = components(S, "dev", "avg")
rows.append(rank_row("Fusion (3,1,1,1) seed-averaged", "fusion_avg", "avg", fuse(Zdev_avg, (3, 1, 1, 1)), src_f, Ydev, "dev"))

df = pd.DataFrame(rows)
df.to_csv(PACK / "03_results_recomputed.csv", index=False)

# ---------- weight grids on DEV (reproduce selection) ----------
Zd = components(S, "dev", "nb_seed", 42); Zt = components(S, "test", "nb_seed", 42)
def key(wv, Z, Y):
    Sc = fuse(Z, wv); return round(mrr_at_k(Sc, Y).mean(), 4), round(p_at_1(Sc, Y).mean(), 4)
coarse = [(key(wv, Zd, Ydev), wv) for wv in itertools.product([0, 1, 2, 3], repeat=4) if sum(wv)]
best_c = None
for k_, wv in coarse:                                   # same loop/tie rule as CELL 8 (first strictly-greater wins)
    if best_c is None or k_ > best_c[0]: best_c = (k_, wv)
seen_w, wide = set(), []
for wv in itertools.product([0, 1, 2, 3, 4, 6, 8], repeat=4):
    g = reduce(math.gcd, wv)
    if g == 0: continue
    wv = tuple(x // g for x in wv)
    if wv in seen_w: continue
    seen_w.add(wv); wide.append((*key(wv, Zd, Ydev), wv))
wide.sort(reverse=True)
gd = pd.DataFrame([{"w_matcher": w_[0], "w_svm": w_[1], "w_roberta": w_[2], "w_secbert": w_[3], "dev_MRR@3": a, "dev_P@1": b} for a, b, w_ in wide])
gd["dev_rank"] = np.arange(1, len(gd) + 1)
gd.to_csv(PACK / "03_fusion_grid_dev.csv", index=False)
rank_3111 = int(gd[(gd.w_matcher == 3) & (gd.w_svm == 1) & (gd.w_roberta == 1) & (gd.w_secbert == 1)]["dev_rank"].iloc[0])

# ---------- report ----------
def ms(v): return f"{np.mean(v):.3f} +/- {np.std(v, ddof=1):.3f}"
def g(group, col, split="test"):
    return df[(df.group == group) & (df.split == split)][col].astype(float).tolist()
def one(group, col): return g(group, col)[0]
M = ["# 03 Results recomputed from saved predictions\n",
     "One metric implementation (`scripts/common.py`): ranking by descending score, **ties broken by lower label index (stable sort)**; "
     "P@1 = share of sentences whose top-1 label is gold; MRR@3 = mean of 1/rank of first gold label in top 3 (0 if none); "
     "P@3 = (#gold in top 3)/3 averaged over sentences. All ranking metrics are computed in the 733-label space against ALL gold labels "
     "(sentences whose gold label was never seen in training count as misses for the classifiers). Label granularity: exact ID match "
     "(sub-technique T1059.001 != parent T1059).\n",
     "Thresholded metrics: dev-tuned global threshold from `metrics.json`, then if a row has no label above threshold the arg-max label is forced "
     "(Exp_1_4 CELL 4 `apply_thresholds`). `micro_F1_180cols(nb)` reproduces the notebook (only the 180 train labels are scored, so the 10 unseen gold "
     "labels are silently ignored); `micro_F1_all_labels` counts them as false negatives.\n",
     "## Per-seed table\n",
     "| system | seed | microF1 (nb) | microF1 (all labels) | macroF1-117 | macroF1-127 | P@1 | MRR@3 | P@3 | thr | empty rows fixed |", "|---|---|---|---|---|---|---|---|---|---|---|"]
for _, r in df[df.group.isin(["svm", "roberta", "secbert"])].iterrows():
    M.append(f"| {r.system} | {r.seed} | {r['micro_F1_180cols(nb)']:.4f} | {r.micro_F1_all_labels:.4f} | {r.macro_F1_117:.4f} | {r.macro_F1_127:.4f} | "
             f"{r['P@1']:.4f} | {r['MRR@3']:.4f} | {r['P@3']:.4f} | {r.threshold:.2f} | {int(r.n_empty_before_fallback)} |")
M += ["\n## Ranking systems\n", "| system | seed | split | P@1 | MRR@3 | P@3 | R@5 | unseen R@5 | top-1 ties |", "|---|---|---|---|---|---|---|---|---|"]
for _, r in df[~df.group.isin(["svm", "roberta", "secbert"])].iterrows():
    M.append(f"| {r.system} | {r.seed} | {r.split} | {r['P@1']:.4f} | {r['MRR@3']:.4f} | {r['P@3']:.4f} | {r['R@5']:.4f} | {r['unseen_R@5']:.2f} | {r.top1_ties} |")

svm = df[df.group == "svm"].iloc[0]
claims = [
 ("B1", "micro-F1 RoBERTa 0.705 +/- 0.011", ms(g("roberta", "micro_F1_180cols(nb)")), "0.705 +/- 0.011"),
 ("B2", "micro-F1 SecBERT 0.703 +/- 0.001", ms(g("secbert", "micro_F1_180cols(nb)")), "0.703 +/- 0.001"),
 ("B3", "micro-F1 SVM 0.696", f"{svm['micro_F1_180cols(nb)']:.3f}", "0.696"),
 ("B4", "macro-F1 RoBERTa 0.563 (117) / 0.519 (127)", f"{np.mean(g('roberta','macro_F1_117')):.3f} / {np.mean(g('roberta','macro_F1_127')):.3f}", "0.563 / 0.519"),
 ("B5", "macro-F1 SecBERT 0.543 / 0.500", f"{np.mean(g('secbert','macro_F1_117')):.3f} / {np.mean(g('secbert','macro_F1_127')):.3f}", "0.543 / 0.500"),
 ("B6", "P@1 SVM 0.742", f"{svm['P@1']:.3f}", "0.742"),
 ("B7", "P@1 RoBERTa 0.756", f"3-seed prob-average: {one('roberta_ens','P@1'):.3f}; mean of seeds: {ms(g('roberta','P@1'))}", "0.756"),
 ("B8", "P@1 SecBERT 0.755", f"3-seed prob-average: {one('secbert_ens','P@1'):.3f}; mean of seeds: {ms(g('secbert','P@1'))}", "0.755"),
 ("B9", "classifiers-only ensemble 0.774", f"{one('cls_only','P@1'):.3f}", "0.774"),
 ("B10a", "bge zero-shot 0.228", f"{one('matcher_zs','P@1'):.3f}", "0.228"),
 ("B10b", "ft20 0.756 +/- 0.015", ms(g("matcher", "P@1")), "0.756 +/- 0.015"),
 ("B10c", "matcher 3-seed ensemble 0.777", f"{one('matcher_ens','P@1'):.3f}", "0.777"),
 ("B11", "equal-weight fusion 0.779", f"matcher s42 (as notebook): {one('fusion_eq_nb','P@1'):.3f}; matcher 3-seed avg: {one('fusion_eq','P@1'):.3f}", "0.779"),
 ("B12a", "seed-paired fusion P@1 0.796 +/- 0.006 (0.790/0.796/0.803)", f"{ms(g('fusion_paired','P@1'))} ({'/'.join(f'{x:.3f}' for x in g('fusion_paired','P@1'))})", "0.796 +/- 0.006"),
 ("B12b", "seed-paired fusion MRR@3 0.852 +/- 0.002", ms(g("fusion_paired", "MRR@3")), "0.852 +/- 0.002"),
 ("B13a", "seed-averaged fusion P@1 0.803", f"{one('fusion_avg','P@1'):.3f}", "0.803"),
 ("B13b", "seed-averaged fusion MRR@3 0.853?", f"{one('fusion_avg','MRR@3'):.3f}", "0.853"),
]
M += ["\n## Claims B1-B13\n", "| ID | claim | recomputed | diff flag |", "|---|---|---|---|"]
import re
for cid, claim, val, ref in claims:
    nums_ref = [float(x) for x in re.findall(r"\d\.\d+", ref)]
    nums_val = [float(x) for x in re.findall(r"\d\.\d+", val)]
    ok = all(any(abs(a - b) <= 0.001 + 1e-9 for b in nums_val) for a in nums_ref)
    M.append(f"| {cid} | {claim} | {val} | {'ok (<=0.001)' if ok else '**DIFF > 0.001**'} |")
M += ["\nNotebook variant of the per-seed fusion (matcher seed varies, classifiers 3-seed averaged; Exp_2.1 CELL 11, `final_results_table.csv`): "
      f"P@1 {ms(g('fusion_nb_seed','P@1'))}, MRR@3 {ms(g('fusion_nb_seed','MRR@3'))}.\n",
      "## B14 fusion weights and grid  [RECOMPUTED on DEV]\n",
      f"- component order: `{ORDER}` (Exp_2.1 CELL 8 output `models: [...]`)",
      f"- coarse grid {{0,1,2,3}}^4 minus all-zero = {len(coarse)} settings, matcher = ft20 seed 42, classifiers = 3-seed averages: DEV winner **{best_c[1]}** with dev (MRR@3, P@1) = ({float(best_c[0][0]):.4f}, {float(best_c[0][1]):.4f})",
      f"- wide grid {{0,1,2,3,4,6,8}}^4 reduced by gcd = **{len(wide)}** settings: DEV winner **{wide[0][2]}** (dev MRR@3 {wide[0][0]}, P@1 {wide[0][1]}); "
      f"(3,1,1,1) is rank **{rank_3111}** of {len(wide)} on that grid (dev MRR@3 {key((3,1,1,1), Zd, Ydev)[0]}).",
      f"- test P@1 for (3,1,1,1) vs (4,1,1,1), matcher s42: {p_at_1(fuse(Zt,(3,1,1,1)), Yte).mean():.4f} vs {p_at_1(fuse(Zt,(4,1,1,1)), Yte).mean():.4f}",
      "- **So (3,1,1,1) is the winner of the 255-setting coarse grid, NOT of the 1,711 grid** (the 1,711 grid prefers (4,1,1,1)). Full dev ranking: `03_fusion_grid_dev.csv`.\n",
      "## Checks\n",
      f"- stored vs recomputed (classifiers, 6 runs): max |micro-F1 diff| = {np.nanmax(np.abs(df['micro_F1_180cols(nb)'] - df['stored_micro_f1'])):.2e}, "
      f"max |macro-F1(117) diff| = {np.nanmax(np.abs(df['macro_F1_117'] - df['stored_macro_f1'])):.2e}, max |P@1 diff| = {np.nanmax(np.abs(df['P@1'] - df['stored_hit@1'])):.2e}, "
      f"max |MRR@3 diff| = {np.nanmax(np.abs(df['MRR@3'] - df['stored_mrr@3'])):.2e}",
      f"- SVM refit vs notebook output (Exp_1_4 CELL 6: micro_f1 0.6961, macro_f1 0.5427, hit@1 0.7421, mrr@3 0.8138, thr -0.45): "
      f"{svm['micro_F1_180cols(nb)']:.4f}, {svm.macro_F1_117:.4f}, {svm['P@1']:.4f}, {svm['MRR@3']:.4f}, thr {t_svm:.2f}",
      f"- matcher stored metrics.json test P@1 per seed: " + ", ".join(f"s{s}={json.load(open(str(PACK.parent / 'run_match_1' / f'ft20_s{s}' / 'metrics.json')))['test']['P@1']:.4f}" for s in SEEDS)
      + " vs recomputed " + ", ".join(f"{x:.4f}" for x in g("matcher", "P@1")),
      f"- rows with a tie for rank 1 (any system): max = {int(df['top1_ties'].max())}",
      f"- RoBERTa dev thresholds: {[round(S.cls_meta['roberta', s]['threshold'], 2) for s in SEEDS]} -> all at the TOP EDGE of the grid np.arange(0.1, 0.9, 0.05) (max 0.85); the optimum may lie above the grid. SecBERT: {[round(S.cls_meta['secbert', s]['threshold'], 2) for s in SEEDS]}."]
w(PACK / "03_results.md", "\n".join(M))
print("\n".join(M[-(len(claims) + 22):]))
