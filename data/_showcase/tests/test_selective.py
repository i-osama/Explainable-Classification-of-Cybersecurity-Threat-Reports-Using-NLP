"""Q1 wave 2 Task 4: selective prediction / risk-coverage, prereg 19."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap import selective as sel
from ttpmap.fusion import LeakageError


def test_margin_basic():
    assert sel.margin(np.array([[3., 1., 2.]])).tolist() == [1.0]
    m = sel.margin(np.array([[np.nan, 2., np.nan]]))          # one finite label: maximally confident
    assert m[0] == np.inf


def test_aurc_known():
    conf = np.array([3., 2., 1.]); ok = np.array([1, 0, 1], bool)
    cov, risk = sel.risk_coverage(conf, ok)
    assert np.allclose(cov, [1 / 3, 2 / 3, 1]) and np.allclose(risk, [0, 0.5, 1 / 3])
    assert abs(sel.aurc(conf, ok) - (0 + 0.5 + 1 / 3) / 3) < 1e-12


def test_aurc_perfect_ranking():
    conf = np.array([5., 4., 3., 2.]); ok = np.array([1, 1, 0, 0], bool)
    assert abs(sel.eaurc(conf, ok)) < 1e-12


def test_ties_deterministic():
    conf = np.array([1., 1., 1., 0.]); ok = np.array([0, 1, 1, 0], bool)
    a = sel.risk_coverage(conf, ok); b = sel.risk_coverage(conf.copy(), ok.copy())
    assert np.array_equal(a[1], b[1])
    assert np.allclose(a[1], [1.0, 0.5, 1 / 3, 0.5])        # stable order keeps index order inside the tie


def test_leakage():
    try:
        sel.dev_threshold_for_coverage(np.arange(10.), 0.8, split="test")
    except LeakageError:
        return
    raise AssertionError("split='test' accepted")


def test_nan_confidence_least_confident():
    assert sel.margin(np.array([[np.nan, np.nan]]))[0] == -np.inf
    conf = np.array([np.nan, 2., 1., np.nan]); t = sel.dev_threshold_for_coverage(conf, 0.5, split="dev")
    assert t == 1.0
    cov, risk = sel.risk_coverage(conf, np.array([0, 1, 1, 0], bool))
    assert risk[1] == 0.0                                          # the two finite rows come first


def test_dev_threshold_coverage():
    conf = np.arange(100.)                                     # keep conf >= t: 80 of 100 at target 0.8
    t = sel.dev_threshold_for_coverage(conf, 0.8, split="dev")
    assert (conf >= t).sum() == 80
