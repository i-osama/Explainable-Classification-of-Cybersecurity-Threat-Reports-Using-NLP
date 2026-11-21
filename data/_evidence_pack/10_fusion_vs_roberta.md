# 10 Fusion vs. the model SHAP currently explains (roberta_pw_s42)

All from saved test scores. [RECOMPUTED]

- P@1: roberta_pw_s42 0.757, fusion (3,1,1,1) seed-averaged 0.803
- same top-1 label: **617 of 725 (85.1%)**; different top-1: **108 (14.9%)**
- of the 108 sentences with a different top-1: fusion right & RoBERTa wrong 48, RoBERTa right & fusion wrong 15, both right (different gold labels) 11, both wrong 34
- so for these sentences the stored SHAP words explain a label that the final system does not output.

## Where the fused decision comes from

For each test sentence: share of the fused top-1 score, and share of the top-1 minus top-2 margin, contributed by each component (weights included).

| component | weight | mean share of top-1 score | median share of top-1/top-2 margin | sentences where the component alone prefers the fused top-1 over the fused top-2 |
|---|---|---|---|---|
| matcher | 3 | 0.388 | 0.210 | 86.5% |
| svm | 1 | 0.167 | 0.203 | 88.3% |
| roberta | 1 | 0.223 | 0.299 | 89.7% |
| secbert | 1 | 0.222 | 0.297 | 89.4% |

RoBERTa (3-seed average) supplies on average 22.3% of the fused top-1 score; the single seed SHAP explains is one third of that component.

## Does the fusion fix unseen and rare techniques? (premise check)

| rarest gold label train support | n | RoBERTa s42 P@1 | matcher ens. P@1 | fusion P@1 | fusion top-1 == RoBERTa s42 top-1 |
|---|---|---|---|---|---|
| unseen (0) | 10 | 0.000 | 0.200 | 0.000 | 50.0% |
| 1-4 | 34 | 0.265 | 0.559 | 0.294 | 50.0% |
| 5-9 | 30 | 0.467 | 0.600 | 0.567 | 73.3% |
| 10-19 | 66 | 0.636 | 0.667 | 0.712 | 81.8% |
| 20-49 | 216 | 0.787 | 0.750 | 0.819 | 84.3% |
| 50+ | 369 | 0.851 | 0.862 | 0.897 | 91.3% |

Unseen-technique sentences (n=10): fusion top-1 correct in 0, gold in fusion top-5 in 5; matcher ensemble top-1 correct in 2. The fusion's top-1 label on these rows is a SEEN label in 10 of 10 rows.