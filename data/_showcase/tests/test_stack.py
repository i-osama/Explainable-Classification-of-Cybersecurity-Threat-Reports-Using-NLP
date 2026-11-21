"""Q1 plan Task 4: stacked (learned) fusion, prereg 15."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap import stack
from ttpmap.fusion import LeakageError
from ttpmap.metrics import hit_at_1


def _toy(n=40, L=6, seed=0):
    rng = np.random.default_rng(seed); X = rng.normal(0, 0.3, (n, L, stack.N_FEATURES)); Y = np.zeros((n, L), bool)
    for i in range(n):
        j = rng.integers(L); X[i, j, 0] = 3.0; Y[i, j] = True
    return X, Y


def test_fit_stacker_refuses_test_split():
    X, Y = _toy()
    try:
        stack.fit_stacker(X, Y, split="test")
    except LeakageError:
        return
    raise AssertionError("fit_stacker accepted split='test'")


def test_pair_features_shape_and_unseen_zero():
    rng = np.random.default_rng(1)
    Z = {k: rng.normal(size=(2, 5)) for k in ("matcher", "svm", "roberta", "secbert")}
    X = stack.pair_features(Z, np.array([0, 1, 2, 0, 5]))
    assert X.shape == (2, 5, 7)
    assert (X[:, 0, 5] == 0).all() and (X[:, 1, 5] == 1).all()                 # seen flag
    assert np.allclose(X[:, 4, 4], np.log1p(5))                                  # log1p(train_count)
    r = X[0, :, 6]; assert np.isclose(r[np.argmax(Z["matcher"][0])], 0.0)      # log(rank 1) = 0 for the matcher's top label


def test_stacker_recovers_planted_signal():
    X, Y = _toy()
    m = stack.fit_stacker(X, Y, split="dev", C_grid=(0.1, 1.0), folds=4)
    Xt, Yt = _toy(seed=5)
    assert hit_at_1(m.score(Xt), Yt).mean() == 1.0 and m.C in (0.1, 1.0)
