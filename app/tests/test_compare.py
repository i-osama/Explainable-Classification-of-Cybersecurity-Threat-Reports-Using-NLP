"""Compare mode: helpers (prompt, id parsing, ranking, Ollama call) and the UI path on the fake thesis root."""
import importlib.util
import json
import os
from pathlib import Path

import numpy as np
import pytest
from streamlit.testing.v1 import AppTest

import compare
from fake_root import build

APP = str(Path(__file__).parent.parent / "app.py")
SEALED = Path(__file__).resolve().parents[2] / "_showcase" / "src" / "ttpmap" / "llm.py"


@pytest.mark.skipif(not SEALED.exists(), reason="thesis source tree not here")
def test_prompt_and_parser_are_the_sealed_ones():
    spec = importlib.util.spec_from_file_location("sealed_llm", SEALED)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    assert compare.CLOSED_TEMPLATE == m.CLOSED_TEMPLATE and compare.OPTIONS == m.OPTIONS
    cat = [("T1057", "Process Discovery"), ("T1003", "OS Credential Dumping")]
    assert compare.closed_prompt("x y", cat) == m.closed_prompt("x y", cat)
    allowed = {"T1057", "T1003", "T1003.001"}
    for s in ("T1057, T1003", "<think>T1003</think> t1057 / T 1003.001", "none", "T1003.001 T1003.001 T9999"):
        assert compare.parse_ids(s, allowed) == m.parse_ids(s, allowed)


class FakeR:
    def __init__(self, nums, cis):
        self.numbers, self.cis = nums, cis

    def num(self, i):
        v = self.numbers.get(i)
        return f"[PENDING: {i}]" if v is None else str(v)


def test_ranking_best_first_and_skips_missing_numbers():
    R = FakeR({"B13a": "0.803", "L1.rr_matcher.p1": "0.597", "L1.closed.p1": "0.257", "L1.closed.sec": "5.8"},
              {"B13a": [0.77, 0.83]})
    rows = compare.ranking(R)
    assert [r["id"] for r in rows] == ["B13a", "L1.rr_matcher.p1", "L1.closed.p1"]  # rr_zero missing -> left out
    assert [r["rank"] for r in rows] == ["Most accurate", "Less accurate", "Least accurate"]
    assert rows[0]["ci"] == [0.77, 0.83] and rows[2]["seconds"] == "5.8"


def test_ask_llm_sends_placement_and_parses():
    sent = {}

    def post(body):
        sent.update(json.loads(body))
        return {"response": "T1057, T1003", "load_duration": 2e9, "eval_duration": 1e9, "prompt_eval_count": 12}

    a = compare.ask_llm("p", "http://localhost:11434", 0, {"T1057", "T1003"}, post=post)
    assert sent["options"]["num_gpu"] == 0 and sent["options"]["temperature"] == 0 and sent["model"] == "qwen2.5:7b"
    assert a["ids"] == ["T1057", "T1003"] and a["load_s"] == 2.0 and a["prompt_tokens"] == 12


def test_host_avoids_localhost():
    assert compare.host("http://localhost:11434/") == "http://127.0.0.1:11434"


class Stub:
    mask = "<mask>"

    def __init__(self, name):
        self.name = name

    def z(self, tx):
        out = np.zeros((len(tx), 733))
        out[:, 5] = 1.0
        return out


def test_compare_mode_renders_and_runs_cpu_column(tmp_path, monkeypatch):
    import live
    root = build(tmp_path / "root")
    monkeypatch.setitem(os.environ, "TTPMAP_ROOT", str(root))
    monkeypatch.setitem(os.environ, "TTPMAP_DEMO", "0")
    monkeypatch.setattr(live, "load", lambda art, full=False: [Stub(n) for n in ("matcher", "svm", "roberta", "secbert")])
    at = AppTest.from_file(APP, default_timeout=120).run()
    at.sidebar.radio[0].set_value("Compare: GPU, CPU, local AI").run()
    assert not at.exception, [e.value for e in at.exception]
    heads = [m.value for m in at.markdown]
    for h in ("#### 1.", "#### 2.", "#### 3."):
        assert any(v.startswith(h) for v in heads), h
    assert any("changes the speed, not the answer" in i.value for i in at.info)
    next(b for b in at.button if b.label == "Run on this PC's CPU").click().run()
    assert not at.exception, [e.value for e in at.exception]
    assert any("s on CPU. Top-3" in c.value for c in at.caption)
