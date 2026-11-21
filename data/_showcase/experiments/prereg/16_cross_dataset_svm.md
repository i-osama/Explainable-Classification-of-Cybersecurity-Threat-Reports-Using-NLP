# Pre-registration 16_cross_dataset_svm: Q1 plan Task 5: objective (b), SVM part (local CPU)

| field | content |
|---|---|
| Hypothesis | H: adding the sibling sources (procedure, derived_procedure) to TRAM train raises TF-IDF + SVM test P@1; siblings alone transfer worse than TRAM alone. |
| Split | train on (a) TRAM train, (b) siblings only, (c) TRAM + siblings; TEST = TRAM test, once per training set |
| Metric | P@1 (primary), MRR@3, R@5, seen/unseen R@5, support-bucket P@1; removed-duplicate counts |
| Comparison | Siblings are de-duplicated against TRAM dev + test before training: exact (normalised text) and near (token-set Jaccard >= 0.90, as A6). Labels outside the 733-label space are dropped and counted. Same TF-IDF (1,2)-gram sublinear + LinearSVC C=1 one-vs-rest as the refit SVM; ranking metrics need no threshold. |
| Seeds | deterministic |
| Dev-only tuning | none |
| Decision rule | Family = (c) vs (a) and (b) vs (a) (2 tests, Holm). The transformer part of objective (b) stays in notebook 08 (prereg 11). |
| What counts as failure / prior exposure | No sibling-trained number has been computed before sealing. |

Split discipline: anything tuned is tuned on DEV only. The test split is evaluated once per configuration listed here. Uncertainty: paired/percentile bootstrap over test sentences, 10,000 resamples, numpy default_rng(20261114). Systems (fixed): SVM (refit, deterministic); RoBERTa and SecBERT = mean probability of seeds 42-44; matcher = mean score of seeds 42-44; fusion = z-score sum with weights (3,1,1,1) in the order matcher, SVM, RoBERTa, SecBERT.
