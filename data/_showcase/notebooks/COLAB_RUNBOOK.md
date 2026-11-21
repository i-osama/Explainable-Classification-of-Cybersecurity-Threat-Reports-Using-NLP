# Colab runbook (for a first-time Colab user)

Nothing in `notebooks/` has run on Colab yet. This page explains, click by click, how to run them and what to send back.
Runtimes are estimates unless a source is named. Kill-switch: Tue 18 Nov 2026, 18:00 Asia/Dhaka. Whatever has not finished by then becomes future work.

**Hardened variants (Prompt F, 16 Nov 2026):** `_showcase/COLAB_UPLOAD/` holds Drive-optional, fail-fast, resumable copies of 04, 06 and `colab_fusion_shap` (plus Kaggle copies of 04 and 06), the input zips and `COLAB_UPLOAD/RUN_COLAB.md` / `COLAB_UPLOAD/KAGGLE.md`. Same model code; prefer them over the originals. Rebuild with `python scripts/make_colab_hardened.py`.

## 0 VS Code or browser?

VS Code is set up: open `_showcase\thesis.code-workspace` (**File > Open Workspace from File...**). The extensions Colab, Jupyter and Python are installed.
To connect a notebook to Colab from VS Code: open the notebook, click **Select Kernel** (top right) > **Colab** > **New Colab Server** > sign in with your
Google account in the browser window that opens > choose **GPU, T4**. Only you can do the sign-in.

Limit: reports from November 2025 say the Colab extension for VS Code cannot mount Google Drive (`drive.mount`) and cannot read files on this PC.
I could not test whether this is still true today. Every notebook here reads its inputs from Drive and saves results and weights to Drive.
So the first cell checks for Drive. If Drive is missing, it stops with a message that tells you to use the browser instead.
**Recommended:** run the notebooks in the browser (sections 1 and 2). Use VS Code to read, edit and run locally (kernel `.venv`).

Getting the files into Drive: run `python scripts\make_drive_bundle.py` (this PC). It builds `_showcase\drive_upload\KDU\Thesis\` with the exact layout
below, about 0.9 GB including the two seed-42 checkpoints for notebook 06, plus all notebooks. Drag the folder `KDU` into **My Drive** at drive.google.com.
If My Drive already has `KDU/Thesis` from the original runs, upload only what notebook 00 reports as missing.

## 1 One-time setup (about 10 minutes)

1. Open https://drive.google.com with the Google account you used for the thesis.
2. Check that this folder exists: `My Drive > KDU > Thesis`. It must contain the folders below. Do not rename anything.

```
MyDrive/KDU/Thesis/
  Dataset/                      tram_dev.tsv, tram_test.tsv, ttp-desc-mappings.csv, combined_train.csv (tram_train.tsv if you have it)
  Exp_1_4_run_tram_2_epoc_30/   roberta_pw_s42 ... secbert_pw_s44   (probabilities, metrics.json, model.safetensors)
  run_match_1/                  zeroshot/, ft20_s42/, ft20_s43/, ft20_s44/   (score files)
  Exp_3_0_shap/                 shap_v2_roberta_pw_s42.jsonl
  showcase_runs/                created by the notebooks (new results)
  run_match_2_saved/            created by notebook 04 (retrained matcher WITH weights)
