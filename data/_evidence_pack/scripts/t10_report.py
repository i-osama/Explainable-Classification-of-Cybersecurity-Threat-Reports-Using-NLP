"""T10: EVIDENCE_REPORT.md (claim ledger, contradictions, NOT-FOUND, proposed experiments) + zip."""
import re, zipfile
import numpy as np, pandas as pd
from pathlib import Path
from common import PACK, ROOT, w

R = pd.read_csv(PACK / "03_results_recomputed.csv"); T = R[R.split == "test"]
B = pd.read_csv(PACK / "04_bootstrap.csv").set_index("id"); H = pd.read_csv(PACK / "07_agreement.csv").set_index("statistic")["value"]
def g(group, col): return T[T.group == group][col].astype(float).to_numpy()
def ms(v): return f"{np.mean(v):.3f} +/- {np.std(v, ddof=1):.3f}"
def one(group, col): return f"{g(group, col)[0]:.3f}"
def ci(i): return f"{B.loc[i, 'delta_P@1']:+.3f} [{B.loc[i, 'ci95_lo_10k']:+.3f}, {B.loc[i, 'ci95_hi_10k']:+.3f}] (10k); [{B.loc[i, 'ci95_lo_nb1000']:+.3f}, {B.loc[i, 'ci95_hi_nb1000']:+.3f}] (1k, rng 0); McNemar p={B.loc[i, 'mcnemar_exact_p']:.3f}"
dl = (PACK / "06_shap.md").read_text(encoding="utf-8")
d725 = re.search(r"ALL 725 rows \[RECOMPUTED, new\] \| mask \| (\d+) \| [\d.]+ \| [\d.]+ \| ([\d.]+) \| (\[[^\]]+\]) \| (\d+ / \d+)", dl)
S3, S1, S4, S6, S7, S8, S2 = "scripts/t3_results.py", "scripts/t1_dataset.py", "scripts/t4_bootstrap.py", "scripts/t6_shap.py", "scripts/t7_human.py", "(hand-written) 08_baseline.md", "(hand-written) 02_settings.md"
CLS = "Exp_1_4_run_tram_2_epoc_30/*_pw_s4{2,3,4}/{test_probs.npy,metrics.json}"; MAT = "run_match_1/ft20_s4{2,3,4}/test_scores.npy"
L = [  # id, claim, thesis value, file value, status, source, script
 ("A1", "total sentences", "4,797", "4,797", "MATCH (RECOMPUTED)", "Dataset/combined_train.csv[tram], tram_dev.tsv, tram_test.tsv", S1),
 ("A2", "train/dev/test", "3,468 / 604 / 725", "3,468 / 604 / 725", "MATCH (RECOMPUTED)", "same", S1),
 ("A3", "train labels", "180", "180", "MATCH (RECOMPUTED)", "same", S1),
 ("A4", "test labels", "127", "127", "MATCH (RECOMPUTED)", "tram_test.tsv", S1),
 ("A5", "seen + unseen test labels", "117 + 10", "117 + 10", "MATCH (RECOMPUTED)", "same", S1),
 ("A6", "overlap with train", "2 test, 1 dev", "exact: 1 test, 0 dev; near-duplicate (Jaccard>=0.9): +1 test, +3 dev rows", "MISMATCH (RECOMPUTED)", "01_duplicates.csv, 01_near_duplicates.csv", S1),
 ("A7", "test sentences truncated at 128", "34 of 725", "34 (RoBERTa tokenizer); 24 (SecBERT tokenizer)", "MATCH for RoBERTa only (RECOMPUTED)", "run-dir tokenizers", S1),
 ("A8", "ATT&CK description entries", "733", "file has 737 rows; 733 after dropping 4 revoked ids", "MATCH with qualifier (RECOMPUTED + VERIFIED Exp_2.1 CELL 2)", "Dataset/ttp-desc-mappings.csv", S1),
 ("B1", "micro-F1 RoBERTa", "0.705 +/- 0.011", ms(g("roberta", "micro_F1_180cols(nb)")), "MATCH (RECOMPUTED)", CLS, S3),
 ("B2", "micro-F1 SecBERT", "0.703 +/- 0.001", ms(g("secbert", "micro_F1_180cols(nb)")), "MATCH (RECOMPUTED)", CLS, S3),
 ("B3", "micro-F1 SVM", "0.696", one("svm", "micro_F1_180cols(nb)"), "MATCH (RECOMPUTED, SVM refit)", "refit; Exp_1_4 CELL 6 output 0.6961", S3),
 ("B4", "macro-F1 RoBERTa 117 / 127", "0.563 / 0.519", f"{g('roberta','macro_F1_117').mean():.3f} / {g('roberta','macro_F1_127').mean():.3f}", "MATCH (RECOMPUTED)", CLS, S3),
 ("B5", "macro-F1 SecBERT 117 / 127", "0.543 / 0.500", f"{g('secbert','macro_F1_117').mean():.3f} / {g('secbert','macro_F1_127').mean():.3f}", "MATCH (RECOMPUTED)", CLS, S3),
 ("B6", "P@1 SVM", "0.742", one("svm", "P@1"), "MATCH (RECOMPUTED)", "refit", S3),
 ("B7", "P@1 RoBERTa", "0.756", f"{one('roberta_ens','P@1')} = 3-seed probability AVERAGE (an ensemble); mean of single seeds = {ms(g('roberta','P@1'))}", "MATCH but MISLABELLED: not comparable with B1 (single-seed mean)", CLS, S3),
 ("B8", "P@1 SecBERT", "0.755", f"{g('secbert_ens','P@1')[0]:.4f} = 3-seed probability average; mean of single seeds = {ms(g('secbert','P@1'))}", "MATCH within 0.001 (file 0.7545 rounds to 0.754 or 0.755); MISLABELLED as B7", CLS, S3),
 ("B9", "classifiers-only ensemble P@1", "0.774", one("cls_only", "P@1"), "MATCH (RECOMPUTED)", CLS + " + SVM refit", S3),
 ("B10a", "bge zero-shot P@1", "0.228", one("matcher_zs", "P@1"), "MATCH (RECOMPUTED)", "run_match_1/zeroshot/test_scores.npy", S3),
 ("B10b", "matcher ft20 P@1", "0.756 +/- 0.015", ms(g("matcher", "P@1")), "MATCH (RECOMPUTED)", MAT, S3),
 ("B10c", "matcher 3-seed ensemble P@1", "0.777", one("matcher_ens", "P@1"), "MATCH (RECOMPUTED)", MAT, S3),
 ("B11", "equal-weight fusion P@1", "0.779", f"{one('fusion_eq_nb','P@1')} with matcher seed 42 (as notebook); {one('fusion_eq','P@1')} with the 3-seed matcher used by the 0.803 fusion", "MATCH, but not like-for-like with B13 (RECOMPUTED)", "Exp_2.1 CELL 8", S3),
 ("B12a", "seed-paired fusion P@1", "0.796 +/- 0.006 (0.790/0.796/0.803)", f"{ms(g('fusion_paired','P@1'))} ({'/'.join(f'{x:.3f}' for x in g('fusion_paired','P@1'))})", "MATCH (RECOMPUTED); definition exists in no notebook", CLS + ", " + MAT, S3),
 ("B12b", "seed-paired fusion MRR@3", "0.852 +/- 0.002", ms(g("fusion_paired", "MRR@3")), "MATCH (RECOMPUTED)", "same", S3),
 ("B13a", "seed-averaged fusion P@1", "0.803", one("fusion_avg", "P@1"), "MATCH (RECOMPUTED)", "same", S3),
 ("B13b", "seed-averaged fusion MRR@3", "0.853?", one("fusion_avg", "MRR@3"), "MISMATCH: 0.856 (0.853 is the notebook's matcher-seed mean, CELL 11)", "run_match_1/final_results_table.csv; Exp_2.1 CELL 11", S3),
 ("B14", "fusion weights and grid", "(3,1,1,1), grid of 1,711", "(3,1,1,1) = DEV winner of the 255-setting grid; the 1,711 grid's DEV winner is (4,1,1,1); (3,1,1,1) is rank 30 of 1,711", "MISMATCH (VERIFIED Exp_2.1 CELL 8/9 + RECOMPUTED)", "03_fusion_grid_dev.csv", S3),
 ("C1", "fusion - classifiers-only dP@1", "+0.029 [0.017, 0.043]", ci("C1"), "MATCH (RECOMPUTED)", "saved predictions", S4),
 ("C2", "fusion - matcher ensemble dP@1", "+0.026 [0.003, 0.051]", ci("C2"), "MATCH on the 1k setting; with 10k resamples the lower bound is +0.001 (borderline)", "saved predictions", S4),
 ("C3", "RoBERTa - SVM dP@1", "+0.014 [-0.015, 0.040]", ci("C3"), "MATCH (RECOMPUTED); thesis setting NOT-FOUND in notebooks", "saved predictions", S4),
 ("C4", "RoBERTa - SecBERT dP@1", "+0.001 [-0.022, 0.025]", ci("C4"), "MATCH (RECOMPUTED); thesis setting NOT-FOUND in notebooks", "saved predictions", S4),
 ("D1", "Krippendorff alpha nominal", "-0.057", f"{float(H['Krippendorff alpha nominal (A,B; 100 rows)']):+.3f}", "MATCH (RECOMPUTED)", "Exp_3_0_shap/hand_check_v2_*.xlsx", S7),
 ("D2", "Krippendorff alpha ordinal", "0.031", f"{float(H['Krippendorff alpha ordinal (A,B; 100 rows)']):+.3f}", "MATCH (RECOMPUTED)", "same", S7),
 ("D3", "Fleiss kappa", "-0.062", f"{float(H['Fleiss kappa (A,B; 100 rows)']):+.3f}", "MATCH (RECOMPUTED)", "same", S7),
 ("D4", "Cohen kappa", "0.062", f"{float(H['Cohen kappa unweighted (A,B)']):+.3f} (unweighted)", "MATCH (RECOMPUTED)", "same", S7),
 ("D5", "third rater rows", "3", "3 of 100", "MATCH (RECOMPUTED)", "same", S7),
 ("E1", "SHAP settings", "permutation, 40 permutations, roberta_pw_s42", "same; word units, <mask> replacement, top-1 logit, all 725 sentences", "MATCH (VERIFIED Exp_3_0b CELL 2 + method block in jsonl)", "Exp_3_0_shap/shap_v2_roberta_pw_s42.jsonl", S6),
 ("E2", "deletion-test difference", "10.19 logits", f"10.189 (n=93, mask); on all eligible test sentences: {d725.group(2)} {d725.group(3)} (n={d725.group(1)})", "MATCH (RECOMPUTED from CSV and by CPU re-run)", "deletion_test_v2_roberta_pw_s42.csv; 06_deletion_test_725.csv", S6),
 ("E3", "top-3 larger than random", "93/93", f"93 / 93; all eligible test sentences: {d725.group(4)}", "MATCH (RECOMPUTED)", "same", S6),
 ("F1", "Nguyen et al. P@1", "0.770", ".770 (arXiv:2401.10337 Table 2, TRAM, 'Asymmetric')", "NOTES-ONLY in project; confirmed from the arXiv PDF (not a project file)", "Exp_2.1 CELL 6/12 constants", S8),
 ("F2", "Nguyen et al. MRR@3", "0.864", ".864 (same row)", "NOTES-ONLY in project; confirmed from the arXiv PDF", "same", S8),
]
PH = [("SVM n-gram range", "word 1-2 grams, sublinear_tf", "VERIFIED Exp_1_4 CELL 6"), ("SVM regularisation constant", "C = 1.0 (LinearSVC, random_state=42, class_weight None)", "VERIFIED Exp_1_4 CELL 6"),
      ("SVM one-vs-rest setup", "OneVsRestClassifier over 180 labels; dev threshold -0.45 + arg-max fallback", "VERIFIED Exp_1_4 CELL 6"),
      ("SVM macro-F1", f"{one('svm','macro_F1_117')} (117 labels) / {one('svm','macro_F1_127')} (127 labels)", "RECOMPUTED; notebook output 0.5427"),
      ("bge exact checkpoint", "BAAI/bge-base-en-v1.5 (HF revision hash NOT-FOUND)", "VERIFIED Exp_2.1 CELL 1; run_match_1/*/metrics.json"),
      ("matcher loss", "multi-positive InfoNCE-style: softplus(logsumexp(negatives) - positive), cosine x 30", "VERIFIED Exp_2.1 CELL 3"),
      ("matcher epochs", "max 20, patience 4, selection by DEV MRR@3; best epochs 17 / 14 / 8", "VERIFIED Exp_2.1 CELL 7; metrics.json"),
      ("matcher negative sampling", "64 uniform random labels per batch from all 733 minus batch golds (+ other rows' golds)", "VERIFIED Exp_2.1 CELL 3"),
      ("fusion component and weight order", "[matcher, SVM, RoBERTa, SecBERT] = (3, 1, 1, 1)", "VERIFIED Exp_2.1 CELL 8 output"),
      ("when (3,1,1,1) was chosen", "first coarse grid (255 settings) on DEV; NOT the 1,711 grid", "VERIFIED cell order CELL 8 -> 9 -> 11 + RECOMPUTED; timestamps NOT-FOUND"),
      ("bootstrap resample count", "1,000 (rng 0) in the notebooks for fusion comparisons; RoBERTa-vs-SVM/SecBERT setting NOT-FOUND; pack uses 10,000", "VERIFIED Exp_2.1 CELL 8/11/13"),
      ("SHAP sample size", "725 (all test sentences); deletion test and human sheet use the first 100 of a fixed permutation", "VERIFIED"),
      ("SHAP sampling procedure", "RandomState(42).permutation(725)", "VERIFIED Exp_3_0b CELL 3"),
      ("SHAP masking procedure", "whitespace word replaced by <mask>; Independent masker over word-presence bits", "VERIFIED Exp_3_0b CELL 2"),
      ("number of removed tokens", "3 words (highest positive SHAP)", "VERIFIED Exp_3_1_deletion_test CELL 2"),
      ("deletion-test definition and 93 denominator", "drop of top-1 logit, top-3 vs mean of 20 random triples; 93 = 100 - 3 short - 4 truncated", "VERIFIED + RECOMPUTED"),
      ("human rating scale", "0 = does not make sense, 1 = partly, 2 = makes sense", "VERIFIED Exp_3_2 CELL 0"),
      ("human sampling procedure", "first 100 of RandomState(42).permutation(725); gold hidden", "VERIFIED Exp_3_2 CELL 0/2"),
      ("ATT&CK description count 733", "737 rows in file, 733 used", "RECOMPUTED"),
      ("whether train was deduplicated", "yes, exact-text drop_duplicates, 3,468 rows; one case-insensitive duplicate pair remains", "VERIFIED Exp_1_4 CELL 4 + RECOMPUTED"),
      ("test split and label granularity equal to the published evaluation", "sizes and 193-label inventory agree; row-level identity UNKNOWN; sub-technique-level exact match on both sides", "08_baseline.md"),
      ("requirements.txt", "09_repro/requirements_local_analysis.txt (exact); Colab training pins only for transformers 5.22.1, torch 2.14.1, shap 0.54.1", "VERIFIED / rest NOT-FOUND"),
      ("tram_train.tsv copy", "not shipped (license NOT-FOUND); 09_repro/make_tram_train.py rebuilds it", "-"),
      ("repository URL", "NOT-FOUND (no .git)", "-"),
      ("optional 256-token re-evaluation", "NOT RUN: matcher weights were never saved; classifier re-evaluation at 256 would need retraining (trained at 128)", "see section d")]
