"""Synthetic stand-in for the thesis artifacts, so the app runs anywhere. Labels are DEMO-xx on purpose: nothing here is a result."""
import numpy as np

from core import Calib, Replay

KW = {  # label -> (name, trigger words)
    "DEMO-01": ("Host Info Discovery", ["computer", "hostname", "systeminfo"]),
    "DEMO-02": ("Memory Credential Theft", ["lsass", "dump", "mimikatz"]),
    "DEMO-03": ("Run-Key Persistence", ["registry", "startup", "autorun"]),
    "DEMO-04": ("Archive Staged Data", ["archive", "rar", "compress"]),  # rare in "training"
    "DEMO-05": ("Account Discovery", ["accounts", "net user", "enumerate"]),
    "DEMO-06": ("Unseen Technique", ["tunnel", "proxy", "relay"]),  # support 0
}
FILL = "the operator then used the tool on the host before moving on".split()


def _sentence(rng, lab):
    w = list(rng.choice(KW[lab][1], 2, replace=False))
    toks = list(rng.choice(FILL, 7)) + w
    rng.shuffle(toks)
    return " ".join(toks), w


def _scores(rng, gold_i, n_lab, strong=True):
    s = rng.normal(0, 1, n_lab) * 2
    s[gold_i] += 14 if strong else 5
    return s


def demo_replay(seed=0, n=40):
    rng = np.random.default_rng(seed)
    labels = list(KW)
    L = len(labels)
    gold_i = rng.integers(0, 5, n)
    texts, S, shap = [], np.zeros((n, L)), {}
    for i, g in enumerate(gold_i):
        t, w = _sentence(rng, labels[g])
        texts.append(t)
        S[i] = _scores(rng, g, L, strong=rng.random() > 0.3)
        explained = labels[int(S[i].argmax())] if i % 7 else labels[(g + 1) % L]  # every 7th: explained label != fused top-1
        vals = [(1.5 + rng.random()) if (u in w and explained == labels[g]) else float(rng.normal(0, 0.1)) for u in t.split()]
        shap[i] = {"values": vals, "label": explained}
    dg = rng.integers(0, 5, 200)
    S_dev = np.stack([_scores(rng, g, L, rng.random() > 0.3) for g in dg])
    Y_dev = np.zeros((200, L), bool)
    Y_dev[np.arange(200), dg] = True
    cal = Calib.fit(S_dev, Y_dev)
    fsh = {0: {"values": shap[0]["values"], "label": labels[int(S[0].argmax())], "correct": True}}  # one stored full-fusion SHAP row
    return Replay(labels, {k: v[0] for k, v in KW.items()}, texts, [[labels[g]] for g in gold_i], S, cal, np.array([40, 35, 30, 2, 25, 0]), shap,
                  drift={"DEMO-05": "status deprecated, successor DEMO-01 (active)"}, conf={"DEMO-02": [("DEMO-05", 3)]},
                  desc={k: f"Synthetic description of {v[0]}: uses {', '.join(v[1])}." for k, v in KW.items()},
                  cal_full=cal, fshap=fsh,
                  banner="SYNTHETIC DEMO DATA: invented sentences, labels and scores. Nothing on this screen is a thesis result.")
