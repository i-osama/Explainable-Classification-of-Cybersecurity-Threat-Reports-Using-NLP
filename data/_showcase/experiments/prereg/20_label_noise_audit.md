# Pre-registration 20_label_noise_audit: Q1 wave 2 Task 5: label-noise candidates on TEST (EXPLORATORY, descriptive)

| field | content |
|---|---|
| Hypothesis | Q (no hypothesis test): how many fusion top-1 errors are sentences where all four components and the fusion agree on the same wrong top-1 label (consensus disagreement with the gold label)? |
| Split | TEST (725) |
| Metric | count and share of fusion top-1 errors that are consensus candidates; relation of the consensus label to the gold labels (parent or sub-technique, sibling sub-technique, same tactic, other) |
| Comparison | Candidate = fusion top-1 not in gold AND matcher, SVM, RoBERTa and SecBERT top-1 all equal the fusion top-1. Descriptive only. |
| Seeds | 42-44 (saved) |
| Dev-only tuning | nothing tuned |
| Decision rule | No decision rule: candidates are not label errors until a human checks them. The review sheet goes to the author (human_study/label_noise_review.xlsx). |
| What counts as failure / prior exposure | Consensus can be shared bias (all systems learnt the same shortcut), so the count is neither a lower nor an upper bound on label noise. Never computed before sealing. |

Split discipline: anything tuned is tuned on DEV only. The test split is evaluated once per configuration listed here. Uncertainty: paired/percentile bootstrap over test sentences, 10,000 resamples, numpy default_rng(20261114). Systems (fixed): SVM (refit, deterministic); RoBERTa and SecBERT = mean probability of seeds 42-44; matcher = mean score of seeds 42-44; fusion = z-score sum with weights (3,1,1,1) in the order matcher, SVM, RoBERTa, SecBERT.
