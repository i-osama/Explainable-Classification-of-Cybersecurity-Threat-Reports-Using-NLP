# PLAN

Form per task: Goal | Inputs | Outputs | Steps (checkable) | DONE-WHEN | Risk and fallback | Local minutes | Colab.
Written before each task starts; results are recorded in `PROGRESS.md`, decisions in `DECISIONS.md`.

## T0 Recon, gap audit, plan
- Goal: know what exists, what is missing, in what order to close it.
- Inputs: `_evidence_pack\PROGRESS.md`, `_evidence_pack\EVIDENCE_REPORT.md`.
- Outputs: `GAP_REGISTER.md`, `PLAN.md`, `STATUS.yaml`.
- Steps: read the two files -> 17-row gap table exists; write plan -> 10 task blocks exist; write status -> YAML parses.
- DONE-WHEN: the three files exist and `STATUS.yaml` loads with `yaml.safe_load`.
- Risk: none. Local: 10 min. Colab: N.

## T1 Truth layer and data models
- Goal: one machine-readable source for every number; typed, validated tables.
- Inputs: `_evidence_pack\*.csv`, `Dataset\*`, saved score files.
- Outputs: `src\ttpmap\schema.py`, `results\tables\*.parquet`, `thesis_numbers.json`, `THESIS_MAP.md`, `docs\DATA_DICTIONARY.md`, ER diagram (Mermaid + PNG).
- Steps: pydantic models -> import works; build tables without sentence text (ids + SHA-256 only) -> validation passes on every row;
  build numbers -> all 40 ledger ids present with status; thesis map -> one row per id.
- DONE-WHEN: `python scripts\build_numbers.py` exits 0 and prints 40/40 ledger claims; schema validation passes on every shipped table.
- Risk: a value cannot be derived by script -> status NOTES-ONLY or NOT-FOUND, never typed by hand. Local: 5 min. Colab: N.

## T2 Code package and tests
- Goal: a small tested library instead of loose scripts.
- Inputs: `_evidence_pack\scripts\common.py`, `systems.py`, `t3`-`t7`.
- Outputs: `src\ttpmap\{data,metrics,fusion,stats,explain,cli}.py`, `viz\`, `configs\*.yaml`, `tests\`, `scripts\verify_claims.py`, `scripts\check_hashes.py`.
- Steps: port metrics with three F1 variants -> toy tests pass; fusion with dev-only guard -> leakage test fails on test ids; regression test -> headline numbers within 0.001;
  CLI -> `python -m ttpmap verify` exits 0.
- DONE-WHEN: test suite green; `verify_claims.py` counts equal the ledger.
- Risk: `pytest` is not installed and installing was not permitted -> tests are plain `test_*` functions that also run under `scripts\run_tests.py`; gate reports which runner was used. Local: 5 min. Colab: N.

## T3 No-training analyses
- Goal: close gaps 3-10 and 12 with saved scores or inference under 10 minutes.
- Inputs: saved probabilities and scores, saved checkpoints (inference only), SHAP file.
- Outputs: `experiments\prereg\*.md` (timestamp + SHA-256, written first), `results\*.csv`, new entries in `thesis_numbers.json`.
- Steps: prereg files hashed before any analysis script exists in `results\`; frequency-prior baseline; ablation with CIs; weight surface (255 and 1,711 grids, dev and test, selection on dev);
  threshold grid above 0.85; F1 variants; support buckets with CIs; tactic, confusions, parent/sub; ECE + reliability bins; efficiency; 128 vs 256 on truncated sentences;
  faithfulness (deletion, insertion, comprehensiveness, sufficiency, random baseline) on the first 100 sentences of the fixed permutation; Holm over the comparison family.
- DONE-WHEN: every analysis has a CSV and number entries, or is listed TODO-COLAB.
- Risk: an inference step exceeds 10 minutes -> stop it, move to notebook 06, mark TODO-COLAB. Local: 40 min. Colab: N (overflow Y).

## T4 Figures
- Goal: 19 figures regenerated from CSV, thesis-ready.
- Inputs: `results\*.csv`, `thesis_numbers.json`, `_evidence_pack` outputs.
- Outputs: `figures\figNN_name.{png,svg}`, `figures\FIGURES.md`, `src\ttpmap\viz\*.py`.
- Steps: one function per figure -> file pair exists; FIGURES.md row with claim ids, source, script, alt text.
- DONE-WHEN: 19 PNG + 19 SVG + 19 rows; Colab-dependent panels carry the word PLACEHOLDER.
- Risk: diagram layout by code is plain -> acceptable; clarity over decoration. Local: 15 min. Colab: N.

## T5 Colab notebooks
- Goal: every training or GPU step is one click away and honest about not having run.
- Inputs: original notebooks (read-only), `_evidence_pack\09_repro\colab_fusion_shap.ipynb`, package code.
- Outputs: `notebooks\00`-`10`, `notebooks\RUN_ORDER.md`, `results\smoke_logs\*.json`.
- Steps: generator writes notebooks -> nbformat validates; SMOKE=True run with nbclient on CPU-feasible ones -> log per notebook; status header says NOT RUN ON COLAB.
- DONE-WHEN: all validate; smoke logs exist; none claims a Colab run.
- Risk: smoke run needs a model download or more than a few minutes -> cell guarded, logged as skipped. Local: 30 min. Colab: Y (author).

## T6 Human-study protocol and verified related work
- Goal: a study design that can succeed where the first failed; a reference list that is checked.
- Outputs: `docs\HUMAN_STUDY_PROTOCOL.md`, `scripts\make_rating_sheet.py`, `results\human_power_simulation.csv`, `docs\RELATED_WORK_VERIFIED.md`.
- Steps: protocol with scale anchors, blinding, controls, analysis plan; power by simulation -> CSV; web check of each reference -> row VERIFIED or UNVERIFIED with URL.
- DONE-WHEN: every reference row has a status and a URL.
- Risk: web tools fail on a source -> row stays UNVERIFIED. The thesis draft is not in the folder, so "every reference used in the thesis" is limited to references named in project files. Local: 20 min. Colab: N.

## T7 Report, story, status board
- Outputs: `scripts\build_report.py`, `report\index.html`, `README.md`, `INVIGILATOR_GUIDE.md`, `PROCESS_LOG.md`, `docs\ETHICS_AND_LIMITATIONS.md`, `docs\THREATS_TO_VALIDITY.md`, `docs\MODEL_CARDS\*.md`, `docs\DATA_CARD.md`, `CITATION.cff`, `LICENSE-NOTE.md`.
- Steps: templates render from `thesis_numbers.json` -> no number typed in a template; report inlines images -> opens offline.
- DONE-WHEN: report exists as one file; every number in it resolves to an id.
- Risk: author name, title page data unknown -> placeholders marked AUTHOR-TO-FILL. Local: 20 min. Colab: N.

## T8 QA gates
- Steps: tests; verify_claims; number-consistency scan; nbformat + smoke logs; figure completeness; link check; secret/PII/text scan; hashes; zip size.
- DONE-WHEN: `results\qa_gates.json` lists each gate PASS or FAIL with reason. Local: 10 min.

## T9 Package and hand-off
- Outputs: `E:\Osamas Paper\_showcase.zip`, final terminal summary. Optional Dockerfile, CI workflow, pre-commit config marked UNTESTED.
- DONE-WHEN: zip under 50 MB, exclusions listed. Local: 5 min.
