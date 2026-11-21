import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "usability"))
import score_sus as S  # noqa: E402


def test_sus_score_bounds_and_neutral():
    assert S.sus([3] * 10) == 50.0
    assert S.sus([5, 1] * 5) == 100.0       # odd items fully agree, even items fully disagree
    assert S.sus([1, 5] * 5) == 0.0


def test_sus_rejects_bad_answers():
    for bad in ([3] * 9, [3] * 9 + [6], [3] * 9 + [0], [3] * 9 + [None]):
        with pytest.raises(ValueError):
            S.sus(bad)


def test_score_file(tmp_path):
    p = tmp_path / "r.csv"
    p.write_text("participant,q1,q2,q3,q4,q5,q6,q7,q8,q9,q10\nP1,3,3,3,3,3,3,3,3,3,3\nP2,5,1,5,1,5,1,5,1,5,1\n", encoding="utf-8")
    rows, summary = S.score_file(p)
    assert [r["sus"] for r in rows] == [50.0, 100.0]
    assert summary == {"n": 2, "mean": 75.0, "sd": 35.36, "min": 50.0, "max": 100.0}
