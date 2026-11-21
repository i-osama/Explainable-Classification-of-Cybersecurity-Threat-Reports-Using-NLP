# 03 Results recomputed from saved predictions

One metric implementation (`scripts/common.py`): ranking by descending score, **ties broken by lower label index (stable sort)**; P@1 = share of sentences whose top-1 label is gold; MRR@3 = mean of 1/rank of first gold label in top 3 (0 if none); P@3 = (#gold in top 3)/3 averaged over sentences. All ranking metrics are computed in the 733-label space against ALL gold labels (sentences whose gold label was never seen in training count as misses for the classifiers). Label granularity: exact ID match (sub-technique T1059.001 != parent T1059).

Thresholded metrics: dev-tuned global threshold from `metrics.json`, then if a row has no label above threshold the arg-max label is forced (Exp_1_4 CELL 4 `apply_thresholds`). `micro_F1_180cols(nb)` reproduces the notebook (only the 180 train labels are scored, so the 10 unseen gold labels are silently ignored); `micro_F1_all_labels` counts them as false negatives.

## Per-seed table

| system | seed | microF1 (nb) | microF1 (all labels) | macroF1-117 | macroF1-127 | P@1 | MRR@3 | P@3 | thr | empty rows fixed |
|---|---|---|---|---|---|---|---|---|---|---|
| TF-IDF+LinearSVC | - | 0.6961 | 0.6921 | 0.5427 | 0.5000 | 0.7421 | 0.8138 | 0.3287 | -0.45 | 105 |
| RoBERTa-base | 42 | 0.7077 | 0.7035 | 0.5681 | 0.5234 | 0.7572 | 0.8113 | 0.3186 | 0.85 | 105 |
| RoBERTa-base | 43 | 0.6931 | 0.6890 | 0.5487 | 0.5055 | 0.7434 | 0.8002 | 0.3149 | 0.85 | 101 |
| RoBERTa-base | 44 | 0.7154 | 0.7111 | 0.5735 | 0.5283 | 0.7545 | 0.8140 | 0.3205 | 0.85 | 106 |
| SecBERT | 42 | 0.7042 | 0.6999 | 0.5363 | 0.4941 | 0.7434 | 0.8055 | 0.3191 | 0.75 | 141 |
| SecBERT | 43 | 0.7022 | 0.6981 | 0.5514 | 0.5080 | 0.7476 | 0.8080 | 0.3209 | 0.65 | 93 |
| SecBERT | 44 | 0.7028 | 0.6986 | 0.5413 | 0.4987 | 0.7393 | 0.8000 | 0.3177 | 0.70 | 117 |

## Ranking systems

| system | seed | split | P@1 | MRR@3 | P@3 | R@5 | unseen R@5 | top-1 ties |
|---|---|---|---|---|---|---|---|---|
| RoBERTa-base 3-seed prob-average | avg | test | 0.7559 | 0.8159 | 0.3218 | 0.8649 | 0.00 | 0 |
| SecBERT 3-seed prob-average | avg | test | 0.7545 | 0.8143 | 0.3251 | 0.8684 | 0.00 | 0 |
| Matcher zero-shot bge-base-en-v1.5 | - | test | 0.2276 | 0.3002 | 0.1343 | 0.4230 | 0.60 | 2 |
| Matcher ft20 | 42 | test | 0.7559 | 0.8195 | 0.3228 | 0.8684 | 0.50 | 0 |
| Matcher ft20 | 43 | test | 0.7710 | 0.8299 | 0.3214 | 0.8731 | 0.60 | 0 |
| Matcher ft20 | 44 | test | 0.7407 | 0.8122 | 0.3209 | 0.8602 | 0.70 | 0 |
| Matcher 3-seed ensemble (mean score) | avg | test | 0.7766 | 0.8366 | 0.3274 | 0.8754 | 0.60 | 0 |
| Classifiers-only ensemble (SVM+RoBERTa+SecBERT, equal z) | avg | test | 0.7738 | 0.8366 | 0.3375 | 0.9013 | 0.00 | 0 |
| Fusion equal weights (1,1,1,1), matcher 3-seed avg | avg | test | 0.7821 | 0.8414 | 0.3375 | 0.9154 | 0.00 | 0 |
| Fusion equal weights (1,1,1,1), matcher s42 [as Exp_2.1 CELL 8] | 42 | test | 0.7793 | 0.8395 | 0.3366 | 0.9142 | 0.00 | 0 |
| Fusion (3,1,1,1) seed-averaged | avg | test | 0.8028 | 0.8556 | 0.3393 | 0.9166 | 0.50 | 0 |
| Fusion (4,1,1,1) seed-averaged [wide-grid dev winner] | avg | test | 0.8083 | 0.8589 | 0.3389 | 0.9072 | 0.50 | 0 |
| Fusion (3,1,1,1) matcher seed s + 3-seed-avg classifiers [Exp_2.1 CELL 11] | 42 | test | 0.8000 | 0.8517 | 0.3347 | 0.9130 | 0.40 | 0 |
| Fusion (3,1,1,1) matcher seed s + 3-seed-avg classifiers [Exp_2.1 CELL 11] | 43 | test | 0.7986 | 0.8543 | 0.3393 | 0.9142 | 0.40 | 0 |
| Fusion (3,1,1,1) matcher seed s + 3-seed-avg classifiers [Exp_2.1 CELL 11] | 44 | test | 0.8000 | 0.8529 | 0.3393 | 0.9177 | 0.70 | 0 |
| Fusion (3,1,1,1) seed-paired (matcher s, RoBERTa s, SecBERT s) | 42 | test | 0.7903 | 0.8501 | 0.3375 | 0.9083 | 0.40 | 0 |
| Fusion (3,1,1,1) seed-paired (matcher s, RoBERTa s, SecBERT s) | 43 | test | 0.7959 | 0.8536 | 0.3402 | 0.9142 | 0.40 | 0 |
| Fusion (3,1,1,1) seed-paired (matcher s, RoBERTa s, SecBERT s) | 44 | test | 0.8028 | 0.8520 | 0.3343 | 0.9130 | 0.60 | 0 |
| Ablation: fusion without matcher | avg | test | 0.7738 | 0.8366 | 0.3375 | 0.9013 | 0.00 | 0 |
| Ablation: fusion without svm | avg | test | 0.7986 | 0.8529 | 0.3370 | 0.8989 | 0.50 | 0 |
| Ablation: fusion without roberta | avg | test | 0.7821 | 0.8453 | 0.3370 | 0.9166 | 0.50 | 0 |
| Ablation: fusion without secbert | avg | test | 0.7903 | 0.8510 | 0.3393 | 0.9119 | 0.40 | 0 |
| Fusion (3,1,1,1) seed-averaged | avg | dev | 0.8228 | 0.8733 | 0.3355 | 0.9073 | 0.50 | 0 |

## Claims B1-B13

| ID | claim | recomputed | diff flag |
|---|---|---|---|
| B1 | micro-F1 RoBERTa 0.705 +/- 0.011 | 0.705 +/- 0.011 | ok (<=0.001) |
| B2 | micro-F1 SecBERT 0.703 +/- 0.001 | 0.703 +/- 0.001 | ok (<=0.001) |
| B3 | micro-F1 SVM 0.696 | 0.696 | ok (<=0.001) |
| B4 | macro-F1 RoBERTa 0.563 (117) / 0.519 (127) | 0.563 / 0.519 | ok (<=0.001) |
| B5 | macro-F1 SecBERT 0.543 / 0.500 | 0.543 / 0.500 | ok (<=0.001) |
| B6 | P@1 SVM 0.742 | 0.742 | ok (<=0.001) |
| B7 | P@1 RoBERTa 0.756 | 3-seed prob-average: 0.756; mean of seeds: 0.752 +/- 0.007 | ok (<=0.001) |
| B8 | P@1 SecBERT 0.755 | 3-seed prob-average: 0.754; mean of seeds: 0.743 +/- 0.004 | ok (<=0.001) |
| B9 | classifiers-only ensemble 0.774 | 0.774 | ok (<=0.001) |
| B10a | bge zero-shot 0.228 | 0.228 | ok (<=0.001) |
| B10b | ft20 0.756 +/- 0.015 | 0.756 +/- 0.015 | ok (<=0.001) |
| B10c | matcher 3-seed ensemble 0.777 | 0.777 | ok (<=0.001) |
| B11 | equal-weight fusion 0.779 | matcher s42 (as notebook): 0.779; matcher 3-seed avg: 0.782 | ok (<=0.001) |
| B12a | seed-paired fusion P@1 0.796 +/- 0.006 (0.790/0.796/0.803) | 0.796 +/- 0.006 (0.790/0.796/0.803) | ok (<=0.001) |
| B12b | seed-paired fusion MRR@3 0.852 +/- 0.002 | 0.852 +/- 0.002 | ok (<=0.001) |
| B13a | seed-averaged fusion P@1 0.803 | 0.803 | ok (<=0.001) |
| B13b | seed-averaged fusion MRR@3 0.853? | 0.856 | **DIFF > 0.001** |

Notebook variant of the per-seed fusion (matcher seed varies, classifiers 3-seed averaged; Exp_2.1 CELL 11, `final_results_table.csv`): P@1 0.800 +/- 0.001, MRR@3 0.853 +/- 0.001.

## B14 fusion weights and grid  [RECOMPUTED on DEV]

- component order: `['matcher', 'svm', 'roberta', 'secbert']` (Exp_2.1 CELL 8 output `models: [...]`)
- coarse grid {0,1,2,3}^4 minus all-zero = 255 settings, matcher = ft20 seed 42, classifiers = 3-seed averages: DEV winner **(3, 1, 1, 1)** with dev (MRR@3, P@1) = (0.8698, 0.8179)
- wide grid {0,1,2,3,4,6,8}^4 reduced by gcd = **1711** settings: DEV winner **(4, 1, 1, 1)** (dev MRR@3 0.8744, P@1 0.8262); (3,1,1,1) is rank **30** of 1711 on that grid (dev MRR@3 0.8698).
- test P@1 for (3,1,1,1) vs (4,1,1,1), matcher s42: 0.8000 vs 0.8041
- **So (3,1,1,1) is the winner of the 255-setting coarse grid, NOT of the 1,711 grid** (the 1,711 grid prefers (4,1,1,1)). Full dev ranking: `03_fusion_grid_dev.csv`.

## Checks

- stored vs recomputed (classifiers, 6 runs): max |micro-F1 diff| = 1.11e-16, max |macro-F1(117) diff| = 1.11e-16, max |P@1 diff| = 2.06e-08, max |MRR@3 diff| = 0.00e+00
- SVM refit vs notebook output (Exp_1_4 CELL 6: micro_f1 0.6961, macro_f1 0.5427, hit@1 0.7421, mrr@3 0.8138, thr -0.45): 0.6961, 0.5427, 0.7421, 0.8138, thr -0.45
- matcher stored metrics.json test P@1 per seed: s42=0.7559, s43=0.7710, s44=0.7407 vs recomputed 0.7559, 0.7710, 0.7407
- rows with a tie for rank 1 (any system): max = 2
- RoBERTa dev thresholds: [0.85, 0.85, 0.85] -> all at the TOP EDGE of the grid np.arange(0.1, 0.9, 0.05) (max 0.85); the optimum may lie above the grid. SecBERT: [0.75, 0.65, 0.7].