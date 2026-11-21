# Pre-registration 15_stacked_fusion: Q1 plan Task 4: learned (stacked) fusion (local CPU)

| field | content |
|---|---|
| Hypothesis | H: a logistic-regression stacker over the four z-scored components plus label-support features beats the hand-set (3,1,1,1) fusion on test P@1. |
| Split | fit and C selection on DEV only (5-fold CV by sentence, KFold shuffle seed 20261114), final fit on all dev; TEST once |
| Metric | P@1 (primary), MRR@3, R@5, support-bucket P@1 |
| Comparison | Features per (sentence, label): z_matcher, z_svm, z_roberta, z_secbert (seed-averaged components), log1p(train_count), seen flag, log(matcher rank). sklearn LogisticRegression (L2, lbfgs, max_iter 2000), C in {0.01, 0.1, 1, 10}, chosen by mean dev-fold MRR@3. Fitting rows: all gold pairs + 50 random negative labels per sentence (default_rng(20261114)); scoring uses all 733 labels. |
| Seeds | 42-44 (saved) |
| Dev-only tuning | C by dev-fold MRR@3; a LeakageError is raised if the fit is called with any split other than dev |
| Decision rule | Family = stacker vs (3,1,1,1) and stacker vs (4,1,1,1) (2 tests, Holm). Success = Holm p < 0.05 vs (3,1,1,1) and CI excluding 0. Otherwise a failed extension, reported. |
| What counts as failure / prior exposure | Dev has 604 sentences; overfitting dev is the expected failure mode. The stacker's test number is computed once. |

Split discipline: anything tuned is tuned on DEV only. The test split is evaluated once per configuration listed here. Uncertainty: paired/percentile bootstrap over test sentences, 10,000 resamples, numpy default_rng(20261114). Systems (fixed): SVM (refit, deterministic); RoBERTa and SecBERT = mean probability of seeds 42-44; matcher = mean score of seeds 42-44; fusion = z-score sum with weights (3,1,1,1) in the order matcher, SVM, RoBERTa, SecBERT.
