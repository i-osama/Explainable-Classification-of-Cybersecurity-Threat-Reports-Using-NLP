"""T3 (part 1): every analysis that needs only SAVED scores. Writes results/*.csv and results/tables/*.parquet.
Pre-registrations: experiments/prereg/01-05, 09. Run: python scripts/run_analyses.py"""
import json, sys
from collections import Counter
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap import RESULTS, SEEDS, EVIDENCE, CLS_DIR, MATCH_DIR, ROOT
from ttpmap.data import build_space, load_tactics, text_sha, file_sha
from ttpmap.metrics import hit_at_1, rr_at_k, precision_at_k, recall_at_k_micro, recall_at_k_per_sample, rank_topk, apply_threshold, f1_scores, f1_per_label, ece
from ttpmap.fusion import components, fuse, rank_space, to_full, zrow, ORDER, coarse_grid, wide_grid, select_weights, select_threshold
from ttpmap.stats import bootstrap_ci, paired_bootstrap, mcnemar_exact, holm
from ttpmap import schema

RESULTS.mkdir(exist_ok=True); (RESULTS / "tables").mkdir(exist_ok=True)
S = build_space(); L = S.L; Y = S.Y["test"]; Yd = S.Y["dev"]; n = len(Y); LAB = np.array(S.labels)
TEST_IDS = [f"test-{i:04d}" for i in range(n)]; DEV_IDS = [f"dev-{i:04d}" for i in range(len(Yd))]
Z = components(S, "test", "avg"); Zd = components(S, "dev", "avg")
def cls_avg(tag, sp="test"): return np.mean([to_full(S.cls_raw[tag, s][sp], S.cls_cols[tag, s], L, -1e9) for s in SEEDS], axis=0)
prior = np.tile(S.train_count.astype(float), (n, 1))
SYS = {"Frequency prior": prior, "TF-IDF + SVM": rank_space(S.svm_raw["test"], S.seen_idx, L), "RoBERTa (3-seed avg)": cls_avg("roberta"),
       "SecBERT (3-seed avg)": cls_avg("secbert"), "Matcher zero-shot": S.matcher_zero_test, "Matcher (3-seed ens.)": Z["matcher"],
       "Classifiers-only ens.": fuse(Z, (0, 1, 1, 1)), "Fusion equal (1,1,1,1)": fuse(Z, (1, 1, 1, 1)), "Fusion (3,1,1,1)": fuse(Z, (3, 1, 1, 1))}
H = {k: hit_at_1(v, Y) for k, v in SYS.items()}; RR = {k: rr_at_k(v, Y) for k, v in SYS.items()}
def w(name, rows): pd.DataFrame(rows).to_csv(RESULTS / name, index=False); print(f"  {name}: {len(rows)} rows")

# ---- 1 systems with CIs
rows = []
for k, Sc in SYS.items():
    c1, c2 = bootstrap_ci(H[k]), bootstrap_ci(RR[k]); un = Y & ~S.seen[None, :]
    top5 = rank_topk(Sc, 5); it = np.zeros(Y.shape, bool); it[np.arange(n)[:, None], top5] = True
    rows.append({"system": k, "P@1": c1["mean"], "P@1_lo": c1["lo"], "P@1_hi": c1["hi"], "MRR@3": c2["mean"], "MRR@3_lo": c2["lo"], "MRR@3_hi": c2["hi"],
                 "P@3": precision_at_k(Sc, Y, 3).mean(), "R@1_micro": recall_at_k_micro(Sc, Y, 1), "R@1_per_sample": recall_at_k_per_sample(Sc, Y, 1),
                 "R@5_micro": recall_at_k_micro(Sc, Y, 5), "unseen_R@5": (it & un).sum() / un.sum(), "n": n})
w("systems.csv", rows)

# ---- 2 per seed + 3 F1 variants
def full_pred(scores, cols, thr):
    P = np.zeros((len(scores), L), bool); P[:, cols] = apply_threshold(scores.copy(), thr); return P
