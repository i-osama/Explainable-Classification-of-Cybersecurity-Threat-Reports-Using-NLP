"""Q1 wave 2 Task 6: ATT&CK version drift helpers, prereg 21."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap import drift


def _ap(sid, ext, name, **kw):
    return {"type": "attack-pattern", "id": sid, "name": name, "external_references": [{"source_name": "mitre-attack", "external_id": ext}], **kw}


def test_revocation_chain():
    rb = {"a": "b", "b": "c"}
    assert drift.final_id("a", rb) == "c"
    assert drift.final_id("x", rb) == "x"
    loop = {"a": "b", "b": "a"}
    assert drift.final_id("a", loop) in {"a", "b"}          # returns, no infinite loop


def test_status_kinds():
    objs = [_ap("s1", "T1001", "Active one"), _ap("s2", "T1002", "Old one", x_mitre_deprecated=True),
            _ap("s3", "T1003", "Revoked one", revoked=True), _ap("s4", "T1004", "Target"),
            {"type": "relationship", "relationship_type": "revoked-by", "source_ref": "s3", "target_ref": "s4"}]
    t = drift.status_table(objs).set_index("id")
    assert t.loc["T1001", "status"] == "active" and t.loc["T1002", "status"] == "deprecated"
    assert t.loc["T1003", "status"] == "revoked" and t.loc["T1003", "final_id"] == "T1004"
    assert t.loc["T1001", "final_id"] == "T1001"


def test_revoked_without_link_has_no_replacement():
    t = drift.status_table([_ap("s1", "T1006", "Gone", revoked=True)]).set_index("id")
    assert t.loc["T1006", "status"] == "revoked" and t.loc["T1006", "final_id"] is None


def test_chain_to_deprecated_target_visible():
    objs = [_ap("s1", "T1007", "Old", revoked=True), _ap("s2", "T1008", "Later deprecated", x_mitre_deprecated=True),
            {"type": "relationship", "relationship_type": "revoked-by", "source_ref": "s1", "target_ref": "s2"}]
    t = drift.status_table(objs).set_index("id")
    assert t.loc["T1007", "final_id"] == "T1008" and t.loc["T1007", "final_status"] == "deprecated"


def test_duplicate_external_id_prefers_active():
    objs = [_ap("s1", "T1005", "Old", revoked=True), _ap("s2", "T1005", "New")]
    assert drift.status_table(objs).set_index("id").loc["T1005", "status"] == "active"
