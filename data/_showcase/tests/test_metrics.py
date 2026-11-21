"""Metric unit tests on hand-computed toy cases, including ties and empty predictions."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import numpy as np
from ttpmap import metrics as M

# 3 sentences, 4 labels. Gold: s0={0}, s1={1,2}, s2={3}
Y = np.array([[1, 0, 0, 0], [0, 1, 1, 0], [0, 0, 0, 1]], dtype=bool)
S = np.array([[0.9, 0.1, 0.0, 0.0],      # s0: top-1 = 0 (hit, rank 1)
              [0.8, 0.1, 0.7, 0.0],      # s1: order 0,2,1 -> first gold at rank 2
              [0.5, 0.4, 0.3, 0.2]])     # s2: gold label 3 is rank 4 -> miss in top 3


def test_p_at_1():
    assert M.hit_at_1(S, Y).tolist() == [1.0, 0.0, 0.0]


def test_mrr_at_3():
    assert np.allclose(M.rr_at_k(S, Y, 3), [1.0, 0.5, 0.0])
    assert abs(M.rr_at_k(S, Y, 3).mean() - 0.5) < 1e-12


def test_p_at_3():
    assert np.allclose(M.precision_at_k(S, Y, 3), [1 / 3, 2 / 3, 0.0])


def test_recall_variants_differ_on_multilabel():
    # micro: gold pairs hit at rank 1 / all gold pairs = 1/4 ; per-sample: mean(1/1, 0/2, 0/1) = 1/3
    assert abs(M.recall_at_k_micro(S, Y, 1) - 0.25) < 1e-12
    assert abs(M.recall_at_k_per_sample(S, Y, 1) - 1 / 3) < 1e-12


def test_ties_broken_by_lower_index():
    s = np.array([[0.5, 0.5, 0.5, 0.5]])
    assert M.rank_topk(s, 4).tolist() == [[0, 1, 2, 3]]
    y = np.array([[0, 1, 0, 0]], dtype=bool)
    assert M.hit_at_1(s, y)[0] == 0.0 and M.rr_at_k(s, y, 3)[0] == 0.5


def test_empty_prediction_gets_argmax():
    s = np.array([[0.1, 0.3, 0.2], [0.9, 0.95, 0.1]])
    P = M.apply_threshold(s.copy(), 0.5)
    assert P.tolist() == [[False, True, False], [True, True, False]]


def test_f1_variants():
    # labels 0,1 seen in training; label 2 unseen. Gold: s0={0}, s1={2}. Prediction: s0={0}, s1={1}.
    y = np.array([[1, 0, 0], [0, 0, 1]], dtype=bool); p = np.array([[1, 0, 0], [0, 1, 0]], dtype=bool); seen = np.array([True, True, False])
    nb = M.f1_scores(p, y, seen, "notebook")      # unseen gold ignored: tp=1 fp=1 fn=0 -> F1 = 2/3 ; macro over label 0 only = 1
    assert abs(nb["micro_f1"] - 2 / 3) < 1e-12 and abs(nb["macro_f1"] - 1.0) < 1e-12 and nb["n_macro_labels"] == 1
    st = M.f1_scores(p, y, seen, "seen_test")     # unseen gold = miss: tp=1 fp=1 fn=1 -> 0.5 ; macro still over label 0
    assert abs(st["micro_f1"] - 0.5) < 1e-12 and abs(st["macro_f1"] - 1.0) < 1e-12
    al = M.f1_scores(p, y, seen, "all_test")      # macro over labels 0 and 2 -> (1 + 0) / 2
    assert abs(al["micro_f1"] - 0.5) < 1e-12 and abs(al["macro_f1"] - 0.5) < 1e-12 and al["n_macro_labels"] == 2


def test_ece_perfectly_calibrated_bin():
    conf = np.array([0.75, 0.75, 0.75, 0.75]); ok = np.array([1, 1, 1, 0.0])
    e, bins = M.ece(conf, ok, 10)
    assert abs(e) < 1e-12 and sum(b["n"] for b in bins) == 4
