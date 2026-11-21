# Portable Live-Demo Folder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `E:\TTP_DEMO`. It is a copy-anywhere Windows folder: double-clicking `START_DEMO.bat` opens the ATT&CK explainer with the full fusion (3,1,1,1), live and offline.

**Architecture:**
- A portable CPython 3.13.18 (the uv standalone build) with `site-packages` copied from the tested `.venv`.
- A Python launcher starts streamlit headless and opens a splash page that redirects when the server is healthy.
- The app gains a live full-fusion mode. It reuses the notebook-06 matcher code and the retrained matcher from Kaggle.
- The app's data sits under `data\` in the thesis-root layout the loader already expects.

**Tech Stack:** Python 3.13, streamlit 1.67, torch 2.15 CPU, transformers 5.23, shap 0.54.1, scikit-learn 1.9.1, pytest 9.2, Windows batch.

**Spec:** `_showcase/docs/superpowers/specs/2026-11-16-portable-demo-design.md`

## Global Constraints
- Never commit or push (project rule: no git identity). There are no commit steps. Back up a file before its first edit, as `<name>.bak_2026-11-16`.
- Never overwrite run outputs or rater files. New results go to new files.
- The build script refuses to run if `E:\TTP_DEMO` exists.
- Never copy: `.venv`, `.git`, `.claude`, `SHARE_PACK_*`, `_colab_returned`, `__pycache__`, `desktop.ini`, `key_PRIVATE.csv`, `access_token`, `kaggle.json`.
- Offline: `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1`. Bind the server to 127.0.0.1 only.
- Every number the app shows comes from `thesis_numbers.json`. Otherwise it is labelled "build-time check, seed 42, not a thesis number".
- Fusion order is `("matcher", "svm", "roberta", "secbert")`, with weights (3,1,1,1) (`core.ORDER`, `core.W4`).
- Matcher: CLS of the last hidden state, L2-normalised. Text max length 128, label max length 256. Score = text embedding · label embedding.

## Review Focus
1. **Folder copied to a path with spaces or non-ASCII characters** (`D:\My Demo\TTP_DEMO`). The bat files and the launcher quote every path. *Test: Task 6, run from a `subst` drive and from a path with spaces.*
2. **Port 8501 is busy** (an old demo is still running). The launcher picks the next free port. *Test: Task 4, `test_free_port_skips_busy`.*
3. **Teacher's PC has no Python and no internet, and has a different HF cache.** Only the bundled runtime and models are used. *Test: Task 6, run with `PATH` stripped and `HF_HOME` set to an empty dir.*
4. **Live full fusion on a long sentence takes minutes on a weak CPU.** The default n_perm stays 10, there is a spinner, and the examples are short. *Test: Task 3, the app test uses the demo stub; timing comes from the Task 5 parity script.*
5. **The matcher label-embedding cache is missing or stale** (another label count). It is rebuilt, not crashed on. *Test: Task 1, `test_label_cache_rebuilt_on_shape_mismatch`.*

---

### Task 1: Live full fusion in `live.py`

**Files:**
- Modify: `ttp_app/live.py`
- Test: `ttp_app/tests/test_live.py`

**Interfaces:**
- Produces:
  - `analyse(comps, text, n_perm=10, seed=42, weights=None) -> dict`. `weights=None` means equal weights. The dict keys are unchanged; it adds `"weights"`.
  - `class MatcherComp(art)`: `name="matcher"`, `.z(tx)`.
    - `art["matcher_state"]` is the path of `matcher_state.pt`.
    - `art["base_model"]` is the dir with the bge config and tokenizer.
    - `art["label_texts"]` is a list of 733 strings.
    - `art["label_cache"]` is the path of the `.npy` file.
  - `load(art, full=False) -> list`. `full=True` gives `[MatcherComp, SvmComp, HFComp roberta, HFComp secbert]`.
  - `FULL_W = (3, 1, 1, 1)`.

