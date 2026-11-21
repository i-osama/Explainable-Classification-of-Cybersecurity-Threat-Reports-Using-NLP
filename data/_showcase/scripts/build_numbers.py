"""Build thesis_numbers.json (the single source of truth) and THESIS_MAP.md from result files only.
No number is typed here except ledger 'thesis values' (the claims being checked) and file-read settings.
Run after run_analyses.py (and run_inference.py if available): python scripts/build_numbers.py"""
import json, re, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap import RESULTS, EVIDENCE, SHOWCASE, ROOT, MATCH_DIR, SHAP_DIR, SEEDS
from ttpmap.schema import Claim

C = []
def add(id, label, value, definition, source, script, status, section, ci=None, display=None, note="", nd=3):
    if value is not None and not isinstance(value, str): value = float(value) if not float(value).is_integer() or isinstance(value, float) else int(value)
    if display is None:
        display = "n/a" if value is None else (value if isinstance(value, str) else (f"{value:,}" if isinstance(value, int) else f"{value:.{nd}f}"))
    C.append(Claim(id=id, label=label, value=value, display=str(display), ci=[float(ci[0]), float(ci[1])] if ci is not None else None, definition=definition,
                   source_file=source, script=script, status=status, thesis_section=section, note=note).model_dump())
def ms(v): return f"{np.mean(v):.3f} +/- {np.std(v, ddof=1):.3f}"
R = lambda f: pd.read_csv(RESULTS / f)
RA, RI, T1 = "scripts/run_analyses.py", "scripts/run_inference.py", "_evidence_pack/scripts/t1_dataset.py"

# ================= A: data =================
sent = pd.read_parquet(RESULTS / "tables" / "sentences.parquet"); tech = pd.read_parquet(RESULTS / "tables" / "techniques.parquet")
n = sent.split.value_counts().to_dict(); src = "Dataset/combined_train.csv[tram], tram_dev.tsv, tram_test.tsv -> results/tables/sentences.parquet"
add("A1", "Total sentences", int(len(sent)), "train + dev + test rows", src, RA, "RECOMPUTED", "Data")
add("A2", "Train / dev / test sentences", f"{n['train']:,} / {n['dev']} / {n['test']}", "rows per split; train after exact-text de-duplication", src, RA, "RECOMPUTED", "Data")
for sp in ("train", "dev", "test"): add(f"A2.{sp}", f"{sp} sentences", int(n[sp]), f"rows in the {sp} split", src, RA, "RECOMPUTED", "Data")
add("A2.labels_all", "Distinct labels, all splits", int(((tech.train_support + tech.dev_support + tech.test_support) > 0).sum()), "distinct technique ids in train + dev + test",
    "results/tables/techniques.parquet", RA, "RECOMPUTED", "Data", note="added 15 Nov from the audit of Thesis_Draft_v2.2.docx (p370)")
add("A2.labels_per_text", "Labels per sentence, all splits", float(sent["labels"].map(len).mean()), "mean number of technique ids per sentence, train + dev + test",
    src, RA, "RECOMPUTED", "Data", nd=2, note="added 15 Nov from the audit of Thesis_Draft_v2.2.docx (p272, p274, p370)")
add("A2.words_mean", "Words per sentence (whitespace), all splits", float(sent["n_words"].mean()), "mean whitespace-separated words per sentence, train + dev + test",
    src, RA, "RECOMPUTED", "Data", nd=1, note="Draft v2.2 p370 says 23 tokens: no common tokenisation gives 23 (whitespace 21.0, \\w+ words 22.5, RoBERTa sub-words 34.1)")
add("A3", "Train labels", int((tech.train_support > 0).sum()), "distinct technique ids with at least one training sentence", "results/tables/techniques.parquet", RA, "RECOMPUTED", "Data")
add("A4", "Test labels", int((tech.test_support > 0).sum()), "distinct technique ids in the test split", "results/tables/techniques.parquet", RA, "RECOMPUTED", "Data")
seen_t = int(((tech.test_support > 0) & (tech.train_support > 0)).sum()); un_t = int(((tech.test_support > 0) & (tech.train_support == 0)).sum())
add("A5", "Seen + unseen test labels", f"{seen_t} + {un_t}", "test labels with / without a training sentence", "results/tables/techniques.parquet", RA, "RECOMPUTED", "Data")
add("A5.seen", "Seen test labels", seen_t, "test labels that occur in training", "results/tables/techniques.parquet", RA, "RECOMPUTED", "Data")
add("A5.unseen", "Unseen test labels", un_t, "test labels that never occur in training", "results/tables/techniques.parquet", RA, "RECOMPUTED", "Data")
dup = pd.read_csv(EVIDENCE / "01_duplicates.csv"); nd_ = pd.read_csv(EVIDENCE / "01_near_duplicates.csv")
ex_t = int((dup.type == "train_x_test").sum()); ex_d = int((dup.type == "train_x_dev").sum())
nt = int(nd_[nd_.pair == "train_x_test"].id_b.nunique()); ndv = int(nd_[nd_.pair == "train_x_dev"].id_b.nunique())
add("A6", "Test / dev sentences also in train", f"exact {ex_t} / {ex_d}; near-duplicate +{nt} / +{ndv}", "exact = equal after lower-casing and whitespace collapse; near = token-set Jaccard >= 0.90, not exact",
    "_evidence_pack/01_duplicates.csv, 01_near_duplicates.csv", T1, "RECOMPUTED", "Data", note="Draft claim '2 test, 1 dev' is wrong as exact duplicates.")
for k, v in (("A6.exact_test", ex_t), ("A6.exact_dev", ex_d), ("A6.near_test", nt), ("A6.near_dev", ndv)):
    add(k, k.split(".")[1].replace("_", " ") + " rows overlapping train", v, "see A6", "_evidence_pack/01_duplicates.csv, 01_near_duplicates.csv", T1, "RECOMPUTED", "Data")
tr = pd.read_csv(EVIDENCE / "01_truncated_test_ids.csv"); tr_r = int(tr.tokenizer.str.startswith("roberta").sum()); tr_s = int(tr.tokenizer.str.startswith("jackaduma").sum())
add("A7", "Test sentences longer than 128 tokens", f"{tr_r} (RoBERTa tokenizer); {tr_s} (SecBERT tokenizer)", "token count including special tokens > 128", "_evidence_pack/01_truncated_test_ids.csv", T1, "RECOMPUTED", "Data")
add("A7.roberta", "Truncated test sentences, RoBERTa", tr_r, "see A7", "_evidence_pack/01_truncated_test_ids.csv", T1, "RECOMPUTED", "Data")
add("A7.secbert", "Truncated test sentences, SecBERT", tr_s, "see A7", "_evidence_pack/01_truncated_test_ids.csv", T1, "RECOMPUTED", "Data")
n_desc = int(len(pd.read_csv(ROOT / "Dataset" / "ttp-desc-mappings.csv", sep="\t")))
add("A8", "ATT&CK description entries", f"{n_desc} in the file; {len(tech)} used", "rows of ttp-desc-mappings.csv; matching space after removing 4 revoked ids", "Dataset/ttp-desc-mappings.csv", RA, "RECOMPUTED", "Data")
add("A8.file", "Description file entries", n_desc, "rows in ttp-desc-mappings.csv (tab-separated)", "Dataset/ttp-desc-mappings.csv", RA, "RECOMPUTED", "Data")
add("A8.space", "Labels in the matching space", int(len(tech)), "description entries minus 4 revoked duplicate ids", "results/tables/techniques.parquet", RA, "RECOMPUTED", "Data")
te = sent[sent.split == "test"]; nl = te["labels"].apply(len)
add("A9.multi_test", "Multi-label test sentences", int((nl > 1).sum()), "test sentences with 2 or more distinct gold labels", "results/tables/sentences.parquet", RA, "RECOMPUTED", "Data")
add("A9.pairs_test", "Gold (sentence, label) pairs in test", int(nl.sum()), "sum of distinct gold labels over test sentences", "results/tables/sentences.parquet", RA, "RECOMPUTED", "Data")
add("A9.sub_share", "Sub-technique labels among train labels", int(((tech.train_support > 0) & tech.is_sub).sum()), "train labels whose id contains a dot", "results/tables/techniques.parquet", RA, "RECOMPUTED", "Data")
add("A9.rare_train", "Train labels with fewer than 5 sentences", int(((tech.train_support > 0) & (tech.train_support < 5)).sum()), "labels with train support 1-4", "results/tables/techniques.parquet", RA, "RECOMPUTED", "Data")
add("A9.median_support", "Median train support per label", int(tech[tech.train_support > 0].train_support.median()), "median training sentences per train label", "results/tables/techniques.parquet", RA, "RECOMPUTED", "Data")

# ================= B: results =================
ps = R("per_seed.csv"); sy = R("systems.csv").set_index("system"); fv = R("f1_variants.csv")
def seedv(system, col): return ps[ps.system == system][col].astype(float).to_numpy()
CLSRC = "Exp_1_4_run_tram_2_epoc_30/*_pw_s4{2,3,4}/test_probs.npy -> results/per_seed.csv"; MSRC = "run_match_1/ft20_s4{2,3,4}/test_scores.npy -> results/per_seed.csv"
for cid, s_, nm in (("B1", "RoBERTa", "RoBERTa"), ("B2", "SecBERT", "SecBERT")):
    v = seedv(s_, "micro_f1_notebook"); add(cid, f"micro-F1 {nm} (3 seeds)", float(v.mean()), "mean +/- sample sd over seeds 42-44; notebook variant (only the 180 train labels are scored), dev threshold + arg-max fallback",
        CLSRC, RA, "RECOMPUTED", "Results", display=ms(v))
    v2 = seedv(s_, "micro_f1_all_test"); add(f"{cid}.all", f"micro-F1 {nm}, unseen gold labels counted as misses", float(v2.mean()), "mean +/- sd; variant all_test", CLSRC, RA, "RECOMPUTED", "Results", display=ms(v2))
    p = seedv(s_, "P@1"); add(f"{cid}.p1_seedmean", f"P@1 {nm}, mean of single seeds", float(p.mean()), "mean +/- sd of per-seed P@1", CLSRC, RA, "RECOMPUTED", "Results", display=ms(p))
    for s, x in zip(SEEDS, v): add(f"{cid}.s{s}", f"micro-F1 {nm} seed {s}", float(x), "notebook variant", CLSRC, RA, "RECOMPUTED", "Results")
svm = ps[ps.system == "TF-IDF + SVM"].iloc[0]
add("B3", "micro-F1 SVM", svm.micro_f1_notebook, "notebook variant; dev threshold; deterministic refit", "refit -> results/per_seed.csv", RA, "RECOMPUTED", "Results")
add("B3.macro117", "macro-F1 SVM (117 seen test labels)", svm.macro_f1_notebook, "macro over test labels seen in training", "refit -> results/per_seed.csv", RA, "RECOMPUTED", "Results")
add("B3.macro127", "macro-F1 SVM (all 127 test labels)", svm.macro_f1_all_test, "macro over all test labels; unseen labels score 0", "refit -> results/per_seed.csv", RA, "RECOMPUTED", "Results")
add("B3.thr", "SVM decision threshold", svm.threshold, "arg max of dev micro-F1 over np.arange(-0.6, 0.31, 0.05)", "refit -> results/per_seed.csv", RA, "RECOMPUTED", "Method", nd=2)
for cid, s_ in (("B4", "RoBERTa"), ("B5", "SecBERT")):
    a, b = seedv(s_, "macro_f1_notebook").mean(), seedv(s_, "macro_f1_all_test").mean()
    add(cid, f"macro-F1 {s_} (117 / 127 labels)", f"{a:.3f} / {b:.3f}", "3-seed mean; over seen test labels / over all test labels", CLSRC, RA, "RECOMPUTED", "Results")
    add(f"{cid}.117", f"macro-F1 {s_}, 117 labels", a, "3-seed mean, seen test labels", CLSRC, RA, "RECOMPUTED", "Results"); add(f"{cid}.127", f"macro-F1 {s_}, 127 labels", b, "3-seed mean, all test labels", CLSRC, RA, "RECOMPUTED", "Results")
