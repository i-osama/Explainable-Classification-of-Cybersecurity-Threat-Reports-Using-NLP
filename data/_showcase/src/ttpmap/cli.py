"""Command line: python -m ttpmap {verify|metrics|analyses|figures|report|test}  (run from _showcase with src on the path,
or use run_all.ps1). Each sub-command runs the corresponding script so the CLI and the scripts cannot drift apart."""
from __future__ import annotations

import argparse
import logging
import subprocess
import sys

import yaml

from . import SHOWCASE
from . import stats

STEPS = {
    "test": ["scripts/run_tests.py"],
    "verify": ["scripts/verify_claims.py"],
    "analyses": ["scripts/run_analyses.py", "scripts/run_support_aware_v2.py"],
    "metrics": ["scripts/build_numbers.py"],
    "figures": ["scripts/make_figures.py"],
    "report": ["scripts/build_docs.py", "scripts/build_report.py"],
    "hashes": ["scripts/check_hashes.py"],
}


def check_config() -> None:
    """The YAML config is documentation that must agree with the code constants."""
    cfg = yaml.safe_load((SHOWCASE / "configs" / "analysis.yaml").read_text(encoding="utf-8"))
    assert cfg["bootstrap"]["resamples"] == stats.BOOT_N and cfg["bootstrap"]["seed"] == stats.BOOT_SEED, "configs/analysis.yaml disagrees with ttpmap.stats"
    from .fusion import ORDER, THESIS_WEIGHTS
    assert tuple(cfg["fusion"]["order"]) == ORDER and tuple(cfg["fusion"]["weights"]) == THESIS_WEIGHTS, "configs/analysis.yaml disagrees with ttpmap.fusion"


def main(argv=None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(prog="ttpmap", description=__doc__)
    ap.add_argument("command", choices=sorted(STEPS))
    a = ap.parse_args(argv)
    check_config()
    for s in STEPS[a.command]:
        r = subprocess.run([sys.executable, "-X", "utf8", str(SHOWCASE / s)], cwd=SHOWCASE)
        if r.returncode:
            return r.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
