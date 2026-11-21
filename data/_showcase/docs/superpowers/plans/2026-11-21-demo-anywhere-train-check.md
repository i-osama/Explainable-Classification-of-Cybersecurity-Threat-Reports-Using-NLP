# Demo Anywhere + Train-and-Check + Plain-Language UI — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The explainer app starts on any Windows 10/11 laptop: a "doctor" checks the PC, downloads what is missing from the fastest server, repairs the folder and starts the app; a visitor can train it with their own examples and see proof that the training worked; every page is understandable without AI or tech knowledge.

**Architecture:** A stdlib-only doctor (`ttp_app/portable/doctor.py`) runs before the existing launcher. It scans, builds a fix plan, races public mirrors, installs hash-locked packages into the folder's own Python, then hands over to `launch.py`. A PowerShell bootstrap covers the one case the doctor cannot: no Python in the folder. In the app, a new Start page and plain-language result lines sit on top of the existing modes; Teach mode becomes "Train and check" with before/after proof on sentences not used for training and a no-damage check on the 604 thesis dev sentences.

**Tech Stack:** Python 3.13.18 (uv build), Streamlit, scikit-learn, torch CPU, Windows batch + PowerShell 5.1, pip/uv with `--require-hashes`.

**Spec:** the user's requests of 21 Nov 2026 (this chat), restated as R1-R6 below.

## Requirements (from the user, 21 Nov 2026)

- R0 (done today, verified): Compare mode, GPU vs CPU vs local LLM (`ttp_app/compare.py`, 60/60 tests, browser run).
- R1 Works on any laptop, anywhere: at start, check the PC for everything the app needs.
- R2 If something is missing: show what will be downloaded, download it from the fastest server for this network, fix the setup, start the app.
- R3 A user can add custom text, train the model, and check whether it works.
- R4 Proof on screen that the custom-trained model really works afterwards.
- R5 A clean UI that a non-AI, non-tech person understands: why this showcase exists, what the project means, how it works.
- R6 Everything verified by real runs on this PC (not only mocked tests).

## Decisions needed from the user (recommendation first)

- D1 Training method. **Recommended: SVM retrain + "example memory".** The SVM is 1 of 6 votes, so retraining it alone rarely changes the final answer (that would look like "training failed"). Example memory: when a new sentence is very close to a taught example (cosine of matcher embeddings >= t, t chosen on thesis train->dev so close matches were right >= 90% of the time), the taught technique wins. Alternative: SVM only (thesis-pure, weak visible effect).
- D2 Packages. **Recommended: two folders.** Full offline folder (~10 GB, USB, no internet needed) plus a "lite" folder (~1.7 GB, no Python inside) that downloads Python + libraries (~0.6 GB) on first start. Alternative: full folder only; downloads only repair broken parts.
- D3 Private thesis files (trained weights, score files, dataset) are never downloaded from the internet: they travel inside the folder. If they are damaged the doctor says "copy the folder again". (Hosting them online would publish thesis material; not planned.)

## Global Constraints

- No git commits or pushes in this project (user rule). Back up every edited file to `_backups/ttp_app_2026-11-21/` first.
- Numbers on screen come only from `thesis_numbers.json` or results files; build-time checks say "not a thesis number".
- Never overwrite run outputs, rater files or `E:\TTP_DEMO`; new builds go to new folders (`E:\TTP_DEMO_v3`, `E:\TTP_DEMO_LITE`).
- The doctor checks only what the app needs; it never reads personal files and sends no user data (download URLs carry no user information).
- Python packages go only into the folder's own runtime, never into a system Python.
- System installs (VC++ runtime, Ollama) run only after the user types `Y`; default is No.
- Every download is SHA-256 checked (package lock hashes, manifest hashes); a mirror serving a different file is skipped.
- Tested platform: Windows 10/11 64-bit. macOS/Linux are not supported and the doctor says so (cannot be tested here).
- Runtime: CPython 3.13.18; package versions frozen from the current `.venv`.
- UI copy: plain English, sentences of 20 words or fewer, each technical term explained once in the glossary.

## Review Focus