def sysrow(cid, name, label, defin, source, extra=""):
    r = sy.loc[name]; add(cid, label, r["P@1"], defin, source + " -> results/systems.csv", RA, "RECOMPUTED", "Results", ci=(r["P@1_lo"], r["P@1_hi"]), note=extra)
    add(cid + ".mrr3", label.replace("P@1", "MRR@3"), r["MRR@3"], defin.replace("P@1", "MRR@3"), source + " -> results/systems.csv", RA, "RECOMPUTED", "Results", ci=(r["MRR@3_lo"], r["MRR@3_hi"]))
sysrow("B0", "Frequency prior", "P@1 frequency-prior baseline", "labels ranked by training frequency for every sentence; P@1 with 95% bootstrap CI", "train label counts")
sysrow("B6", "TF-IDF + SVM", "P@1 SVM", "share of test sentences whose top-1 label is gold", "refit")
sysrow("B7", "RoBERTa (3-seed avg)", "P@1 RoBERTa (3-seed probability average)", "P@1 of the mean probability of seeds 42-44 (an ensemble, not a seed mean)", "roberta_pw_s4{2,3,4}/test_probs.npy", "Single-seed mean is B1.p1_seedmean.")
sysrow("B8", "SecBERT (3-seed avg)", "P@1 SecBERT (3-seed probability average)", "P@1 of the mean probability of seeds 42-44 (an ensemble, not a seed mean)", "secbert_pw_s4{2,3,4}/test_probs.npy", "Single-seed mean is B2.p1_seedmean.")
sysrow("B9", "Classifiers-only ens.", "P@1 classifiers-only ensemble", "z-score sum of SVM, RoBERTa, SecBERT with equal weights", "saved predictions")
sysrow("B10a", "Matcher zero-shot", "P@1 bge zero-shot", "cosine of sentence and description embeddings, no training", "run_match_1/zeroshot/test_scores.npy")
v = seedv("Matcher ft20", "P@1"); add("B10b", "P@1 fine-tuned matcher (3 seeds)", float(v.mean()), "mean +/- sample sd over seeds 42-44", MSRC, RA, "RECOMPUTED", "Results", display=ms(v))
sysrow("B10c", "Matcher (3-seed ens.)", "P@1 matcher 3-seed ensemble", "mean cosine score of seeds 42-44", "run_match_1/ft20_s*/test_scores.npy")
eq42 = float(ps[ps.system == "Fusion equal (1,1,1,1) matcher s42"]["P@1"].iloc[0])
add("B11", "P@1 equal-weight fusion, matcher seed 42", eq42, "weights (1,1,1,1); matcher seed 42 only, classifiers 3-seed averages (as in Exp_2.1 CELL 8)", "saved predictions -> results/per_seed.csv", RA, "RECOMPUTED", "Results",
    note="Not like-for-like with B13a; use B11.avg for that.")
sysrow("B11.avg", "Fusion equal (1,1,1,1)", "P@1 equal-weight fusion, 3-seed matcher", "weights (1,1,1,1) with the same seed-averaged components as B13a", "saved predictions")
vp = seedv("Fusion (3,1,1,1) seed-paired", "P@1"); vm = seedv("Fusion (3,1,1,1) seed-paired", "MRR@3")
add("B12a", "P@1 fusion (3,1,1,1), seed-paired", float(vp.mean()), "matcher, RoBERTa and SecBERT all from seed s; mean +/- sd over s = 42, 43, 44", "saved predictions -> results/per_seed.csv", RA, "RECOMPUTED", "Results",
    display=ms(vp), note="Per seed: " + " / ".join(f"{x:.3f}" for x in vp) + ". This definition exists in no notebook.")
add("B12b", "MRR@3 fusion (3,1,1,1), seed-paired", float(vm.mean()), "as B12a", "saved predictions -> results/per_seed.csv", RA, "RECOMPUTED", "Results", display=ms(vm))
vn = seedv("Fusion (3,1,1,1) matcher seed varied", "P@1"); vnm = seedv("Fusion (3,1,1,1) matcher seed varied", "MRR@3")
add("B12nb", "P@1 fusion (3,1,1,1), notebook definition", float(vn.mean()), "matcher seed s with 3-seed-averaged classifiers; mean +/- sd over s (Exp_2.1 CELL 11, final_results_table.csv)", "saved predictions -> results/per_seed.csv", RA, "RECOMPUTED", "Results", display=ms(vn))
add("B12nb.mrr3", "MRR@3 fusion (3,1,1,1), notebook definition", float(vnm.mean()), "as B12nb", "saved predictions -> results/per_seed.csv", RA, "RECOMPUTED", "Results", display=ms(vnm))
r = sy.loc["Fusion (3,1,1,1)"]
add("B13a", "P@1 fusion (3,1,1,1), seed-averaged", r["P@1"], "all components averaged over seeds 42-44 before fusing; one system, 95% bootstrap CI over test sentences", "saved predictions -> results/systems.csv", RA, "RECOMPUTED", "Results", ci=(r["P@1_lo"], r["P@1_hi"]))
add("B13b", "MRR@3 fusion (3,1,1,1), seed-averaged", r["MRR@3"], "as B13a", "saved predictions -> results/systems.csv", RA, "RECOMPUTED", "Results", ci=(r["MRR@3_lo"], r["MRR@3_hi"]), note="Draft value 0.853 belongs to B12nb.mrr3.")
ws = R("weight_surface.csv"); s42 = ws[ws.matcher == "matcher_s42"]
def sel(g): x = s42[(s42.grid == g) & s42.dev_selected].iloc[0]; return x
def wstr(x): return f"({int(x.w_matcher)},{int(x.w_svm)},{int(x.w_roberta)},{int(x.w_secbert)})"
c_, w_ = sel("coarse_255"), sel("wide_1711"); r3111 = s42[(s42.grid == "wide_1711") & (s42.w_matcher == 3) & (s42.w_svm == 1) & (s42.w_roberta == 1) & (s42.w_secbert == 1)].iloc[0]
add("B14", "Fusion weights and the grid they come from", f"{wstr(c_)} = dev winner of the {int((s42.grid == 'coarse_255').sum())}-setting grid; the {int((s42.grid == 'wide_1711').sum()):,}-setting grid selects {wstr(w_)}",
    "selection by dev MRR@3 then dev P@1, matcher seed 42, order (matcher, SVM, RoBERTa, SecBERT)", "results/weight_surface.csv; Exp_2.1 CELL 8, 9, 11", RA, "RECOMPUTED", "Method",
    note=f"(3,1,1,1) is rank {int(r3111.dev_rank)} of {int((s42.grid == 'wide_1711').sum()):,} on the wide grid.")
add("B14.coarse_n", "Settings in the coarse grid", int((s42.grid == "coarse_255").sum()), "{0,1,2,3}^4 minus all-zero", "results/weight_surface.csv", RA, "RECOMPUTED", "Method")
add("B14.wide_n", "Settings in the wide grid", int((s42.grid == "wide_1711").sum()), "{0,1,2,3,4,6,8}^4 reduced by gcd", "results/weight_surface.csv", RA, "RECOMPUTED", "Method")
add("B14.rank3111", "Dev rank of (3,1,1,1) on the wide grid", int(r3111.dev_rank), "rank by dev MRR@3 then dev P@1", "results/weight_surface.csv", RA, "RECOMPUTED", "Method")
add("B14.test3111", "Test P@1 of (3,1,1,1), matcher seed 42", r3111["test_P@1"], "reported, never used for selection", "results/weight_surface.csv", RA, "RECOMPUTED", "Results")
add("B14.test4111", "Test P@1 of (4,1,1,1), matcher seed 42", w_["test_P@1"], "reported, never used for selection", "results/weight_surface.csv", RA, "RECOMPUTED", "Results")
for g, k in (("coarse_255", "B14.top10_coarse"), ("wide_1711", "B14.top10_wide")):
    t = s42[(s42.grid == g) & (s42.dev_rank <= 10)]["test_P@1"]
    add(k, f"Test P@1 range over the 10 best dev settings, {g}", f"{t.min():.3f} to {t.max():.3f}", "min and max test P@1 among the 10 best dev settings (matcher seed 42)", "results/weight_surface.csv", RA, "RECOMPUTED", "Sensitivity")
    add(k + ".spread", f"Test P@1 spread over the 10 best dev settings, {g}", float(t.max() - t.min()), "max minus min", "results/weight_surface.csv", RA, "RECOMPUTED", "Sensitivity")

# ================= C: statistics =================
cm = R("comparisons.csv").set_index("id"); labels = {"C1": "Fusion minus classifiers-only", "C2": "Fusion minus matcher ensemble", "C3": "RoBERTa minus SVM", "C4": "RoBERTa minus SecBERT",
    "A1": "Fusion minus fusion without matcher", "A2": "Fusion minus fusion without SVM", "A3": "Fusion minus fusion without RoBERTa", "A4": "Fusion minus fusion without SecBERT"}
for cid, r in cm.iterrows():
    pid = cid if cid.startswith("C") else "ABL." + cid
    add(pid, f"{labels[cid]}, delta P@1", r["delta_P@1"], f"paired bootstrap over 725 test sentences, 10,000 resamples, default_rng(20261114), percentile 95% CI", "results/comparisons.csv", RA, "RECOMPUTED", "Statistics",
        ci=(r.ci_lo, r.ci_hi), display=f"{r['delta_P@1']:+.3f}", note=f"supported under the pre-registered rule: {bool(r.supported)}")
    add(pid + ".p", f"{labels[cid]}, exact McNemar p", r.p_mcnemar, f"two-sided exact binomial on discordant pairs ({int(r.mcnemar_b)} vs {int(r.mcnemar_c)})", "results/comparisons.csv", RA, "RECOMPUTED", "Statistics")
    add(pid + ".holm", f"{labels[cid]}, Holm-adjusted p", r.p_holm, f"Holm step-down over the family of {int(r.family_size)} tests (prereg 01)", "results/comparisons.csv", RA, "RECOMPUTED", "Statistics")
    add(pid + ".mrr", f"{labels[cid]}, delta MRR@3", r["delta_MRR@3"], "paired bootstrap, as above", "results/comparisons.csv", RA, "RECOMPUTED", "Statistics", ci=(r.mrr_ci_lo, r.mrr_ci_hi), display=f"{r['delta_MRR@3']:+.3f}")
ab = R("ablation.csv")
for _, r in ab.iterrows():
    k = "ABL.full" if r.system == "Fusion (3,1,1,1)" else "ABL.no_" + r.system.split()[-1].lower()
    add(k, f"P@1 {r.system}", r["mean"], "seed-averaged components; one weight set to 0", "results/ablation.csv", RA, "RECOMPUTED", "Ablation", ci=(r.lo, r.hi))

# ================= D: human study =================
H = pd.read_csv(EVIDENCE / "07_agreement.csv").set_index("statistic")["value"]; HS = "Exp_3_0_shap/hand_check_v2_*.xlsx -> _evidence_pack/07_agreement.csv"; T7 = "_evidence_pack/scripts/t7_human.py"
for cid, key, lab in (("D1", "Krippendorff alpha nominal (A,B; 100 rows)", "Krippendorff alpha, nominal"), ("D2", "Krippendorff alpha ordinal (A,B; 100 rows)", "Krippendorff alpha, ordinal"),
                      ("D3", "Fleiss kappa (A,B; 100 rows)", "Fleiss kappa"), ("D4", "Cohen kappa unweighted (A,B)", "Cohen kappa, unweighted"),
                      ("D4.lin", "Cohen kappa linear-weighted (A,B)", "Cohen kappa, linear weights"), ("D6", "Percent agreement exact (A,B)", "Exact agreement between the two full raters")):
    add(cid, lab, float(H[key]), "two raters, 100 sentences, scale 0-2", HS, T7, "RECOMPUTED", "Human study", display=f"{float(H[key]):+.3f}" if cid != "D6" else f"{float(H[key]):.2f}")
add("D5", "Sentences rated by the third rater", 3, "rated rows in the third rating sheet (of 100)", HS, T7, "RECOMPUTED", "Human study")
add("D4.ci", "Cohen kappa 95% CI", H["Cohen kappa unweighted 95% CI (2000 resamples, RandomState(42))"], "percentile bootstrap, 2,000 resamples of sentences", HS, T7, "RECOMPUTED", "Human study")

