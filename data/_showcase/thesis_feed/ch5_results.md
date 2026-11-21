# Chapter 5: Results: numbers, tables, figures, caveats

Every number below comes from `thesis_numbers.json` (do not retype; quote the id). Status meanings: RECOMPUTED = recomputed from saved predictions by a showcase script; VERIFIED = read from a file or code; NOTES-ONLY = a copied constant; TODO-COLAB = not yet run; NOT-FOUND = searched, absent.

## Numbers

| id | value | 95% CI | definition | source file | status |
|---|---|---|---|---|---|
| `ABL.A1` | +0.029 | [0.017, 0.043] | Fusion minus fusion without matcher, delta P@1. paired bootstrap over 725 test sentences, 10,000 resamples, default_rng(20261114), percentile 95% CI | `results/comparisons.csv` | RECOMPUTED |
| `ABL.A1.p` | 0.000 |  | Fusion minus fusion without matcher, exact McNemar p. two-sided exact binomial on discordant pairs (23 vs 2) | `results/comparisons.csv` | RECOMPUTED |
| `ABL.A1.holm` | 0.000 |  | Fusion minus fusion without matcher, Holm-adjusted p. Holm step-down over the family of 8 tests (prereg 01) | `results/comparisons.csv` | RECOMPUTED |
| `ABL.A1.mrr` | +0.019 | [0.010, 0.029] | Fusion minus fusion without matcher, delta MRR@3. paired bootstrap, as above | `results/comparisons.csv` | RECOMPUTED |
| `ABL.A2` | +0.004 | [-0.006, 0.015] | Fusion minus fusion without SVM, delta P@1. paired bootstrap over 725 test sentences, 10,000 resamples, default_rng(20261114), percentile 95% CI | `results/comparisons.csv` | RECOMPUTED |
| `ABL.A2.p` | 0.607 |  | Fusion minus fusion without SVM, exact McNemar p. two-sided exact binomial on discordant pairs (9 vs 6) | `results/comparisons.csv` | RECOMPUTED |
| `ABL.A2.holm` | 1.000 |  | Fusion minus fusion without SVM, Holm-adjusted p. Holm step-down over the family of 8 tests (prereg 01) | `results/comparisons.csv` | RECOMPUTED |
| `ABL.A2.mrr` | +0.003 | [-0.003, 0.009] | Fusion minus fusion without SVM, delta MRR@3. paired bootstrap, as above | `results/comparisons.csv` | RECOMPUTED |
| `ABL.A3` | +0.021 | [0.007, 0.034] | Fusion minus fusion without RoBERTa, delta P@1. paired bootstrap over 725 test sentences, 10,000 resamples, default_rng(20261114), percentile 95% CI | `results/comparisons.csv` | RECOMPUTED |
| `ABL.A3.p` | 0.006 |  | Fusion minus fusion without RoBERTa, exact McNemar p. two-sided exact binomial on discordant pairs (21 vs 6) | `results/comparisons.csv` | RECOMPUTED |
| `ABL.A3.holm` | 0.036 |  | Fusion minus fusion without RoBERTa, Holm-adjusted p. Holm step-down over the family of 8 tests (prereg 01) | `results/comparisons.csv` | RECOMPUTED |
| `ABL.A3.mrr` | +0.010 | [0.003, 0.018] | Fusion minus fusion without RoBERTa, delta MRR@3. paired bootstrap, as above | `results/comparisons.csv` | RECOMPUTED |
| `ABL.A4` | +0.012 | [0.003, 0.023] | Fusion minus fusion without SecBERT, delta P@1. paired bootstrap over 725 test sentences, 10,000 resamples, default_rng(20261114), percentile 95% CI | `results/comparisons.csv` | RECOMPUTED |
| `ABL.A4.p` | 0.035 |  | Fusion minus fusion without SecBERT, exact McNemar p. two-sided exact binomial on discordant pairs (12 vs 3) | `results/comparisons.csv` | RECOMPUTED |
| `ABL.A4.holm` | 0.176 |  | Fusion minus fusion without SecBERT, Holm-adjusted p. Holm step-down over the family of 8 tests (prereg 01) | `results/comparisons.csv` | RECOMPUTED |
| `ABL.A4.mrr` | +0.005 | [-0.003, 0.012] | Fusion minus fusion without SecBERT, delta MRR@3. paired bootstrap, as above | `results/comparisons.csv` | RECOMPUTED |
| `ABL.full` | 0.803 | [0.774, 0.832] | P@1 Fusion (3,1,1,1). seed-averaged components; one weight set to 0 | `results/ablation.csv` | RECOMPUTED |
| `ABL.no_matcher` | 0.774 | [0.742, 0.804] | P@1 Fusion without matcher. seed-averaged components; one weight set to 0 | `results/ablation.csv` | RECOMPUTED |
| `ABL.no_svm` | 0.799 | [0.768, 0.828] | P@1 Fusion without svm. seed-averaged components; one weight set to 0 | `results/ablation.csv` | RECOMPUTED |
| `ABL.no_roberta` | 0.782 | [0.752, 0.812] | P@1 Fusion without roberta. seed-averaged components; one weight set to 0 | `results/ablation.csv` | RECOMPUTED |
| `ABL.no_secbert` | 0.790 | [0.760, 0.819] | P@1 Fusion without secbert. seed-averaged components; one weight set to 0 | `results/ablation.csv` | RECOMPUTED |
| `G1.prior_microf1_notebook` | 0.047 |  | Frequency prior micro-F1 (notebook). always predict the most frequent training label | `results/f1_variants.csv` | RECOMPUTED |
| `G1.prior_microf1_seen_test` | 0.047 |  | Frequency prior micro-F1 (seen_test). always predict the most frequent training label | `results/f1_variants.csv` | RECOMPUTED |
| `G1.prior_microf1_all_test` | 0.047 |  | Frequency prior micro-F1 (all_test). always predict the most frequent training label | `results/f1_variants.csv` | RECOMPUTED |
| `G2.roberta.micro.notebook` | 0.705 |  | micro-F1 RoBERTa, variant notebook. mean over seeds (single run for SVM); see docs/THESIS_MAP for the three variants | `results/f1_variants.csv` | RECOMPUTED |
| `G2.roberta.macro.notebook` | 0.563 |  | macro-F1 RoBERTa, variant notebook. mean over seeds | `results/f1_variants.csv` | RECOMPUTED |
| `G2.roberta.micro.seen_test` | 0.701 |  | micro-F1 RoBERTa, variant seen_test. mean over seeds (single run for SVM); see docs/THESIS_MAP for the three variants | `results/f1_variants.csv` | RECOMPUTED |
| `G2.roberta.macro.seen_test` | 0.563 |  | macro-F1 RoBERTa, variant seen_test. mean over seeds | `results/f1_variants.csv` | RECOMPUTED |
| `G2.roberta.micro.all_test` | 0.701 |  | micro-F1 RoBERTa, variant all_test. mean over seeds (single run for SVM); see docs/THESIS_MAP for the three variants | `results/f1_variants.csv` | RECOMPUTED |
| `G2.roberta.macro.all_test` | 0.519 |  | macro-F1 RoBERTa, variant all_test. mean over seeds | `results/f1_variants.csv` | RECOMPUTED |
| `G2.secbert.micro.notebook` | 0.703 |  | micro-F1 SecBERT, variant notebook. mean over seeds (single run for SVM); see docs/THESIS_MAP for the three variants | `results/f1_variants.csv` | RECOMPUTED |
| `G2.secbert.macro.notebook` | 0.543 |  | macro-F1 SecBERT, variant notebook. mean over seeds | `results/f1_variants.csv` | RECOMPUTED |
| `G2.secbert.micro.seen_test` | 0.699 |  | micro-F1 SecBERT, variant seen_test. mean over seeds (single run for SVM); see docs/THESIS_MAP for the three variants | `results/f1_variants.csv` | RECOMPUTED |
| `G2.secbert.macro.seen_test` | 0.543 |  | macro-F1 SecBERT, variant seen_test. mean over seeds | `results/f1_variants.csv` | RECOMPUTED |
| `G2.secbert.micro.all_test` | 0.699 |  | micro-F1 SecBERT, variant all_test. mean over seeds (single run for SVM); see docs/THESIS_MAP for the three variants | `results/f1_variants.csv` | RECOMPUTED |
| `G2.secbert.macro.all_test` | 0.500 |  | macro-F1 SecBERT, variant all_test. mean over seeds | `results/f1_variants.csv` | RECOMPUTED |
| `G2.svm.micro.notebook` | 0.696 |  | micro-F1 TF-IDF + SVM, variant notebook. mean over seeds (single run for SVM); see docs/THESIS_MAP for the three variants | `results/f1_variants.csv` | RECOMPUTED |
| `G2.svm.macro.notebook` | 0.543 |  | macro-F1 TF-IDF + SVM, variant notebook. mean over seeds | `results/f1_variants.csv` | RECOMPUTED |
| `G2.svm.micro.seen_test` | 0.692 |  | micro-F1 TF-IDF + SVM, variant seen_test. mean over seeds (single run for SVM); see docs/THESIS_MAP for the three variants | `results/f1_variants.csv` | RECOMPUTED |
| `G2.svm.macro.seen_test` | 0.543 |  | macro-F1 TF-IDF + SVM, variant seen_test. mean over seeds | `results/f1_variants.csv` | RECOMPUTED |
| `G2.svm.micro.all_test` | 0.692 |  | micro-F1 TF-IDF + SVM, variant all_test. mean over seeds (single run for SVM); see docs/THESIS_MAP for the three variants | `results/f1_variants.csv` | RECOMPUTED |
| `G2.svm.macro.all_test` | 0.500 |  | macro-F1 TF-IDF + SVM, variant all_test. mean over seeds | `results/f1_variants.csv` | RECOMPUTED |
| `G3.roberta.thr_old` | 0.85 / 0.85 / 0.85 |  | roberta dev thresholds, original grid. grid 0.10-0.85 step 0.05, seeds 42-44 | `results/threshold_grid.csv` | RECOMPUTED |
| `G3.roberta.thr_new` | 0.93 / 0.83 / 0.88 |  | roberta dev thresholds, extended grid. grid 0.10-0.99 step 0.01, seeds 42-44 | `results/threshold_grid.csv` | RECOMPUTED |
| `G3.roberta.delta` | -0.0006 |  | roberta test micro-F1 change with the extended threshold grid. mean over seeds of (extended - original); threshold chosen on dev | `results/threshold_grid.csv` | RECOMPUTED |
| `G3.secbert.thr_old` | 0.75 / 0.65 / 0.70 |  | secbert dev thresholds, original grid. grid 0.10-0.85 step 0.05, seeds 42-44 | `results/threshold_grid.csv` | RECOMPUTED |
| `G3.secbert.thr_new` | 0.75 / 0.73 / 0.58 |  | secbert dev thresholds, extended grid. grid 0.10-0.99 step 0.01, seeds 42-44 | `results/threshold_grid.csv` | RECOMPUTED |
| `G3.secbert.delta` | -0.0007 |  | secbert test micro-F1 change with the extended threshold grid. mean over seeds of (extended - original); threshold chosen on dev | `results/threshold_grid.csv` | RECOMPUTED |
| `G4.svm.unseen` | 0.000 | [0.000, 0.000] | P@1 TF-IDF + SVM, rarest gold label train support unseen. test sentences whose rarest gold label has train support unseen; n = 10; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.roberta.unseen` | 0.000 | [0.000, 0.000] | P@1 RoBERTa (3-seed avg), rarest gold label train support unseen. test sentences whose rarest gold label has train support unseen; n = 10; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.secbert.unseen` | 0.000 | [0.000, 0.000] | P@1 SecBERT (3-seed avg), rarest gold label train support unseen. test sentences whose rarest gold label has train support unseen; n = 10; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.matcher.unseen` | 0.200 | [0.000, 0.500] | P@1 Matcher (3-seed ens.), rarest gold label train support unseen. test sentences whose rarest gold label has train support unseen; n = 10; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.fusion.unseen` | 0.000 | [0.000, 0.000] | P@1 Fusion (3,1,1,1), rarest gold label train support unseen. test sentences whose rarest gold label has train support unseen; n = 10; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.svm.1_4` | 0.206 | [0.088, 0.353] | P@1 TF-IDF + SVM, rarest gold label train support 1-4. test sentences whose rarest gold label has train support 1-4; n = 34; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.roberta.1_4` | 0.294 | [0.147, 0.441] | P@1 RoBERTa (3-seed avg), rarest gold label train support 1-4. test sentences whose rarest gold label has train support 1-4; n = 34; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.secbert.1_4` | 0.176 | [0.059, 0.324] | P@1 SecBERT (3-seed avg), rarest gold label train support 1-4. test sentences whose rarest gold label has train support 1-4; n = 34; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.matcher.1_4` | 0.559 | [0.382, 0.735] | P@1 Matcher (3-seed ens.), rarest gold label train support 1-4. test sentences whose rarest gold label has train support 1-4; n = 34; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.fusion.1_4` | 0.294 | [0.147, 0.441] | P@1 Fusion (3,1,1,1), rarest gold label train support 1-4. test sentences whose rarest gold label has train support 1-4; n = 34; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.svm.5_9` | 0.400 | [0.233, 0.567] | P@1 TF-IDF + SVM, rarest gold label train support 5-9. test sentences whose rarest gold label has train support 5-9; n = 30; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.roberta.5_9` | 0.500 | [0.333, 0.667] | P@1 RoBERTa (3-seed avg), rarest gold label train support 5-9. test sentences whose rarest gold label has train support 5-9; n = 30; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.secbert.5_9` | 0.400 | [0.233, 0.567] | P@1 SecBERT (3-seed avg), rarest gold label train support 5-9. test sentences whose rarest gold label has train support 5-9; n = 30; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.matcher.5_9` | 0.600 | [0.433, 0.767] | P@1 Matcher (3-seed ens.), rarest gold label train support 5-9. test sentences whose rarest gold label has train support 5-9; n = 30; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.fusion.5_9` | 0.567 | [0.400, 0.733] | P@1 Fusion (3,1,1,1), rarest gold label train support 5-9. test sentences whose rarest gold label has train support 5-9; n = 30; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.svm.10_19` | 0.606 | [0.485, 0.727] | P@1 TF-IDF + SVM, rarest gold label train support 10-19. test sentences whose rarest gold label has train support 10-19; n = 66; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.roberta.10_19` | 0.636 | [0.515, 0.742] | P@1 RoBERTa (3-seed avg), rarest gold label train support 10-19. test sentences whose rarest gold label has train support 10-19; n = 66; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.secbert.10_19` | 0.697 | [0.591, 0.803] | P@1 SecBERT (3-seed avg), rarest gold label train support 10-19. test sentences whose rarest gold label has train support 10-19; n = 66; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.matcher.10_19` | 0.667 | [0.545, 0.773] | P@1 Matcher (3-seed ens.), rarest gold label train support 10-19. test sentences whose rarest gold label has train support 10-19; n = 66; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.fusion.10_19` | 0.712 | [0.606, 0.818] | P@1 Fusion (3,1,1,1), rarest gold label train support 10-19. test sentences whose rarest gold label has train support 10-19; n = 66; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.svm.20_49` | 0.722 | [0.662, 0.782] | P@1 TF-IDF + SVM, rarest gold label train support 20-49. test sentences whose rarest gold label has train support 20-49; n = 216; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.roberta.20_49` | 0.759 | [0.699, 0.815] | P@1 RoBERTa (3-seed avg), rarest gold label train support 20-49. test sentences whose rarest gold label has train support 20-49; n = 216; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.secbert.20_49` | 0.755 | [0.694, 0.810] | P@1 SecBERT (3-seed avg), rarest gold label train support 20-49. test sentences whose rarest gold label has train support 20-49; n = 216; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.matcher.20_49` | 0.750 | [0.690, 0.806] | P@1 Matcher (3-seed ens.), rarest gold label train support 20-49. test sentences whose rarest gold label has train support 20-49; n = 216; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.fusion.20_49` | 0.819 | [0.764, 0.870] | P@1 Fusion (3,1,1,1), rarest gold label train support 20-49. test sentences whose rarest gold label has train support 20-49; n = 216; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.svm.50plus` | 0.875 | [0.840, 0.908] | P@1 TF-IDF + SVM, rarest gold label train support 50+. test sentences whose rarest gold label has train support 50+; n = 369; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.roberta.50plus` | 0.859 | [0.824, 0.894] | P@1 RoBERTa (3-seed avg), rarest gold label train support 50+. test sentences whose rarest gold label has train support 50+; n = 369; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.secbert.50plus` | 0.867 | [0.832, 0.900] | P@1 SecBERT (3-seed avg), rarest gold label train support 50+. test sentences whose rarest gold label has train support 50+; n = 369; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.matcher.50plus` | 0.862 | [0.827, 0.897] | P@1 Matcher (3-seed ens.), rarest gold label train support 50+. test sentences whose rarest gold label has train support 50+; n = 369; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.fusion.50plus` | 0.897 | [0.864, 0.927] | P@1 Fusion (3,1,1,1), rarest gold label train support 50+. test sentences whose rarest gold label has train support 50+; n = 369; 95% bootstrap CI | `results/support_buckets.csv` | RECOMPUTED |
| `G4.n.unseen` | 10 |  | Test sentences in support bucket unseen. see G4 | `results/support_buckets.csv` | RECOMPUTED |
| `G4.n.1_4` | 34 |  | Test sentences in support bucket 1-4. see G4 | `results/support_buckets.csv` | RECOMPUTED |
| `G4.n.5_9` | 30 |  | Test sentences in support bucket 5-9. see G4 | `results/support_buckets.csv` | RECOMPUTED |
| `G4.n.10_19` | 66 |  | Test sentences in support bucket 10-19. see G4 | `results/support_buckets.csv` | RECOMPUTED |
| `G4.n.20_49` | 216 |  | Test sentences in support bucket 20-49. see G4 | `results/support_buckets.csv` | RECOMPUTED |
| `G4.n.50plus` | 369 |  | Test sentences in support bucket 50+. see G4 | `results/support_buckets.csv` | RECOMPUTED |
| `G5.matcher.unseen` | -0.200 | [-0.500, 0.000] | Fusion minus Matcher (3-seed ens.), support unseen. paired delta P@1 with 95% bootstrap CI; n = 10; fixed 0, broken 2 | `results/fixed_broken.csv` | RECOMPUTED |
| `G5.clsonly.unseen` | +0.000 | [0.000, 0.000] | Fusion minus Classifiers-only ens., support unseen. paired delta P@1 with 95% bootstrap CI; n = 10; fixed 0, broken 0 | `results/fixed_broken.csv` | RECOMPUTED |
| `G5.matcher.1_4` | -0.265 | [-0.441, -0.088] | Fusion minus Matcher (3-seed ens.), support 1-4. paired delta P@1 with 95% bootstrap CI; n = 34; fixed 1, broken 10 | `results/fixed_broken.csv` | RECOMPUTED |
| `G5.clsonly.1_4` | +0.118 | [0.029, 0.235] | Fusion minus Classifiers-only ens., support 1-4. paired delta P@1 with 95% bootstrap CI; n = 34; fixed 4, broken 0 | `results/fixed_broken.csv` | RECOMPUTED |
| `G5.matcher.5_9` | -0.033 | [-0.167, 0.100] | Fusion minus Matcher (3-seed ens.), support 5-9. paired delta P@1 with 95% bootstrap CI; n = 30; fixed 2, broken 3 | `results/fixed_broken.csv` | RECOMPUTED |
| `G5.clsonly.5_9` | +0.100 | [0.000, 0.201] | Fusion minus Classifiers-only ens., support 5-9. paired delta P@1 with 95% bootstrap CI; n = 30; fixed 3, broken 0 | `results/fixed_broken.csv` | RECOMPUTED |
| `G5.matcher.10_19` | +0.045 | [-0.045, 0.136] | Fusion minus Matcher (3-seed ens.), support 10-19. paired delta P@1 with 95% bootstrap CI; n = 66; fixed 6, broken 3 | `results/fixed_broken.csv` | RECOMPUTED |
| `G5.clsonly.10_19` | +0.045 | [0.000, 0.106] | Fusion minus Classifiers-only ens., support 10-19. paired delta P@1 with 95% bootstrap CI; n = 66; fixed 3, broken 0 | `results/fixed_broken.csv` | RECOMPUTED |
| `G5.matcher.20_49` | +0.069 | [0.019, 0.120] | Fusion minus Matcher (3-seed ens.), support 20-49. paired delta P@1 with 95% bootstrap CI; n = 216; fixed 23, broken 8 | `results/fixed_broken.csv` | RECOMPUTED |
| `G5.clsonly.20_49` | +0.032 | [0.009, 0.060] | Fusion minus Classifiers-only ens., support 20-49. paired delta P@1 with 95% bootstrap CI; n = 216; fixed 8, broken 1 | `results/fixed_broken.csv` | RECOMPUTED |
| `G5.matcher.50plus` | +0.035 | [0.011, 0.062] | Fusion minus Matcher (3-seed ens.), support 50+. paired delta P@1 with 95% bootstrap CI; n = 369; fixed 19, broken 6 | `results/fixed_broken.csv` | RECOMPUTED |
| `G5.clsonly.50plus` | +0.011 | [0.000, 0.024] | Fusion minus Classifiers-only ens., support 50+. paired delta P@1 with 95% bootstrap CI; n = 369; fixed 5, broken 1 | `results/fixed_broken.csv` | RECOMPUTED |
| `G5.matcher.total` | 51 / 32 |  | Sentences fixed / broken by the fusion vs Matcher (3-seed ens.). fusion right & reference wrong / fusion wrong & reference right | `results/fixed_broken.csv` | RECOMPUTED |
| `G5.clsonly.total` | 23 / 2 |  | Sentences fixed / broken by the fusion vs Classifiers-only ens.. fusion right & reference wrong / fusion wrong & reference right | `results/fixed_broken.csv` | RECOMPUTED |
| `G6.unseen_r5_fusion` | 0.50 |  | Unseen-label R@5, fusion. share of the 10 unseen gold (sentence, label) pairs found in the top 5 | `results/systems.csv` | RECOMPUTED |
| `G6.unseen_r5_clsonly` | 0.00 |  | Unseen-label R@5, classifiers-only. as above; classifiers cannot output unseen labels | `results/systems.csv` | RECOMPUTED |
| `G6.unseen_r5_matcher` | 0.60 |  | Unseen-label R@5, matcher ensemble. as above | `results/systems.csv` | RECOMPUTED |
| `G7.ece.roberta` | 0.172 +/- 0.007 |  | ECE roberta (3 seeds). 10 equal-width bins; confidence = probability of the top-1 label; mean +/- sd over seeds | `results/calibration.csv` | RECOMPUTED |
| `G7.conf.roberta` | 0.913 |  | Mean top-1 confidence roberta. mean over seeds | `results/calibration.csv` | RECOMPUTED |
| `G7.ece.secbert` | 0.138 +/- 0.012 |  | ECE secbert (3 seeds). 10 equal-width bins; confidence = probability of the top-1 label; mean +/- sd over seeds | `results/calibration.csv` | RECOMPUTED |
| `G7.conf.secbert` | 0.867 |  | Mean top-1 confidence secbert. mean over seeds | `results/calibration.csv` | RECOMPUTED |
| `G8.family_errors.svm` | 7 of 187 |  | TF-IDF + SVM: errors inside the gold label's technique family. wrong top-1 that is the parent, a sub-technique or a sibling of a gold label / all wrong top-1 | `results/parent_sub.csv` | RECOMPUTED |
| `G8.techlevel.svm` | 0.752 |  | TF-IDF + SVM: technique-level P@1. prediction and gold reduced to the parent technique | `results/parent_sub.csv` | RECOMPUTED |
| `G8.family_errors.roberta` | 5 of 177 |  | RoBERTa (3-seed avg): errors inside the gold label's technique family. wrong top-1 that is the parent, a sub-technique or a sibling of a gold label / all wrong top-1 | `results/parent_sub.csv` | RECOMPUTED |
| `G8.techlevel.roberta` | 0.763 |  | RoBERTa (3-seed avg): technique-level P@1. prediction and gold reduced to the parent technique | `results/parent_sub.csv` | RECOMPUTED |
| `G8.family_errors.secbert` | 5 of 178 |  | SecBERT (3-seed avg): errors inside the gold label's technique family. wrong top-1 that is the parent, a sub-technique or a sibling of a gold label / all wrong top-1 | `results/parent_sub.csv` | RECOMPUTED |
| `G8.techlevel.secbert` | 0.761 |  | SecBERT (3-seed avg): technique-level P@1. prediction and gold reduced to the parent technique | `results/parent_sub.csv` | RECOMPUTED |
| `G8.family_errors.matcher` | 5 of 162 |  | Matcher (3-seed ens.): errors inside the gold label's technique family. wrong top-1 that is the parent, a sub-technique or a sibling of a gold label / all wrong top-1 | `results/parent_sub.csv` | RECOMPUTED |
| `G8.techlevel.matcher` | 0.783 |  | Matcher (3-seed ens.): technique-level P@1. prediction and gold reduced to the parent technique | `results/parent_sub.csv` | RECOMPUTED |
| `G8.family_errors.fusion` | 4 of 143 |  | Fusion (3,1,1,1): errors inside the gold label's technique family. wrong top-1 that is the parent, a sub-technique or a sibling of a gold label / all wrong top-1 | `results/parent_sub.csv` | RECOMPUTED |
| `G8.techlevel.fusion` | 0.808 |  | Fusion (3,1,1,1): technique-level P@1. prediction and gold reduced to the parent technique | `results/parent_sub.csv` | RECOMPUTED |
| `G9.v2.weights` | (3, 6, 4, 4) |  | Support-aware fusion v2: dev-selected matcher weights (unseen, 1-4, 5-19, 20+). prereg 13; 1,296 dev settings | `results/support_aware_v2.csv` | RECOMPUTED |
| `G9.v2.p1` | 0.810 |  | Support-aware fusion v2: test P@1. single test evaluation of the dev-selected setting | `results/support_aware_v2.csv` | RECOMPUTED |
| `G9.v2.rare` | 0.386 |  | Support-aware fusion v2: P@1 on rare-label sentences (support 0-4). n = 44; baseline (3,1,1,1) = 0.227 | `results/support_aware_v2.csv` | RECOMPUTED |
| `G9.v2.rare_base` | 0.227 |  | Fusion (3,1,1,1): P@1 on rare-label sentences (support 0-4). n = 44 | `results/support_aware_v2.csv` | RECOMPUTED |
| `G9.v2.success` | False |  | Support-aware fusion v2: pre-registered success rule met. Holm p < 0.05 vs (3,1,1,1), CI excluding 0, and rare-bucket P@1 rises | `results/support_aware_v2.csv` | RECOMPUTED |
| `G9.fam1` | +0.007 | [-0.001, 0.017] | support-aware v2 vs (3,1,1,1): delta P@1. paired bootstrap CI; exact McNemar p = 0.227; Holm p = 0.453 (family of 4) | `results/support_aware_family.csv` | RECOMPUTED |
| `G9.fam1.holm` | 0.453 |  | support-aware v2 vs (3,1,1,1): Holm-adjusted p. see above | `results/support_aware_family.csv` | RECOMPUTED |
| `G9.fam2` | +0.001 | [-0.007, 0.010] | support-aware v2 vs (4,1,1,1): delta P@1. paired bootstrap CI; exact McNemar p = 1.000; Holm p = 1.000 (family of 4) | `results/support_aware_family.csv` | RECOMPUTED |
| `G9.fam2.holm` | 1.000 |  | support-aware v2 vs (4,1,1,1): Holm-adjusted p. see above | `results/support_aware_family.csv` | RECOMPUTED |
| `G9.fam3` | +0.028 | [0.017, 0.040] | support-aware v2 vs equal (1,1,1,1): delta P@1. paired bootstrap CI; exact McNemar p = 0.000; Holm p = 0.000 (family of 4) | `results/support_aware_family.csv` | RECOMPUTED |
| `G9.fam3.holm` | 0.000 |  | support-aware v2 vs equal (1,1,1,1): Holm-adjusted p. see above | `results/support_aware_family.csv` | RECOMPUTED |
| `G9.fam4` | +0.006 | [0.001, 0.011] | support-aware v1 (prereg 09) vs (3,1,1,1): delta P@1. paired bootstrap CI; exact McNemar p = 0.125; Holm p = 0.375 (family of 4) | `results/support_aware_family.csv` | RECOMPUTED |
| `G9.fam4.holm` | 0.375 |  | support-aware v1 (prereg 09) vs (3,1,1,1): Holm-adjusted p. see above | `results/support_aware_family.csv` | RECOMPUTED |
| `G9.v1.weights` | (4, 4, 4) |  | Support-aware fusion v1 (three bands): dev-selected matcher weights. prereg 09; bands 0-4, 5-19, 20+ | `results/support_aware_fusion.csv` | RECOMPUTED |
| `G11.roberta` | 19 vs 17 of 34 |  | roberta_pw_s42: hits on the truncated sentences, 128 vs 256 tokens at inference. inference only (model trained at 128); gained 1, lost 3, exact McNemar p = 0.625 | `results/maxlen.csv` | RECOMPUTED |
| `G11.secbert` | 20 vs 20 of 34 |  | secbert_pw_s42: hits on the truncated sentences, 128 vs 256 tokens at inference. inference only (model trained at 128); gained 5, lost 5, exact McNemar p = 1.000 | `results/maxlen.csv` | RECOMPUTED |
| `G2.roberta.micro_drop` | 0.0043 |  | micro-F1 RoBERTa: drop when unseen gold labels count as misses. 3-seed mean of (notebook variant - all_test variant) | `results/per_seed.csv` | RECOMPUTED |
| `G2.secbert.micro_drop` | 0.0042 |  | micro-F1 SecBERT: drop when unseen gold labels count as misses. 3-seed mean of (notebook variant - all_test variant) | `results/per_seed.csv` | RECOMPUTED |
| `G4.svm.5_19` | 0.542 |  | P@1 TF-IDF + SVM, rarest gold label train support 5-19. n-weighted mean of buckets 5-9 and 10-19; n = 96; no CI (merged after the fact) | `results/support_buckets.csv` | RECOMPUTED |
| `G4.roberta.5_19` | 0.594 |  | P@1 RoBERTa (3-seed avg), rarest gold label train support 5-19. n-weighted mean of buckets 5-9 and 10-19; n = 96; no CI (merged after the fact) | `results/support_buckets.csv` | RECOMPUTED |
| `G4.secbert.5_19` | 0.604 |  | P@1 SecBERT (3-seed avg), rarest gold label train support 5-19. n-weighted mean of buckets 5-9 and 10-19; n = 96; no CI (merged after the fact) | `results/support_buckets.csv` | RECOMPUTED |
| `G4.matcher.5_19` | 0.646 |  | P@1 Matcher (3-seed ens.), rarest gold label train support 5-19. n-weighted mean of buckets 5-9 and 10-19; n = 96; no CI (merged after the fact) | `results/support_buckets.csv` | RECOMPUTED |
| `G4.fusion.5_19` | 0.667 |  | P@1 Fusion (3,1,1,1), rarest gold label train support 5-19. n-weighted mean of buckets 5-9 and 10-19; n = 96; no CI (merged after the fact) | `results/support_buckets.csv` | RECOMPUTED |
| `G4.n.5_19` | 96 |  | Test sentences in support buckets 5-9 and 10-19 together. sum of the two bucket sizes | `results/support_buckets.csv` | RECOMPUTED |

## Tables (CSV for editing, markdown for reading)

- `tables/t_systems.csv` / `.md`
- `tables/t_fusion_definitions.csv` / `.md`
- `tables/t_per_seed.csv` / `.md`
- `tables/t_f1_variants.csv` / `.md`
- `tables/t_comparisons_holm.csv` / `.md`
- `tables/t_ablation.csv` / `.md`
- `tables/t_support_buckets.csv` / `.md`
- `tables/t_fixed_broken.csv` / `.md`
- `tables/t_tactics.csv` / `.md`
- `tables/t_top_confusions.csv` / `.md`
- `tables/t_parent_sub.csv` / `.md`
- `tables/t_calibration.csv` / `.md`
- `tables/t_faithfulness.csv` / `.md`
- `tables/t_maxlen_128_vs_256.csv` / `.md`
- `tables/t_threshold_grid.csv` / `.md`
- `tables/t_support_aware_family.csv` / `.md`
- `tables/t_human_agreement.csv` / `.md`

## Figures (in `../figures/`, PNG 300 dpi and SVG; alt text in `../figures/FIGURES.md`)

- `fig05_all_systems.png`
- `fig07_forest_deltas.png`
- `fig09_ablation.png`
- `fig08_weight_sensitivity.png`
- `fig06_support_buckets.png`
- `fig10_fixed_broken.png`
- `fig11_tactic_heatmap.png`
- `fig12_top_confusions.png`
- `fig13_reliability.png`
- `fig15_faithfulness_curves.png`
- `fig14_shap_examples.png`
- `fig19_human_agreement.png`

## Caveats to state

- Bootstrap: 10,000 resamples, numpy default_rng(20261114), sentence-level, percentile 95% CI. The notebooks used 1,000 resamples with seed 0; do not mix the two.
- F1 in the notebooks ignores the 10 unseen test labels; say which variant a number uses.
- P@1 of RoBERTa 0.756 and SecBERT 0.754 are 3-seed ensembles; single-seed means are 0.752 +/- 0.007 and 0.743 +/- 0.004.
- Buckets with few sentences (unseen n = 10, 1-4 n = 34) have wide intervals; report direction, not size.
- Support-aware fusion was pre-registered and failed its success rule; it is a negative result, not an improvement.

See also `FUSION_DEFINITIONS.md`, `NEW_FINDINGS.md`, `DIFFERENCES.md`, `DO_NOT_CLAIM.md`.