ps, fv = [], []
grid_svm = np.arange(-0.6, 0.31, 0.05)
t_svm = select_threshold(S.svm_raw["dev"], Yd[:, S.seen_idx], grid_svm, split="dev")
runs = [("TF-IDF + SVM", "-", S.svm_raw["test"], S.seen_idx, t_svm)] + [(nice, s, S.cls_raw[tag, s]["test"], S.cls_cols[tag, s], S.cls_meta[tag, s]["threshold"])
        for tag, nice in (("roberta", "RoBERTa"), ("secbert", "SecBERT")) for s in SEEDS]
for nice, s, sc, cols, thr in runs:
    P = full_pred(sc, cols, thr); R_ = rank_space(sc, cols, L); r = {"system": nice, "seed": s, "threshold": thr, "P@1": hit_at_1(R_, Y).mean(), "MRR@3": rr_at_k(R_, Y).mean()}
    for v in ("notebook", "seen_test", "all_test"):
        f = f1_scores(P, Y, S.seen, v); r[f"micro_f1_{v}"] = f["micro_f1"]; r[f"macro_f1_{v}"] = f["macro_f1"]
        fv.append({"system": nice, "seed": s, "variant": v, **f})
    ps.append(r)
for s in SEEDS: ps.append({"system": "Matcher ft20", "seed": s, "P@1": hit_at_1(S.matcher_raw[s]["test"], Y).mean(), "MRR@3": rr_at_k(S.matcher_raw[s]["test"], Y).mean()})
for mode, nm in (("paired", "Fusion (3,1,1,1) seed-paired"), ("nb_seed", "Fusion (3,1,1,1) matcher seed varied")):
    for s in SEEDS:
        F = fuse(components(S, "test", mode, s), (3, 1, 1, 1)); ps.append({"system": nm, "seed": s, "P@1": hit_at_1(F, Y).mean(), "MRR@3": rr_at_k(F, Y).mean()})
ps.append({"system": "Fusion equal (1,1,1,1) matcher s42", "seed": 42, "P@1": hit_at_1(fuse(components(S, "test", "nb_seed", 42), (1, 1, 1, 1)), Y).mean()})
# frequency prior F1: predict the single most frequent train label for every sentence
Pp = np.zeros((n, L), bool); Pp[:, int(np.argmax(S.train_count))] = True
for v in ("notebook", "seen_test", "all_test"): fv.append({"system": "Frequency prior", "seed": "-", "variant": v, **f1_scores(Pp, Y, S.seen, v)})
w("per_seed.csv", ps); w("f1_variants.csv", fv)

# ---- 4 comparison family (prereg 01) + 5 ablation
ABL = {f"Fusion without {nm}": fuse(Z, tuple(0 if i == j else x for j, x in enumerate((3, 1, 1, 1)))) for i, nm in enumerate(ORDER)}
HA = {k: hit_at_1(v, Y) for k, v in ABL.items()}
fam = [("C1", "Fusion (3,1,1,1)", "Classifiers-only ens.", H), ("C2", "Fusion (3,1,1,1)", "Matcher (3-seed ens.)", H), ("C3", "RoBERTa (3-seed avg)", "TF-IDF + SVM", H),
       ("C4", "RoBERTa (3-seed avg)", "SecBERT (3-seed avg)", H)] + [(f"A{i + 1}", "Fusion (3,1,1,1)", f"Fusion without {nm}", None) for i, nm in enumerate(ORDER)]
rows = []
for cid, a, b, src in fam:
    ha, hb = H[a], (H[b] if src is not None else HA[b])
    pb = paired_bootstrap(ha, hb); mc = mcnemar_exact(ha, hb)
    rb = paired_bootstrap(RR[a], RR[b] if src is not None else rr_at_k(ABL[b], Y))
    rows.append({"id": cid, "A": a, "B": b, "P@1_A": ha.mean(), "P@1_B": hb.mean(), "delta_P@1": pb["delta"], "ci_lo": pb["lo"], "ci_hi": pb["hi"], "p_boot": pb["p_boot"],
                 "mcnemar_b": mc["b"], "mcnemar_c": mc["c"], "p_mcnemar": mc["p"], "delta_MRR@3": rb["delta"], "mrr_ci_lo": rb["lo"], "mrr_ci_hi": rb["hi"]})
adj = holm([r["p_mcnemar"] for r in rows])
for r, a_ in zip(rows, adj):
    r["p_holm"] = a_; r["family_size"] = len(rows); r["supported"] = bool(a_ < 0.05 and (r["ci_lo"] > 0 or r["ci_hi"] < 0))