- Offline laptop with a broken package: doctor must say "needs internet for: <items>" within 10 s, not hang (probe timeout 4 s). Test in Task 2.
- Mirror reachable but serving a wrong or HTML file (captive portal, stale mirror): hash mismatch -> next mirror, clear message. Test in Task 2.
- Folder on read-only USB/DVD: repairs impossible -> "copy the folder to this laptop first", before any download. Test in Task 1.
- Folder path with spaces, non-ASCII letters or > 100 characters (OneDrive Desktop): bat quoting works; doctor warns on long path. Tests in Tasks 1 and 4.
- Training lines with unknown IDs, empty check list, or check sentences identical to training lines: clear message; identical lines are not counted as "new sentences". Test in Task 7.

---

## File Structure

| File | Responsibility |
|---|---|
| `ttp_app/portable/doctor.py` (new) | PC scan -> `Check` list; fix plan; console report; runs fixes; hands over to `launch.main()` |
| `ttp_app/portable/mirrors.py` (new) | Mirror lists, mirror race, verified download with fallback |
| `ttp_app/portable/repair.py` (new) | Fix actions: packages, runtime, base model, VC++ runtime, Ollama |
| `ttp_app/portable/bootstrap.ps1` (new) | No-Python case: fastest PyPI mirror -> uv wheel (hash-checked) -> `uv python install` -> doctor |
| `ttp_app/portable/START_DEMO.bat` (modify) | Run doctor; bootstrap when `runtime\python\python.exe` is missing |
| `ttp_app/portable/requirements.lock.txt` (generated) | Exact versions + SHA-256 of all runtime packages |
| `_showcase/scripts/make_lock.py` (new) | Writes the lock from the `.venv` (via `uv pip compile --generate-hashes`) |
| `_showcase/scripts/build_portable_demo.py` (modify) | `--lite` build; copies lock, doctor, bootstrap; manifest marks `public` (re-downloadable) vs `private` files |
| `ttp_app/home.py` (new) | Start page, glossary, plain-language result sentence |
| `ttp_app/teach.py` (new) | Example memory, before/after check report, dev no-damage check, verdict |
| `ttp_app/calibrate_memory.py` (new) | Build-time threshold t for the example memory -> `_build/memory_calib.json` |
| `ttp_app/examples_teach.json` (new) | Hand-written sample pack: training lines + separate check lines |
| `ttp_app/app.py` (modify) | Plain mode names, Start page default, advanced settings folded away, Train-and-check page |
| `ttp_app/portable/README_DEMO.md` (modify) | One-page plain guide: start, what the doctor does, troubleshooting |

---

### Task 1: Doctor scan (no network)

**Files:** Create `ttp_app/portable/doctor.py`; Test `ttp_app/tests/test_doctor.py`

**Interfaces:**
- Produces: `@dataclass Check(key: str, ok: bool, need: str, detail: str, fix: str | None)` with `need` in `{"required", "optional", "info"}`; `scan(bundle: Path, probes: Probes = REAL) -> list[Check]`; `Probes` = object with `windows() -> tuple[bool, str]`, `avx2() -> bool`, `ram_gb() -> tuple[float, float]` (total, free), `disk_free_gb(path) -> float`, `runtime_python(bundle) -> Path | None`, `missing_packages(py, lock) -> list[str]`, `bad_files(bundle) -> tuple[list[str], list[str]]` (public, private), `vcredist() -> bool`, `writable(bundle) -> bool`, `ollama() -> tuple[bool, bool]` (installed, has qwen2.5:7b).
- Keys used later: `os`, `cpu`, `ram`, `disk`, `python`, `packages`, `files_public`, `files_private`, `vcredist`, `writable`, `path`, `ollama`.

