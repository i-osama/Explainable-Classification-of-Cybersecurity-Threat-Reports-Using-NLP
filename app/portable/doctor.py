"""Doctor: checks this PC and this folder before the demo starts, then (main) repairs what it can and starts the app.

Standard library only, so it runs with the folder's own Python (or any Python 3.9+).
It looks only at what the app needs: Windows version, CPU, memory, disk, the folder's Python and libraries,
the folder's files, the Microsoft C++ runtime and (optional) Ollama. It never reads personal files.

    python doctor.py [--scan-only] [BUNDLE]
"""
from __future__ import annotations

import ctypes
import importlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOCK = "requirements.lock.txt"
VC_DLLS = ("vcruntime140.dll", "vcruntime140_1.dll", "msvcp140.dll")
LLM = "qwen2.5:7b"
RAM_MIN_GB, RAM_FREE_GB, PATH_MAX = 6.0, 3.0, 100
LIBS = ("streamlit", "numpy", "pandas", "sklearn", "torch", "transformers", "shap")  # import check when a folder has no lock


@dataclass
class Check:
    key: str
    ok: bool
    need: str           # "required" | "optional" | "info"
    detail: str
    fix: str | None     # repair action key, or None when only the user can fix it


_PIN = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)\s*==\s*([^\s\\;]+)")