- [ ] **Step 1:** Add the tests:
  - `test_weighted_shap_is_additive`: Stubs `a,b,c` with weights `(3,1,1)`. Check that `o["additivity_error"] < 1e-6`, that `o["scores"]` equals `3*z_a+z_b+z_c` of the full text, and that `o["k"] == 0`.
  - `test_label_cache_rebuilt_on_shape_mismatch`: Use the helper `live._label_emb(cache_path, n_labels, compute)`. A stale `.npy` of shape (5,4) and `n_labels=3` makes `compute` run and overwrite the file. A good cache does not call `compute`.
- [ ] **Step 2:** Run `..\.venv\Scripts\python.exe -m pytest tests/test_live.py -q`. Expected: the 2 new tests fail.
- [ ] **Step 3:** Implement the code:
  - The `weights` parameter: S is the weighted sum of the components' z, and V is the weighted sum of the component SHAP columns.
  - `_label_emb`: `np.load`, with a shape check against `n_labels`, then `np.save`.
  - `MatcherComp`: `AutoConfig/AutoModel.from_pretrained(base_model)`, then `load_state_dict` of `torch.load(state)`. The state-dict keys carry the prefix `enc.`, which is stripped. CPU, `eval()`, `mask = tok.mask_token`.
  - `load(art, full)`.
  - Update the module docstring: the classifier-only mode stays, and full mode was added.
- [ ] **Step 4:** Run the same command. Expected: all `test_live.py` tests pass.

### Task 2: Loader additions in `core.py`

**Files:**
- Modify: `ttp_app/core.py` (`load_replay`, `Replay`)
- Modify: `ttp_app/tests/fake_root.py`, adding `run_match_2_saved/ft20_s42/{dev,test}_scores.npy` and `results/colab/fusion_shap/fusion_shap_full_s42.jsonl` (rows 0-4)
- Test: `ttp_app/tests/test_loader.py`

**Interfaces:**
- Consumes: none.
- Produces:
  - `Replay.cal_full: Calib | None`, fitted on DEV: z of (retrained-matcher dev scores, SVM, RoBERTa s42, SecBERT s42) with `W4`. It is `None` when the retrained matcher dir is missing.
  - `Replay.fshap: dict` maps a test row to `{"values": list, "label": str, "correct": bool}`.
  - `Replay.art` gains `matcher_state`, `base_model`, `label_texts` and `label_cache`.
  - The retrained matcher is looked up first in `root/run_match_2_saved/ft20_s42`, then in `root/_showcase/results/colab/matcher_ft20_s42`.
  - The seed-averaged replay `S` must keep reading `run_match_1` for all 3 seeds, so B13a stays unchanged. Only `cal_full` uses the retrained matcher.
  - The base model is looked up in `root/models/bge-base-en-v1.5`, then in `TTPMAP_BGE`, then in the HF cache snapshot.
  - `label_cache = root/models/label_emb_ft20_s42.npy`.

- [ ] **Step 1:** Add the tests in `test_loader.py`:
  - `test_full_calibration_and_fusion_shap_loaded`: `r.cal_full is not None`, `set(r.fshap) == {0,1,2,3,4}`, `len(r.art["label_texts"]) == 733`.
  - `test_replay_scores_unchanged_by_retrained_matcher`: `r.S` equals the value computed from the `run_match_1` files only. Use the existing loader test's way of building the root.
- [ ] **Step 2:** Run `pytest tests/test_loader.py -q`. Expected: the new tests fail.
- [ ] **Step 3:** Implement the code. Change `mdir` so that replay `S` uses `run_match_2_saved` only when all 3 seeds are there; otherwise it uses `run_match_1`. This fixes the existing bug where a seed-42-only `run_match_2_saved` would silently replace seed 42 in B13a.
- [ ] **Step 4:** Run `pytest -q` (whole app suite). Expected: all pass.
- [ ] **Step 5:** Run `verify_artifacts.py` with `TTPMAP_ROOT="E:\Osamas Paper"`. Expected: `16/16 match`.

### Task 3: App UI in `app.py`, theme and examples

**Files:**
- Modify: `ttp_app/app.py`
- Create: `ttp_app/.streamlit/config.toml` (dark theme, `gatherUsageStats=false`)
- Create: `ttp_app/examples.json`: 6 short CTI sentences, each with a source note. They are taken from `docs/DEMO_GUIDE.md` or written fresh, never from the test set.
- Modify: `ttp_app/demo_data.py`, so that the demo Replay has `cal_full` and `fshap` for row 0.
- Test: `ttp_app/tests/test_app.py`