w("comparisons.csv", rows)
w("ablation.csv", [{"system": "Fusion (3,1,1,1)", **bootstrap_ci(H["Fusion (3,1,1,1)"]), "MRR@3": RR["Fusion (3,1,1,1)"].mean()}] +
  [{"system": k, **bootstrap_ci(HA[k]), "MRR@3": rr_at_k(ABL[k], Y).mean()} for k in ABL])

# ---- 6 weight surface (prereg 03)
rows = []
for mode, seed, tag in (("nb_seed", 42, "matcher_s42"), ("avg", None, "matcher_avg")):
    zd, zt = components(S, "dev", mode, seed), components(S, "test", mode, seed)
    for gname, grid in (("coarse_255", coarse_grid()), ("wide_1711", wide_grid())):
        sel, key = select_weights(zd, Yd, grid, split="dev", sentence_ids=DEV_IDS, forbidden_ids=TEST_IDS)
        tmp = []
        for wv in grid:
            fd, ft = fuse(zd, wv), fuse(zt, wv)
            tmp.append({"matcher": tag, "grid": gname, "w_matcher": wv[0], "w_svm": wv[1], "w_roberta": wv[2], "w_secbert": wv[3],
                        "dev_MRR@3": round(float(rr_at_k(fd, Yd).mean()), 4), "dev_P@1": round(float(hit_at_1(fd, Yd).mean()), 4),
                        "test_P@1": float(hit_at_1(ft, Y).mean()), "test_MRR@3": float(rr_at_k(ft, Y).mean()), "dev_selected": tuple(wv) == sel})
        d = pd.DataFrame(tmp).sort_values(["dev_MRR@3", "dev_P@1"], ascending=False, kind="stable").reset_index(drop=True); d["dev_rank"] = d.index + 1
        rows += d.to_dict("records")
w("weight_surface.csv", rows)

# ---- 7 threshold grid extension (prereg 04)
rows = []; g0 = np.arange(0.1, 0.9, 0.05); g1 = np.arange(0.10, 0.9951, 0.01)
for tag in ("roberta", "secbert"):
    for s in SEEDS:
        cols = S.cls_cols[tag, s]; dv, te = S.cls_raw[tag, s]["dev"], S.cls_raw[tag, s]["test"]
        t0 = select_threshold(dv, Yd[:, cols], g0, split="dev"); t1 = select_threshold(dv, Yd[:, cols], g1, split="dev")
        f0 = f1_scores(full_pred(te, cols, t0), Y, S.seen, "notebook"); f1_ = f1_scores(full_pred(te, cols, t1), Y, S.seen, "notebook")
        d0 = f1_scores(full_pred(dv, cols, t0), Yd, S.seen, "notebook"); d1 = f1_scores(full_pred(dv, cols, t1), Yd, S.seen, "notebook")
        rows.append({"model": tag, "seed": s, "thr_original_grid": t0, "thr_stored": S.cls_meta[tag, s]["threshold"], "thr_extended_grid": t1,
                     "dev_micro_f1_original": d0["micro_f1"], "dev_micro_f1_extended": d1["micro_f1"],
                     "test_micro_f1_original": f0["micro_f1"], "test_micro_f1_extended": f1_["micro_f1"], "test_macro_f1_original": f0["macro_f1"], "test_macro_f1_extended": f1_["macro_f1"]})
w("threshold_grid.csv", rows)

