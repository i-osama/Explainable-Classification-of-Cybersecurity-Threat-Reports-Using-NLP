"""Human study v2 scorer (scripts/score_human_study.py): schema checks and the pre-registered primary rule, on synthetic sheets only."""
import sys, tempfile
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import score_human_study as S


def _key(t):
    k = pd.DataFrame({"item_id": [f"I{i:03d}" for i in range(80)], "test_row": range(80), "condition": ["real"] * 60 + ["control"] * 20, "top1_correct": [True, False] * 40})
    k.to_csv(Path(t) / "key.csv", index=False); return k


def _sheets(t, k, gap, raters=3, seed=0):
    rng = np.random.default_rng(seed); q = np.where(k.condition == "real", 2.5 + gap / 2, 2.5 - gap / 2) + rng.normal(0, 0.5, len(k))
    for r in range(1, raters + 1):
        v = np.clip(np.rint(q + rng.normal(0, 0.3, len(k))), 1, 5).astype(int)
        pd.DataFrame({"item_id": k.item_id, "rating_1_to_5": v, "note": ""}).to_csv(Path(t) / f"rating_sheet_R{r}.csv", index=False)


def test_schema_problems_are_reported_not_dropped():
    with tempfile.TemporaryDirectory() as t:
        k = _key(t); _sheets(t, k, 2.0)
        df = pd.read_csv(Path(t) / "rating_sheet_R1.csv", dtype=str)
        df.loc[0, "rating_1_to_5"] = "7"; df.loc[1, "rating_1_to_5"] = "x"; df = pd.concat([df.iloc[:-1], df.iloc[[2]]])  # invalid, non-number, last missing, duplicate
        df.to_csv(Path(t) / "rating_sheet_R1.csv", index=False)
        key, M, issues = S.load(Path(t) / "key.csv", t); text = " | ".join(issues)
        assert "more than once" in text and "I079 missing" in text and "'7'" in text and "'x'" in text
        assert M.loc["R1"].isna().sum() == 3            # 7, x and the missing item; nothing imputed


def test_primary_rule_needs_a_full_point_and_an_interval_above_zero():
    for gap, met in ((2.0, True), (0.0, False)):
        with tempfile.TemporaryDirectory() as t:
            k = _key(t); _sheets(t, k, gap)
            out, raters, items = S.analyse(*S.load(Path(t) / "key.csv", t))
            assert out["primary"]["rule_met"] is met and out["n_raters"] == 3 and len(raters) == 3 and len(items) == 80
            assert "alpha_ordinal" in out["secondary"] and out["status"] == "OK"


def test_fewer_than_three_raters_is_flagged():
    with tempfile.TemporaryDirectory() as t:
        k = _key(t); _sheets(t, k, 2.0, raters=2)
        out, _, _ = S.analyse(*S.load(Path(t) / "key.csv", t))
        assert out["status"].startswith("FEWER THAN 3")