# ================= E: explainability =================
d = pd.read_csv(EVIDENCE / "06_deletion_test_725.csv")
def dsum(x): diff = x.drop_top_mask - x.drop_random_mask; return float(diff.mean()), int((diff > 0).sum()), int(len(x))
f100 = d[d.in_first_100 & d.used.astype(bool) & ~d.truncated.astype(bool)]; fall = d[d.used.astype(bool) & ~d.truncated.astype(bool)]
m1, k1, n1 = dsum(f100); m2, k2, n2 = dsum(fall)
rec0 = json.loads(open(SHAP_DIR / "shap_v2_roberta_pw_s42.jsonl", encoding="utf-8").readline()); nrec = sum(1 for l in open(SHAP_DIR / "shap_v2_roberta_pw_s42.jsonl", encoding="utf-8") if l.strip())
add("E1", "SHAP settings", f"{rec0['method']['algorithm']} SHAP, {rec0['method']['n_perm']} permutations, model roberta_pw_s42, {nrec} sentences", "method block stored with every record: " + json.dumps(rec0["method"]),
    "Exp_3_0_shap/shap_v2_roberta_pw_s42.jsonl; Exp_3_0b CELL 2", "_evidence_pack/scripts/t6_shap.py", "VERIFIED", "Explainability")
add("E1.n", "Sentences with stored SHAP values", nrec, "records in the SHAP file", "Exp_3_0_shap/shap_v2_roberta_pw_s42.jsonl", "_evidence_pack/scripts/t6_shap.py", "VERIFIED", "Explainability")
add("E2", "Deletion test: top-3 minus random-3 drop (logits), 100-sentence sample", m1, "mean over eligible sentences of [logit drop after masking the 3 highest-SHAP words] - [mean drop over 20 random 3-word sets]; top-1 label logit",
    "_evidence_pack/06_deletion_test_725.csv (rows in_first_100)", "_evidence_pack/scripts/t6_shap.py", "RECOMPUTED", "Explainability", nd=2)
add("E3", "Sentences where top-3 drop exceeds random drop, 100-sentence sample", f"{k1} / {n1}", "count / eligible (at least 6 words, at least 3 positive SHAP words, not truncated)", "_evidence_pack/06_deletion_test_725.csv", "_evidence_pack/scripts/t6_shap.py", "RECOMPUTED", "Explainability")
add("E3.n", "Eligible sentences in the 100-sentence sample", n1, "100 sampled minus short/too-few-positive minus truncated", "_evidence_pack/06_deletion_test_725.csv", "_evidence_pack/scripts/t6_shap.py", "RECOMPUTED", "Explainability")
add("E2.all", "Deletion test difference on all eligible test sentences", m2, "as E2, all test sentences", "_evidence_pack/06_deletion_test_725.csv", "_evidence_pack/scripts/t6_shap.py", "RECOMPUTED", "Explainability", nd=2)
add("E3.all", "Top-3 larger than random, all eligible test sentences", f"{k2} / {n2}", "as E3, all test sentences", "_evidence_pack/06_deletion_test_725.csv", "_evidence_pack/scripts/t6_shap.py", "RECOMPUTED", "Explainability")
ev = R("explained_vs_fusion.csv").iloc[0]
add("E4", "Test sentences where the explained model and the fusion output different top-1 labels", int(ev.different_top1), "roberta_pw_s42 top-1 vs seed-averaged fusion top-1", "results/explained_vs_fusion.csv", RA, "RECOMPUTED", "Explainability",
    display=f"{int(ev.different_top1)} of {int(ev.n)} ({ev.share_different:.1%})")
add("E4.share", "Share of test sentences with different top-1 labels", float(ev.share_different), "see E4", "results/explained_vs_fusion.csv", RA, "RECOMPUTED", "Explainability")
if (RESULTS / "faithfulness_summary.csv").exists():
    fs = R("faithfulness_summary.csv"); keys = ["E5.del_auc", "E5.ins_auc", "E5.comp_prob", "E5.suff_prob", "E5.comp_logit", "E5.suff_logit"]
    for k, (_, r) in zip(keys, fs.iterrows()):
        add(k, f"Faithfulness: {r.measure}, SHAP minus random", r.delta, f"paired difference SHAP order vs mean of 5 random orders; n = {int(r.n)} eligible sentences of the fixed 100-sentence sample; SHAP {r.shap:.3f}, random {r['random']:.3f}",
            "results/faithfulness_summary.csv", RI, "RECOMPUTED", "Explainability", ci=(r.ci_lo, r.ci_hi), display=f"{r.delta:+.3f}", note=f"supported (prereg 06): {bool(r.supported)}; SHAP better in {int(r.shap_better_in)} of {int(r.n)}")
        add(k + ".shap", f"{r.measure}: SHAP order", r.shap, "mean over eligible sentences", "results/faithfulness_summary.csv", RI, "RECOMPUTED", "Explainability")
        add(k + ".random", f"{r.measure}: random order", r["random"], "mean over eligible sentences", "results/faithfulness_summary.csv", RI, "RECOMPUTED", "Explainability")
    add("E5.n", "Sentences in the faithfulness analysis", int(fs.n.iloc[0]), "eligible sentences among the first 100 of the fixed permutation", "results/faithfulness.csv", RI, "RECOMPUTED", "Explainability")
p11 = EVIDENCE / "11_fusion_shap.md"
if p11.exists():
    t = p11.read_text(encoding="utf-8")
    m = re.search(r"top-3 by SHAP of the fused score \| ([\d.]+)", t); m2_ = re.search(r"top-3 by the stored RoBERTa-only SHAP \| ([\d.]+)", t); m3 = re.search(r"Eligible sentences: (\d+)", t)
    add("E6.partial", "Partial-fusion SHAP (no matcher): drop of the fused score, fused-SHAP vs RoBERTa-SHAP top-3", f"{m.group(1)} vs {m2_.group(1)} (n = {m3.group(1)})",
        "classifier components only (SVM + RoBERTa s42 + SecBERT s42), 40 fixed sentences; z-score sum of the fused top-1 label", "_evidence_pack/11_fusion_shap.md", "_evidence_pack/scripts/x1_fusion_shap.py, x2_fusion_shap_summary.py", "RECOMPUTED", "Explainability",
        note="Matcher excluded (weights never saved); not the full fusion.")

# ================= F: baseline =================
fr = pd.read_csv(MATCH_DIR / "final_results_table.csv"); pr = fr[fr.model.str.startswith("Paper")].iloc[0]
add("F1", "Published baseline P@1 (Nguyen et al., TRAM, 'Asymmetric')", float(pr["P@1"]), "constant typed into the notebooks from the paper; confirmed against arXiv:2401.10337 Table 2 (not a project file); not re-run",
    "run_match_1/final_results_table.csv; _evidence_pack/08_baseline.md", "(none: copied constant)", "NOTES-ONLY", "Baseline", note="Split and training-mode comparability UNKNOWN.")
add("F2", "Published baseline MRR@3", float(pr["MRR@3"]), "as F1", "run_match_1/final_results_table.csv; _evidence_pack/08_baseline.md", "(none: copied constant)", "NOTES-ONLY", "Baseline")

# ================= G: new analyses =================
for _, r in fv[fv.system == "Frequency prior"].iterrows():
    add(f"G1.prior_microf1_{r.variant}", f"Frequency prior micro-F1 ({r.variant})", r.micro_f1, "always predict the most frequent training label", "results/f1_variants.csv", RA, "RECOMPUTED", "Baselines")
for nm in ("RoBERTa", "SecBERT", "TF-IDF + SVM"):
    x = fv[fv.system == nm]
    for v in ("notebook", "seen_test", "all_test"):
        y = x[x.variant == v]; key = nm.split()[0].lower().replace("tf-idf", "svm")
        add(f"G2.{key}.micro.{v}", f"micro-F1 {nm}, variant {v}", float(y.micro_f1.mean()), "mean over seeds (single run for SVM); see docs/THESIS_MAP for the three variants", "results/f1_variants.csv", RA, "RECOMPUTED", "Results")
        add(f"G2.{key}.macro.{v}", f"macro-F1 {nm}, variant {v}", float(y.macro_f1.mean()), "mean over seeds", "results/f1_variants.csv", RA, "RECOMPUTED", "Results")
tg = R("threshold_grid.csv")
for tag in ("roberta", "secbert"):
    x = tg[tg.model == tag]
    add(f"G3.{tag}.thr_old", f"{tag} dev thresholds, original grid", " / ".join(f"{v:.2f}" for v in x.thr_original_grid), "grid 0.10-0.85 step 0.05, seeds 42-44", "results/threshold_grid.csv", RA, "RECOMPUTED", "Sensitivity")
    add(f"G3.{tag}.thr_new", f"{tag} dev thresholds, extended grid", " / ".join(f"{v:.2f}" for v in x.thr_extended_grid), "grid 0.10-0.99 step 0.01, seeds 42-44", "results/threshold_grid.csv", RA, "RECOMPUTED", "Sensitivity")
    dl = (x.test_micro_f1_extended - x.test_micro_f1_original)
    add(f"G3.{tag}.delta", f"{tag} test micro-F1 change with the extended threshold grid", float(dl.mean()), "mean over seeds of (extended - original); threshold chosen on dev", "results/threshold_grid.csv", RA, "RECOMPUTED", "Sensitivity", display=f"{dl.mean():+.4f}",
        note="per seed: " + " / ".join(f"{v:+.4f}" for v in dl))
sb = R("support_buckets.csv"); short = {"TF-IDF + SVM": "svm", "RoBERTa (3-seed avg)": "roberta", "SecBERT (3-seed avg)": "secbert", "Matcher (3-seed ens.)": "matcher", "Fusion (3,1,1,1)": "fusion"}
for _, r in sb.iterrows():
    b = r.bucket.replace("+", "plus").replace("-", "_")
    add(f"G4.{short[r.system]}.{b}", f"P@1 {r.system}, rarest gold label train support {r.bucket}", r["P@1"], f"test sentences whose rarest gold label has train support {r.bucket}; n = {int(r.n_sentences)}; 95% bootstrap CI",
        "results/support_buckets.csv", RA, "RECOMPUTED", "Error analysis", ci=(r.lo, r.hi))
for b in sb.bucket.unique(): add(f"G4.n.{b.replace('+', 'plus').replace('-', '_')}", f"Test sentences in support bucket {b}", int(sb[sb.bucket == b].n_sentences.iloc[0]), "see G4", "results/support_buckets.csv", RA, "RECOMPUTED", "Error analysis")
fb = R("fixed_broken.csv")
for _, r in fb.iterrows():
    ref = "matcher" if r.reference.startswith("Matcher") else "clsonly"; b = r.bucket.replace("+", "plus").replace("-", "_")
    add(f"G5.{ref}.{b}", f"Fusion minus {r.reference}, support {r.bucket}", r["delta_P@1"], f"paired delta P@1 with 95% bootstrap CI; n = {int(r.n)}; fixed {int(r.fixed)}, broken {int(r.broken)}", "results/fixed_broken.csv", RA, "RECOMPUTED", "Error analysis",
        ci=(r.ci_lo, r.ci_hi), display=f"{r['delta_P@1']:+.3f}")
for ref, k in (("Matcher (3-seed ens.)", "matcher"), ("Classifiers-only ens.", "clsonly")):
    x = fb[fb.reference == ref]; add(f"G5.{k}.total", f"Sentences fixed / broken by the fusion vs {ref}", f"{int(x.fixed.sum())} / {int(x['broken'].sum())}", "fusion right & reference wrong / fusion wrong & reference right", "results/fixed_broken.csv", RA, "RECOMPUTED", "Error analysis")
