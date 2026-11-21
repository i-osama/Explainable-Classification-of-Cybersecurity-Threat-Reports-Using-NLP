"""Explanation text for one SHAP result: a deterministic template, or local qwen2.5:7b checked by a grounding rule.

GROUNDING RULE v1 (fixed before any model output was looked at; change it only with a new version number):
  (a) the text quotes at least one span in double quotes;
  (b) every word inside the quotes is one of the top-K positive-SHAP words (K = 5, case-folded, edge punctuation stripped);
  (c) every technique id in the text equals the explained label.
Fail any one and the app shows the template text instead. The check proves the words come from SHAP,
not that the explanation is right or that analysts find it useful (no human study supports that).
"""
from __future__ import annotations

import json
import re
import string
import urllib.request

K = 5
MODEL = "qwen2.5:7b"  # same model, quantisation and decoding as prereg 17 (temp 0, seed 0)
_PUNCT = string.punctuation + "“”‘’"
_QUOTE = re.compile(r'["“]([^"“”]+)["”]')
_TID = re.compile(r"T\d{4}(?:\.\d{3})?")


def norm(w):
    return w.strip(_PUNCT).lower()


def top_words(units, values, k=K):
    """Top-k units by positive SHAP value, as (word, value)."""
    ranked = sorted(((u.strip(), float(v)) for u, v in zip(units, values) if float(v) > 0), key=lambda t: -t[1])
    return ranked[:k]


def grounded(text, allowed, explained):
    """Return (ok, reason). `allowed` = words from top_words()."""
    ok_words = {norm(w) for w in allowed} - {""}
    quotes = _QUOTE.findall(text)
    if not quotes:
        return False, "no quoted words"
    for q in quotes:
        for w in q.split():
            if norm(w) and norm(w) not in ok_words:
                return False, f"quoted word not in top-{K} SHAP words: {w!r}"
    bad = [t for t in _TID.findall(text) if t != explained]
    if bad:
        return False, f"mentions other technique id(s): {sorted(set(bad))}"
    return True, "ok"


def template(explained, name, desc, words, note=""):
    if not words:
        return f"No word had a positive attribution for {name}, so no words are highlighted as support. {note}".strip()
    ws = ", ".join(f'"{w}"' for w, _ in words)
    d = f" ATT&CK describes it as: {desc[:220].rstrip()}{'...' if len(desc) > 220 else ''}" if desc else ""
    return (f"The explained model (RoBERTa, seed 42) chose {name}. The words that pushed its score up most are {ws}.{d} "
            f"This shows which words the model used, not that the choice is right. {note}").strip()


def prompt(text, explained, name, desc, words):
    return (
        "You explain a classifier's choice to a security analyst. Use only the facts below.\n"
        f"Sentence: {text}\n"
        f"Chosen technique: {name}\n"
        f"ATT&CK description: {desc[:400]}\n"
        f"Words that raised the score most (only these may be quoted): {', '.join(w for w, _ in words)}\n"
        "Write at most 2 sentences. Put every quoted word in double quotes. Do not mention any technique id other than "
        f"{explained}. Do not say the classifier is correct. Do not add facts that are not above."
    )


def ask_ollama(p, url="http://localhost:11434", model=MODEL, timeout=180):
    body = json.dumps({"model": model, "prompt": p, "stream": False,
                       "options": {"temperature": 0, "seed": 0, "num_predict": 120, "num_ctx": 8192}}).encode()
    req = urllib.request.Request(url.rstrip("/") + "/api/generate", body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:  # only a local URL is expected here
        return json.loads(r.read())["response"].strip()


def ollama_up(url="http://localhost:11434"):
    try:
        urllib.request.urlopen(url.rstrip("/") + "/api/tags", timeout=1.5).read()
        return True
    except Exception:
        return False


def explain(text, explained, name, desc, units, values, use_llm=False, url="http://localhost:11434", note="", ask=ask_ollama):
    """-> dict(text, source, grounded, reason). Never raises: any LLM failure falls back to the template."""
    words = top_words(units, values)
    tpl = template(explained, name, desc, words, note)
    if not use_llm or not words:
        return {"text": tpl, "source": "template", "grounded": None, "reason": "template"}
    try:
        out = ask(prompt(text, explained, name, desc, words), url=url)
    except Exception as e:  # server down, timeout, bad JSON
        return {"text": tpl, "source": "template", "grounded": None, "reason": f"LLM unavailable ({type(e).__name__})"}
    ok, why = grounded(out, [w for w, _ in words], explained)
    if ok:
        return {"text": (out + (" " + note if note else "")).strip(), "source": MODEL, "grounded": True, "reason": why}
    return {"text": tpl, "source": "template", "grounded": False, "reason": f"LLM text rejected: {why}", "rejected": out}
