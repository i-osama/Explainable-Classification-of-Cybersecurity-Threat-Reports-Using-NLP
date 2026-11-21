"""T0: inventory, environment, hashes."""
import csv, hashlib, os, platform, subprocess, sys, time
from pathlib import Path
from collections import Counter
from common import ROOT, PACK, w

SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "_evidence_pack", ".ipynb_checkpoints"}
DATA_EXT = {".csv", ".tsv", ".json", ".jsonl", ".npy", ".pt", ".pkl", ".xlsx", ".txt", ".png", ".safetensors", ".bin"}
BIG = 500 * 1024 * 1024


def walk():
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            yield Path(dp) / f


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


files = sorted(walk())
rows, skipped, ext_count = [], [], Counter()
for p in files:
    st = p.stat(); ext = p.suffix.lower(); ext_count[ext] += 1
    if ext in DATA_EXT:
        if st.st_size > BIG:
            skipped.append((str(p.relative_to(ROOT)), st.st_size)); digest = "SKIPPED>500MB"
        else:
            digest = sha(p)
        rows.append([str(p.relative_to(ROOT)), st.st_size,
                     time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime)), digest])
with open(PACK / "00_hashes.csv", "w", newline="", encoding="utf-8") as fh:
    cw = csv.writer(fh); cw.writerow(["path", "bytes", "mtime", "sha256"]); cw.writerows(rows)

# tree depth 3
tree = []
def rec(d, depth):
    if depth > 3: return
    for c in sorted(d.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
        if c.name in SKIP_DIRS: continue
        if c.is_dir():
            n = sum(1 for _ in c.rglob("*") if _.is_file())
            tree.append("  " * (depth - 1) + f"{c.name}/  ({n} files)"); rec(c, depth + 1)
        elif depth <= 2 or c.suffix.lower() not in {".npy"}:
            tree.append("  " * (depth - 1) + f"{c.name}  [{c.stat().st_size:,} B]")
rec(ROOT, 1)

nbs = [p for p in files if p.suffix == ".ipynb"]
pdfs = [p for p in files if p.suffix.lower() == ".pdf"]
ckpt = [p for p in files if p.suffix.lower() in {".safetensors", ".bin", ".pt"}]
human = [p for p in files if "hand_check" in p.name or "rater_agreement" in p.name]
py = [p for p in files if p.suffix == ".py"]
git = (ROOT / ".git").exists()

md = ["# 00 Inventory", "", f"Root: `{ROOT}`  generated {time.strftime('%Y-%m-%d %H:%M')}", "",
      f"- total files (excl. .venv, _evidence_pack, checkpoints dirs): {len(files)}",
      f"- data/result files hashed: {len(rows)} (skipped >500MB: {len(skipped)})",
      f"- by extension: {dict(ext_count.most_common())}",
      f"- git repo: {'YES' if git else 'NO (.git absent) -> remote/commit/status NOT-FOUND'}", "",
      "## Notebooks", *[f"- `{p.relative_to(ROOT)}` ({p.stat().st_size:,} B)" for p in nbs], "",
      "## Scripts (.py outside pack)", *([f"- `{p.relative_to(ROOT)}`" for p in py] or ["- NONE (all code lives in notebooks)"]), "",
      "## Papers (PDF)", *([f"- `{p.relative_to(ROOT)}`" for p in pdfs] or ["- NOT-FOUND: no PDF anywhere under root"]), "",
      "## Human-rating files", *[f"- `{p.relative_to(ROOT)}` ({p.stat().st_size:,} B)" for p in human], "",
      "## Model checkpoints", *[f"- `{p.relative_to(ROOT)}` ({p.stat().st_size:,} B)" for p in ckpt], "",
      "## Files >500MB (not hashed)", *([f"- `{a}` {b:,} B" for a, b in skipped] or ["- none"]), "",
      "## Tree (depth 3)", "```", *tree, "```"]
w(PACK / "00_inventory.md", "\n".join(md))

def run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=120, shell=True).stdout.strip()
    except Exception as e:
        return f"ERR {e}"
env = [f"python: {sys.version}", f"executable: {sys.executable}", f"os: {platform.platform()}",
       f"cpu: {platform.processor()}  cores={os.cpu_count()}", "", "## nvidia-smi",
       run("nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv") or "nvidia-smi NOT-FOUND", "",
       "## git", "NOT A GIT REPO" if not git else run(f'git -C "{ROOT}" remote -v') , "",
       "## NOTE", "This is the LOCAL analysis env (CPU). Training ran on Google Colab; the Colab pip freeze was NOT saved -> NOT-FOUND.",
       "", "## installed packages (importlib.metadata; the venv has no pip module)",
       "\n".join(sorted({f"{d.metadata['Name']}=={d.version}" for d in __import__("importlib.metadata").metadata.distributions()}, key=str.lower))]
w(PACK / "00_env.txt", "\n".join(env))
print(f"files={len(files)} hashed={len(rows)} skipped_big={len(skipped)} notebooks={len(nbs)} pdfs={len(pdfs)} "
      f"checkpoints={len(ckpt)} human={len(human)} py={len(py)} git={git}")
print("ext:", dict(ext_count.most_common()))
