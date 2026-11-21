"""Mirror race and verified download against a local HTTP server (no internet)."""
import hashlib
import http.server
import sys
import threading
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "portable"))
import mirrors  # noqa: E402

GOOD = b"wheel bytes " * 1000
ROUTES = {  # path -> (delay seconds, status, body)
    "/fast/pip/": (0.0, 200, b"<html>pip index</html>"),
    "/slow/pip/": (0.4, 200, b"<html>pip index</html>"),
    "/bad/f.whl": (0.0, 200, b"<html>captive portal login</html>"),
    "/good/f.whl": (0.0, 200, GOOD),
}


class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        delay, status, body = ROUTES.get(self.path, (0.0, 404, b"not found"))
        time.sleep(delay)
        self.send_response(status)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


@pytest.fixture(scope="module")
def srv():
    s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{s.server_address[1]}"
    s.shutdown()


def closed_port():
    import socket
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close()
    return f"http://127.0.0.1:{p}"


def test_race_orders_by_speed(srv):
    res = mirrors.race([f"{srv}/slow", f"{srv}/fast"], "pip/")
    assert [b for b, _ in res] == [f"{srv}/fast", f"{srv}/slow"] and res[0][1] < res[1][1]


def test_race_unreachable_is_none_and_last(srv):
    dead = closed_port()
    res = mirrors.race([dead, f"{srv}/fast"], "pip/")
    assert res[0][0] == f"{srv}/fast" and res[-1] == (dead, None)


def test_offline_all_none_within_10s():
    t0 = time.time()
    res = mirrors.race([closed_port(), closed_port(), "http://10.255.255.1"], "pip/")
    assert all(s is None for _, s in res) and time.time() - t0 < 10


def test_fetch_falls_back_on_hash_mismatch(srv, tmp_path):
    seen = []
    dest = mirrors.fetch([f"{srv}/bad/f.whl", f"{srv}/good/f.whl"], tmp_path / "f.whl", hashlib.sha256(GOOD).hexdigest(),
                         progress=lambda done, total: seen.append((done, total)))
    assert dest.read_bytes() == GOOD and not list(tmp_path.glob("*.part"))
    assert seen and seen[-1][0] == len(GOOD)


def test_fetch_all_bad_raises_with_reasons(srv, tmp_path):
    with pytest.raises(mirrors.DownloadError) as e:
        mirrors.fetch([f"{srv}/missing.whl", f"{srv}/bad/f.whl"], tmp_path / "f.whl", hashlib.sha256(GOOD).hexdigest())
    msg = str(e.value)
    assert "404" in msg and "hash" in msg and "/bad/f.whl" in msg
    assert not (tmp_path / "f.whl").exists() and not list(tmp_path.glob("*.part"))


def test_mirror_lists_are_https():
    assert mirrors.PYPI[0] == "https://pypi.org/simple" and all(u.startswith("https://") for u in mirrors.PYPI + mirrors.HF)