un = sy["unseen_R@5"]
add("G6.unseen_r5_fusion", "Unseen-label R@5, fusion", float(un["Fusion (3,1,1,1)"]), "share of the 10 unseen gold (sentence, label) pairs found in the top 5", "results/systems.csv", RA, "RECOMPUTED", "Error analysis", nd=2)
add("G6.unseen_r5_clsonly", "Unseen-label R@5, classifiers-only", float(un["Classifiers-only ens."]), "as above; classifiers cannot output unseen labels", "results/systems.csv", RA, "RECOMPUTED", "Error analysis", nd=2)
add("G6.unseen_r5_matcher", "Unseen-label R@5, matcher ensemble", float(un["Matcher (3-seed ens.)"]), "as above", "results/systems.csv", RA, "RECOMPUTED", "Error analysis", nd=2)
ca = R("calibration.csv")
for tag in ("roberta", "secbert"):
    x = ca[ca.model == tag]; add(f"G7.ece.{tag}", f"ECE {tag} (3 seeds)", float(x.ECE.mean()), "10 equal-width bins; confidence = probability of the top-1 label; mean +/- sd over seeds", "results/calibration.csv", RA, "RECOMPUTED", "Calibration", display=ms(x.ECE.to_numpy()))
    add(f"G7.conf.{tag}", f"Mean top-1 confidence {tag}", float(x.mean_confidence.mean()), "mean over seeds", "results/calibration.csv", RA, "RECOMPUTED", "Calibration")
psb = R("parent_sub.csv")
for k_, s_ in short.items():
    x = psb[psb.system == k_]; fam_ = x[x.relation.isin(["predicted the parent", "predicted a sub-technique", "sibling sub-technique"])]
    add(f"G8.family_errors.{s_}", f"{k_}: errors inside the gold label's technique family", f"{int(fam_.errors.sum())} of {int(x.total_errors.iloc[0])}", "wrong top-1 that is the parent, a sub-technique or a sibling of a gold label / all wrong top-1", "results/parent_sub.csv", RA, "RECOMPUTED", "Error analysis")
    add(f"G8.techlevel.{s_}", f"{k_}: technique-level P@1", float(x[x.relation.str.startswith("technique-level")].share.iloc[0]), "prediction and gold reduced to the parent technique", "results/parent_sub.csv", RA, "RECOMPUTED", "Error analysis")
sa = R("support_aware_v2.csv").iloc[0]; sf = R("support_aware_family.csv"); s1 = R("support_aware_fusion.csv").iloc[0]
add("G9.v2.weights", "Support-aware fusion v2: dev-selected matcher weights (unseen, 1-4, 5-19, 20+)", f"({int(sa.selected_w_unseen)}, {int(sa.selected_w_rare)}, {int(sa.selected_w_mid)}, {int(sa.selected_w_frequent)})", "prereg 13; 1,296 dev settings", "results/support_aware_v2.csv", "scripts/run_support_aware_v2.py", "RECOMPUTED", "Extension")
add("G9.v2.p1", "Support-aware fusion v2: test P@1", sa["test_P@1"], "single test evaluation of the dev-selected setting", "results/support_aware_v2.csv", "scripts/run_support_aware_v2.py", "RECOMPUTED", "Extension")
add("G9.v2.rare", "Support-aware fusion v2: P@1 on rare-label sentences (support 0-4)", sa["rare_P@1"], f"n = {int(sa.rare_n)}; baseline (3,1,1,1) = {sa['rare_P@1_baseline']:.3f}", "results/support_aware_v2.csv", "scripts/run_support_aware_v2.py", "RECOMPUTED", "Extension", ci=None)
add("G9.v2.rare_base", "Fusion (3,1,1,1): P@1 on rare-label sentences (support 0-4)", sa["rare_P@1_baseline"], f"n = {int(sa.rare_n)}", "results/support_aware_v2.csv", "scripts/run_support_aware_v2.py", "RECOMPUTED", "Extension")
add("G9.v2.success", "Support-aware fusion v2: pre-registered success rule met", str(bool(sa.success_rule_met)), "Holm p < 0.05 vs (3,1,1,1), CI excluding 0, and rare-bucket P@1 rises", "results/support_aware_v2.csv", "scripts/run_support_aware_v2.py", "RECOMPUTED", "Extension")
for i, r in sf.iterrows():
    add(f"G9.fam{i + 1}", f"{r.comparison}: delta P@1", r["delta_P@1"], f"paired bootstrap CI; exact McNemar p = {r.p_mcnemar:.3f}; Holm p = {r.p_holm:.3f} (family of {int(r.family_size)})", "results/support_aware_family.csv", "scripts/run_support_aware_v2.py", "RECOMPUTED", "Extension",
        ci=(r.ci_lo, r.ci_hi), display=f"{r['delta_P@1']:+.3f}")
    add(f"G9.fam{i + 1}.holm", f"{r.comparison}: Holm-adjusted p", r.p_holm, "see above", "results/support_aware_family.csv", "scripts/run_support_aware_v2.py", "RECOMPUTED", "Extension")
add("G9.v1.weights", "Support-aware fusion v1 (three bands): dev-selected matcher weights", f"({int(s1.selected_w_rare)}, {int(s1.selected_w_mid)}, {int(s1.selected_w_frequent)})", "prereg 09; bands 0-4, 5-19, 20+", "results/support_aware_fusion.csv", RA, "RECOMPUTED", "Extension",
    note="A uniform result means dev did not prefer support-dependent weights.")
if (RESULTS / "efficiency.csv").exists():
    ef = R("efficiency.csv")
    for _, r in ef.iterrows():
        k = r.system.split()[0].lower().replace("tf-idf", "svm")
        if pd.notna(r.parameters): add(f"G10.params.{k}", f"Parameters, {r.system}", int(r.parameters), str(r.note), "results/efficiency.csv", RI, "RECOMPUTED", "Efficiency")
        if pd.notna(r.median_ms): add(f"G10.ms.{k}", f"Median CPU latency per sentence, {r.system} (ms)", r.median_ms, f"batch size 1, 100 sentences after 5 warm-up; p90 = {r.p90_ms:.1f} ms; timed with: {r.timed_with}; hardware in results/hardware.json",
                                    "results/efficiency.csv", RI, "RECOMPUTED", "Efficiency", nd=1)
if (RESULTS / "maxlen.csv").exists():
    for _, r in R("maxlen.csv").iterrows():
        k = r.model.split("_")[0]
        add(f"G11.{k}", f"{r.model}: hits on the truncated sentences, 128 vs 256 tokens at inference", f"{int(r.hits_128)} vs {int(r.hits_256)} of {int(r.n)}", f"inference only (model trained at 128); gained {int(r.gained)}, lost {int(r.lost)}, exact McNemar p = {r.p_mcnemar:.3f}",
            "results/maxlen.csv", RI, "RECOMPUTED", "Sensitivity")

ov = R("overlap_sensitivity.csv"); base_ = ov[ov.removed == "none"].set_index("system")
for rem in ("exact", "exact+near"):
    x = ov[ov.removed == rem].set_index("system"); dmax = float((x["P@1"] - base_["P@1"]).abs().max()); k = rem.replace("+", "_")
    add(f"G12.{k}.n", f"Test sentences removed ({rem} overlap with train)", int(x.n_removed.iloc[0]), f"test ids {x.removed_test_ids.iloc[0]}", "results/overlap_sensitivity.csv", RA, "RECOMPUTED", "Data")
    add(f"G12.{k}.maxdelta", f"Largest change in any system's P@1 after removing the {rem} overlap", dmax, "max over 6 systems of |P@1 without overlap - P@1 with all 725|", "results/overlap_sensitivity.csv", RA, "RECOMPUTED", "Data", nd=4)

for sysn, k in (("Fusion (3,1,1,1)", "fusion"), ("RoBERTa (3-seed avg)", "roberta"), ("SecBERT (3-seed avg)", "secbert"), ("TF-IDF + SVM", "svm"), ("Matcher (3-seed ens.)", "matcher")):
    x = ov[ov.system == sysn].set_index("removed")
    add(f"G12.p1.{k}", f"P@1 {sysn}: all 725 test sentences vs without the exact+near overlap", f"{x.loc['none', 'P@1']:.4f} vs {x.loc['exact+near', 'P@1']:.4f}", "P@1 on 725 sentences vs on 723 (test ids 59 and 124 removed)",
        "results/overlap_sensitivity.csv", RA, "RECOMPUTED", "Data", note=f"exact only (724 sentences): {x.loc['exact', 'P@1']:.4f}")
# spreads of macro-F1 over seeds, both label scopes
for cid, s_ in (("B4", "RoBERTa"), ("B5", "SecBERT")):
    for scope, col in (("117", "macro_f1_notebook"), ("127", "macro_f1_all_test")):
        v = seedv(s_, col); add(f"{cid}.{scope}.sd", f"macro-F1 {s_}, {scope} labels, mean +/- sd", float(v.mean()), "sample sd over seeds 42-44", CLSRC, RA, "RECOMPUTED", "Results", display=ms(v))
for s_, k in (("RoBERTa", "roberta"), ("SecBERT", "secbert")):
    d_ = seedv(s_, "micro_f1_notebook").mean() - seedv(s_, "micro_f1_all_test").mean()
    add(f"G2.{k}.micro_drop", f"micro-F1 {s_}: drop when unseen gold labels count as misses", float(d_), "3-seed mean of (notebook variant - all_test variant)", "results/per_seed.csv", RA, "RECOMPUTED", "Results", nd=4)
add("B1.minus_svm", "micro-F1 RoBERTa (3-seed mean) minus SVM", float(seedv("RoBERTa", "micro_f1_notebook").mean() - svm.micro_f1_notebook), "difference of B1 and B3", "results/per_seed.csv", RA, "RECOMPUTED", "Results")
add("A7.roberta_pct", "Share of test sentences truncated at 128 tokens (RoBERTa)", tr_r / n["test"], "A7.roberta / test sentences", "_evidence_pack/01_truncated_test_ids.csv", T1, "RECOMPUTED", "Data", display=f"{100 * tr_r / n['test']:.1f}%")
for sysn, k in short.items():                                   # merged 5-19 bucket used by the draft's table (exact: n-weighted mean of two exact means)
    x = sb[(sb.system == sysn) & sb.bucket.isin(["5-9", "10-19"])]
    add(f"G4.{k}.5_19", f"P@1 {sysn}, rarest gold label train support 5-19", float((x["P@1"] * x.n_sentences).sum() / x.n_sentences.sum()),
        f"n-weighted mean of buckets 5-9 and 10-19; n = {int(x.n_sentences.sum())}; no CI (merged after the fact)", "results/support_buckets.csv", RA, "RECOMPUTED", "Error analysis")
b59 = sb[sb.bucket.isin(["5-9", "10-19"])].drop_duplicates("bucket").n_sentences.sum()
add("G4.n.5_19", "Test sentences in support buckets 5-9 and 10-19 together", int(b59), "sum of the two bucket sizes", "results/support_buckets.csv", RA, "RECOMPUTED", "Error analysis")
comb = pd.read_csv(ROOT / "Dataset" / "combined_train.csv")
add("A10.combined_rows", "Rows in the combined training collection", int(len(comb)), "rows of combined_train.csv (three sources)", "Dataset/combined_train.csv", "scripts/build_numbers.py", "RECOMPUTED", "Data")
import ast as _ast
add("A10.combined_labels", "Distinct labels in the combined training collection", int(len({t for x in comb["labels"] for t in _ast.literal_eval(x)})), "distinct technique ids over all rows", "Dataset/combined_train.csv", "scripts/build_numbers.py", "RECOMPUTED", "Data")
for src_, cnt_ in comb.source_dataset.value_counts().items(): add(f"A10.rows.{src_}", f"Rows from source '{src_}'", int(cnt_), "value counts of source_dataset", "Dataset/combined_train.csv", "scripts/build_numbers.py", "RECOMPUTED", "Data")
# earlier 15-epoch configuration and the pw / nopw choice (stored metrics.json, VERIFIED)
for tag in ("roberta", "secbert"):
    v = [json.load(open(ROOT / "runs_tram_1.1_epoch_15" / f"{tag}_s{s}" / "metrics.json"))["test"]["micro_f1"] for s in SEEDS]
    add(f"H1.{tag}_15ep", f"micro-F1 {tag}, earlier 15-epoch configuration (3 seeds)", float(np.mean(v)), "stored test micro-F1, mean +/- sd over seeds 42-44", "runs_tram_1.1_epoch_15/*/metrics.json", "scripts/build_numbers.py", "VERIFIED", "Method", display=ms(np.array(v)))