**Interfaces:**
- Consumes: Task 1 `load(art, full)` and `analyse(..., weights)`; Task 2 `cal_full` and `fshap`.
- Produces:
  - Mode radio as `sidebar.radio[0]`, with the options `["Replay (725 test sentences)", "Live: full fusion (3,1,1,1)", "Live: classifiers only"]`.
  - The alpha radio stays `sidebar.radio[1]`.
  - The live full mode is disabled, with a reason shown, when `R.cal_full is None`.

- [ ] **Step 1:** Add the tests:
  - `test_replay_shows_fusion_shap_when_available`: In demo, row 0. A caption contains `"Full fusion SHAP"`.
  - `test_header_badge_reads_registry`: Some markdown contains `"B13a"` or the B13a display value.
- [ ] **Step 2:** Run `pytest tests/test_app.py -q`. Expected: the new tests fail.
- [ ] **Step 3:** Implement the code:
  - Header badge.
  - Replay: prefer `fshap` and caption `"Full fusion SHAP (3,1,1,1), seed 42, retrained matcher, 40 permutations (notebook 06)"`. Otherwise use RoBERTa SHAP with the old caption.
  - Live full mode, with `cal_full` and `get_live(root, full)`.
  - Example buttons fill the text area.
  - Update the limits panel lines: fusion SHAP is now shown for 100 replay sentences; live full fusion uses seed 42 only and the retrained matcher (not bit-identical to `run_match_1`).
- [ ] **Step 4:** Run `pytest -q`. Expected: everything passes, including the old tests.

### Task 4: Launcher (`launch.py`, `splash.html`, `check.py`, bat files, icon)

**Files:**
- Create in `ttp_app/portable/`:
  - `launch.py`, `check.py`, `splash.html`, `make_icon.py` (writes `icon.ico` with PIL if present, else skipped)
  - `START_DEMO.bat`, `CHECK_DEMO.bat`, `MAKE_DESKTOP_SHORTCUT.bat`, `README_DEMO.md`
- Test: `ttp_app/tests/test_launcher.py`

**Interfaces:**
- Produces:
  - `launch.free_port(start=8501, tries=20) -> int`
  - `launch.env_for(bundle: Path) -> dict`, which sets `TTPMAP_ROOT=bundle/data`, the offline variables, `PYTHONNOUSERSITE=1` and `STREAMLIT_BROWSER_GATHER_USAGE_STATS=false`.
  - `check.run(bundle: Path, deep: bool) -> int`, which returns the number of failures and prints `[ OK ]` / `[FAIL]` lines.
    - Quick checks: runtime, imports, the data files in `MANIFEST.sha256.json` exist with the right sizes, and the port.
    - Deep checks add: the SHA-256 of every manifest file, `verify_artifacts.py`, `pytest -q` on the app, and the parity script from Task 5.
- The bat files resolve everything from `%~dp0`. They call `"%~dp0runtime\python\python.exe" -I -X utf8 "%~dp0launcher\launch.py"`.
- The splash page reads `?port=`, polls `http://127.0.0.1:<port>/_stcore/health` every 500 ms, and then `location.replace`s to the app.

- [ ] **Step 1:** Add the tests:
  - `test_free_port_skips_busy`: Bind a socket on a port P, then `free_port(P) != P`.
  - `test_env_for_sets_offline_and_root`.
  - `test_check_quick_reports_missing_file`: A temporary bundle whose manifest lists a missing file gives `run(...) >= 1`.
- [ ] **Step 2:** Run `pytest tests/test_launcher.py -q`. Expected: fail.
- [ ] **Step 3:** Implement the code. The launcher does these steps in order:
  1. Prints a banner.
  2. Runs `check.run(quick)` and stops with a red message and a pause if anything fails.
  3. Starts `python -m streamlit run app/app.py --server.headless true --server.address 127.0.0.1 --server.port P --browser.gatherUsageStats false`, with logs going to `logs/streamlit_<ts>.log`.
  4. Opens `splash.html?port=P` with `webbrowser`.
  5. Waits on the process. Ctrl+C ends it cleanly.
