"""Shared figure style: serif font, colour-blind-safe palette (Okabe-Ito), white background, 300 dpi PNG + SVG, no baked-in titles."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OI = {"black": "#000000", "orange": "#E69F00", "sky": "#56B4E9", "green": "#009E73", "yellow": "#F0E442", "blue": "#0072B2", "vermillion": "#D55E00", "purple": "#CC79A7", "grey": "#8C8C8C"}
SYS_COLOR = {"TF-IDF + SVM": OI["grey"], "RoBERTa (3-seed avg)": OI["sky"], "SecBERT (3-seed avg)": OI["green"], "Matcher (3-seed ens.)": OI["orange"],
             "Fusion (3,1,1,1)": OI["blue"], "Classifiers-only ens.": OI["purple"], "Frequency prior": "#BBBBBB", "Matcher zero-shot": OI["yellow"], "Fusion equal (1,1,1,1)": OI["vermillion"]}
SYS_HATCH = {"TF-IDF + SVM": "", "RoBERTa (3-seed avg)": "//", "SecBERT (3-seed avg)": "..", "Matcher (3-seed ens.)": "\\\\", "Fusion (3,1,1,1)": ""}
SHORT = {"TF-IDF + SVM": "SVM", "RoBERTa (3-seed avg)": "RoBERTa", "SecBERT (3-seed avg)": "SecBERT", "Matcher (3-seed ens.)": "Matcher", "Fusion (3,1,1,1)": "Fusion"}


def setup() -> None:
    plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"], "font.size": 10, "axes.titlesize": 10,
                         "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white", "svg.fonttype": "none",
                         "axes.spines.top": False, "axes.spines.right": False, "axes.axisbelow": True, "legend.frameon": False})


def save(fig, out_dir: Path, name: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_dir / f"{name}.png", dpi=300)
    fig.savefig(out_dir / f"{name}.svg")
    plt.close(fig)


def box(ax, x, y, w, h, text, fc="white", ec="black", fs=9, lw=1.0, ls="-"):
    from matplotlib.patches import FancyBboxPatch
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06", fc=fc, ec=ec, lw=lw, ls=ls))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, wrap=True)


def arrow(ax, x0, y0, x1, y1, text=None, color="black", ls="-"):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="-|>", color=color, lw=1.0, ls=ls, shrinkA=0, shrinkB=0))
    if text:
        ax.text((x0 + x1) / 2, (y0 + y1) / 2 + 0.08, text, ha="center", va="bottom", fontsize=7.5, color=color)
