# Pre-registration 19_selective_prediction: Q1 wave 2 Task 4: selective prediction for analyst triage (local CPU)

| field | content |
|---|---|
| Hypothesis | H: ranking sentences by the fusion's top-1 minus top-2 score margin gives a lower area under the risk-coverage curve (AURC, risk = 1 - hit at rank 1) than each component. |
| Split | thresholds on DEV; TEST once |
| Metric | AURC (primary), E-AURC, realised test coverage and selective P@1 at dev-chosen thresholds for target coverage 0.5, 0.8, 0.9 |
| Comparison | Systems: fusion (3,1,1,1), matcher, SVM, RoBERTa, SecBERT. Confidence = top-1 minus top-2 score (NaN as -inf). Stable sort for ties. Family = fusion AURC vs each component (4 tests): paired bootstrap over test sentences (both AURCs recomputed per resample), two-sided bootstrap p, Holm over 4. |
| Seeds | 42-44 (saved) |
| Dev-only tuning | confidence thresholds for each target coverage fitted on DEV only (LeakageError otherwise) |
| Decision rule | Supported for a component if Holm p < 0.05 and the 95% CI of AURC(fusion) - AURC(component) is below 0. |
| What counts as failure / prior exposure | Margins of z-score sums and of probabilities are on different scales; only within-system ordering is used, so this is valid. No risk-coverage curve was computed before sealing. |

Split discipline: anything tuned is tuned on DEV only. The test split is evaluated once per configuration listed here. Uncertainty: paired/percentile bootstrap over test sentences, 10,000 resamples, numpy default_rng(20261114). Systems (fixed): SVM (refit, deterministic); RoBERTa and SecBERT = mean probability of seeds 42-44; matcher = mean score of seeds 42-44; fusion = z-score sum with weights (3,1,1,1) in the order matcher, SVM, RoBERTa, SecBERT.
