import numpy as np
import pytest

shap = pytest.importorskip("shap")
import live  # noqa: E402

L = 6


class Stub:
    """Deterministic fake component: score of label j rises with the number of words in KEY[j]."""
    mask = "<mask>"
    KEY = {0: {"lsass", "dump"}, 1: {"registry", "run"}}

    def __init__(self, name, scale):
        self.name, self.scale = name, scale

    def z(self, tx):
        out = np.zeros((len(tx), L))
        for i, t in enumerate(tx):
            for j, ks in self.KEY.items():
                out[i, j] = self.scale * len(ks & set(t.lower().split()))
        return out


def test_live_shap_is_additive_and_points_at_trigger_words():
    comps = [Stub("a", 1.0), Stub("b", 2.0), Stub("c", 0.5)]
    o = live.analyse(comps, "attacker used mimikatz to dump lsass quickly", n_perm=8)
    assert o["k"] == 0 and o["additivity_error"] < 1e-6
    words = [u.strip() for u in o["units"]]
    top2 = {words[i] for i in np.argsort(o["values"])[-2:]}
    assert top2 == {"dump", "lsass"}
    assert set(o["ms"]) == {"a", "b", "c"}


def test_live_needs_two_words():
    with pytest.raises(ValueError):
        live.analyse([Stub("a", 1.0)], "lsass")


def test_weighted_shap_is_additive():
    comps = [Stub("a", 1.0), Stub("b", 2.0), Stub("c", 0.5)]
    text = "attacker added registry run key then dump lsass"
    o = live.analyse(comps, text, n_perm=8, weights=(3, 1, 1))
    want = 3 * comps[0].z([text])[0] + comps[1].z([text])[0] + comps[2].z([text])[0]
    assert np.allclose(o["scores"], want) and o["additivity_error"] < 1e-6
    assert o["k"] == int(want.argmax()) and tuple(o["weights"]) == (3, 1, 1)


def test_label_cache_rebuilt_on_shape_mismatch(tmp_path):
    p, calls = tmp_path / "emb.npy", []

    def compute():
        calls.append(1)
        return np.ones((3, 4))

    np.save(p, np.zeros((5, 4)))  # stale: other label count
    assert live._label_emb(p, 3, compute).shape == (3, 4) and calls == [1] and np.load(p).shape == (3, 4)
    assert live._label_emb(p, 3, compute).shape == (3, 4) and calls == [1]  # good cache: no recompute


def test_score_batch_is_weighted_sum():
    comps = [Stub("a", 1.0), Stub("b", 2.0)]
    tx = ["dump lsass now", "registry run key", "nothing here"]
    S = live.score_batch(comps, tx, weights=(3, 1))
    assert S.shape == (3, L) and np.allclose(S, 3 * comps[0].z(tx) + comps[1].z(tx))
