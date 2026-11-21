# 11 SHAP of the fused score (classifiers-only part of the fusion (0,1,1,1), NO matcher, seed 42)

Source `11_fusion_shap_partial.jsonl`: 40 test sentences = first 40 of `RandomState(42).permutation(725)` (same fixed sample as the stored SHAP run and the human sheet). Method identical to Exp_3_0b except the explained function: weighted sum of per-row z-scores for the fused top-1 label; components ['svm', 'roberta_s42', 'secbert_s42'] with weights [1.0, 1.0, 1.0]. [RECOMPUTED, new]

- additivity error (sum of SHAP + base vs. fused score): max 4.4e-06
- fused top-1 correct: 32 of 40; stored RoBERTa s42 top-1 correct on the same rows: 31
- fused top-1 label equals the label the stored RoBERTa SHAP explains: 35 of 40

## Do the fused explanations differ from the stored RoBERTa explanations?

- same label (n=35): Spearman rank correlation of word scores, mean 0.726, median 0.741, min 0.265; top-3 word overlap: mean 2.40 of 3; all 3 identical in 15 sentences, <=1 shared in 1
- different label (n=5): Spearman mean 0.027 (the two explanations are about different techniques)

## Which component carries the attribution mass?

Share of sum |SHAP| (weights applied), mean over sentences:

| component | weight | mean share |
|---|---|---|
| svm | 1.0 | 0.306 |
| roberta_s42 | 1.0 | 0.350 |
| secbert_s42 | 1.0 | 0.343 |

Spearman between components' word scores (same sentence, same label), mean: svm vs roberta_s42 0.519; svm vs secbert_s42 0.566; roberta_s42 vs secbert_s42 0.551

## Deletion test on the FUSED score (word removal, 3 words)

Eligible sentences: 38 (>= 6 words, >= 3 positive words in both explanations). Drop = fused z-score sum of the fused top-1 label before minus after.

| words removed | mean drop | 95% CI |
|---|---|---|
| top-3 by SHAP of the fused score | 23.951 | [20.068, 27.665] |
| top-3 by the stored RoBERTa-only SHAP | 22.736 | [18.794, 26.752] |
| 3 random words (mean of 20 draws) | 5.526 | [3.730, 7.508] |

- fused-SHAP minus RoBERTa-SHAP drop: mean +1.215, 95% CI [-0.645, +3.536]; fused-SHAP larger in 12, equal in 14, smaller in 12 of 38
- RoBERTa-SHAP words recover 95% of the drop that the fused-SHAP words achieve; random words 23%
- restricted to sentences where the two explanations target the same label (n=33): fused 23.979, RoBERTa 24.505
- sentences where the labels differ (n=5): fused 23.763, RoBERTa 11.063

Limits: this is a faithfulness measurement (does hiding the words move the explained score), not a plausibility measurement; the matcher (weight 3, about 39% of the fused top-1 score) is NOT included because its weights were never saved.