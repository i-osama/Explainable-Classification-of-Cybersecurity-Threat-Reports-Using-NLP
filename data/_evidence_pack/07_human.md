# 07 Human-study evidence

Rating files: 3 workbooks `Exp_3_0_shap/hand_check_v2_roberta_pw_s42*.xlsx` (sheet `rating`). Raters are identified here only by role and by the first 8 hex digits of the file SHA-256 (full hashes in `00_hashes.csv`). No names or personal data are reproduced.

## Design  [VERIFIED: Exp_3_2_hand_check CELL 0-2]

- unit rated: one test sentence with the 3 highest positive SHAP words marked `[[word]]`, plus predicted technique id, name, status, first sentence of its description. Gold labels hidden (`SHOW_GOLD = False`).
- question: do the marked words make sense as evidence for the predicted technique?
- scale (ordinal, 3 levels): **2 = makes sense, 1 = partly, 0 = does not make sense**.
- sampling: first 100 rows of `numpy.random.RandomState(42).permutation(725)`: a fixed random sample of the test set, no hand selection; same order as the SHAP run.
- explained model: roberta_pw_s42; technique names from MITRE `attack-stix-data` master (cache `attack_technique_names.json`), not pinned to v12.

## Raters  [RECOMPUTED from the workbooks]

| role | file sha256[:8] | rows in sheet | rows rated | 2 | 1 | 0 | mean | rows match fixed sample |
|---|---|---|---|---|---|---|---|---|
| Rater A | 9e83b71a | 100 | 100 | 49 | 47 | 4 | 1.45 | True |
| Rater B | 0c1fb4a9 | 100 | 100 | 83 | 10 | 7 | 1.76 | True |
| Rater C | ceb79cdb | 100 | 3 | 3 | 0 | 0 | 2.00 | True |

Roles: Rater A's sheet is the project author's own sheet according to the notebook output order (Exp_3_3 CELL output 'raters: ... (A), ... (B)'); the profession/expertise of Raters B and C is NOT-FOUND in any file. Rater C's rated rows: `[326, 518, 554]` (sheet positions [0, 1, 2]).

## Agreement  [RECOMPUTED]

| statistic | value | note |
|---|---|---|
| Krippendorff alpha nominal (A,B; 100 rows) | -0.057 |  |
| Krippendorff alpha ordinal (A,B; 100 rows) | 0.031 |  |
| Krippendorff alpha nominal (A,B,C; C has 3 rows) | -0.050 |  |
| Krippendorff alpha ordinal (A,B,C; C has 3 rows) | 0.037 |  |
| Fleiss kappa (A,B; 100 rows) | -0.062 |  |
| Cohen kappa unweighted (A,B) | 0.062 |  |
| Cohen kappa linear-weighted (A,B) | 0.133 |  |
| Cohen kappa quadratic-weighted (A,B) | 0.236 |  |
| Percent agreement exact (A,B) | 0.490 | 49 of 100 |
| Percent agreement within 1 point (A,B) | 0.980 |  |
| Cohen kappa binary '2 vs not' (A,B) | 0.053 |  |
| Cohen kappa binary '0 vs not' (A,B) | 0.521 |  |
| Percent agreement (A,C) on C's 3 rows | 1.000 | A=[2, 2, 2] C=[2, 2, 2]; kappa undefined/meaningless at n=3 (C constant) |
| Percent agreement (B,C) on C's 3 rows | 1.000 | B=[2, 2, 2] C=[2, 2, 2]; kappa undefined/meaningless at n=3 (C constant) |
| Cohen kappa unweighted 95% CI (2000 resamples, RandomState(42)) | [-0.076, 0.196] |  |
| Krippendorff alpha nominal 95% CI (same resamples) | [-0.237, 0.124] |  |

Contingency table (rows Rater A, columns Rater B):

| A \ B | 0 | 1 | 2 |
|---|---|---|---|
| 0 | 3 | 0 | 1 |
| 1 | 3 | 4 | 40 |
| 2 | 1 | 6 | 42 |

Merged file `rater_agreement_v2_roberta_pw_s42.csv` equals the two full workbooks: True; it has no Rater C column.

## Claims D1-D5

| ID | claim | recomputed | status |
|---|---|---|---|
| D1 | Krippendorff alpha nominal -0.057 | -0.057 | MATCH |
| D2 | Krippendorff alpha ordinal 0.031 | +0.031 | MATCH |
| D3 | Fleiss kappa -0.062 | -0.062 | MATCH |
| D4 | Cohen kappa 0.062 | unweighted +0.062; linear +0.133; quadratic +0.236 | MATCH |
| D5 | third rater rated only 3 rows | 3 rated of 100 | MATCH |

Reading: agreement between the two full raters is at chance level; the human study cannot support a plausibility claim. The marginals differ strongly (Rater A gives '2' to 49%, Rater B to 83%), which is what drives kappa to ~0 despite 49% raw agreement.