for var in ("pw", "nopw"):
    m_ = json.load(open(ROOT / "Exp_1_4_run_tram_2_epoc_30" / f"roberta_{var}_s42" / "metrics.json"))
    add(f"H2.roberta_{var}_dev", f"RoBERTa seed 42, {'with' if var == 'pw' else 'without'} positive weight: best dev micro-F1", m_["dev_best_micro_f1"], "stored dev_best_micro_f1", f"Exp_1_4_run_tram_2_epoc_30/roberta_{var}_s42/metrics.json", "scripts/build_numbers.py", "VERIFIED", "Method")
    add(f"H2.roberta_{var}_test", f"RoBERTa seed 42, {'with' if var == 'pw' else 'without'} positive weight: test micro-F1", m_["test"]["micro_f1"], "stored test micro_f1", f"Exp_1_4_run_tram_2_epoc_30/roberta_{var}_s42/metrics.json", "scripts/build_numbers.py", "VERIFIED", "Method")
ra_ = pd.read_csv(SHAP_DIR / "rater_agreement_v2_roberta_pw_s42.csv"); rc_ = [c for c in ra_.columns if c.startswith("rating_")]
sh = sorted(float((ra_[c] == 2).mean()) for c in rc_)
add("D7.raterA_2", "Rater A: share of explanations rated 2 (makes sense)", sh[0], "share of the 100 sentences rated 2 by the rater with the lower share", "Exp_3_0_shap/rater_agreement_v2_roberta_pw_s42.csv", "scripts/build_numbers.py", "RECOMPUTED", "Human study", display=f"{100 * sh[0]:.0f}%")
add("D7.raterB_2", "Rater B: share of explanations rated 2 (makes sense)", sh[1], "share of the 100 sentences rated 2 by the rater with the higher share", "Exp_3_0_shap/rater_agreement_v2_roberta_pw_s42.csv", "scripts/build_numbers.py", "RECOMPUTED", "Human study", display=f"{100 * sh[1]:.0f}%")

# ================= M: Q1 plan Task 1 (explainer): R@5, matcher variants, averaged-matcher weight grid =================
RMV = "scripts/run_matcher_variants.py"
for cid, name in (("B6", "TF-IDF + SVM"), ("B7", "RoBERTa (3-seed avg)"), ("B8", "SecBERT (3-seed avg)"), ("B9", "Classifiers-only ens."), ("B10a", "Matcher zero-shot"),
                  ("B10c", "Matcher (3-seed ens.)"), ("B11.avg", "Fusion equal (1,1,1,1)")):
    add(f"{cid}.r5", f"R@5 {name}", sy.loc[name]["R@5_micro"], "gold (sentence, label) pairs found in the top 5 / all gold pairs", "saved predictions -> results/systems.csv", RA, "RECOMPUTED", "Results")
add("B13c", "R@5 fusion (3,1,1,1), seed-averaged", sy.loc["Fusion (3,1,1,1)"]["R@5_micro"], "as B6.r5", "saved predictions -> results/systems.csv", RA, "RECOMPUTED", "Results")
add("B13a.halfwidth", "Half-width of the 95% CI of fusion P@1", (sy.loc["Fusion (3,1,1,1)"]["P@1_hi"] - sy.loc["Fusion (3,1,1,1)"]["P@1_lo"]) / 2,
    "(hi - lo) / 2 of B13a: how much a P@1 on 725 test sentences moves by chance", "results/systems.csv", RA, "RECOMPUTED", "Results")
mv = R("matcher_variants.csv"); mv["seed"] = mv["seed"].astype(str)
def mvr(v, s, sysn="matcher"): return mv[(mv.variant == v) & (mv.seed == s) & (mv.system == sysn)].iloc[0]
MSRC2 = "run_match_1/<variant>/test_scores.npy, metrics.json -> results/matcher_variants.csv"
x = mvr("ft8", "42")
add("M1.ft8.p1", "P@1 matcher, 8-epoch budget, seed 42 only", x["P@1"], "fine-tuned bge, epochs 8, patience 3; one seed", MSRC2, RMV, "RECOMPUTED", "Results", ci=(x["P@1_lo"], x["P@1_hi"]))
add("M1.ft8.mrr3", "MRR@3 matcher, 8-epoch budget, seed 42 only", x["MRR@3"], "as M1.ft8.p1", MSRC2, RMV, "RECOMPUTED", "Results")
add("M1.ft8.epochs", "Epoch budget / patience of the 8-epoch matcher run", f"{int(x.epochs)} / {int(x.patience)}", "config.epochs / config.patience of run_match_1/ft_s42", MSRC2, RMV, "RECOMPUTED", "Method")
x = mvr("ft20", "ens")
add("M1.ft20.best_epochs", "Best dev epoch of the 20-epoch matcher, seeds 42 / 43 / 44", x["best_epoch"], "epoch with the best dev MRR@3 (early stopping)", MSRC2, RMV, "RECOMPUTED", "Method")
add("M1.ft20.budget", "Epoch budget / patience of the 20-epoch matcher runs", f"{int(x.epochs)} / {int(x.patience)}", "config.epochs / config.patience of run_match_1/ft20_s*", MSRC2, RMV, "RECOMPUTED", "Method")
add("M1.n_neg", "Random negative labels per batch (matcher training)", int(x.n_neg), "config.n_neg of run_match_1/ft20_s*", MSRC2, RMV, "RECOMPUTED", "Method")
u = mv[(mv.variant == "ft20") & (mv.seed.isin([str(s) for s in SEEDS]))]["unseen_R@5"].to_numpy()
add("M1.ft20.unseen_r5_seeds", "Unseen-label R@5 of the 20-epoch matcher over seeds", float(u.mean()), "mean +/- sample sd over seeds 42-44 (10 unseen gold pairs)", MSRC2, RMV, "RECOMPUTED", "Results", display=ms(u))
for k, sysn in (("M1.L256", "matcher"), ("M1.L256.fusion", "fusion (3,1,1,1)")):
    x = mvr("ft20L256", "ens", sysn); lab = "matcher with 256-token descriptions, 3-seed ens." if sysn == "matcher" else "fusion (3,1,1,1) with the 256-token matcher"
    add(f"{k}.p1", f"P@1 {lab}", x["P@1"], "descriptions truncated at 256 instead of 128 tokens in training and scoring", MSRC2, RMV, "RECOMPUTED", "Results", ci=(x["P@1_lo"], x["P@1_hi"]))
    add(f"{k}.mrr3", f"MRR@3 {lab}", x["MRR@3"], "as above", MSRC2, RMV, "RECOMPUTED", "Results")
    add(f"{k}.unseen_r5", f"Unseen-label R@5, {lab}", x["unseen_R@5"], "as G6", MSRC2, RMV, "RECOMPUTED", "Results", nd=2)
wa = ws[ws.matcher == "matcher_avg"]
for g, k in (("coarse_255", "B14.avg_coarse"), ("wide_1711", "B14.avg_wide")):
    xa = wa[(wa.grid == g) & wa.dev_selected].iloc[0]
    add(k, f"Dev-selected weights, seed-averaged matcher, {g}", wstr(xa), "selection by dev MRR@3 then dev P@1; matcher = mean of seeds 42-44", "results/weight_surface.csv", RA, "RECOMPUTED", "Method")
    add(k + ".test", f"Test P@1 of the dev-selected weights, seed-averaged matcher, {g}", xa["test_P@1"], "reported, never used for selection", "results/weight_surface.csv", RA, "RECOMPUTED", "Sensitivity")

if (RESULTS / "attack_version.csv").exists():
    av = R("attack_version.csv").iloc[0]; AVS, AVC = "Dataset/ttp-desc-mappings.csv vs _evidence_pack/external/enterprise-attack-12.1.json -> results/attack_version.csv", "scripts/check_attack_version.py"
    add("A11", "ATT&CK release of the description file", f"technique-id set {'identical to' if av.id_set_equal else 'differs from'} Enterprise v{av.stix_version} ({int(av.file_ids)} ids); texts close but not identical",
        "no version string is stored in the data; inferred from the id set and the description texts", AVS, AVC, "RECOMPUTED", "Data")
    add("A11.sim_median", "Median text similarity of the descriptions to ATT&CK v12.1", av.text_similarity_median, "difflib ratio after removing citations, links and punctuation", AVS, AVC, "RECOMPUTED", "Data")
    add("A11.sim_lt_080", "Descriptions with similarity below 0.80 to ATT&CK v12.1", int(av.text_sim_lt_0_80) if "text_sim_lt_0_80" in av else int(av["text_sim_lt_0.80"]), "count of 737", AVS, AVC, "RECOMPUTED", "Data")

# ================= Q: Q1 plan Tasks 3-7 (each block runs only once its result file exists) =================
def famrow(f, rid, lab, a, b, src, script, sec):
    x = f[(f.iloc[:, 0] == a) & (f.iloc[:, 1] == b)].iloc[0]
    add(rid, lab, x["delta_P@1"], f"paired bootstrap CI; exact McNemar p = {x['p_mcnemar']:.3f}; Holm p = {x['p_holm']:.3f} (family of {int(x['family_size'])})", src, script, "RECOMPUTED", sec,
        ci=(x["ci_lo"], x["ci_hi"]), display=f"{x['delta_P@1']:+.3f}")
    add(rid + ".holm", lab.replace("delta P@1", "Holm-adjusted p"), x["p_holm"], "see " + rid, src, script, "RECOMPUTED", sec)
if (RESULTS / "stacking.csv").exists():
    st = R("stacking.csv").set_index("system"); sf = R("stacking_family.csv"); sb = R("stacking_buckets.csv"); sm = json.loads((RESULTS / "stacking_model.json").read_text())
    SS, SSC = "results/stacking.csv, stacking_family.csv, stacking_buckets.csv", "scripts/run_stacking.py"
    x = st.loc["Stacked fusion (LR)"]
    add("ST1.p1", "P@1 stacked fusion (logistic regression fitted on dev)", x["P@1"], "prereg 15; 7 features per (sentence, label); C by 5-fold dev CV", SS, SSC, "RECOMPUTED", "Results", ci=(x["P@1_lo"], x["P@1_hi"]))
    add("ST1.mrr3", "MRR@3 stacked fusion", x["MRR@3"], "as ST1.p1", SS, SSC, "RECOMPUTED", "Results", ci=(x["MRR@3_lo"], x["MRR@3_hi"]))
    add("ST1.r5", "R@5 stacked fusion", x["R@5_micro"], "as B6.r5", SS, SSC, "RECOMPUTED", "Results")
    add("ST1.unseen_r5", "Unseen-label R@5, stacked fusion", x["unseen_R@5"], "as G6", SS, SSC, "RECOMPUTED", "Results", nd=2)
    add("ST1.C", "Dev-selected C of the stacker", sm["C"], "argmax of mean dev-fold MRR@3 over C in {0.01, 0.1, 1, 10}", "results/stacking_model.json", SSC, "RECOMPUTED", "Method", display=str(sm["C"]))
    x4 = st.loc["Fusion (4,1,1,1)"]
    add("ST1.ref4111", "P@1 fusion (4,1,1,1), seed-averaged components", x4["P@1"], "the wide-grid pick with matcher seed 42, applied to seed-averaged components", SS, SSC, "RECOMPUTED", "Sensitivity", ci=(x4["P@1_lo"], x4["P@1_hi"]))
    famrow(sf, "ST1.d3111", "Stacked fusion minus (3,1,1,1), delta P@1", "Stacked fusion (LR)", "Fusion (3,1,1,1)", SS, SSC, "Results")
    famrow(sf, "ST1.d4111", "Stacked fusion minus (4,1,1,1), delta P@1", "Stacked fusion (LR)", "Fusion (4,1,1,1)", SS, SSC, "Results")
    add("ST1.success", "Stacked fusion: pre-registered success rule met", str(bool(sf.success_rule_met.any())), "Holm p < 0.05 vs (3,1,1,1) and CI excluding 0", SS, SSC, "RECOMPUTED", "Results")
    for b, k in (("unseen", "unseen"), ("1-4", "1_4")):
        y = sb[(sb.bucket == b) & (sb.system == "Stacked fusion (LR)")].iloc[0]
        add(f"ST1.b.{k}", f"P@1 stacked fusion, rarest gold label train support {b}", y["P@1"], "as G4", SS, SSC, "RECOMPUTED", "Results", ci=(y["lo"], y["hi"]))