def norm(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def lock_pins(lock: Path) -> dict:
    """{name: version} from a pip-compile style lock (hash lines are skipped)."""
    out = {}
    for line in Path(lock).read_text(encoding="utf-8").splitlines():
        m = _PIN.match(line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


_CHECK_PKGS = """
import json, re, sys
from importlib import metadata
pins = json.loads(sys.argv[1])
have = {re.sub(r"[-_.]+", "-", (d.metadata["Name"] or "")).lower(): d.version.split("+")[0] for d in metadata.distributions()}
print(json.dumps([n for n, v in pins.items() if have.get(re.sub(r"[-_.]+", "-", n).lower()) != v.split("+")[0]]))
"""
_CHECK_MODS = """
import importlib.util, json, sys
print(json.dumps([m for m in json.loads(sys.argv[1]) if importlib.util.find_spec(m) is None]))
"""


class Probes:
    """Real answers for this PC. Every method is small and never raises (a failed probe answers 'not found')."""

    def windows(self):
        if platform.system() != "Windows":
            return False, f"{platform.system()} {platform.machine()}"
        try:
            rel = int(platform.release())
        except ValueError:
            rel = 0
        ok = rel >= 10 and platform.machine().endswith("64") and sys.maxsize > 2 ** 32
        return ok, f"Windows {platform.release()} {platform.machine()}"

    def avx2(self):
        try:
            return bool(ctypes.windll.kernel32.IsProcessorFeaturePresent(40))  # PF_AVX2_INSTRUCTIONS_AVAILABLE
        except (AttributeError, OSError):
            return False

    def ram_gb(self):
        class MS(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong), ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong), ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong), ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong), ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        try:
            m = MS(); m.dwLength = ctypes.sizeof(MS)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
            return m.ullTotalPhys / 2 ** 30, m.ullAvailPhys / 2 ** 30
        except (AttributeError, OSError):
            return 0.0, 0.0

    def disk_free_gb(self, path):
        p = Path(path)
        while not p.exists() and p != p.parent:
            p = p.parent
        try:
            return shutil.disk_usage(p).free / 2 ** 30
        except OSError:
            return 0.0

    def runtime_python(self, bundle):
        py = Path(bundle) / "runtime" / "python" / "python.exe"
        return py if py.is_file() else None

    def missing_packages(self, py, lock):
        """Locked packages that are missing or have another version; without a lock, the main modules that do not import."""
        pins = lock_pins(lock) if Path(lock).is_file() else {}
        code, arg, fallback = (_CHECK_PKGS, json.dumps(pins), sorted(pins)) if pins else (_CHECK_MODS, json.dumps(LIBS), list(LIBS))
        try:
            r = subprocess.run([str(py), "-E", "-s", "-c", code, arg], capture_output=True, text=True, timeout=120)
            return json.loads(r.stdout.strip().splitlines()[-1]) if r.returncode == 0 else fallback
        except (OSError, ValueError, IndexError, subprocess.TimeoutExpired):
            return fallback

    def bad_files(self, bundle):
        """Core files of launcher/MANIFEST.sha256.json that are missing or have the wrong size -> (public, private)."""
        try:
            items = json.loads((Path(bundle) / "launcher" / "MANIFEST.sha256.json").read_text(encoding="utf-8"))["files"]
        except (OSError, ValueError, KeyError):
            return [], ["launcher/MANIFEST.sha256.json"]
        pub, priv = [], []
        for it in items:
            if not it.get("core", True):
                continue
            p = Path(bundle) / it["path"]
            if not p.is_file() or p.stat().st_size != it["size"]:
                (pub if it.get("origin") == "public" else priv).append(it["path"])
        return pub, priv

    def vcredist(self):
        sys32 = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32"
        return all((sys32 / d).is_file() for d in VC_DLLS)

    def writable(self, bundle):
        t = Path(bundle) / ".doctor_write_test"
        try:
            t.write_text("ok"); t.unlink()
            return True
        except OSError:
            return False

    def ollama(self):
        exe = shutil.which("ollama") or next((str(p) for p in (Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Ollama" / "ollama.exe",)
                                              if p.is_file()), None)
        try:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            with opener.open("http://127.0.0.1:11434/api/tags", timeout=1.5) as r:
                names = {m.get("name") for m in json.loads(r.read()).get("models", [])}
            return True, LLM in names
        except (OSError, ValueError):
            return exe is not None, False


REAL = Probes()


def scan(bundle: Path, probes: Probes = REAL) -> list[Check]:
    bundle = Path(bundle)
    out = []
    ok, txt = probes.windows()
    out.append(Check("os", ok, "required", txt if ok else f"{txt}: this demo runs on Windows 10/11 64-bit only", None))
    avx2 = probes.avx2()
    out.append(Check("cpu", avx2, "info", "AVX2 present" if avx2 else "AVX2 not found (very old CPU): the models may run slowly", None))
    total, free = probes.ram_gb()
    if total < RAM_MIN_GB:
        out.append(Check("ram", False, "required", f"{total:.1f} GB memory; the models need at least {RAM_MIN_GB:.0f} GB", None))
    elif free < RAM_FREE_GB:
        out.append(Check("ram", False, "info", f"{free:.1f} of {total:.1f} GB memory free: close other programs before the demo", None))
    else:
        out.append(Check("ram", True, "required", f"{total:.1f} GB memory, {free:.1f} GB free", None))

    py = probes.runtime_python(bundle)
    if py is None:
        out.append(Check("python", False, "required", "the folder has no working Python", "runtime"))
        out.append(Check("packages", False, "required", "the libraries are installed together with Python", "packages"))
    else:
        out.append(Check("python", True, "required", str(py), None))
        lock = bundle / "launcher" / LOCK
        miss = probes.missing_packages(py, lock)
        out.append(Check("packages", not miss, "required", "all libraries present" if not miss else
                         f"{len(miss)} missing or wrong version: {', '.join(miss[:6])}{' ...' if len(miss) > 6 else ''}",
                         "packages" if miss else None))
    pub, priv = probes.bad_files(bundle)
    out.append(Check("files_public", not pub, "required", "public model files present" if not pub else
                     f"{len(pub)} public model file(s) missing, e.g. {pub[0]}", "files_public" if pub else None))
    out.append(Check("files_private", not priv, "required", "thesis model and data files present" if not priv else
                     f"{len(priv)} thesis file(s) missing or damaged, e.g. {priv[0]}: copy the whole folder again "
                     "(they cannot be downloaded)", None))
    vc = probes.vcredist()
    out.append(Check("vcredist", vc, "required", "Microsoft C++ runtime present" if vc else
                     "Microsoft Visual C++ runtime missing (PyTorch needs it)", None if vc else "vcredist"))

    repairs = [c for c in out if not c.ok and c.fix]
    downloading = any(c.fix in ("runtime", "packages", "files_public") for c in repairs)
    need_gb = 3.0 if py is None else 1.0 if downloading else 0.0
    free_gb = probes.disk_free_gb(bundle)
    out.append(Check("disk", free_gb >= need_gb, "required" if need_gb else "info",
                     f"{free_gb:.1f} GB free" + (f", downloads need {need_gb:.0f} GB" if need_gb else ""), None))
    w = probes.writable(bundle)
    out.append(Check("writable", w, "required" if repairs else "info", "folder is writable" if w else
                     ("the folder is read-only (USB stick or DVD): copy the folder to this laptop first" if repairs else
                      "the folder is read-only: fine for the demo (logs go to the temp folder)"), None))
    long_path, ascii_path = len(str(bundle)) > PATH_MAX, str(bundle).isascii()
    out.append(Check("path", not long_path and ascii_path, "info", f"folder path has {len(str(bundle))} characters" + (
        ": move the folder closer to the drive root, e.g. C:\\TTP_DEMO" if long_path else
        "; it has non-English letters: if a step fails, move the folder to C:\\TTP_DEMO" if not ascii_path else ""), None))
    inst, model = probes.ollama()
    out.append(Check("ollama", inst and model, "optional",
                     f"Ollama with {LLM} ready" if inst and model else f"Ollama installed, {LLM} not found or Ollama not running" if inst
                     else "Ollama not installed (only the local-AI comparison needs it)",
                     None if inst and model else "ollama_model" if inst else "ollama"))
    return out


TAG = {True: "[ OK ]", "required": "[FAIL]", "optional": "[ -- ]", "info": "[NOTE]"}
NAMES = {"os": "Windows", "cpu": "Processor", "ram": "Memory", "disk": "Disk space", "python": "Python (in the folder)",
         "packages": "Libraries", "files_public": "Public model files", "files_private": "Thesis files",
         "vcredist": "C++ runtime", "writable": "Folder access", "path": "Folder path", "ollama": "Local AI (optional)"}


def report(checks: list[Check]) -> str:
    return "\n".join(f"  {TAG[True] if c.ok else TAG[c.need]} {NAMES.get(c.key, c.key):<24} {c.detail}" for c in checks)


def blocking(checks: list[Check]) -> list[Check]:
    """Required checks that fail; the app cannot start while any remains."""
    return [c for c in checks if not c.ok and c.need == "required"]


OPTIONAL = ("ollama", "ollama_model")


def _ask_console(q):
    try:
        return input("    " + q).strip().lower() in ("y", "yes")
    except EOFError:  # no console (scheduled run): never install Windows-wide software unasked
        return False


def _size_text(fix, bundle, probes):
    if fix.key != "packages":
        return f"about {fix.size_mb} MB" if fix.size_mb else "size unknown"
    try:
        sizes = json.loads((Path(bundle) / "launcher" / "requirements.sizes.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        sizes = {}
    py = probes.runtime_python(bundle)
    names = probes.missing_packages(py, Path(bundle) / "launcher" / LOCK) if py else list(lock_pins(Path(bundle) / "launcher" / LOCK)) \
        if (Path(bundle) / "launcher" / LOCK).is_file() else []
    known = {norm(k): v for k, v in sizes.items() if v}
    return size_words(len(names), sum(known.get(norm(n), 0) for n in names)) if names else "the missing libraries"


def size_words(n: int, nbytes: int) -> str:
    size = f"{nbytes / 2 ** 20:.0f} MB" if nbytes >= 2 ** 20 else f"{max(1, round(nbytes / 1000))} KB"
    return f"{n} {'library' if n == 1 else 'libraries'}, about {size}"


def main(argv=None, probes: Probes = REAL, start=None, ask=None, race=None, fixer=None) -> int:
    """Scan -> show what is missing -> pick the fastest servers -> fix -> scan again -> start the app."""
    sys.path.insert(0, str(HERE))
    import mirrors
    import repair
    argv = sys.argv[1:] if argv is None else list(argv)
    flags = {a for a in argv if a.startswith("--")}
    pos = [a for a in argv if not a.startswith("--")]
    bundle = Path(pos[0]) if pos else HERE.parent
    race, fixer = race or mirrors.race, fixer or repair.apply
    if ask is None:
        ask = (lambda q: True) if "--yes" in flags else _ask_console
    os.system("")  # colour codes on in the Windows console
    print("\n  Checking this PC and this folder (only what the demo needs)...\n")
    checks = scan(bundle, probes)
    print(report(checks))
    if "--scan-only" in flags:
        return len(blocking(checks))
    fixes = [f for f in repair.plan(checks) if "--optional" in flags or f.key not in OPTIONAL]
    if fixes:
        w = next(c for c in checks if c.key == "writable")
        if not w.ok:
            print(f"\n  {w.detail}")
            return 1
        print("\n  Will fix:")
        for f in fixes:
            print(f"    - {f.title}: {_size_text(f, bundle, probes)}, from {f.source}" + (" (asks first)" if f.needs_consent else ""))
        pypi, hf = [], list(mirrors.HF)
        if any(f.key in ("packages", "runtime") for f in fixes):
            print("\n  Finding the fastest Python package server for this network...")
            res = race(mirrors.PYPI, "pip/")
            print(mirrors.table(res))
            pypi = [b for b, s in res if s is not None]
        if any(f.key == "files_public" for f in fixes):
            res = race(mirrors.HF, mirrors.HF_PROBE)
            print(mirrors.table(res))
            hf = [b for b, s in res if s is not None]
        if (any(f.key in ("packages", "runtime") for f in fixes) and not pypi) or (any(f.key == "files_public" for f in fixes) and not hf):
            print("\n  No server answered: this PC seems to be offline. The demo " + repair.needs_internet_text(fixes))
            print("  Connect to the internet (or copy the complete folder from the USB stick) and start again.")
            return 1
        for f in fixes:
            print(f"\n  Fixing: {f.title}")
            bases = pypi if f.key == "packages" else pypi[:1] or [""]  # only libraries are retried on the next server
            ok = any(fixer(f, bundle, b, ask, hf_bases=hf) for b in bases)
            print("    done." if ok else "    not fixed.")
        print("\n  Checking again...\n")
        importlib.invalidate_caches()  # libraries installed just now must be found by the start check in this process
        checks = scan(bundle, probes)
        print(report(checks))
    left = blocking(checks)
    if left:
        print("\n  The demo cannot start yet:\n" + "\n".join(f"    - {NAMES.get(c.key, c.key)}: {c.detail}" for c in left))
        return 1
    print("\n  Everything the demo needs is here. Starting...\n")
    if start is None:
        import launch
        start = launch.main
    return start()


if __name__ == "__main__":
    sys.exit(main())
