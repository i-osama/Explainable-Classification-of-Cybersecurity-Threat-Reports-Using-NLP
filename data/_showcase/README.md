# Explainable classification of cyber-threat reports: research showcase

Sentence-level mapping of CTI text to MITRE ATT&CK techniques on TRAM, with word-level explanations. This folder is the auditable companion of the thesis:
code, data models, results, figures, notebooks, and an honest status board. Every number below is rendered from `thesis_numbers.json`.

## 60-second tour

1. **Task.** One sentence of a threat report in, a ranked list of ATT&CK techniques out, plus the words that drove the top prediction.
2. **Main result.** Fusion P@1 0.803 [0.774, 0.832] (seed-averaged; 0.796 +/- 0.006 seed-paired). It beats the classifiers-only ensemble by +0.029. It does not beat the matcher ensemble after correction for 8 tests (Holm p 0.190).
3. **Main limits.** No gain on rare or unseen techniques; explanations cover one RoBERTa model, not the fusion; the human study is at chance. Full list: `thesis_feed/DO_NOT_CLAIM.md`.
4. **Check it yourself.** `powershell -File demo.ps1` recomputes the headline numbers from the saved prediction files in under a minute and prints PASS or FAIL.
5. **Read it.** Open `report/index.html` (one offline file). What is still open: the status board below and `STATUS.yaml`.

## One-page story

**Task.** Given one sentence from a cyber-threat-intelligence report, rank the MITRE ATT&CK techniques it describes, and show which words drove the top prediction,
so that an analyst can check the prediction instead of trusting it. Data: TRAM, 4,797 sentences (3,468 / 604 / 725 train / dev / test), 180 labels in training, 127 in test of which 10 never occur in training.

**What was built.** Four components (TF-IDF + linear SVM, RoBERTa, SecBERT, a fine-tuned bge bi-encoder that matches sentences to technique descriptions) and a late fusion of their
per-sentence z-scores with weights chosen on the development set only.

**What the evidence supports.**
- Fusion (3,1,1,1) reaches P@1 0.803 [0.774, 0.832] with all components seed-averaged; 0.796 +/- 0.006 seed-paired; 0.800 +/- 0.001 in the notebook's definition. It beats the classifiers-only ensemble (+0.029, Holm p 0.000).
- Word-level SHAP explanations of the RoBERTa classifier are faithful to that model: masking the three top words lowers the predicted logit by 10.13 more than masking three random words (644 / 645 sentences), and deletion, insertion, comprehensiveness and sufficiency all favour SHAP order.

