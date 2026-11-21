"""ttpmap: analysis package for sentence-level mapping of CTI text to MITRE ATT&CK techniques (TRAM).

Read-only on the project data; all outputs go to `_showcase/results` and `_showcase/figures`.
"""
import os
from pathlib import Path

__version__ = "0.1.0"

SHOWCASE: Path = Path(__file__).resolve().parents[2]
ROOT: Path = Path(os.environ.get("TTPMAP_ROOT", SHOWCASE.parent))
EVIDENCE: Path = ROOT / "_evidence_pack"
DATA: Path = ROOT / "Dataset"
CLS_DIR: Path = ROOT / "Exp_1_4_run_tram_2_epoc_30"
MATCH_DIR: Path = ROOT / "run_match_1"
SHAP_DIR: Path = ROOT / "Exp_3_0_shap"
RESULTS: Path = SHOWCASE / "results"
FIGURES: Path = SHOWCASE / "figures"
SEEDS = (42, 43, 44)
