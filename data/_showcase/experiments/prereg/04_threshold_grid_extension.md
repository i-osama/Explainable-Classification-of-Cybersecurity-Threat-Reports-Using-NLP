# Pre-registration 04_threshold_grid_extension: Decision-threshold grid above 0.85

| field | content |
|---|---|
| Hypothesis | H: RoBERTa's dev-optimal threshold lies above the original grid's upper edge (0.85), and moving it changes test micro-F1 by less than 0.01. |
| Split | dev for selection; test micro-F1 reported once at the newly selected threshold |
| Metric | micro-F1 (notebook variant) and macro-F1 |
| Comparison | original grid np.arange(0.10, 0.90, 0.05) vs extended grid np.arange(0.10, 0.9951, 0.01); all 6 classifier runs |
| Seeds | 42, 43, 44 (saved probabilities) |
| Dev-only tuning | threshold = arg max dev micro-F1, first maximum |
| Decision rule | Report old and new threshold and the test delta per run. No headline number is replaced; the extended result is a sensitivity note. |
| What counts as failure / prior exposure | If |delta test micro-F1| >= 0.01 for RoBERTa on average, the thesis must state that the reported F1 is grid-limited. Not computed before. |

Split discipline: anything tuned is tuned on DEV only. The test split is evaluated once per configuration listed here. Uncertainty: paired/percentile bootstrap over test sentences, 10,000 resamples, numpy default_rng(20261114). Systems (fixed): SVM (refit, deterministic); RoBERTa and SecBERT = mean probability of seeds 42-44; matcher = mean score of seeds 42-44; fusion = z-score sum with weights (3,1,1,1) in the order matcher, SVM, RoBERTa, SecBERT.
