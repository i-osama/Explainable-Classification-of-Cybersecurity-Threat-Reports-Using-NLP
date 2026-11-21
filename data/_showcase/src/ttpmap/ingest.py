"""Accept Colab outputs (Q1 plan Task 8): every output file listed in a manifest must exist locally with the same SHA-256.
Paths in manifests are Colab paths; they are mapped to the returned folder by the part after "KDU/Thesis/" (or after "showcase_runs/",
"content/out/" or "kaggle/working/out/", the output roots of the hardened notebooks).
All-or-nothing: if any file is missing or differs, or a manifest is a SMOKE run, nothing is copied."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Dict, List


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _local(src: Path, colab_path: str) -> Path:
    s = colab_path.replace("\\", "/")
    for key in ("KDU/Thesis/", "showcase_runs/", "content/out/", "kaggle/working/out/"):     # last two: hardened notebooks (Prompt F)
        if key in s:
            tail = s.split(key, 1)[1]
            for cand in (src / tail, src / "showcase_runs" / tail):
                if cand.exists():
                    return cand
    hits = list(src.rglob(Path(s).name))
    return hits[0] if len(hits) == 1 else src / "__missing__" / Path(s).name


def ingest(src: Path, dest: Path) -> Dict:
    bad: List[str] = []; plan = []; runs = {}
    mans = sorted(Path(src).rglob("manifest_*.json"))
    if not mans:
        bad.append(f"no manifest_*.json under {src}")
    for m in mans:
        man = json.loads(m.read_text(encoding="utf-8")); rid = man.get("run_id", m.stem)
        if man.get("status") == "SMOKE":
            bad.append(f"{rid}: SMOKE manifest (a dry run, not a result)"); continue
        for cp, h in man.get("output_sha256", {}).items():
            lp = _local(Path(src), cp)
            if not lp.exists():
                bad.append(f"{rid}: missing {cp}")
            elif _sha(lp) != h:
                bad.append(f"{rid}: SHA-256 differs for {cp}")
            else:
                plan.append((rid, lp))
        runs[rid] = {"manifest": str(m), "status": man.get("status"), "metrics": man.get("metrics", {}), "env": man.get("env", {})}
    if bad:
        return {"ok": False, "bad": bad, "copied": 0}
    dest = Path(dest); dest.mkdir(parents=True, exist_ok=True)
    for rid, lp in plan:
        out = dest / rid / lp.name
        if out.exists() and _sha(out) != _sha(lp):
            return {"ok": False, "bad": [f"{rid}: {out} already exists with different content (never overwritten)"], "copied": 0}
        out.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(lp, out)
    for m in mans:
        shutil.copy2(m, dest / m.name)
    (dest / "INGEST_LOG.json").write_text(json.dumps({"source": str(src), "runs": runs}, indent=1), encoding="utf-8")
    return {"ok": True, "bad": [], "copied": len(plan)}
