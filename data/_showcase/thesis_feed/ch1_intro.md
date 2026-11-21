# Chapter 1: Introduction: numbers, tables, figures, caveats

Every number below comes from `thesis_numbers.json` (do not retype; quote the id). Status meanings: RECOMPUTED = recomputed from saved predictions by a showcase script; VERIFIED = read from a file or code; NOTES-ONLY = a copied constant; TODO-COLAB = not yet run; NOT-FOUND = searched, absent.

## Numbers

| id | value | 95% CI | definition | source file | status |
|---|---|---|---|---|---|
| `A1` | 4,797 |  | Total sentences. train + dev + test rows | `Dataset/combined_train.csv[tram], tram_dev.tsv, tram_test.tsv -> results/tables/sentences.parquet` | RECOMPUTED |
| `A2` | 3,468 / 604 / 725 |  | Train / dev / test sentences. rows per split; train after exact-text de-duplication | `Dataset/combined_train.csv[tram], tram_dev.tsv, tram_test.tsv -> results/tables/sentences.parquet` | RECOMPUTED |
| `A3` | 180 |  | Train labels. distinct technique ids with at least one training sentence | `results/tables/techniques.parquet` | RECOMPUTED |
| `A4` | 127 |  | Test labels. distinct technique ids in the test split | `results/tables/techniques.parquet` | RECOMPUTED |
| `A5` | 117 + 10 |  | Seen + unseen test labels. test labels with / without a training sentence | `results/tables/techniques.parquet` | RECOMPUTED |
| `B13a` | 0.803 | [0.774, 0.832] | P@1 fusion (3,1,1,1), seed-averaged. all components averaged over seeds 42-44 before fusing; one system, 95% bootstrap CI over test sentences | `saved predictions -> results/systems.csv` | RECOMPUTED |
| `B12a` | 0.796 +/- 0.006 |  | P@1 fusion (3,1,1,1), seed-paired. matcher, RoBERTa and SecBERT all from seed s; mean +/- sd over s = 42, 43, 44 | `saved predictions -> results/per_seed.csv` | RECOMPUTED |
| `B12nb` | 0.800 +/- 0.001 |  | P@1 fusion (3,1,1,1), notebook definition. matcher seed s with 3-seed-averaged classifiers; mean +/- sd over s (Exp_2.1 CELL 11, final_results_table.csv) | `saved predictions -> results/per_seed.csv` | RECOMPUTED |
| `C1` | +0.029 | [0.017, 0.043] | Fusion minus classifiers-only, delta P@1. paired bootstrap over 725 test sentences, 10,000 resamples, default_rng(20261114), percentile 95% CI | `results/comparisons.csv` | RECOMPUTED |
| `C1.holm` | 0.000 |  | Fusion minus classifiers-only, Holm-adjusted p. Holm step-down over the family of 8 tests (prereg 01) | `results/comparisons.csv` | RECOMPUTED |
| `C2` | +0.026 | [0.001, 0.051] | Fusion minus matcher ensemble, delta P@1. paired bootstrap over 725 test sentences, 10,000 resamples, default_rng(20261114), percentile 95% CI | `results/comparisons.csv` | RECOMPUTED |
| `C2.holm` | 0.190 |  | Fusion minus matcher ensemble, Holm-adjusted p. Holm step-down over the family of 8 tests (prereg 01) | `results/comparisons.csv` | RECOMPUTED |
| `C3` | +0.014 | [-0.014, 0.041] | RoBERTa minus SVM, delta P@1. paired bootstrap over 725 test sentences, 10,000 resamples, default_rng(20261114), percentile 95% CI | `results/comparisons.csv` | RECOMPUTED |
| `C3.holm` | 1.000 |  | RoBERTa minus SVM, Holm-adjusted p. Holm step-down over the family of 8 tests (prereg 01) | `results/comparisons.csv` | RECOMPUTED |
| `E2.all` | 10.13 |  | Deletion test difference on all eligible test sentences. as E2, all test sentences | `_evidence_pack/06_deletion_test_725.csv` | RECOMPUTED |
| `E3.all` | 644 / 645 |  | Top-3 larger than random, all eligible test sentences. as E3, all test sentences | `_evidence_pack/06_deletion_test_725.csv` | RECOMPUTED |
| `D1` | -0.057 |  | Krippendorff alpha, nominal. two raters, 100 sentences, scale 0-2 | `Exp_3_0_shap/hand_check_v2_*.xlsx -> _evidence_pack/07_agreement.csv` | RECOMPUTED |
| `F1` | 0.770 |  | Published baseline P@1 (Nguyen et al., TRAM, 'Asymmetric'). constant typed into the notebooks from the paper; confirmed against arXiv:2401.10337 Table 2 (not a project file); not re-run | `run_match_1/final_results_table.csv; _evidence_pack/08_baseline.md` | NOTES-ONLY |
| `F2` | 0.864 |  | Published baseline MRR@3. as F1 | `run_match_1/final_results_table.csv; _evidence_pack/08_baseline.md` | NOTES-ONLY |

## Figures (in `../figures/`, PNG 300 dpi and SVG; alt text in `../figures/FIGURES.md`)

- `fig01_architecture.png`

## Caveats to state

- Headline P@1 depends on the fusion definition: 0.803 seed-averaged, 0.796 +/- 0.006 seed-paired, 0.800 +/- 0.001 notebook. Name the one used.
- The gain over the matcher ensemble (+0.026) is not supported after Holm correction (p = 0.190). Do not list it as a contribution.
- Explanations are for one RoBERTa seed, not for the fusion.
