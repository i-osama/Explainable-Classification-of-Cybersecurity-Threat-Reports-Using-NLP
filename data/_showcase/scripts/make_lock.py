"""Freeze the project .venv into a hash-checked lock for the portable doctor (Windows, Python 3.13).

    python make_lock.py

Writes ttp_app/portable/requirements.lock.txt (pins + SHA-256 from pypi.org, via `uv pip compile --generate-hashes`),
ttp_app/portable/requirements.sizes.json (download size of the wheel pip picks on Windows) and
ttp_app/portable/bootstrap.json (uv wheel file name + SHA-256 + size, Python version) for bootstrap.ps1.
Checks: every .venv package is in the lock with the same version and at least one hash.
"""
import json
import re
import subprocess
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(r"E:\Osamas Paper")
VENV_PY = ROOT / ".venv" / "Scripts" / "python.exe"
OUT = ROOT / "ttp_app" / "portable"
TAGS = ("cp313-cp313-win_amd64", "cp313-abi3-win_amd64", "cp312-abi3-win_amd64", "cp311-abi3-win_amd64", "cp310-abi3-win_amd64",
        "cp39-abi3-win_amd64", "cp38-abi3-win_amd64", "cp37-abi3-win_amd64", "py3-none-win_amd64", "py313-none-any", "py3-none-any",
        "py2.py3-none-any")
PY_VERSION = "3.13.18"


def frozen():
    code = "import json; from importlib import metadata as m; print(json.dumps({d.metadata['Name']: d.version for d in m.distributions()}))"
    return json.loads(subprocess.run([str(VENV_PY), "-c", code], capture_output=True, text=True, check=True).stdout)


def pypi_json(name, version):
    with urllib.request.urlopen(f"https://pypi.org/pypi/{name}/{version}/json", timeout=30) as r:
        return json.loads(r.read())


def pick_wheel(files):
    """The wheel pip would pick on Windows x64 / CPython 3.13: first matching tag in TAGS order."""
    wheels = [f for f in files if f["filename"].endswith(".whl")]
    for tag in TAGS:
        for f in wheels:
            if f["filename"][:-4].endswith(tag):
                return f
    return None


def main():
    pins = {n: v.split("+")[0] for n, v in frozen().items()}
    req_in = OUT / "_lock.in"
    req_in.write_text("\n".join(f"{n}=={v}" for n, v in sorted(pins.items(), key=lambda x: x[0].lower())) + "\n", encoding="utf-8")
    lock = OUT / "requirements.lock.txt"
    r = subprocess.run(["uv", "pip", "compile", str(req_in), "--generate-hashes", "--python-version", "3.13",
                        "--python-platform", "x86_64-pc-windows-msvc", "--index-url", "https://pypi.org/simple",
                        "--no-header", "--quiet", "-o", str(lock)], capture_output=True, text=True)
    req_in.unlink()
    if r.returncode:
        sys.exit("uv pip compile failed:\n" + r.stderr[-3000:])
    text = lock.read_text(encoding="utf-8")
    got = {re.sub(r"[-_.]+", "-", m.group(1)).lower(): m.group(2) for m in re.finditer(r"^([A-Za-z0-9][A-Za-z0-9._-]*)==(\S+)", text, re.M)}
    bad = [n for n, v in pins.items() if got.get(re.sub(r"[-_.]+", "-", n).lower()) != v]
    blocks = re.split(r"\n(?=[A-Za-z0-9])", text)
    no_hash = [b.split("==")[0] for b in blocks if "==" in b and "--hash=sha256:" not in b]
    print(f"lock: {len(got)} packages, {len(pins)} in .venv; version mismatches: {bad or 'none'}; without hash: {no_hash or 'none'}")

    def size(item):
        n, v = item
        try:
            w = pick_wheel(pypi_json(n, v)["urls"])
            return n, (w["size"] if w else None)
        except Exception:
            return n, None
    with ThreadPoolExecutor(8) as ex:
        sizes = dict(ex.map(size, sorted(pins.items())))
    (OUT / "requirements.sizes.json").write_text(json.dumps(sizes, indent=1), encoding="utf-8")
    known = [s for s in sizes.values() if s]
    print(f"sizes: {len(known)}/{len(sizes)} known, total {sum(known) / 2 ** 20:.0f} MB")

    uv_v = subprocess.run(["uv", "--version"], capture_output=True, text=True, check=True).stdout.split()[1]
    w = next(f for f in pypi_json("uv", uv_v)["urls"] if f["filename"].endswith("win_amd64.whl"))
    boot = {"python": PY_VERSION, "uv_version": uv_v, "uv_wheel": w["filename"], "uv_sha256": w["digests"]["sha256"], "uv_size": w["size"]}
    (OUT / "bootstrap.json").write_text(json.dumps(boot, indent=1), encoding="utf-8")
    print("bootstrap:", boot)
    sys.exit(1 if bad or no_hash else 0)


if __name__ == "__main__":
    main()
