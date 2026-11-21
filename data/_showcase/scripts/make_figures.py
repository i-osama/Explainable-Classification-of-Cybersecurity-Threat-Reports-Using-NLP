"""T4: regenerate all figures from results/*.csv. Usage: python scripts/make_figures.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap import FIGURES
from ttpmap.viz.figures import make_all
rows = make_all()
png = len(list(FIGURES.glob("fig*.png"))); svg = len(list(FIGURES.glob("fig*.svg")))
print(f"figures: {len(rows)} functions, {png} png, {svg} svg, FIGURES.md rows {len(rows)}")
