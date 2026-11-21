"""Tests that need the project data: split overlap, leakage of ids, determinism, regression of headline numbers.
Skipped (reported as SKIP) when the dataset folder is absent, e.g. in a public clone."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import numpy as np
from ttpmap import DATA, CLS_DIR, MATCH_DIR, SEEDS

HAVE = (DATA / "tram_test.tsv").exists() and (CLS_DIR / "roberta_pw_s42" / "test_probs.npy").exists() and (MATCH_DIR / "ft20_s42" / "test_scores.npy").exists()
TOL = 0.001


def _space():
    from ttpmap.data import build_space
    return build_space()


def test_split_sizes_and_label_space():
    if not HAVE: return "SKIP"
    S = _space()
    assert (len(S.train), len(S.dev), len(S.test)) == (3468, 604, 725)
    assert S.L == 733 and int(S.seen.sum()) == 180
    assert int((S.Y["test"].sum(0) > 0).sum()) == 127 and int(((S.Y["test"].sum(0) > 0) & S.seen).sum()) == 117


def test_split_overlap_is_small_and_known():
    if not HAVE: return "SKIP"
    from ttpmap.data import norm_text
    S = _space(); n = {k: set(map(norm_text, getattr(S, k)["text"])) for k in ("train", "dev", "test")}
    assert len(n["train"] & n["test"]) == 1, "exactly one normalised test sentence is also in train"
    assert len(n["train"] & n["dev"]) == 0 and len(n["dev"] & n["test"]) == 0


def test_tuning_never_sees_test_ids():
    if not HAVE: return "SKIP"
    from ttpmap.fusion import components, select_weights, coarse_grid, LeakageError
    S = _space(); Zd = components(S, "dev", "nb_seed", 42)
    dev_ids = [f"dev-{i:04d}" for i in range(len(S.dev))]; test_ids = [f"test-{i:04d}" for i in range(len(S.test))]
    w, _ = select_weights(Zd, S.Y["dev"], coarse_grid(), split="dev", sentence_ids=dev_ids, forbidden_ids=test_ids)
    assert w == (3, 1, 1, 1), "dev winner of the 255-setting grid"
    try:
        select_weights(components(S, "test", "nb_seed", 42), S.Y["test"], coarse_grid(), split="dev", sentence_ids=test_ids, forbidden_ids=test_ids)
        raise AssertionError("test ids were accepted by a tuning function")
    except LeakageError:
        pass


def test_wide_grid_prefers_4111():
    if not HAVE: return "SKIP"
    from ttpmap.fusion import components, select_weights, wide_grid
    S = _space(); w, _ = select_weights(components(S, "dev", "nb_seed", 42), S.Y["dev"], wide_grid(), split="dev")
    assert w == (4, 1, 1, 1)


def test_headline_numbers_regression():
    if not HAVE: return "SKIP"
    from ttpmap.fusion import components, fuse, rank_space
    from ttpmap.metrics import hit_at_1, rr_at_k
    S = _space(); Y = S.Y["test"]; Z = components(S, "test", "avg")
    exp = {"fusion_p1": (hit_at_1(fuse(Z, (3, 1, 1, 1)), Y).mean(), 0.803), "fusion_mrr3": (rr_at_k(fuse(Z, (3, 1, 1, 1)), Y).mean(), 0.856),
           "classifiers_only_p1": (hit_at_1(fuse(Z, (0, 1, 1, 1)), Y).mean(), 0.774), "matcher_ens_p1": (hit_at_1(Z["matcher"], Y).mean(), 0.777),
           "svm_p1": (hit_at_1(rank_space(S.svm_raw["test"], S.seen_idx, S.L), Y).mean(), 0.742), "zeroshot_p1": (hit_at_1(S.matcher_zero_test, Y).mean(), 0.228)}
    paired = [hit_at_1(fuse(components(S, "test", "paired", s), (3, 1, 1, 1)), Y).mean() for s in SEEDS]
    exp["fusion_paired_mean"] = (float(np.mean(paired)), 0.796); exp["fusion_paired_sd"] = (float(np.std(paired, ddof=1)), 0.006)
    nb = [hit_at_1(fuse(components(S, "test", "nb_seed", s), (3, 1, 1, 1)), Y).mean() for s in SEEDS]
    exp["fusion_nb_mean"] = (float(np.mean(nb)), 0.800)
    bad = {k: v for k, v in exp.items() if abs(v[0] - v[1]) > TOL}
    assert not bad, f"outside {TOL}: {bad}"


def test_stored_classifier_metrics_reproduce():
    if not HAVE: return "SKIP"
    from ttpmap.metrics import apply_threshold, f1_scores
    S = _space(); Y = S.Y["test"]
    for tag in ("roberta", "secbert"):
        for s in SEEDS:
            m = S.cls_meta[tag, s]; cols = S.cls_cols[tag, s]
            P = np.zeros(Y.shape, bool); P[:, cols] = apply_threshold(S.cls_raw[tag, s]["test"].copy(), m["threshold"])
            f = f1_scores(P, Y, S.seen, "notebook")
            assert abs(f["micro_f1"] - m["test"]["micro_f1"]) < 1e-9 and abs(f["macro_f1"] - m["test"]["macro_f1"]) < 1e-9, (tag, s)


def test_fusion_is_deterministic():
    if not HAVE: return "SKIP"
    from ttpmap.fusion import components, fuse
    S = _space()
    a = fuse(components(S, "test", "avg"), (3, 1, 1, 1)); b = fuse(components(S, "test", "avg"), (3, 1, 1, 1))
    assert np.array_equal(a, b)
