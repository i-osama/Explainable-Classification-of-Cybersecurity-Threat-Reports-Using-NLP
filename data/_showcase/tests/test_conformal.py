"""Q1 wave 2 Task 3: split-conformal prediction sets, prereg 18."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap import conformal as cp
from ttpmap.fusion import LeakageError


def _one_gold(scores_of_gold, L=4):
    n = len(scores_of_gold); S = np.zeros((n, L)); Y = np.zeros((n, L), bool)
    S[:, 0] = scores_of_gold; Y[:, 0] = True
    return S, Y


def test_leakage():
    S, Y = _one_gold([0.5, 0.6])
    for fn in (cp.calibrate_threshold, cp.calibrate_rank):
        try:
            fn(S, Y, 0.1, split="test")
        except LeakageError:
            continue
        raise AssertionError(f"{fn.__name__} accepted split='test'")


def test_exact_quantile():
    S, Y = _one_gold(np.arange(1, 10) / 10)          # gold scores 0.1 .. 0.9, other labels 0
    tau = cp.calibrate_threshold(S, Y, 0.2, split="dev")  # ceil(10 * 0.8) = 8th smallest of -0.9..-0.1 = -0.2
    assert abs(tau - 0.2) < 1e-12
    m = cp.set_metrics(cp.sets_by_threshold(S, tau), Y)
    assert abs(m["coverage_all"] - 8 / 9) < 1e-12


def test_quantile_above_n_gives_full_set():
    S, Y = _one_gold([0.3, 0.5, 0.7])
    tau = cp.calibrate_threshold(S, Y, 0.1, split="dev")  # ceil(4 * 0.9) = 4 > 3
    assert tau == -np.inf
    sets = cp.sets_by_threshold(S, tau)
    assert sets.all()
    assert cp.calibrate_rank(S, Y, 0.1, split="dev") == S.shape[1]


def test_nan_scores_never_in_set():
    S, Y = _one_gold(np.linspace(0.2, 0.9, 20)); S[:, 3] = np.nan
    tau = cp.calibrate_threshold(S, Y, 0.2, split="dev")
    assert np.isfinite(tau)
    sets = cp.sets_by_threshold(S, -np.inf)
    assert not sets[:, 3].any()
    assert not cp.sets_by_rank(S, 4)[:, 3].any()


def test_rank_rule():
    S = np.array([[4., 3, 2, 1]] * 4); Y = np.zeros((4, 4), bool)
    for i in range(4):
        Y[i, i] = True                                # worst gold ranks 1, 2, 3, 4
    assert cp.calibrate_rank(S, Y, 0.25, split="dev") == 4   # ceil(5 * 0.75) = 4
    assert cp.sets_by_rank(S, 2).sum(axis=1).tolist() == [2, 2, 2, 2]


def test_zero_label_rows_dropped():
    S, Y = _one_gold([0.1, 0.2, 0.3, 0.4, 0.5]); Y[0] = False
    tau = cp.calibrate_threshold(S, Y, 0.2, split="dev")  # 4 rows left: ceil(5 * 0.8) = 4th smallest of -0.5..-0.2 = -0.2
    assert abs(tau - 0.2) < 1e-12


def test_coverage_synthetic():
    rng = np.random.default_rng(7); n, L = 2000, 30
    S = rng.normal(size=(n, L)); Y = np.zeros((n, L), bool)
    gold = rng.integers(L, size=n); Y[np.arange(n), gold] = True; S[np.arange(n), gold] += 1.5
    tau = cp.calibrate_threshold(S[:1000], Y[:1000], 0.1, split="dev")
    cov = cp.set_metrics(cp.sets_by_threshold(S[1000:], tau), Y[1000:])["coverage_all"]
    assert 0.87 <= cov <= 0.93, cov
    k = cp.calibrate_rank(S[:1000], Y[:1000], 0.1, split="dev")
    cov_k = cp.set_metrics(cp.sets_by_rank(S[1000:], k), Y[1000:])["coverage_all"]
    assert 0.87 <= cov_k <= 0.93, cov_k
