"""Live mode with word-level permutation SHAP. Two systems:

- full fusion (3,1,1,1) = matcher + SVM + RoBERTa s42 + SecBERT s42, with the matcher retrained on Kaggle (notebook 04,
  seed 42, saved weights). Same components and z-scoring as notebook 06 (T2.full_fusion_shap).
- classifier-only (0,1,1,1) = SVM + RoBERTa s42 + SecBERT s42, equal weights (the earlier live mode).
Same SHAP settings as notebook 06 except n_perm, which is a speed knob here.
torch / transformers / shap are imported lazily so replay mode needs none of them.
"""
from __future__ import annotations

import time

import numpy as np

from core import split_units, to_full, zrow

OOV = "zzzmaskzzz"  # SVM mask token, as in notebook 06 (asserted absent from the TF-IDF vocabulary there)
MAX_LEN = 128      # sentence max tokens (classifiers and matcher, as in notebooks 04/06)
LABEL_LEN = 256    # matcher label-description max tokens at scoring (notebook 04 label_max_len_eval)
FULL_W = (3, 1, 1, 1)  # order of load(full=True): matcher, svm, roberta, secbert (core.ORDER)


def _label_emb(path, n_labels, compute):
    """Cached matcher label embeddings; recomputed when missing or built for another label count."""
    try:
        E = np.load(path)
        if E.shape[0] == n_labels:
            return E
    except (OSError, ValueError):
        pass
    E = compute()
    try:
        np.save(path, E)
    except OSError:  # read-only folder (e.g. a DVD/USB copy): keep it in memory only
        pass
    return E


class SvmComp:
    name, mask = "svm", OOV

    def __init__(self, art):
        self.vec, self.svm, self.idx, self.L = art["vec"], art["svm"], art["seen_idx"], len(art["labels"])
        assert OOV not in self.vec.vocabulary_

    def z(self, tx):
        return zrow(to_full(self.svm.decision_function(self.vec.transform(list(tx))), self.idx, self.L))


class HFComp:
    def __init__(self, tag, art, seed=42):
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        d = art["cls_root"] / f"{tag}_pw_s{seed}"
        self.torch, self.name, self.L = torch, f"{tag}_s{seed}", len(art["labels"])
        self.dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tok = AutoTokenizer.from_pretrained(str(d))
        self.model = AutoModelForSequenceClassification.from_pretrained(str(d)).float().to(self.dev).eval()
        lab2i = {l: i for i, l in enumerate(art["labels"])}
        self.cols = np.array([lab2i[str(c).upper()] for c in np.load(d / "mlb_classes.npy", allow_pickle=True)])
        self.mask = self.tok.mask_token

    def z(self, tx):
        tx, out = list(tx), []
        with self.torch.no_grad():
            for s in range(0, len(tx), 64):
                enc = self.tok(tx[s:s + 64], truncation=True, max_length=MAX_LEN, padding=True, return_tensors="pt").to(self.dev)
                out.append(self.torch.sigmoid(self.model(**enc).logits).cpu().numpy())
        return zrow(to_full(np.concatenate(out), self.cols, self.L))


class MatcherComp:
    """bge-base bi-encoder: CLS of the last hidden state, L2-normalised; score = sentence emb . label emb (notebook 04/06)."""
    name = "matcher"

    def __init__(self, art):
        import torch
        from transformers import AutoConfig, AutoModel, AutoTokenizer

        self.torch = torch
        self.tok = AutoTokenizer.from_pretrained(str(art["base_model"]))
        self.model = AutoModel.from_config(AutoConfig.from_pretrained(str(art["base_model"])))
        sd = torch.load(art["matcher_state"], map_location="cpu", weights_only=True)
        self.model.load_state_dict({k.removeprefix("enc."): v for k, v in sd.items()})  # saved from a wrapper with .enc
        self.model.float().eval()
        self.mask = self.tok.mask_token
        self.E = _label_emb(art["label_cache"], len(art["label_texts"]), lambda: self._emb(art["label_texts"], LABEL_LEN))

    def _emb(self, tx, max_len):
        tx, out = list(tx), []
        with self.torch.no_grad():
            for s in range(0, len(tx), 64):
                enc = self.tok(tx[s:s + 64], truncation=True, max_length=max_len, padding=True, return_tensors="pt")
                h = self.model(**enc).last_hidden_state[:, 0].float()
                out.append(self.torch.nn.functional.normalize(h, dim=-1).numpy())
        return np.concatenate(out)

    def raw(self, tx):
        return self._emb(tx, MAX_LEN) @ self.E.T

    def z(self, tx):
        return zrow(self.raw(tx))


def load(art, full=False):
    cls = [SvmComp(art), HFComp("roberta", art), HFComp("secbert", art)]
    return [MatcherComp(art), *cls] if full else cls


def score_batch(comps, texts, weights=None):
    """Fused z-scores (n, L) of many sentences at once; no SHAP (report mode)."""
    w = np.ones(len(comps)) if weights is None else np.asarray(weights, float)
    return np.tensordot(w, np.stack([c.z(list(texts)) for c in comps]), axes=1)


def comp_scores(comps, parts, keeps, k):
    """Score of label k from each component for each keep-mask row; masked words use that component's own mask token."""
    return np.stack([c.z(["".join(l + (w if kp else c.mask) + t for (l, w, t), kp in zip(parts, keep)) for keep in keeps])[:, k] for c in comps], axis=1)


def analyse(comps, text, n_perm=10, seed=42, weights=None):
    """-> scores row (weighted z-sum; equal weights when None), top-1 index, SHAP units/values of that top-1 score, timings."""
    import shap

    parts = split_units(text)
    n = len(parts)
    if n < 2:
        raise ValueError("need at least 2 words")
    ms, zs = {}, []
    for c in comps:  # one timed pass per component, batch size 1 (same way the latency figure was measured)
        t0 = time.perf_counter()
        zs.append(c.z([text])[0])
        ms[c.name] = (time.perf_counter() - t0) * 1000
    w = np.ones(len(comps)) if weights is None else np.asarray(weights, float)
    S = np.tensordot(w, np.asarray(zs), axes=1)
    k = int(S.argmax())
    ex = shap.Explainer(lambda M: comp_scores(comps, parts, np.asarray(M) > 0.5, k), shap.maskers.Independent(np.zeros((1, n))),
                        algorithm="permutation", seed=seed)
    t0 = time.perf_counter()
    sv = ex(np.ones((1, n)), max_evals=n_perm * (2 * n + 1), batch_size=64, silent=True)[0]
    V = np.asarray(sv.values) @ w  # Shapley values are linear in the explained output: fused = weighted sum of components
    return {"scores": S, "k": k, "units": ["".join(p) for p in parts], "values": V.tolist(), "ms": ms, "weights": tuple(w.tolist()),
            "shap_s": time.perf_counter() - t0, "additivity_error": float(abs(V.sum() + np.asarray(sv.base_values) @ w - S[k]))}
