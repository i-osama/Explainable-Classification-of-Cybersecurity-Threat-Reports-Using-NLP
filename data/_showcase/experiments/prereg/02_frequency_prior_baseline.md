# Pre-registration 02_frequency_prior_baseline: Frequency-prior baseline

| field | content |
|---|---|
| Hypothesis | H: a model that ignores the sentence and always ranks labels by training frequency is far below every learned system. |
| Split | test |
| Metric | P@1, MRR@3, micro/macro-F1 (predict the single most frequent train label) |
| Comparison | prior vs SVM (descriptive; not part of the test family) |
| Seeds | none |
| Dev-only tuning | nothing tuned; ranking = train label counts, ties by lower label index |
| Decision rule | Reported as the floor. No decision depends on it. |
| What counts as failure / prior exposure | If the prior reaches P@1 above 0.20 the task is easier than described and that is stated. Never computed before this registration. |

Split discipline: anything tuned is tuned on DEV only. The test split is evaluated once per configuration listed here. Uncertainty: paired/percentile bootstrap over test sentences, 10,000 resamples, numpy default_rng(20261114). Systems (fixed): SVM (refit, deterministic); RoBERTa and SecBERT = mean probability of seeds 42-44; matcher = mean score of seeds 42-44; fusion = z-score sum with weights (3,1,1,1) in the order matcher, SVM, RoBERTa, SecBERT.
