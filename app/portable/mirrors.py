"""Pick the fastest server for this network, then download with a SHA-256 check and fall back to the next server.

Standard library only.   python mirrors.py --race     (prints the race for this PC)
"""
from __future__ import annotations

import hashlib
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable, Optional, Sequence
from urllib.parse import urlparse

# Python package index: the official one first, then large public mirrors (Asia and elsewhere). Same files, checked by hash.
PYPI = ("https://pypi.org/simple", "https://pypi.tuna.tsinghua.edu.cn/simple", "https://mirrors.aliyun.com/pypi/simple",
        "https://mirrors.cloud.tencent.com/pypi/simple", "https://mirror.kakao.com/pypi/simple")
HF = ("https://huggingface.co", "https://hf-mirror.com")
HF_PROBE = "BAAI/bge-base-en-v1.5/resolve/main/config.json"
UA = {"User-Agent": "ttp-demo-doctor/1.0"}


class DownloadError(RuntimeError):
    pass


def _opener(url):
    """Local test servers bypass any system proxy; internet URLs use this PC's proxy settings."""
    host = urlparse(url).hostname or ""
    return urllib.request.build_opener(urllib.request.ProxyHandler({})) if host in ("127.0.0.1", "localhost") else urllib.request.build_opener()


def _time_get(url, timeout):
    t0 = time.perf_counter()
    with _opener(url).open(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        r.read()
    return time.perf_counter() - t0


def _probe(base, path, timeout, tries):
    url = base.rstrip("/") + "/" + path.lstrip("/")
    best = None
    for _ in range(tries):  # best of `tries`; a server that fails once is not retried
        try:
            s = _time_get(url, timeout)
        except (OSError, urllib.error.URLError, ValueError):
            break
        best = s if best is None else min(best, s)
    return base, best


def race(bases: Sequence[str], path: str, timeout: float = 4.0, tries: int = 2) -> list:
    """[(base, seconds or None)] fastest first; None = not reachable. All servers are probed at the same time."""
    with ThreadPoolExecutor(max_workers=max(1, len(bases))) as ex:
        res = list(ex.map(lambda b: _probe(b, path, timeout, tries), bases))
    return sorted(res, key=lambda r: (r[1] is None, r[1] or 0.0))


def fetch(urls: Sequence[str], dest: Path, sha256: Optional[str] = None,
          progress: Optional[Callable[[int, int], None]] = None, timeout: float = 30.0) -> Path:
    """Download the first URL that works and matches the hash; a wrong file is deleted and the next URL is tried."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + ".part")
    reasons = []
    for url in urls:
        h = hashlib.sha256()
        try:
            with _opener(url).open(urllib.request.Request(url, headers=UA), timeout=timeout) as r, open(part, "wb") as f:
                total, done = int(r.headers.get("Content-Length") or 0), 0
                for chunk in iter(lambda: r.read(1 << 16), b""):
                    f.write(chunk); h.update(chunk); done += len(chunk)
                    if progress:
                        progress(done, total)
        except urllib.error.HTTPError as e:
            reasons.append(f"{url}: HTTP {e.code}")
            part.unlink(missing_ok=True)
            continue
        except (OSError, urllib.error.URLError, ValueError) as e:
            reasons.append(f"{url}: {type(e).__name__} {e}")
            part.unlink(missing_ok=True)
            continue
        if sha256 and h.hexdigest() != sha256.lower():
            reasons.append(f"{url}: hash mismatch (got a different file, e.g. a login page)")
            part.unlink(missing_ok=True)
            continue
        os.replace(part, dest)
        return dest
    raise DownloadError("download failed from every server:\n  " + "\n  ".join(reasons))


def table(res) -> str:
    return "\n".join(f"  {('%6.0f ms' % (s * 1000)) if s is not None else '   ---   '}  {b}" + ("   <- fastest" if i == 0 and s is not None else "")
                     for i, (b, s) in enumerate(res))


if __name__ == "__main__":
    if "--race" in sys.argv:
        print("Python package servers (time to load the 'pip' index page):")
        print(table(race(PYPI, "pip/")))
        print("Model servers (time to load a small model file):")
        print(table(race(HF, HF_PROBE)))
