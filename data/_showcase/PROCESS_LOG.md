# Process log

Only events with file evidence. Dates of the experimental phase are **reconstructed from file timestamps** (modification times of result files and notebooks;
`results/process_timeline.csv`, built by `scripts/build_timeline.py`). They show when files were last written, not how long the work took.

## Timeline

| first file | last file | track | event | evidence | basis |
|---|---|---|---|---|---|
| 2026-09-21 | 2026-10-17 | Data | Dataset files obtained (TRAM dev/test, combined train, ATT&CK descriptions) | Dataset/* | reconstructed from file timestamps |
| 2026-09-29 | 2026-09-29 | Classifiers | First TRAM classifier notebook (pilot) | Experiments/Exp_0_tram.ipynb | reconstructed from file timestamps |
| 2026-10-06 | 2026-10-06 | Classifiers | Head learning-rate probe | Experiments/Exp_01_Tram.ipynb | reconstructed from file timestamps |
| 2026-10-12 | 2026-10-12 | Classifiers | 15-epoch runs, RoBERTa and SecBERT, seeds 42-44 | runs_tram_1.1_epoch_15/* | reconstructed from file timestamps |
| 2026-10-13 | 2026-10-14 | Classifiers | 30-epoch runs with higher head learning rate (final classifiers) | run_tram_2_epoc_30/* | reconstructed from file timestamps |
| 2026-10-17 | 2026-10-17 | Matcher | Zero-shot and first fine-tuned matcher, 20-epoch seed 42 | run_match_1/{zeroshot,ft_s42,ft20_s42} | reconstructed from file timestamps |
| 2026-10-26 | 2026-10-26 | Matcher | Matcher seeds 43 and 44 | run_match_1/ft20_s43, ft20_s44 | reconstructed from file timestamps |
| 2026-10-28 | 2026-10-28 | Fusion | Fusion weights and final results table | run_match_1/final_results_table.csv | reconstructed from file timestamps |
| 2026-11-03 | 2026-11-04 | Matcher | 256-token description ablation and label-rarity chart | run_match_1/ft20L256_*, label_rarity.png | reconstructed from file timestamps |
| 2026-11-06 | 2026-11-06 | Classifiers | Classifier runs re-saved with checkpoints (pw / nopw, seeds 42-44) | Exp_1_4_run_tram_2_epoc_30/* | reconstructed from file timestamps |
| 2026-11-07 | 2026-11-07 | Explainability | SHAP pilots (token-level, then word-level with 10 permutations) | Exp_3_0_shap/shap_roberta_pw_s42.jsonl, shap_v1_* | reconstructed from file timestamps |
| 2026-11-10 | 2026-11-10 | Explainability | Deletion test on the 100-sentence sample | Exp_3_0_shap/deletion_test_v2_roberta_pw_s42.csv | reconstructed from file timestamps |
| 2026-11-11 | 2026-11-11 | Human study | Rating sheets filled and agreement computed | Exp_3_0_shap/ rating sheets (by role), rater_agreement_v2_*.csv | reconstructed from file timestamps |
| 2026-11-12 | 2026-11-12 | Explainability | Word-level SHAP for all test sentences (40 permutations) | Exp_3_0_shap/shap_v2_roberta_pw_s42.jsonl | reconstructed from file timestamps |
| 2026-11-14 | 2026-11-14 | Audit | Evidence pack: every claim recomputed from saved predictions | _evidence_pack/*.md, *.csv | reconstructed from file timestamps |
| 2026-11-14 | 2026-11-14 | Showcase | Showcase: package, tests, pre-registered analyses, truth file | _showcase/results/*.csv, thesis_numbers.json | reconstructed from file timestamps |

## Audit phase (14 November 2026, from `_evidence_pack/PROGRESS.md` and the git log)

1. Evidence pack T0-T10: every claim of the draft recomputed from saved predictions; ledger of 40 claims; the leakage review; the baseline paper read from arXiv.
2. Deletion test re-run on all eligible test sentences; SHAP of the classifier part of the fusion on 40 sentences.
3. A local CPU retraining of the matcher was started and stopped during its first epoch (about two hours per epoch); no weights were produced and nothing from it is used.
4. Showcase: package, tests, pre-registered analyses, figures, notebooks, report. Commits are in the private repository from 14 November 2026 onward.

## The 15 contradictions between the draft and the files, and how each was resolved

| # | contradiction (as found in the evidence pack) | resolution |
|---|---|---|
| 1 | the draft attributed (3,1,1,1) to the 1,711-setting grid | files: (3,1,1,1) = dev winner of the 255-setting grid; the 1,711-setting grid selects (4,1,1,1). Draft corrected to say so; both grids reported |
| 2 | seed-averaged fusion MRR@3 given as 0.853 | file value 0.856; corrected |
| 3 | "2 test and 1 dev sentence also in train" | exact 1 / 0; near-duplicate +1 / +3; corrected in the text. One table cell still carries the old wording (`THESIS_PLACEHOLDERS.md` section 14) |
| 4 | two fusion headline numbers with different meanings | both kept with definitions: seed-paired 0.796 +/- 0.006, notebook 0.800 +/- 0.001, seed-averaged 0.803; the draft headlines the seed-paired value; author to confirm |
| 5 | P@1 of RoBERTa and SecBERT were 3-seed ensembles presented beside single-seed F1 | both stated: ensembles 0.756 and 0.754, single-seed means 0.752 +/- 0.007 and 0.743 +/- 0.004 |
| 6 | equal-weight fusion compared on a different matcher | both stated: 0.779 (matcher seed 42) and 0.782 (3-seed matcher) |
| 7 | "34 truncated sentences" for all models | 34 (RoBERTa tokenizer); 24 (SecBERT tokenizer) |
| 8 | "733 description entries" | 737 in the file; 733 used |
| 9 | fusion vs matcher ensemble presented as significant | borderline: +0.026 [0.001, 0.051], McNemar p 0.048, Holm p 0.190; reported as not robust |
| 10 | SHAP sample believed to be 100 sentences | the stored file covers 725 sentences; the deletion test and rating sheet use the first 100 |
| 11 | "fusion helps on unseen techniques" | P@1 0.000 on unseen labels; unseen R@5 0.50 vs 0.00 for the classifiers; reported as a limitation |
| 12 | notebook F1 ignores the unseen test labels | three variants computed; micro-F1 drops by 0.0043 (RoBERTa) when unseen gold labels count as misses |
| 13 | RoBERTa threshold on the edge of its grid | extended grid checked: thresholds 0.93 / 0.83 / 0.88; test micro-F1 changes by -0.0006 on average |
| 14 | baseline R@1 compared with a different quantity | the paper's per-sample definition implemented in `notebooks/09_baseline_same_protocol.ipynb`; R@1 is not compared in the thesis |
| 15 | description file called CSV; venue of the baseline unconfirmed | file is tab-separated; venue confirmed by web search as Findings of EACL 2024 (`docs/RELATED_WORK_VERIFIED.md`) |
