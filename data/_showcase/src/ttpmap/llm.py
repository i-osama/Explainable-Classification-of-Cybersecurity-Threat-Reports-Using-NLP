"""LLM baseline (Q1 plan Task 7, prereg 17): fixed prompts, id parsing, local Ollama client.

Prompts are fixed before the test run; their SHA-256 is sealed in experiments/prereg/17_llm_local.md (tests/test_llm.py checks it).
The closed-set prompt puts the label catalogue BEFORE the sentence so the shared prefix can be reused between requests.
"""
from __future__ import annotations

import json
import os
import re
import urllib.request
from typing import Dict, List, Sequence, Set, Tuple

CLOSED_TEMPLATE = (
    "You are a cyber threat intelligence analyst. Map the sentence to MITRE ATT&CK Enterprise techniques.\n"
    "Choose only from this list (id: name):\n{catalog}\n\n"
    "Sentence: {sentence}\n\n"
    "Answer with up to 3 technique ids from the list, most likely first, separated by commas. Output only the ids."
)
RR_TEMPLATE = (
    "You are a cyber threat intelligence analyst. Map the sentence to MITRE ATT&CK Enterprise techniques.\n\n"
    "Sentence: {sentence}\n\n"
    "Candidate techniques (id: name: description):\n{candidates}\n\n"
    "Answer with up to 3 candidate ids, most likely first, separated by commas. Output only the ids."
)
OPTIONS = {"temperature": 0, "seed": 0, "num_predict": 64, "num_ctx": 8192}
DESC_WORDS = 40          # each candidate description is cut to its first 40 words
N_CANDIDATES = 20

_ID = re.compile(r"\bT\s*(\d{4})(?:\s*[./]\s*(\d{3}))?\b", re.I)


def parse_ids(text: str, allowed: Set[str], k: int = 3) -> List[str]:
    """Technique ids in order of first appearance, normalised to Txxxx or Txxxx.yyy; ids outside `allowed` are dropped."""
    text = re.sub(r"<think>.*?</think>", " ", text or "", flags=re.S | re.I)
    out: List[str] = []
    for m in _ID.finditer(text):
        tid = f"T{m.group(1)}" + (f".{m.group(2)}" if m.group(2) else "")
        if tid in allowed and tid not in out:
            out.append(tid)
        if len(out) == k:
            break
    return out


def closed_prompt(sentence: str, catalog: Sequence[Tuple[str, str]]) -> str:
    return CLOSED_TEMPLATE.format(catalog="\n".join(f"{i}: {n}" for i, n in catalog), sentence=sentence)


def short_desc(desc: str, words: int = DESC_WORDS) -> str:
    w = str(desc).split()
    return " ".join(w[:words]) + (" ..." if len(w) > words else "")


def rr_prompt(sentence: str, cands: Sequence[Tuple[str, str, str]]) -> str:
    return RR_TEMPLATE.format(sentence=sentence, candidates="\n".join(f"{i}: {n}: {d}" for i, n, d in cands))


def placement() -> Dict:
    """Hardware placement only (not a pre-registered option): GPU layer count from TTPMAP_OLLAMA_NUM_GPU, else Ollama's automatic fit."""
    v = os.environ.get("TTPMAP_OLLAMA_NUM_GPU", "").strip()
    return {"num_gpu": int(v)} if v else {}


def generate(model: str, prompt: str, host: str = "http://127.0.0.1:11434", timeout: int = 900, extra: Dict | None = None) -> Dict:
    """One non-streaming Ollama /api/generate call with the pre-registered options plus the hardware placement."""
    body = json.dumps({"model": model, "prompt": prompt, "stream": False, "options": {**OPTIONS, **placement(), **(extra or {})}}).encode("utf-8")
    req = urllib.request.Request(f"{host}/api/generate", data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())