CONTRA = [
 "B14: draft says (3,1,1,1) came from the 1,711 grid. Files: it is the DEV winner of the 255-setting grid (matcher seed 42); the 1,711 grid's DEV winner is (4,1,1,1) and (3,1,1,1) is rank 30 there.",
 "B13b: seed-averaged fusion MRR@3 is 0.856, not 0.853 (0.853 belongs to the notebook's per-matcher-seed mean 0.800 +/- 0.001).",
 "B12: `run_match_1/final_results_table.csv` reports fusion over 3 runs as 0.800 +/- 0.001 (matcher seed varies, classifiers 3-seed averaged); the draft's 0.796 +/- 0.006 is a different construction (all components seed s) that no notebook contains. Both reproduce; the thesis must define which one it reports.",
 "B7/B8: P@1 0.756 / 0.755 are 3-seed probability-averaged ensembles; `final_results_table.csv` and the per-seed means give RoBERTa 0.752 +/- 0.007 and SecBERT 0.743 +/- 0.004. Next to single-seed micro-F1 (B1/B2) this mixes two kinds of numbers.",
 "B11: equal-weight 0.779 uses matcher seed 42 only; with the 3-seed matcher used by the 0.803 fusion, equal weights give 0.782. Gain of tuning on equal footing = +0.021, not +0.024.",
 "A6: exact normalised duplicates are 1 test and 0 dev sentence in train (not 2 and 1); near-duplicates add 1 test and 3 dev rows.",
 "A7: 34 truncated sentences holds for the RoBERTa tokenizer only; SecBERT truncates 24.",
 "A8: 733 is the label space after removing 4 revoked ids; the description file has 737 entries.",
 "C2: fusion vs matcher ensemble is borderline: lower CI bound +0.001 with 10,000 resamples (+0.003 with the notebook's 1,000), exact McNemar p = 0.048 (51 vs 32).",
 "Status note says SHAP sample size is unknown / '100 stored rows': the local file holds all 725 rows; the deletion test and rating sheet use the first 100.",
 "Status note 'fusion helps on techniques unseen in training': on the 10 unseen-label test sentences the fusion's P@1 is 0.000 (matcher alone 0.200); the fusion only raises unseen R@5 from 0.0 to 0.5. On labels with 1-4 training sentences fusion P@1 is 0.294 vs matcher 0.559. The fusion's net gain comes from labels with >= 10 training sentences (`05_errors.md`).",
 "Micro/macro-F1 in the notebooks score only the 180 train-label columns: the 10 unseen test labels are ignored rather than counted as misses (micro-F1 with them as false negatives is lower; see `03_results.md`).",
 "RoBERTa's dev threshold is 0.85 for all three seeds = the top edge of the search grid (0.10-0.85).",
 "Baseline R@1: the paper defines R@k per sample (hits/|Q|); notebooks compare a 'micro' R@1 (hits / all gold labels) with the paper's .658. Not the same quantity.",
 "CLAUDE.md says ttp-desc-mappings is a CSV; it is TAB-separated. Notebooks cite 'EACL Findings 2024' for the baseline; venue not confirmed from the PDF.",
]
NF = [
 "`Dataset/tram_train.tsv`: not on E: (searched Dataset/, whole tree). Train reconstructed from combined_train.csv tram slice.",
 "Matcher model weights (all seeds): never saved (Exp_2.1 CELL 3 has no save call); searched run_match_1/ for *.safetensors, *.pt, *.bin.",
 "SVM predictions/scores: never saved; refit.",
 "Zero-shot matcher DEV scores: only test_scores.npy exists in run_match_1/zeroshot/.",
 "Colab environment (pip freeze, Python version, GPU model, CUDA): not saved; only transformers 5.22.1, torch 2.14.1+cu130, shap 0.54.1 appear in files.",
 "Git repository / remote URL / commit: no .git directory.",
 "Baseline paper PDF, its code, its predictions, its split files: no PDF and no such files under E:\\Osamas Paper.",
 "License and source commit of the TRAM data and of ttp-desc-mappings.csv; ATT&CK version string inside any data file.",
 "Pre-deduplication size of tram_train.tsv.",
 "Bootstrap setting behind C3/C4 and the 'seed-paired' fusion definition: in no notebook or script (searched nb_src/*.txt).",
 "Timestamps/execution counts for Exp_2.1 (all exec=None), so 'when' is known by cell order only.",
 "Rater roles/expertise for Raters B and C; rating instructions beyond the notebook text; any record of rater training.",
 "Thesis draft, .dotx template, and the earlier audit text: not in the folder, so claims were checked as listed in the brief, not against the prose.",
 "Training wall-clock times for the classifiers.",
 "Tactic mapping: not in the project; ATT&CK v12.1 STIX downloaded into external/ (excluded from the zip).",
]
EXP = [
 ("Published baseline on the identical split", "clone github.com/tumeteor/mitre-ttp-mapping, train 'Asymmetric' in *separate* TRAM mode, score with scripts/common.py", "about 24 h on a V100 (paper, Limitations) per run", "turns the side-by-side with .770/.864 into a controlled comparison; settles split/mode comparability"),
 ("Fusion ablation (drop each component)", "ALREADY COMPUTABLE from saved scores: rows 'Ablation: fusion without ...' in 03_results_recomputed.csv (python t3_results.py); add bootstrap CIs per ablation", "< 1 min CPU", "shows each component's contribution: without matcher 0.774, SVM 0.799, RoBERTa 0.782, SecBERT 0.790"),
 ("Weight-sensitivity surface", "plot DEV and TEST P@1 over matcher weight 0..8 with others fixed at 1, from 03_fusion_grid_dev.csv + a test column", "< 1 min CPU", "shows (3,1,1,1) vs (4,1,1,1) is a flat region, defuses the grid question"),
 ("Objective (b): combined-dataset run", "Exp_1_4 train_model and Exp_2.1 train_matcher on Dataset/combined_train.csv (14,465 rows), same dev/test", "classifiers: about 4x the TRAM run per seed on a T4; matcher: about 2 h per seed (estimate)", "the registered objective; also matches the baseline's 'combined' mode"),
 ("Learning curve", "train_model / train_matcher on 25/50/75/100% of train (stratified, 3 seeds)", "about 12 short runs per model on a T4, several hours", "shows whether more TRAM data would help rare labels"),
 ("Matcher retrain WITH saved weights", "09_repro/colab_train_matcher_with_save.py", "20-30 min per seed on a T4", "prerequisite for full-fusion SHAP, 256-token re-evaluation, any new inference"),
 ("Full-fusion SHAP", "python x1_fusion_shap.py --n 100 --matcher-dir <saved matcher>; python x2_fusion_shap_summary.py --file 11_fusion_shap_full.jsonl", "about 25 s per sentence on this CPU with the matcher added (estimate from the 14 s partial run)", "explains the system that produces the headline number"),
 ("Third rater completes the sheet + written rating guideline", "no code", "about 2 h of rater time", "agreement is at chance (alpha -0.057); current human study cannot support plausibility"),
 ("Threshold grid extended to 0.95", "re-pick thresholds on saved dev_probs.npy with np.arange(0.1, 0.96, 0.05)", "< 1 min CPU", "RoBERTa threshold sits on the grid edge for all seeds"),
 ("256-token re-evaluation of the classifiers", "retrain with max_length=256 (weights at 128 cannot be re-used fairly)", "about 2x the 128-token run", "only 34 test sentences are affected (P@1 0.53-0.68 on them); low priority"),
]
M = ["# EVIDENCE REPORT\n", "Project: `E:\\Osamas Paper`. Pack: `_evidence_pack\\`. Every value below is tagged VERIFIED (read from a file/notebook cell), "
     "RECOMPUTED (pack script on saved predictions/labels), NOTES-ONLY, or NOT-FOUND. Detail files: `00`-`11` in this folder.\n",
     "## (a) Claim ledger\n", "| ID | claim | thesis value | file value | status | source file | script |", "|---|---|---|---|---|---|---|"]
