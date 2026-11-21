"""Repair plan and actions (no downloads, no installers: those are faked)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "portable"))
import doctor  # noqa: E402
import repair  # noqa: E402
from doctor import Check  # noqa: E402


def fails(*keys):
    fix = {"python": "runtime", "packages": "packages", "files_public": "files_public", "vcredist": "vcredist", "ollama": "ollama",
           "files_private": None}
    return [Check(k, False, "optional" if k == "ollama" else "required", k, fix[k]) for k in keys]


def test_plan_order_and_consent():
    p = repair.plan(fails("ollama", "packages", "vcredist", "python", "files_public"))
    assert [f.key for f in p] == ["runtime", "packages", "files_public", "vcredist", "ollama"]
    assert {f.key for f in p if f.needs_consent} == {"vcredist", "ollama"}
    assert all(f.needs_internet for f in p) and all(f.title and f.source for f in p)


def test_private_damage_has_no_fix():
    assert repair.plan(fails("files_private")) == []


def test_offline_plan_reports_needs_internet():
    msg = repair.needs_internet_text(repair.plan(fails("packages", "vcredist")))
    assert msg.startswith("needs internet for:") and "libraries" in msg.lower() and "C++" in msg


def test_pip_cmd_flags(tmp_path):
    c = repair.pip_cmd(Path("py.exe"), tmp_path / "sub.txt", "https://mirrors.aliyun.com/pypi/simple")
    assert c[:3] == ["py.exe", "-m", "pip"] and "--require-hashes" in c and "--no-deps" in c
    assert c[c.index("--index-url") + 1] == "https://mirrors.aliyun.com/pypi/simple" and "--only-binary" in c


def test_uv_cmd_flags(tmp_path):
    c = repair.uv_cmd(Path("uv.exe"), Path("py.exe"), tmp_path / "sub.txt", "https://pypi.org/simple")
    assert c[:3] == ["uv.exe", "pip", "install"] and "--require-hashes" in c and "--no-deps" in c
    assert c[c.index("--python") + 1] == "py.exe" and c[c.index("--index-url") + 1] == "https://pypi.org/simple"


def test_lock_subset_keeps_hashes(tmp_path):
    lock = tmp_path / "lock.txt"
    lock.write_text("# top\na==1.0 \\\n    --hash=sha256:aaa \\\n    --hash=sha256:aa2\n    # via x\nb==2.0 \\\n    --hash=sha256:bbb\n",
                    encoding="utf-8")
    out = repair.lock_subset(lock, ["b"], tmp_path / "sub.txt").read_text(encoding="utf-8")
    assert "b==2.0" in out and "sha256:bbb" in out and "a==1.0" not in out and "aaa" not in out


def test_ask_no_skips_system_install(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(repair.mirrors, "fetch", lambda *a, **k: calls.append(("fetch", a)))
    monkeypatch.setattr(repair.subprocess, "run", lambda *a, **k: calls.append(("run", a)))
    fx = next(f for f in repair.plan(fails("vcredist")) if f.key == "vcredist")
    assert repair.apply(fx, tmp_path, "https://pypi.org/simple", ask=lambda q: False) is False and calls == []


def test_installed_local_version_matches_lock(tmp_path):
    """torch 2.15.0+cpu (installed) must satisfy torch==2.15.0 (the PyPI pin): no endless reinstall."""
    from importlib import metadata
    v = metadata.version("torch").split("+")[0]
    lock = tmp_path / "lock.txt"
    lock.write_text(f"torch=={v} \\\n    --hash=sha256:00\n", encoding="utf-8")
    assert doctor.REAL.missing_packages(Path(sys.executable), lock) == []


def test_install_runtime_takes_the_real_folder_not_the_link(tmp_path, monkeypatch):
    """uv puts the real cpython-3.13.18-... folder next to a cpython-3.13-... junction that sorts first (seen on a real run)."""
    import _winapi
    import pytest
    if not hasattr(_winapi, "CreateJunction"):
        pytest.skip("Windows only")

    def fake_run(cmd, **k):
        d = Path(cmd[cmd.index("--install-dir") + 1])
        real = d / "cpython-3.13.18-windows-x86_64-none"
        real.mkdir(parents=True)
        (real / "python.exe").write_bytes(b"MZ")
        (real / "Lib").mkdir()
        (real / "Lib" / "EXTERNALLY-MANAGED").write_text("x")
        _winapi.CreateJunction(str(real), str(d / "cpython-3.13-windows-x86_64-none"))
        return 0
    monkeypatch.setattr(repair, "find_uv", lambda b: Path("uv.exe"))
    monkeypatch.setattr(repair, "_run", fake_run)
    assert repair.install_runtime(tmp_path) is True
    py = tmp_path / "runtime" / "python"
    assert (py / "python.exe").read_bytes() == b"MZ" and not py.is_junction()
    assert not (py / "Lib" / "EXTERNALLY-MANAGED").exists() and not (tmp_path / "runtime" / "_py").exists()