if (RESULTS / "robustness.csv").exists():
    rb = R("robustness.csv"); rf = R("robustness_family.csv"); RS, RSC = "results/robustness.csv, robustness_family.csv", "scripts/run_robustness.py"
    SN = {"TF-IDF + SVM": "svm", "RoBERTa (3-seed avg)": "roberta", "SecBERT (3-seed avg)": "secbert", "Matcher zero-shot": "zeroshot", "Classifiers-only ens.": "clsonly"}
    for _, x in rb.iterrows():
        k = f"R1.{SN[x.system]}.{x.perturbation}"
        if x.perturbation == "clean":
            add(k, f"P@1 {x.system}, clean input (local re-inference)", x["P@1"], "prereg 14; must equal the saved-score value", RS, RSC, "RECOMPUTED", "Robustness", ci=(x["P@1_lo"], x["P@1_hi"])); continue
        add(k, f"P@1 change, {x.system}, perturbation {x.perturbation}", x["delta_P@1"], f"perturbed minus clean, paired bootstrap CI; perturbation changed {int(x.n_changed)} of {int(x.n)} sentences",
            RS, RSC, "RECOMPUTED", "Robustness", ci=(x["delta_lo"], x["delta_hi"]), display=f"{x['delta_P@1']:+.3f}")
        add(k + ".changed", f"P@1 on the changed sentences, {x.system}, {x.perturbation}: clean vs perturbed", f"{x['P@1_changed_clean']:.3f} vs {x['P@1_changed_pert']:.3f} (n = {int(x.n_changed)})",
            "descriptive; only the sentences the perturbation altered", RS, RSC, "RECOMPUTED", "Robustness")
    for _, x in rf.iterrows():
        add(f"R1.fam.{x.perturbation}", f"Classifiers-only ens., {x.perturbation}: Holm-adjusted p", x["p_holm"], f"exact McNemar, Holm over {int(x.family_size)}; robust rule met: {bool(x.robust_rule)}", RS, RSC, "RECOMPUTED", "Robustness")
    add("R1.n_groups_changed", "Test sentences containing a threat-group name", int(rb[rb.perturbation == "mask_groups"].n_changed.iloc[0]), "ATT&CK v12.1 intrusion sets and aliases, 4+ characters, case-sensitive", RS, RSC, "RECOMPUTED", "Robustness")
if (RESULTS / "cross_dataset_svm.csv").exists():
    xd = R("cross_dataset_svm.csv").set_index("train_set"); xf = R("cross_dataset_family.csv"); XS, XSC = "results/cross_dataset_svm.csv, cross_dataset_family.csv", "scripts/run_cross_dataset_svm.py"
    for k, lab in (("a", "TRAM train"), ("b", "siblings only"), ("c", "TRAM + siblings")):
        x = xd.loc[k]
        add(f"X1.{k}.p1", f"P@1 TF-IDF + SVM trained on {lab}, TRAM test", x["P@1"], "prereg 16; siblings de-duplicated against TRAM dev + test", XS, XSC, "RECOMPUTED", "Cross-dataset", ci=(x["P@1_lo"], x["P@1_hi"]))
        add(f"X1.{k}.mrr3", f"MRR@3 TF-IDF + SVM trained on {lab}", x["MRR@3"], "as above", XS, XSC, "RECOMPUTED", "Cross-dataset")
        add(f"X1.{k}.rows", f"Training rows, {lab}", int(x["train_rows"]), "after de-duplication and label filtering", XS, XSC, "RECOMPUTED", "Cross-dataset")
        add(f"X1.{k}.labels", f"Training labels, {lab}", int(x["train_labels"]), "distinct labels with a training row", XS, XSC, "RECOMPUTED", "Cross-dataset")
    for _, x in xf.iterrows():
        famrow(xf, f"X1.d.{x.A}{x.B}", f"SVM ({x.A}) minus SVM ({x.B}), delta P@1", x.A, x.B, XS, XSC, "Cross-dataset")
    xa = xd.loc["c"]
    add("X1.removed", "Sibling rows removed as duplicates of TRAM dev/test", f"exact {int(xa.removed_exact)}, near {int(xa.removed_near)}", "normalised text; token-set Jaccard >= 0.90", XS, XSC, "RECOMPUTED", "Cross-dataset")
    for k in ("b", "c"):
        add(f"X1.{k}.unseen_r5", f"Unseen-label R@5 (unseen in TRAM train), SVM trained on set {k}", xd.loc[k]["unseen_R@5"], "as G6; the siblings cover some TRAM-unseen labels", XS, XSC, "RECOMPUTED", "Cross-dataset", nd=2)
        add(f"X1.{k}.fusion_expl", f"EXPLORATORY: P@1 fusion (3,1,1,1) with the SVM trained on set {k}", xd.loc[k]["fusion_3111_with_this_svm_P@1"],
            "NOT pre-registered as a test; weights not re-tuned; read on test, so hypothesis-generating only (needs a new split or a dev-only confirmation)", XS, XSC, "RECOMPUTED", "Cross-dataset")
if (RESULTS / "power_mde.csv").exists():
    pw = R("power_mde.csv")
    for _, x in pw.iterrows():
        add(f"P1.{x.id}", f"Minimum detectable delta P@1 (power 0.8), {x.A} vs {x.B}", x["mde"], f"simulated, n = 725, observed discordance {x.discordant_share:.3f}, alpha {x.alpha:.4f} (Holm rank {int(x.holm_rank)})",
            "results/power_mde.csv", "scripts/run_power.py", "RECOMPUTED", "Statistics")
if (RESULTS / "llm_baseline.csv").exists():
    lb = R("llm_baseline.csv").set_index("variant"); lf = R("llm_family.csv"); LS, LSC = "results/llm_baseline.csv, llm_family.csv", "scripts/run_llm_baseline.py"
    for v in lb.index:
        x = lb.loc[v]
        add(f"L1.{v}.p1", f"P@1 LLM baseline qwen2.5:7b, {v}", x["P@1"], "prereg 17; local Ollama, temperature 0", LS, LSC, "RECOMPUTED", "Baselines", ci=(x["P@1_lo"], x["P@1_hi"]))
        add(f"L1.{v}.mrr3", f"MRR@3 LLM baseline, {v}", x["MRR@3"], "LLM ids first, then retriever order", LS, LSC, "RECOMPUTED", "Baselines", ci=(x["MRR@3_lo"], x["MRR@3_hi"]))
        add(f"L1.{v}.r5", f"R@5 LLM baseline, {v}", x["R@5_micro"], "as B6.r5", LS, LSC, "RECOMPUTED", "Baselines")
        add(f"L1.{v}.parse", f"Parse rate LLM baseline, {v}", x["parse_rate"], "share of replies with at least one valid id", LS, LSC, "RECOMPUTED", "Baselines")
        add(f"L1.{v}.sec", f"Seconds per sentence, LLM baseline {v}", x["seconds_per_sentence"], "wall time per request on this PC (CPU + GTX 960)", LS, LSC, "RECOMPUTED", "Efficiency", nd=1)
        for ref, rk in (("Matcher (3-seed ens.)", "matcher"), ("Fusion (3,1,1,1)", "fusion")):
            famrow(lf, f"L1.{v}.d_{rk}", f"LLM {v} minus {ref}, delta P@1", f"LLM {v}", ref, LS, LSC, "Baselines")

# ================= Q1 wave 2 (preregs 18-21, 15 Nov 2026) =================
CK = {"Fusion (3,1,1,1)": "fusion", "Matcher (3-seed ens.)": "matcher", "TF-IDF + SVM": "svm", "RoBERTa (3-seed avg)": "roberta", "SecBERT (3-seed avg)": "secbert",
      "TF-IDF + SVM (raw decision score)": "svm_raw", "RoBERTa (3-seed mean probability)": "roberta_raw", "SecBERT (3-seed mean probability)": "secbert_raw"}
if (RESULTS / "conformal.csv").exists():
    cf = R("conformal.csv"); cff = R("conformal_family.csv"); cb = R("conformal_buckets.csv")
    CS, CSC = "results/conformal.csv, conformal_family.csv, conformal_buckets.csv", "scripts/run_conformal.py"
    for _, x in cf.iterrows():
        k = f"CP1.{CK[x.system]}.{x.rule}.a{int(round(x.alpha * 100))}"
        add(k + ".cov", f"Conformal coverage of all gold labels, {x.system}, {x.rule} rule, alpha {x.alpha:.2f}", x["coverage_all"],
            f"prereg 18; calibrated on dev; Wilson 95% CI; nominal {1 - x.alpha:.2f}", CS, CSC, "RECOMPUTED", "Uncertainty", ci=(x["cov_lo"], x["cov_hi"]))
        add(k + ".size", f"Mean conformal set size (labels per sentence), {x.system}, {x.rule} rule, alpha {x.alpha:.2f}", x["size_mean"],
            "bootstrap 95% CI", CS, CSC, "RECOMPUTED", "Uncertainty", ci=(x["size_lo"], x["size_hi"]), nd=2)
    for _, x in cff.iterrows():
        add(f"CP1.d.{CK[x.B]}", f"Conformal set size, fusion minus {x.B} (alpha 0.10, score rule)", x["delta_size"],
            f"paired bootstrap CI; Wilcoxon p = {x.p_wilcoxon:.2g}; Holm p = {x.p_holm:.2g} (family of {int(x.family_size)}); supported: {bool(x.supported)}",
            CS, CSC, "RECOMPUTED", "Uncertainty", ci=(x["ci_lo"], x["ci_hi"]), display=f"{x['delta_size']:+.2f}")
    h1 = cf[(cf.system == "Fusion (3,1,1,1)") & (cf.rule == "score") & (cf.alpha.round(2) == 0.10)].iloc[0]
    add("CP1.H1", "Conformal H1 met: 0.90 inside the Wilson CI of fusion coverage (alpha 0.10, score rule)", str(bool(h1.nominal_in_ci)), "prereg 18", CS, CSC, "RECOMPUTED", "Uncertainty")
    add("CP1.H2", "Conformal H2 met: fusion sets smaller than every component (Holm)", str(bool(cff.supported.all())), "prereg 18", CS, CSC, "RECOMPUTED", "Uncertainty")
    for b, bk in (("unseen", "unseen"), ("1-4", "1_4"), ("50+", "50p")):
        for sysn in ("Fusion (3,1,1,1)", "Matcher (3-seed ens.)"):
            y = cb[(cb.bucket == b) & (cb.system == sysn)].iloc[0]
            add(f"CP1.b.{bk}.{CK[sysn]}", f"Conformal coverage, {sysn}, rarest gold label train support {b} (alpha 0.10, score rule)", y["coverage_all"],
                f"descriptive; the guarantee is marginal, not per bucket; n = {int(y.n_sentences)}", CS, CSC, "RECOMPUTED", "Uncertainty", ci=(y["cov_lo"], y["cov_hi"]), nd=2)
if (RESULTS / "conformal_posthoc_raw.csv").exists():
    cpr = R("conformal_posthoc_raw.csv")
    for _, x in cpr[(cpr.rule == "score") & (cpr.alpha.round(2) == 0.10)].iterrows():
        add(f"CP2.{CK[x.system]}.size", f"POST-HOC: mean conformal set size, {x.system} (alpha 0.10, score rule)", x["size_mean"],
            "D27; not pre-registered; raw scores, labels outside the classifier space never in a set", "results/conformal_posthoc_raw.csv", "scripts/run_conformal_posthoc.py",
            "RECOMPUTED", "Uncertainty", ci=(x["size_lo"], x["size_hi"]), nd=2)
        add(f"CP2.{CK[x.system]}.cov", f"POST-HOC: conformal coverage, {x.system} (alpha 0.10, score rule)", x["coverage_all"], "D27; Wilson 95% CI",
            "results/conformal_posthoc_raw.csv", "scripts/run_conformal_posthoc.py", "RECOMPUTED", "Uncertainty", ci=(x["cov_lo"], x["cov_hi"]))
