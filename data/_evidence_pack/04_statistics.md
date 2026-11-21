# 04 Statistics

Paired bootstrap over the 725 test sentences, 10,000 resamples, `numpy.random.default_rng(20261114)`, percentile 95% CI. Second CI column = notebook setting (1,000 resamples, `default_rng(0)`). McNemar = exact two-sided binomial on discordant pairs.

Note: the bootstrap resamples test sentences only; it does not include training-seed variance.

| ID | A minus B | dP@1 | 95% CI (10k) | 95% CI (nb 1k, rng 0) | claimed | McNemar b / c | exact p | dMRR@3 [CI] |
|---|---|---|---|---|---|---|---|---|
| C1 | fusion(3,1,1,1) seed-avg - classifiers-only | +0.0290 | [+0.017, +0.043] | [+0.017, +0.043] | +0.029 [0.017, 0.043] | 23 / 2 | 0.0000 | +0.019 [+0.010, +0.029] |
| C2 | fusion(3,1,1,1) seed-avg - matcher 3-seed ens | +0.0262 | [+0.001, +0.051] | [+0.003, +0.051] | +0.026 [0.003, 0.051] | 51 / 32 | 0.0475 | +0.019 [+0.003, +0.036] |
| C3 | RoBERTa 3-seed avg - SVM | +0.0138 | [-0.014, +0.041] | [-0.015, +0.040] | +0.014 [-0.015, 0.040] | 60 / 50 | 0.3909 | +0.002 [-0.018, +0.022] |
| C4 | RoBERTa 3-seed avg - SecBERT 3-seed avg | +0.0014 | [-0.023, +0.025] | [-0.022, +0.025] | +0.001 [-0.022, 0.025] | 40 / 39 | 1.0000 | +0.002 [-0.016, +0.019] |

Origin of the claimed intervals: C1: Exp_2.1 CELL 13: 1000 resamples, default_rng(0); C2: Exp_2.1 CELL 11: 1000 resamples, default_rng(0), first comparison in loop; C3: NOT-FOUND in any notebook (number comes from an earlier audit note); C4: NOT-FOUND in any notebook (number comes from an earlier audit note)