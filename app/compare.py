"""Compare mode: one test sentence answered three ways, plus the stored whole-test-set numbers.

- GPU: the seed-42 full fusion (3,1,1,1) from the score files computed on the GPU (Colab / Kaggle).
- CPU: the same four models with the same weights, run now on this PC's CPU (live.py).
- Local LLM: qwen2.5:7b in Ollama on this PC (stored answers of the thesis run, or one new call).

The point the page makes: where a model runs (GPU or CPU) changes the speed, not the answer;
which model runs changes the answer. Every aggregate number is read from thesis_numbers.json or a
results file; nothing is typed here.
"""
from __future__ import annotations

import csv
import json
import os
import re
import time
import urllib.request
from pathlib import Path

import numpy as np

import core

# Copied from _showcase/src/ttpmap/llm.py (prereg 17, sealed); tests/test_compare.py checks they are still identical.
CLOSED_TEMPLATE = (
    "You are a cyber threat intelligence analyst. Map the sentence to MITRE ATT&CK Enterprise techniques.\n"
    "Choose only from this list (id: name):\n{catalog}\n\n"
    "Sentence: {sentence}\n\n"
    "Answer with up to 3 technique ids from the list, most likely first, separated by commas. Output only the ids."
)
OPTIONS = {"temperature": 0, "seed": 0, "num_predict": 64, "num_ctx": 8192}
LLM_MODEL = "qwen2.5:7b"
_ID = re.compile(r"\bT\s*(\d{4})(?:\s*[./]\s*(\d{3}))?\b", re.I)

# (variant, label, P@1 id, seconds id) of the thesis LLM baseline (prereg 17)
LLM_VARIANTS = (
    ("rr_matcher", "Local LLM + matcher shortlist (20 candidates)", "L1.rr_matcher.p1", "L1.rr_matcher.sec"),
    ("rr_zero", "Local LLM + zero-shot shortlist (20 candidates)", "L1.rr_zero.p1", "L1.rr_zero.sec"),
    ("closed", "Local LLM alone (list of 180 techniques)", "L1.closed.p1", "L1.closed.sec"),
)
CPU_MS_IDS = (("matcher", "G10.ms.matcher"), ("svm", "G10.ms.svm"), ("roberta", "G10.ms.roberta"), ("secbert", "G10.ms.secbert"))
RANK_WORDS = ("Most accurate", "Less accurate", "Less accurate", "Least accurate")


def parse_ids(text, allowed, k=3):
    """Same rule as ttpmap.llm.parse_ids: ids in order of first appearance, unknown ids dropped."""
    text = re.sub(r"<think>.*?</think>", " ", text or "", flags=re.S | re.I)
    out = []
    for m in _ID.finditer(text):
        tid = f"T{m.group(1)}" + (f".{m.group(2)}" if m.group(2) else "")
        if tid in allowed and tid not in out:
            out.append(tid)
        if len(out) == k:
            break
    return out


def results_dir(root):
    env = os.environ.get("TTPMAP_RESULTS")
    return core._find(root, *([env] if env else []), "results", "_showcase/results")


def _float(s):
    try:
        return float(str(s).split()[0])
    except (ValueError, IndexError):
        return None


def ranking(R):
    """Whole-test-set rows (725 sentences), best first. Values and CIs come from thesis_numbers.json."""
    rows = [{"system": "Fusion (3,1,1,1) of the trained models", "id": "B13a",
             "runs on": "trained on a cloud GPU (Colab / Kaggle); runs on GPU or CPU with the same answer", "seconds id": None}]
    rows += [{"system": lab, "id": pid, "runs on": "this PC: Ollama, 9 of 29 layers on the GTX 960, rest on CPU", "seconds id": sid}
             for _, lab, pid, sid in LLM_VARIANTS]
    for r in rows:
        r["P@1"] = _float(R.num(r["id"]))
        r["ci"] = R.cis.get(r["id"])
        r["seconds"] = R.num(r["seconds id"]) if r["seconds id"] else None
    rows = [r for r in rows if r["P@1"] is not None]
    rows.sort(key=lambda r: -r["P@1"])
    for i, r in enumerate(rows):
        r["rank"] = RANK_WORDS[0] if i == 0 else RANK_WORDS[-1] if i == len(rows) - 1 else RANK_WORDS[1]
    return rows


def cpu_ms(R):
    """Median CPU latency per sentence of each trained model (G10), and their sum = one fusion pass."""
    ms = {name: _float(R.num(i)) for name, i in CPU_MS_IDS}
    return ms, (sum(ms.values()) if all(v is not None for v in ms.values()) else None)


