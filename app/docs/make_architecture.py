"""Draw docs/img/architecture.png and .svg: data -> research pipeline -> app modules -> screen, plus the checks."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).parent / "img"
INK, MUTED, LINE = "#1f2328", "#57606a", "#8c959f"
FILL = {"data": "#eef3f8", "research": "#f3eefa", "app": "#eaf5ee", "ui": "#fff6e5", "check": "#fbeaea"}
fig, ax = plt.subplots(figsize=(13, 6.4)); ax.set_xlim(0, 13); ax.set_ylim(0, 6.4); ax.axis("off")

def box(x, y, w, h, title, lines, kind):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12", fc=FILL[kind], ec=LINE, lw=1))
    ax.text(x + 0.12, y + h - 0.16, title, fontsize=10.5, weight="bold", color=INK, va="top")
    ax.text(x + 0.12, y + h - 0.48, "\n".join(lines), fontsize=8.6, color=MUTED, va="top", linespacing=1.35)

def arrow(x1, y1, x2, y2):
    ax.annotate("", (x2, y2), (x1, y1), arrowprops=dict(arrowstyle="-|>", color=LINE, lw=1.2, shrinkA=2, shrinkB=2))

ax.text(0.1, 6.3, "ATT&CK threat-report explainer: architecture", fontsize=13, weight="bold", color=INK, va="top")
ax.text(0.1, 5.95, "research pipeline (thesis) and application (objective c) share the same saved files: the app reads boxes 1 and 2 directly and retrains nothing", fontsize=9, color=MUTED, va="top")
box(0.1, 2.75, 2.9, 2.85, "1  Thesis data and runs", ["TRAM train / dev / test", "ATT&CK descriptions (v12.1)", "RoBERTa, SecBERT: saved", "  probabilities, 3 seeds", "Matcher: saved scores, 3 seeds", "Stored SHAP (RoBERTa s42)", "Checkpoints s42 (live mode)"], "data")
box(3.4, 2.75, 2.9, 2.85, "2  Research pipeline", ["ttpmap package + scripts", "pre-registered analyses 01-21", "fusion, conformal sets, triage", "results/*.csv", "thesis_numbers.json (registry)", "report, thesis feed, QA gates"], "research")
box(6.7, 4.3, 2.9, 1.3, "3a  core.py", ["load saved scores, z-score fusion", "(3,1,1,1); dev-fitted conformal", "and triage thresholds; warnings"], "app")
box(6.7, 2.75, 2.9, 1.3, "3b  live.py + explain.py", ["SVM + RoBERTa + SecBERT (CPU)", "permutation SHAP; template or", "local qwen2.5:7b + grounding rule"], "app")
box(10.0, 2.75, 2.9, 2.85, "4  app.py (Streamlit UI)", ["ranked techniques (top 5)", "conformal candidate set", "triage tier (margin)", "rare / retired / confusion", "  warnings", "SHAP word highlights", "written explanation", "limits panel (registry ids)"], "ui")
box(3.4, 0.35, 9.5, 2.05, "5  Checks (evaluation of the artefact)", ["verify_artifacts.py: the app recomputes P@1, conformal and triage numbers from the saved scores",
    "   and compares them with results/*.csv (16 checks)",
    "tests: app (pytest, incl. Streamlit AppTest) and research package (run_tests.py)",
    "QA gates: numbers, links, hashes, privacy",
    "grounding_report.py: does the LLM text quote only top-5 SHAP words; live timing",
    "usability study kit (SUS) for the human evaluation"], "check")
box(0.1, 0.35, 2.9, 2.05, "Rules", ["dev-only tuning, test once", "every number from the registry", "no data leaves the PC", "AI assistance disclosed"], "data")
arrow(3.0, 4.2, 3.4, 4.2); arrow(6.3, 4.95, 6.7, 4.95); arrow(6.3, 3.4, 6.7, 3.4); arrow(9.6, 4.95, 10.0, 4.95); arrow(9.6, 3.4, 10.0, 3.4)
arrow(4.85, 2.75, 4.85, 2.4); arrow(8.15, 2.75, 8.15, 2.4); arrow(11.45, 2.75, 11.45, 2.4)
OUT.mkdir(parents=True, exist_ok=True)
for ext in ("png", "svg"):
    fig.savefig(OUT / f"architecture.{ext}", dpi=200, bbox_inches="tight", facecolor="white")
print("written", OUT / "architecture.png")
