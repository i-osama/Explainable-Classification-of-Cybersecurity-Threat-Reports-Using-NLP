# Pre-registration 05_f1_variants_support_buckets: F1 variants and performance by train support

| field | content |
|---|---|
| Hypothesis | H1: counting unseen gold labels as misses lowers micro-F1 by less than 0.01 (only 10 of 851 gold pairs). H2: fusion P@1 is below the matcher's on labels with 1-4 training sentences and above it at 20 or more. |
| Split | test |
| Metric | micro/macro-F1 in 3 variants (notebook, seen_test, all_test); P@1 and top-1 label-F1 per bucket with 95% bootstrap CI |
| Comparison | Buckets by the train support of the sentence's rarest gold label: 0, 1-4, 5-9, 10-19, 20-49, 50+ (fixed in the evidence-pack brief). |
| Seeds | 42-44 |
| Dev-only tuning | nothing tuned |
| Decision rule | H2 is called supported per bucket only if the paired bootstrap CI of (fusion - matcher) excludes 0. |
| What counts as failure / prior exposure | Bucket point values were already seen (05_rarity_buckets.csv). New: CIs and paired CIs. Small buckets (n=10, 34, 30) are expected to be inconclusive and will be reported so. |

Split discipline: anything tuned is tuned on DEV only. The test split is evaluated once per configuration listed here. Uncertainty: paired/percentile bootstrap over test sentences, 10,000 resamples, numpy default_rng(20261114). Systems (fixed): SVM (refit, deterministic); RoBERTa and SecBERT = mean probability of seeds 42-44; matcher = mean score of seeds 42-44; fusion = z-score sum with weights (3,1,1,1) in the order matcher, SVM, RoBERTa, SecBERT.
