# Pre-registration 18_conformal_sets: Q1 wave 2 Task 3: split-conformal prediction sets (local CPU)

| field | content |
|---|---|
| Hypothesis | H1: split-conformal sets of the fusion calibrated on DEV reach the nominal coverage on TEST (all gold labels in the set) at alpha 0.10. H2: at alpha 0.10 the fusion's sets are smaller than the sets of each of its four components. |
| Split | calibration DEV (604 sentences); TEST (725) once per system, alpha and rule |
| Metric | coverage_all (all gold labels in the set; primary), coverage_any, mean / median / 90th-percentile set size, empty-set rate; coverage per support bucket of the rarest gold label |
| Comparison | Systems: fusion (3,1,1,1), matcher, SVM, RoBERTa, SecBERT (seed-averaged components). Rules: (a) score threshold, nonconformity = -min over gold labels of the system score, set = labels with score >= tau; (b) rank threshold, nonconformity = worst rank of a gold label, set = top-k. alpha in {0.10 (primary), 0.20}. Quantile = ceil((n+1)(1-alpha))-th smallest nonconformity on dev; above n gives the full label set. NaN scores are treated as -inf. |
| Seeds | 42-44 (saved) |
| Dev-only tuning | tau / k fitted on DEV only; a LeakageError is raised for any other split |
| Decision rule | H1 supported if the Wilson 95% CI of fusion test coverage_all at alpha 0.10 (rule a) contains 0.90. H2: family = fusion vs each component, per-sentence set size (rule a, alpha 0.10), two-sided Wilcoxon signed-rank, Holm over 4; supported if Holm p < 0.05 and the paired bootstrap CI of the mean size difference excludes 0 with fusion smaller. |
| What counts as failure / prior exposure | Coverage is marginal, not conditional on the label: low coverage for unseen and rare labels is expected and reported, not tested. Dev and test are assumed exchangeable (random TRAM split); if dev-test label shift is large the guarantee can fail and that is stated. No conformal set was computed before sealing. |

Split discipline: anything tuned is tuned on DEV only. The test split is evaluated once per configuration listed here. Uncertainty: paired/percentile bootstrap over test sentences, 10,000 resamples, numpy default_rng(20261114). Systems (fixed): SVM (refit, deterministic); RoBERTa and SecBERT = mean probability of seeds 42-44; matcher = mean score of seeds 42-44; fusion = z-score sum with weights (3,1,1,1) in the order matcher, SVM, RoBERTa, SecBERT.
