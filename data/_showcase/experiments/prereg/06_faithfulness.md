# Pre-registration 06_faithfulness: Faithfulness of the stored word-level SHAP explanations

| field | content |
|---|---|
| Hypothesis | H: masking words in SHAP order lowers the explained logit faster than masking in random order (deletion), and revealing them raises it faster (insertion); comprehensiveness of the top-3 words exceeds that of 3 random words; sufficiency is lower (better) for top-3 than for random-3. |
| Split | test, first 100 rows of RandomState(42).permutation(725) (the fixed sample of the existing deletion test) |
| Metric | explained quantity = logit (and sigmoid probability) of roberta_pw_s42's top-1 label; curves for k = 0..10 masked/revealed words; AUC by trapezoid over k normalised by the k=0 value; comprehensiveness and sufficiency at k=3 |
| Comparison | SHAP order vs mean of 5 random orders (RandomState(1000 + row)); eligibility = at least 6 words, not truncated at 128 tokens |
| Seeds | model seed 42 (the explained model) |
| Dev-only tuning | nothing tuned; k=3 fixed by the earlier deletion test; curve length 10 fixed here |
| Decision rule | Each H is supported if the paired bootstrap 95% CI of (SHAP - random) excludes 0 in the stated direction. |
| What counts as failure / prior exposure | The deletion result at k=3 was already seen (10.19 logits). Insertion, comprehensiveness, sufficiency and the curves were never computed. Limit stated in advance: mask-token perturbation is the same perturbation SHAP used, so this tests consistency of the attribution, not human plausibility. |

Split discipline: anything tuned is tuned on DEV only. The test split is evaluated once per configuration listed here. Uncertainty: paired/percentile bootstrap over test sentences, 10,000 resamples, numpy default_rng(20261114). Systems (fixed): SVM (refit, deterministic); RoBERTa and SecBERT = mean probability of seeds 42-44; matcher = mean score of seeds 42-44; fusion = z-score sum with weights (3,1,1,1) in the order matcher, SVM, RoBERTa, SecBERT.
