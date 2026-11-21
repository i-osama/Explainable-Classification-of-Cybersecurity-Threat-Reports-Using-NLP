from pathlib import Path

import numpy as np
import pytest

import core
import demo_data

FX = Path(__file__).parent / "fixtures"


def test_zrow_to_full_fuse():
    F = core.to_full(np.array([[1.0, 2.0, 3.0]]), np.array([0, 2, 3]), 4)
    assert np.isnan(F[0, 1])
    z = core.zrow(F)
    assert z[0, 1] == 0.0 and abs(np.nanmean(F - F)) == 0  # unknown label -> 0
    Z = {n: np.ones((1, 4)) for n in core.ORDER}
    assert core.fuse(Z, (3, 1, 1, 1))[0, 0] == 6 and core.fuse(Z, (0, 1, 1, 1))[0, 0] == 3


def test_conformal_tau_marginal_coverage():
    rng = np.random.default_rng(0)
    def draw(n):
        S = rng.normal(0, 1, (n, 30)); g = rng.integers(0, 30, n); S[np.arange(n), g] += 4
        Y = np.zeros((n, 30), bool); Y[np.arange(n), g] = True
        return S, Y
    S_d, Y_d = draw(600); S_t, Y_t = draw(4000)
    for a in (0.1, 0.2):
        tau = core.conformal_tau(S_d, Y_d, a)
        cov = ((S_t >= tau) | ~Y_t).all(1).mean()  # all gold labels inside the set
        assert cov >= 1 - a - 0.03


def test_conformal_full_set_when_quantile_beyond_n():
    S = np.random.default_rng(1).normal(size=(5, 4)); Y = np.zeros((5, 4), bool); Y[:, 0] = True
    assert core.conformal_tau(S, Y, 0.01) == -np.inf  # ceil(6 * 0.99) = 6 > 5


def test_margin_and_assess_tiers():
    S = np.array([[5.0, 1.0, 0.0], [2.0, 1.9, 0.0]])
    assert core.margin(S).tolist() == [4.0, pytest.approx(0.1)]
    cal = core.Calib(tau={0.1: 1.5, 0.2: 3.0}, thr={0.5: 3.0, 0.8: 1.0, 0.9: 0.5})
    a, b = core.assess(S[0], cal), core.assess(S[1], cal)
    assert a["tier"] == 0 and a["set"] == [0] and b["tier"] == 2 and b["set"] == [0, 1]
    assert core.assess(S[1], core.Calib({0.1: 99, 0.2: 99}, cal.thr))["set"] == []  # empty set is possible and handled


def test_triage_threshold_is_thesis_order_statistic():
    # prereg 19 / ttpmap.selective.dev_threshold_for_coverage: t = sorted_desc[round(c * n) - 1], accept margin >= t (no interpolation)
    m = np.arange(1.0, 11.0)
    S = np.stack([m, np.zeros_like(m)], axis=1)
    cal = core.Calib.fit(S, np.eye(2, dtype=bool)[np.zeros(10, int)])
    assert cal.thr[0.9] == 2.0 and cal.thr[0.8] == 3.0 and cal.thr[0.5] == 6.0


def test_calib_thresholds_are_ordered():
    R = demo_data.demo_replay()
    assert R.cal.thr[0.5] > R.cal.thr[0.8] > R.cal.thr[0.9] and R.cal.tau[0.2] > R.cal.tau[0.1]


def test_flags_rare_drift_confusion():
    R = demo_data.demo_replay()
    msgs = [m for _, m in R.flags("DEMO-04")]
    assert any("Rare label" in m for m in msgs)
    assert any("Not active" in m for m in R.flags("DEMO-05") and [m for _, m in R.flags("DEMO-05")])
    assert any("Known confusion" in m for m in [m for _, m in R.flags("DEMO-02")])
    assert not R.flags("DEMO-01")


def test_loaders_on_real_result_files():
    nums = core.load_numbers(FX / "thesis_numbers.json")
    assert nums["E4"].startswith("108 of 725") and nums["B13a"] == "0.803"
    sel = core.load_selective(FX / "selective.csv")
    assert sel[0.5]["p1"] > sel[0.9]["p1"] and 0.4 < sel[0.5]["cov"] < 0.5
    assert core.load_drift(FX / "attack_drift_ids.csv")  # non-active ids only
    conf = core.load_confusions(FX / "confusions.csv")
    assert all(n >= 2 for v in conf.values() for _, n in v)


def test_drift_message_deprecated_without_successor(tmp_path):
    p = tmp_path / "d.csv"
    p.write_text("id,status_v12.1,status_latest,final_id_latest,final_status_latest,desc_similarity\n"
                 "T1064,deprecated,deprecated,T1064,deprecated,\nT1574.002,active,revoked,T1574.001,active,\nT1082,active,active,T1082,active,0.9\n")
    d = core.load_drift(p)
    assert set(d) == {"T1064", "T1574.002"}
    assert "successor" not in d["T1064"] and "no replacement" in d["T1064"]
    assert "revoked" in d["T1574.002"] and "T1574.001" in d["T1574.002"]


def test_load_names_from_attack_json(tmp_path):
    p = tmp_path / "n.json"
    p.write_text('{"techniques": {"T1124": {"name": "System Time Discovery"}, "t1007": {"name": "System Service Discovery"}}}', encoding="utf-8")
    assert core.load_names(p) == {"T1124": "System Time Discovery", "T1007": "System Service Discovery"}


def test_load_stix_names_prefers_live_object(tmp_path):
    ref = lambda i: [{"source_name": "mitre-attack", "external_id": i}]
    objs = [{"type": "attack-pattern", "name": "Old Name", "revoked": True, "external_references": ref("T1574.001")},
            {"type": "attack-pattern", "name": "DLL Search Order Hijacking", "external_references": ref("T1574.001")},
            {"type": "attack-pattern", "name": "Scripting", "x_mitre_deprecated": True, "external_references": ref("T1064")},
            {"type": "malware", "name": "not a technique", "external_references": ref("S0001")}]
    p = tmp_path / "b.json"
    p.write_text(__import__("json").dumps({"objects": objs}), encoding="utf-8")
    assert core.load_stix_names(p) == {"T1574.001": "DLL Search Order Hijacking", "T1064": "Scripting"}


def test_retired_labels_in_conformal_set_are_listed():
    R = demo_data.demo_replay()
    j = R.labels.index("DEMO-05")
    assert R.set_drift([0, j], "DEMO-01") == [("DEMO-05", R.drift["DEMO-05"])]
    assert R.set_drift([j], "DEMO-05") == []  # the top-1 label is already flagged by flags()


def test_env_flag_reads_off_values_as_off(monkeypatch):
    for v, want in (("1", True), ("true", True), ("Yes", True), ("on", True), ("0", False), ("false", False), ("no", False), ("", False)):
        monkeypatch.setenv("TTPMAP_DEMO", v)
        assert core.env_flag("TTPMAP_DEMO") is want, v
    monkeypatch.delenv("TTPMAP_DEMO")
    assert core.env_flag("TTPMAP_DEMO") is False


def test_missing_thesis_number_is_marked_pending():
    assert demo_data.demo_replay().num("B13a") == "[PENDING: B13a]"
