"""Build _showcase/drive_upload/KDU/ : the exact folder layout the Colab notebooks expect under My Drive.
Drag the folder `KDU` from drive_upload/ into "My Drive" in the browser (drive.google.com). If My Drive already has KDU/Thesis
from the original runs, upload only what notebook 00 reports as missing. Local copy only; never committed or zipped.
Usage: python scripts/make_drive_bundle.py [--no-checkpoints]   (checkpoints = seed-42 classifiers, about 0.8 GB, needed by notebook 06)"""
import shutil, sys
from pathlib import Path
SHOW = Path(__file__).resolve().parents[1]; ROOT = SHOW.parent; DST = SHOW / "drive_upload" / "KDU" / "Thesis"
pats = ["Dataset/tram_dev.tsv", "Dataset/tram_test.tsv", "Dataset/ttp-desc-mappings.csv", "Dataset/combined_train.csv",
        "Exp_1_4_run_tram_2_epoc_30/*_pw_s4[234]/*.npy", "Exp_1_4_run_tram_2_epoc_30/*_pw_s4[234]/metrics.json",
        "run_match_1/zeroshot/*", "run_match_1/ft20_s4[234]/*", "run_match_1/final_results_table.csv", "Exp_3_0_shap/shap_v2_roberta_pw_s42.jsonl"]
if "--no-checkpoints" not in sys.argv:
    pats += [f"Exp_1_4_run_tram_2_epoc_30/{m}_pw_s42/{f}" for m in ("roberta", "secbert") for f in ("model.safetensors", "config.json", "tokenizer.json", "tokenizer_config.json")]
files = sorted({p for pat in pats for p in ROOT.glob(pat) if p.is_file()})
need = sum(p.stat().st_size for p in files); free = shutil.disk_usage(SHOW).free
if need * 1.1 > free: print(f"not enough disk space: need {need / 1e9:.2f} GB, free {free / 1e9:.2f} GB"); sys.exit(1)
for p in files:
    q = DST / p.relative_to(ROOT); q.parent.mkdir(parents=True, exist_ok=True)
    if not q.exists() or q.stat().st_size != p.stat().st_size: shutil.copy2(p, q)
nb = DST / "notebooks"; nb.mkdir(exist_ok=True)
for p in sorted((SHOW / "notebooks").glob("*.ipynb")) + [ROOT / "_evidence_pack" / "09_repro" / "colab_fusion_shap.ipynb"]:
    shutil.copy2(p, nb / p.name)
(DST / "README_UPLOAD.txt").write_text("Drag the folder KDU into 'My Drive' (drive.google.com). Result: My Drive/KDU/Thesis/... as the notebooks expect.\n"
                                       "Open notebooks from My Drive/KDU/Thesis/notebooks with Google Colaboratory. Start with 00_setup_and_verify.ipynb.\n", encoding="utf-8")
print(f"bundle: {DST.parent.parent} | {len(files)} data files + {len(list(nb.glob('*.ipynb')))} notebooks | {need / 1e9:.2f} GB")
