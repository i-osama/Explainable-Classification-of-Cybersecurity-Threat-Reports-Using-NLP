"""Train and check: teach the tool new examples, then prove on other sentences that it learned them.

Training = (1) the SVM is refit on the thesis training data plus the examples, and (2) an "example memory": when a new
sentence is very close to a taught example (cosine of the matcher's sentence embeddings >= t), the taught technique wins.
t comes from calibrate_memory.py (thesis train -> dev, not test). This is a demo feature, not a thesis result.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

import core

APP_DIR = Path(__file__).parent
DEV_DROP_MAX = 0.01  # the no-damage check fails when thesis dev P@1 drops by more than 1 point


@dataclass
class Memory:
    emb: np.ndarray                     # (n, d) L2-normalised matcher embeddings of the taught examples
    labels: list                        # per example: list of technique ids (first = the answer)
    texts: list = field(default_factory=list)
    t: float = 0.9

    def lookup(self, E) -> list:
        """Per query row: (labels, similarity, example index) of the closest example when similarity >= t, else None."""
        if len(self.labels) == 0 or len(E) == 0:
            return [None] * len(E)
        S = np.asarray(E) @ np.asarray(self.emb).T
        j = S.argmax(1)
        return [(self.labels[k], float(S[i, k]), int(k)) if S[i, k] >= self.t else None for i, k in enumerate(j)]


def load_t(root) -> float | None:
    """Memory threshold from memory_calib.json (folder models/ or the app's _build/); None when not calibrated."""
    for p in (Path(root) / "models" / "memory_calib.json", APP_DIR / "_build" / "memory_calib.json"):
        try:
            return float(json.loads(p.read_text(encoding="utf-8"))["t"])
        except (OSError, ValueError, KeyError):
            continue
    return None


def matcher_emb(comps, texts) -> np.ndarray:
    m = next(c for c in comps if c.name == "matcher")
    return m._emb(list(texts), 128)


def build_memory(comps, rows, t) -> Memory:
    return Memory(emb=matcher_emb(comps, [s for s, _ in rows]), labels=[list(ids) for _, ids in rows], texts=[s for s, _ in rows], t=t)


def predict(comps, labels, texts, memory=None, weights=(3, 1, 1, 1)) -> list:
    """Top technique per sentence from the fused models; the example memory wins when it fires."""
    texts = list(texts)
    if not texts:
        return []
    S = np.tensordot(np.asarray(weights, float), np.stack([c.z(texts) for c in comps]), axes=1)
    out = [{"top": labels[int(r.argmax())], "source": "model", "sim": None, "example": None} for r in S]
    if memory is not None:
        for o, hit in zip(out, memory.lookup(matcher_emb(comps, texts))):
            if hit:
                o.update(top=hit[0][0], source="memory", sim=hit[1], example=hit[2])
    return out


def _norm(s):
    return " ".join(str(s).lower().split())


def split_check(train_rows, check_rows):
    """Test sentences identical to a training line prove nothing: they are left out, with a message."""
    seen = {_norm(s) for s, _ in train_rows}
    kept = [r for r in check_rows if _norm(r[0]) not in seen]
    msgs = [f"Left out: \"{s[:60]}\" is identical to a training line." for s, _ in check_rows if _norm(s) in seen]
    return kept, msgs


def check_report(before, after, gold) -> dict:
    return {"n": len(gold), "right_before": sum(b["top"] in g for b, g in zip(before, gold)),
            "right_after": sum(a["top"] in g for a, g in zip(after, gold))}


def dev_p1(R, art, memory, E_dev) -> float:
    """Seed-42 full fusion on the 604 thesis dev sentences (stored dev scores + the SVM in `art`), plus the memory."""
    d, L = art["dev"], len(art["labels"])
    Z = {**d["z"], "svm": core.zrow(core.to_full(art["svm"].decision_function(art["vec"].transform(d["texts"])), art["seen_idx"], L))}
    S = core.fuse(Z, core.W4 if "matcher" in Z else (0, 1, 1, 1))
    tops = [art["labels"][int(j)] for j in S.argmax(1)]
    if memory is not None:
        for i, hit in enumerate(memory.lookup(E_dev)):
            if hit:
                tops[i] = hit[0][0]
    lab = np.array(art["labels"])
    return float(np.mean([t in set(lab[np.where(y)[0]]) for t, y in zip(tops, d["Y"])]))


def verdict(train_rep, check_rep, dev_before, dev_after):
    """(worked, plain-language message). Worked = more test sentences right and no damage on the thesis dev sentences."""
    n, rb, ra = check_rep["n"], check_rep["right_before"], check_rep["right_after"]
    if n == 0:
        return False, "Add test sentences (not used for training) to prove that training worked."
    if dev_before - dev_after > DEV_DROP_MAX:
        return False, (f"Careful: training made the thesis sentences worse ({dev_before:.1%} right before, {dev_after:.1%} after). "
                       "Use fewer or more specific examples, then train again.")
    if ra <= rb:
        return False, (f"Training did not change the result on your test sentences ({ra} of {n} right, before: {rb} of {n}). "
                       "Try more examples, or examples closer to the test sentences.")
    return True, (f"Training worked: {ra} of {n} test sentences are now right (before: {rb} of {n}). "
                  f"It learned {train_rep['right_after']} of {train_rep['n']} training examples. "
                  f"No damage: the 604 thesis check sentences were {dev_before:.1%} right before and {dev_after:.1%} after.")
