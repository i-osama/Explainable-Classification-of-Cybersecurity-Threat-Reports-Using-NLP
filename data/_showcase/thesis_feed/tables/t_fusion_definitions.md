| definition | claim_id_P@1 | P@1 | P@1_95%CI | claim_id_MRR@3 | MRR@3 | per_seed_P@1 (42/43/44) | runs | how computed |
|---|---|---|---|---|---|---|---|---|
| seed-averaged | B13a | 0.803 | [0.774, 0.832] | B13b | 0.856 | - | 1 system (no seed spread) | all components averaged over seeds 42-44, then fused once |
| seed-paired | B12a | 0.796 +/- 0.006 |  | B12b | 0.852 +/- 0.002 | 0.790 / 0.796 / 0.803 | 3 runs | matcher, RoBERTa and SecBERT all from the same seed s; mean +/- sd over s = 42, 43, 44 |
| notebook (matcher seed varied) | B12nb | 0.800 +/- 0.001 |  | B12nb.mrr3 | 0.853 +/- 0.001 | 0.800 / 0.799 / 0.800 | 3 runs | matcher seed s, classifiers averaged over 3 seeds; mean +/- sd (Exp_2.1 CELL 11, final_results_table.csv) |
| equal weights, matcher seed 42 | B11 | 0.779 |  | - | - | - | 1 | weights (1,1,1,1); matcher seed 42 only, classifiers 3-seed averages (as in Exp_2.1 CELL 8) |
| equal weights, seed-averaged | B11.avg | 0.782 | [0.750, 0.812] | - | - | - | 1 | weights (1,1,1,1) with the same seed-averaged components as B13a |