if (RESULTS / "selective.csv").exists():
    sl = R("selective.csv").set_index("system"); slf = R("selective_family.csv")
    SLS, SLC = "results/selective.csv, selective_family.csv, risk_coverage.csv", "scripts/run_selective.py"
    for name in ("Fusion (3,1,1,1)", "Matcher (3-seed ens.)", "TF-IDF + SVM", "RoBERTa (3-seed avg)", "SecBERT (3-seed avg)"):
        x = sl.loc[name]; key = CK[name]
        add(f"SP1.{key}.aurc", f"AURC (risk = top-1 error), {name}", x["AURC"], "prereg 19; confidence = top-1 minus top-2 score; lower is better", SLS, SLC, "RECOMPUTED", "Triage", nd=4)
        add(f"SP1.{key}.eaurc", f"E-AURC (AURC minus the AURC of a perfect ordering), {name}", x["E-AURC"], "prereg 19", SLS, SLC, "RECOMPUTED", "Triage", nd=4)
        for t, tk in (("0.5", "50"), ("0.8", "80"), ("0.9", "90")):
            add(f"SP1.{key}.sel{tk}", f"Selective P@1, {name}, dev threshold for coverage {t}", x[f"selP@1_{t}"], "accepted test sentences only; bootstrap 95% CI",
                SLS, SLC, "RECOMPUTED", "Triage", ci=(x[f"selP@1_{t}_lo"], x[f"selP@1_{t}_hi"]))
            add(f"SP1.{key}.cov{tk}", f"Realised test coverage, {name}, dev threshold for coverage {t}", x[f"cov{t}_test"], "share of test sentences accepted",
                SLS, SLC, "RECOMPUTED", "Triage")
    for _, x in slf.iterrows():
        add(f"SP1.d.{CK[x.B]}", f"AURC, fusion minus {x.B}", x["delta_AURC"],
            f"paired bootstrap CI (both AURCs per resample); bootstrap p = {x.p_boot:.3g}; Holm p = {x.p_holm:.3g} (family of {int(x.family_size)}); supported: {bool(x.supported)}",
            SLS, SLC, "RECOMPUTED", "Triage", ci=(x["ci_lo"], x["ci_hi"]), display=f"{x['delta_AURC']:+.4f}")
        add(f"SP1.d.{CK[x.B]}.holm", f"AURC, fusion minus {x.B}: Holm-adjusted p", x["p_holm"], f"see SP1.d.{CK[x.B]}", SLS, SLC, "RECOMPUTED", "Triage")
if (RESULTS / "selective_posthoc_raw.csv").exists():
    for _, x in R("selective_posthoc_raw.csv").iterrows():
        add(f"SP2.{CK[x.system]}.aurc", f"POST-HOC: AURC, {x.system}", x["AURC"], "D27; not pre-registered", "results/selective_posthoc_raw.csv", "scripts/run_selective.py", "RECOMPUTED", "Triage", nd=4)
if (RESULTS / "label_noise_summary.csv").exists():
    ln = R("label_noise_summary.csv").set_index("metric")["value"]; LNS, LNC = "results/label_noise_summary.csv, label_noise_candidates.csv", "scripts/run_label_noise.py"
    add("LN1.fusion_err", "Fusion top-1 errors on test", int(ln["fusion_top1_errors"]), "test sentences whose fusion top-1 label is not a gold label", LNS, LNC, "RECOMPUTED", "Error analysis")
    add("LN1.n", "EXPLORATORY: test sentences where fusion and all four components agree on the same wrong top-1 label", int(ln["unanimous_wrong_candidates"]),
        "prereg 20; label-noise CANDIDATES, not validated label errors (shared model bias is also possible)", LNS, LNC, "RECOMPUTED", "Error analysis")
    add("LN1.share_err", "EXPLORATORY: share of fusion top-1 errors that are unanimous-wrong candidates", ln["share_of_fusion_errors"], "LN1.n / LN1.fusion_err", LNS, LNC, "RECOMPUTED", "Error analysis")
    for r, rk in (("sibling sub-technique", "sibling"), ("same tactic", "same_tactic"), ("other tactic", "other_tactic"), ("predicted the parent", "parent"), ("predicted a sub-technique", "sub")):
        add(f"LN1.rel.{rk}", f"EXPLORATORY: unanimous-wrong candidates whose consensus label is a {r} of the gold label" if rk in ("sibling", "parent", "sub") else
            f"EXPLORATORY: unanimous-wrong candidates whose consensus label shares a tactic with the gold label" if rk == "same_tactic" else
            "EXPLORATORY: unanimous-wrong candidates whose consensus label shares no tactic with the gold label", int(ln[f"relation: {r}"]), "count", LNS, LNC, "RECOMPUTED", "Error analysis")
if (RESULTS / "attack_drift.csv").exists():
    ad = R("attack_drift.csv").iloc[0]; ADS, ADC = "results/attack_drift.csv, attack_drift_ids.csv", "scripts/check_attack_drift.py"; ver = f"v{ad.latest_version}"
    add("AD1.version", "Current Enterprise ATT&CK release used for the drift check", f"{ver} (collection modified {str(ad.latest_modified)[:10]})",
        f"mitre-attack/attack-stix-data; bundle SHA-256 {str(ad.bundle_sha256)[:16]}...", ADS, ADC, "RECOMPUTED", "Data")
    for s in ("active", "deprecated", "revoked"):
        add(f"AD1.ids_{s}", f"Label ids {s} in ATT&CK {ver}", int(ad[f"ids_{s}"]), "of the 737 ids of the v12.1 description file", ADS, ADC, "RECOMPUTED", "Data")
    add("AD1.ids_nonactive_v121", "Label ids already deprecated or revoked in ATT&CK v12.1", int(ad["ids_nonactive_already_in_v12.1"]), "the description file keeps revoked ids", ADS, ADC, "RECOMPUTED", "Data")
    add("AD1.ids_after", f"Label ids that became deprecated or revoked between v12.1 and {ver}", int(ad["ids_became_nonactive_after_v12.1"]), "see results/attack_drift_ids.csv", ADS, ADC, "RECOMPUTED", "Data")
    add("AD1.test_any", f"Test sentences with at least one gold label not active in {ver}", int(ad["test_sentences_any_nonactive"]), "of 725", ADS, ADC, "RECOMPUTED", "Data")
    add("AD1.test_share", f"Share of test sentences with a gold label not active in {ver}", ad["test_share_sentences_any_nonactive"], "AD1.test_any / 725", ADS, ADC, "RECOMPUTED", "Data")
    add("AD1.test_already", "Test sentences whose gold label was already deprecated or revoked in v12.1", int(ad["test_sentences_nonactive_already_v12.1"]), "data-quality issue of TRAM", ADS, ADC, "RECOMPUTED", "Data")
    add("AD1.test_after", f"Test sentences whose gold label became non-active after v12.1", int(ad["test_sentences_nonactive_after_v12.1"]), "e.g. T1562 split into new techniques", ADS, ADC, "RECOMPUTED", "Data")
    add("AD1.new_ids", f"Active techniques in {ver} absent from the label space", int(ad["latest_active_ids_absent_from_label_space"]), "cannot be predicted by any system here", ADS, ADC, "RECOMPUTED", "Data")
    add("AD1.desc_sim", f"Median description similarity, v12.1 file vs {ver} (active ids)", ad["desc_similarity_median_active"], "difflib ratio, autojunk off (D28)", ADS, ADC, "RECOMPUTED", "Data")
    add("AD1.desc_lt080", f"Active ids whose description similarity to {ver} is below 0.80", int(ad["desc_similarity_lt_0.80"]), "count", ADS, ADC, "RECOMPUTED", "Data")

# ================= APP: explainer application (thesis objective c, ..\ttp_app), checks run on this PC 15 Nov 2026 =================
APC = "scripts/ingest_app_checks.py"
if (RESULTS / "app_verify.csv").exists():
    av = R("app_verify.csv")
    add("APP1.verify", "App replay reproduces the thesis numbers", f"{int(av.ok.sum())} of {len(av)} checks match",
        "ttp_app/verify_artifacts.py: P@1, conformal tau/coverage/size (alpha 0.10, 0.20), triage coverage and selective P@1 (0.5, 0.8, 0.9), stored SHAP count, E4, SHAP length",
        "results/app_verify.csv", APC, "RECOMPUTED", "Explainer app", note="first run 15/16; the triage threshold used np.quantile instead of the prereg-19 order statistic (D29)")
    add("APP1.verify_ok", "App checks matching the thesis", int(av.ok.sum()), f"of {len(av)}", "results/app_verify.csv", APC, "RECOMPUTED", "Explainer app")
if (RESULTS / "app_tests.csv").exists():
    at_ = R("app_tests.csv").iloc[0]
    add("APP4.tests_passed", "App tests passing", int(at_["passed"]), f"pytest -q in ttp_app; failed {int(at_['failed'])}, skipped {int(at_['skipped'])}",
        "results/app_tests.csv", APC, "RECOMPUTED", "Explainer app")
    add("APP4.tests_failed", "App tests failing", int(at_["failed"]), "pytest -q in ttp_app", "results/app_tests.csv", APC, "RECOMPUTED", "Explainer app")
if (RESULTS / "app_live_timing.csv").exists():
    lt = R("app_live_timing.csv"); lt = lt[lt["error"].isna()] if "error" in lt else lt
    for _, r in lt.iterrows():
        add(f"APP2.{r['sentence']}.p{int(r['n_perm'])}", f"Live mode seconds, {int(r['words'])}-word sentence, {int(r['n_perm'])} permutations", float(r["wall_s"]),
            "wall clock of live.analyse(): SVM + RoBERTa s42 + SecBERT s42 scoring and permutation SHAP, CPU (6 threads), batch 64; one run, invented sentence",
            "results/app_live_timing.csv", APC, "RECOMPUTED", "Explainer app", nd=1)
    add("APP2.additivity_max", "Largest SHAP additivity error in live mode", float(lt["additivity_error"].max()), "|sum(SHAP) + base - score|; must be below 1e-3",
        "results/app_live_timing.csv", APC, "RECOMPUTED", "Explainer app", display=f"{lt['additivity_error'].max():.1e}")
if (RESULTS / "app_grounding.csv").exists():
    ag = R("app_grounding.csv").iloc[0]
    _ans = int(ag["n"]) - int(ag["llm_unavailable"])
    add("APP3.grounding", "Grounding rule v1 pass rate of qwen2.5:7b explanations", "n/a (no LLM answer)" if not _ans else float(ag["pass_rate"]),
        f"passed / (n - LLM unavailable) over the first {int(ag['n'])} test rows with stored SHAP; rule v1 fixed before any output was read; DESCRIPTIVE, no human check of correctness",
        "results/app_grounding.csv", APC, "RECOMPUTED", "Explainer app",
        display=f"{int(ag['passed'])} of {_ans} ({ag['pass_rate']:.0%})" if _ans else "n/a (no LLM answer)")
    for k in ("passed", "failed", "llm_unavailable"):
        add(f"APP3.{k}", f"Grounding report: {k.replace('_', ' ')}", int(ag[k]), f"of {int(ag['n'])} rows", "results/app_grounding.csv", APC, "RECOMPUTED", "Explainer app")
    add("APP3.seconds_median", "Median seconds per grounding-report row", float(ag["seconds_median"]), "wall clock per row: LLM call, grounding check and template fallback", "results/app_grounding.csv", APC,
        "RECOMPUTED", "Explainer app", nd=1)
if (RESULTS / "app_grounding_causes_posthoc.csv").exists():
    gc = R("app_grounding_causes_posthoc.csv")
    add("APP3.only_name", "Rule-v1 failures caused only by quoting the explained technique's own id or name (POST-HOC)", int(gc.loc[gc.violations == "technique id/name", "rows"].sum()),
        f"of {int(gc.rows.sum())} failed rows; descriptive input for a proposed rule v2, not a pass rate", "results/app_grounding_causes_posthoc.csv", APC, "RECOMPUTED", "Explainer app")
    add("APP3.not_in_sentence", "Rule-v1 failures that quote at least one word absent from the sentence (POST-HOC)", int(gc.loc[gc.violations.str.contains("word not in sentence"), "rows"].sum()),
        f"of {int(gc.rows.sum())} failed rows", "results/app_grounding_causes_posthoc.csv", APC, "RECOMPUTED", "Explainer app")

# ================= Colab reruns (hash-checked by scripts/ingest_colab.py; results/colab/) =================
_byid = {c["id"]: c for c in C}; _done_colab = set()
_CRMAP = {"data_audit": {"n_train": "A2.train", "n_dev": "A2.dev", "n_test": "A2.test", "train_labels": "A3", "test_labels": "A4", "test_labels_unseen": "A5.unseen",
                         "multi_label_test": "A9.multi_test", "gold_pairs_test": "A9.pairs_test", "test_over_128_roberta": "A7.roberta"},
          "baselines": {"prior_P@1": "B0", "svm_P@1": "B6", "svm_MRR@3": "B6.mrr3", "svm_micro_f1_notebook": "B3", "svm_macro_f1_notebook": "B3.macro117",
                        "zeroshot_P@1": "B10a", "zeroshot_MRR@3": "B10a.mrr3"}}