**What the evidence does not support (reported as findings).**
- Transformers are not better than the SVM here: RoBERTa minus SVM is +0.014 [-0.014, 0.041], Holm p 1.000.
- The fusion's gain over the matcher ensemble is not robust: +0.026 [0.001, 0.051], exact McNemar p 0.048, Holm p 0.190.
- The fusion does not help rare or unseen techniques: P@1 0.000 on the 10 unseen-label sentences (matcher 0.200) and 0.294 vs 0.559 for labels with 1-4 training sentences. A pre-registered support-aware fusion did not fix this (success rule met: False).
- The first human plausibility study is at chance agreement (Krippendorff alpha -0.057); a second study is designed but not run.
- The explained model is one RoBERTa seed, not the fusion: their top-1 labels differ on 108 of 725 (14.9%) test sentences. SHAP of the full fusion is not available (the matcher's weights were never saved).
- The published baseline (P@1 0.770, MRR@3 0.864) was not re-run; the comparison is side by side, not controlled.


## Verify in 10 minutes

See `INVIGILATOR_GUIDE.md`. Short version, from this folder, with the project's Python:

```
python scripts/run_tests.py        # unit, leakage, determinism and regression tests
python scripts/verify_claims.py    # recomputes the headline numbers from saved predictions
python scripts/check_hashes.py     # SHA-256 of every input and shipped output
start report\index.html            # the whole story, offline
```

## Status board

| id | area | item | state | evidence |
|---|---|---|---|---|
| S01 | Data | Split sizes, label counts, overlap, truncation | **DONE** | _evidence_pack/01_dataset.md |
| S02 | Data | Data licence: HF card field is 'cc' with no variant (verified); upstream TRAM repo Apache-2.0; ATT&CK version string in data still absent | **PARTIAL** | docs/DATA_CARD.md, LICENSE-NOTE.md |
| S03 | Results | All headline numbers recomputed from saved predictions | **DONE** | scripts/verify_claims.py |
| S04 | Results | Fusion headline definition: author chose B13a (seed-averaged, 0.803 with CI) on 15 Nov; B12a (seed-paired mean +/- sd) reported beside it | **DONE** | DECISIONS.md D24 |
| S05 | Baselines | Frequency prior, TF-IDF SVM, zero-shot bge | **DONE** | results/systems.csv |
| S06 | Baselines | Published baseline on the same protocol | **TODO-COLAB** | notebooks/09_baseline_same_protocol.ipynb |
| S07 | Baselines | LLM baseline: open-weights qwen2.5:7b, 3 variants (prereg 17): no variant beats the matcher (D26); API model optional | **NEGATIVE-RESULT** | results/llm_baseline.csv, llm_family.csv; notebooks/10 for an API model |
| S08 | Analysis | Ablation, weight sensitivity, threshold grid, F1 variants | **DONE** | results/ablation.csv, weight_surface.csv, threshold_grid.csv, f1_variants.csv |
| S09 | Analysis | Error analysis by support, tactic, confusion | **DONE** | results/support_buckets.csv |
| S10 | Analysis | Fusion does not help unseen and rare labels | **NEGATIVE-RESULT** | results/support_buckets.csv |
| S11 | Statistics | Paired bootstrap, exact McNemar, Holm correction | **DONE** | results/comparisons.csv |
| S12 | Statistics | Transformers vs SVM: no supported difference | **NEGATIVE-RESULT** | results/comparisons.csv |
| S13 | Explainability | Word-level SHAP for one RoBERTa seed, all test sentences | **DONE** | _evidence_pack/06_shap.md |
| S14 | Explainability | Faithfulness: deletion, insertion, comprehensiveness, sufficiency | **DONE** | results/faithfulness.csv |
| S15 | Explainability | SHAP of the full fusion, seed 42, 100 sentences (notebook 06 on Kaggle T4, 16 Nov) | **DONE** | results/colab/manifest_fusion_shap.json |
| S16 | Human study | First plausibility study: agreement at chance | **NEGATIVE-RESULT** | _evidence_pack/07_human.md |
| S17 | Human study | Second study with protocol, 3+ raters | **TODO-AUTHOR** | docs/HUMAN_STUDY_PROTOCOL.md |
| S18 | Efficiency | Parameters and CPU latency | **DONE** | results/efficiency.csv |
| S19 | Robustness | Extra seeds 45-46 | **TODO-COLAB** | notebooks/03, notebooks/04 |
| S20 | Extension | Support-aware fusion (two pre-registered variants, run locally): no supported gain | **NEGATIVE-RESULT** | results/support_aware_v2.csv, support_aware_family.csv |
| S27 | Statistics | Fusion vs matcher ensemble does not survive Holm correction | **NEGATIVE-RESULT** | results/comparisons.csv |
| S28 | Reproducibility | Number audit of Thesis_Draft_v2.2.docx against thesis_numbers.json (D30): unregistered numbers are literature values and settings; 13 of 18 confidence intervals in the draft are still the 1,000-resample values (C3, C4, C2/C3/C4 MRR@3) although the draft states 10,000; '23 tokens' (p370) not reproduced by the data | **DONE** | AUDIT_TODO.md, results/number_audit_v2_2/intervals.csv, audit_report.md |
| S29 | Explainability | 256 tokens at inference on truncated sentences: no gain (training at 256 not tested) | **NEGATIVE-RESULT** | results/maxlen.csv |
| S21 | Extension | Objective (b): sibling datasets -> TRAM test (SVM done locally: siblings hurt; transformers on Colab) | **PARTIAL** | results/cross_dataset_svm.csv; notebooks/08 |
| S22 | Reproducibility | Package, tests, hashes, run order | **DONE** | INVIGILATOR_GUIDE.md |
| S23 | Reproducibility | Colab environment capture | **TODO-COLAB** | notebooks/00 |
| S24 | Reproducibility | Matcher weights: seed 42 retrained and saved (notebook 04 on Kaggle T4, 16 Nov); seeds 43-44 not retrained | **PARTIAL** | results/colab/manifest_matcher_ft20_s42.json |
| S25 | Release | Git repository, licence choice, author metadata | **TODO-AUTHOR** | LICENSE-NOTE.md, CITATION.cff |
| S26 | Related work | Reference verification: 20 core VERIFIED, 2 PARTLY (one number each), 10 of 11 method references VERIFIED (Holm on JSTOR) | **PARTIAL** | docs/RELATED_WORK_VERIFIED.md |
| S30 | Explainability | Plain-language matcher/fusion explainer, 8 errors corrected, every number registered | **DONE** | thesis_feed/EXPLAINER_MATCHER_FUSION.md |
| S31 | Robustness | Robustness and shortcut test, 5 pre-registered perturbations: ensemble robust, no measurable group-name dependence | **DONE** | results/robustness.csv, robustness_family.csv (prereg 14) |
| S32 | Extension | Learned (stacked) fusion does not beat (3,1,1,1) | **NEGATIVE-RESULT** | results/stacking.csv (prereg 15) |
| S33 | Statistics | Minimum detectable effect per comparison (power 0.8) | **DONE** | results/power_mde.csv |
| S34 | Reproducibility | Hash-checked ingest of Colab outputs | **DONE** | scripts/ingest_colab.py, tests/test_ingest.py |
| S35 | Release | Article brief and claude.ai project instructions generated from the registry | **DONE** | thesis_feed/Q1_MANUSCRIPT_BRIEF.md, WEB_CLAUDE_PROMPT.md |
| S36 | Robustness | Robustness of the full fusion (needs the retrained matcher weights) | **TODO-COLAB** | notebooks/04 then scripts/run_robustness.py |
| S37 | Uncertainty | Split-conformal candidate sets (prereg 18): fusion meets nominal coverage with the smallest sets; post-hoc raw-score variant for classifiers (D27) | **DONE** | results/conformal.csv, conformal_family.csv, conformal_buckets.csv, conformal_posthoc_raw.csv |
| S38 | Uncertainty | Abstention for analyst triage (prereg 19): fusion has the lowest AURC; margin vs matcher small | **DONE** | results/selective.csv, selective_family.csv, risk_coverage.csv |
| S39 | Data | Label-noise candidates (prereg 20, EXPLORATORY); human check of the review sheet pending | **TODO-AUTHOR** | results/label_noise_candidates.csv, label_noise_summary.csv; human_study/materials_local/label_noise_review.xlsx |
| S40 | Data | ATT&CK version drift v12.1 to current release (prereg 21); description similarity fixed to autojunk off (D28) | **DONE** | results/attack_drift.csv, attack_drift_ids.csv, attack_version.csv |
| S41 | Release | REFORMS reporting checklist (32 items) with evidence and open holes | **DONE** | docs/REFORMS_CHECKLIST.md |
| S42 | Related work | 2026 refresh: 3 new TTP-mapping papers and 6 method references verified | **DONE** | docs/RELATED_WORK_VERIFIED.md section F |
| S43 | Release | Explainer app (objective c, ..	tp_app): replay reproduces all registered checks after the triage-threshold fix (D29); live mode timed; grounding of LLM explanations measured; AI assistance disclosed in its README | **DONE** | results/app_verify.csv, app_live_timing.csv, app_grounding.csv; ttp_app/README.md |
| S44 | Release | Design-science framing (D31): system chapter (requirements, architecture, verification), demo guide with screenshots, double-click launcher, usability study kit (SUS); the usability study itself is the author's task (T9.usability_sus) | **PARTIAL** | thesis_feed/ch4b_system_design.md; ttp_app/docs/DEMO_GUIDE.md; ttp_app/usability/ |

Truth file: 649 entries: NOT-FOUND 10, NOTES-ONLY 2, RECOMPUTED 622, TODO-COLAB 6, VERIFIED 9. Nothing marked TODO-COLAB or NOT-FOUND carries a value.

## Folder map

| path | content |
|---|---|
| `thesis_numbers.json`, `THESIS_MAP.md` | single source of truth for every number; map from thesis item to file and script |
| `THESIS_PLACEHOLDERS.md` | answers to the open items of the draft, plus the number audit of the draft |
| `GAP_REGISTER.md`, `PLAN.md`, `PROGRESS.md`, `DECISIONS.md`, `STATUS.yaml`, `PROCESS_LOG.md` | what was missing, what was planned, what was done, why |
| `src/ttpmap/` | package: data models, loaders, the one metric implementation, fusion with dev-only guards, statistics, explanation utilities, figures, CLI |
| `tests/`, `scripts/` | tests; `verify_claims.py`, `check_hashes.py`, analysis and build scripts |
| `experiments/prereg/` | pre-registrations, sealed with timestamp and SHA-256 before the analysis ran |
| `results/` | CSV per analysis, typed tables (`tables/*.parquet`, no sentence text), hashes, smoke logs |
| `figures/` | 19 figures as PNG and SVG, `FIGURES.md` |
| `notebooks/` | Colab notebooks 00-10 and `RUN_ORDER.md`; none has been run on Colab |
| `docs/` | data card, data dictionary, model cards, ethics, threats to validity, verified references, human-study protocol |
| `report/index.html` | self-contained report |
| `../_evidence_pack/` | the earlier audit of the 40 claims of the draft (read-only base) |

## What is not here

Model weights, the TRAM sentences, rating sheets and the baseline paper are not in this folder or in the repository (size, unknown data licence, privacy).
`docs/DATA_CARD.md` says how to obtain the data; `notebooks/04_train_matcher_save.ipynb` retrains the one model whose weights were never saved.

## AI assistance

Claude Code (Anthropic) was used for engineering and analysis in this folder: refactoring the notebooks' analysis code into a package, writing tests and scripts,
recomputing every number from saved predictions, generating figures, notebooks and this documentation. The experiments' design, the original training runs and the
interpretation are the author's; the author checks and finalises all wording according to the university's AI-use policy and must be able to explain every number and decision.
No text here was written or altered to evade AI-detection tools.