- [ ] **Step 4:** Run `pytest tests/test_launcher.py -q`. Expected: pass.

### Task 5: Real-data parity check and build-time evaluation

**Files:**
- Create: `ttp_app/check_live_parity.py`

**Interfaces:**
- Consumes: Task 1 `load(art, True)` and Task 2 `load_replay`.
- Produces: a JSON file `<root>/models/live_parity.json` with these fields:
  - `matcher_max_abs_diff`, `roberta_max_abs_diff`, `secbert_max_abs_diff` (live against stored test arrays, on test rows 0-19)
  - `full_s42_test_p1` and `full_s42_test_p1_ci` (bootstrap of 2000 resamples with seed 20261114, computed from the stored score files)
  - `seconds_per_sentence_full_nperm10`
- It also writes the label-embedding cache.

- [ ] **Step 1:** Run it on real data with `TTPMAP_ROOT="E:\Osamas Paper"`. Expected:
  - The matcher diff is ≤ 2e-3, because the stored scores came from a GPU with AMP off at eval. If it is larger, investigate before going on.
  - The classifier diffs are ≤ 1e-4.
  - The file is written.
- [ ] **Step 2:** Show `full_s42_test_p1` in the app sidebar only, labelled "build-time check, seed 42, not a thesis number".

### Task 6: Build script, bundle and end-to-end checks

**Files:**
- Create: `_showcase/scripts/build_portable_demo.py`

**Interfaces:**
- Consumes: everything above.
- Produces `E:\TTP_DEMO`, with the layout from the spec, `launcher/MANIFEST.sha256.json` (the data, app and launcher files, with relative path, size and SHA-256), and a secret-scan result.

- [ ] **Step 1:** Implement the script:
  - Refuse if the target exists.
  - Copy the runtime from `%APPDATA%\uv\python\cpython-3.13.18-windows-x86_64-none`.
  - Copy `.venv\Lib\site-packages` into `runtime\python\Lib\site-packages` and remove `EXTERNALLY-MANAGED` from the copy.
  - Copy the app without tests caches, and the launcher files to the bundle root.
  - Copy the data files the loader reads.
  - Copy the bge snapshot (only config, tokenizer and vocab files, not `model.safetensors`, because the state dict carries the weights).
  - Copy `models/label_emb_ft20_s42.npy` and `live_parity.json`.
  - Copy `thesis_material` with the exclusions.
  - Write the manifest.
  - Run the secret scan, with the same patterns as `build_pack.py`.
- [ ] **Step 2:** Run the script. Expected: it prints the sizes, `SECRET SCAN: CLEAN` and `MANIFEST n files`.
- [ ] **Step 3:** Run `E:\TTP_DEMO\CHECK_DEMO.bat` with `PATH` stripped to `C:\Windows\System32` and `HF_HOME` set to an empty temporary dir. Expected: `ALL CHECKS PASSED`.
- [ ] **Step 4:** Path independence: run `subst T: "E:\TTP_DEMO"`, then run `T:\launcher` quick check and a headless launch. Poll `/_stcore/health`, expecting `ok`, then stop it and run `subst T: /d`.
- [ ] **Step 5:** Drive the real app in the browser through `T:` or `E:\TTP_DEMO`:
  - Replay sentence 1 shows the fusion SHAP caption.
  - Live full fusion on one example returns a top-5 and SHAP.
  - Take screenshots for `README_DEMO.md`.

### Task 7: Docs

**Files:**
- Modify: `ttp_app/README.md` and `ttp_app/docs/DEMO_GUIDE.md` (new mode, portable start)
- Modify: `E:\TTP_DEMO\README_DEMO.md` (comes from Task 4; add screenshots and the 10-minute teacher script)
- Note for the thesis, in the summary to the author (no draft edit): one sentence for the app chapter about the new live full-fusion mode, and the `DO_NOT_CLAIM` row that changes.

- [ ] **Step 1:** Write the docs.
- [ ] **Step 2:** Rerun the whole app `pytest -q`, `verify_artifacts.py` (16/16) and `E:\TTP_DEMO\CHECK_DEMO.bat`. Expected: everything PASS.
