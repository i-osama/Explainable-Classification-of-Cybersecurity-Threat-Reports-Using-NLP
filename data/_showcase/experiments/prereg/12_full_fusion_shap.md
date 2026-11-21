# Pre-registration 12_full_fusion_shap: SHAP of the full fusion (Colab)

| field | content |
|---|---|
| Hypothesis | H: explanations of the fused score are more faithful TO THE FUSED SCORE than the stored RoBERTa-only explanations, mainly on sentences where the two systems output different top-1 labels. |
| Split | test, first 100 rows of the fixed permutation |
| Metric | drop of the fused score after removing the top-3 words (fused-SHAP vs RoBERTa-SHAP vs random-3) |
| Comparison | seed-paired fusion (3,1,1,1) with a matcher retrained with saved weights |
| Seeds | 42 |
| Dev-only tuning | linearity shortcut is used only if the per-row z-score statistics are verified constant under masking; they are NOT (mean and sd are recomputed per perturbed sentence), so the notebook explains each component's z-scored output directly and sums with the weights (exact by linearity of Shapley values in the OUTPUT, no assumption on the z statistics) |
| Decision rule | Supported if the paired bootstrap CI of (fused-SHAP drop - RoBERTa-SHAP drop) excludes 0. |
| What counts as failure / prior exposure | Partial result already seen without the matcher (n=40): no difference when labels agree, large difference when they differ. The retrained matcher is not the original one; its own test P@1 is reported next to the result. TODO-COLAB. |

Split discipline: anything tuned is tuned on DEV only. The test split is evaluated once per configuration listed here. Uncertainty: paired/percentile bootstrap over test sentences, 10,000 resamples, numpy default_rng(20261114). Systems (fixed): SVM (refit, deterministic); RoBERTa and SecBERT = mean probability of seeds 42-44; matcher = mean score of seeds 42-44; fusion = z-score sum with weights (3,1,1,1) in the order matcher, SVM, RoBERTa, SecBERT.
