"""E2 + E3: thesis_feed/ = one file per thesis part, with every number the part may use (from thesis_numbers.json),
tables as CSV + markdown (from results/*.csv), figures, caveats; plus FUSION_DEFINITIONS.md, DIFFERENCES.md,
NEW_FINDINGS.md, DO_NOT_CLAIM.md. Usage: python scripts/build_thesis_feed.py"""
import json, sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _tpl import render, numbers, SHOW

N = numbers(); R = SHOW / "results"; F = SHOW / "thesis_feed"; T = F / "tables"; T.mkdir(parents=True, exist_ok=True)
def W(name, text): (F / name).write_text(render(text.strip() + "\n", N), encoding="utf-8")
def ci(c): return f"[{c['ci'][0]:.3f}, {c['ci'][1]:.3f}]" if c["ci"] else ""
def esc(s): return str(s).replace("|", "/").replace("\n", " ")
def claims_table(ids):
    rows = ["| id | value | 95% CI | definition | source file | status |", "|---|---|---|---|---|---|"]
    for i in ids:
        c = N[i]; rows.append(f"| `{i}` | {esc(c['display'])} | {ci(c)} | {esc(c['label'])}. {esc(c['definition'])} | `{esc(c['source_file'])}` | {c['status']} |")
    return "\n".join(rows)
def pick(prefixes=(), sections=(), exclude=()):
    return [k for k, c in N.items() if (any(k == p or k.startswith(p + ".") for p in prefixes) or c["thesis_section"] in sections) and not any(k.startswith(e) for e in exclude)]
def table(name, df, cols=None, rnd=4):
    df = df[cols] if cols else df; df = df.copy()
    for c in df.columns:
        if df[c].dtype.kind == "f": df[c] = df[c].round(rnd)
    df.to_csv(T / f"{name}.csv", index=False)
    md = "| " + " | ".join(map(str, df.columns)) + " |\n|" + "---|" * len(df.columns) + "\n" + "\n".join("| " + " | ".join(esc(v) for v in r) + " |" for r in df.itertuples(index=False))
    (T / f"{name}.md").write_text(md + "\n", encoding="utf-8"); return f"`tables/{name}.csv` / `.md`"
rd = lambda f: pd.read_csv(R / f)

