"""Q1 plan Task 8: Colab outputs are only accepted when every output hash in the manifest matches."""
import hashlib, json, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap.ingest import ingest


def _run(tmp: Path, good: bool, status: str = "DONE"):
    src = tmp / "returned" / "showcase_runs" / "04_train_matcher_save"; (src / "ft20_s42").mkdir(parents=True)
    f = src / "ft20_s42" / "test_scores.npy"; f.write_bytes(b"scores")
    h = hashlib.sha256(b"scores" if good else b"other").hexdigest()
    man = {"run_id": "matcher_ft20_s42", "status": status, "metrics": {"P@1": 0.76}, "env": {"gpu": "Tesla T4"},
           "output_sha256": {"/content/drive/MyDrive/KDU/Thesis/showcase_runs/04_train_matcher_save/ft20_s42/test_scores.npy": h}}
    (src / "manifest_matcher_ft20_s42.json").write_text(json.dumps(man))
    return ingest(tmp / "returned", tmp / "dest")


def test_ingest_rejects_hash_mismatch():
    with tempfile.TemporaryDirectory() as t:
        r = _run(Path(t), good=False)
        assert r["ok"] is False and r["bad"] and not (Path(t) / "dest").exists()


def test_ingest_accepts_matching_hash_and_logs():
    with tempfile.TemporaryDirectory() as t:
        r = _run(Path(t), good=True)
        assert r["ok"] is True and (Path(t) / "dest" / "matcher_ft20_s42" / "test_scores.npy").read_bytes() == b"scores"
        log = json.loads((Path(t) / "dest" / "INGEST_LOG.json").read_text())
        assert log["runs"]["matcher_ft20_s42"]["metrics"]["P@1"] == 0.76


def test_ingest_maps_hardened_out_paths():
    """Prompt F: hardened notebooks write to /content/out (Colab) or /kaggle/working/out (Kaggle); two seeds share file names."""
    for prefix in ("/content/out", "/kaggle/working/out"):
        with tempfile.TemporaryDirectory() as t:
            src = Path(t) / "returned"; m = src / "showcase_runs" / "04_train_matcher_save"; m.mkdir(parents=True)
            for sd in (42, 43):
                d = src / "run_match_2_saved" / f"ft20_s{sd}"; d.mkdir(parents=True); (d / "test_scores.npy").write_bytes(f"s{sd}".encode())
                out = {f"{prefix}/run_match_2_saved/ft20_s{sd}/test_scores.npy": hashlib.sha256(f"s{sd}".encode()).hexdigest()}
                (m / f"manifest_matcher_ft20_s{sd}.json").write_text(json.dumps({"run_id": f"matcher_ft20_s{sd}", "status": "DONE", "output_sha256": out}))
            r = ingest(src, Path(t) / "dest")
            assert r["ok"] is True and r["copied"] == 2, r


def test_ingest_rejects_smoke_manifests():
    with tempfile.TemporaryDirectory() as t:
        r = _run(Path(t), good=True, status="SMOKE")
        assert r["ok"] is False and "SMOKE" in r["bad"][0]