def gpu_fused_s42(R):
    """(725, L) seed-42 full fusion from the stored GPU score files; the SVM is refit on CPU (deterministic).

    Same recipe as check_live_parity.py. None when a score file is missing.
    """
    art, L = R.art, len(R.labels)
    lab2i = {l: i for i, l in enumerate(R.labels)}
    try:
        Z = {"matcher": core.zrow(np.load(art["matcher_state"].parent / "test_scores.npy")),
             "svm": core.zrow(core.to_full(art["svm"].decision_function(art["vec"].transform(R.texts)), art["seen_idx"], L))}
        for tag in ("roberta", "secbert"):
            d = art["cls_root"] / f"{tag}_pw_s42"
            cols = np.array([lab2i[str(x).upper()] for x in np.load(d / "mlb_classes.npy", allow_pickle=True)])
            Z[tag] = core.zrow(core.to_full(np.load(d / "test_probs.npy"), cols, L))
    except (OSError, KeyError, ValueError):
        return None
    return core.fuse(Z)


def top_k(row, labels, k=3):
    return [labels[j] for j in np.argsort(-row)[:k]]


def llm_rows(res):
    """{variant: {test row: stored reply}} from results/llm_raw/<variant>_test.jsonl (the thesis run); missing files are skipped."""
    out = {}
    for v, *_ in LLM_VARIANTS:
        f = Path(res) / "llm_raw" / f"{v}_test.jsonl" if res else None
        if not f or not f.exists():
            continue
        rows = {}
        for line in f.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
                rows[int(r["i"])] = r
            except (ValueError, KeyError):
                continue
        out[v] = rows
    return out


def placement_bench(res):
    """Rows of results/llm_raw/bench_placement.csv (same LLM, CPU only vs N layers on the GTX 960; 3 dev prompts)."""
    f = Path(res) / "llm_raw" / "bench_placement.csv" if res else None
    if not f or not f.exists():
        return []
    with f.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def parity(root):
    """live_parity.json from check_live_parity.py: live CPU scores vs the stored GPU score files."""
    for p in (Path(root) / "models" / "live_parity.json", Path(__file__).parent / "_build" / "live_parity.json"):
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
    return None


def stix_names_last_wins(root):
    """Names as the LLM baseline built them: every attack-pattern object of ATT&CK v12.1, the last one with an id wins."""
    p = core._find(root, "_evidence_pack/external/enterprise-attack-12.1.json")
    if not p:
        return {}
    objs = json.loads(Path(p).read_text(encoding="utf-8"))["objects"]
    return {r["external_id"]: o["name"] for o in objs if o["type"] == "attack-pattern"
            for r in o.get("external_references", []) if r.get("source_name") == "mitre-attack"}


def short_desc(desc, words):
    w = str(desc).split()
    return " ".join(w[:words]) + (" ..." if len(w) > words else "")


def catalog(R, names):
    """(id, name) of the 180 seen techniques, in label order: the closed-list prompt of the thesis run."""
    return [(R.labels[j], names.get(R.labels[j]) or R.names.get(R.labels[j]) or short_desc(R.desc.get(R.labels[j], ""), 6))
            for j in R.art["seen_idx"]]


def closed_prompt(sentence, cat):
    return CLOSED_TEMPLATE.format(catalog="\n".join(f"{i}: {n}" for i, n in cat), sentence=sentence)


def host(url):
    """127.0.0.1 instead of localhost: localhost tries IPv6 first and loses 2 s per request on this PC (D23)."""
    return url.rstrip("/").replace("//localhost", "//127.0.0.1")


def has_model(url, model=LLM_MODEL):
    try:
        with urllib.request.urlopen(host(url) + "/api/tags", timeout=2) as r:
            return any(m.get("name") == model for m in json.loads(r.read()).get("models", []))
    except Exception:
        return False


def ask_llm(prompt, url, num_gpu, allowed, timeout=600, post=None):
    """One Ollama call with the thesis options; num_gpu = layers on the GPU (0 = CPU only). -> ids, seconds, stats."""
    body = json.dumps({"model": LLM_MODEL, "prompt": prompt, "stream": False,
                       "options": {**OPTIONS, "num_gpu": int(num_gpu)}}).encode("utf-8")
    t0 = time.perf_counter()
    if post is None:
        req = urllib.request.Request(host(url) + "/api/generate", data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            out = json.loads(r.read())
    else:  # tests
        out = post(body)
    wall = time.perf_counter() - t0
    ns = 1e9
    return {"ids": parse_ids(out.get("response", ""), allowed), "raw": str(out.get("response", ""))[:200], "wall_s": wall,
            "load_s": out.get("load_duration", 0) / ns, "prompt_s": out.get("prompt_eval_duration", 0) / ns,
            "gen_s": out.get("eval_duration", 0) / ns, "prompt_tokens": out.get("prompt_eval_count")}


def torch_gpu():
    """(usable, text) for PyTorch on this PC; imports torch, so call it only when the CPU column is used."""
    try:
        import torch
    except ImportError:
        return False, "PyTorch not installed"
    if not torch.cuda.is_available():
        return False, f"torch {torch.__version__}: no usable CUDA GPU, models run on the CPU"
    return True, f"torch {torch.__version__}: CUDA GPU {torch.cuda.get_device_name(0)}"
