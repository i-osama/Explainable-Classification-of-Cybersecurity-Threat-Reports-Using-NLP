"""Plain-language UI: Start page (default), mode buttons, the one-line answer in plain words, every mode renders."""
import os
from pathlib import Path

import numpy as np
from streamlit.testing.v1 import AppTest

import home
from fake_root import build

APP = str(Path(__file__).parent.parent / "app.py")


class Stub:
    mask = "<mask>"

    def __init__(self, name):
        self.name = name

    def z(self, tx):
        out = np.zeros((len(tx), 733))
        out[:, 3] = 1.0
        return out

    def _emb(self, tx, max_len=128):  # matcher sentence embedding (train-and-check memory)
        E = np.zeros((len(list(tx)), 8)); E[:, 0] = 1.0
        return E


def app(tmp_path, monkeypatch):
    import live
    root = build(tmp_path / "root")
    monkeypatch.setitem(os.environ, "TTPMAP_ROOT", str(root))
    monkeypatch.setitem(os.environ, "TTPMAP_DEMO", "0")
    monkeypatch.setattr(live, "load", lambda art, full=False: [Stub(n) for n in (("matcher", "svm", "roberta", "secbert") if full else ("svm", "roberta", "secbert"))])
    at = AppTest.from_file(APP, default_timeout=120).run()
    assert not at.exception, [e.value for e in at.exception]
    return at


def test_start_page_is_default_and_shows_registry_numbers(tmp_path, monkeypatch):
    at = app(tmp_path, monkeypatch)
    assert at.sidebar.radio[0].value == "Start here"
    text = " ".join(m.value for m in at.markdown)
    assert "80 of 100" in text  # B13a = 0.803 in the fixture registry
    assert "What is this?" in [s.value for s in at.subheader] and at.expander  # glossary


def test_start_buttons_switch_mode(tmp_path, monkeypatch):
    at = app(tmp_path, monkeypatch)
    next(b for b in at.button if b.label == "Try a sentence").click().run()
    assert not at.exception and at.sidebar.radio[0].value == "Try a sentence"
    assert at.text_area(key="text") is not None


def test_plain_line_tiers():
    class R:
        names = {"T1082": "System Information Discovery"}
        desc = {"T1082": "An adversary may attempt to get detailed information about the operating system and hardware. More text here."}

        def name(self, lab):
            return f"{lab} {self.names[lab]}"
    r = R()
    s0, s1, s2 = (home.plain_line(r, "T1082", t) for t in (0, 1, 2))
    assert "T1082 System Information Discovery" in s0 and "operating system and hardware" in s0 and "More text" not in s0
    assert s0.endswith("very sure.") and s1.endswith("fairly sure.") and "a person should check" in s2


def test_every_mode_renders_without_error(tmp_path, monkeypatch):
    at = app(tmp_path, monkeypatch)
    for m in at.sidebar.radio[0].options:
        at.sidebar.radio[0].set_value(m).run()
        assert not at.exception, (m, [e.value for e in at.exception])
