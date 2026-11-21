"""T9: zip _showcase as E:\\Osamas Paper\\_showcase.zip. Excludes weights, rating sheets with dataset text, the private
study key, smoke-run artefacts, caches and logs. Prints size and exclusions."""
import zipfile
from pathlib import Path
SHOW = Path(__file__).resolve().parents[1]; zp = SHOW.parent / "_showcase.zip"
EXC_DIR = {"__pycache__", ".pytest_cache", "sheets", "smoke_runs", ".ipynb_checkpoints", "materials_local", "drive_upload"}; EXC_EXT = {".pt", ".bin", ".safetensors", ".ckpt", ".npy", ".npz", ".pyc", ".zip"}
excl, n = [], 0
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for p in sorted(SHOW.rglob("*")):
        if p.is_dir(): continue
        rel = p.relative_to(SHOW.parent)
        if EXC_DIR & set(p.parts) or p.suffix.lower() in EXC_EXT or p.name == "key_PRIVATE.csv" or ("returned" in p.parts and p.name != "raters_TEMPLATE.csv") or (p.name.startswith("_") and p.suffix in (".txt", ".log")):
            excl.append(str(rel).replace("\\", "/")); continue
        z.write(p, rel); n += 1
kinds = sorted({("human_study/sheets (dataset text)" if "sheets" in e else "human_study/key_PRIVATE.csv" if "key_PRIVATE" in e else "results/smoke_runs (smoke artefacts)" if "smoke_runs" in e
                 else "human_study/materials_local (training sentences)" if "materials_local" in e else "drive_upload (dataset files for Drive)" if "drive_upload" in e else "nested zip" if e.endswith(".zip") else "__pycache__" if "__pycache__" in e else "logs" if e.endswith((".txt", ".log")) else "weights / arrays") for e in excl})
print(f"ZIP: {zp} | {n} files | {zp.stat().st_size / 1e6:.1f} MB (limit 50) | excluded {len(excl)} files: {', '.join(kinds) or 'nothing'}")
