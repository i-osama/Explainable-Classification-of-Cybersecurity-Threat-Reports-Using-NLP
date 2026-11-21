# REFORMS checklist (Kapoor et al., Science Advances 2024)

Reporting standard: REFORMS, 32 items in 8 modules (template `checklist.docx` from reforms.cs.princeton.edu, read 15 Nov 2026; reference verified in `docs/RELATED_WORK_VERIFIED.md` section F).
For each item: where the evidence is, and an honest status. MET = reported with evidence in this package; PARTIAL = reported with a stated hole; NOT MET = missing; AUTHOR = the thesis text must state it (the package cannot).
No number appears here; every number lives in `thesis_numbers.json`.

| item | what REFORMS asks | status | evidence |
|---|---|---|---|
| 1a | population or distribution of the claim | MET | `docs/DATA_CARD.md` (English CTI sentences annotated with Enterprise ATT&CK ids, TRAM); `docs/THREATS_TO_VALIDITY.md` (external validity) |
| 1b | why this population | AUTHOR | thesis chapter 1; `thesis_feed/ch1_intro.md` |
| 1c | why ML | AUTHOR | thesis chapter 1 (manual mapping cost); `thesis_feed/ch1_intro.md` |
| 2a | dataset with link or DOI | MET | `docs/DATA_CARD.md` (Hugging Face dataset id, TRAM repository, licence fields verified); `results/hashes.json` |
| 2b | code with a versioned link | PARTIAL | code is in this package with SHA-256 hashes (`results/hashes.json`); no public versioned repository (author decision, `STATUS.yaml` S25) |
| 2c | computing infrastructure, software versions, run time | PARTIAL | `results/hardware.json`, `requirements.txt`, `results/efficiency.csv`, `results/process_timeline.csv`; the Colab environment of the original runs is not recorded (`STATUS.yaml` S23, TODO-COLAB) |
| 2d | README with instructions | MET | `README.md`, `INVIGILATOR_GUIDE.md`, `notebooks/RUN_ORDER.md` |
| 2e | reproduction script for all results | PARTIAL | `run_all.ps1`, `finish_q1.ps1`, `scripts/verify_claims.py` recompute every local number from saved predictions; GPU training is in the Colab notebooks and the matcher weights were never saved (`STATUS.yaml` S24) |
| 3a | data sources, collection time, annotation process | PARTIAL | `docs/DATA_CARD.md`; ATT&CK release inferred, not stored in the data (`results/attack_version.csv`); TRAM annotation process is upstream (TRAM wiki "Data Annotation") |
| 3b | sampling frame | PARTIAL | `docs/DATA_CARD.md`; how TRAM sentences were sampled from reports is not documented upstream |
| 3c | why the dataset suits the task | MET | `docs/DATA_CARD.md`; `thesis_feed/ch2_related.md` (TRAM is the common sentence-level benchmark) |
| 3d | outcome variable and its statistics | MET | `docs/DATA_DICTIONARY.md`; `_evidence_pack/01_dataset.md` (labels per sentence, label counts, support buckets) |
| 3e | number of samples | MET | `_evidence_pack/01_dataset.md`; registry keys in `thesis_numbers.json` |
| 3f | missing data by class | MET | no empty text, no empty label list and no NaN field in train, dev or test (checked 15 Nov 2026 with `ttpmap.data.load_split`); wave 2: labels revoked in ATT&CK are reported as a data-quality issue (`results/attack_drift.csv`, prereg 21) |
| 3g | representativeness of the sample for the claim | PARTIAL | `docs/THREATS_TO_VALIDITY.md`; one benchmark only; campaign-level and report-level settings differ (arXiv 2604.07470, 2606.18166) |
| 4a | excluded samples and why | MET | train = TRAM slice of `combined_train.csv`, exact-text dedup (`src/ttpmap/data.py`); dev/test near-duplicates against train measured (`results/overlap_sensitivity.csv`) |
| 4b | impossible or corrupt samples | PARTIAL | label-noise candidates listed, not yet validated by a human (`results/label_noise_candidates.csv`, prereg 20; review sheet with the author) |
| 4c | all transformations | MET | `src/ttpmap/data.py`, `src/ttpmap/fusion.py` (row z-score), `configs/systems.yaml` |
| 5a | models, features, loss | MET | `docs/MODEL_CARDS/`, `configs/systems.yaml` (TF-IDF + linear SVM, RoBERTa, SecBERT with BCE and optional pos_weight, bi-encoder matcher, z-score fusion) |
| 5b | why these model types | AUTHOR | thesis chapter 3; `thesis_feed/ch3_method.md` |
| 5c | evaluation method and splits | MET | fixed TRAM dev/test split; dev-only tuning; pre-registrations `experiments/prereg/01-21` sealed with SHA-256 |
| 5d | how the reported model was selected | MET | best epoch by dev micro-F1, fusion weights by dev grid (`results/weight_surface.csv`), headline definition decision D24 (`DECISIONS.md`) |
| 5e | hyper-parameter ranges, selection, final values | PARTIAL | fusion and threshold grids (`results/weight_surface.csv`, `results/threshold_grid.csv`); transformer hyper-parameters from `config.json` of each run; no search over transformer hyper-parameters was run |
| 5f | appropriate baselines | PARTIAL | frequency prior, TF-IDF + SVM, zero-shot matcher (`results/systems.csv`), local LLM (prereg 17); the published baseline is not re-run under the same protocol (`STATUS.yaml` S06, TODO-COLAB) |
| 6a | preprocessing and modelling use training data only | MET | `LeakageError` guards in `src/ttpmap/fusion.py`, `stack.py`, `conformal.py`, `selective.py`, tested in `tests/` |
| 6b | duplicates between train and test | MET | exact and near-duplicate removal sensitivity (`results/overlap_sensitivity.csv`); sibling sets deduplicated against TRAM dev/test (prereg 16) |
| 6c | features are legitimate (no leakage) | MET | shortcut test with group-name and IOC masking (`results/robustness.csv`, prereg 14) |
| 7a | all metrics, suitability of the selection metric | MET | P@1, MRR@3, R@5, micro/macro-F1 variants (`results/f1_variants.csv`), calibration (`results/calibration.csv`), conformal coverage and set size (prereg 18), AURC (prereg 19) |
| 7b | uncertainty estimates and how computed | MET | percentile bootstrap, 10,000 resamples, fixed seed (`src/ttpmap/stats.py`); seeds as mean +/- sd; Wilson intervals for coverage |
| 7c | choice of tests and their assumptions | MET | exact McNemar for paired hits, Holm per family, minimum detectable effects (`results/power_mde.csv`); Wilcoxon signed-rank for paired set sizes (prereg 18) |
| 8a | external validity | PARTIAL | cross-dataset SVM (`results/cross_dataset_svm.csv`); transformer cross-dataset runs TODO-COLAB (`STATUS.yaml` S21) |
| 8b | where the findings should not hold | MET | `docs/THREATS_TO_VALIDITY.md`, `thesis_feed/DO_NOT_CLAIM.md`; labels outside the v12.1 space and techniques added after v12.1 (`results/attack_drift.csv`) |

Open holes (the same ones `STATUS.yaml` lists): Colab environment (2c), matcher weights (2e), public versioned code (2b), published baseline under the same protocol (5f), transformer cross-dataset runs (8a), human validation of label-noise candidates (4b).
