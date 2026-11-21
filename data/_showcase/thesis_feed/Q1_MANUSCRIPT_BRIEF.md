# Article brief for the writer (claude.ai): sentence-level ATT&CK technique mapping on TRAM

Every number below is rendered from `thesis_numbers.json`; ids are in backticks in the tables of `THESIS_MAP.md`.
Pending Colab or author work is written as `[PENDING: <id>]`. Claims listed in `DO_NOT_CLAIM.md` are never made.

## 1 One-paragraph story
Mapping CTI sentences to ATT&CK techniques is a 733-label, long-tailed problem. A description-reading bi-encoder (matcher) and three supervised classifiers make different errors. A dev-tuned z-score fusion of the four reaches test P@1 0.803 [0.774, 0.832], MRR@3 0.856, R@5 0.917. It beats the classifiers-only ensemble (+0.029 [0.017, 0.043], Holm p 0.000), but not the matcher ensemble with statistical support (+0.026, Holm p 0.190). The tail is where it fails: the fusion gets P@1 0.000 on never-seen labels and 0.294 on labels with 1-4 training sentences, where the matcher alone gets 0.200 and 0.559. Three pre-registered fixes (support-aware weights, longer descriptions, a learned stacker) do not close this gap. The classifier ensemble is robust to five pre-registered input perturbations and shows no measurable dependence on threat-group names (few test sentences name one).

## 2 Contributions (each with its evidence)
1. A pre-registered, fully reproducible evaluation protocol: dev-only tuning, one test pass per configuration, paired bootstrap (10,000 resamples), exact McNemar, Holm, minimum detectable effects. Evidence: `experiments/prereg/` 01-21, `results/comparisons.csv`, `results/power_mde.csv`.
2. Description-based matching plus late fusion: matcher ensemble 0.777 [0.746, 0.807]; fusion 0.803; weights from a 255-setting dev grid (`B14`); sensitivity to a 1,711-setting grid (`B14.avg_wide`, test 0.810).
3. Honest failure analysis of the tail: support buckets (`G4`), unseen R@5 (`G6`), support-aware fusion (`G9`), longer descriptions (`M1.L256.*`), stacked fusion (`ST1`).
4. Robustness and shortcut analysis (new): five pre-registered perturbations (`R1`), see `Q1_FINDINGS.md`.
5. Data-scale check (new): sibling sources hurt the SVM (-0.077); transformer part `[PENDING: T6.cross_dataset]`.
6. Explanation faithfulness for RoBERTa (`E5`) and a human plausibility study at chance agreement (`D1`, `D2`); full-fusion SHAP `[PENDING: T2.full_fusion_shap]`.
7. LLM baseline with open weights (`L1`, prereg 17).
8. Uncertainty an analyst can use (new, wave 2): split-conformal candidate sets with a coverage guarantee (`CP1`, prereg 18; fusion about 2.80 labels for 90% coverage) and abstention for triage (`SP1`, prereg 19; lowest AURC 0.0715).
9. Data validity (new, wave 2): label-noise candidates (`LN1`, EXPLORATORY), ATT&CK version drift of the label space (`AD1`), REFORMS reporting checklist (`docs/REFORMS_CHECKLIST.md`).
10. Objective (c): a CPU-only explainer application that replays the test set from saved scores and reproduces the registered numbers (`APP1`), shows conformal sets, triage tiers, rarity and ATT&CK-drift warnings, SHAP words and grounded explanations (`APP2`, `APP3`); built with AI assistance (disclosed). See `Q1_FINDINGS.md` Q17.

## 3 Research questions
- RQ1 Does description-based matching add to supervised classifiers? (C1, A1)
- RQ2 Where does fusion help and where does it fail? (G4, G5, G6, ST1, G9)
- RQ3 Are the systems robust, and do they take shortcuts? (R1)
- RQ4 Do more training sources or an LLM change the picture? (X1, L1, T6)
- RQ5 Are the explanations faithful and plausible? (E5, D1)
- RQ6 Can the system tell an analyst how sure it is, and is the label space still valid? (CP1, SP1, LN1, AD1)

## 4 Structure and what goes where
| section | content | sources |
|---|---|---|
| Introduction | problem, long tail, contributions above | ch1_intro.md |
| Related work | verified references only | ch2_related.md, docs/RELATED_WORK_VERIFIED.md |
| Data and task | TRAM splits 3,468 / 604 / 725; 733-label space; overlap exact 1 / 0; near-duplicate +1 / +3 | ch3_method.md, docs/DATA_CARD.md |
| Methods | classifiers, matcher (EXPLAINER_MATCHER_FUSION.md method lines), fusion, stacker, perturbations, statistics | ch3_method.md, FUSION_DEFINITIONS.md, prereg 14-17 |
| Results | main table (EXPLAINER table), comparisons, tail buckets, robustness, stacking, cross-source, LLM, conformal sets, triage | ch5_results.md, NEW_FINDINGS.md, Q1_FINDINGS.md |
| Explainability | faithfulness, human study, fusion-vs-explained gap (108 of 725 (14.9%)); explainer application, objective (c) (`APP1`-`APP3`, AI assistance disclosed) | ch5_results.md, Q1_FINDINGS.md Q17, `ttp_app/README.md` |
| Discussion | what is and is not supported; MDE wording | DO_NOT_CLAIM.md, Q1_FINDINGS.md Q5 |
| Threats to validity | one dataset and split; baseline not re-run; ATT&CK v12.1 vs current (`AD1`); label-noise candidates (`LN1`) | docs/THREATS_TO_VALIDITY.md, Q1_FINDINGS.md Q13-Q14 |
| Ethics, reproducibility | dual use; no sentence text shipped; hashes; tests; REFORMS checklist (appendix) | docs/ETHICS_AND_LIMITATIONS.md, INVIGILATOR_GUIDE.md, docs/REFORMS_CHECKLIST.md |

## 5 Still open before submission
| item | id | who |
|---|---|---|
| Matcher retrained with saved weights | `T1.matcher_retrained_p1` | Colab (notebook 04) |
| Full-fusion SHAP | `T2.full_fusion_shap` | Colab (06) |
| Fusion replication with the retrained matcher | `T3.fusion_replication` | Colab (05) |
| Seeds 45 and 46 | `T4.seeds_45_46` | Colab (03, 04) |
| Published baseline under our protocol | `T5.baseline_same_protocol` | Colab (09) |
| Transformers on sibling sources | `T6.cross_dataset` | Colab (08) |
| Second human study, 3+ raters | `T8.human_study_v2` | author |
| Human check of the label-noise candidates (`LN1.n` sentences) | `LN1` | author (review sheet in `human_study/materials_local/`) |
| Dataset licence variant, author metadata | `N6.data_licence` | author |

Venue: a security or applied-ML journal. Check the current quartile (SJR / JCR) and scope of each candidate before choosing; do not state a quartile from memory.
