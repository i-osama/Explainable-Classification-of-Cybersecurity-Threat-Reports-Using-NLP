"""Start the explainer from the portable folder: self-check, local server on 127.0.0.1, browser splash -> app.

Run by START_DEMO.bat with the folder's own Python. Nothing is installed and nothing is fetched from the internet.
"""
import datetime
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check  # noqa: E402

INK, AMBER, GREEN, RED, DIM, END = "\033[94m", "\033[93m", "\033[92m", "\033[91m", "\033[2m", "\033[0m"
BANNER = r"""
     _  _____ _____   ___    ____ _  __
    / \|_   _|_   _| ( _ )  / ___| |/ /
   / _ \ | |   | |   / _ \/\ |   | ' /     threat-report explainer
  / ___ \| |   | |  | (_>  < |___| . \     fusion (3,1,1,1) + SHAP, offline
 /_/   \_\_|   |_|   \___/\/\____|_|\_\
"""


def free_port(start=8501, tries=20):
    """First port from `start` that nobody listens on (an old demo window may still hold 8501)."""
    for p in range(start, start + tries + 1):
        with socket.socket() as s:
            try:
                s.bind(("127.0.0.1", p))
                return p
            except OSError:
                continue
    raise RuntimeError(f"no free port in {start}-{start + tries}: close other demo windows")


def env_for(bundle):
    """Environment for the app: the folder's data, offline model loading, no user packages or PYTHONPATH from this PC."""
    bundle = Path(bundle)
    e = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP")}
    e.update(TTPMAP_ROOT=str(bundle / "data"), TTPMAP_DEMO="0", HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1",
             HF_HUB_DISABLE_TELEMETRY="1", PYTHONNOUSERSITE="1", PYTHONUTF8="1",
             STREAMLIT_BROWSER_GATHER_USAGE_STATS="false", TOKENIZERS_PARALLELISM="false")
    return e


def server_cmd(bundle, port):
    """Command for the web app, always with the folder's own Python."""
    py, app = [sys.executable, "-E", "-s", "-X", "utf8"], Path(bundle) / "app"
    return py + ["-m", "streamlit", "run", str(app / "app.py"), "--server.headless", "true", "--server.address", "127.0.0.1",
                 "--server.port", str(port), "--browser.gatherUsageStats", "false", "--server.fileWatcherType", "none"]


def writable_dir(bundle):
    """logs/ next to the app, or the temp folder when the copy is read-only (DVD, write-protected USB)."""
    for d in (Path(bundle) / "logs", Path(tempfile.gettempdir()) / "TTP_DEMO_logs"):
        try:
            d.mkdir(parents=True, exist_ok=True)
            (d / ".w").write_text("ok"); (d / ".w").unlink()
            return d
        except OSError:
            continue
    raise RuntimeError("no writable folder for logs")


NO_PROXY = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # a PC's system proxy must not see 127.0.0.1


def healthy(port, timeout=1.0):
    try:
        with NO_PROXY.open(f"http://127.0.0.1:{port}/_stcore/health", timeout=timeout) as r:
            return r.status == 200
    except OSError:
        return False


def main():
    bundle = Path(__file__).resolve().parent.parent
    os.system("")
    print(INK + BANNER + END)
    print(f"  {DIM}folder: {bundle}{END}\n  Checking this copy...")
    if check.run(bundle, deep=False):
        print(f"\n  {RED}The folder is incomplete or damaged.{END} Copy the whole TTP_DEMO folder again, then run CHECK_DEMO.bat.")
        return 1
    port, logs = free_port(), writable_dir(bundle)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log = open(logs / f"streamlit_{stamp}.log", "w", encoding="utf-8")
    proc = subprocess.Popen(server_cmd(bundle, port), cwd=bundle / "app", env=env_for(bundle), stdout=log, stderr=subprocess.STDOUT)
    splash = logs / f"splash_{port}.html"  # port baked in: a file:// URL with ?port= loses its query on some PCs
    splash.write_text((bundle / "launcher" / "splash.html").read_text(encoding="utf-8").replace("{{PORT}}", str(port)), encoding="utf-8")
    webbrowser.open(splash.as_uri())
    print(f"  Starting the local server on {AMBER}http://127.0.0.1:{port}{END} ...", flush=True)
    t0 = time.time()
    while not healthy(port):
        if proc.poll() is not None:
            print(f"  {RED}The server stopped.{END} Log: {log.name}")
            return 1
        if time.time() - t0 > 180:
            print(f"  {RED}No answer after 3 minutes.{END} Log: {log.name}")
            break
        time.sleep(0.5)
    else:
        print(f"  {GREEN}Ready in {time.time() - t0:.0f} s.{END} The browser switches to the app by itself.")
    print(f"\n  If no browser opened, open {AMBER}http://127.0.0.1:{port}{END} by hand.")
    print(f"  {DIM}Keep this window open during the demo. Close it (or press Ctrl+C) to stop the app.{END}\n")
    try:
        return proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        return 0


if __name__ == "__main__":
    sys.exit(main())
