"""Portable launcher: free port, environment, quick self-check."""
import json
import socket
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "portable"))
import check  # noqa: E402
import launch  # noqa: E402


def test_free_port_skips_busy():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); s.listen(1)
    busy = s.getsockname()[1]
    try:
        p = launch.free_port(busy, tries=20)
        assert p != busy and busy < p <= busy + 20
    finally:
        s.close()


def test_env_for_sets_offline_and_root(tmp_path, monkeypatch):
    monkeypatch.setenv("PYTHONPATH", r"C:\elsewhere")
    e = launch.env_for(tmp_path)
    assert e["TTPMAP_ROOT"] == str(tmp_path / "data") and e["HF_HUB_OFFLINE"] == "1" and e["TRANSFORMERS_OFFLINE"] == "1"
    assert e["PYTHONNOUSERSITE"] == "1" and "PYTHONPATH" not in e and e["TTPMAP_DEMO"] == "0"


def test_check_quick_reports_missing_file(tmp_path):
    (tmp_path / "launcher").mkdir(); (tmp_path / "data").mkdir()
    (tmp_path / "data" / "ok.txt").write_text("abc")
    files = [{"path": "data/ok.txt", "size": 3, "sha256": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"},
             {"path": "data/missing.npy", "size": 10, "sha256": "0" * 64}]
    (tmp_path / "launcher" / "MANIFEST.sha256.json").write_text(json.dumps({"files": files}))
    assert check.run(tmp_path, deep=False) == 1


def test_check_deep_catches_changed_file(tmp_path):
    (tmp_path / "launcher").mkdir(); (tmp_path / "data").mkdir()
    (tmp_path / "data" / "ok.txt").write_text("abd")  # same size, other bytes
    files = [{"path": "data/ok.txt", "size": 3, "sha256": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"}]
    (tmp_path / "launcher" / "MANIFEST.sha256.json").write_text(json.dumps({"files": files}))
    assert check.files(tmp_path, deep=True) == 1 and check.files(tmp_path, deep=False) == 0


def _bundle(tmp_path, files):
    (tmp_path / "launcher").mkdir(exist_ok=True)
    (tmp_path / "launcher" / "MANIFEST.sha256.json").write_text(json.dumps({"files": files}))
    return tmp_path


def test_quick_check_ignores_edited_thesis_material_but_not_app_files(tmp_path):
    (tmp_path / "data" / "_showcase").mkdir(parents=True); (tmp_path / "app").mkdir()
    (tmp_path / "data" / "_showcase" / "draft.docx").write_text("edited during the viva")  # size differs from the manifest
    (tmp_path / "app" / "app.py").write_text("abc")
    b = _bundle(tmp_path, [{"path": "data/_showcase/draft.docx", "size": 3, "sha256": "0" * 64, "core": False},
                           {"path": "app/app.py", "size": 3, "sha256": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad", "core": True}])
    assert check.run(b, deep=False) == 0
    (tmp_path / "app" / "app.py").unlink()
    assert check.run(b, deep=False) == 1


def test_healthy_ignores_system_proxy(monkeypatch):
    import http.server
    import threading

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200); self.end_headers(); self.wfile.write(b"ok")

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    monkeypatch.setenv("HTTP_PROXY", "http://127.0.0.1:9"); monkeypatch.setenv("http_proxy", "http://127.0.0.1:9")
    monkeypatch.delenv("NO_PROXY", raising=False); monkeypatch.delenv("no_proxy", raising=False)
    try:
        assert launch.healthy(srv.server_address[1], timeout=3)
    finally:
        srv.shutdown()


def test_secret_scan_looks_inside_zips(tmp_path):
    import importlib.util
    import zipfile
    top = Path(__file__).resolve().parents[2]  # thesis folder, or the portable folder (script under data/)
    script = next(p for p in (top / "_showcase", top / "data" / "_showcase") if (p / "scripts" / "build_portable_demo.py").exists())
    spec = importlib.util.spec_from_file_location("bpd", script / "scripts" / "build_portable_demo.py")
    bpd = importlib.util.module_from_spec(spec); spec.loader.exec_module(bpd)
    z = tmp_path / "pack.zip"
    with zipfile.ZipFile(z, "w") as f:
        f.writestr("a/kaggle.json", "{}")
        f.writestr("b/notes.md", "token " + "KGAT" + "_abcdefgh12345 here")  # built at runtime: the real scan must not flag this file
    assert {why for _, why in bpd.scan_file(z, None)} == {"forbidden file", "token pattern"}
    ok = tmp_path / "ok.zip"
    with zipfile.ZipFile(ok, "w") as f:
        f.writestr("readme.md", "nothing secret")
    assert bpd.scan_file(ok, None) == []


def test_server_cmd_runs_the_app_with_the_folders_python(tmp_path):
    cmd = launch.server_cmd(tmp_path, 8501)
    assert cmd[0] == launch.sys.executable and "streamlit" in cmd and str(tmp_path / "app" / "app.py") in cmd and "8501" in cmd


# ---- doctor start flow (Task 4) ----
import doctor  # noqa: E402
from test_doctor import Fake  # noqa: E402

PORT_DIR = Path(__file__).parent.parent / "portable"


class Seq(Fake):
    """missing_packages answers from a list, one per scan (first scan: missing, after the fix: none)."""

    def __init__(self, seq, **kw):
        super().__init__(**kw)
        self.seq = list(seq)

    def missing_packages(self, py, lock):
        return self.seq.pop(0) if len(self.seq) > 1 else self.seq[0]


def run_main(probes, argv=(), races=None):
    calls = {"fix": [], "start": 0, "race": 0}

    def fixer(fx, bundle, index, ask, hf_bases=None):
        calls["fix"].append((fx.key, index)); return True

    def race(bases, path, **k):
        calls["race"] += 1
        return races if races is not None else [(b, 0.05 * (i + 1)) for i, b in enumerate(bases)]

    def start():
        calls["start"] += 1; return 0
    rc = doctor.main(["X:/b", *argv], probes=probes, start=start, ask=lambda q: False, race=race, fixer=fixer)
    return rc, calls


def test_bat_runs_doctor_and_bootstraps_when_python_missing():
    bat = (PORT_DIR / "START_DEMO.bat").read_text(encoding="utf-8")
    assert 'if not exist "%PY%"' in bat and "bootstrap.ps1" in bat and r'launcher\doctor.py' in bat
    assert '"%~dp0."' in bat  # a quoted %~dp0 ends with a backslash that would escape the closing quote


def test_main_fixes_then_starts(capsys):
    rc, calls = run_main(Seq([["six"], []]))
    assert rc == 0 and calls["start"] == 1 and calls["fix"] == [("packages", "https://pypi.org/simple")]
    assert "Will fix" in capsys.readouterr().out


def test_main_stops_on_private_damage():
    rc, calls = run_main(Fake(bad_files=([], ["data/Dataset/tram_test.tsv"])))
    assert rc == 1 and calls["start"] == 0 and calls["fix"] == []


def test_scan_only_never_downloads():
    rc, calls = run_main(Fake(missing_packages=["six"]), argv=["--scan-only"])
    assert rc == 1 and calls == {"fix": [], "start": 0, "race": 0}


def test_optional_fix_not_offered_on_start():
    rc, calls = run_main(Fake(ollama=(False, False)))
    assert rc == 0 and calls["start"] == 1 and calls["fix"] == []


def test_offline_shows_needs_internet(capsys):
    rc, calls = run_main(Fake(missing_packages=["six"]), races=[("https://pypi.org/simple", None)])
    assert rc == 1 and calls["start"] == 0 and "needs internet for:" in capsys.readouterr().out


def test_bootstrap_uses_same_mirrors_and_checks_hash():
    import mirrors
    ps = (PORT_DIR / "bootstrap.ps1").read_text(encoding="utf-8")
    assert all(f"'{m}'" in ps for m in mirrors.PYPI) and "uv_sha256" in ps
    assert "EXTERNALLY-MANAGED" in ps  # the folder's own Python must accept the libraries


BUILD = Path(__file__).resolve().parents[2] / "_showcase" / "scripts" / "build_portable_demo.py"


@__import__("pytest").mark.skipif(not BUILD.exists(), reason="build script not in this folder")
def test_lite_selection_is_what_the_app_reads(tmp_path):
    """Every file core.load_replay opens on a fake thesis root must be in the lite folder."""
    import importlib.util
    import core
    from fake_root import build
    spec = importlib.util.spec_from_file_location("bpd", BUILD)
    bpd = importlib.util.module_from_spec(spec); spec.loader.exec_module(bpd)
    root = build(tmp_path / "root").resolve()
    opened = []
    sys.addaudithook(lambda ev, a: opened.append(a[0]) if ev == "open" and isinstance(a[0], (str, bytes, Path)) else None)
    core.load_replay(str(root))
    rels = sorted({Path(str(p)).resolve().relative_to(root).as_posix() for p in opened
                   if str(Path(str(p)).resolve()).startswith(str(root))} - {""})
    assert rels and all(bpd.lite_selected(r) for r in rels), [r for r in rels if not bpd.lite_selected(r)]
    assert not bpd.lite_selected("Exp_1_4_run_tram_2_epoc_30/roberta_nopw_s42/model.safetensors")
    assert not bpd.lite_selected("Exp_1_4_run_tram_2_epoc_30/roberta_pw_s43/model.safetensors")


def test_main_refreshes_import_caches_after_a_fix(monkeypatch):
    seen = []
    monkeypatch.setattr(doctor.importlib, "invalidate_caches", lambda: seen.append(1))
    rc, calls = run_main(Seq([["six"], []]))
    assert rc == 0 and calls["start"] == 1 and seen  # libraries installed in this run must be importable by the start check


def test_bootstrap_does_not_depend_on_script_modules():
    """Get-FileHash / Expand-Archive / Invoke-WebRequest live in modules that Windows PowerShell 5.1 cannot load when it inherits
    PowerShell 7's PSModulePath (seen on a real run). The bootstrap uses .NET directly, and the bat clears PSModulePath."""
    ps = (PORT_DIR / "bootstrap.ps1").read_text(encoding="utf-8")
    assert not any(c in ps for c in ("Get-FileHash", "Expand-Archive", "Invoke-WebRequest"))
    assert "SHA256]::Create()" in ps and "ZipFile]::ExtractToDirectory" in ps
    bat = (PORT_DIR / "START_DEMO.bat").read_text(encoding="utf-8")
    assert 'set "PSModulePath="' in bat


def test_bootstrap_skips_the_minor_version_link():
    ps = (PORT_DIR / "bootstrap.ps1").read_text(encoding="utf-8")
    assert "ReparsePoint" in ps  # uv adds a cpython-3.13-... junction next to the real folder


def _bpd():
    import importlib.util
    spec = importlib.util.spec_from_file_location("bpd", BUILD)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


@__import__("pytest").mark.skipif(not BUILD.exists(), reason="build script not in this folder")
def test_identity_scan_finds_names_in_office_metadata_and_file_names(tmp_path):
    import zipfile
    bpd = _bpd()
    d = tmp_path / "a.docx"
    with zipfile.ZipFile(d, "w") as z:
        z.writestr("docProps/core.xml", "<cp:lastModifiedBy>Jane Tester</cp:lastModifiedBy>")
    clean = tmp_path / "b.docx"
    with zipfile.ZipFile(clean, "w") as z:
        z.writestr("docProps/core.xml", "<cp:lastModifiedBy>KDU</cp:lastModifiedBy>")
    (tmp_path / "handcheck_jane.csv").write_text("ok", encoding="utf-8")
    pats = [b"jane tester", b"jane"]
    assert bpd.identity_hits("a.docx", d, pats) and not bpd.identity_hits("b.docx", clean, pats)
    assert bpd.identity_hits("handcheck_jane.csv", tmp_path / "handcheck_jane.csv", pats)


@__import__("pytest").mark.skipif(not BUILD.exists(), reason="build script not in this folder")
def test_identity_patterns_skip_generic_names(monkeypatch):
    bpd = _bpd()
    monkeypatch.setattr(bpd.getpass, "getuser", lambda: "admin")
    monkeypatch.setenv("COMPUTERNAME", "LAPTOP-XYZ1")
    pats = bpd.identity_patterns(git=False)
    assert b"laptop-xyz1" in pats and b"admin" not in pats
