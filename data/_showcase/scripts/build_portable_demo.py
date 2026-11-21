"""Build the portable demo folder (default E:\\TTP_DEMO): own Python + libraries, the app, the thesis project as data, a manifest.

    python build_portable_demo.py [--target E:\\TTP_DEMO]

Never overwrites: stops when the target exists. Run ttp_app/check_live_parity.py first (it makes ttp_app/_build/).
"""
import argparse
import getpass
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(r"E:\Osamas Paper")
APP = ROOT / "ttp_app"
PORT = APP / "portable"
UV_PY = Path(os.environ["APPDATA"]) / "uv" / "python" / "cpython-3.13.18-windows-x86_64-none"
VENV_SP = ROOT / ".venv" / "Lib" / "site-packages"
BGE = Path.home() / ".cache" / "huggingface" / "hub" / "models--BAAI--bge-base-en-v1.5" / "snapshots"

# never in the folder: environments, git, secrets, share packs, upload duplicates, caches
SKIP_TOP = {".venv", ".git", ".claude", ".superpowers", ".pytest_cache", "_colab_returned", "_downloads", "graphify-out", "ttp_app"}
SKIP_ANY = {"__pycache__", ".pytest_cache", "desktop.ini", "key_private.csv", "access_token", "kaggle.json", ".ipynb_checkpoints"}
SKIP_SHOWCASE = {"drive_upload", "COLAB_UPLOAD"}
FORBIDDEN = {"key_private.csv", "access_token", "kaggle.json"}
# files the app, its checks and the launcher need: a problem here stops START_DEMO; other thesis material is only reported
CORE = ("app/", "launcher/", "data/Dataset/", "data/Exp_1_4_run_tram_2_epoc_30/", "data/run_match_1/", "data/Exp_3_0_shap/",
        "data/_showcase/results/", "data/_showcase/thesis_numbers.json", "data/_evidence_pack/external/", "data/models/")
PATS = [re.compile(rb"KGAT_[A-Za-z0-9]{8,}"), re.compile(rb'"key"\s*:\s*"[0-9a-f]{32}"'),
        re.compile(rb"(?<![A-Za-z0-9])AIza[0-9A-Za-z_-]{35}"), re.compile(rb"(?<![A-Za-z0-9])sk-ant-[A-Za-z0-9_-]{30,}"),
        re.compile(rb"(?<![A-Za-z0-9])sk-(?:proj-)?[A-Za-z0-9_-]{32,}"), re.compile(rb"(?<![A-Za-z0-9])gsk_[A-Za-z0-9]{30,}")]  # not inside words  # Kaggle, Google AI Studio, Anthropic, OpenAI, Groq keys
TEXT = {".md", ".json", ".jsonl", ".csv", ".tsv", ".txt", ".yaml", ".yml", ".html", ".py", ".ipynb", ".log", ".bat", ".ps1", ".toml"}
# lite folder: only what the app, its checks and live mode read (data paths relative to the thesis root)
LITE = ("Dataset/*", "Exp_1_4_run_tram_2_epoc_30/*_pw_s4[234]/*.npy", "Exp_1_4_run_tram_2_epoc_30/*_pw_s4[234]/*.json",
        "Exp_1_4_run_tram_2_epoc_30/*_pw_s42/*", "run_match_1/*", "run_match_2_saved/*", "Exp_3_0_shap/*", "_showcase/results/*",
        "_showcase/thesis_numbers.json", "_evidence_pack/external/*", "models/*",
        "results/*", "thesis_numbers.json")  # the app also accepts results/ and thesis_numbers.json at the root
LITE_TOP = {p.split("/")[0] for p in LITE}
LAUNCHER = ("launch.py", "check.py", "doctor.py", "mirrors.py", "repair.py", "bootstrap.ps1", "requirements.lock.txt",
            "requirements.sizes.json", "bootstrap.json", "splash.html", "icon.ico")
TOP = ("START_DEMO.bat", "CHECK_DEMO.bat", "SETUP_LOCAL_AI.bat", "MAKE_DESKTOP_SHORTCUT.bat", "README_DEMO.md")
HF_REPO = "BAAI/bge-base-en-v1.5"


GENERIC_NAMES = {"user", "users", "admin", "administrator", "owner", "public", "default", "guest", "workgroup"}


