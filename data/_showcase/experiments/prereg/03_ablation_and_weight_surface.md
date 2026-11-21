# Pre-registration 03_ablation_and_weight_surface: Fusion ablation and weight-sensitivity surface

| field | content |
|---|---|
| Hypothesis | H1: removing any component lowers test P@1. H2: test P@1 is flat (within 0.01) across the 10 best dev settings of each grid, i.e. the result does not hinge on (3,1,1,1). |
| Split | dev for ranking settings; test reported for every setting but never used to rank |
| Metric | P@1 and MRR@3 |
| Comparison | Ablation: (3,1,1,1) with one weight set to 0, seed-averaged components. Surface: both dev grids (255 and 1,711 settings), matcher seed 42 as in the notebook, plus the seed-averaged matcher. |
| Seeds | none |
| Dev-only tuning | selection objective = dev MRR@3 (4 d.p.), tie-break dev P@1 (as in the notebook) |
| Decision rule | H1 supported for a component only if its ablation contrast passes the rule of prereg 01. H2 supported if max-min test P@1 over the top-10 dev settings <= 0.01 on both grids. |
| What counts as failure / prior exposure | Ablation point values and the top-10 wide-grid test scores were already seen (evidence pack; notebook output). New here: CIs, tests, the full dev+test surface. |

Split discipline: anything tuned is tuned on DEV only. The test split is evaluated once per configuration listed here. Uncertainty: paired/percentile bootstrap over test sentences, 10,000 resamples, numpy default_rng(20261114). Systems (fixed): SVM (refit, deterministic); RoBERTa and SecBERT = mean probability of seeds 42-44; matcher = mean score of seeds 42-44; fusion = z-score sum with weights (3,1,1,1) in the order matcher, SVM, RoBERTa, SecBERT.
