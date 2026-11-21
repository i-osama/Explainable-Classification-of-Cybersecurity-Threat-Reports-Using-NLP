# Chapter 6: Discussion and conclusion: numbers, tables, figures, caveats

Every number below comes from `thesis_numbers.json` (do not retype; quote the id). Status meanings: RECOMPUTED = recomputed from saved predictions by a showcase script; VERIFIED = read from a file or code; NOTES-ONLY = a copied constant; TODO-COLAB = not yet run; NOT-FOUND = searched, absent.

## Numbers

| id | value | 95% CI | definition | source file | status |
|---|---|---|---|---|---|
| `C2` | +0.026 | [0.001, 0.051] | Fusion minus matcher ensemble, delta P@1. paired bootstrap over 725 test sentences, 10,000 resamples, default_rng(20261114), percentile 95% CI | `results/comparisons.csv` | RECOMPUTED |
| `C2.p` | 0.048 |  | Fusion minus matcher ensemble, exact McNemar p. two-sided exact binomial on discordant pairs (51 vs 32) | `results/comparisons.csv` | RECOMPUTED |
| `C2.holm` | 0.190 |  | Fusion minus matcher ensemble, Holm-adjusted p. Holm step-down over the family of 8 tests (prereg 01) | `results/comparisons.csv` | RECOMPUTED |
| `C3` | +0.014 | [-0.014, 0.041] | RoBERTa minus SVM, delta P@1. paired bootstrap over 725 test sentences, 10,000 resamples, default_rng(20261114), percentile 95% CI | `results/comparisons.csv` | RECOMPUTED |
| `C3.holm` | 1.000 |  | RoBERTa minus SVM, Holm-adjusted p. Holm step-down over the family of 8 tests (prereg 01) | `results/comparisons.csv` | RECOMPUTED |
| `C4` | +0.001 | [-0.023, 0.025] | RoBERTa minus SecBERT, delta P@1. paired bootstrap over 725 test sentences, 10,000 resamples, default_rng(20261114), percentile 95% CI | `results/comparisons.csv` | RECOMPUTED |
| `C4.holm` | 1.000 |  | RoBERTa minus SecBERT, Holm-adjusted p. Holm step-down over the family of 8 tests (prereg 01) | `results/comparisons.csv` | RECOMPUTED |
| `G9.v2.success` | False |  | Support-aware fusion v2: pre-registered success rule met. Holm p < 0.05 vs (3,1,1,1), CI excluding 0, and rare-bucket P@1 rises | `results/support_aware_v2.csv` | RECOMPUTED |
| `G9.fam1` | +0.007 | [-0.001, 0.017] | support-aware v2 vs (3,1,1,1): delta P@1. paired bootstrap CI; exact McNemar p = 0.227; Holm p = 0.453 (family of 4) | `results/support_aware_family.csv` | RECOMPUTED |
| `G9.fam1.holm` | 0.453 |  | support-aware v2 vs (3,1,1,1): Holm-adjusted p. see above | `results/support_aware_family.csv` | RECOMPUTED |
| `G9.v2.rare` | 0.386 |  | Support-aware fusion v2: P@1 on rare-label sentences (support 0-4). n = 44; baseline (3,1,1,1) = 0.227 | `results/support_aware_v2.csv` | RECOMPUTED |
| `G9.v2.rare_base` | 0.227 |  | Fusion (3,1,1,1): P@1 on rare-label sentences (support 0-4). n = 44 | `results/support_aware_v2.csv` | RECOMPUTED |
| `G4.fusion.unseen` | 0.000 | [0.000, 0.000] | P@1 Fusion (3,1,1,1), rarest gold label train support unseen. test sentences whose rarest gold label has train support unseen; n = 10; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.matcher.unseen` | 0.200 | [0.000, 0.500] | P@1 Matcher (3-seed ens.), rarest gold label train support unseen. test sentences whose rarest gold label has train support unseen; n = 10; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.fusion.1_4` | 0.294 | [0.147, 0.441] | P@1 Fusion (3,1,1,1), rarest gold label train support 1-4. test sentences whose rarest gold label has train support 1-4; n = 34; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.matcher.1_4` | 0.559 | [0.382, 0.735] | P@1 Matcher (3-seed ens.), rarest gold label train support 1-4. test sentences whose rarest gold label has train support 1-4; n = 34; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G6.unseen_r5_fusion` | 0.50 |  | Unseen-label R@5, fusion. share of the 10 unseen gold (sentence, label) pairs found in the top 5 | `results/systems.csv` | RECOMPUTED |
| `D1` | -0.057 |  | Krippendorff alpha, nominal. two raters, 100 sentences, scale 0-2 | `Exp_3_0_shap/hand_check_v2_*.xlsx -> _evidence_pack/07_agreement.csv` | RECOMPUTED |
| `D2` | +0.031 |  | Krippendorff alpha, ordinal. two raters, 100 sentences, scale 0-2 | `Exp_3_0_shap/hand_check_v2_*.xlsx -> _evidence_pack/07_agreement.csv` | RECOMPUTED |
| `D5` | 3 |  | Sentences rated by the third rater. rated rows in the third rating sheet (of 100) | `Exp_3_0_shap/hand_check_v2_*.xlsx -> _evidence_pack/07_agreement.csv` | RECOMPUTED |
| `E4` | 108 of 725 (14.9%) |  | Test sentences where the explained model and the fusion output different top-1 labels. roberta_pw_s42 top-1 vs seed-averaged fusion top-1 | `results/explained_vs_fusion.csv` | RECOMPUTED |
| `E4.share` | 0.149 |  | Share of test sentences with different top-1 labels. see E4 | `results/explained_vs_fusion.csv` | RECOMPUTED |
| `G11.roberta` | 19 vs 17 of 34 |  | roberta_pw_s42: hits on the truncated sentences, 128 vs 256 tokens at inference. inference only (model trained at 128); gained 1, lost 3, exact McNemar p = 0.625 | `results/maxlen.csv` | RECOMPUTED |
| `G11.secbert` | 20 vs 20 of 34 |  | secbert_pw_s42: hits on the truncated sentences, 128 vs 256 tokens at inference. inference only (model trained at 128); gained 5, lost 5, exact McNemar p = 1.000 | `results/maxlen.csv` | RECOMPUTED |
| `F1` | 0.770 |  | Published baseline P@1 (Nguyen et al., TRAM, 'Asymmetric'). constant typed into the notebooks from the paper; confirmed against arXiv:2401.10337 Table 2 (not a project file); not re-run | `run_match_1/final_results_table.csv; _evidence_pack/08_baseline.md` | NOTES-ONLY |
| `F2` | 0.864 |  | Published baseline MRR@3. as F1 | `run_match_1/final_results_table.csv; _evidence_pack/08_baseline.md` | NOTES-ONLY |
| `B14.test3111` | 0.800 |  | Test P@1 of (3,1,1,1), matcher seed 42. reported, never used for selection | `results/weight_surface.csv` | RECOMPUTED |
| `B14.test4111` | 0.804 |  | Test P@1 of (4,1,1,1), matcher seed 42. reported, never used for selection | `results/weight_surface.csv` | RECOMPUTED |
| `T3.fusion_replication` | n/a |  | Fusion and ablation with the retrained matcher. replication of B12a/B13a | `notebooks/05_fusion_and_ablation.ipynb` | TODO-COLAB |
| `T4.seeds_45_46` | n/a |  | Five-seed means (seeds 42-46). prereg 10 | `notebooks/03_train_classifiers.ipynb, 04_train_matcher_save.ipynb` | TODO-COLAB |
| `T5.baseline_same_protocol` | n/a |  | Published baseline under our protocol. re-run of Nguyen et al. on the same split and metric code | `notebooks/09_baseline_same_protocol.ipynb` | TODO-COLAB |
| `T6.cross_dataset` | n/a |  | Objective (b): sibling datasets to TRAM test. prereg 11 | `notebooks/08_extension_cross_dataset.ipynb` | TODO-COLAB |
| `T8.human_study_v2` | n/a |  | Second human study (3+ raters, protocol). docs/HUMAN_STUDY_PROTOCOL.md | `scripts/make_rating_sheet.py` | TODO-COLAB |
| `T9.usability_sus` | n/a |  | Usability study of the explainer app (3-5 users, 5 tasks, SUS); author task, not Colab. design-science evaluation of the artefact | `ttp_app/usability/USABILITY_STUDY.md, ttp_app/usability/score_sus.py` | TODO-COLAB |
| `N1.tram_train_tsv` | n/a |  | Original tram_train.tsv. searched Dataset/ and the whole tree; rebuilt from combined_train.csv | `-` | NOT-FOUND |
| `N2.matcher_weights` | n/a |  | Original matcher weights. run_match_1/ holds score files only | `-` | NOT-FOUND |
| `N3.svm_scores` | n/a |  | Saved SVM scores. never written by any notebook; refit | `-` | NOT-FOUND |
| `N4.colab_env` | n/a |  | Colab environment of the original runs. no pip freeze saved | `-` | NOT-FOUND |
| `N5.git_history` | n/a |  | Git history of the original work. no repository existed before 2026-11-14 | `-` | NOT-FOUND |
| `N6.data_licence` | n/a |  | Dataset licence and source commit. no licence text in the folder | `-` | NOT-FOUND |
| `N7.attack_version_in_data` | n/a |  | ATT&CK version string inside a data file. only in notebook comments | `-` | NOT-FOUND |
| `N8.pre_dedup_size` | n/a |  | Train size before de-duplication. raw train file absent | `-` | NOT-FOUND |
| `N9.rater_roles` | n/a |  | Background of raters B and C. not recorded in any file | `-` | NOT-FOUND |
| `N10.training_times` | n/a |  | Classifier training times. not printed by the notebooks | `-` | NOT-FOUND |

## Tables (CSV for editing, markdown for reading)

- `tables/t_comparisons_holm.csv` / `.md`
- `tables/t_support_buckets.csv` / `.md`
- `tables/t_support_aware_family.csv` / `.md`
- `tables/t_human_agreement.csv` / `.md`

## Figures (in `../figures/`, PNG 300 dpi and SVG; alt text in `../figures/FIGURES.md`)

- `fig06_support_buckets.png`
- `fig10_fixed_broken.png`
- `fig18_status_board.png`

## Caveats to state

- Human study: agreement at chance (-0.057); no plausibility claim can rest on it.
- The explained model and the fusion disagree on the top-1 label for 108 of 725 (14.9%) test sentences.
- Fusion does not help unseen or rare techniques: P@1 0.000 (unseen) and 0.294 (1-4) vs matcher 0.200 and 0.559.