```

3. Upload the notebooks: in Drive, open `KDU > Thesis`, click **New > Folder**, name it `notebooks`. Open it, click **New > File upload**, select all `.ipynb` files from
   `E:\Osamas Paper\_showcase\notebooks\`.
4. Double-click a notebook in Drive. If Drive asks which app to use, choose **Google Colaboratory**. (If it is not offered: **Open with > Connect more apps**, search "Colaboratory", install.)

## 2 Every time you open a notebook

1. Menu **Runtime > Change runtime type**. Hardware accelerator: **T4 GPU**. Click **Save**.
2. Run the first code cell: click it, press **Shift + Enter**. Colab asks to connect to Google Drive: click **Connect to Google Drive** and allow access with the same account.
3. The first cell prints the GPU name and package versions. If it says `No GPU found`, repeat step 1. GPU notebooks stop on purpose without a GPU.
4. Run the remaining cells one by one with **Shift + Enter**, top to bottom. Do not use "Run all" after editing a cell.
5. A cell is finished when the spinning circle on its left stops. Long cells print one line per epoch or per sentence.

## 3 Run order

| step | notebook | runtime (T4) | result files to check afterwards |
|---|---|---|---|
| 0 | `00_setup_and_verify` | 1 min | `showcase_runs/00_setup_and_verify/env_colab.json`; the cell must print `missing: 0` |
| 1 | `04_train_matcher_save`, first training cell only (seed 42) | 20-30 min (estimate printed in the original matcher notebook) | `run_match_2_saved/ft20_s42/matcher_state.pt` and `metrics.json` with `"finished": true` |
| 2 | `06_explainability` | 30-60 min | `showcase_runs/06_explainability/fusion_shap_summary.json` |
| 3 | `05_fusion_and_ablation` | 1 min | `showcase_runs/05_fusion_and_ablation/fusion_replication.json` |
| 4 | `04` second training cell (seeds 43-46), then `03_train_classifiers` | matcher 20-30 min per seed; classifiers about 15-25 min per run | `run_match_2_saved/ft20_s4*/metrics.json`, `showcase_runs/03_train_classifiers/*/metrics.json` |
| 5 | `09_baseline_same_protocol` | 1 min | `baseline_protocol.json` |
| 6 | `08_extension_cross_dataset` | about 1.5-2 h per run, 6 runs | only if time remains before the kill-switch |
| - | `01`, `02`, `07`, `10` | minutes | optional re-checks; `10` is a protocol and does not call any model |

`_evidence_pack/09_repro/colab_fusion_shap.ipynb` does steps 1 and 2 in one notebook. Use either that file or notebooks 04 + 06, not both.

## 4 What to paste back to Claude Code

Download these folders from Drive (right-click > **Download**; Drive zips them) and unzip into `E:\Osamas Paper\_colab_returned\`, keeping the folder names:
- `showcase_runs/` (all of it; it is small)
- from `run_match_2_saved/ft20_s*/`: `metrics.json`, `test_scores.npy`, `dev_scores.npy`. Also download `matcher_state.pt` of seed 42 (about 440 MB): with it the full fusion can be re-scored on this PC, including the robustness perturbations (prereg 14). Leave `ckpt_last.pt` on Drive.

Then run (or type `INGEST COLAB OUTPUTS` in Claude Code, which runs it for you):

```
E:\Osamas Paper\.venv\Scripts\python.exe -X utf8 scripts\ingest_colab.py
```

It checks every output file against the SHA-256 in its manifest. If one is missing or different, or a manifest is a SMOKE dry run, it copies nothing and prints why. If all match, it copies them to `results\colab\` and rebuilds `thesis_numbers.json`. Also paste the printed output of the last cell of each notebook you ran (the evidence table).

## 5 When something goes wrong

| problem | what you see | fix |
|---|---|---|
| Disconnect / timeout | "Runtime disconnected", or the page reloads | Reconnect (top right), run the first cell again, then the training cell again. It prints `resumed after epoch N` and continues from the last finished epoch, because a checkpoint is written to Drive after every epoch. Finished seeds print `skip (result file exists)`. |
| Idle disconnect | runs stop after about 90 minutes without interaction (free tier) | keep the browser tab open and in front; click into the notebook now and then |
| Out of GPU memory | `CUDA out of memory` | **Runtime > Restart session**, run the first cell, then the training cell again. If it repeats, edit `batch_size=16` to `batch_size=8` in the call of `train_matcher_save` or `train_model` and note this change in your log. |
| GPU quota used up | "You cannot currently connect to a GPU due to usage limits" | wait several hours (the free-tier limit resets), or use a different Google account that also has access to the Drive folder (share `KDU/Thesis` with it), or buy Colab Pay As You Go compute units. Do not switch to CPU for training; it is far too slow (one matcher epoch took about two hours on the thesis PC). |
| Drive not found | `FileNotFoundError ... /content/drive/MyDrive/KDU/Thesis` | the folder name or account is different; check section 1 |
| Missing package | `ModuleNotFoundError` | run `!pip install -q <name>` in a new cell, then re-run the cell |
| Hugging Face download slow or rate-limited | warning about unauthenticated requests | ignore the warning; if a download fails, run the cell again |
| A cell is still running when the kill-switch arrives | - | stop it (**Runtime > Interrupt execution**). Results already written to Drive are kept; the rest becomes future work |

## 6 Dry run without a GPU

In the first code cell, change `SMOKE = os.environ.get("TTPMAP_SMOKE", "0") == "1"` to `SMOKE = True`. Each notebook then runs on 20 sentences and finishes within about
two minutes (measured locally on CPU, `results/smoke_logs/`). Smoke results are code checks, never results; they are written to a separate folder and are not used anywhere.