def identity_patterns(git=True) -> list:
    """Strings that identify the build PC or its user (user name, computer name, git name and e-mail), read from this PC
    at build time and only used to keep files out of the folder; they are never written anywhere."""
    vals = {getpass.getuser(), os.environ.get("COMPUTERNAME", ""), os.environ.get("USERDOMAIN", "")}
    if git:
        for k in ("user.name", "user.email"):
            try:
                vals.add(subprocess.run(["git", "config", "--global", k], capture_output=True, text=True, timeout=10).stdout.strip())
            except (OSError, subprocess.SubprocessError):
                pass
    return sorted({v.strip().lower().encode() for v in vals if len(v.strip()) >= 4 and v.strip().lower() not in GENERIC_NAMES})


def identity_hits(rel, p, pats, max_bytes=300_000_000) -> bool:
    """The file name, the file bytes, or (zip-based files: docx, xlsx, pptx, whl, zip) any member holds an identity string."""
    if any(x in str(rel).lower().encode() for x in pats):
        return True
    p = Path(p)
    if p.stat().st_size > max_bytes:
        return False
    data = p.read_bytes()
    if any(x in data.lower() for x in pats):
        return True
    if data[:2] == b"PK":
        try:
            with zipfile.ZipFile(p) as z:
                return any(any(x in z.read(n).lower() for x in pats) for n in z.namelist() if z.getinfo(n).file_size < max_bytes)
        except (zipfile.BadZipFile, OSError, RuntimeError):
            return False
    return False


def lite_selected(rel: str) -> bool:
    import fnmatch
    return any(fnmatch.fnmatch(rel, p) for p in LITE)


def ignore_data(d, names):
    d = Path(d)
    out = {n for n in names if n.lower() in SKIP_ANY or n.startswith("SHARE_PACK_")}
    if d == ROOT:
        out |= {n for n in names if n in SKIP_TOP or n.lower().endswith(".zip")}  # root zips are upload copies
    if d == ROOT / "_showcase":
        out |= {n for n in names if n in SKIP_SHOWCASE}
    return out


def ignore_app(d, names):
    return {n for n in names if n.lower() in SKIP_ANY or n in {"_build", ".streamlit_cache"} or ".bak_" in n or n.endswith(".log")}


