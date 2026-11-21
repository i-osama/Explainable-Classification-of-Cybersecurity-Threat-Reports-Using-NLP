# EVIDENCE REPORT

Project: `E:\Osamas Paper`. Pack: `_evidence_pack\`. Every value below is tagged VERIFIED (read from a file/notebook cell), RECOMPUTED (pack script on saved predictions/labels), NOTES-ONLY, or NOT-FOUND. Detail files: `00`-`11` in this folder.

## (a) Claim ledger

| ID | claim | thesis value | file value | status | source file | script |
|---|---|---|---|---|---|---|
| A1 | total sentences | 4,797 | 4,797 | MATCH (RECOMPUTED) | Dataset/combined_train.csv[tram], tram_dev.tsv, tram_test.tsv | scripts/t1_dataset.py |
| A2 | train/dev/test | 3,468 / 604 / 725 | 3,468 / 604 / 725 | MATCH (RECOMPUTED) | same | scripts/t1_dataset.py |
| A3 | train labels | 180 | 180 | MATCH (RECOMPUTED) | same | scripts/t1_dataset.py |
| A4 | test labels | 127 | 127 | MATCH (RECOMPUTED) | tram_test.tsv | scripts/t1_dataset.py |
| A5 | seen + unseen test labels | 117 + 10 | 117 + 10 | MATCH (RECOMPUTED) | same | scripts/t1_dataset.py |
| A6 | overlap with train | 2 test, 1 dev | exact: 1 test, 0 dev; near-duplicate (Jaccard>=0.9): +1 test, +3 dev rows | MISMATCH (RECOMPUTED) | 01_duplicates.csv, 01_near_duplicates.csv | scripts/t1_dataset.py |
| A7 | test sentences truncated at 128 | 34 of 725 | 34 (RoBERTa tokenizer); 24 (SecBERT tokenizer) | MATCH for RoBERTa only (RECOMPUTED) | run-dir tokenizers | scripts/t1_dataset.py |
| A8 | ATT&CK description entries | 733 | file has 737 rows; 733 after dropping 4 revoked ids | MATCH with qualifier (RECOMPUTED + VERIFIED Exp_2.1 CELL 2) | Dataset/ttp-desc-mappings.csv | scripts/t1_dataset.py |
| B1 | micro-F1 RoBERTa | 0.705 +/- 0.011 | 0.705 +/- 0.011 | MATCH (RECOMPUTED) | Exp_1_4_run_tram_2_epoc_30/*_pw_s4{2,3,4}/{test_probs.npy,metrics.json} | scripts/t3_results.py |
| B2 | micro-F1 SecBERT | 0.703 +/- 0.001 | 0.703 +/- 0.001 | MATCH (RECOMPUTED) | Exp_1_4_run_tram_2_epoc_30/*_pw_s4{2,3,4}/{test_probs.npy,metrics.json} | scripts/t3_results.py |
| B3 | micro-F1 SVM | 0.696 | 0.696 | MATCH (RECOMPUTED, SVM refit) | refit; Exp_1_4 CELL 6 output 0.6961 | scripts/t3_results.py |
| B4 | macro-F1 RoBERTa 117 / 127 | 0.563 / 0.519 | 0.563 / 0.519 | MATCH (RECOMPUTED) | Exp_1_4_run_tram_2_epoc_30/*_pw_s4{2,3,4}/{test_probs.npy,metrics.json} | scripts/t3_results.py |
| B5 | macro-F1 SecBERT 117 / 127 | 0.543 / 0.500 | 0.543 / 0.500 | MATCH (RECOMPUTED) | Exp_1_4_run_tram_2_epoc_30/*_pw_s4{2,3,4}/{test_probs.npy,metrics.json} | scripts/t3_results.py |
| B6 | P@1 SVM | 0.742 | 0.742 | MATCH (RECOMPUTED) | refit | scripts/t3_results.py |
| B7 | P@1 RoBERTa | 0.756 | 0.756 = 3-seed probability AVERAGE (an ensemble); mean of single seeds = 0.752 +/- 0.007 | MATCH but MISLABELLED: not comparable with B1 (single-seed mean) | Exp_1_4_run_tram_2_epoc_30/*_pw_s4{2,3,4}/{test_probs.npy,metrics.json} | scripts/t3_results.py |
| B8 | P@1 SecBERT | 0.755 | 0.7545 = 3-seed probability average; mean of single seeds = 0.743 +/- 0.004 | MATCH within 0.001 (file 0.7545 rounds to 0.754 or 0.755); MISLABELLED as B7 | Exp_1_4_run_tram_2_epoc_30/*_pw_s4{2,3,4}/{test_probs.npy,metrics.json} | scripts/t3_results.py |
| B9 | classifiers-only ensemble P@1 | 0.774 | 0.774 | MATCH (RECOMPUTED) | Exp_1_4_run_tram_2_epoc_30/*_pw_s4{2,3,4}/{test_probs.npy,metrics.json} + SVM refit | scripts/t3_results.py |
| B10a | bge zero-shot P@1 | 0.228 | 0.228 | MATCH (RECOMPUTED) | run_match_1/zeroshot/test_scores.npy | scripts/t3_results.py |
| B10b | matcher ft20 P@1 | 0.756 +/- 0.015 | 0.756 +/- 0.015 | MATCH (RECOMPUTED) | run_match_1/ft20_s4{2,3,4}/test_scores.npy | scripts/t3_results.py |
| B10c | matcher 3-seed ensemble P@1 | 0.777 | 0.777 | MATCH (RECOMPUTED) | run_match_1/ft20_s4{2,3,4}/test_scores.npy | scripts/t3_results.py |
| B11 | equal-weight fusion P@1 | 0.779 | 0.779 with matcher seed 42 (as notebook); 0.782 with the 3-seed matcher used by the 0.803 fusion | MATCH, but not like-for-like with B13 (RECOMPUTED) | Exp_2.1 CELL 8 | scripts/t3_results.py |
| B12a | seed-paired fusion P@1 | 0.796 +/- 0.006 (0.790/0.796/0.803) | 0.796 +/- 0.006 (0.790/0.796/0.803) | MATCH (RECOMPUTED); definition exists in no notebook | Exp_1_4_run_tram_2_epoc_30/*_pw_s4{2,3,4}/{test_probs.npy,metrics.json}, run_match_1/ft20_s4{2,3,4}/test_scores.npy | scripts/t3_results.py |
| B12b | seed-paired fusion MRR@3 | 0.852 +/- 0.002 | 0.852 +/- 0.002 | MATCH (RECOMPUTED) | same | scripts/t3_results.py |
| B13a | seed-averaged fusion P@1 | 0.803 | 0.803 | MATCH (RECOMPUTED) | same | scripts/t3_results.py |
| B13b | seed-averaged fusion MRR@3 | 0.853? | 0.856 | MISMATCH: 0.856 (0.853 is the notebook's matcher-seed mean, CELL 11) | run_match_1/final_results_table.csv; Exp_2.1 CELL 11 | scripts/t3_results.py |
| B14 | fusion weights and grid | (3,1,1,1), grid of 1,711 | (3,1,1,1) = DEV winner of the 255-setting grid; the 1,711 grid's DEV winner is (4,1,1,1); (3,1,1,1) is rank 30 of 1,711 | MISMATCH (VERIFIED Exp_2.1 CELL 8/9 + RECOMPUTED) | 03_fusion_grid_dev.csv | scripts/t3_results.py |
| C1 | fusion - classifiers-only dP@1 | +0.029 [0.017, 0.043] | +0.029 [+0.017, +0.043] (10k); [+0.017, +0.043] (1k, rng 0); McNemar p=0.000 | MATCH (RECOMPUTED) | saved predictions | scripts/t4_bootstrap.py |
| C2 | fusion - matcher ensemble dP@1 | +0.026 [0.003, 0.051] | +0.026 [+0.001, +0.051] (10k); [+0.003, +0.051] (1k, rng 0); McNemar p=0.048 | MATCH on the 1k setting; with 10k resamples the lower bound is +0.001 (borderline) | saved predictions | scripts/t4_bootstrap.py |
| C3 | RoBERTa - SVM dP@1 | +0.014 [-0.015, 0.040] | +0.014 [-0.014, +0.041] (10k); [-0.015, +0.040] (1k, rng 0); McNemar p=0.391 | MATCH (RECOMPUTED); thesis setting NOT-FOUND in notebooks | saved predictions | scripts/t4_bootstrap.py |
| C4 | RoBERTa - SecBERT dP@1 | +0.001 [-0.022, 0.025] | +0.001 [-0.023, +0.025] (10k); [-0.022, +0.025] (1k, rng 0); McNemar p=1.000 | MATCH (RECOMPUTED); thesis setting NOT-FOUND in notebooks | saved predictions | scripts/t4_bootstrap.py |
| D1 | Krippendorff alpha nominal | -0.057 | -0.057 | MATCH (RECOMPUTED) | Exp_3_0_shap/hand_check_v2_*.xlsx | scripts/t7_human.py |
| D2 | Krippendorff alpha ordinal | 0.031 | +0.031 | MATCH (RECOMPUTED) | same | scripts/t7_human.py |
| D3 | Fleiss kappa | -0.062 | -0.062 | MATCH (RECOMPUTED) | same | scripts/t7_human.py |
| D4 | Cohen kappa | 0.062 | +0.062 (unweighted) | MATCH (RECOMPUTED) | same | scripts/t7_human.py |
| D5 | third rater rows | 3 | 3 of 100 | MATCH (RECOMPUTED) | same | scripts/t7_human.py |
| E1 | SHAP settings | permutation, 40 permutations, roberta_pw_s42 | same; word units, <mask> replacement, top-1 logit, all 725 sentences | MATCH (VERIFIED Exp_3_0b CELL 2 + method block in jsonl) | Exp_3_0_shap/shap_v2_roberta_pw_s42.jsonl | scripts/t6_shap.py |
| E2 | deletion-test difference | 10.19 logits | 10.189 (n=93, mask); on all eligible test sentences: 10.132 [9.785, 10.502] (n=645) | MATCH (RECOMPUTED from CSV and by CPU re-run) | deletion_test_v2_roberta_pw_s42.csv; 06_deletion_test_725.csv | scripts/t6_shap.py |
| E3 | top-3 larger than random | 93/93 | 93 / 93; all eligible test sentences: 644 / 645 | MATCH (RECOMPUTED) | same | scripts/t6_shap.py |
| F1 | Nguyen et al. P@1 | 0.770 | .770 (arXiv:2401.10337 Table 2, TRAM, 'Asymmetric') | NOTES-ONLY in project; confirmed from the arXiv PDF (not a project file) | Exp_2.1 CELL 6/12 constants | (hand-written) 08_baseline.md |
| F2 | Nguyen et al. MRR@3 | 0.864 | .864 (same row) | NOTES-ONLY in project; confirmed from the arXiv PDF | same | (hand-written) 08_baseline.md |

Ledger counts: MATCH: 26; MATCH WITH CAVEAT: 9; MISMATCH: 3; NOTES-ONLY (confirmed outside the folder): 2 (total 40).

### Placeholders

| item | value | basis |
|---|---|---|
| SVM n-gram range | word 1-2 grams, sublinear_tf | VERIFIED Exp_1_4 CELL 6 |
| SVM regularisation constant | C = 1.0 (LinearSVC, random_state=42, class_weight None) | VERIFIED Exp_1_4 CELL 6 |
| SVM one-vs-rest setup | OneVsRestClassifier over 180 labels; dev threshold -0.45 + arg-max fallback | VERIFIED Exp_1_4 CELL 6 |
| SVM macro-F1 | 0.543 (117 labels) / 0.500 (127 labels) | RECOMPUTED; notebook output 0.5427 |
| bge exact checkpoint | BAAI/bge-base-en-v1.5 (HF revision hash NOT-FOUND) | VERIFIED Exp_2.1 CELL 1; run_match_1/*/metrics.json |
| matcher loss | multi-positive InfoNCE-style: softplus(logsumexp(negatives) - positive), cosine x 30 | VERIFIED Exp_2.1 CELL 3 |
| matcher epochs | max 20, patience 4, selection by DEV MRR@3; best epochs 17 / 14 / 8 | VERIFIED Exp_2.1 CELL 7; metrics.json |
| matcher negative sampling | 64 uniform random labels per batch from all 733 minus batch golds (+ other rows' golds) | VERIFIED Exp_2.1 CELL 3 |
| fusion component and weight order | [matcher, SVM, RoBERTa, SecBERT] = (3, 1, 1, 1) | VERIFIED Exp_2.1 CELL 8 output |
| when (3,1,1,1) was chosen | first coarse grid (255 settings) on DEV; NOT the 1,711 grid | VERIFIED cell order CELL 8 -> 9 -> 11 + RECOMPUTED; timestamps NOT-FOUND |
| bootstrap resample count | 1,000 (rng 0) in the notebooks for fusion comparisons; RoBERTa-vs-SVM/SecBERT setting NOT-FOUND; pack uses 10,000 | VERIFIED Exp_2.1 CELL 8/11/13 |
| SHAP sample size | 725 (all test sentences); deletion test and human sheet use the first 100 of a fixed permutation | VERIFIED |
| SHAP sampling procedure | RandomState(42).permutation(725) | VERIFIED Exp_3_0b CELL 3 |
| SHAP masking procedure | whitespace word replaced by <mask>; Independent masker over word-presence bits | VERIFIED Exp_3_0b CELL 2 |
| number of removed tokens | 3 words (highest positive SHAP) | VERIFIED Exp_3_1_deletion_test CELL 2 |
| deletion-test definition and 93 denominator | drop of top-1 logit, top-3 vs mean of 20 random triples; 93 = 100 - 3 short - 4 truncated | VERIFIED + RECOMPUTED |
| human rating scale | 0 = does not make sense, 1 = partly, 2 = makes sense | VERIFIED Exp_3_2 CELL 0 |
| human sampling procedure | first 100 of RandomState(42).permutation(725); gold hidden | VERIFIED Exp_3_2 CELL 0/2 |
| ATT&CK description count 733 | 737 rows in file, 733 used | RECOMPUTED |
| whether train was deduplicated | yes, exact-text drop_duplicates, 3,468 rows; one case-insensitive duplicate pair remains | VERIFIED Exp_1_4 CELL 4 + RECOMPUTED |
| test split and label granularity equal to the published evaluation | sizes and 193-label inventory agree; row-level identity UNKNOWN; sub-technique-level exact match on both sides | 08_baseline.md |
| requirements.txt | 09_repro/requirements_local_analysis.txt (exact); Colab training pins only for transformers 5.22.1, torch 2.14.1, shap 0.54.1 | VERIFIED / rest NOT-FOUND |
| tram_train.tsv copy | not shipped (license NOT-FOUND); 09_repro/make_tram_train.py rebuilds it | - |
| repository URL | NOT-FOUND (no .git) | - |
| optional 256-token re-evaluation | NOT RUN: matcher weights were never saved; classifier re-evaluation at 256 would need retraining (trained at 128) | see section d |

### Review focus

LEAKAGE: PASS (thresholds, epochs, fusion weights, pw choice, SHAP model all DEV-based or fixed in advance; two notes in `02_settings.md`). METRIC DEFINITIONS: PASS with notes. SPLIT OVERLAP: PASS (1 exact test duplicate). MISSING ARTIFACTS: FAIL (listed in c). SELECTION BIAS: PASS for the pack, UNKNOWN for the draft.

## (b) Contradictions between notes and files

1. B14: draft says (3,1,1,1) came from the 1,711 grid. Files: it is the DEV winner of the 255-setting grid (matcher seed 42); the 1,711 grid's DEV winner is (4,1,1,1) and (3,1,1,1) is rank 30 there.
2. B13b: seed-averaged fusion MRR@3 is 0.856, not 0.853 (0.853 belongs to the notebook's per-matcher-seed mean 0.800 +/- 0.001).
3. B12: `run_match_1/final_results_table.csv` reports fusion over 3 runs as 0.800 +/- 0.001 (matcher seed varies, classifiers 3-seed averaged); the draft's 0.796 +/- 0.006 is a different construction (all components seed s) that no notebook contains. Both reproduce; the thesis must define which one it reports.
4. B7/B8: P@1 0.756 / 0.755 are 3-seed probability-averaged ensembles; `final_results_table.csv` and the per-seed means give RoBERTa 0.752 +/- 0.007 and SecBERT 0.743 +/- 0.004. Next to single-seed micro-F1 (B1/B2) this mixes two kinds of numbers.
5. B11: equal-weight 0.779 uses matcher seed 42 only; with the 3-seed matcher used by the 0.803 fusion, equal weights give 0.782. Gain of tuning on equal footing = +0.021, not +0.024.
6. A6: exact normalised duplicates are 1 test and 0 dev sentence in train (not 2 and 1); near-duplicates add 1 test and 3 dev rows.
7. A7: 34 truncated sentences holds for the RoBERTa tokenizer only; SecBERT truncates 24.
8. A8: 733 is the label space after removing 4 revoked ids; the description file has 737 entries.
9. C2: fusion vs matcher ensemble is borderline: lower CI bound +0.001 with 10,000 resamples (+0.003 with the notebook's 1,000), exact McNemar p = 0.048 (51 vs 32).
10. Status note says SHAP sample size is unknown / '100 stored rows': the local file holds all 725 rows; the deletion test and rating sheet use the first 100.
11. Status note 'fusion helps on techniques unseen in training': on the 10 unseen-label test sentences the fusion's P@1 is 0.000 (matcher alone 0.200); the fusion only raises unseen R@5 from 0.0 to 0.5. On labels with 1-4 training sentences fusion P@1 is 0.294 vs matcher 0.559. The fusion's net gain comes from labels with >= 10 training sentences (`05_errors.md`).
12. Micro/macro-F1 in the notebooks score only the 180 train-label columns: the 10 unseen test labels are ignored rather than counted as misses (micro-F1 with them as false negatives is lower; see `03_results.md`).
13. RoBERTa's dev threshold is 0.85 for all three seeds = the top edge of the search grid (0.10-0.85).
14. Baseline R@1: the paper defines R@k per sample (hits/|Q|); notebooks compare a 'micro' R@1 (hits / all gold labels) with the paper's .658. Not the same quantity.
15. CLAUDE.md says ttp-desc-mappings is a CSV; it is TAB-separated. Notebooks cite 'EACL Findings 2024' for the baseline; venue not confirmed from the PDF.

## (c) NOT-FOUND

1. `Dataset/tram_train.tsv`: not on E: (searched Dataset/, whole tree). Train reconstructed from combined_train.csv tram slice.
2. Matcher model weights (all seeds): never saved (Exp_2.1 CELL 3 has no save call); searched run_match_1/ for *.safetensors, *.pt, *.bin.
3. SVM predictions/scores: never saved; refit.
4. Zero-shot matcher DEV scores: only test_scores.npy exists in run_match_1/zeroshot/.
5. Colab environment (pip freeze, Python version, GPU model, CUDA): not saved; only transformers 5.22.1, torch 2.14.1+cu130, shap 0.54.1 appear in files.
6. Git repository / remote URL / commit: no .git directory.
7. Baseline paper PDF, its code, its predictions, its split files: no PDF and no such files under E:\Osamas Paper.
8. License and source commit of the TRAM data and of ttp-desc-mappings.csv; ATT&CK version string inside any data file.
9. Pre-deduplication size of tram_train.tsv.
10. Bootstrap setting behind C3/C4 and the 'seed-paired' fusion definition: in no notebook or script (searched nb_src/*.txt).
11. Timestamps/execution counts for Exp_2.1 (all exec=None), so 'when' is known by cell order only.
12. Rater roles/expertise for Raters B and C; rating instructions beyond the notebook text; any record of rater training.
13. Thesis draft, .dotx template, and the earlier audit text: not in the folder, so claims were checked as listed in the brief, not against the prose.
14. Training wall-clock times for the classifiers.
15. Tactic mapping: not in the project; ATT&CK v12.1 STIX downloaded into external/ (excluded from the zip).

## (d) Experiments that would strengthen the thesis (NOT RUN unless stated)

| experiment | command | runtime | reason |
|---|---|---|---|
| Published baseline on the identical split | clone github.com/tumeteor/mitre-ttp-mapping, train 'Asymmetric' in *separate* TRAM mode, score with scripts/common.py | about 24 h on a V100 (paper, Limitations) per run | turns the side-by-side with .770/.864 into a controlled comparison; settles split/mode comparability |
| Fusion ablation (drop each component) | ALREADY COMPUTABLE from saved scores: rows 'Ablation: fusion without ...' in 03_results_recomputed.csv (python t3_results.py); add bootstrap CIs per ablation | < 1 min CPU | shows each component's contribution: without matcher 0.774, SVM 0.799, RoBERTa 0.782, SecBERT 0.790 |
| Weight-sensitivity surface | plot DEV and TEST P@1 over matcher weight 0..8 with others fixed at 1, from 03_fusion_grid_dev.csv + a test column | < 1 min CPU | shows (3,1,1,1) vs (4,1,1,1) is a flat region, defuses the grid question |
| Objective (b): combined-dataset run | Exp_1_4 train_model and Exp_2.1 train_matcher on Dataset/combined_train.csv (14,465 rows), same dev/test | classifiers: about 4x the TRAM run per seed on a T4; matcher: about 2 h per seed (estimate) | the registered objective; also matches the baseline's 'combined' mode |
| Learning curve | train_model / train_matcher on 25/50/75/100% of train (stratified, 3 seeds) | about 12 short runs per model on a T4, several hours | shows whether more TRAM data would help rare labels |
| Matcher retrain WITH saved weights | 09_repro/colab_train_matcher_with_save.py | 20-30 min per seed on a T4 | prerequisite for full-fusion SHAP, 256-token re-evaluation, any new inference |
| Full-fusion SHAP | python x1_fusion_shap.py --n 100 --matcher-dir <saved matcher>; python x2_fusion_shap_summary.py --file 11_fusion_shap_full.jsonl | about 25 s per sentence on this CPU with the matcher added (estimate from the 14 s partial run) | explains the system that produces the headline number |
| Third rater completes the sheet + written rating guideline | no code | about 2 h of rater time | agreement is at chance (alpha -0.057); current human study cannot support plausibility |
| Threshold grid extended to 0.95 | re-pick thresholds on saved dev_probs.npy with np.arange(0.1, 0.96, 0.05) | < 1 min CPU | RoBERTa threshold sits on the grid edge for all seeds |
| 256-token re-evaluation of the classifiers | retrain with max_length=256 (weights at 128 cannot be re-used fairly) | about 2x the 128-token run | only 34 test sentences are affected (P@1 0.53-0.68 on them); low priority |

## Extra analyses done in this pack (new content)

- `05_errors.md`: rarity buckets, tactics, confusions, fixed/broken, truncation, calibration; `fig_rarity.png`, `fig_fusion_delta.png`.
- `06_shap.md`: deletion test re-run on all eligible test sentences; `fig_shap_ex1-3.png` by a pre-stated rule.
- `10_fusion_vs_roberta.md`: the model SHAP explains and the fusion disagree on the top-1 label for 108 of 725 sentences.
- `11_fusion_shap.md`: SHAP of the fused score for the components with saved weights (see file).