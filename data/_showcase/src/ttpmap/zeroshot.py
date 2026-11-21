"""Zero-shot bge scoring on CPU, same recipe as Exp_2.1 (shared encoder, CLS pooling, L2 norm, cosine; text 128 / labels 256 tokens).
Used for zero-shot dev candidates (never saved by the notebook) and for perturbed test sentences (Q1 plan Tasks 3 and 7)."""
from __future__ import annotations

from typing import Dict, Sequence, Tuple

import numpy as np

MODEL = "BAAI/bge-base-en-v1.5"
_CACHE: Dict[str, object] = {}
_LABELS: Dict[Tuple[str, int], np.ndarray] = {}


def _load(name: str = MODEL):
    if name not in _CACHE:
        import torch
        from transformers import AutoModel, AutoTokenizer
        tok = AutoTokenizer.from_pretrained(name); enc = AutoModel.from_pretrained(name).eval()
        torch.set_grad_enabled(False)
        _CACHE[name] = (tok, enc)
    return _CACHE[name]


def embed(texts: Sequence[str], max_len: int, name: str = MODEL, bs: int = 64) -> np.ndarray:
    import torch
    tok, enc = _load(name); out = []
    for i in range(0, len(texts), bs):
        b = tok(list(texts[i:i + bs]), padding=True, truncation=True, max_length=max_len, return_tensors="pt")
        h = enc(**{k: v for k, v in b.items() if k in ("input_ids", "attention_mask", "token_type_ids")}).last_hidden_state[:, 0]
        out.append(torch.nn.functional.normalize(h.float(), dim=-1).numpy())
    return np.concatenate(out)


def scores(texts: Sequence[str], label_texts: Sequence[str], name: str = MODEL, text_max_len: int = 128, label_max_len: int = 256) -> np.ndarray:
    key = (name, len(label_texts))
    if key not in _LABELS:
        _LABELS[key] = embed(list(label_texts), label_max_len, name)
    return embed(list(texts), text_max_len, name) @ _LABELS[key].T