def scan_file(p, tok):
    """[(name, why)] for a forbidden file name or a token pattern, in the file itself or in the members of a zip."""
    p, hits = Path(p), []

    def one(name, data):
        if Path(name).name.lower() in FORBIDDEN:
            hits.append((name, "forbidden file"))
        elif data is not None and ((tok and tok in data) or any(x.search(data) for x in PATS)):
            hits.append((name, "token pattern"))

    if p.suffix.lower() == ".zip":
        with zipfile.ZipFile(p) as z:
            for n in z.namelist():
                one(f"{p}::{n}", z.read(n) if Path(n).suffix.lower() in TEXT else None)
    else:
        one(str(p), p.read_bytes() if p.suffix.lower() in TEXT and p.stat().st_size < 50_000_000 else None)
    return hits


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def step(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default=r"E:\TTP_DEMO")
    ap.add_argument("--lite", action="store_true", help="no Python inside (first start downloads it) and only the data the app reads")
    a = ap.parse_args()
    T, lite = Path(a.target), a.lite
    if T.exists():
        sys.exit(f"STOP: {T} exists (never overwrite). Rename or remove it first.")
    build = APP / "_build"
    for f in ("label_emb_ft20_s42.npy", "live_parity.json", "memory_calib.json"):
        if not (build / f).exists():
            sys.exit(f"STOP: {build / f} missing: run ttp_app/check_live_parity.py and ttp_app/calibrate_memory.py first")
    if json.loads((build / "live_parity.json").read_text(encoding="utf-8"))["status"] != "PASS":
        sys.exit("STOP: live parity check did not pass")

    if lite:
        step("runtime: none (START_DEMO downloads Python and the libraries on first start)")
    else:
        step("runtime: portable CPython 3.13.18 + the tested .venv libraries + uv (for repairs)")
        no_cache = lambda d, n: {x for x in n if x.lower() in ("desktop.ini", "__pycache__")}  # .pyc files hold this PC's paths
        shutil.copytree(UV_PY.resolve(), T / "runtime" / "python", ignore=no_cache)
        shutil.copytree(VENV_SP, T / "runtime" / "python" / "Lib" / "site-packages", dirs_exist_ok=True, ignore=no_cache)
        for m in (T / "runtime" / "python" / "Lib").glob("EXTERNALLY-MANAGED"):
            m.unlink()  # this copy is private to the folder
        (T / "runtime" / "uv").mkdir()
        shutil.copy2(shutil.which("uv"), T / "runtime" / "uv" / "uv.exe")

    step("app + launcher")
    shutil.copytree(APP, T / "app", ignore=ignore_app)
    (T / "launcher").mkdir()
    for f in LAUNCHER:
        shutil.copy2(PORT / f, T / "launcher" / f)
    for f in TOP:
        shutil.copy2(PORT / f, T / f)

    if lite:
        step("data: only the files the app reads (lite)")
        for top in sorted(LITE_TOP - {"models"}):
            for p in sorted((ROOT / top).rglob("*")) if (ROOT / top).is_dir() else [ROOT / top] if (ROOT / top).is_file() else []:
                rel = p.relative_to(ROOT).as_posix()
                if p.is_file() and lite_selected(rel) and not (set(p.relative_to(ROOT).parts) & SKIP_ANY | {p.name.lower()} & SKIP_ANY):
                    (T / "data" / rel).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(p, T / "data" / rel)
    else:
        step("data: the thesis project (filtered)")
        shutil.copytree(ROOT, T / "data", ignore=ignore_data)
    M = T / "data" / "models"
    M.mkdir()
    snap = next(d for d in sorted(BGE.glob("*")) if (d / "config.json").exists())
    shutil.copytree(snap, M / "bge-base-en-v1.5", ignore=lambda d, n: {x for x in n if x in {"model.safetensors", "desktop.ini"}})
    for f in ("label_emb_ft20_s42.npy", "live_parity.json", "memory_calib.json"):
        shutil.copy2(build / f, M / f)

    step("privacy: nothing may name this PC or its user (file names, contents, Office metadata)")
    pats = identity_patterns()
    dropped, blocking = [], []
    for p in sorted(T.rglob("*")):
        if p.is_file() and identity_hits(p.relative_to(T).as_posix(), p, pats):
            rel = p.relative_to(T).as_posix()
            if rel.startswith("data/"):
                p.unlink()
                dropped.append(rel)
            else:
                blocking.append(rel)
    print(f"  {len(dropped)} thesis-material file(s) left out because they name this PC or its user")
    if blocking:
        sys.exit("STOP: app, launcher or runtime files name this PC or its user:\n  " + "\n  ".join(blocking[:20]))

    step("manifest (SHA-256 of app, launcher and data files)")
    items = []
    for part in ("app", "launcher", "data"):
        for p in sorted((T / part).rglob("*")):
            if p.is_file() and p.name != "MANIFEST.sha256.json" and p.name.lower() != "desktop.ini":  # Windows adds these to new folders
                rel = p.relative_to(T).as_posix()
                it = {"path": rel, "size": p.stat().st_size, "sha256": sha256(p), "core": rel.startswith(CORE)}
                bge = "data/models/bge-base-en-v1.5/"
                if rel.startswith(bge):  # public Hugging Face files: the doctor can download them again at this exact revision
                    it.update(origin="public", url=f"{HF_REPO}/resolve/{snap.name}/{rel[len(bge):]}")
                items.append(it)
    (T / "launcher" / "MANIFEST.sha256.json").write_text(json.dumps({"built": time.strftime("%Y-%m-%d %H:%M"), "files": items}), encoding="utf-8")

    step("secret scan")
    tok_file = Path.home() / ".kaggle" / "access_token"
    tok = tok_file.read_text(encoding="utf-8").strip().encode() if tok_file.exists() else None
    hard, longest = [], 0
    for p in T.rglob("*"):
        if not p.is_file():
            continue
        longest = max(longest, len(p.relative_to(T).as_posix()))
        if p.relative_to(T).parts[0] != "runtime" or p.name.lower() in FORBIDDEN:
            hard += scan_file(p, tok)
    size = sum(p.stat().st_size for p in T.rglob("*") if p.is_file())
    print(f"\nTARGET {T}  size {size / 1e9:.2f} GB  manifest {len(items)} files ({sum(i['core'] for i in items)} core)  longest relative path {longest} chars")
    print("SECRET SCAN:", "CLEAN" if not hard else f"{len(hard)} HITS")
    for h in hard[:20]:
        print("  ", h)
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main())