- [ ] Step 1: Tests `test_scan_all_ok_on_fake_probes` (every Check ok), `test_missing_package_is_required_fix` (`packages` ok False, fix `"packages"`), `test_private_file_damage_says_copy_again` (fix None, detail contains "copy the whole folder again"), `test_readonly_folder_blocks_repairs` (`writable` False and detail contains "copy the folder to this laptop first"), `test_long_path_warns` (path of 120 chars -> `path` need `"info"`, ok False), `test_low_ram_required` (total 4.0 GB -> `ram` required fail; free 2.0 of 16 -> info only), `test_non_windows_unsupported` (`os` required fail, detail "Windows 10/11 64-bit only").
- [ ] Step 2: Run `..\.venv\Scripts\python.exe -m pytest -q tests\test_doctor.py` -> FAIL (module missing).
- [ ] Step 3: Implement with stdlib only (`ctypes` `IsProcessorFeaturePresent(40)` for AVX2, `GlobalMemoryStatusEx` for RAM, `shutil.disk_usage`, `importlib.metadata` run inside the folder's Python via one subprocess that prints JSON). RAM rule: total < 6 GB = required fail; free < 3 GB = info. Reuse `check.files` sizes logic and `launch.writable_dir`.
- [ ] Step 4: Run tests -> PASS. Real run: `E:\TTP_DEMO\runtime\python\python.exe ttp_app\portable\doctor.py --scan-only E:\TTP_DEMO` -> every required line `[ OK ]`.

### Task 2: Mirror race and verified download

**Files:** Create `ttp_app/portable/mirrors.py`; Test `ttp_app/tests/test_mirrors.py`

**Interfaces:**
- Produces: `PYPI = ("https://pypi.org/simple", "https://pypi.tuna.tsinghua.edu.cn/simple", "https://mirrors.aliyun.com/pypi/simple", "https://mirrors.cloud.tencent.com/pypi/simple", "https://mirror.kakao.com/pypi/simple")`, `HF = ("https://huggingface.co", "https://hf-mirror.com")`; `race(bases: Sequence[str], path: str, timeout: float = 4.0, tries: int = 2) -> list[tuple[str, float | None]]` (fastest first, None = unreachable, all probes in parallel threads); `fetch(urls: Sequence[str], dest: Path, sha256: str | None, progress: Callable[[int, int], None] | None = None) -> Path` (tries URLs in order; deletes and skips a file whose hash differs; raises `DownloadError` listing every URL and reason).
- Race probe for PyPI = GET `<base>/pip/` (the simple page: latency + bandwidth); for HF = HEAD of the bge `config.json`.

- [ ] Step 1: Tests against a local `http.server` thread with per-path delays (no internet): `test_race_orders_by_speed`, `test_race_unreachable_is_none_and_last`, `test_offline_all_none_within_10s`, `test_fetch_falls_back_on_hash_mismatch` (first server returns HTML, second the right bytes -> second used, first file deleted), `test_fetch_all_bad_raises_with_reasons`.
- [ ] Step 2: Run -> FAIL.
- [ ] Step 3: Implement (`urllib.request`, `concurrent.futures.ThreadPoolExecutor`, `.part` file then rename).
- [ ] Step 4: Run -> PASS. Real run: `python ttp_app\portable\mirrors.py --race` prints a 5-row table for this network (record it in the verification note).

### Task 3: Lock file and repair actions

**Files:** Create `_showcase/scripts/make_lock.py`, `ttp_app/portable/repair.py`, generated `ttp_app/portable/requirements.lock.txt`; Test `ttp_app/tests/test_repair.py`

**Interfaces:**
- Consumes: `Check` (Task 1), `race`, `fetch`, `PYPI`, `HF` (Task 2).
- Produces: `plan(checks: list[Check]) -> list[Fix]` with `@dataclass Fix(key: str, title: str, size_mb: int | None, source: str, needs_consent: bool, needs_internet: bool)`, ordered runtime -> packages -> files_public -> vcredist -> ollama; `apply(fix: Fix, bundle: Path, index: str, ask: Callable[[str], bool]) -> bool`; `pip_cmd(py: Path, lock_subset: Path, index: str) -> list[str]` (contains `--require-hashes`, `--no-deps`, `--index-url <index>`, `--only-binary :all:`); `uv_cmd(...)` same flags for uv; `lock_subset(lock: Path, names: list[str], out: Path) -> Path`.
- Sources: VC++ = `https://aka.ms/vs/17/release/vc_redist.x64.exe` run with `/install /passive /norestart`; Ollama = `https://ollama.com/download/OllamaSetup.exe` then `ollama pull qwen2.5:7b` (4.7 GB); base model files from fastest `HF` with manifest hashes.

- [ ] Step 1: `make_lock.py` freezes `.venv` (importlib.metadata), writes `name==version` (torch pinned `2.15.0`, PyPI build), runs `uv pip compile --generate-hashes --python-version 3.13 --python-platform x86_64-pc-windows-msvc`; check: every frozen package appears with at least one `--hash=sha256:` and versions equal the `.venv`.
- [ ] Step 2: Tests: `test_plan_order_and_consent` (vcredist and ollama need consent, packages do not), `test_private_damage_has_no_fix`, `test_offline_plan_reports_needs_internet`, `test_pip_cmd_flags`, `test_lock_subset_keeps_hashes`, `test_ask_no_skips_system_install` (ask returns False -> installer never started).
- [ ] Step 3: Run -> FAIL; implement; run -> PASS.

### Task 4: Start flow (doctor -> fixes -> app) and no-Python bootstrap

**Files:** Modify `ttp_app/portable/START_DEMO.bat`, `ttp_app/portable/doctor.py` (add `main()`), Create `ttp_app/portable/bootstrap.ps1`; Test `ttp_app/tests/test_launcher.py` (extend)

**Interfaces:**
- Consumes: `scan`, `plan`, `apply`, `race`, `launch.main()`.
- Produces: `doctor.main(argv) -> int` with flags `--scan-only`, `--yes` (consent to system installs, for tests only). Console shows: table of checks, then "Will download: <title> (<size> MB) from <fastest mirror> (<ms> ms)", progress, rescan, then starts the app.
- `bootstrap.ps1 -Bundle <path>`: races `PYPI` with `Invoke-WebRequest` timings, downloads the `uv` wheel named in the lock (hash checked), extracts `uv.exe` to `runtime\uv\`, runs `uv python install 3.13.18 --install-dir runtime\python-dl`, moves it to `runtime\python`, then `runtime\python\python.exe launcher\doctor.py`.

- [ ] Step 1: Tests: `test_bat_runs_doctor_and_bootstraps_when_python_missing` (bat text: quoted `%~dp0`, `bootstrap.ps1` branch), `test_main_fixes_then_starts` (fake probes: packages missing -> apply called once -> rescan ok -> launch called), `test_main_stops_on_private_damage` (launch not called, exit 1), `test_scan_only_never_downloads`.
- [ ] Step 2: Run -> FAIL; implement; run -> PASS.

### Task 5: Build both folders

**Files:** Modify `_showcase/scripts/build_portable_demo.py`; Test `ttp_app/tests/test_launcher.py` (build helpers)

**Interfaces:**
- Produces: `--lite` flag (no `runtime/`; data = only what `core.load_replay` + live mode read: `Dataset/`, `Exp_1_4_run_tram_2_epoc_30/*_pw_s4[234]/*.npy` + `*_pw_s42` model dirs, `run_match_1/`, `Exp_3_0_shap/`, `_showcase/results/`, `_showcase/thesis_numbers.json`, `_evidence_pack/external/`, `models/`); manifest entries get `"origin": "public" | "private"` and, for public files, `"url"` path relative to the HF repo.
- [ ] Step 1: Test `test_lite_selection_is_what_the_app_reads` (selection list vs paths opened by `core.load_replay` on the fake root).
- [ ] Step 2: Run -> FAIL; implement; run -> PASS.
- [ ] Step 3: Build: `.venv\Scripts\python.exe _showcase\scripts\build_portable_demo.py --target E:\TTP_DEMO_v3` and `--lite --target E:\TTP_DEMO_LITE`; expected: secret scan clean, sizes about 10 GB and 1.7 GB.

### Task 6: Plain-language UI and Start page

**Files:** Create `ttp_app/home.py`; Modify `ttp_app/app.py`; Tests `ttp_app/tests/test_home.py`, update mode labels in `tests/test_app_live.py`, `tests/test_compare.py`

**Interfaces:**
- Produces: `MODES` (new order and names): `"Start here"`, `"Try a sentence"` (live full fusion), `"Check a whole report"`, `"Train and check"`, `"Browse test sentences"` (replay), `"Compare: GPU, CPU, local AI"`, `"Advanced: classifiers only"`; `home_ui(R) -> None`; `plain_line(R, top: str, tier: int) -> str` (e.g. "The tool thinks this sentence describes T1082 System Information Discovery: <first sentence of the ATT&CK description>. It is very sure."); `GLOSSARY: dict[str, str]` (technique, MITRE ATT&CK, threat report, P@1, confidence, SHAP word colours, fusion, GPU/CPU, LLM, training).
- Start page blocks: the problem (1 short paragraph), what the tool does (3 steps), how good (B13a and L1.closed.p1 from the registry, in words: "right first answer for 80 of 100 new sentences"), what you can do (one button per mode), glossary expander. Sidebar: conformal alpha, SHAP permutations, Ollama URL inside an "Advanced settings" expander.
- [ ] Step 1: Tests: `test_start_page_is_default_and_shows_registry_numbers`, `test_start_buttons_switch_mode`, `test_plain_line_tiers` (tier 0/1/2 -> "very sure" / "fairly sure" / "not sure: a person should check"), `test_every_mode_renders_without_error` (fake root, stub models).
- [ ] Step 2: Run -> FAIL; implement; run -> PASS (all old tests updated to new labels).

### Task 7: Train and check (with proof)

**Files:** Create `ttp_app/teach.py`, `ttp_app/calibrate_memory.py`, `ttp_app/examples_teach.json`; Modify `ttp_app/app.py` (`teach_ui` -> `train_ui`); Tests `ttp_app/tests/test_teach.py`

**Interfaces:**
- Consumes: `core.retrain_svm`, `core.calib_for`, `live.load(art, full=True)` (matcher `_emb`), `core.fuse`.
- Produces: `Memory(emb: np.ndarray, labels: list[list[str]], texts: list[str], t: float)`; `Memory.lookup(E: np.ndarray) -> list[tuple[list[str], float, int] | None]`; `predict(R, comps, art, memory, texts) -> list[dict]` (`top`, `source` in `{"model", "memory"}`, `sim`); `check_report(before: list[dict], after: list[dict], gold: list[list[str]]) -> dict` (`n`, `right_before`, `right_after`); `dev_p1(R, art, memory) -> float` (seed-42 full fusion on 604 dev sentences, stored dev scores + the given SVM + memory); `verdict(train_rep, check_rep, dev_before, dev_after) -> tuple[bool, str]` (worked = check `right_after > right_before` and dev drop <= 0.01).
- `calibrate_memory.py`: train sentences = memory, dev sentences = queries; smallest t in 0.50..0.99 (step 0.01) with precision >= 0.90 and >= 20 matches; writes `{"t", "precision", "matches", "dev_n"}`; label "not a thesis number".
- Sample pack: hand-written lines (not from the dataset) for one technique that the thesis system gets wrong on the check lines today; chosen by running the base system first (record the before result).
- [ ] Step 1: Tests: `test_memory_fires_only_above_t`, `test_check_lines_equal_to_training_lines_are_excluded` (message "identical to a training line"), `test_check_report_counts`, `test_verdict_rules` (no gain -> not worked, explains why; dev drop 0.02 -> warns "made the thesis sentences worse"), `test_train_flow_with_stubs` (AppTest: load sample -> Train -> Check -> success box text "Training worked").
- [ ] Step 2: Run -> FAIL; implement; run -> PASS.
- [ ] Step 3: Real data: `..\.venv\Scripts\python.exe calibrate_memory.py` (prints t, precision); sample pack on real models -> before k/m, after k/m, dev P@1 before/after; write them to `ttp_app/_build/train_check_verification.json`.

### Task 8: End-to-end verification on this PC (R6)

- [ ] `..\.venv\Scripts\python.exe -m pytest -q tests` -> all pass (60 old + new).
- [ ] `E:\TTP_DEMO_v3\CHECK_DEMO.bat` -> ALL CHECKS PASSED.
- [ ] Repair test: delete one small locked package (`blinker`) from `E:\TTP_DEMO_v3\runtime`; run START_DEMO -> doctor shows it, races mirrors, installs it hash-checked, app health `200`.
- [ ] Lite test: `E:\TTP_DEMO_LITE\START_DEMO.bat` -> bootstrap downloads uv + Python + all packages (~0.6 GB) from the fastest mirror, app health `200`; record mirror, minutes, MB.
- [ ] Browser walkthrough (Chrome) of the lite app: Start page, Try a sentence, Train and check with the sample pack (verdict box), Compare; save screenshots.
- [ ] Update `README_DEMO.md` (plain guide) and project memory notes; old `E:\TTP_DEMO` left untouched.
