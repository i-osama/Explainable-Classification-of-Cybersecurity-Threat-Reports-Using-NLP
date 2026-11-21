"""Train and check: example memory, before/after report on new sentences, no-damage check, verdict, and the UI flow."""
import json
import os
import zlib
from pathlib import Path

import numpy as np
import pytest
from streamlit.testing.v1 import AppTest

import core
import teach
from fake_root import build

APP = str(Path(__file__).parent.parent / "app.py")


def test_memory_fires_only_above_t():
    m = teach.Memory(emb=np.array([[1.0, 0.0], [0.0, 1.0]]), labels=[["T1"], ["T2"]], texts=["a", "b"], t=0.9)
    out = m.lookup(np.array([[1.0, 0.0], [0.6, 0.8], [0.95, 0.31225]]))
    assert out[0][:1] == (["T1"],) and out[0][2] == 0 and out[1] is None
    assert out[2][0] == ["T1"] and out[2][1] == pytest.approx(0.95, abs=1e-3)


def test_check_lines_equal_to_training_lines_are_excluded():
    train = [("The tool deletes shadow copies.", ["T1490"])]
    check = [("the tool  deletes shadow copies.", ["T1490"]), ("Backups were wiped by the malware.", ["T1490"])]
    kept, msgs = teach.split_check(train, check)
    assert kept == [check[1]] and any("identical to a training line" in m for m in msgs)


def test_check_report_counts():
    rep = teach.check_report([{"top": "T1"}, {"top": "T9"}], [{"top": "T1"}, {"top": "T2"}], [["T1"], ["T2"]])
    assert rep == {"n": 2, "right_before": 1, "right_after": 2}


def test_verdict_rules():
    ok, msg = teach.verdict({"n": 3, "right_after": 3}, {"n": 4, "right_before": 0, "right_after": 4}, 0.800, 0.801)
    assert ok and msg.startswith("Training worked")
    ok, msg = teach.verdict({"n": 3, "right_after": 3}, {"n": 4, "right_before": 2, "right_after": 2}, 0.800, 0.800)
    assert not ok and "did not change" in msg
    ok, msg = teach.verdict({"n": 3, "right_after": 3}, {"n": 4, "right_before": 0, "right_after": 4}, 0.800, 0.780)
    assert not ok and "made the thesis sentences worse" in msg
    ok, msg = teach.verdict({"n": 3, "right_after": 3}, {"n": 0, "right_before": 0, "right_after": 0}, 0.800, 0.800)
    assert not ok and "Add test sentences" in msg


def test_dev_p1_with_memory(tmp_path):
    R = core.load_replay(str(build(tmp_path / "root")))
    E = np.eye(len(R.art["dev"]["texts"]), 4)
    base = teach.dev_p1(R, R.art, None, E)
    never = teach.Memory(emb=np.array([[0.0, 0.0, 0.0, 1.0]]), labels=[["T1999"]], texts=["x"], t=2.0)
    always = teach.Memory(emb=np.ones((1, 4)) / 2, labels=[["T1931"]], texts=["x"], t=-1.0)  # T1931 is never gold in the fake dev set
    assert teach.dev_p1(R, R.art, never, E) == base and 0 < base <= 1
    assert teach.dev_p1(R, R.art, always, E) < base


class Stub:
    mask = "<mask>"

    def __init__(self, name):
        self.name = name

    def z(self, tx):
        out = np.zeros((len(tx), 733))
        out[:, 3] = 1.0
        return out

    def _emb(self, tx, max_len=128):
        """Bag of words: sentences sharing words are close, unrelated ones are not."""
        E = np.zeros((len(list(tx)), 64))
        for i, t in enumerate(tx):
            for w in t.lower().replace(".", " ").split():
                E[i, zlib.crc32(w.encode()) % 64] += 1.0
        return E / np.maximum(np.linalg.norm(E, axis=1, keepdims=True), 1e-9)


def test_train_flow_with_stubs(tmp_path, monkeypatch):
    import live
    root = build(tmp_path / "root")
    (root / "models").mkdir(exist_ok=True)
    (root / "models" / "memory_calib.json").write_text(json.dumps({"t": 0.5, "precision": 0.9, "matches": 50, "dev_n": 604}), encoding="utf-8")
    monkeypatch.setitem(os.environ, "TTPMAP_ROOT", str(root))
    monkeypatch.setitem(os.environ, "TTPMAP_DEMO", "0")
    monkeypatch.setattr(live, "load", lambda art, full=False: [Stub(n) for n in (("matcher", "svm", "roberta", "secbert") if full else ("svm", "roberta", "secbert"))])
    # fake random scores make any SVM refit move fake dev P@1 by about 1 point; the 1-point rule is pinned in test_verdict_rules
    monkeypatch.setattr(teach, "DEV_DROP_MAX", 0.05)
    at = AppTest.from_file(APP, default_timeout=180).run()
    at.sidebar.radio[0].set_value("Train and check").run()
    next(b for b in at.button if b.label == "Load a ready-made example").click().run()
    assert "T1490" in at.text_area(key="teach").value and at.text_area(key="teach_check").value
    next(b for b in at.button if b.label == "Train and check").click().run()
    assert not at.exception, [e.value for e in at.exception]
    assert any(s.value.startswith("Training worked") for s in at.success), [w.value for w in at.warning]
    at.sidebar.radio[0].set_value("Try a sentence").run()
    assert any("custom-trained" in i.value for i in at.info)
    at.sidebar.radio[0].set_value("Train and check").run()
    next(b for b in at.button if b.label.startswith("Undo")).click().run()
    at.sidebar.radio[0].set_value("Try a sentence").run()
    assert not any("custom-trained" in i.value for i in at.info)


def test_choose_t_smallest_with_precision():
    import calibrate_memory as cm
    sims = np.array([0.95, 0.92, 0.91, 0.85, 0.80, 0.70] * 10)
    hits = np.array([1, 1, 1, 1, 0, 0] * 10, bool)
    r = cm.choose_t(sims, hits, target=0.90, min_matches=20)
    assert r["t"] == pytest.approx(0.81) and r["precision"] == 1.0 and r["matches"] == 40
    assert cm.choose_t(sims, np.zeros(60, bool), target=0.9, min_matches=20)["t"] is None


def test_small_bank_pairs_score_one_label_at_a_time():
    import calibrate_memory as cm
    E_tr = np.array([[1, 0], [1, 0], [0, 1], [0, 1], [0, 1]], float)
    Y_tr = np.array([[1, 0], [1, 0], [0, 1], [0, 1], [0, 1]], bool)
    E_dv = np.array([[1, 0], [0.6, 0.8]], float)
    Y_dv = np.array([[1, 0], [1, 0]], bool)
    sims, hits = cm.small_bank_pairs(E_tr, Y_tr, E_dv, Y_dv, k=2, seed=0)
    assert sims.shape == hits.shape == (4,)  # 2 labels with >= 2 examples x 2 dev sentences
    assert sorted(zip(sims.round(2), hits)) == [(0.0, False), (0.6, True), (0.8, False), (1.0, True)]