# ---------------- tables ----------------
tb = {}
tb["systems"] = table("t_systems", rd("systems.csv"), ["system", "P@1", "P@1_lo", "P@1_hi", "MRR@3", "MRR@3_lo", "MRR@3_hi", "P@3", "R@5_micro", "unseen_R@5"])
ps = rd("per_seed.csv"); tb["per_seed"] = table("t_per_seed", ps, [c for c in ["system", "seed", "threshold", "micro_f1_notebook", "micro_f1_all_test", "macro_f1_notebook", "macro_f1_all_test", "P@1", "MRR@3"] if c in ps.columns])
tb["f1"] = table("t_f1_variants", rd("f1_variants.csv"), ["system", "seed", "variant", "micro_f1", "macro_f1", "micro_precision", "micro_recall", "n_macro_labels"])
cm = rd("comparisons.csv"); tb["cmp"] = table("t_comparisons_holm", cm, ["id", "A", "B", "P@1_A", "P@1_B", "delta_P@1", "ci_lo", "ci_hi", "mcnemar_b", "mcnemar_c", "p_mcnemar", "p_holm", "family_size", "supported", "delta_MRR@3", "mrr_ci_lo", "mrr_ci_hi"])
ab = rd("ablation.csv").rename(columns={"mean": "P@1", "lo": "P@1_lo", "hi": "P@1_hi"}); tb["abl"] = table("t_ablation", ab, ["system", "P@1", "P@1_lo", "P@1_hi", "MRR@3", "n"])
tb["sup"] = table("t_support_buckets", rd("support_buckets.csv"), ["bucket", "system", "n_sentences", "P@1", "lo", "hi", "top1_label_F1"])
tb["fb"] = table("t_fixed_broken", rd("fixed_broken.csv"), None)
tb["tac"] = table("t_tactics", rd("tactics.csv"), None)
tb["conf"] = table("t_top_confusions", rd("confusions.csv"), None)
tb["ps"] = table("t_parent_sub", rd("parent_sub.csv"), None)
tb["cal"] = table("t_calibration", rd("calibration.csv"), None)
tb["faith"] = table("t_faithfulness", rd("faithfulness_summary.csv"), None)
tb["maxlen"] = table("t_maxlen_128_vs_256", rd("maxlen.csv"), None)
tb["eff"] = table("t_efficiency", rd("efficiency.csv"), None)
tb["thr"] = table("t_threshold_grid", rd("threshold_grid.csv"), None)
tb["ov"] = table("t_overlap_sensitivity", rd("overlap_sensitivity.csv"), ["system", "removed", "n_removed", "removed_test_ids", "n", "P@1", "MRR@3"])
tb["sa"] = table("t_support_aware_family", rd("support_aware_family.csv"), None)
ws = rd("weight_surface.csv"); tb["ws"] = table("t_weight_top10", ws[ws.dev_rank <= 10], ["matcher", "grid", "dev_rank", "w_matcher", "w_svm", "w_roberta", "w_secbert", "dev_MRR@3", "dev_P@1", "test_P@1", "test_MRR@3"])
hum = pd.read_csv(SHOW.parent / "_evidence_pack" / "07_agreement.csv"); tb["hum"] = table("t_human_agreement", hum, None)
ds = pd.DataFrame([{"item": N[k]["label"], "value": N[k]["display"], "claim_id": k} for k in ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9.multi_test", "A9.pairs_test", "A9.median_support", "A9.rare_train", "A10.combined_rows", "A10.combined_labels"]])
tb["data"] = table("t_dataset", ds, None)

# ---------------- E3: fusion definitions ----------------
fus = [("seed-averaged", "B13a", "B13b", "all components averaged over seeds 42-44, then fused once", "1 system (no seed spread)", "-"),
       ("seed-paired", "B12a", "B12b", "matcher, RoBERTa and SecBERT all from the same seed s; mean +/- sd over s = 42, 43, 44", "3 runs", "Fusion (3,1,1,1) seed-paired"),
       ("notebook (matcher seed varied)", "B12nb", "B12nb.mrr3", "matcher seed s, classifiers averaged over 3 seeds; mean +/- sd (Exp_2.1 CELL 11, final_results_table.csv)", "3 runs", "Fusion (3,1,1,1) matcher seed varied")]
rows = []
for nm, p, m, d, nr, key in fus:
    seeds = " / ".join(f"{v:.3f}" for v in ps[ps.system == key]["P@1"]) if key != "-" else "-"
    rows.append({"definition": nm, "claim_id_P@1": p, "P@1": N[p]["display"], "P@1_95%CI": ci(N[p]), "claim_id_MRR@3": m, "MRR@3": N[m]["display"], "per_seed_P@1 (42/43/44)": seeds, "runs": nr, "how computed": d})
for nm, i in (("equal weights, matcher seed 42", "B11"), ("equal weights, seed-averaged", "B11.avg")):
    rows.append({"definition": nm, "claim_id_P@1": i, "P@1": N[i]["display"], "P@1_95%CI": ci(N[i]), "claim_id_MRR@3": "-", "MRR@3": "-", "per_seed_P@1 (42/43/44)": "-", "runs": "1", "how computed": N[i]["definition"]})
tb["fus"] = table("t_fusion_definitions", pd.DataFrame(rows), None)
W("FUSION_DEFINITIONS.md", r"""
# Fusion: three definitions of the same weights (3,1,1,1)

All three use the same weights and the same components. They differ only in how the three training seeds are combined. All three reproduce from the saved files.
They are not three results. They are three ways to summarise one result, and the thesis must name the one it uses each time.

""" + (T / "t_fusion_definitions.md").read_text(encoding="utf-8") + r"""

## Where each value appears in draft v2

Source: the number ledger of draft v2 that the author pasted on 14 Nov 2026 (paragraph numbers `p` are the audit script's indices; `table` = the paragraph is a table cell).
Draft v2.2 has not been seen on this PC; re-run `scripts/audit_numbers.py` on it to refresh this list.

| draft location | value printed | definition it matches |
|---|---|---|
| abstract, p192 | 0.803 | seed-averaged `B13a` |
| reproduction text p594 and table p601 | 0.803 | seed-averaged `B13a` |
| reproduction table p610 | 0.796 +/- 0.006 (0.790, 0.796, 0.803) | seed-paired `B12a` |
| results text p637 | 0.803; 0.796 +/- 0.006; 0.800 +/- 0.001; MRR@3 0.852 +/- 0.002 | all three, named in the text |
| main results table, p640-p670 | row "seed-paired" 0.796 +/- 0.006 and MRR@3 0.852 +/- 0.002; row "seed-averaged" 0.803 | `B12a`, `B12b`, `B13a` |
| comparison table, p679-p692 (+0.029, +0.026) | deltas | computed with the seed-averaged fusion `B13a` |
| overlap-sensitivity table, p704-p722 | 0.8028 | seed-averaged `B13a` |
| support-bucket table, p745-p766 | per-bucket P@1 | seed-averaged fusion, 3-seed matcher ensemble |
| summary table, p798-p810 | +0.029, +0.026 | seed-averaged `B13a` |
| discussion p817 | 0.803 vs equal weights 0.779 | `B13a` vs `B11`: NOT like-for-like (see DIFFERENCES.md) |
| discussion p820 | "0.796 to 0.803", MRR@3 0.852 | `B12a` to `B13a`; MRR@3 from `B12b` |
| baseline table, p823-p840 | seed-paired 0.796 +/- 0.006, MRR@3 0.852 +/- 0.002; seed-averaged 0.803, MRR@3 0.856 | `B12a`, `B12b`, `B13a`, `B13b` |
| conclusion p859, appendix p929 | 0.803 | seed-averaged `B13a` |

Finding: the plan says the draft headlines the seed-paired value 0.796, but the abstract (p192) and the conclusion (p859) state 0.803 (seed-averaged).
All comparison intervals (C1, C2) and all per-bucket results are computed with the seed-averaged fusion. If 0.796 is the headline, say in each of those places that the test uses the seed-averaged system.
""")

# ---------------- per-chapter files ----------------
caveat = {
 "ch1": ["Headline P@1 depends on the fusion definition: {{B13a}} seed-averaged, {{B12a}} seed-paired, {{B12nb}} notebook. Name the one used.",
         "The gain over the matcher ensemble ({{C2}}) is not supported after Holm correction (p = {{C2.holm}}). Do not list it as a contribution.",
         "Explanations are for one RoBERTa seed, not for the fusion."],
 "ch2": ["Numbers taken from other papers are not in thesis_numbers.json. Each needs a citation; one is not found in its paper (57.83%) and one count conflicts (ATT&CK v12), see `docs/RELATED_WORK_VERIFIED.md`.",
         "The published baseline ({{F1}}, {{F2}}) was not re-run; split and training mode are not verified to match ours."],
 "ch3": ["Train is the tram slice of combined_train.csv after exact-text de-duplication; the raw tram_train.tsv is not in the folder.",
         "Overlap with train: {{A6}}. State exact and near-duplicate counts separately.",
         "{{A7}}: the 34 is RoBERTa-specific."],
 "ch4": ["Matcher weights were never saved; the matcher can only be re-scored from saved score files until notebook 04 is run.",
         "Latency was measured on one desktop CPU (`results/hardware.json`); the matcher was timed with the public base checkpoint."],
 "ch5": ["Bootstrap: 10,000 resamples, numpy default_rng(20261114), sentence-level, percentile 95% CI. The notebooks used 1,000 resamples with seed 0; do not mix the two.",
         "F1 in the notebooks ignores the {{A5.unseen}} unseen test labels; say which variant a number uses.",
         "P@1 of RoBERTa {{B7}} and SecBERT {{B8}} are 3-seed ensembles; single-seed means are {{B1.p1_seedmean}} and {{B2.p1_seedmean}}.",
         "Buckets with few sentences (unseen n = {{G4.n.unseen}}, 1-4 n = {{G4.n.1_4}}) have wide intervals; report direction, not size.",
         "Support-aware fusion was pre-registered and failed its success rule; it is a negative result, not an improvement."],
 "ch6": ["Human study: agreement at chance ({{D1}}); no plausibility claim can rest on it.",
         "The explained model and the fusion disagree on the top-1 label for {{E4}} test sentences.",
         "Fusion does not help unseen or rare techniques: P@1 {{G4.fusion.unseen}} (unseen) and {{G4.fusion.1_4}} (1-4) vs matcher {{G4.matcher.unseen}} and {{G4.matcher.1_4}}."],
}
figs = {"ch1": ["fig01_architecture"], "ch2": [], "ch3": ["fig01_architecture", "fig02_protocol", "fig04_data_long_tail"], "ch4": ["fig03_er_diagram", "fig16_latency_accuracy", "fig17_process_timeline"],
        "ch5": ["fig05_all_systems", "fig07_forest_deltas", "fig09_ablation", "fig08_weight_sensitivity", "fig06_support_buckets", "fig10_fixed_broken", "fig11_tactic_heatmap", "fig12_top_confusions", "fig13_reliability", "fig15_faithfulness_curves", "fig14_shap_examples", "fig19_human_agreement"],
        "ch6": ["fig06_support_buckets", "fig10_fixed_broken", "fig18_status_board"], "app": ["fig03_er_diagram", "fig17_process_timeline", "fig18_status_board"]}
ids = {
 "ch1": ["A1", "A2", "A3", "A4", "A5", "B13a", "B12a", "B12nb", "C1", "C1.holm", "C2", "C2.holm", "C3", "C3.holm", "E2.all", "E3.all", "D1", "F1", "F2"],
 "ch2": ["F1", "F2"],
 "ch3": pick(("A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "B14", "B3.thr", "E1", "G12")),
 "ch4": pick(("B14", "B3.thr", "H1", "H2", "G10", "E1", "E1.n")),
 "ch5": pick(("B", "C", "ABL", "D", "E", "G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9", "G11"), exclude=("B14",)),
 "ch6": ["C2", "C2.p", "C2.holm", "C3", "C3.holm", "C4", "C4.holm", "G9.v2.success", "G9.fam1", "G9.fam1.holm", "G9.v2.rare", "G9.v2.rare_base", "G4.fusion.unseen", "G4.matcher.unseen", "G4.fusion.1_4", "G4.matcher.1_4",
         "G6.unseen_r5_fusion", "D1", "D2", "D5", "E4", "E4.share", "G11.roberta", "G11.secbert", "F1", "F2", "B14.test3111", "B14.test4111"] + pick(sections=("Open work", "Limitations")),
}
ids["ch5"] = [k for k in ids["ch5"] if not k.startswith(("B14",))]
tabs = {"ch1": [], "ch2": [], "ch3": ["data", "ov"], "ch4": ["eff", "ws"], "ch5": ["systems", "fus", "per_seed", "f1", "cmp", "abl", "sup", "fb", "tac", "conf", "ps", "cal", "faith", "maxlen", "thr", "sa", "hum"],
        "ch6": ["cmp", "sup", "sa", "hum"], "app": ["per_seed", "f1", "ws", "thr", "ov", "tac", "conf", "eff"]}
titles = {"ch1": "Chapter 1: Introduction", "ch2": "Chapter 2: Related work", "ch3": "Chapter 3: Method", "ch4": "Chapter 4: Implementation", "ch5": "Chapter 5: Results", "ch6": "Chapter 6: Discussion and conclusion", "app": "Appendices"}
files = {"ch1": "ch1_intro", "ch2": "ch2_related", "ch3": "ch3_method", "ch4": "ch4_implementation", "ch5": "ch5_results", "ch6": "ch6_discussion_conclusion", "app": "appendices"}
LIT = """
## Numbers from other papers (not in thesis_numbers.json; cite each)

| number in draft | source paper | status (docs/RELATED_WORK_VERIFIED.md) |
|---|---|---|
| P@1 .770, MRR@3 .864 (TRAM, "Asymmetric") | Nguyen et al., arXiv:2401.10337, Table 2 | VERIFIED from the PDF |
| P@1 .674 (XR-LINEAR on TRAM) | same, Table 2 | VERIFIED from the PDF |
| 1.16 labels and 23 tokens per TRAM text | same, Table 1 | VERIFIED from the PDF |
| about 24 h training on one V100 | same, Limitations | VERIFIED from the PDF |
| 39,296 samples; F1 92.42% | TTPXHunter, arXiv:2403.03267 | VERIFIED (abstract) |
| "193 TTPs" for TTPXHunter | TTPXHunter, full text Fig. 9 | VERIFIED (full text, 15 Nov 2026) |
| 6,612 descriptions; 8.9 s per query | Kumarasinghe et al., AsiaCCS 2024 | VERIFIED (full text, 15 Nov 2026) |
| P@1 57.83% | Kumarasinghe et al., AsiaCCS 2024 | NOT FOUND in the full text: drop it or give its source |
| F1 24.8 of the TRAM model on AnnoCTR | Lange et al., LREC-COLING 2024 | VERIFIED (full text: "TRAM baseline 24.8") |
| 2,066 sentences, 37 techniques (TRAM-Clean) | Cheng et al., CTI2TTP, arXiv 2605.25836 | VERIFIED (full text, 15 Nov 2026) |
| 14 tactics, 193 techniques, 401 sub-techniques (ATT&CK v12) | draft cites ATT&CK | CONFLICT: Nguyen et al. state 196 techniques and 411 sub-techniques for v12.0 |
| best micro-F1 0.22 of seven open LLMs (8B-236B) on complex CTI reports; 2,076 sentences, 114 techniques | Ryan et al., arXiv 2606.18166 (2026) | VERIFIED (abstract); other data than TRAM: do not compare numbers directly |
| 29 methods on 90 reports of 3 campaigns; max F1 78.6% (SolarWinds), 54.9% (XZ Utils) | Haque et al., arXiv 2604.07470 (2026) | VERIFIED (abstract) |
| 150 reports mapped to ATT&CK version 19.1; 269 techniques | Das et al., arXiv 2607.23312 (2026) | VERIFIED (abstract and full text) |

Recent work (2026) to discuss: open-weights LLMs are weak at multi-label technique classification on complex reports (Ryan et al.), which matches our local LLM baseline (`L1`, prereg 17); campaign-level extraction differs from sentence-level TRAM evaluation (Haque et al.); current datasets already use ATT&CK v19.1 while TRAM is v12.1 (Das et al.; our drift check `AD1`).
"""
for k, f in files.items():
    body = [f"# {titles[k]}: numbers, tables, figures, caveats", "", "Every number below comes from `thesis_numbers.json` (do not retype; quote the id). Status meanings: RECOMPUTED = recomputed from saved predictions by a showcase script; "
            "VERIFIED = read from a file or code; NOTES-ONLY = a copied constant; TODO-COLAB = not yet run; NOT-FOUND = searched, absent.", ""]
    if k != "app":
        body += ["## Numbers", "", claims_table(list(dict.fromkeys(ids[k])))]
    else:
        body += ["## Numbers", "", "All entries: `../THESIS_MAP.md` (one row per id). Full list of open and missing items:", "", claims_table(pick(sections=("Open work", "Limitations")))]
    if k == "ch2": body.append(LIT)
    if tabs[k]: body += ["", "## Tables (CSV for editing, markdown for reading)", ""] + [f"- {tb[t]}" for t in tabs[k]]
    if figs[k]: body += ["", "## Figures (in `../figures/`, PNG 300 dpi and SVG; alt text in `../figures/FIGURES.md`)", ""] + [f"- `{x}.png`" for x in figs[k]]
    if k in caveat: body += ["", "## Caveats to state", ""] + [f"- {c}" for c in caveat[k]]
    if k == "ch5": body += ["", "See also `FUSION_DEFINITIONS.md`, `NEW_FINDINGS.md`, `DIFFERENCES.md`, `DO_NOT_CLAIM.md`."]
    W(f"{f}.md", "\n".join(body))

# ---------------- NEW_FINDINGS ----------------
W("NEW_FINDINGS.md", r"""
# New findings since draft v2 (all pre-registered in `../experiments/prereg/`)

## 1 Holm correction over 8 paired comparisons (prereg 01)
Family: C1-C4 and the four ablations A1-A4. Test: exact McNemar on P@1 hits; Holm step-down. Interval: paired bootstrap, 10,000 resamples.

| id | comparison | delta P@1 | 95% CI | McNemar p | Holm p | supported |
|---|---|---|---|---|---|---|
""" + "\n".join(f"| {r.id} | {r.A} minus {r.B} | {r['delta_P@1']:+.4f} | [{r.ci_lo:+.3f}, {r.ci_hi:+.3f}] | {r.p_mcnemar:.4f} | {r.p_holm:.4f} | {r.supported} |" for _, r in cm.iterrows()) + r"""

What it is: fusion beats the classifiers-only ensemble ({{C1}}, Holm p {{C1.holm}}); removing the matcher or RoBERTa lowers P@1 with support.
What it is not: evidence that fusion beats the matcher ensemble ({{C2}}, Holm p {{C2.holm}}), that SVM or SecBERT add anything to the fusion, or that RoBERTa beats SVM ({{C3}}, Holm p {{C3.holm}}).

## 2 Support-aware fusion (prereg 09 and 13): failed its rule
The matcher weight depends on the label's train support. Tuned on dev; test evaluated once per variant.
- Four-band variant: dev-selected weights {{G9.v2.weights}}; test P@1 {{G9.v2.p1}} vs {{B13a}} for (3,1,1,1); delta {{G9.fam1}} {{G9.fam1|ci}}, Holm p {{G9.fam1.holm}}.
- P@1 on sentences with rare labels (support 0-4): {{G9.v2.rare}} vs {{G9.v2.rare_base}}; small group, interval in `tables/t_support_aware_family.csv`.
- Pre-registered success rule met: {{G9.v2.success}}. Three-band variant weights: {{G9.v1.weights}}.
What it is: a direction worth testing on more data. What it is not: an improvement.

## 3 SHAP faithfulness (prereg 06), RoBERTa seed 42, {{E5.n}} sentences
| measure | SHAP order | random order | difference | 95% CI |
|---|---|---|---|---|
| deletion AUC (lower is better) | {{E5.del_auc.shap}} | {{E5.del_auc.random}} | {{E5.del_auc}} | {{E5.del_auc|ci}} |
| insertion AUC (higher is better) | {{E5.ins_auc.shap}} | {{E5.ins_auc.random}} | {{E5.ins_auc}} | {{E5.ins_auc|ci}} |
| comprehensiveness, top-3, probability | {{E5.comp_prob.shap}} | {{E5.comp_prob.random}} | {{E5.comp_prob}} | {{E5.comp_prob|ci}} |
| sufficiency, top-3, probability (lower is better) | {{E5.suff_prob.shap}} | {{E5.suff_prob.random}} | {{E5.suff_prob}} | {{E5.suff_prob|ci}} |
What it is: SHAP word order tracks what moves this model's score. What it is not: a test of human plausibility, or of the fusion.

## 4 Maximum length 256 at inference (prereg 08), 34 truncated test sentences
RoBERTa: {{G11.roberta}}. SecBERT: {{G11.secbert}}. Models were trained at 128 tokens; training at 256 was not tested.

## 5 Unseen and rare labels
- Unseen-label sentences (n = {{G4.n.unseen}}): P@1 fusion {{G4.fusion.unseen}}, matcher ensemble {{G4.matcher.unseen}}, classifiers {{G4.roberta.unseen}}.
- R@5 on the 10 unseen gold pairs: fusion {{G6.unseen_r5_fusion}}, matcher {{G6.unseen_r5_matcher}}, classifiers-only {{G6.unseen_r5_clsonly}}.
- Support 1-4 (n = {{G4.n.1_4}}): fusion {{G4.fusion.1_4}} vs matcher {{G4.matcher.1_4}}. Support 5-19 (n = {{G4.n.5_19}}): fusion {{G4.fusion.5_19}} vs matcher {{G4.matcher.5_19}}.
- Support 20-49: fusion {{G4.fusion.20_49}} vs matcher {{G4.matcher.20_49}}; 50+: {{G4.fusion.50plus}} vs {{G4.matcher.50plus}}.

## 6 Other checks
- Extended threshold grid: RoBERTa thresholds {{G3.roberta.thr_old}} -> {{G3.roberta.thr_new}}; mean change in test micro-F1 {{G3.roberta.delta}}.
- Overlap removal (exact + near, {{G12.exact_near.n}} sentences): largest P@1 change in any system {{G12.exact_near.maxdelta}}.
- Calibration: ECE RoBERTa {{G7.ece.roberta}}, SecBERT {{G7.ece.secbert}} (10 bins, top-1 probability).
""")

# ---------------- DIFFERENCES ----------------
au = pd.read_csv(R / "number_audit" / "audit_rows.csv"); ns = au[au.status == "NOT SUPPORTED"]
W("DIFFERENCES.md", r"""
# Differences between the draft and the files

Basis: the number ledger of **draft v2** pasted by the author on 14 Nov 2026 (`../results/number_audit/ledger_from_author_paste.csv`). Draft v2.2 is not on this PC.
Re-run `scripts/audit_numbers.py` on v2.2 (E7) to confirm which of these are already fixed.

## A The 8 numbers that differ from the files

| para | draft value | file value | why |
|---|---|---|---|
""" + "\n".join(f"| {int(r.para)} | `{r.token}` | see reason | {esc(r.supporting_key_or_reason)} ({esc(r.context)[:90]}) |" for _, r in ns.iterrows()) + r"""

Common cause: the draft quotes intervals from the notebook setting (1,000 resamples, seed 0) while saying 10,000 resamples. File values at 10,000 resamples:
C3 {{C3}} {{C3|ci}}; C4 {{C4}} {{C4|ci}}; MRR@3 deltas: C2 {{C2.mrr}} {{C2.mrr|ci}}, C3 {{C3.mrr}} {{C3.mrr|ci}}, C4 {{C4.mrr}} {{C4.mrr|ci}}.

## B Other contradictions and open marks found in draft v2

| para | draft says | files say | action |
|---|---|---|---|
| 604 (table) | "2 test and 1 development sentence found" | {{A6}} | replace with exact and near counts |
| 192, 859 | headline 0.803 | the plan says the headline is seed-paired {{B12a}} | pick one definition; see FUSION_DEFINITIONS.md |
| 817 | equal weights 0.779 is "0.002 to 0.005 above the controls (0.774 and 0.777)" | 0.779 uses matcher seed 42 only (`B11`); with the same seed-averaged matcher as the controls it is {{B11.avg}} | use {{B11.avg}} for the comparison, or say it is not like-for-like |
| 192, 676, 790, 854, 865 | fusion vs matcher ensemble "+0.026 (interval 0.001 to 0.051), p = 0.048", called borderline | after Holm over 8 tests: p = {{C2.holm}} | say it does not survive correction |
| 197 | ATT&CK v12: 14 tactics, 193 techniques, 401 sub-techniques | Nguyen et al. (v12.0): 196 techniques, 411 sub-techniques; our description file has {{A8.file}} entries | cite the source of the count used |
| 313 | TTPXHunter "193 TTPs" | not found in the paper's abstract | check or drop |
| 322, 323, 333, 335 | 6,612; 57.83%; 8.9 s; 24.8; 2,066; 37 | not found by web search | check each in its paper |
| 852 | SHAP "on a sample of 100 sentences" | stored SHAP covers {{E1.n}} sentences; the deletion test and rating sheet use the first 100 | separate the two |
| 848 | RoBERTa threshold 0.85 "[extended-grid analysis pending]" | done: thresholds {{G3.roberta.thr_new}}, test micro-F1 change {{G3.roberta.delta}} | fill |
| 697, 870 | "[optional: re-evaluate at 256 tokens]" | done at inference: RoBERTa {{G11.roberta}} | fill, and say training at 256 was not tested |
| 741 | "[confirm the reference system for 0.0]" | classifiers-only ensemble ({{G6.unseen_r5_clsonly}}); fusion {{G6.unseen_r5_fusion}} | fill |
| 767 | "[confirm ... three-seed ensemble or seed 42]"; 5-19 bucket values missing | matcher = 3-seed ensemble; 5-19: fusion {{G4.fusion.5_19}}, matcher {{G4.matcher.5_19}} (n = {{G4.n.5_19}}) | fill |
| 502 | "[confirm the seed]" | numpy default_rng(20261114), 10,000 resamples | fill |
| 584, 769 | "[confirm ... sampling rule ... 93 ... 10.19 definition]" | `THESIS_PLACEHOLDERS.md` section 7 | fill |
| 929 (appendix) | "[export requirements.txt]", "[copy tram_train.tsv]" | `requirements.txt` exists; tram_train.tsv is rebuilt by `_evidence_pack/09_repro/make_tram_train.py` (not shipped: licence) | fill |
| 931 (appendix) | "[confirm sampling procedure]" | first 100 of RandomState(42).permutation(725) | fill |
""")

W("DO_NOT_CLAIM.md", r"""
# Claims the evidence does not support

| do not claim | why (evidence) |
|---|---|
| Fusion beats the matcher ensemble | {{C2}} {{C2|ci}}; McNemar p {{C2.p}}; Holm p {{C2.holm}} over 8 tests |
| Transformers beat TF-IDF + SVM | RoBERTa minus SVM {{C3}} {{C3|ci}}, Holm p {{C3.holm}}; micro-F1 {{B1}} vs {{B3}} |
| SecBERT (security pre-training) beats RoBERTa, or the reverse | {{C4}} {{C4|ci}} |
| Fusion helps unseen or rare techniques | unseen P@1 {{G4.fusion.unseen}}; support 1-4: {{G4.fusion.1_4}} vs matcher {{G4.matcher.1_4}} |
| The model predicts techniques never seen in training | only the matcher can; unseen P@1 of the fusion is {{G4.fusion.unseen}}; R@5 {{G6.unseen_r5_fusion}} |
| Support-aware fusion improves results | failed its pre-registered rule ({{G9.v2.success}}); Holm p {{G9.fam1.holm}} |
| The explanations explain the fused system | they explain RoBERTa seed 42; top-1 differs from the fusion on {{E4}} sentences |
| Explanations are plausible to analysts | only study: Krippendorff alpha {{D1}} (nominal), {{D2}} (ordinal); third rater {{D5}} sentences |
| Better than the state of the art / beats Nguyen et al. | baseline not re-run; split and training mode unverified; our MRR@3 {{B13b}} is below their {{F2}} |
| (3,1,1,1) is the best weight setting | it wins the 255-setting grid only; the 1,711 grid picks (4,1,1,1); `B14` |
| Reading longer inputs would help | 256 tokens at inference: RoBERTa {{G11.roberta}}; training at 256 not tested |
| Results hold for other datasets or ATT&CK versions | one dataset, one split; label space = ATT&CK v12.1 (`A11`); drift to the current release in `AD1` |
| Train and test are disjoint | {{A6}} (effect on P@1 at most {{G12.exact_near.maxdelta}}) |
| Classifier probabilities are calibrated | ECE {{G7.ece.roberta}} (RoBERTa); mean confidence {{G7.conf.roberta}} |
""")
# ---------------- Q1 plan (15 Nov): new findings, extra do-not-claim rows, article brief, web-chat prompt ----------------
HAVE_LLM = "L1.closed.p1" in N
RS_ = [("svm", "TF-IDF + SVM"), ("roberta", "RoBERTa ens."), ("secbert", "SecBERT ens."), ("zeroshot", "bge zero-shot"), ("clsonly", "classifiers-only ens.")]
PT_ = ["mask_groups", "mask_software", "mask_iocs", "typo_5pct", "lower_nopunct"]
rob_tab = "| system | clean P@1 | " + " | ".join(PT_) + " |\n|---|---|" + "---|" * len(PT_) + "\n" + "\n".join(
    f"| {lab} | {{{{R1.{s}.clean}}}} | " + " | ".join(f"{{{{R1.{s}.{p}}}}} {{{{R1.{s}.{p}|ci}}}}" for p in PT_) + " |" for s, lab in RS_)
llm_sec = (r"""
## Q6 LLM baseline, open weights (prereg 17), qwen2.5:7b on this PC
| variant | P@1 | 95% CI | MRR@3 | R@5 | parse rate | minus matcher ens. | Holm p | minus fusion | Holm p |
|---|---|---|---|---|---|---|---|---|---|
""" + "\n".join(f"| {v} | {{{{L1.{v}.p1}}}} | {{{{L1.{v}.p1|ci}}}} | {{{{L1.{v}.mrr3}}}} | {{{{L1.{v}.r5}}}} | {{{{L1.{v}.parse}}}} | {{{{L1.{v}.d_matcher}}}} {{{{L1.{v}.d_matcher|ci}}}} | {{{{L1.{v}.d_matcher.holm}}}} | {{{{L1.{v}.d_fusion}}}} {{{{L1.{v}.d_fusion|ci}}}} | {{{{L1.{v}.d_fusion.holm}}}} |"
                for v in ("closed", "rr_matcher", "rr_zero")) + "\n\nNo variant beats the matcher ensemble, so the pre-registered hypothesis holds (D26). "
                "Letting the LLM re-rank the matcher's top 20 changes P@1 by {{L1.rr_matcher.d_matcher}} {{L1.rr_matcher.d_matcher|ci}} against the matcher alone. "
                "A 7B local model is a lower bound on LLM performance; an API model (notebook 10) is not run.\n") if HAVE_LLM else "\n## Q6 LLM baseline (prereg 17)\nRUNNING on this PC (resumable, about 8 hours). Write `[PENDING: L1]` until `results/llm_baseline.csv` exists.\n"
CP_ROWS = [("fusion", "Fusion (3,1,1,1)"), ("matcher", "Matcher (3-seed ens.)"), ("svm", "TF-IDF + SVM"), ("roberta", "RoBERTa ens."), ("secbert", "SecBERT ens.")]
wave2_sec = r"""

## Q11 Conformal prediction sets (prereg 18): calibrated on dev, TEST once, alpha 0.10, score rule
| system | coverage of all gold labels | 95% CI (Wilson) | mean set size (labels) | 95% CI |
|---|---|---|---|---|
""" + "\n".join(f"| {lab} | {{{{CP1.{k}.score.a10.cov}}}} | {{{{CP1.{k}.score.a10.cov|ci}}}} | {{{{CP1.{k}.score.a10.size}}}} | {{{{CP1.{k}.score.a10.size|ci}}}} |" for k, lab in CP_ROWS) + r"""

- H1 (0.90 inside the CI of the fusion's coverage): {{CP1.H1}}. H2 (fusion sets smaller than every component, Wilcoxon, Holm over 4): {{CP1.H2}}; fusion minus matcher {{CP1.d.matcher}} {{CP1.d.matcher|ci}} labels.
- An analyst gets about {{CP1.fusion.score.a10.size}} candidate techniques per sentence for 90% coverage of all gold labels; a fixed top-k list needs {{CP1.fusion.rank.a10.size}} for the same guarantee.
- The classifier rows are large because the z-scored components put the 553 labels outside a classifier's space at z = 0 (D27). POST-HOC, not pre-registered, with raw scores: RoBERTa {{CP2.roberta_raw.size}}, SecBERT {{CP2.secbert_raw.size}}, SVM {{CP2.svm_raw.size}} labels. The fusion's sets stay the smallest.
- The guarantee is marginal, not per label: unseen labels are covered {{CP1.b.unseen.fusion}} by the fusion and {{CP1.b.unseen.matcher}} by the matcher; labels with 1-4 training sentences {{CP1.b.1_4.fusion}} vs {{CP1.b.1_4.matcher}}.

## Q12 Abstention for analyst triage (prereg 19): confidence = top-1 minus top-2 score, thresholds on dev
| system | AURC (lower is better) | E-AURC | selective P@1, dev target 0.5 | 95% CI | test coverage |
|---|---|---|---|---|---|
""" + "\n".join(f"| {lab} | {{{{SP1.{k}.aurc}}}} | {{{{SP1.{k}.eaurc}}}} | {{{{SP1.{k}.sel50}}}} | {{{{SP1.{k}.sel50|ci}}}} | {{{{SP1.{k}.cov50}}}} |" for k, lab in CP_ROWS) + r"""

- Fusion minus component AURC: matcher {{SP1.d.matcher}} {{SP1.d.matcher|ci}} (Holm p {{SP1.d.matcher.holm}}), SVM {{SP1.d.svm}} (Holm p {{SP1.d.svm.holm}}), RoBERTa {{SP1.d.roberta}} (Holm p {{SP1.d.roberta.holm}}), SecBERT {{SP1.d.secbert}} (Holm p {{SP1.d.secbert.holm}}). All four meet the pre-registered rule; against the matcher the margin is small.
- Reading for practice: the fusion answers the most confident {{SP1.fusion.cov50}} of sentences at P@1 {{SP1.fusion.sel50}} and passes the rest to an analyst; at coverage {{SP1.fusion.cov90}} its P@1 is {{SP1.fusion.sel90}}.
- This does not overturn C2: on P@1 itself the fusion does not beat the matcher ensemble after Holm.

## Q13 Label-noise candidates (prereg 20, EXPLORATORY)
{{LN1.n}} of {{LN1.fusion_err}} fusion top-1 errors ({{LN1.share_err}}) are sentences where the fusion and all four components agree on the same wrong label. The consensus label is a sibling sub-technique in {{LN1.rel.sibling}}, shares a tactic in {{LN1.rel.same_tactic}} and shares no tactic in {{LN1.rel.other_tactic}} cases.
These are candidates for a human check (`human_study/materials_local/label_noise_review.xlsx`, author only), not label errors: a bias shared by all models produces the same pattern. Report no label-noise rate before the check.

## Q14 ATT&CK version drift (prereg 21, descriptive)
Against {{AD1.version}}: of the 737 label ids, {{AD1.ids_active}} are active, {{AD1.ids_deprecated}} deprecated and {{AD1.ids_revoked}} revoked. {{AD1.ids_nonactive_v121}} were already non-active in v12.1 (the description file keeps revoked ids); {{AD1.ids_after}} became non-active later.
{{AD1.test_any}} test sentences ({{AD1.test_share}}) carry such a label: {{AD1.test_already}} already in v12.1 (a TRAM data-quality issue) and {{AD1.test_after}} since then (T1562 Impair Defenses was split into new techniques). {{AD1.new_ids}} active techniques of the current release are outside the label space and cannot be predicted.
Median description similarity to the current text {{AD1.desc_sim}} ({{AD1.desc_lt080}} ids below 0.80). State results as valid for ATT&CK Enterprise v12.1.

## Q15 Reporting standard and Q16 related work
REFORMS checklist, 32 items with evidence and open holes: `docs/REFORMS_CHECKLIST.md`. Related work refreshed with three 2026 papers: `docs/RELATED_WORK_VERIFIED.md` section F and `ch2_related.md`.
"""
HAVE_APP, HAVE_GROUND = "APP1.verify" in N, "APP3.grounding" in N
app_sec = (r"""

## Q17 Explainer application (thesis objective c, folder `ttp_app`), checked on the thesis PC on 15 Nov 2026
- Replay of the 725 test sentences from the saved scores reproduces the registered numbers: {{APP1.verify}} (P@1, conformal tau, coverage and set size at alpha 0.10 and 0.20, triage coverage and selective P@1 at three targets, stored SHAP count, `E4`). The first run matched 15 of 16: the app's triage threshold interpolated between dev margins instead of using the prereg-19 order statistic. Fixed with a test (D29).
- Live mode (classifier-only fusion SVM + RoBERTa s42 + SecBERT s42, NOT the reported system) on CPU, one run per setting on invented sentences, seconds for scoring plus permutation SHAP: 7 words {{APP2.short.p10}} (10 permutations) / {{APP2.short.p40}} (40); 26 words {{APP2.medium.p10}} / {{APP2.medium.p40}}; 54 words {{APP2.long.p10}} / {{APP2.long.p40}}. Largest SHAP additivity error {{APP2.additivity_max}}.
- """ + ("Written explanations from local qwen2.5:7b pass grounding rule v1 (every quoted word is a top-5 positive-SHAP word; no other technique id) in {{APP3.grounding}} of the first 100 test rows with stored SHAP ({{APP3.llm_unavailable}} rows had no LLM answer; median {{APP3.seconds_median}} s per row). "
          if HAVE_GROUND else "Grounding pass rate of the written explanations: `[PENDING: APP3.grounding]`. ") + (
          "POST-HOC, rule unchanged: {{APP3.only_name}} of the failures quote only the explained technique's own id or name; {{APP3.not_in_sentence}} quote a word that is not in the sentence. A rule v2 that also accepts the explained technique's id and name is proposed in `ttp_app/README.md`; it needs a fresh row set before any v2 number is reported. "
          if "APP3.only_name" in N else "") + r"""A pass shows only that the quoted words come from SHAP; it does not show that an explanation is correct or useful (no human study; the first plausibility study is at chance, `D1`, `D2`).
- The screen warns when the explained model (RoBERTa seed 42) and the fusion disagree on top-1 (test sentences: {{E4}}), when a label is rare or not active in the latest ATT&CK release, and on known confusions; names follow ATT&CK v12.1.
- AI assistance: the application was written with Claude (claude.ai) and checked and corrected with Claude Code; the thesis must disclose this under the university's AI-use rules (`ttp_app/README.md`, section "AI assistance").
""") if HAVE_APP else "\n\n## Q17 Explainer application (thesis objective c)\nNot yet checked on the thesis PC: `[PENDING: APP1.verify]`.\n"
wave2_sec += app_sec
W("Q1_FINDINGS.md", r"""
# Q1 upgrade findings (15 Nov 2026), all pre-registered in `../experiments/prereg/` (14-21) unless marked EXPLORATORY or POST-HOC

## Q2 Robustness and shortcut test (prereg 14), TEST, change in P@1 vs clean input [95% paired CI]
""" + rob_tab + r"""

- No measurable dependence on threat-group names: masking them changes the classifiers-only ensemble by {{R1.clsonly.mask_groups}} (Holm p {{R1.fam.mask_groups}}). Only {{R1.n_groups_changed}} test sentences name a group (on those: {{R1.clsonly.mask_groups.changed}}), so only a large dependence could have been detected.
- The ensemble meets the pre-registered robustness rule for all five perturbations (Holm p: groups {{R1.fam.mask_groups}}, software {{R1.fam.mask_software}}, IOCs {{R1.fam.mask_iocs}}, typos {{R1.fam.typo_5pct}}, lower-case {{R1.fam.lower_nopunct}}).
- Single models are less robust: RoBERTa loses {{R1.roberta.lower_nopunct}} {{R1.roberta.lower_nopunct|ci}} when text is lower-cased without punctuation (a cased model).
- On the sentences that contain IOCs the ensemble drops {{R1.clsonly.mask_iocs.changed}}: IOC strings carry signal for these sentences.
- Software masking also removes legitimate evidence (tool names such as cmd.exe are often the technique), so it is an upper bound on name reliance. Fusion with the fine-tuned matcher: TODO-COLAB (weights not saved).

## Q3 Learned (stacked) fusion (prereg 15): negative result
Logistic regression over 7 features per (sentence, label), fitted on dev (C = {{ST1.C}} by 5-fold dev CV).
Test P@1 {{ST1.p1}} {{ST1.p1|ci}} vs {{B13a}} for (3,1,1,1): delta {{ST1.d3111}} {{ST1.d3111|ci}}, Holm p {{ST1.d3111.holm}}. Success rule met: {{ST1.success}}.
Unseen-label R@5 falls to {{ST1.unseen_r5}} (fusion {{G6.unseen_r5_fusion}}). The simple dev-tuned weighted sum is not beaten by a learned combiner on 604 dev sentences.

## Q4 Objective (b), TF-IDF + SVM part (prereg 16)
| training set | rows | labels | test P@1 | 95% CI | MRR@3 | unseen R@5 |
|---|---|---|---|---|---|---|
| (a) TRAM train | {{X1.a.rows}} | {{X1.a.labels}} | {{X1.a.p1}} | {{X1.a.p1|ci}} | {{X1.a.mrr3}} | 0 |
| (b) siblings only | {{X1.b.rows}} | {{X1.b.labels}} | {{X1.b.p1}} | {{X1.b.p1|ci}} | {{X1.b.mrr3}} | {{X1.b.unseen_r5}} |
| (c) TRAM + siblings | {{X1.c.rows}} | {{X1.c.labels}} | {{X1.c.p1}} | {{X1.c.p1|ci}} | {{X1.c.mrr3}} | {{X1.c.unseen_r5}} |

Siblings removed as duplicates of TRAM dev/test: {{X1.removed}}. Adding siblings lowers SVM P@1: (c) minus (a) {{X1.d.ca}} {{X1.d.ca|ci}}, Holm p {{X1.d.ca.holm}}; (b) minus (a) {{X1.d.ba}} {{X1.d.ba|ci}}.
EXPLORATORY (not a pre-registered test, read on test): with the (c) SVM inside the fusion, P@1 is {{X1.c.fusion_expl}}. This is a hypothesis for a new split or a dev-only confirmation, not a result.
The transformer part of objective (b) is notebook 08 (TODO-COLAB).

## Q5 Minimum detectable effect (power 0.8, n = 725, Holm alpha of each comparison)
| comparison | observed delta P@1 | MDE |
|---|---|---|
| fusion vs classifiers-only (C1) | {{C1}} | {{P1.C1}} |
| fusion vs matcher ensemble (C2) | {{C2}} | {{P1.C2}} |
| RoBERTa vs SVM (C3) | {{C3}} | {{P1.C3}} |
| RoBERTa vs SecBERT (C4) | {{C4}} | {{P1.C4}} |

A null result here means "no difference larger than about the MDE", never "equal".
""" + llm_sec + wave2_sec)
with open(F / "DO_NOT_CLAIM.md", "a", encoding="utf-8") as fh:
    fh.write(render(r"""| The classifiers rely on threat-group names | masking groups: {{R1.clsonly.mask_groups}} {{R1.clsonly.mask_groups|ci}}, Holm p {{R1.fam.mask_groups}} |
| Every model is robust to surface noise | the ensemble is; RoBERTa alone loses {{R1.roberta.lower_nopunct}} {{R1.roberta.lower_nopunct|ci}} on lower-cased text |
| A learned (stacked) fusion beats the weighted sum | {{ST1.d3111}} {{ST1.d3111|ci}}; success rule {{ST1.success}} |
| More training data from the sibling sources helps | SVM (c) minus (a) {{X1.d.ca}} {{X1.d.ca|ci}} |
| Sibling data improves the fusion | {{X1.c.fusion_expl}} is EXPLORATORY: not pre-registered, read on test |
| RoBERTa and the SVM perform the same | the study cannot detect differences below {{P1.C3}} (MDE); say "no difference larger than about {{P1.C3}}" |
""" + (r"""| An LLM improves on the matcher | best local variant (re-ranking) {{L1.rr_matcher.d_matcher}} {{L1.rr_matcher.d_matcher|ci}}; only a 7B open model was tested |
""" if HAVE_LLM else "") + r"""| Conformal coverage holds for every label or bucket | marginal guarantee only; unseen-label coverage of the fusion {{CP1.b.unseen.fusion}} |
| Classifier conformal sets need hundreds of labels | artefact of the z-scored representation (D27); raw scores (POST-HOC): RoBERTa {{CP2.roberta_raw.size}} labels |
| The fusion triages clearly better than the matcher | AURC difference {{SP1.d.matcher}} {{SP1.d.matcher|ci}}, Holm p {{SP1.d.matcher.holm}}: small margin |
| TRAM has a label-noise rate of N% | {{LN1.n}} unvalidated candidates (prereg 20, EXPLORATORY) |
| The results hold for the current ATT&CK release | {{AD1.test_any}} test sentences carry a label not active in {{AD1.version}}; {{AD1.new_ids}} current techniques are outside the label space |
""" + (r"""| The app's live mode shows the reported fusion | live mode is classifier-only (SVM + RoBERTa s42 + SecBERT s42); the reported fusion needs the matcher weights `[PENDING: T1.matcher_retrained_p1]` |
| The app's live conformal sets carry the coverage guarantee | live-mode thresholds are fitted on dev and never evaluated on test |
| The generated explanations are correct or help analysts | """ + ("grounding pass {{APP3.grounding}} only checks that quoted words are top-5 SHAP words" if HAVE_GROUND else "grounding not yet measured") + r"""; no human study of the explanations |
| The replay SHAP explains the fusion | it explains RoBERTa seed 42; top-1 differs from the fusion on {{E4}} |
""" if HAVE_APP else ""), N))
import shutil as _sh
_arch = SHOW.parent / "ttp_app" / "docs" / "img" / "architecture.png"
if _arch.exists():
    (F / "figures_app").mkdir(exist_ok=True); _sh.copy(_arch, F / "figures_app" / "architecture.png")
if HAVE_APP:
    W("ch4b_system_design.md", r"""
# Chapter 4b (or Chapter 5 of a project-style thesis): the explainer application as a design-science artefact

All numbers are rendered from `thesis_numbers.json`. Screenshots and the demo script are in `ttp_app/docs/DEMO_GUIDE.md` (local; they show test sentences, so they are not in this upload).

## 4b.1 Research approach: design science
The thesis follows design science research: it builds an artefact for a real problem and evaluates it (Hevner et al. 2004; the six activities of Peffers et al. 2007). Mapping of the activities to this work:
| activity (Peffers et al. 2007) | in this thesis |
|---|---|
| 1 problem identification and motivation | analysts must map threat-report sentences to ATT&CK techniques and judge how far to trust a suggestion (ch1) |
| 2 objectives of a solution | (a) accurate technique ranking, (b) more training sources, (c) an explainable tool an analyst can use |
| 3 design and development | classifiers, matcher, fusion (ch3); the explainer application (this chapter) |
| 4 demonstration | replay of the 725 test sentences and a live mode (4b.6) |
| 5 evaluation | experiments with pre-registration (ch5, Q1_FINDINGS); artefact checks (4b.5); usability study `[PENDING: T9.usability_sus]` |
| 6 communication | thesis, report, reproducible package |

## 4b.2 Requirements
| id | requirement | how it is met | evidence |
|---|---|---|---|
| FR1 | rank ATT&CK techniques for a sentence | fused scores (3,1,1,1), top 5 shown | test P@1 {{B13a}} |
| FR2 | give a candidate set with a stated coverage | split-conformal set, alpha 0.10 or 0.20, fitted on dev | coverage {{CP1.fusion.score.a10.cov}}, mean size {{CP1.fusion.score.a10.size}} |
| FR3 | say when to pass a sentence to an analyst | triage tier from the top-1 minus top-2 margin, dev thresholds | selective P@1 {{SP1.fusion.sel50}} at coverage {{SP1.fusion.cov50}} |
| FR4 | warn where the model is weak | rare-label, retired-technique (ATT&CK drift) and known-confusion warnings | `G4`, `AD1`, confusions table |
| FR5 | show why | SHAP word highlights; caution when the explained model differs from the fusion | differs on {{E4}} |
| FR6 | short written explanation that cannot invent evidence | template, or local qwen2.5:7b checked by grounding rule v1 | pass {{APP3.grounding}} |
| FR7 | state the limits next to the result | limits panel filled from the registry by id | `core.LIMITS` |
| FR8 | analyse new text | live mode, classifier-only | timings 4b.5 |
| NFR1 | reproduce the thesis numbers exactly | replay from saved scores, same formulas | {{APP1.verify}} |
| NFR2 | run on a CPU-only PC, no data leaves it | CPU inference; LLM only on localhost | live timings 4b.5 |
| NFR3 | no test-set tuning | thresholds fitted on dev only | prereg 18, 19; D29 |
| NFR4 | testable and maintainable | unit, integration and UI tests; small modules | {{APP4.tests_passed}} app tests pass |

## 4b.3 Architecture
Figure: `figures_app/architecture.png`. Data and runs (saved probabilities, matcher scores, stored SHAP) feed both the research pipeline and the app. `core.py` loads and fuses the saved scores and fits the dev thresholds; `live.py` runs the three classifiers and permutation SHAP on new text; `explain.py` writes the explanation and applies the grounding rule; `app.py` is the Streamlit user interface; `verify_artifacts.py` and the tests check the whole chain.

## 4b.4 Design decisions
- Replay from saved scores instead of retraining: the screen shows exactly the evaluated system, and every number can be checked against the thesis.
- Calibration on dev only, as pre-registered; the test set is only read.
- The explanation model is a local open-weights LLM behind a fixed grounding rule, so no text leaves the PC and the text can quote only SHAP evidence.
- Streamlit: a Python-only interface that reuses the research code.
- Honesty by design: limits panel, caution messages, `[PENDING]` for any missing number. Built with AI assistance (Claude, Claude Code), disclosed.

## 4b.5 Verification and validation of the artefact
- Reproduction: {{APP1.verify}} (`verify_artifacts.py`; the first run found one difference in the triage threshold rule, fixed with a test, D29).
- Tests: {{APP4.tests_passed}} app tests pass, {{APP4.tests_failed}} fail (unit tests, a fake thesis folder of the real shape, Streamlit AppTest of the user interface).
- Live mode on CPU (seconds, one run each): 7 words {{APP2.short.p10}} / {{APP2.short.p40}}, 26 words {{APP2.medium.p10}} / {{APP2.medium.p40}}, 54 words {{APP2.long.p10}} / {{APP2.long.p40}} at 10 / 40 permutations; additivity error at most {{APP2.additivity_max}}.
- Grounding of LLM text: {{APP3.grounding}} pass rule v1; {{APP3.only_name}} failures quote only the explained technique's own id or name (POST-HOC; rule v2 proposed, not applied).

## 4b.6 Demonstration
Five screens (see the demo guide): a correct sentence with a one-label set; a wrong sentence whose gold label is inside the conformal set; a retired technique; a rare label with low confidence and a caution message; the limits panel.

## 4b.7 Evaluation with users
Planned: 3-5 users, five tasks, System Usability Scale (Brooke 1996; benchmarks Bangor et al. 2008), descriptive only. Result: `[PENDING: T9.usability_sus]`. Kit: `ttp_app/usability/`.
""")
W("Q1_MANUSCRIPT_BRIEF.md", r"""
# Article brief for the writer (claude.ai): sentence-level ATT&CK technique mapping on TRAM

Every number below is rendered from `thesis_numbers.json`; ids are in backticks in the tables of `THESIS_MAP.md`.
Pending Colab or author work is written as `[PENDING: <id>]`. Claims listed in `DO_NOT_CLAIM.md` are never made.

## 1 One-paragraph story
Mapping CTI sentences to ATT&CK techniques is a 733-label, long-tailed problem. A description-reading bi-encoder (matcher) and three supervised classifiers make different errors. A dev-tuned z-score fusion of the four reaches test P@1 {{B13a}} {{B13a|ci}}, MRR@3 {{B13b}}, R@5 {{B13c}}. It beats the classifiers-only ensemble ({{C1}} {{C1|ci}}, Holm p {{C1.holm}}), but not the matcher ensemble with statistical support ({{C2}}, Holm p {{C2.holm}}). The tail is where it fails: the fusion gets P@1 {{G4.fusion.unseen}} on never-seen labels and {{G4.fusion.1_4}} on labels with 1-4 training sentences, where the matcher alone gets {{G4.matcher.unseen}} and {{G4.matcher.1_4}}. Three pre-registered fixes (support-aware weights, longer descriptions, a learned stacker) do not close this gap. The classifier ensemble is robust to five pre-registered input perturbations and shows no measurable dependence on threat-group names (few test sentences name one).

## 2 Contributions (each with its evidence)
1. A pre-registered, fully reproducible evaluation protocol: dev-only tuning, one test pass per configuration, paired bootstrap (10,000 resamples), exact McNemar, Holm, minimum detectable effects. Evidence: `experiments/prereg/` 01-21, `results/comparisons.csv`, `results/power_mde.csv`.
2. Description-based matching plus late fusion: matcher ensemble {{B10c}} {{B10c|ci}}; fusion {{B13a}}; weights from a 255-setting dev grid (`B14`); sensitivity to a 1,711-setting grid (`B14.avg_wide`, test {{B14.avg_wide.test}}).
3. Honest failure analysis of the tail: support buckets (`G4`), unseen R@5 (`G6`), support-aware fusion (`G9`), longer descriptions (`M1.L256.*`), stacked fusion (`ST1`).
4. Robustness and shortcut analysis (new): five pre-registered perturbations (`R1`), see `Q1_FINDINGS.md`.
5. Data-scale check (new): sibling sources hurt the SVM ({{X1.d.ca}}); transformer part `[PENDING: T6.cross_dataset]`.
6. Explanation faithfulness for RoBERTa (`E5`) and a human plausibility study at chance agreement (`D1`, `D2`); full-fusion SHAP `[PENDING: T2.full_fusion_shap]`.
7. LLM baseline with open weights (`L1`, prereg 17){llm_note}.
8. Uncertainty an analyst can use (new, wave 2): split-conformal candidate sets with a coverage guarantee (`CP1`, prereg 18; fusion about {{CP1.fusion.score.a10.size}} labels for 90% coverage) and abstention for triage (`SP1`, prereg 19; lowest AURC {{SP1.fusion.aurc}}).
9. Data validity (new, wave 2): label-noise candidates (`LN1`, EXPLORATORY), ATT&CK version drift of the label space (`AD1`), REFORMS reporting checklist (`docs/REFORMS_CHECKLIST.md`).
10. Objective (c): a CPU-only explainer application that replays the test set from saved scores and reproduces the registered numbers (`APP1`), shows conformal sets, triage tiers, rarity and ATT&CK-drift warnings, SHAP words and grounded explanations (`APP2`, `APP3`); built with AI assistance (disclosed). See `Q1_FINDINGS.md` Q17.

## 3 Research questions
- RQ1 Does description-based matching add to supervised classifiers? (C1, A1)
- RQ2 Where does fusion help and where does it fail? (G4, G5, G6, ST1, G9)
- RQ3 Are the systems robust, and do they take shortcuts? (R1)
- RQ4 Do more training sources or an LLM change the picture? (X1, L1, T6)
- RQ5 Are the explanations faithful and plausible? (E5, D1)
- RQ6 Can the system tell an analyst how sure it is, and is the label space still valid? (CP1, SP1, LN1, AD1)

## 4 Structure and what goes where
| section | content | sources |
|---|---|---|
| Introduction | problem, long tail, contributions above | ch1_intro.md |
| Related work | verified references only | ch2_related.md, docs/RELATED_WORK_VERIFIED.md |
| Data and task | TRAM splits {{A2}}; 733-label space; overlap {{A6}} | ch3_method.md, docs/DATA_CARD.md |
| Methods | classifiers, matcher (EXPLAINER_MATCHER_FUSION.md method lines), fusion, stacker, perturbations, statistics | ch3_method.md, FUSION_DEFINITIONS.md, prereg 14-17 |
| Results | main table (EXPLAINER table), comparisons, tail buckets, robustness, stacking, cross-source, LLM, conformal sets, triage | ch5_results.md, NEW_FINDINGS.md, Q1_FINDINGS.md |
| Explainability | faithfulness, human study, fusion-vs-explained gap ({{E4}}); explainer application, objective (c) (`APP1`-`APP3`, AI assistance disclosed) | ch5_results.md, Q1_FINDINGS.md Q17, `ttp_app/README.md` |
| Discussion | what is and is not supported; MDE wording | DO_NOT_CLAIM.md, Q1_FINDINGS.md Q5 |
| Threats to validity | one dataset and split; baseline not re-run; ATT&CK v12.1 vs current (`AD1`); label-noise candidates (`LN1`) | docs/THREATS_TO_VALIDITY.md, Q1_FINDINGS.md Q13-Q14 |
| Ethics, reproducibility | dual use; no sentence text shipped; hashes; tests; REFORMS checklist (appendix) | docs/ETHICS_AND_LIMITATIONS.md, INVIGILATOR_GUIDE.md, docs/REFORMS_CHECKLIST.md |

## 5 Still open before submission
| item | id | who |
|---|---|---|
| Matcher retrained with saved weights | `T1.matcher_retrained_p1` | Colab (notebook 04) |
| Full-fusion SHAP | `T2.full_fusion_shap` | Colab (06) |
| Fusion replication with the retrained matcher | `T3.fusion_replication` | Colab (05) |
| Seeds 45 and 46 | `T4.seeds_45_46` | Colab (03, 04) |
| Published baseline under our protocol | `T5.baseline_same_protocol` | Colab (09) |
| Transformers on sibling sources | `T6.cross_dataset` | Colab (08) |
| Second human study, 3+ raters | `T8.human_study_v2` | author |
| Human check of the label-noise candidates (`LN1.n` sentences) | `LN1` | author (review sheet in `human_study/materials_local/`) |
| Dataset licence variant, author metadata | `N6.data_licence` | author |

Venue: a security or applied-ML journal. Check the current quartile (SJR / JCR) and scope of each candidate before choosing; do not state a quartile from memory.
""".replace("{llm_note}", "" if HAVE_LLM else ": `[PENDING: L1]`, running on this PC"))
W("WEB_CLAUDE_PROMPT.md", r"""
# Project instructions for claude.ai (paste into the Project's custom instructions)

You are the writing partner for a thesis and journal article on mapping cyber-threat-intelligence sentences to MITRE ATT&CK techniques (TRAM data).
The uploaded files are the only source of facts.

Rules:
1. Numbers: use only values in `thesis_numbers.json`. In drafts, put the id after each number in brackets, e.g. "P@1 {{B13a}} [B13a]"; the author removes the brackets at the end. If a number is not in the file, say so and do not estimate it.
2. Uncertainty: report a 95% interval with every headline number and the Holm-adjusted p with every comparison. A non-significant result is written as "no difference larger than about <MDE>" (`power_mde.csv`), never as "equal".
3. Never write anything listed in `thesis_feed/DO_NOT_CLAIM.md`. Results marked EXPLORATORY are hypotheses, not findings.
4. Pending work: ids with status TODO-COLAB or NOT-FOUND are written as `[PENDING: <id>]`. Do not invent placeholders' values.
5. Definitions: the fusion headline is the seed-averaged system (`B13a`), see `thesis_feed/FUSION_DEFINITIONS.md`. The matcher and fusion are explained in plain language in `thesis_feed/EXPLAINER_MATCHER_FUSION.md`; use its method lines.
6. Pre-registration: every analysis since 14 Nov is pre-registered (`experiments/prereg/`); say so in the methods, and report failed pre-registered rules as negative results.
7. Literature: cite only references marked VERIFIED in `docs/RELATED_WORK_VERIFIED.md`; mark the rest `[CHECK REF]`.
8. Style: plain academic English, short sentences, no hype words ("novel", "state-of-the-art", "significantly" without a test).
9. Draft check: before changing a results paragraph, read `AUDIT_TODO.md` (numbers and confidence intervals of the newest draft that differ from the registry) and fix those first.
10. AI assistance: the explainer application (objective c, `Q1_FINDINGS.md` Q17) and the analysis code were built with AI tools (Claude, Claude Code). Keep a disclosure statement in the thesis as the university's AI-use rules require; do not hide or minimise it.

Start-up prompts the author can use:
- "Using Q1_MANUSCRIPT_BRIEF.md, draft the Results section with the main table and the comparisons, with ids in brackets."
- "Check this paragraph against thesis_numbers.json and DO_NOT_CLAIM.md and list every problem."
- "Write the Threats to Validity section from docs/THREATS_TO_VALIDITY.md and Q1_FINDINGS.md."
- "List every change the newest draft needs from AUDIT_TODO.md, with the paragraph number, the old text and the registry value."
- "Write the objective (c) section about the explainer application from Q1_FINDINGS.md Q17, including the AI-assistance disclosure."
""")
print("thesis_feed:", len(list(F.glob("*.md"))), "md files,", len(list(T.glob("*.csv"))), "csv tables")
