"""E8: _showcase/UPLOAD_TO_CLAUDE_AI.zip (< 20 MB) + UPLOAD_INDEX.md, for the thesis writer in claude.ai.
Contents fixed by the close-out brief. Every file is scanned for full dataset sentences before zipping; the build stops if one is found."""
import re, sys, zipfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap.data import load_split, norm_text

SHOW = Path(__file__).resolve().parents[1]; ZP = SHOW / "UPLOAD_TO_CLAUDE_AI.zip"
files = [SHOW / f for f in ("thesis_numbers.json", "THESIS_PLACEHOLDERS.md", "STATUS.yaml", "GAP_REGISTER.md", "DECISIONS.md", "AUDIT_TODO.md", "report/index.html",
                            "docs/THREATS_TO_VALIDITY.md", "docs/RELATED_WORK_VERIFIED.md", "notebooks/RUN_ORDER.md", "notebooks/COLAB_RUNBOOK.md", "figures/FIGURES.md",
                            "docs/superpowers/plans/2026-11-15-q1-upgrade.md", "docs/superpowers/plans/2026-11-15-q1-wave2.md", "docs/REFORMS_CHECKLIST.md")]
files += sorted((SHOW / "experiments" / "prereg").glob("1[4-9]_*.md")) + sorted((SHOW / "experiments" / "prereg").glob("2[0-9]_*.md"))
files += sorted((SHOW / "thesis_feed").rglob("*.*")) + sorted((SHOW / "results").glob("*.csv")) + sorted((SHOW / "figures").glob("*.png"))
files = [f for f in files if f.name.lower() != "desktop.ini"]          # Google Drive / Windows folder artefacts
DESC = {"thesis_numbers.json": "single source of truth: every number (id, value, CI, definition, source file, script, status)", "THESIS_PLACEHOLDERS.md": "answers to the draft's open items, with sources; section 14 = number audit of draft v2",
        "STATUS.yaml": "status board: done, partial, negative result, to do on Colab, to do by the author, not found", "GAP_REGISTER.md": "17 research dimensions rated covered, partial or missing",
        "DECISIONS.md": "every non-obvious choice and its reason", "AUDIT_TODO.md": "unregistered numbers of the draft with the nearest registry key and likely cause",
        "report/index.html": "self-contained report: story, results with intervals, error analysis, explainability, limits, status (open in a browser)",
        "docs/THREATS_TO_VALIDITY.md": "internal, construct, external and conclusion threats with status", "docs/RELATED_WORK_VERIFIED.md": "reference check by web search: VERIFIED, PARTLY or UNVERIFIED, with URLs",
        "notebooks/RUN_ORDER.md": "Colab run order, runtimes, what each notebook fills", "notebooks/COLAB_RUNBOOK.md": "click-by-click Colab guide and fixes", "figures/FIGURES.md": "figure list with claim ids, sources and alt text",
        "thesis_feed/FUSION_DEFINITIONS.md": "the three fusion definitions and where each appears in draft v2", "thesis_feed/DIFFERENCES.md": "numbers and statements where draft v2 differs from the files",
        "thesis_feed/NEW_FINDINGS.md": "results added after draft v2 (Holm, support-aware fusion, faithfulness, 256 tokens, unseen labels)", "thesis_feed/DO_NOT_CLAIM.md": "claims the evidence does not support",
        "thesis_feed/WEB_CLAUDE_PROMPT.md": "START HERE: paste into the claude.ai Project instructions (number, claim and pending-work rules)",
        "thesis_feed/Q1_MANUSCRIPT_BRIEF.md": "article brief: story, contributions with evidence ids, research questions, section map, open items",
        "thesis_feed/Q1_FINDINGS.md": "results of 15 Nov: robustness/shortcuts, stacked fusion, sibling sources, minimum detectable effects, LLM baseline; wave 2: conformal sets, triage (AURC), label-noise candidates, ATT&CK drift",
        "docs/REFORMS_CHECKLIST.md": "REFORMS reporting checklist (32 items) with evidence paths and open holes; use as an appendix",
        "docs/superpowers/plans/2026-11-15-q1-wave2.md": "Q1 wave 2 plan: conformal sets, triage, label noise, ATT&CK drift, REFORMS, 2026 references",
        "thesis_feed/EXPLAINER_MATCHER_FUSION.md": "plain-language explainer of the matcher and the fusion (corrected 15 Nov), with method lines",
        "docs/superpowers/plans/2026-11-15-q1-upgrade.md": "Q1 upgrade plan: gap table, tasks, what runs where"}
sents = {norm_text(t) for sp in ("train", "dev", "test") for t in load_split(sp)["text"] if len(str(t)) >= 60}
bad = []
for p in files:
    if p.suffix in (".png",): continue
    t = norm_text(re.sub(r"<[^>]+>", " ", p.read_text(encoding="utf-8", errors="ignore")))
    n = sum(1 for s in sents if s in t)
    if n: bad.append(f"{p.relative_to(SHOW)}: {n} dataset sentences")
if bad: print("STOP, dataset text found:", bad); sys.exit(1)
def desc(rel):
    if rel in DESC: return DESC[rel]
    if rel.startswith("thesis_feed/tables/"): return f"table for the thesis ({'CSV for editing' if rel.endswith('.csv') else 'markdown for reading'}), built by scripts/build_thesis_feed.py"
    if rel.startswith("thesis_feed/"): return "numbers, tables, figures and caveats for this thesis part"
    if rel.startswith("results/"): return "derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py"
    if rel.startswith("figures/"): return "figure, 300 dpi PNG (SVG in the repository); caption and alt text in figures/FIGURES.md"
    return ""
idx = ["# UPLOAD INDEX", "", "Contents of `UPLOAD_TO_CLAUDE_AI.zip`. No dataset text, no model weights, no rater data. Every number comes from `thesis_numbers.json`.", "", "| file | what it is |", "|---|---|"]
idx += [f"| `{p.relative_to(SHOW).as_posix()}` | {desc(p.relative_to(SHOW).as_posix())} |" for p in files]
(SHOW / "UPLOAD_INDEX.md").write_text("\n".join(idx) + "\n", encoding="utf-8")
with zipfile.ZipFile(ZP, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    z.write(SHOW / "UPLOAD_INDEX.md", "UPLOAD_INDEX.md")
    for p in files: z.write(p, p.relative_to(SHOW).as_posix())
mb = ZP.stat().st_size / 1e6
print(f"UPLOAD ZIP: {ZP} | {len(files) + 1} files | {mb:.1f} MB (limit 20) | dataset-text scan: clean")
sys.exit(0 if mb < 20 else 1)
