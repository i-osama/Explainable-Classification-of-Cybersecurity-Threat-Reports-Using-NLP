# PROGRESS (showcase)

Resume: run from `E:\Osamas Paper\_showcase` with `E:\Osamas Paper\.venv\Scripts\python.exe -X utf8`. Console output is truncated by a
plugin: redirect to a file. Rebuild everything: `powershell -File run_all.ps1` (`-Fast` skips 7 minutes of CPU inference).
Commit: `powershell -File scripts\git_commit.ps1 "T<n>: ..."` (guarded; pushes to the author's private backup remote).
Kill-switch: Tue 18 Nov 2026 18:00 Asia/Dhaka: unfinished items become FUTURE-WORK in STATUS.yaml, pre-registrations kept.

| Task | Status | Gate | Main files |
|---|---|---|---|
| T0 recon, gaps, plan | DONE | STATUS.yaml parses | GAP_REGISTER.md, PLAN.md, STATUS.yaml, DECISIONS.md |
| T1 truth layer, data models | DONE | 40/40 ledger ids; all table rows schema-valid | src/ttpmap/schema.py, results/tables/*.parquet, thesis_numbers.json, THESIS_MAP.md |
| T2 package, tests | DONE | 26 tests pass (fallback runner); verify_claims PASS | src/ttpmap/*, tests/*, scripts/run_tests.py, verify_claims.py, check_hashes.py, configs/* |
| Prompt B placeholder sheet | DONE | - | THESIS_PLACEHOLDERS.md (sections 1-14) |
| Draft number audit | DONE from the pasted ledger (no .docx on this PC) | 153 numbers: 128 supported, 8 differ | scripts/audit_numbers.py, audit_from_ledger.py, results/number_audit/* |
| T3 no-training analyses | DONE | every analysis has a CSV + number entries | experiments/prereg/01-13 + REGISTRY.csv, scripts/run_analyses.py, run_inference.py, run_support_aware_v2.py |
| T4 figures | DONE | 19 png + 19 svg + FIGURES.md | src/ttpmap/viz/*, scripts/make_figures.py, figures/* |
| T6 protocol + related work | DONE | every reference row has a status and URL | docs/RELATED_WORK_VERIFIED.md, docs/HUMAN_STUDY_PROTOCOL.md, scripts/make_rating_sheet.py, results/human_power_simulation.csv |
| T5 Colab notebooks | DONE (written, validated, smoke-run locally; NONE run on Colab) | 11 valid, 11 smoke PASS | notebooks/00-10, RUN_ORDER.md, scripts/make_notebooks.py, smoke_notebooks.py, results/smoke_logs/ |
| T7 report, README, cards | DONE | report is one offline file; unknown claim id aborts the build | scripts/build_docs.py, build_report.py, README.md, INVIGILATOR_GUIDE.md, PROCESS_LOG.md, docs/*, report/index.html |
| T8 QA gates | DONE | 9 of 9 PASS (results/qa_gates.json) | scripts/qa_gates.py, configs/number_whitelist.txt |
| T9 package | DONE | zip 5.5 MB | ../_showcase.zip, scripts/package.py, ci/ (UNTESTED templates) |

## Close-out tasks (E1-E8, started 14 Nov 2026 evening)

| Task | Status | Evidence |
|---|---|---|
| E1 state check | DONE | 26/26 tests, VERIFY PASS, 9/9 gates; no `thesis\` folder |
| E2 thesis feed | DONE | thesis_feed/ (7 chapter files, NEW_FINDINGS, DIFFERENCES, DO_NOT_CLAIM, 21 tables) |
| E3 fusion definitions | DONE | thesis_feed/FUSION_DEFINITIONS.md |
| E4 Colab runbook, resumable notebooks | DONE (nb03 resume code untested: GPU-only) | notebooks/COLAB_RUNBOOK.md; 11/11 smoke PASS, max 90 s |
| E5 human-study kit | DONE | docs/RATER_INSTRUCTIONS.md; scripts/validate_returned.py (self-tested on a copy); worked examples local only: human_study/materials_local/ |
| E6 repo polish | DONE | README 60-second tour; INVIGILATOR_GUIDE data-to-table flow; demo.ps1 (VERIFY: PASS); [FILL] marks in CITATION.cff, LICENSE-NOTE.md, DATA_CARD.md; 9/9 gates |
| E7 audit loop | PARTIAL: no .docx in thesis\ yet; dry run on the pasted v2 ledger | scripts/audit_loop.py, AUDIT_TODO.md (16 unregistered: 11 literature, 3 rounding, 2 settings) |
| E8 upload package, tag | DONE | UPLOAD_TO_CLAUDE_AI.zip (local, not committed), UPLOAD_INDEX.md, tag freeze-2026-11-14 |

## Open
- `pytest` 9.2.0 installed in `.venv` on 15 Nov 2026 (with streamlit for the app); `scripts/run_tests.py` still works without it.
- Thesis .docx not on this PC: run `python scripts\audit_numbers.py <docx> --registry thesis_numbers.json --out results\number_audit` on the real file.
- Colab: nothing run. Order in `notebooks/RUN_ORDER.md`. After a run: Prompt C (ingest).
- Human study v2: sheets generated locally in `human_study/sheets/` (3 raters); two worked examples from TRAINING sentences still to be written by the author before sending.
- Author decisions: fusion headline definition; licence; author metadata in CITATION.cff.

## Key results of T3 (all in thesis_numbers.json)
- Holm over the family of 8: fusion vs classifiers-only and the ablations of matcher and RoBERTa stay supported; fusion vs matcher ensemble does not.
- Support-aware fusion (two pre-registered variants): no supported gain over (3,1,1,1).
- Extended threshold grid moves RoBERTa thresholds but changes test micro-F1 by less than 0.003.
- Faithfulness: deletion, insertion, comprehensiveness, sufficiency all favour SHAP order over random order.
- 256 tokens at inference on the truncated sentences: no gain.
- Draft v2 still quotes 1,000-resample intervals for C3/C4 and three MRR@3 intervals that differ from the 10,000-resample values (THESIS_PLACEHOLDERS.md section 14).

## Q1 upgrade, 15 Nov 2026 (plan: `docs/superpowers/plans/2026-11-15-q1-upgrade.md`)
| task | state | evidence |
|---|---|---|
| T0 clean baseline, QA gate fixed (01 outputs, desktop.ini untracked) | DONE | commits 6ebac5e..99f25bb |
| T1 corrected explainer, matcher variants scored, 26 new ids | DONE | `thesis_feed/EXPLAINER_MATCHER_FUSION.md`, `results/matcher_variants.csv` |
| T2 preregs 14-17 sealed before any test number | DONE | `experiments/prereg/REGISTRY.csv` |
| T3 robustness and shortcut test | DONE | `results/robustness*.csv`, ids `R1.*` |
| T4 stacked fusion | NEGATIVE-RESULT | `results/stacking*.csv`, ids `ST1.*` |
| T5 cross-dataset, SVM part | DONE (siblings hurt the SVM; fusion signal EXPLORATORY) | `results/cross_dataset_*.csv`, ids `X1.*` |
| T6 minimum detectable effects | DONE | `results/power_mde.csv`, ids `P1.*` |
| T7 local LLM baseline (qwen2.5:7b, 3 variants) | NEGATIVE-RESULT (finished 11:44 on 15 Nov; no variant beats the matcher, D26) | `results/llm_baseline.csv`, `llm_family.csv`, ids `L1.*` |
| T8 hash-checked Colab ingest, runbook section 4 | DONE | `scripts/ingest_colab.py`, `tests/test_ingest.py` |
| T9 Q1 findings, article brief, claude.ai prompt, upload zip | DONE (LLM rows fill in after T7) | `thesis_feed/Q1_*.md`, `WEB_CLAUDE_PROMPT.md`, `UPLOAD_TO_CLAUDE_AI.zip` |
| T10 close-out | DONE except T7 scoring | tests 49/49, verify_claims PASS, prereg hashes OK, QA gates 9/9 |

Deviations from the plan text: `load_entity_names` takes the loaded STIX objects (testable without a file); `dedup_against` returns `{"exact", "near"}` counts; prereg 17 has 3 variants (closed, rr_matcher, rr_zero) and a family of 6, not 4; software and group masks are separate perturbations (group names are a pure shortcut test, tool names are partly real evidence).

## Q1 wave 2 (15 Nov 2026, 11:10-12:00 Dhaka; plan `docs/superpowers/plans/2026-11-15-q1-wave2.md`)

| task | state | evidence |
|---|---|---|
| T0 LLM close-out | DONE (finish_q1.ps1 11/11 OK, QA gates 9/9) | `results/llm_raw/finish_q1.log`, D26 |
| T1 related work: 3 papers of 2026 + 6 method references verified (arXiv API, Crossref, PMLR) | DONE | `docs/RELATED_WORK_VERIFIED.md` section F; ch2 literature table re-synchronised with the log |
| T2 preregs 18-21 sealed before any test number | DONE | `experiments/prereg/REGISTRY.csv` (21 sealed) |
| T3 split-conformal sets (prereg 18) | DONE (H1 and H2 met; POST-HOC raw-score variant, D27) | `results/conformal*.csv`, ids `CP1.*`, `CP2.*` |
| T4 abstention / AURC (prereg 19) | DONE (fusion lowest AURC, small margin vs matcher) | `results/selective*.csv`, `risk_coverage.csv`, ids `SP1.*`, `SP2.*` |
| T5 label-noise candidates (prereg 20, EXPLORATORY) | DONE; human check TODO-AUTHOR | `results/label_noise_*.csv`, ids `LN1.*` |
| T6 ATT&CK drift to the current release (prereg 21) | DONE | `results/attack_drift*.csv`, ids `AD1.*` |
| T7 REFORMS checklist | DONE | `docs/REFORMS_CHECKLIST.md` |
| T8 registry, thesis feed, STATUS S37-S42, GAP Q11-Q16, upload zip | DONE | tests 68/68, verify_claims PASS, QA gates 9/9, zip 152 files |
| T9 code review (10 findings) | DONE: 6 fixed (difflib autojunk incl. A11, D28; xlsx overwrite guard; NaN confidence; drift final_id/final_status; deprecated description duplicates; docstring), 4 not changed with reasons (rank-tie rule is sealed and secondary; speed; duplication) | this file |

Deviations from the plan text: drift helpers live in `src/ttpmap/drift.py` (testable) instead of the script; the download went to `E:/Osamas Paper/_downloads/attack_latest/` because `_evidence_pack/` is the read-only base; the review sheet is in `human_study/materials_local/`.

## Objective (c) explainer app and draft v2.2 audit (15 Nov 2026, 13:30 onward)

| task | state | evidence |
|---|---|---|
| A1 verify the claude.ai app on the real folder | DONE: 15/16, then 16/16 after the triage-threshold fix (D29) | `ttp_app/verify_artifacts_output.txt`, `results/app_verify.csv` |
| A2 app tests | DONE: 26 passed (6 new, written failing first) | `ttp_app/tests/test_core.py` |
| A3 replay by hand (6 sentence types) | DONE: names (60 -> 733 labels), deprecated-successor text, retired labels in the conformal set fixed | AppTest on the real folder + running server |
| A4 live mode timing (10 / 40 permutations, 3 lengths) | DONE | `ttp_app/live_timing.json`, `results/app_live_timing.csv` |
| A5 grounding report (100 rows, rule v1 unchanged) | DONE: 23 of 100 pass; 31 failures only quote the explained technique's own id/name (POST-HOC); rule v2 proposed, not applied | `results/app_grounding.csv`, `app_grounding_causes_posthoc.csv`; texts stay in `ttp_app/grounding_report.csv` |
| A7 code review (7 findings) | DONE: all 7 fixed with tests (interval parser: CI wording, more separators, half-up rounding, POINT OUTSIDE rows listed; AUDIT_TODO lists NO CLAIM rows; `TTPMAP_DEMO=0`; 0-of-0 pass rate) | `tests/test_check_intervals.py` (7), `ttp_app/tests/test_core.py` (26 app tests) |
| A6 AI-assistance disclosure | DONE | `ttp_app/README.md` section "AI assistance" |
| D1 number audit of `Thesis_Draft_v2.2.docx` + new interval check | DONE (D30): 13 of 18 intervals are still the 1,000-resample values; dataset statistics registered | `AUDIT_TODO.md`, `results/number_audit_v2_2/`, `scripts/check_intervals.py` |

Environment: `streamlit 1.67.0` and `pytest 9.2.0` added to `.venv` (dry run first: 13 packages added, none changed).
| P1 design-science framing, references (Hevner 2004, Peffers 2007, Bangor 2008 VERIFIED; Brooke 1996 PARTLY) | DONE (D31) | `docs/RELATED_WORK_VERIFIED.md` section G |
| P2 system chapter from the registry | DONE | `thesis_feed/ch4b_system_design.md`, `thesis_feed/figures_app/architecture.png` |
| P3 demo kit: launcher, guide, 5 screenshots, architecture figure | DONE (launcher tested: first run blocked by Streamlit's e-mail prompt, fixed with headless mode) | `ttp_app/run_app.bat`, `ttp_app/docs/` |
| P4 usability study kit (SUS), 3 tests | DONE; the study with 3-5 users is the author's task (`T9.usability_sus`) | `ttp_app/usability/` |