for _mf in sorted((RESULTS / "colab").glob("manifest_*.json")):
    _man = json.loads(_mf.read_text(encoding="utf-8")); _rid = _man.get("run_id"); _mp = _CRMAP.get(_rid)
    if not _mp or _man.get("status") != "DONE": continue
    _d = [abs(float(_man["metrics"][k]) - float(_byid[i]["value"])) for k, i in _mp.items() if k in _man["metrics"] and i in _byid]
    add(f"CR.{_rid}", f"Colab rerun of the {_rid} notebook: registry values reproduced", sum(x < 1e-9 for x in _d),
        f"of {len(_d)} compared values ({', '.join(_mp.values())}); max |difference| {max(_d):.1e}; runner {_man['env'].get('gpu') if _man['env'].get('gpu') not in (None, 'none') else 'Colab CPU'}, torch {_man['env'].get('torch', '?')}",
        f"results/colab/{_mf.name}", "scripts/ingest_colab.py", "RECOMPUTED", "Reproducibility", display=f"{sum(x < 1e-9 for x in _d)} of {len(_d)}")
_ENV0 = RESULTS / "colab" / "env_00" / "env_colab.json"
if _ENV0.exists():
    _e = json.loads(_ENV0.read_text(encoding="utf-8")); _pk = {k.lower(): v for k, v in _e.get("packages", {}).items()}
    _txt = (f"Python {_e['python']}, {_e['gpu']} ({_e.get('nvidia_smi', '').split(',')[1].strip() if ',' in _e.get('nvidia_smi', '') else '?'}), torch {_e['torch']}, "
            + ", ".join(f"{p} {_pk.get(p, '?')}" for p in ("transformers", "sentence-transformers", "shap", "scikit-learn", "numpy", "pandas")))
    add("T7.env_colab", "Colab environment (python, packages, GPU)", _txt, f"written by notebook 00 on Colab; {_e.get('n_packages')} packages listed; 36 of 36 input SHA-256 equal to the PC copy",
        "results/colab/env_00/env_colab.json", "notebooks/00_setup_and_verify.ipynb", "VERIFIED", "Reproducibility")
    _done_colab.add("T7.env_colab")
_M42 = RESULTS / "colab" / "manifest_matcher_ft20_s42.json"          # notebook 04 or colab_fusion_shap, after scripts/ingest_colab.py
if _M42.exists() and json.loads(_M42.read_text(encoding="utf-8")).get("status") == "DONE":
    _m = json.loads(_M42.read_text(encoding="utf-8")); _t = _m["metrics"]
    add("T1.matcher_retrained_p1", "Test P@1 of the matcher retrained with saved weights", float(_t["P@1"]),
        f"seed 42, Exp_2.1 settings, GPU {_m['env'].get('gpu', '?')}; GPU nondeterminism: compare with the original run, not bit-identical; run {_m['run_id']}",
        "results/colab/manifest_matcher_ft20_s42.json", "notebooks/04_train_matcher_save.ipynb", "RECOMPUTED", "Reproducibility")
    for _k in ("MRR@3", "R@5"):
        if _k in _t: add(f"T1.matcher_retrained_{_k.replace('@', '').lower()}", f"Test {_k} of the matcher retrained with saved weights", float(_t[_k]), "as T1.matcher_retrained_p1",
                         "results/colab/manifest_matcher_ft20_s42.json", "notebooks/04_train_matcher_save.ipynb", "RECOMPUTED", "Reproducibility")
    _done_colab.add("T1.matcher_retrained_p1")
_FS = RESULTS / "colab" / "manifest_fusion_shap.json"                 # notebook 06 or colab_fusion_shap
if _FS.exists() and json.loads(_FS.read_text(encoding="utf-8")).get("status") == "DONE":
    _f = json.loads(_FS.read_text(encoding="utf-8")); _t = _f["metrics"]
    if "fused_minus_roberta" in _t:
        add("T2.full_fusion_shap", "Full-fusion SHAP: deletion-test drop, fused-SHAP top-3 minus RoBERTa-SHAP top-3 (logit-z units)", float(_t["fused_minus_roberta"]),
            f"paired bootstrap over {int(_t.get('n_deletion', 0))} eligible sentences of {int(_t['n_sentences'])}; prereg 12; system: {_f['config'].get('system', '?')}",
            "results/colab/manifest_fusion_shap.json", "notebooks/06_explainability.ipynb", "RECOMPUTED", "Explainability", ci=[_t["fused_minus_roberta_lo"], _t["fused_minus_roberta_hi"]])
    else:
        add("T2.full_fusion_shap", "Full-fusion SHAP: sentences explained (colab_fusion_shap notebook)", int(_t["n_sentences"]),
            f"max additivity error {_t.get('max_additivity_error', float('nan')):.1e}; deletion-test summary is printed by that notebook's Cell 6, not stored in the manifest",
            "results/colab/manifest_fusion_shap.json", "_evidence_pack/09_repro/colab_fusion_shap.ipynb", "RECOMPUTED", "Explainability")
    for _k in ("n_sentences", "max_additivity_error", "fused_top1_correct", "same_label_share"):
        if _k in _t: add(f"T2.{_k}", f"Full-fusion SHAP: {_k.replace('_', ' ')}", float(_t[_k]) if _k != "n_sentences" else int(_t[_k]), "from the run manifest",
                         "results/colab/manifest_fusion_shap.json", "notebooks/06_explainability.ipynb", "RECOMPUTED", "Explainability",
                         display=f"{_t[_k]:.1e}" if _k == "max_additivity_error" else None)
    _done_colab.add("T2.full_fusion_shap")
_HS = RESULTS / "human_study_v2_summary.json"          # written by scripts/score_human_study.py once rated sheets are back
if _HS.exists():
    _h = json.loads(_HS.read_text(encoding="utf-8")); _p = _h.get("primary"); _s = _h.get("secondary", {})
    if _p:
        add("T8.human_study_v2", "Human study v2: REAL minus CONTROL mean rating (1-5 scale)", _p["diff_real_minus_control"],
            f"per-item mean over {_h['n_raters']} raters; percentile bootstrap over items, 10,000 resamples; rule (lower bound > 0 and >= 1.0) met: {_p['rule_met']}; status {_h['status']}",
            "results/human_study_v2_summary.json", "scripts/score_human_study.py", "RECOMPUTED", "Human evaluation", ci=_p["ci"], nd=2)
        if "alpha_ordinal" in _s:
            add("T8.alpha_ordinal", "Human study v2: Krippendorff alpha (ordinal) on REAL items", _s["alpha_ordinal"], f"{_s['alpha_band']}; {_s['alpha_ci_resamples']} item resamples for the interval",
                "results/human_study_v2_summary.json", "scripts/score_human_study.py", "RECOMPUTED", "Human evaluation", ci=_s["alpha_ordinal_ci"])
        add("T8.n_raters", "Human study v2: raters", int(_h["n_raters"]), "returned sheets", "results/human_study_v2_summary.json", "scripts/score_human_study.py", "RECOMPUTED", "Human evaluation")
        _done_colab.add("T8.human_study_v2")

# ================= TODO-COLAB and NOT-FOUND =================
for k, lab, d_, nb in (("T1.matcher_retrained_p1", "Test P@1 of the matcher retrained with saved weights", "seed 42, same settings as Exp_2.1", "notebooks/04_train_matcher_save.ipynb"),
                       ("T2.full_fusion_shap", "Full-fusion SHAP: fused-SHAP vs RoBERTa-SHAP faithfulness", "prereg 12", "notebooks/06_explainability.ipynb"),
                       ("T3.fusion_replication", "Fusion and ablation with the retrained matcher", "replication of B12a/B13a", "notebooks/05_fusion_and_ablation.ipynb"),
                       ("T4.seeds_45_46", "Five-seed means (seeds 42-46)", "prereg 10", "notebooks/03_train_classifiers.ipynb, 04_train_matcher_save.ipynb"),
                       ("T5.baseline_same_protocol", "Published baseline under our protocol", "re-run of Nguyen et al. on the same split and metric code", "notebooks/09_baseline_same_protocol.ipynb"),
                       ("T6.cross_dataset", "Objective (b): sibling datasets to TRAM test", "prereg 11", "notebooks/08_extension_cross_dataset.ipynb"),
                       ("T7.env_colab", "Colab environment (python, packages, GPU)", "captured by notebook 00", "notebooks/00_setup_and_verify.ipynb"),
                       ("T8.human_study_v2", "Second human study (3+ raters, protocol)", "docs/HUMAN_STUDY_PROTOCOL.md", "scripts/make_rating_sheet.py"),
                       ("T9.usability_sus", "Usability study of the explainer app (3-5 users, 5 tasks, SUS); author task, not Colab", "design-science evaluation of the artefact",
                        "ttp_app/usability/USABILITY_STUDY.md, ttp_app/usability/score_sus.py")):
    if k not in _done_colab: add(k, lab, None, d_, nb, nb, "TODO-COLAB", "Open work")
for k, lab, where in (("N1.tram_train_tsv", "Original tram_train.tsv", "searched Dataset/ and the whole tree; rebuilt from combined_train.csv"), ("N2.matcher_weights", "Original matcher weights", "run_match_1/ holds score files only"),
                      ("N3.svm_scores", "Saved SVM scores", "never written by any notebook; refit"), ("N4.colab_env", "Colab environment of the original runs", "no pip freeze saved"),
                      ("N5.git_history", "Git history of the original work", "no repository existed before 2026-11-14"), ("N6.data_licence", "Dataset licence and source commit", "no licence text in the folder"),
                      ("N7.attack_version_in_data", "ATT&CK version string inside a data file", "only in notebook comments"), ("N8.pre_dedup_size", "Train size before de-duplication", "raw train file absent"),
                      ("N9.rater_roles", "Background of raters B and C", "not recorded in any file"), ("N10.training_times", "Classifier training times", "not printed by the notebooks")):
    add(k, lab, None, where, "-", "-", "NOT-FOUND", "Limitations")

ids = [c["id"] for c in C]; assert len(ids) == len(set(ids)), [i for i in ids if ids.count(i) > 1]
ledger = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10a", "B10b", "B10c", "B11", "B12a", "B12b", "B13a", "B13b", "B14",
          "C1", "C2", "C3", "C4", "D1", "D2", "D3", "D4", "D5", "E1", "E2", "E3", "F1", "F2"]
missing = [i for i in ledger if i not in ids]; assert not missing, missing
_sc = {}
for c in C: _sc[c["status"]] = _sc.get(c["status"], 0) + 1
out = {"schema": "ttpmap.schema.Claim", "generated_by": "scripts/build_numbers.py", "n_claims": len(C), "status_counts": _sc, "ledger_ids": ledger, "claims": C}
(SHOWCASE / "thesis_numbers.json").write_text(json.dumps(out, indent=1, ensure_ascii=True), encoding="utf-8")
M = ["# THESIS MAP", "", "Every number the thesis may state: id -> value -> where it comes from. Generated by `scripts/build_numbers.py`; do not edit.",
     "The 40 ledger claims of the evidence pack are marked L.", "", "| id | L | section | label | value | 95% CI | status | source file | script |", "|---|---|---|---|---|---|---|---|---|"]
for c in C:
    ci = f"[{c['ci'][0]:.3f}, {c['ci'][1]:.3f}]" if c["ci"] else ""
    M.append(f"| {c['id']} | {'L' if c['id'] in ledger else ''} | {c['thesis_section']} | {c['label']} | {c['display']} | {ci} | {c['status']} | {c['source_file']} | {c['script']} |")
(SHOWCASE / "THESIS_MAP.md").write_text("\n".join(M), encoding="utf-8")
st = pd.Series([c["status"] for c in C]).value_counts().to_dict()
print(f"claims: {len(C)} | ledger ids present: {len(ledger) - len(missing)}/{len(ledger)} | by status: {st}")
