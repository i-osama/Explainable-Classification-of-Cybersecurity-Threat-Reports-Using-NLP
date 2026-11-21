import os
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).parent.parent / "app.py")


def _run():
    os.environ["TTPMAP_DEMO"] = "1"
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert not at.exception, [e.value for e in at.exception]
    return at


def test_demo_app_renders_panels():
    at = _run()
    assert any("SYNTHETIC DEMO DATA" in w.value for w in at.warning)
    heads = [s.value for s in at.subheader]
    assert {"Predicted techniques", "Why: SHAP words", "Explanation"} <= set(heads)
    assert any("Conformal set" in m.value for m in at.markdown)
    assert any("Triage" in m.value for m in at.markdown)


def test_demo_app_other_sentences_and_alpha():
    at = _run()
    for pos in (1, 7, 8, 40):  # pos 8 = row 7, where the explained label differs from the fused top-1
        at.sidebar.number_input[0].set_value(pos).run()
        assert not at.exception, (pos, [e.value for e in at.exception])
    at.sidebar.number_input[0].set_value(8).run()
    assert any("do not explain the fused answer" in w.value for w in at.warning)
    at.sidebar.radio[1].set_value(0.2).run()
    assert not at.exception


def test_replay_shows_fusion_shap_when_available():
    at = _run()  # sentence 1 = row 0, which has a stored full-fusion SHAP in the demo data
    assert any("Full fusion SHAP" in c.value for c in at.caption)
    at.sidebar.number_input[0].set_value(2).run()  # row 1: no fusion SHAP -> RoBERTa caption
    assert any("RoBERTa seed 42 only" in c.value for c in at.caption)


def test_header_badge_reads_registry():
    at = _run()
    assert any("First answer right" in m.value and "B13a" in m.value for m in at.markdown)


def test_mode_list_offers_full_fusion():
    at = _run()
    assert "Try a sentence" in at.sidebar.radio[0].options  # live full fusion (3,1,1,1)
