# Pre-registration 07_efficiency_latency: Model size and CPU latency

| field | content |
|---|---|
| Hypothesis | Descriptive, no hypothesis. |
| Split | 100 test sentences = first 100 of the fixed permutation |
| Metric | parameter count; median and p90 wall-clock seconds per sentence, batch size 1, 100 timed runs after 5 warm-up runs; peak resident memory of the process |
| Comparison | SVM vs RoBERTa vs SecBERT (single seed) on this PC's CPU; matcher cannot be timed (weights never saved) -> timed with the public base checkpoint and labelled as such |
| Seeds | seed 42 checkpoints |
| Dev-only tuning | nothing tuned |
| Decision rule | Report hardware (CPU model, threads, torch version) with the numbers. |
| What counts as failure / prior exposure | Latency on a shared desktop is noisy; medians only, no claims of significance. |

Split discipline: anything tuned is tuned on DEV only. The test split is evaluated once per configuration listed here. Uncertainty: paired/percentile bootstrap over test sentences, 10,000 resamples, numpy default_rng(20261114). Systems (fixed): SVM (refit, deterministic); RoBERTa and SecBERT = mean probability of seeds 42-44; matcher = mean score of seeds 42-44; fusion = z-score sum with weights (3,1,1,1) in the order matcher, SVM, RoBERTa, SecBERT.