M += [f"| {a} | {b} | {c} | {d} | {e} | {f} | {g_} |" for a, b, c, d, e, f, g_ in L]
def cat(s):
    if s.startswith("MISMATCH"): return "MISMATCH"
    if s.startswith("NOTES-ONLY"): return "NOTES-ONLY (confirmed outside the folder)"
    if "MISLABELLED" in s or "qualifier" in s or "only" in s or "borderline" in s or "not like-for-like" in s or "NOT-FOUND" in s or "no notebook" in s: return "MATCH WITH CAVEAT"
    return "MATCH"
counts = pd.Series([cat(x[4]) for x in L]).value_counts()
M += ["\nLedger counts: " + "; ".join(f"{k}: {v}" for k, v in counts.items()) + f" (total {len(L)}).\n",
      "### Placeholders\n", "| item | value | basis |", "|---|---|---|"] + [f"| {a} | {b} | {c} |" for a, b, c in PH]
M += ["\n### Review focus\n", "LEAKAGE: PASS (thresholds, epochs, fusion weights, pw choice, SHAP model all DEV-based or fixed in advance; two notes in `02_settings.md`). "
      "METRIC DEFINITIONS: PASS with notes. SPLIT OVERLAP: PASS (1 exact test duplicate). MISSING ARTIFACTS: FAIL (listed in c). SELECTION BIAS: PASS for the pack, UNKNOWN for the draft.\n",
      "## (b) Contradictions between notes and files\n"] + [f"{i}. {c}" for i, c in enumerate(CONTRA, 1)]
