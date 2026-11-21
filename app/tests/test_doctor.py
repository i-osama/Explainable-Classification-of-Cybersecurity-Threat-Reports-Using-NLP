"""Doctor scan: what the PC and the folder have, as Check rows (no network, fake probes)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "portable"))
import doctor  # noqa: E402


class Fake:
    """Probe answers of a healthy Windows 11 laptop; tests change one answer at a time."""

    def __init__(self, **kw):
        self.a = dict(windows=(True, "Windows 11 AMD64"), avx2=True, ram_gb=(16.0, 9.0), disk_free_gb=50.0,
                      runtime_python=Path("X:/b/runtime/python/python.exe"), missing_packages=[], bad_files=([], []),
                      vcredist=True, writable=True, ollama=(True, True))
        self.a.update(kw)

    def windows(self): return self.a["windows"]
    def avx2(self): return self.a["avx2"]
    def ram_gb(self): return self.a["ram_gb"]
    def disk_free_gb(self, path): return self.a["disk_free_gb"]
    def runtime_python(self, bundle): return self.a["runtime_python"]
    def missing_packages(self, py, lock): return self.a["missing_packages"]
    def bad_files(self, bundle): return self.a["bad_files"]
    def vcredist(self): return self.a["vcredist"]
    def writable(self, bundle): return self.a["writable"]
    def ollama(self): return self.a["ollama"]


B = Path("X:/b")


def by_key(checks):
    return {c.key: c for c in checks}


def test_scan_all_ok_on_fake_probes():
    cs = doctor.scan(B, Fake())
    assert {c.key for c in cs} >= {"os", "cpu", "ram", "disk", "python", "packages", "files_public", "files_private",
                                    "vcredist", "writable", "path", "ollama"}
    assert all(c.ok for c in cs), [c for c in cs if not c.ok]


def test_missing_package_is_required_fix():
    c = by_key(doctor.scan(B, Fake(missing_packages=["blinker"])))["packages"]
    assert not c.ok and c.need == "required" and c.fix == "packages" and "blinker" in c.detail


def test_no_python_needs_runtime_and_packages():
    k = by_key(doctor.scan(B, Fake(runtime_python=None)))
    assert k["python"].fix == "runtime" and not k["python"].ok
    assert k["packages"].fix == "packages" and not k["packages"].ok


def test_private_file_damage_says_copy_again():
    c = by_key(doctor.scan(B, Fake(bad_files=([], ["data/Dataset/tram_test.tsv"]))))["files_private"]
    assert not c.ok and c.fix is None and "copy the whole folder again" in c.detail and c.need == "required"


def test_public_file_damage_is_a_download_fix():
    c = by_key(doctor.scan(B, Fake(bad_files=(["data/models/bge/tokenizer.json"], []))))["files_public"]
    assert not c.ok and c.fix == "files_public"


def test_readonly_folder_blocks_repairs():
    c = by_key(doctor.scan(B, Fake(writable=False, missing_packages=["blinker"])))["writable"]
    assert not c.ok and c.need == "required" and "copy the folder to this laptop first" in c.detail


def test_readonly_folder_is_fine_when_nothing_to_repair():
    c = by_key(doctor.scan(B, Fake(writable=False)))["writable"]
    assert c.need == "info"


def test_long_path_warns():
    c = by_key(doctor.scan(Path("C:/" + "x" * 118), Fake()))["path"]
    assert not c.ok and c.need == "info"


def test_low_ram_required():
    assert by_key(doctor.scan(B, Fake(ram_gb=(4.0, 2.0))))["ram"].need == "required"
    c = by_key(doctor.scan(B, Fake(ram_gb=(16.0, 2.0))))["ram"]
    assert not c.ok and c.need == "info"


def test_non_windows_unsupported():
    c = by_key(doctor.scan(B, Fake(windows=(False, "Darwin arm64"))))["os"]
    assert not c.ok and c.need == "required" and "Windows 10/11 64-bit only" in c.detail


def test_missing_vcredist_is_a_fix():
    c = by_key(doctor.scan(B, Fake(vcredist=False)))["vcredist"]
    assert not c.ok and c.need == "required" and c.fix == "vcredist"


def test_ollama_is_optional():
    k = by_key(doctor.scan(B, Fake(ollama=(False, False))))
    assert k["ollama"].need == "optional" and k["ollama"].fix == "ollama"
    assert by_key(doctor.scan(B, Fake(ollama=(True, False))))["ollama"].fix == "ollama_model"


def test_disk_needs_space_only_when_downloading():
    assert by_key(doctor.scan(B, Fake(disk_free_gb=0.5)))["disk"].ok  # nothing to download
    c = by_key(doctor.scan(B, Fake(disk_free_gb=0.5, runtime_python=None)))["disk"]
    assert not c.ok and c.need == "required"


def test_lock_names_parse_pip_compile_format(tmp_path):
    f = tmp_path / "lock.txt"
    f.write_text("# header\nnumpy==2.3.1 \\\n    --hash=sha256:aa\nscikit-learn==1.6.1 \\\n    --hash=sha256:bb\n", encoding="utf-8")
    assert doctor.lock_pins(f) == {"numpy": "2.3.1", "scikit-learn": "1.6.1"}


def test_real_probes_on_this_pc():
    p = doctor.REAL
    ok, text = p.windows()
    assert isinstance(ok, bool) and text
    total, free = p.ram_gb()
    assert total > 0 and 0 <= free <= total
    assert p.disk_free_gb(Path(__file__)) > 0


def test_no_lock_falls_back_to_import_check(tmp_path, monkeypatch):
    monkeypatch.setattr(doctor, "LIBS", ("json", "definitely_not_a_module_xyz"))
    assert doctor.REAL.missing_packages(Path(sys.executable), tmp_path / "missing.lock") == ["definitely_not_a_module_xyz"]


def test_download_size_words():
    assert doctor.size_words(1, 11_000) == "1 library, about 11 KB"
    assert doctor.size_words(173, 360 * 2 ** 20) == "173 libraries, about 360 MB"
