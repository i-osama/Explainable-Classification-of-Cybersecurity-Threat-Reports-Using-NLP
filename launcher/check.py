"""Self-check of the portable demo folder. Quick (every start): Python, libraries, files present with the right size.
Deep (CHECK_DEMO.bat): also SHA-256 of every file, the artifact check against the thesis numbers, the app tests,
and the live-vs-stored parity of the full fusion.

    python check.py [--deep]          prints [ OK ] / [FAIL] lines; exit code = number of failures
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

GREEN, RED, DIM, END = "\033[92m", "\033[91m", "\033[2m", "\033[0m"
LIBS = ("streamlit", "numpy", "pandas", "sklearn", "torch", "transformers", "shap")


def say(ok, msg):
    print(f"  {GREEN}[ OK ]{END} {msg}" if ok else f"  {RED}[FAIL]{END} {msg}", flush=True)
    return 0 if ok else 1


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def files(bundle, deep):
    """Files listed in launcher/MANIFEST.sha256.json: present with the right size; deep also compares SHA-256.
    Only "core" files (app, launcher, what the app loads) can fail the check; edited thesis material is reported, not blocking."""
    man = Path(bundle) / "launcher" / "MANIFEST.sha256.json"
    try:
        items = json.loads(man.read_text(encoding="utf-8"))["files"]
    except (OSError, ValueError, KeyError) as e:
        return say(False, f"manifest unreadable: {man} ({type(e).__name__})")
    bad, other = [], []
    for it in items:
        p = Path(bundle) / it["path"]
        if not p.is_file() or p.stat().st_size != it["size"] or (deep and sha256(p) != it["sha256"]):
            (bad if it.get("core", True) else other).append(it["path"])
    core = [it for it in items if it.get("core", True)]
    what = "SHA-256 checked" if deep else "present, sizes match"
    if other:
        print(f"  {DIM}[info] {len(other)} thesis-material file(s) changed or missing since the build (the app does not use them), "
              f"e.g. {other[0]}{END}")
    return say(not bad, f"{len(core) - len(bad)}/{len(core)} app, model and data files {what}"
               + (f"; first problem: {bad[0]} (copy the whole folder again)" if bad else ""))


def run_py(bundle, args, cwd, label, timeout=1800):
    sys.path.insert(0, str(Path(__file__).parent))
    from launch import env_for
    t0 = time.time()
    r = subprocess.run([sys.executable, "-E", "-s", "-X", "utf8", *args], cwd=cwd, env=env_for(Path(bundle)),
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    tail = (r.stdout.strip() or r.stderr.strip()).splitlines()[-1:] or [""]  # stdout summary first; stderr holds progress bars
    return say(r.returncode == 0, f"{label}: {tail[0][:110]} {DIM}({time.time() - t0:.0f} s){END}")


def run(bundle, deep=False):
    bundle = Path(bundle)
    os.system("")  # turns on colour codes in the Windows console
    fails = 0
    print(f"  {DIM}python {sys.version.split()[0]} at {sys.executable}{END}")
    missing = [m for m in LIBS if importlib.util.find_spec(m) is None]
    fails += say(not missing, "libraries: " + ("all present" if not missing else "missing " + ", ".join(missing)))
    fails += files(bundle, deep)
    if deep:
        app = bundle / "app"
        fails += run_py(bundle, ["verify_artifacts.py"], app, "app numbers vs thesis registry")
        fails += run_py(bundle, ["-m", "pytest", "-q", "-p", "no:cacheprovider"], app, "app tests")
        fails += run_py(bundle, ["check_live_parity.py", "--out", str(bundle / "logs" / "parity")], app, "live full fusion vs stored scores")
    return fails


if __name__ == "__main__":
    b = Path(__file__).resolve().parent.parent
    n = run(b, deep="--deep" in sys.argv)
    print(f"\n  {GREEN}ALL CHECKS PASSED{END}" if n == 0 else f"\n  {RED}{n} CHECK(S) FAILED{END}: see the lines above.")
    sys.exit(n)
