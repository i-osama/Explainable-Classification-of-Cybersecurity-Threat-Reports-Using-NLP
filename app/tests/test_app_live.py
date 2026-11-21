"""Live full-fusion UI path on the fake thesis root, with stub models (no torch): example button -> Analyse -> panels."""
import os
from pathlib import Path

import numpy as np
import pytest
from streamlit.testing.v1 import AppTest

from fake_root import build

pytest.importorskip("shap")
APP = str(Path(__file__).parent.parent / "app.py")


class Stub:
    mask = "<mask>"

    def __init__(self, name):
        self.name = name

    def z(self, tx):
        out = np.zeros((len(tx), 733))
        for i, t in enumerate(tx):
            out[i, 3] = sum(w in t.lower() for w in ("tasklist", "processes"))
        return out

    def _emb(self, tx, max_len=128):  # matcher sentence embedding: bag of words
        import zlib
        E = np.zeros((len(list(tx)), 64))
        for i, t in enumerate(tx):
            for w in t.lower().split():
                E[i, zlib.crc32(w.encode()) % 64] += 1.0
        return E / np.maximum(np.linalg.norm(E, axis=1, keepdims=True), 1e-9)


def test_live_full_fusion_example_to_panels(tmp_path, monkeypatch):
    import live
    root = build(tmp_path / "root")
    monkeypatch.setitem(os.environ, "TTPMAP_ROOT", str(root))
    monkeypatch.setitem(os.environ, "TTPMAP_DEMO", "0")
    monkeypatch.setattr(live, "load", lambda art, full=False: [Stub(n) for n in (("matcher", "svm", "roberta", "secbert") if full else ("svm", "roberta", "secbert"))])
    at = AppTest.from_file(APP, default_timeout=120).run()
    assert not at.exception, [e.value for e in at.exception]
    at.sidebar.radio[0].set_value("Try a sentence").run()
    at.button[0].click().run()  # first example: "Process listing"
    assert "tasklist" in at.text_area[0].value
    next(b for b in at.button if b.label == "Analyse").click().run()
    assert not at.exception, [e.value for e in at.exception]
    assert {"Predicted techniques", "Why: SHAP words"} <= {s.value for s in at.subheader}
    assert any("Full fusion (3,1,1,1), seed 42, live run." in c.value for c in at.caption)
    assert any("matcher" in c.value and "Latency" in c.value for c in at.caption)


def _live_app(tmp_path, monkeypatch):
    import live
    root = build(tmp_path / "root")
    monkeypatch.setitem(os.environ, "TTPMAP_ROOT", str(root))
    monkeypatch.setitem(os.environ, "TTPMAP_DEMO", "0")
    monkeypatch.setattr(live, "load", lambda art, full=False: [Stub(n) for n in (("matcher", "svm", "roberta", "secbert") if full else ("svm", "roberta", "secbert"))])
    at = AppTest.from_file(APP, default_timeout=120).run()
    at.sidebar.radio[0].set_value("Try a sentence").run()
    return at


def test_live_refuses_long_text_with_reason(tmp_path, monkeypatch):
    at = _live_app(tmp_path, monkeypatch)
    at.text_area[0].input(" ".join(["tasklist"] * 45)).run()
    next(b for b in at.button if b.label == "Analyse").click().run()
    assert not at.exception and not any(s.value == "Why: SHAP words" for s in at.subheader)
    assert any("40 words" in w.value for w in at.warning)


def test_analyse_button_is_enabled_before_text_commits(tmp_path, monkeypatch):
    at = _live_app(tmp_path, monkeypatch)
    b = next(b for b in at.button if b.label == "Analyse")
    assert not b.disabled  # a disabled button swallows the first click after typing in the browser
    b.click().run()
    assert any("Type or paste" in w.value for w in at.warning)


def _mode(tmp_path, monkeypatch, label):
    at = _live_app(tmp_path, monkeypatch)
    at.sidebar.radio[0].set_value(label).run()
    assert not at.exception, [e.value for e in at.exception]
    return at


def test_report_mode_finds_techniques_then_explains_one(tmp_path, monkeypatch):
    at = _mode(tmp_path, monkeypatch, "Check a whole report")
    at.text_area(key="report").input("The malware runs tasklist to list processes. It then sends them to the server.\nok").run()
    next(b for b in at.button if b.label == "Find techniques").click().run()
    assert not at.exception, [e.value for e in at.exception]
    assert len(at.dataframe) == 1 and len(at.dataframe[0].value) == 2  # "ok" is dropped (under 3 words)
    next(b for b in at.button if b.label == "Explain this sentence").click().run()
    assert "Why: SHAP words" in {s.value for s in at.subheader}


def test_train_reports_unknown_ids_and_asks_for_test_sentences(tmp_path, monkeypatch):
    at = _mode(tmp_path, monkeypatch, "Train and check")
    lines = "\n".join(f"T1390: zebrafoo implant variant {i} beacons home" for i in range(3)) + "\nT9999: an unknown technique id"
    at.text_area(key="teach").input(lines).run()
    next(b for b in at.button if b.label == "Train and check").click().run()
    assert not at.exception, [e.value for e in at.exception]
    assert any("T9999" in e.value for e in at.error) and any("Add test sentences" in w.value for w in at.warning)
