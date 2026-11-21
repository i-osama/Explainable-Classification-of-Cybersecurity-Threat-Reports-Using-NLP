import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_intervals as CI

CLAIMS = [{"id": "C3", "value": 0.013793, "ci": [-0.013793, 0.041379]},
          {"id": "C4", "value": 0.001379, "ci": [-0.023448, 0.024828]},
          {"id": "C2.mrr", "value": 0.019, "ci": [0.0031, 0.0362]},
          {"id": "X", "value": 0.5, "ci": None}]


def test_finds_three_phrasings():
    t = ("RoBERTa minus SVM is +0.014 in P@1 (−0.015 to +0.040) and the gap is +0.014 [−0.014, +0.041]. "
         "The difference is +0.001 with a 95% interval of −0.023 to +0.025, and 0.019 in MRR@3 (0.003 to 0.037 [confirm]).")
    got = CI.find(t)
    assert [(g["point"], g["lo"], g["hi"]) for g in got] == [("+0.014", "−0.015", "+0.040"), ("+0.014", "−0.014", "+0.041"),
                                                              ("+0.001", "−0.023", "+0.025"), ("0.019", "0.003", "0.037")]


def test_point_does_not_jump_over_other_numbers():
    got = CI.find("MRR@3 (−0.018 to +0.020), and RoBERTa minus SecBERT is +0.001 (−0.022 to +0.025)")
    assert [(g["point"], g["lo"]) for g in got] == [("+0.001", "−0.022")]


def test_compare_with_registry():
    rows = CI.check([{"idx": 7, "text": "+0.014 [−0.015, +0.040] and +0.014 [−0.014, +0.041] and +0.001 (−0.023 to +0.025) "
                                         "and 0.019 (0.003 to 0.037) and 0.777 [0.70, 0.80]"}], CLAIMS)
    st = [(r["point"], r["status"], r["ids"]) for r in rows]
    assert st == [("+0.014", "DIFFERS", "C3"), ("+0.014", "OK", "C3"), ("+0.001", "OK", "C4"), ("0.019", "DIFFERS", "C2.mrr"), ("0.777", "NO CLAIM", "")]
    assert rows[0]["registry"] == "[-0.014, +0.041]" and rows[0]["para"] == 7


def test_range_that_does_not_contain_the_point_is_listed_not_dropped():
    rows = CI.check([{"idx": 1, "text": "a gap of 0.006 [0.790, 0.796] between runs"}], CLAIMS)
    assert [r["status"] for r in rows] == ["POINT OUTSIDE"]


def test_ci_wording_and_more_separators():
    got = lambda t: [(g["point"], g["lo"], g["hi"]) for g in CI.find(t)]
    assert got("P@1 0.612 (95% CI 0.577 to 0.647)") == [("0.612", "0.577", "0.647")]
    assert got("0.612 (95% CI: 0.577, 0.647)") == [("0.612", "0.577", "0.647")]
    assert got("0.612 [0.577-0.647]") == [("0.612", "0.577", "0.647")]
    assert got("0.612 [0.577; 0.647]") == [("0.612", "0.577", "0.647")]
    assert got("+0.014 [−0.015, +0.040]") == [("+0.014", "−0.015", "+0.040")]


def test_rounding_is_half_up_like_authors():
    claims = [{"id": "H", "value": 0.125, "ci": [0.0125, 2.675]}]
    assert CI.check([{"idx": 1, "text": "0.13 [0.01, 2.68]"}], claims)[0]["status"] == "OK"


def test_differs_reports_nearest_claim_not_first():
    claims = [{"id": "C1.mrr", "value": 0.019, "ci": [0.010, 0.029]}] + CLAIMS
    r = CI.check([{"idx": 2, "text": "0.019 (0.003 to 0.037)"}], claims)[0]
    assert r["status"] == "DIFFERS" and r["ids"].startswith("C2.mrr") and r["registry"] == "[+0.003, +0.036]"
    r = CI.check([{"idx": 3, "text": "+0.003 (−0.022 to +0.026)"}], claims)[0]   # point itself differs: nearest claim overall
    assert r["status"] == "DIFFERS" and r["ids"].startswith("C4")


def test_seed_value_lists_are_not_intervals():
    """Draft v2.2 p610/p637: 'mean ± sd (seed values)' with three numbers is a seed list, not an interval."""
    for t in ("P@1 0.796 ± 0.006 (0.790, 0.796, 0.803)", "and 0.796 ± 0.006 (0.790, 0.796 and 0.803) when"):
        rows = CI.check([{"idx": 1, "text": t}], CLAIMS)
        assert [r["status"] for r in rows] == ["SEED LIST"], rows
