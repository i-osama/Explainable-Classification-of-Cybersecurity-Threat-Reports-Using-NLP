# Pre-registration 10_new_seeds_45_46: Additional seeds 45 and 46 (Colab)

| field | content |
|---|---|
| Hypothesis | H: adding two seeds does not move any 3-seed mean by more than one standard deviation. |
| Split | dev for epoch/threshold selection; test once per run |
| Metric | micro-F1, macro-F1, P@1, MRR@3 per seed; 5-seed mean and sd |
| Comparison | RoBERTa, SecBERT, matcher with the unchanged training settings |
| Seeds | 45, 46 (new); 42-44 untouched |
| Dev-only tuning | as in the original runs |
| Decision rule | Report 3-seed and 5-seed values side by side. No selection of seeds. |
| What counts as failure / prior exposure | If a run diverges it is reported, not replaced. TODO-COLAB. |

Split discipline: anything tuned is tuned on DEV only. The test split is evaluated once per configuration listed here. Uncertainty: paired/percentile bootstrap over test sentences, 10,000 resamples, numpy default_rng(20261114). Systems (fixed): SVM (refit, deterministic); RoBERTa and SecBERT = mean probability of seeds 42-44; matcher = mean score of seeds 42-44; fusion = z-score sum with weights (3,1,1,1) in the order matcher, SVM, RoBERTa, SecBERT.
