# Pre-registration 01_statistics_family: Comparison family and multiplicity correction

| field | content |
|---|---|
| Hypothesis | H: the fusion's P@1 gain over its parts is not explained by chance; RoBERTa does not differ from SVM or SecBERT. |
| Split | test (725 sentences) |
| Metric | P@1 (per-sentence hit at rank 1) |
| Comparison | Family of 8 two-sided tests: C1 fusion vs classifiers-only; C2 fusion vs matcher ensemble; C3 RoBERTa vs SVM; C4 RoBERTa vs SecBERT; A1-A4 full fusion vs fusion without matcher / SVM / RoBERTa / SecBERT. Exact McNemar per pair; Holm step-down over the 8 p-values. |
| Seeds | none (uses saved predictions of seeds 42-44) |
| Dev-only tuning | nothing is tuned |
| Decision rule | A difference is called supported only if the Holm-adjusted McNemar p < 0.05 AND the bootstrap 95% CI excludes 0. |
| What counts as failure / prior exposure | Any comparison failing either condition is reported as 'not supported'. C1-C4 raw values were already seen in the evidence pack (04_bootstrap.csv); this registration fixes the family size and the correction, not a first look. |

Split discipline: anything tuned is tuned on DEV only. The test split is evaluated once per configuration listed here. Uncertainty: paired/percentile bootstrap over test sentences, 10,000 resamples, numpy default_rng(20261114). Systems (fixed): SVM (refit, deterministic); RoBERTa and SecBERT = mean probability of seeds 42-44; matcher = mean score of seeds 42-44; fusion = z-score sum with weights (3,1,1,1) in the order matcher, SVM, RoBERTa, SecBERT.
