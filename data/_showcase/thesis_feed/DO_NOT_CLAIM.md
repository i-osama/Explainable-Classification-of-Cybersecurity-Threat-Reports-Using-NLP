# Claims the evidence does not support

| do not claim | why (evidence) |
|---|---|
| Fusion beats the matcher ensemble | +0.026 [0.001, 0.051]; McNemar p 0.048; Holm p 0.190 over 8 tests |
| Transformers beat TF-IDF + SVM | RoBERTa minus SVM +0.014 [-0.014, 0.041], Holm p 1.000; micro-F1 0.705 +/- 0.011 vs 0.696 |
| SecBERT (security pre-training) beats RoBERTa, or the reverse | +0.001 [-0.023, 0.025] |
| Fusion helps unseen or rare techniques | unseen P@1 0.000; support 1-4: 0.294 vs matcher 0.559 |
| The model predicts techniques never seen in training | only the matcher can; unseen P@1 of the fusion is 0.000; R@5 0.50 |
| Support-aware fusion improves results | failed its pre-registered rule (False); Holm p 0.453 |
| The explanations explain the fused system | they explain RoBERTa seed 42; top-1 differs from the fusion on 108 of 725 (14.9%) sentences |
| Explanations are plausible to analysts | only study: Krippendorff alpha -0.057 (nominal), +0.031 (ordinal); third rater 3 sentences |
| Better than the state of the art / beats Nguyen et al. | baseline not re-run; split and training mode unverified; our MRR@3 0.856 is below their 0.864 |
| (3,1,1,1) is the best weight setting | it wins the 255-setting grid only; the 1,711 grid picks (4,1,1,1); `B14` |
| Reading longer inputs would help | 256 tokens at inference: RoBERTa 19 vs 17 of 34; training at 256 not tested |
| Results hold for other datasets or ATT&CK versions | one dataset, one split; label space = ATT&CK v12.1 (`A11`); drift to the current release in `AD1` |
| Train and test are disjoint | exact 1 / 0; near-duplicate +1 / +3 (effect on P@1 at most 0.0007) |
| Classifier probabilities are calibrated | ECE 0.172 +/- 0.007 (RoBERTa); mean confidence 0.913 |
| The classifiers rely on threat-group names | masking groups: -0.001 [-0.004, 0.000], Holm p 1.000 |
| Every model is robust to surface noise | the ensemble is; RoBERTa alone loses -0.030 [-0.052, -0.010] on lower-cased text |
| A learned (stacked) fusion beats the weighted sum | -0.014 [-0.026, -0.001]; success rule False |
| More training data from the sibling sources helps | SVM (c) minus (a) -0.077 [-0.116, -0.040] |
| Sibling data improves the fusion | 0.817 is EXPLORATORY: not pre-registered, read on test |
| RoBERTa and the SVM perform the same | the study cannot detect differences below 0.048 (MDE); say "no difference larger than about 0.048" |
| An LLM improves on the matcher | best local variant (re-ranking) -0.179 [-0.215, -0.143]; only a 7B open model was tested |
| Conformal coverage holds for every label or bucket | marginal guarantee only; unseen-label coverage of the fusion 0.00 |
| Classifier conformal sets need hundreds of labels | artefact of the z-scored representation (D27); raw scores (POST-HOC): RoBERTa 6.15 labels |
| The fusion triages clearly better than the matcher | AURC difference -0.0119 [-0.024, -0.001], Holm p 0.040: small margin |
| TRAM has a label-noise rate of N% | 37 unvalidated candidates (prereg 20, EXPLORATORY) |
| The results hold for the current ATT&CK release | 39 test sentences carry a label not active in v20.1 (collection modified 2026-11-05); 125 current techniques are outside the label space |
| The app's live mode shows the reported fusion | live mode is classifier-only (SVM + RoBERTa s42 + SecBERT s42); the reported fusion needs the matcher weights `[PENDING: T1.matcher_retrained_p1]` |
| The app's live conformal sets carry the coverage guarantee | live-mode thresholds are fitted on dev and never evaluated on test |
| The generated explanations are correct or help analysts | grounding pass 23 of 100 (23%) only checks that quoted words are top-5 SHAP words; no human study of the explanations |
| The replay SHAP explains the fusion | it explains RoBERTa seed 42; top-1 differs from the fusion on 108 of 725 (14.9%) |