# ---- 8 support buckets with CIs (prereg 05)
MAIN = ["TF-IDF + SVM", "RoBERTa (3-seed avg)", "SecBERT (3-seed avg)", "Matcher (3-seed ens.)", "Fusion (3,1,1,1)"]
tc = S.train_count; rarest = np.where(Y, tc[None, :], 10**9).min(1)
BUCK = [("unseen", 0, 0), ("1-4", 1, 4), ("5-9", 5, 9), ("10-19", 10, 19), ("20-49", 20, 49), ("50+", 50, 10**8)]
rows, fb = [], []
for bname, lo, hi in BUCK:
    m = (rarest >= lo) & (rarest <= hi); lm = (tc >= lo) & (tc <= hi) & (Y.sum(0) > 0)
    for k in MAIN:
        c = bootstrap_ci(H[k][m]); P1 = np.zeros_like(Y); P1[np.arange(n), rank_topk(SYS[k], 1)[:, 0]] = True
        rows.append({"bucket": bname, "system": k, "n_sentences": int(m.sum()), "n_labels": int(lm.sum()), "P@1": c["mean"], "lo": c["lo"], "hi": c["hi"],
                     "top1_label_F1": float(f1_per_label(P1, Y)[lm].mean())})
    pb = paired_bootstrap(H["Fusion (3,1,1,1)"][m], H["Matcher (3-seed ens.)"][m]); pc = paired_bootstrap(H["Fusion (3,1,1,1)"][m], H["Classifiers-only ens."][m])
    for ref, p_ in (("Matcher (3-seed ens.)", pb), ("Classifiers-only ens.", pc)):
        fb.append({"bucket": bname, "n": int(m.sum()), "reference": ref, "fixed": int(((H["Fusion (3,1,1,1)"] == 1) & (H[ref] == 0) & m).sum()),
                   "broken": int(((H["Fusion (3,1,1,1)"] == 0) & (H[ref] == 1) & m).sum()), "delta_P@1": p_["delta"], "ci_lo": p_["lo"], "ci_hi": p_["hi"]})
w("support_buckets.csv", rows); w("fixed_broken.csv", fb)

# ---- 9 tactics, confusions, parent/sub
tech = load_tactics().set_index("id"); tname = tech["name"].to_dict(); ttac = tech["tactics"].to_dict()
rows = []
for ta in sorted({x for t in LAB[Y.sum(0) > 0] for x in ttac.get(t, [])}):
    cols = np.array([ta in ttac.get(t, []) for t in LAB]); m = (Y & cols[None, :]).any(1)
    for k in MAIN:
        c = bootstrap_ci(H[k][m]); rows.append({"tactic": ta, "system": k, "n_sentences": int(m.sum()), "P@1": c["mean"], "lo": c["lo"], "hi": c["hi"]})
w("tactics.csv", rows)
def rel(g, p):
    if "." in g and p == g.split(".")[0]: return "predicted the parent"
    if "." in p and g == p.split(".")[0]: return "predicted a sub-technique"
    if g.split(".")[0] == p.split(".")[0]: return "sibling sub-technique"
    return "other technique"
conf, ps_ = [], []
for k in MAIN:
    c = Counter(); rc = Counter(); top = rank_topk(SYS[k], 1)[:, 0]
    for i in np.where(H[k] == 0)[0]:
        p = LAB[top[i]]; rels = []
        for g in LAB[Y[i]]: c[(g, p)] += 1; rels.append(rel(g, p))
        rc[next(x for x in ("predicted the parent", "predicted a sub-technique", "sibling sub-technique", "other technique") if x in rels)] += 1
    for (g, p), v in c.most_common(20):
        conf.append({"system": k, "gold": g, "gold_name": tname.get(g, "?"), "predicted": p, "predicted_name": tname.get(p, "?"), "count": v, "relation": rel(g, p),
                     "gold_train_support": int(tc[S.lab2i[g]]), "pred_train_support": int(tc[S.lab2i[p]])})
    tot = int((H[k] == 0).sum())
    for x in ("predicted the parent", "predicted a sub-technique", "sibling sub-technique", "other technique"):
        ps_.append({"system": k, "relation": x, "errors": rc.get(x, 0), "total_errors": tot, "share": rc.get(x, 0) / tot})
    par = np.array([l.split(".")[0] for l in LAB])
    ps_.append({"system": k, "relation": "technique-level P@1 (parent match counts)", "errors": np.nan, "total_errors": tot,
                "share": float(np.mean([par[top[i]] in set(par[Y[i]]) for i in range(n)]))})
w("confusions.csv", conf); w("parent_sub.csv", ps_)

# ---- 10 calibration
er, rb = [], []
for tag in ("roberta", "secbert"):
    for s in SEEDS:
        P = S.cls_raw[tag, s]["test"]; top = P.argmax(1); cf = P[np.arange(n), top]; ok = Y[:, S.cls_cols[tag, s]][np.arange(n), top].astype(float)
        e, bins = ece(cf, ok); er.append({"model": tag, "seed": s, "ECE": e, "mean_confidence": cf.mean(), "accuracy": ok.mean()})
        rb += [{"model": tag, "seed": s, **b} for b in bins]
