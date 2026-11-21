"""Fusion, leakage guard, statistics, explanation units and schema tests (no project data needed)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import numpy as np
from ttpmap import fusion as F, stats as ST, explain as E, schema as SC


def _raises(exc, fn, *a, **k):
    try:
        fn(*a, **k)
    except exc:
        return True
    return False


def test_grid_sizes():
    assert len(F.coarse_grid()) == 255 and len(F.wide_grid()) == 1711
    assert (3, 1, 1, 1) in F.coarse_grid() and (4, 1, 1, 1) in F.wide_grid()


def test_zrow_unknown_labels_are_neutral():
    x = np.array([[1.0, 2.0, 3.0, np.nan]]); z = F.zrow(x)
    assert z[0, 3] == 0.0 and abs(z[0, :3].mean()) < 1e-9 and abs(z[0, :3].std() - 1) < 1e-6


def _toy():
    rng = np.random.default_rng(0); Y = np.zeros((20, 6), bool); Y[np.arange(20), rng.integers(0, 6, 20)] = True
    Z = {n: rng.standard_normal((20, 6)) + (2.0 * Y if n == "matcher" else 0) for n in F.ORDER}
    return Z, Y


def test_leakage_guard_split_name():
    Z, Y = _toy()
    assert _raises(F.LeakageError, F.select_weights, Z, Y, F.coarse_grid(), split="test")
    assert _raises(F.LeakageError, F.select_threshold, Z["svm"], Y, [0.0, 0.5], split="test")


def test_leakage_guard_test_ids():
    Z, Y = _toy(); ids = [f"dev-{i:04d}" for i in range(19)] + ["test-0007"]
    assert _raises(F.LeakageError, F.select_weights, Z, Y, F.coarse_grid(), split="dev", sentence_ids=ids, forbidden_ids=["test-0007", "test-0008"])
    w, key = F.select_weights(Z, Y, F.coarse_grid(), split="dev", sentence_ids=ids[:19], forbidden_ids=["test-0007"])
    assert w[0] > 0, "the informative component must receive weight"


def test_selection_is_deterministic():
    Z, Y = _toy()
    assert F.select_weights(Z, Y, F.wide_grid(), split="dev") == F.select_weights(Z, Y, F.wide_grid(), split="dev")


def test_holm_textbook_example():
    # p = .01 .04 .03 .005 -> sorted .005 .01 .03 .04 -> x4 .02, x3 .03, x2 .06, x1 .04 -> monotone: .02 .03 .06 .06
    assert np.allclose(ST.holm([0.01, 0.04, 0.03, 0.005]), [0.03, 0.06, 0.06, 0.02])


def test_mcnemar_counts_and_symmetry():
    a = np.array([1, 1, 1, 0, 0, 1]); b = np.array([1, 0, 0, 0, 1, 0])
    m = ST.mcnemar_exact(a, b)
    assert (m["b"], m["c"]) == (3, 1) and abs(m["p"] - 0.625) < 1e-12        # 2 * P(X >= 3 | n = 4, p = .5) = 2 * 5/16
    assert abs(ST.mcnemar_exact(b, a)["p"] - m["p"]) < 1e-12


def test_bootstrap_is_seeded():
    x = np.arange(50) % 2
    assert ST.bootstrap_ci(x) == ST.bootstrap_ci(x)
    d = ST.paired_bootstrap(np.ones(30), np.zeros(30))
    assert d["delta"] == 1.0 and d["lo"] == 1.0 and d["hi"] == 1.0


def test_wilson_known_value():
    lo, hi = ST.wilson(83, 100)
    assert abs(lo - 0.7445) < 5e-4 and abs(hi - 0.8908) < 5e-4


def test_units_tile_text_and_mask():
    t = "can  enumerate Registry keys."; parts = E.split_units(t)
    assert "".join("".join(p) for p in parts) == t and len(parts) == 4
    assert E.mask_words(parts, {1}, "<mask>") == "can  <mask> Registry keys."
    assert E.keep_only(parts, {1}, "<mask>") == "<mask>  enumerate <mask> <mask>"
    assert E.remove_words(parts, {3}, t) == "can  enumerate Registry"
    assert E.order_by_attribution([0.1, 0.9, -0.2, 0.9]) == [1, 3, 0, 2]


def test_schema_accepts_and_rejects():
    ok = {"id": "T1059.001", "name": "PowerShell", "tactics": ["execution"], "parent_id": "T1059", "is_sub": True, "train_support": 3, "dev_support": 0, "test_support": 1}
    SC.Technique.model_validate(ok)
    assert _raises(Exception, SC.Technique.model_validate, {**ok, "parent_id": None})
    assert _raises(Exception, SC.Technique.model_validate, {**ok, "id": "1059"})
    c = {"id": "B13a", "label": "x", "value": 0.803, "display": "0.803", "ci": [0.77, 0.83], "definition": "d", "source_file": "f", "script": "s", "status": "RECOMPUTED", "thesis_section": "5"}
    SC.Claim.model_validate(c)
    assert _raises(Exception, SC.Claim.model_validate, {**c, "ci": [0.9, 0.1]})
    assert _raises(Exception, SC.Claim.model_validate, {**c, "status": "TODO-COLAB"})        # a TODO claim must not carry a value
    assert _raises(Exception, SC.Sentence.model_validate, {"id": "test-0001", "split": "test", "text_sha256": "0" * 64, "n_words": 3, "labels": ["T1059", "T1059"]})
