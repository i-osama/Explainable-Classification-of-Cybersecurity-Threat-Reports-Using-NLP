# Fusion: three definitions of the same weights (3,1,1,1)

All three use the same weights and the same components. They differ only in how the three training seeds are combined. All three reproduce from the saved files.
They are not three results. They are three ways to summarise one result, and the thesis must name the one it uses each time.

| definition | claim_id_P@1 | P@1 | P@1_95%CI | claim_id_MRR@3 | MRR@3 | per_seed_P@1 (42/43/44) | runs | how computed |
|---|---|---|---|---|---|---|---|---|
| seed-averaged | B13a | 0.803 | [0.774, 0.832] | B13b | 0.856 | - | 1 system (no seed spread) | all components averaged over seeds 42-44, then fused once |
| seed-paired | B12a | 0.796 +/- 0.006 |  | B12b | 0.852 +/- 0.002 | 0.790 / 0.796 / 0.803 | 3 runs | matcher, RoBERTa and SecBERT all from the same seed s; mean +/- sd over s = 42, 43, 44 |
| notebook (matcher seed varied) | B12nb | 0.800 +/- 0.001 |  | B12nb.mrr3 | 0.853 +/- 0.001 | 0.800 / 0.799 / 0.800 | 3 runs | matcher seed s, classifiers averaged over 3 seeds; mean +/- sd (Exp_2.1 CELL 11, final_results_table.csv) |
| equal weights, matcher seed 42 | B11 | 0.779 |  | - | - | - | 1 | weights (1,1,1,1); matcher seed 42 only, classifiers 3-seed averages (as in Exp_2.1 CELL 8) |
| equal weights, seed-averaged | B11.avg | 0.782 | [0.750, 0.812] | - | - | - | 1 | weights (1,1,1,1) with the same seed-averaged components as B13a |


## Where each value appears in draft v2

Source: the number ledger of draft v2 that the author pasted on 14 Nov 2026 (paragraph numbers `p` are the audit script's indices; `table` = the paragraph is a table cell).
Draft v2.2 has not been seen on this PC; re-run `scripts/audit_numbers.py` on it to refresh this list.

| draft location | value printed | definition it matches |
|---|---|---|
| abstract, p192 | 0.803 | seed-averaged `B13a` |
| reproduction text p594 and table p601 | 0.803 | seed-averaged `B13a` |
| reproduction table p610 | 0.796 +/- 0.006 (0.790, 0.796, 0.803) | seed-paired `B12a` |
| results text p637 | 0.803; 0.796 +/- 0.006; 0.800 +/- 0.001; MRR@3 0.852 +/- 0.002 | all three, named in the text |
| main results table, p640-p670 | row "seed-paired" 0.796 +/- 0.006 and MRR@3 0.852 +/- 0.002; row "seed-averaged" 0.803 | `B12a`, `B12b`, `B13a` |
| comparison table, p679-p692 (+0.029, +0.026) | deltas | computed with the seed-averaged fusion `B13a` |
| overlap-sensitivity table, p704-p722 | 0.8028 | seed-averaged `B13a` |
| support-bucket table, p745-p766 | per-bucket P@1 | seed-averaged fusion, 3-seed matcher ensemble |
| summary table, p798-p810 | +0.029, +0.026 | seed-averaged `B13a` |
| discussion p817 | 0.803 vs equal weights 0.779 | `B13a` vs `B11`: NOT like-for-like (see DIFFERENCES.md) |
| discussion p820 | "0.796 to 0.803", MRR@3 0.852 | `B12a` to `B13a`; MRR@3 from `B12b` |
| baseline table, p823-p840 | seed-paired 0.796 +/- 0.006, MRR@3 0.852 +/- 0.002; seed-averaged 0.803, MRR@3 0.856 | `B12a`, `B12b`, `B13a`, `B13b` |
| conclusion p859, appendix p929 | 0.803 | seed-averaged `B13a` |

Finding: the plan says the draft headlines the seed-paired value 0.796, but the abstract (p192) and the conclusion (p859) state 0.803 (seed-averaged).
All comparison intervals (C1, C2) and all per-bucket results are computed with the seed-averaged fusion. If 0.796 is the headline, say in each of those places that the test uses the seed-averaged system.