w("calibration.csv", er); w("reliability_bins.csv", rb)

# ---- 11 support-aware fusion (prereg 09): dev selection, test touched once
band = np.where(tc <= 4, 0, np.where(tc <= 19, 1, 2))
def sa_fuse(Zx, wm): return np.array(wm, float)[band][None, :] * Zx["matcher"] + Zx["svm"] + Zx["roberta"] + Zx["secbert"]
import itertools
best = None; grid_rows = []
for wm in itertools.product([1, 2, 3, 4, 6, 8], repeat=3):
    fd = sa_fuse(Zd, wm); key = (round(float(rr_at_k(fd, Yd).mean()), 4), round(float(hit_at_1(fd, Yd).mean()), 4))
    grid_rows.append({"w_rare": wm[0], "w_mid": wm[1], "w_frequent": wm[2], "dev_MRR@3": key[0], "dev_P@1": key[1]})
    if best is None or key > best[0]: best = (key, wm)
w("support_aware_dev_grid.csv", grid_rows)
wm = best[1]; ft = sa_fuse(Z, wm); hs = hit_at_1(ft, Y); base = H["Fusion (3,1,1,1)"]; rare = rarest <= 4
pb = paired_bootstrap(hs, base); mc = mcnemar_exact(hs, base); pr = paired_bootstrap(hs[rare], base[rare])
rare_d = np.where(Yd, tc[None, :], 10**9).min(1) <= 4
w("support_aware_fusion.csv", [{"selected_w_rare": wm[0], "selected_w_mid": wm[1], "selected_w_frequent": wm[2], "dev_MRR@3": best[0][0], "dev_P@1": best[0][1],
     "dev_baseline_MRR@3": round(float(rr_at_k(sa_fuse(Zd, (3, 3, 3)), Yd).mean()), 4), "n_dev_rare": int(rare_d.sum()),
     "test_P@1": hs.mean(), "test_P@1_baseline": base.mean(), "delta_P@1": pb["delta"], "ci_lo": pb["lo"], "ci_hi": pb["hi"], "p_mcnemar": mc["p"],
     "test_MRR@3": rr_at_k(ft, Y).mean(), "test_MRR@3_baseline": RR["Fusion (3,1,1,1)"].mean(),
     "rare_n": int(rare.sum()), "rare_P@1": hs[rare].mean(), "rare_P@1_baseline": base[rare].mean(), "rare_delta": pr["delta"], "rare_ci_lo": pr["lo"], "rare_ci_hi": pr["hi"],
     "success_rule_met": bool(pb["lo"] >= -0.005 and hs[rare].mean() > base[rare].mean()), "test_evaluations": 1}])

# ---- 12 disagreement between the explained model and the fusion
R42 = rank_space(S.cls_raw["roberta", 42]["test"], S.cls_cols["roberta", 42], L); t42 = rank_topk(R42, 1)[:, 0]; tf = rank_topk(SYS["Fusion (3,1,1,1)"], 1)[:, 0]
h42 = hit_at_1(R42, Y); hf = H["Fusion (3,1,1,1)"]; same = t42 == tf
w("explained_vs_fusion.csv", [{"n": n, "same_top1": int(same.sum()), "different_top1": int((~same).sum()), "share_different": float((~same).mean()),
     "fusion_right_roberta_wrong": int(((hf == 1) & (h42 == 0)).sum()), "roberta_right_fusion_wrong": int(((hf == 0) & (h42 == 1)).sum()),
     "both_wrong_different_label": int(((hf == 0) & (h42 == 0) & ~same).sum()), "roberta_s42_P@1": h42.mean()}])

# ---- 12b overlap sensitivity: drop test sentences that also occur in train (ids from the evidence pack duplicate files)
dup = pd.read_csv(EVIDENCE / "01_duplicates.csv"); nd_ = pd.read_csv(EVIDENCE / "01_near_duplicates.csv")
ex_ids = sorted({int(float(x)) for v in dup[dup.type == "train_x_test"].ids_b for x in str(v).split(";")}); near_ids = sorted(set(nd_[nd_.pair == "train_x_test"].id_b.astype(int)))
rows = []
for k in MAIN + ["Classifiers-only ens."]:
    for nm, drop in (("none", []), ("exact", ex_ids), ("exact+near", sorted(set(ex_ids + near_ids)))):
        m = np.ones(n, bool); m[drop] = False
        rows.append({"system": k, "removed": nm, "n_removed": len(drop), "removed_test_ids": ";".join(map(str, drop)), "n": int(m.sum()), "P@1": H[k][m].mean(), "MRR@3": RR[k][m].mean()})
