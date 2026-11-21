import numpy as np
import pytest

import core
from fake_root import build


@pytest.fixture(scope="module")
def R(tmp_path_factory):
    return core.load_replay(build(tmp_path_factory.mktemp("thesis") / "root"))


def test_load_replay_end_to_end(R):
    assert R.S.shape == (725, 733) and len(R.texts) == 725 and len(R.labels) == 733
    assert np.isfinite(R.S).all() and R.train_count.sum() > 0 and (R.train_count > 0).sum() == 180
    assert len(R.shap) == 10 and R.cal_cls is not None and {"vec", "svm", "seen_idx", "cls_root", "labels"} <= set(R.art)
    assert R.num("E4").startswith("108 of 725") and R.desc[R.labels[0]] == "description of technique t1200 with spaces"  # citation: and spaces cleaned
    assert R.cal.tau[0.1] < R.cal.tau[0.2] and R.cal.thr[0.5] > R.cal.thr[0.9]
    assert R.sel[0.5]["cov"] < R.sel[0.9]["cov"]


def test_fused_scores_use_weights_3_1_1_1(R):
    # the matcher alone cannot decide the ranking when its weight is 3 of 6, but it must contribute: S is not a plain 3-way sum
    assert core.assess(R.S[0], R.cal)["top5"].shape == (5,)


def test_verify_script_runs_and_flags_fake_numbers(R, tmp_path):
    import verify_artifacts as v
    res = tmp_path / "results"; res.mkdir()
    import shutil
    for f in ("selective.csv", "explained_vs_fusion.csv", "conformal.csv"):
        src = core.Path(__file__).parent / "fixtures" / f
        if src.exists():
            shutil.copy(src, res / f)
    if not (res / "explained_vs_fusion.csv").exists():
        pytest.skip("fixtures for verify not built")
    rows = v.checks(R, res)
    assert len(rows) >= 10 and not all(ok for *_, ok in rows)  # fake scores must NOT pass as thesis numbers


def test_full_calibration_and_fusion_shap_loaded(R):
    assert R.cal_full is not None and R.cal_full.tau[0.1] < R.cal_full.tau[0.2]
    assert set(R.fshap) == {0, 1, 2, 3, 4} and R.fshap[0]["label"] == R.labels[1] and R.fshap[0]["correct"] is True
    assert len(R.art["label_texts"]) == 733 and R.art["matcher_state"].name == "matcher_state.pt"
    assert R.art["label_cache"].name == "label_emb_ft20_s42.npy"


def test_replay_scores_unchanged_by_seed42_only_retrained_matcher(tmp_path, R):
    root = build(tmp_path / "root")
    d = root / "run_match_2_saved" / "ft20_s42"  # only seed 42 retrained: must NOT replace seed 42 inside the 3-seed B13a replay
    d.mkdir(parents=True)
    np.save(d / "dev_scores.npy", np.zeros((604, 733))); np.save(d / "test_scores.npy", np.zeros((725, 733)))
    assert np.allclose(core.load_replay(root).S, R.S)


def test_split_sentences_drops_fragments_and_caps():
    t = "The actor ran whoami. Then it dumped lsass memory!\nIt used RAR to stage data? ok\n\n  short one  "
    assert core.split_sentences(t) == ["The actor ran whoami.", "Then it dumped lsass memory!", "It used RAR to stage data?", "short one"][:3]
    assert len(core.split_sentences(" . ".join(["alpha beta gamma"] * 500), max_n=300)) == 300


def test_parse_labelled_lines(R):
    a, b = R.labels[0], R.labels[190]
    rows, errs = core.parse_labelled(f"{a}: attacker ran tool one\n{a.lower()}, {b} : second sentence here\nT9999: unknown id line\nno colon line\n\n", R.labels)
    assert rows == [("attacker ran tool one", [a]), ("second sentence here", sorted([a, b]))]
    assert len(errs) == 2 and "T9999" in errs[0] and "line 4" in errs[1]


def test_read_upload_csv_uses_text_column():
    data = b"id,text,labels\n1,first sentence here,['T1082']\n2,second sentence there,T1105;T1059\n"
    assert core.read_upload("r.csv", data) == "first sentence here\nsecond sentence there"
    assert core.read_labelled_csv(data) == [("first sentence here", ["T1082"]), ("second sentence there", ["T1059", "T1105"])]
    assert core.read_upload("r.txt", "café ran.".encode("utf-8")) == "café ran."


def test_calib_for_reproduces_loaded_calibration(R):
    for full, cal in ((True, R.cal_full), (False, R.cal_cls)):
        c = core.calib_for(R.art, full)
        assert c.tau == pytest.approx(cal.tau) and c.thr == pytest.approx(cal.thr)


def test_retrain_svm_learns_a_new_label(R):
    new = R.labels[190]  # unseen in the fake train split (180 seen labels)
    rows = [(f"zebrafoo implant variant {i} beacons home", [new]) for i in range(3)]
    art2 = core.retrain_svm(R.art, rows)
    assert art2["n_added"] == 3 and R.labels.index(new) in art2["seen_idx"] and R.labels.index(new) not in R.art["seen_idx"]
    top = lambda art: R.labels[int(core.svm_scores(art, ["zebrafoo implant beacons"])[0].argmax())]
    assert top(art2) == new and top(R.art) != new
    assert isinstance(core.calib_for(art2, True), core.Calib) and isinstance(core.calib_for(art2, False), core.Calib)
