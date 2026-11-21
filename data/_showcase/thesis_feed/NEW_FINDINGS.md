# New findings since draft v2 (all pre-registered in `../experiments/prereg/`)

## 1 Holm correction over 8 paired comparisons (prereg 01)
Family: C1-C4 and the four ablations A1-A4. Test: exact McNemar on P@1 hits; Holm step-down. Interval: paired bootstrap, 10,000 resamples.

| id | comparison | delta P@1 | 95% CI | McNemar p | Holm p | supported |
|---|---|---|---|---|---|---|
| C1 | Fusion (3,1,1,1) minus Classifiers-only ens. | +0.0290 | [+0.017, +0.043] | 0.0000 | 0.0002 | True |
| C2 | Fusion (3,1,1,1) minus Matcher (3-seed ens.) | +0.0262 | [+0.001, +0.051] | 0.0475 | 0.1901 | False |
| C3 | RoBERTa (3-seed avg) minus TF-IDF + SVM | +0.0138 | [-0.014, +0.041] | 0.3909 | 1.0000 | False |
| C4 | RoBERTa (3-seed avg) minus SecBERT (3-seed avg) | +0.0014 | [-0.023, +0.025] | 1.0000 | 1.0000 | False |
| A1 | Fusion (3,1,1,1) minus Fusion without matcher | +0.0290 | [+0.017, +0.043] | 0.0000 | 0.0002 | True |
| A2 | Fusion (3,1,1,1) minus Fusion without svm | +0.0041 | [-0.006, +0.015] | 0.6072 | 1.0000 | False |
| A3 | Fusion (3,1,1,1) minus Fusion without roberta | +0.0207 | [+0.007, +0.034] | 0.0059 | 0.0355 | True |
| A4 | Fusion (3,1,1,1) minus Fusion without secbert | +0.0124 | [+0.003, +0.023] | 0.0352 | 0.1758 | False |

What it is: fusion beats the classifiers-only ensemble (+0.029, Holm p 0.000); removing the matcher or RoBERTa lowers P@1 with support.
What it is not: evidence that fusion beats the matcher ensemble (+0.026, Holm p 0.190), that SVM or SecBERT add anything to the fusion, or that RoBERTa beats SVM (+0.014, Holm p 1.000).

## 2 Support-aware fusion (prereg 09 and 13): failed its rule
The matcher weight depends on the label's train support. Tuned on dev; test evaluated once per variant.
- Four-band variant: dev-selected weights (3, 6, 4, 4); test P@1 0.810 vs 0.803 for (3,1,1,1); delta +0.007 [-0.001, 0.017], Holm p 0.453.
- P@1 on sentences with rare labels (support 0-4): 0.386 vs 0.227; small group, interval in `tables/t_support_aware_family.csv`.
- Pre-registered success rule met: False. Three-band variant weights: (4, 4, 4).
What it is: a direction worth testing on more data. What it is not: an improvement.

## 3 SHAP faithfulness (prereg 06), RoBERTa seed 42, 95 sentences
| measure | SHAP order | random order | difference | 95% CI |
|---|---|---|---|---|
| deletion AUC (lower is better) | 0.173 | 0.667 | -0.494 | [-0.534, -0.452] |
| insertion AUC (higher is better) | 0.830 | 0.360 | +0.470 | [0.427, 0.513] |
| comprehensiveness, top-3, probability | 0.768 | 0.175 | +0.593 | [0.527, 0.656] |
| sufficiency, top-3, probability (lower is better) | 0.056 | 0.641 | -0.585 | [-0.640, -0.527] |
What it is: SHAP word order tracks what moves this model's score. What it is not: a test of human plausibility, or of the fusion.

## 4 Maximum length 256 at inference (prereg 08), 34 truncated test sentences
RoBERTa: 19 vs 17 of 34. SecBERT: 20 vs 20 of 34. Models were trained at 128 tokens; training at 256 was not tested.

## 5 Unseen and rare labels
- Unseen-label sentences (n = 10): P@1 fusion 0.000, matcher ensemble 0.200, classifiers 0.000.
- R@5 on the 10 unseen gold pairs: fusion 0.50, matcher 0.60, classifiers-only 0.00.
- Support 1-4 (n = 34): fusion 0.294 vs matcher 0.559. Support 5-19 (n = 96): fusion 0.667 vs matcher 0.646.
- Support 20-49: fusion 0.819 vs matcher 0.750; 50+: 0.897 vs 0.862.

## 6 Other checks
- Extended threshold grid: RoBERTa thresholds 0.85 / 0.85 / 0.85 -> 0.93 / 0.83 / 0.88; mean change in test micro-F1 -0.0006.
- Overlap removal (exact + near, 2 sentences): largest P@1 change in any system 0.0007.
- Calibration: ECE RoBERTa 0.172 +/- 0.007, SecBERT 0.138 +/- 0.012 (10 bins, top-1 probability).