w("overlap_sensitivity.csv", rows)

# ---- 13 tables (no sentence text)
sent = []
for sp in ("train", "dev", "test"):
    d = getattr(S, sp)
    sent += [{"id": f"{sp}-{i:04d}", "split": sp, "text_sha256": text_sha(t), "n_words": max(1, len(str(t).split())), "labels": list(l)} for i, (t, l) in enumerate(zip(d["text"], d["labels"]))]
schema.validate_rows(sent, schema.Sentence); pd.DataFrame(sent).to_parquet(RESULTS / "tables" / "sentences.parquet", index=False)
techs = [{"id": l, "name": tname.get(l, "(not in ATT&CK v12.1 STIX)"), "tactics": list(ttac.get(l, [])), "parent_id": l.split(".")[0] if "." in l else None, "is_sub": "." in l,
          "train_support": int(tc[i]), "dev_support": int(Yd[:, i].sum()), "test_support": int(Y[:, i].sum())} for i, l in enumerate(S.labels)]
schema.validate_rows(techs, schema.Technique); pd.DataFrame(techs).to_parquet(RESULTS / "tables" / "techniques.parquet", index=False)
preds = []
for k, Sc in SYS.items():
    t3 = rank_topk(Sc, 3)
    preds += [{"sentence_id": TEST_IDS[i], "system": k, "top1": LAB[t3[i, 0]], "top2": LAB[t3[i, 1]], "top3": LAB[t3[i, 2]], "hit_at_1": bool(H[k][i]), "rr_at_3": float(RR[k][i])} for i in range(n)]
schema.validate_rows(preds, schema.Prediction); pd.DataFrame(preds).to_parquet(RESULTS / "tables" / "predictions.parquet", index=False)
sm = []
for tag in ("roberta", "secbert"):
    for s in SEEDS:
        for sp in ("dev", "test"):
            p = CLS_DIR / f"{tag}_pw_s{s}" / f"{sp}_probs.npy"; a = S.cls_raw[tag, s][sp]
            sm.append({"system": tag, "seed": s, "split": sp, "n_sentences": a.shape[0], "n_labels": a.shape[1], "score_kind": "probability", "source_file": str(p.relative_to(ROOT)).replace("\\", "/"), "sha256": file_sha(p)})
for s in SEEDS:
    for sp in ("dev", "test"):
        p = MATCH_DIR / f"ft20_s{s}" / f"{sp}_scores.npy"; a = S.matcher_raw[s][sp]
        sm.append({"system": "matcher_ft20", "seed": s, "split": sp, "n_sentences": a.shape[0], "n_labels": a.shape[1], "score_kind": "cosine", "source_file": str(p.relative_to(ROOT)).replace("\\", "/"), "sha256": file_sha(p)})
p = MATCH_DIR / "zeroshot" / "test_scores.npy"
sm.append({"system": "matcher_zeroshot", "seed": "-", "split": "test", "n_sentences": 725, "n_labels": 733, "score_kind": "cosine", "source_file": str(p.relative_to(ROOT)).replace("\\", "/"), "sha256": file_sha(p)})
for sp in ("dev", "test"):
    sm.append({"system": "svm", "seed": "-", "split": sp, "n_sentences": S.svm_raw[sp].shape[0], "n_labels": S.svm_raw[sp].shape[1], "score_kind": "decision_function",
               "source_file": "refit in memory (scores never saved)", "sha256": None})
schema.validate_rows(sm, schema.ScoreMatrix); d = pd.DataFrame(sm); d["seed"] = d["seed"].astype(str); d.to_parquet(RESULTS / "tables" / "score_matrices.parquet", index=False)
print(f"  tables: sentences {len(sent)}, techniques {len(techs)}, predictions {len(preds)}, score_matrices {len(sm)} (all rows schema-valid)")
