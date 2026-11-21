# Portable live-demo folder for the ATT&CK explainer (design, 16 Nov 2026)

## Intent
The author must be able to show a real, live demonstration when the teacher asks.
One folder is copied to any Windows PC. A double-click starts the web app with the best system. Nothing is installed and no internet is needed.

## Goals
- One folder, `E:\TTP_DEMO`, copied as is (USB or disk). Double-click `START_DEMO.bat`. The browser opens and the app is ready.
- The app uses the best system:
  - Replay: the seed-averaged fusion B13a.
  - Live: the full fusion (3,1,1,1) with the matcher retrained on Kaggle (seed 42).
- Explanations explain the fused answer where the evidence exists:
  - Replay: the notebook-06 fusion SHAP for its 100 sentences; RoBERTa SHAP elsewhere, labelled.
  - Live: SHAP of the fused score.
- A polished start: a coloured console self-check, a browser splash page that waits for the server, a dark theme, one-click example sentences, and a desktop shortcut.
- One self-check button (`CHECK_DEMO.bat`) that ends in a clear PASS or FAIL.
- The thesis material comes along: notebooks, run folders, Dataset, and `_showcase` (report, draft, figures, results).

## Non-goals
- No online deployment, no Mac or Linux, and no GPU requirement (CPU torch).
- No change to thesis numbers or the registry.

## Anti-goals (failure even if it works)
- It needs the internet, admin rights, or an installer on the teacher's PC.
- The app shows a number that is not in `thesis_numbers.json`, or that is not clearly labelled as a build-time check.
- Secrets end up in the folder: the Kaggle token, `key_PRIVATE.csv` or `.git`.
- Run outputs or rater files in the project are overwritten.

## Approaches considered
1. **Python inside the folder (chosen).** A copy of the uv CPython 3.13.18 standalone build. Its `site-packages` is copied from the tested `.venv`, which gives exactly the versions behind 80/80 and 29/29. The app is always started as `python -m streamlit`, never through `Scripts\*.exe`, because those embed absolute paths.
2. **Build on first start** (uv + offline wheels). Rejected: the first start is slow and more can break in front of the teacher.
3. **Single exe** (PyInstaller). Rejected: torch and streamlit do not freeze reliably.

## Design
- **Layout of `E:\TTP_DEMO`** (short root, because torch paths are long and Windows has a 260-character limit):
  - `START_DEMO.bat`, `CHECK_DEMO.bat`, `MAKE_DESKTOP_SHORTCUT.bat`, `README_DEMO.md`
  - `runtime\python\`: portable Python with the libraries.
  - `app\`: the upgraded `ttp_app`, including `.streamlit\config.toml`.
  - `launcher\`: `launch.py`, `splash.html`, `check.py`, `icon.ico`, `MANIFEST.sha256.json`.
  - `data\`: the minimal thesis-root layout the app expects (`TTPMAP_ROOT`):
    - `Dataset`, `Exp_1_4_run_tram_2_epoc_30`, `run_match_1`, `Exp_3_0_shap`, `_evidence_pack\external`
    - `_showcase\results` (including `colab`), `_showcase\thesis_numbers.json`
    - `run_match_2_saved\ft20_s42` (retrained matcher)
    - `models\bge-base-en-v1.5` (config and tokenizer)
  - `thesis_material\`: a filtered copy of the project. Excluded: `.venv`, `.git`, `.claude`, `SHARE_PACK_*`, `_colab_returned`, `__pycache__`, `desktop.ini`, `key_PRIVATE.csv`, any token or `kaggle.json`.
- **Launcher** (`launch.py`, run by the portable Python):
  1. Sets offline variables (`HF_HUB_OFFLINE`, `TRANSFORMERS_OFFLINE`) and `TTPMAP_ROOT=data`.
  2. Runs fast checks: files present, libraries import, and a free port on 127.0.0.1.
  3. Starts streamlit headless.
  4. Opens `splash.html?port=N`. The splash polls `/_stcore/health` and redirects when the server is ready.
  5. Writes logs to `logs\`.
- **App changes**, made in `ttp_app` source and then copied:
  - `live.py`: `MatcherComp` with the same code as notebook 06 (CLS-pooled, L2-normalised bge-base; text max length 128, label max length 256; scores = embeddings · label embeddings).
    - Label embeddings are cached to `.npy` on the first load.
    - `load(art, full)`: full uses weights (3,1,1,1) with the order (matcher, svm, roberta, secbert).
    - The fused SHAP is the weighted sum of the component Shapley values. This holds because Shapley values are linear.
  - `core.load_replay`:
    - Adds `cal_full`, fitted on DEV only: retrained matcher dev scores + seed-42 classifiers + SVM.
    - Adds `art["matcher_dir"]`, `art["base_model"]` and `fshap` (from `fusion_shap_full_s42.jsonl`).
  - `app.py`:
    - Mode list: Replay | Live full fusion (default for live) | Live classifiers only.
    - Replay shows the fusion SHAP when it is available.
    - One-click example sentences.
    - A header badge with the B13a value from the registry.
    - The limits panel is updated.
  - Tests:
    - Fake-root tests for the new mode.
    - Parity script: live matcher and classifier scores on test sentences against the stored `test_scores.npy` and `test_probs.npy`, within tolerance.
- **Build script** (`_showcase/scripts/build_portable_demo.py`):
  - Copies the files and writes `MANIFEST.sha256.json`.
  - Refuses to overwrite an existing `E:\TTP_DEMO`.
  - Ends with a secret scan.

## Left to the builder
- Theme colours, the splash look, and the wording of the example sentences. The examples come from the thesis `DEMO_GUIDE`.
- Whether the live full-fusion test P@1 is shown. It may be shown only if it is labelled "build-time check, seed 42, not a thesis number".