M += ["\n## (c) NOT-FOUND\n"] + [f"{i}. {c}" for i, c in enumerate(NF, 1)]
M += ["\n## (d) Experiments that would strengthen the thesis (NOT RUN unless stated)\n", "| experiment | command | runtime | reason |", "|---|---|---|---|"] + [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in EXP]
extra = PACK / "11_fusion_shap.md"
M += ["\n## Extra analyses done in this pack (new content)\n",
      "- `05_errors.md`: rarity buckets, tactics, confusions, fixed/broken, truncation, calibration; `fig_rarity.png`, `fig_fusion_delta.png`.",
      "- `06_shap.md`: deletion test re-run on all eligible test sentences; `fig_shap_ex1-3.png` by a pre-stated rule.",
      "- `10_fusion_vs_roberta.md`: the model SHAP explains and the fusion disagree on the top-1 label for 108 of 725 sentences.",
      f"- `11_fusion_shap.md`: {'SHAP of the fused score for the components with saved weights (see file).' if extra.exists() else 'not produced in this run.'}"]
w(PACK / "EVIDENCE_REPORT.md", "\n".join(M))

# ---- zip ----
zp = ROOT / "_evidence_pack.zip"
excluded = []
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for p in sorted(PACK.rglob("*")):
        if p.is_dir() or "__pycache__" in p.parts or p.name.startswith("_") and p.suffix == ".txt": continue
        if "matcher_retrain" in p.parts and p.suffix in (".pt", ".npy"): excluded.append(f"{p.relative_to(PACK)} ({p.stat().st_size / 1e6:.0f} MB)"); continue
        if "external" in p.parts: excluded.append(f"{p.relative_to(PACK)} ({p.stat().st_size / 1e6:.0f} MB)"); continue
        z.write(p, p.relative_to(PACK.parent))
size = zp.stat().st_size / 1e6
print("LEDGER COUNTS:", "; ".join(f"{k}={v}" for k, v in counts.items()), f"(total {len(L)})")
print("CONTRADICTIONS:"); [print(f" {i}. {c[:175]}") for i, c in enumerate(CONTRA, 1)]
print("NOT-FOUND:"); [print(f" {i}. {c[:120]}") for i, c in enumerate(NF, 1)]
print(f"ZIP: {zp} ({size:.1f} MB, limit 25) excluded: {excluded or 'nothing'}")
