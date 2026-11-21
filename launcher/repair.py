"""Repair actions for the doctor: what to download, from where, and how to install it.

Libraries go only into the folder's own Python, hash-checked (pip/uv --require-hashes). Windows-wide installs
(Microsoft C++ runtime, Ollama) run only after the user says yes.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import doctor
import mirrors

ORDER = ("runtime", "packages", "files_public", "vcredist", "ollama", "ollama_model")
PY_VERSION = "3.13.18"
VC_URL = "https://aka.ms/vs/17/release/vc_redist.x64.exe"
OLLAMA_URL = "https://ollama.com/download/OllamaSetup.exe"
INFO = {  # key -> (title, size MB or None, source, needs consent)
    "runtime": ("Python 3.13 for this folder", 30, "python-build-standalone (GitHub), via uv", False),
    "packages": ("Python libraries (streamlit, torch, transformers, ...)", None, "fastest Python package server", False),
    "files_public": ("Public model files (bge-base tokenizer and config)", 1, "fastest Hugging Face server", False),
    "vcredist": ("Microsoft Visual C++ runtime (Windows-wide install)", 25, "Microsoft (aka.ms)", True),
    "ollama": ("Ollama + qwen2.5:7b, only for the local-AI comparison", 5500, "ollama.com", True),
    "ollama_model": ("qwen2.5:7b model for Ollama", 4700, "ollama.com", True),
}


@dataclass
class Fix:
    key: str
    title: str
    size_mb: Optional[int]
    source: str
    needs_consent: bool
    needs_internet: bool = True


def plan(checks) -> list:
    keys = {c.fix for c in checks if not c.ok and c.fix}
    return [Fix(k, *INFO[k]) for k in ORDER if k in keys]


def needs_internet_text(fixes) -> str:
    return "needs internet for: " + "; ".join(f.title for f in fixes if f.needs_internet)


def lock_subset(lock: Path, names, out: Path) -> Path:
    """The lock entries (pin line + its hash lines) of `names` only."""
    want = {doctor.norm(n) for n in names}
    keep, on = [], False
    for line in Path(lock).read_text(encoding="utf-8").splitlines():
        m = doctor._PIN.match(line)
        if m:
            on = doctor.norm(m.group(1)) in want
        elif not line.startswith((" ", "\t")):
            on = False
        if on and not line.strip().startswith("#"):
            keep.append(line)
    text = "\n".join(keep).rstrip(" \\")
    Path(out).write_text(text + "\n", encoding="utf-8")
    return Path(out)


def pip_cmd(py: Path, sub: Path, index: str) -> list:
    return [str(py), "-m", "pip", "install", "--require-hashes", "--no-deps", "--only-binary", ":all:", "--no-input",
            "--disable-pip-version-check", "--index-url", index, "-r", str(sub)]


def uv_cmd(uv: Path, py: Path, sub: Path, index: str) -> list:
    return [str(uv), "pip", "install", "--python", str(py), "--require-hashes", "--no-deps", "--only-binary", ":all:",
            "--index-url", index, "-r", str(sub)]


def find_uv(bundle: Path) -> Optional[Path]:
    for p in (Path(bundle) / "runtime" / "uv" / "uv.exe", Path(bundle) / "launcher" / "uv.exe"):
        if p.is_file():
            return p
    w = shutil.which("uv")
    return Path(w) if w else None


def _run(cmd, **kw) -> int:
    print("    $ " + " ".join(str(c) for c in cmd[:6]) + (" ..." if len(cmd) > 6 else ""), flush=True)
    return subprocess.run(cmd, **kw).returncode


def install_packages(bundle: Path, py: Path, names, index: str) -> bool:
    lock = Path(bundle) / "launcher" / doctor.LOCK
    with tempfile.TemporaryDirectory() as t:
        sub = lock_subset(lock, names, Path(t) / "subset.txt")
        uv = find_uv(bundle)
        env = {**os.environ, "PIP_NO_CACHE_DIR": "1", "UV_NO_CACHE": "1"}  # nothing left behind in the user's profile
        return _run(uv_cmd(uv, py, sub, index) if uv else pip_cmd(py, sub, index), env=env) == 0


def install_runtime(bundle: Path) -> bool:
    """uv downloads CPython into runtime/_py; its interpreter folder becomes runtime/python."""
    uv = find_uv(bundle)
    if uv is None:
        print("    uv not found: run START_DEMO.bat (it fetches uv first).")
        return False
    tmp = Path(bundle) / "runtime" / "_py"
    if _run([str(uv), "python", "install", PY_VERSION, "--install-dir", str(tmp), "--no-bin"]) != 0:
        return False
    # uv adds a cpython-3.13-... junction next to the real cpython-3.13.18-... folder: move the real one, then drop the link
    found = next((p.parent for p in sorted(tmp.glob("cpython-*/python.exe")) if not (p.parent.is_junction() or p.parent.is_symlink())), None)
    if found is None:
        return False
    shutil.move(str(found), str(Path(bundle) / "runtime" / "python"))
    for link in tmp.glob("cpython-*"):
        if link.is_junction() or link.is_symlink():
            os.rmdir(link) if link.is_junction() else link.unlink()  # removes the link only, never its target
    shutil.rmtree(tmp, ignore_errors=True)
    (Path(bundle) / "runtime" / "python" / "Lib" / "EXTERNALLY-MANAGED").unlink(missing_ok=True)  # the folder's own Python
    return True


def fetch_public_files(bundle: Path, hf_bases) -> bool:
    items = json.loads((Path(bundle) / "launcher" / "MANIFEST.sha256.json").read_text(encoding="utf-8"))["files"]
    ok = True
    for it in items:
        p = Path(bundle) / it["path"]
        if it.get("origin") != "public" or (p.is_file() and p.stat().st_size == it["size"]):
            continue
        try:
            mirrors.fetch([b.rstrip("/") + "/" + it["url"] for b in hf_bases], p, it["sha256"])
            print(f"    downloaded {it['path']}")
        except mirrors.DownloadError as e:
            print(f"    {e}")
            ok = False
    return ok


def _installer(url: str, args, ok_codes=(0,)) -> bool:
    with tempfile.TemporaryDirectory() as t:
        exe = Path(t) / Path(url).name
        if not exe.suffix:
            exe = exe.with_suffix(".exe")
        mirrors.fetch([url], exe, None, progress=_bar)
        print()
        return _run([str(exe), *args]) in ok_codes


def _bar(done, total):
    if total:
        print(f"\r    {done / 2 ** 20:7.1f} of {total / 2 ** 20:.1f} MB", end="", flush=True)


def ollama_pull() -> bool:
    exe = shutil.which("ollama") or str(Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Ollama" / "ollama.exe")
    return _run([exe, "pull", doctor.LLM]) == 0


def apply(fix: Fix, bundle: Path, index: str, ask: Callable[[str], bool], hf_bases=mirrors.HF) -> bool:
    """Run one fix. Returns True when it finished without error (the doctor rescans afterwards)."""
    if fix.needs_consent and not ask(f"Install {fix.title}? About {fix.size_mb} MB from {fix.source}. [y/N] "):
        print("    skipped.")
        return False
    if fix.key == "runtime":
        return install_runtime(bundle)
    if fix.key == "packages":
        py = doctor.REAL.runtime_python(bundle)
        missing = doctor.REAL.missing_packages(py, Path(bundle) / "launcher" / doctor.LOCK) if py else []
        return bool(py) and (not missing or install_packages(bundle, py, missing, index))
    if fix.key == "files_public":
        return fetch_public_files(bundle, hf_bases)
    if fix.key == "vcredist":
        return _installer(VC_URL, ["/install", "/passive", "/norestart"], ok_codes=(0, 1638, 3010))
    if fix.key == "ollama":
        return _installer(OLLAMA_URL, ["/SILENT"]) and ollama_pull()
    if fix.key == "ollama_model":
        return ollama_pull()
    return False
