"""Q1 plan Task 7: LLM baseline helpers (no network)."""
import hashlib, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap import llm

ALLOWED = {"T1059.001", "T1105"}


def test_parse_ids_normalises():
    assert llm.parse_ids("1. t1059/001 2) T1105, T9999", ALLOWED) == ["T1059.001", "T1105"]


def test_parse_ids_dedup_and_k():
    assert llm.parse_ids("T1105, T1105, T1059.001", ALLOWED, k=1) == ["T1105"]


def test_parse_ids_empty_on_prose():
    assert llm.parse_ids("I cannot tell which technique this is.", ALLOWED) == []


def test_parse_ids_ignores_think_block():
    assert llm.parse_ids("<think>maybe T1105</think> T1059.001", ALLOWED) == ["T1059.001"]


def test_prompts_contain_inputs():
    p = llm.closed_prompt("The actor ran a script.", [("T1105", "Ingress Tool Transfer")])
    assert "T1105: Ingress Tool Transfer" in p and p.rstrip().endswith("Output only the ids.") and "The actor ran a script." in p
    q = llm.rr_prompt("The actor ran a script.", [("T1105", "Ingress Tool Transfer", "Adversaries may transfer tools.")])
    assert "T1105: Ingress Tool Transfer: Adversaries may transfer tools." in q


def test_prompts_are_fixed():
    """The template hashes are written into experiments/prereg/17_llm_local.md before the test run; any edit breaks this test."""
    f = Path(__file__).resolve().parents[1] / "experiments" / "prereg" / "17_llm_local.md"
    if not f.exists():
        return "SKIP"
    txt = f.read_text(encoding="utf-8")
    for t in (llm.CLOSED_TEMPLATE, llm.RR_TEMPLATE):
        assert hashlib.sha256(t.encode("utf-8")).hexdigest() in txt
