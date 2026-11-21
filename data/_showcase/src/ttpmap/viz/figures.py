"""One function per figure. Each reads results/*.csv (or the truth file), writes figNN_name.png + .svg, and returns a
dict(claims, source, alt) used for figures/FIGURES.md. No figure has a baked-in title; the thesis adds captions."""
from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from .. import EVIDENCE, FIGURES, RESULTS, SHAP_DIR, SHOWCASE
from .style import OI, SHORT, SYS_COLOR, SYS_HATCH, arrow, box, save, setup

MAIN = ["TF-IDF + SVM", "RoBERTa (3-seed avg)", "SecBERT (3-seed avg)", "Matcher (3-seed ens.)", "Fusion (3,1,1,1)"]
BUCKETS = ["unseen", "1-4", "5-9", "10-19", "20-49", "50+"]
R = lambda f: pd.read_csv(RESULTS / f)


def _numbers():
    return {c["id"]: c for c in json.loads((SHOWCASE / "thesis_numbers.json").read_text(encoding="utf-8"))["claims"]}


def fig01_architecture():
    fig, ax = plt.subplots(figsize=(7.2, 3.6)); ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.axis("off")
    box(ax, 0.1, 2.0, 1.5, 1.0, "CTI sentence", fc="#F2F2F2")
    comp = [("TF-IDF + linear SVM\n(one-vs-rest)", OI["grey"], 4.1, "decision values\n180 labels"), ("RoBERTa-base\nclassifier", OI["sky"], 3.0, "probabilities\n180 labels"),
            ("SecBERT\nclassifier", OI["green"], 1.9, "probabilities\n180 labels"), ("bge-base bi-encoder\nmatcher", OI["orange"], 0.8, "cosine to 733\ndescriptions")]
    for name, col, y, out in comp:
        box(ax, 2.3, y - 0.42, 2.1, 0.84, name, ec=col, lw=1.8); arrow(ax, 1.6, 2.5, 2.3, y)
        box(ax, 4.9, y - 0.36, 1.5, 0.72, out, fs=7.5, ec="#666666"); arrow(ax, 4.4, y, 4.9, y)
        box(ax, 6.7, y - 0.3, 0.9, 0.6, "z-score\nper sentence", fs=7); arrow(ax, 6.4, y, 6.7, y); arrow(ax, 7.6, y, 8.2, 2.5)
    box(ax, 0.1, 0.35, 1.5, 0.75, "ATT&CK technique\ndescriptions", fc="#F2F2F2", fs=8); arrow(ax, 1.6, 0.72, 2.3, 0.72)
    box(ax, 8.2, 2.0, 1.7, 1.0, "weighted sum\nw = (3, 1, 1, 1)\nmatcher first", ec=OI["blue"], lw=1.8, fs=8.5)
    ax.text(9.05, 1.75, "ranked techniques", ha="center", va="top", fontsize=8.5)
    save(fig, FIGURES, "fig01_architecture")
    return dict(claims="B14", source="configs/analysis.yaml (order, weights)", alt="Diagram: a sentence goes to four models (SVM, RoBERTa, SecBERT, bge matcher); each output is z-scored per sentence and summed with weights 3 for the matcher and 1 for the others to rank techniques.")


def fig02_protocol():
    fig, ax = plt.subplots(figsize=(7.2, 3.4)); ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.axis("off")
    N = _numbers()
    box(ax, 0.2, 3.6, 2.4, 1.0, f"TRAIN\n{N['A2.train']['display']} sentences", fc="#E8F1FA", ec=OI["blue"])
    box(ax, 3.8, 3.6, 2.4, 1.0, f"DEV\n{N['A2.dev']['display']} sentences", fc="#FFF4DD", ec=OI["orange"])
    box(ax, 7.4, 3.6, 2.4, 1.0, f"TEST\n{N['A2.test']['display']} sentences", fc="#FBE9E1", ec=OI["vermillion"])
    box(ax, 0.2, 1.9, 2.4, 1.1, "fit model weights\n(SVM, classifiers,\nmatcher)", fs=8.5)
    box(ax, 3.8, 1.5, 2.4, 1.5, "select on DEV only:\nbest epoch, decision\nthreshold, fusion weights,\npw vs no-pw", fs=8.5)
    box(ax, 7.4, 1.9, 2.4, 1.1, "report once per\nfixed configuration", fs=8.5)
    for x in (1.4, 5.0, 8.6): arrow(ax, x, 3.6, x, 3.0)
    arrow(ax, 2.6, 2.45, 3.8, 2.45); arrow(ax, 6.2, 2.45, 7.4, 2.45, "frozen settings")
    box(ax, 3.3, 0.2, 3.4, 0.8, "guard in code: tuning functions raise\nLeakageError on any test id", fs=8, ec=OI["vermillion"], ls="--")
    arrow(ax, 5.0, 1.0, 5.0, 1.5, color=OI["vermillion"], ls="--")
    save(fig, FIGURES, "fig02_protocol")
    return dict(claims="A2.train, A2.dev, A2.test", source="thesis_numbers.json; src/ttpmap/fusion.py", alt="Diagram of the protocol: model weights are fitted on train; epoch, threshold and fusion weights are selected on dev only; the test split is used once per frozen configuration; tuning code rejects test ids.")


def fig03_er():
    fig, ax = plt.subplots(figsize=(7.2, 3.9)); ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")
    ent = {"Sentence": (0.2, 3.3, ["id (PK)", "split", "text_sha256", "n_words", "labels[] (FK)"]), "Technique": (3.6, 3.3, ["id (PK)", "name", "tactics[]", "parent_id (FK)", "is_sub", "train/dev/test_support"]),
           "ScoreMatrix": (7.0, 3.3, ["system, seed, split", "n_sentences x n_labels", "score_kind", "source_file, sha256"]), "Prediction": (0.2, 0.3, ["sentence_id (FK)", "system", "top1, top2, top3 (FK)", "hit_at_1, rr_at_3"]),
           "RunManifest": (3.6, 0.3, ["run_id (PK)", "system, seed", "config_hash, env", "input/output sha256", "metrics, status"]), "Claim": (7.0, 0.3, ["id (PK)", "value, display, ci", "definition", "source_file, script", "status, thesis_section"])}
    for name, (x, y, fields) in ent.items():
        h = 0.36 * (len(fields) + 1) + 0.1
        ax.add_patch(plt.Rectangle((x, y), 2.8, h, fc="white", ec="black", lw=1)); ax.add_patch(plt.Rectangle((x, y + h - 0.42), 2.8, 0.42, fc="#E8F1FA", ec="black", lw=1))
        ax.text(x + 1.4, y + h - 0.21, name, ha="center", va="center", fontsize=9, fontweight="bold")
        for i, f in enumerate(fields): ax.text(x + 0.1, y + h - 0.62 - 0.36 * i, f, ha="left", va="center", fontsize=7.5)
    arrow(ax, 3.0, 4.3, 3.6, 4.3, "n : m"); arrow(ax, 7.0, 4.3, 6.4, 4.3, "columns"); arrow(ax, 1.6, 2.1, 1.6, 3.3, "1 : n"); arrow(ax, 2.7, 2.2, 3.75, 3.3); ax.text(3.05, 2.95, "top-k", fontsize=7.5, ha="right")
    arrow(ax, 6.4, 1.2, 7.0, 1.2, "feeds"); arrow(ax, 8.4, 3.3, 5.6, 2.5, "produced by", color="#666666")
    save(fig, FIGURES, "fig03_er_diagram")
    return dict(claims="-", source="src/ttpmap/schema.py; docs/DATA_DICTIONARY.md", alt="Entity-relationship diagram of the six data models: Sentence, Technique, ScoreMatrix, Prediction, RunManifest and Claim, with their fields and links.")


def fig04_data():
    t = pd.read_parquet(RESULTS / "tables" / "techniques.parquet"); s = pd.read_parquet(RESULTS / "tables" / "sentences.parquet")
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw={"width_ratios": [1, 1.7]})
    n = s.split.value_counts().reindex(["train", "dev", "test"]); multi = s.groupby("split")["labels"].apply(lambda x: (x.apply(len) > 1).sum()).reindex(n.index)
    a.bar(n.index, n - multi, color=OI["sky"], edgecolor="black", lw=0.5, label="one label"); a.bar(n.index, multi, bottom=n - multi, color=OI["orange"], edgecolor="black", lw=0.5, hatch="//", label="two or more labels")
    for i, v in enumerate(n): a.text(i, v + 40, f"{v:,}", ha="center", fontsize=8)
    a.set_ylabel("Sentences"); a.set_xlabel("Split"); a.legend(fontsize=8); a.set_ylim(0, n.max() * 1.15)
    sup = np.sort(t[t.train_support > 0].train_support.to_numpy())[::-1]
    b.bar(np.arange(1, len(sup) + 1), sup, width=1.0, color=OI["blue"]); b.set_yscale("log"); b.set_xlabel("Training labels, most to least frequent (rank)"); b.set_ylabel("Training sentences per label (log scale)")
    for thr, ls in ((5, "--"), (20, ":")): b.axhline(thr, color=OI["vermillion"], ls=ls, lw=1); b.text(len(sup), thr * 1.12, f"{thr} sentences", ha="right", fontsize=7.5, color=OI["vermillion"])
    save(fig, FIGURES, "fig04_data_long_tail")
    return dict(claims="A2, A3, A9.multi_test, A9.rare_train, A9.median_support", source="results/tables/sentences.parquet, techniques.parquet", alt="Left: bar chart of sentences per split, split into single- and multi-label. Right: training sentences per label on a log scale, ranked, showing a long tail with many labels below 5 sentences.")


def fig05_systems():
    d = R("systems.csv").set_index("system"); order = ["Frequency prior", "Matcher zero-shot", "TF-IDF + SVM", "SecBERT (3-seed avg)", "RoBERTa (3-seed avg)", "Classifiers-only ens.", "Matcher (3-seed ens.)", "Fusion equal (1,1,1,1)", "Fusion (3,1,1,1)"]
    fig, ax = plt.subplots(figsize=(7.2, 3.5)); y = np.arange(len(order))
    for off, m, mk, lab in ((0.15, "P@1", "o", "P@1"), (-0.15, "MRR@3", "s", "MRR@3")):
        v = d.loc[order, m]; lo = d.loc[order, m + "_lo"]; hi = d.loc[order, m + "_hi"]
        ax.errorbar(v, y + off, xerr=[v - lo, hi - v], fmt=mk, color=OI["blue"] if m == "P@1" else OI["vermillion"], ms=5, capsize=2.5, lw=1, label=lab, mfc="white" if m == "MRR@3" else None)
    ax.set_yticks(y); ax.set_yticklabels(order); ax.set_xlabel("Score on the test set (95% bootstrap interval over sentences)"); ax.set_xlim(0, 1); ax.xaxis.grid(True, lw=0.4, color="#cccccc"); ax.legend(loc="lower right")
    save(fig, FIGURES, "fig05_all_systems")
    return dict(claims="B0, B6, B7, B8, B9, B10a, B10c, B11.avg, B13a, B13b", source="results/systems.csv", alt="Dot plot with 95% intervals of P@1 and MRR@3 for nine systems, from the frequency prior at the bottom to the tuned fusion at the top; intervals of the five learned single systems overlap.")


def fig06_support():
    d = R("support_buckets.csv"); fig, ax = plt.subplots(figsize=(7.2, 3.7)); x = np.arange(len(BUCKETS)); bw = 0.16
    for j, k in enumerate(MAIN):
        v = d[d.system == k].set_index("bucket").loc[BUCKETS]
        ax.bar(x + (j - 2) * bw, v["P@1"], bw, color=SYS_COLOR[k], hatch=SYS_HATCH[k], edgecolor="black", lw=0.5, label=SHORT[k], yerr=[v["P@1"] - v.lo, v.hi - v["P@1"]], error_kw=dict(lw=0.7, capsize=1.5))
    ns = d.drop_duplicates("bucket").set_index("bucket").loc[BUCKETS].n_sentences
    ax.set_xticks(x); ax.set_xticklabels([f"{b}\n(n = {n})" for b, n in zip(BUCKETS, ns)]); ax.set_ylim(0, 1.0); ax.yaxis.grid(True, lw=0.4, color="#cccccc")
    ax.set_xlabel("Training sentences for the rarest gold label of the test sentence"); ax.set_ylabel("P@1 (95% bootstrap interval)"); ax.legend(ncol=5, loc="upper left", bbox_to_anchor=(0, 1.13), fontsize=9, columnspacing=1.0, handlelength=1.4)
    save(fig, FIGURES, "fig06_support_buckets")
    return dict(claims="G4.*", source="results/support_buckets.csv", alt="Grouped bars of P@1 with intervals for five systems in six label-frequency buckets; all systems rise with label frequency; only the matcher scores above zero on unseen labels and it leads on labels with 1-4 training sentences; the fusion leads from 10 training sentences upward.")


def fig07_forest():
    d = R("comparisons.csv"); lab = {"C1": "Fusion - classifiers-only", "C2": "Fusion - matcher ensemble", "C3": "RoBERTa - SVM", "C4": "RoBERTa - SecBERT", "A1": "Fusion - (no matcher)", "A2": "Fusion - (no SVM)", "A3": "Fusion - (no RoBERTa)", "A4": "Fusion - (no SecBERT)"}
    fig, ax = plt.subplots(figsize=(7.2, 3.3)); y = np.arange(len(d))[::-1]
    for yi, (_, r) in zip(y, d.iterrows()):
        c = OI["blue"] if r.supported else OI["grey"]
        ax.errorbar(r["delta_P@1"], yi, xerr=[[r["delta_P@1"] - r.ci_lo], [r.ci_hi - r["delta_P@1"]]], fmt="o", color=c, capsize=3, lw=1.3, ms=5, mfc=c if r.supported else "white")
        ax.text(0.074, yi, f"Holm p = {r.p_holm:.3f}" if r.p_holm >= 0.001 else "Holm p < 0.001", va="center", fontsize=8)
    ax.axvline(0, color="black", lw=0.8); ax.set_yticks(y); ax.set_yticklabels([f"{i}  {lab[i]}" for i in d.id]); ax.set_xlim(-0.03, 0.105)
    ax.set_xlabel("Paired difference in P@1 (95% bootstrap interval); filled = supported after Holm correction"); ax.xaxis.grid(True, lw=0.4, color="#cccccc")
    save(fig, FIGURES, "fig07_forest_deltas")
    return dict(claims="C1-C4, ABL.A1-ABL.A4 (+ .holm)", source="results/comparisons.csv", alt="Forest plot of eight paired P@1 differences with intervals and Holm-adjusted p-values; fusion minus classifiers-only and the ablations of matcher and RoBERTa are supported; fusion minus matcher ensemble and the RoBERTa comparisons are not.")


def fig08_weights():
    d = R("weight_surface.csv"); d = d[(d.matcher == "matcher_s42") & (d.grid == "wide_1711") & (d.w_roberta == 1) & (d.w_secbert == 1)]
    ws = [0, 1, 2, 3, 4, 6, 8]; fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.1))
    for ax, col, lab in ((axs[0], "dev_MRR@3", "DEV MRR@3 (selection objective)"), (axs[1], "test_P@1", "TEST P@1 (reported only)")):
        M = np.full((len(ws), len(ws)), np.nan)
        for _, r in d.iterrows(): M[ws.index(int(r.w_svm)), ws.index(int(r.w_matcher))] = r[col]
        im = ax.imshow(M, origin="lower", cmap="cividis", aspect="auto")
        for i in range(len(ws)):
            for j in range(len(ws)):
                if not np.isnan(M[i, j]): ax.text(j, i, f"{M[i, j]:.3f}"[1:], ha="center", va="center", fontsize=6.5, color="white" if M[i, j] < np.nanmean(M) else "black")
        ax.set_xticks(range(len(ws))); ax.set_xticklabels(ws); ax.set_yticks(range(len(ws))); ax.set_yticklabels(ws); ax.set_xlabel("Matcher weight"); ax.set_ylabel("SVM weight"); ax.set_title(lab, fontsize=9)
        for wm, mk in ((3, "o"), (4, "s")): ax.plot(ws.index(wm), ws.index(1), mk, mfc="none", mec=OI["vermillion"], ms=15, mew=1.5)
        fig.colorbar(im, ax=ax, fraction=0.046)
    save(fig, FIGURES, "fig08_weight_sensitivity")
    return dict(claims="B14, B14.test3111, B14.test4111, B14.top10_wide", source="results/weight_surface.csv (RoBERTa and SecBERT weights fixed at 1, matcher seed 42)", alt="Two heat maps over matcher weight and SVM weight: dev MRR@3 and test P@1. Both are flat around matcher weights 3 to 6; a circle marks (3,1,1,1) and a square marks (4,1,1,1).")


def fig09_ablation():
    d = R("ablation.csv"); fig, ax = plt.subplots(figsize=(6.0, 2.6)); y = np.arange(len(d))[::-1]
    cols = [OI["blue"]] + [OI["grey"]] * (len(d) - 1)
    ax.barh(y, d["mean"], color=cols, edgecolor="black", lw=0.5, xerr=[d["mean"] - d.lo, d.hi - d["mean"]], error_kw=dict(lw=0.8, capsize=2))
    for yi, v in zip(y, d["mean"]): ax.text(0.705, yi, f"{v:.3f}", va="center", fontsize=8, color="white")
    ax.set_yticks(y); ax.set_yticklabels(d.system); ax.set_xlim(0.70, 0.85); ax.set_xlabel("P@1 on the test set (95% bootstrap interval)"); ax.xaxis.grid(True, lw=0.4, color="#cccccc")
    save(fig, FIGURES, "fig09_ablation")
    return dict(claims="ABL.full, ABL.no_matcher, ABL.no_svm, ABL.no_roberta, ABL.no_secbert", source="results/ablation.csv", alt="Horizontal bars of P@1 for the full fusion and for the fusion with each component removed; removing the matcher costs most, removing the SVM least.")


def fig10_fixed_broken():
    d = R("fixed_broken.csv"); fig, ax = plt.subplots(figsize=(7.2, 3.4)); x = np.arange(len(BUCKETS)); bw = 0.38
    for off, ref, c, h, lab in ((-bw / 2, "Matcher (3-seed ens.)", OI["blue"], "", "vs. matcher ensemble"), (bw / 2, "Classifiers-only ens.", OI["orange"], "//", "vs. classifiers-only ensemble")):
        v = d[d.reference == ref].set_index("bucket").loc[BUCKETS]
        ax.bar(x + off, v.fixed, bw, color=c, hatch=h, edgecolor="black", lw=0.5, label=f"fixed (up) / broken (down) {lab}"); ax.bar(x + off, -v["broken"], bw, color="white", hatch=h, edgecolor=c, lw=0.9)
        for xi, f_, b_ in zip(x + off, v.fixed, v["broken"]): ax.text(xi, f_ + 0.4, str(int(f_)), ha="center", va="bottom", fontsize=8); ax.text(xi, -b_ - 0.4, str(int(b_)), ha="center", va="top", fontsize=8)
    ns = d.drop_duplicates("bucket").set_index("bucket").loc[BUCKETS].n
    ax.axhline(0, color="black", lw=0.8); ax.set_xticks(x); ax.set_xticklabels([f"{b}\n(n = {n})" for b, n in zip(BUCKETS, ns)]); lim = max(d.fixed.max(), d["broken"].max()) + 6; ax.set_ylim(-lim, lim)
    ax.set_yticks(ax.get_yticks()); ax.set_yticklabels([str(int(abs(t))) for t in ax.get_yticks()]); ax.set_xlabel("Training sentences for the rarest gold label of the test sentence"); ax.set_ylabel("Test sentences"); ax.legend(fontsize=8.5, loc="upper left")
    save(fig, FIGURES, "fig10_fixed_broken")
    return dict(claims="G5.matcher.*, G5.clsonly.*", source="results/fixed_broken.csv", alt="Diverging bars per label-frequency bucket: sentences the fusion gets right that a reference gets wrong (up) and the reverse (down). Against the matcher the fusion breaks more than it fixes for labels with 1-4 training sentences and gains from 20 upward.")


def fig11_tactics():
    d = R("tactics.csv"); n = d.drop_duplicates("tactic").set_index("tactic").n_sentences.sort_values(ascending=False); P = d.pivot(index="tactic", columns="system", values="P@1").loc[n.index, MAIN]
    fig, ax = plt.subplots(figsize=(6.6, 4.2)); im = ax.imshow(P.to_numpy(), cmap="cividis", vmin=0.3, vmax=0.9, aspect="auto")
    for i in range(P.shape[0]):
        for j in range(P.shape[1]): ax.text(j, i, f"{P.iat[i, j]:.2f}", ha="center", va="center", fontsize=8, color="white" if P.iat[i, j] < 0.6 else "black")
    ax.set_xticks(range(len(MAIN))); ax.set_xticklabels([SHORT[k] for k in MAIN]); ax.set_yticks(range(len(n))); ax.set_yticklabels([f"{t} (n = {v})" for t, v in n.items()])
    ax.spines[:].set_visible(False); fig.colorbar(im, ax=ax, fraction=0.04, label="P@1")
    save(fig, FIGURES, "fig11_tactic_heatmap")
    return dict(claims="-", source="results/tactics.csv (tactics from ATT&CK v12.1 STIX; a sentence counts under every tactic of its gold labels)", alt="Heat map of P@1 by ATT&CK tactic (rows, ordered by number of test sentences) and system (columns); small tactics such as impact, exfiltration and lateral movement score lowest.")


def fig12_confusions():
    d = R("confusions.csv"); d = d[d.system == "Fusion (3,1,1,1)"].head(12).iloc[::-1]
    fig, ax = plt.subplots(figsize=(7.2, 3.9)); y = np.arange(len(d))
    ax.barh(y, d["count"], color=OI["blue"], edgecolor="black", lw=0.5)
    ax.set_yticks(y); ax.set_yticklabels([f"{g} {gn[:26]}  ->  {p} {pn[:24]}" for g, gn, p, pn in zip(d.gold, d.gold_name, d.predicted, d.predicted_name)], fontsize=7.5)
    ax.set_xlabel("Test sentences (gold technique -> technique ranked first by the fusion)"); ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    save(fig, FIGURES, "fig12_top_confusions")
    return dict(claims="G8.family_errors.fusion", source="results/confusions.csv", alt="Horizontal bars of the twelve most frequent confusions of the fusion, each a gold technique and the technique predicted instead; the largest are Permission Groups Discovery read as Account Discovery and Credentials In Files read as OS Credential Dumping.")


def fig13_reliability():
    d = R("reliability_bins.csv"); fig, ax = plt.subplots(figsize=(4.2, 3.8)); ax.plot([0, 1], [0, 1], color="black", lw=0.8, ls="--", label="perfect calibration")
    for tag, c, mk in (("roberta", OI["sky"], "o"), ("secbert", OI["green"], "s")):
        g = d[d.model == tag].groupby("bin_lo").apply(lambda x: pd.Series({"conf": np.average(x.mean_conf.dropna(), weights=x.n[x.mean_conf.notna()]) if x.n.sum() else np.nan,
                                                                             "acc": np.average(x.accuracy.dropna(), weights=x.n[x.accuracy.notna()]) if x.n.sum() else np.nan, "n": x.n.sum()}), include_groups=False).dropna()
        g = g[g.n >= 15]
        ax.plot(g.conf, g.acc, marker=mk, color=c, lw=1.2, ms=5, label={"roberta": "RoBERTa", "secbert": "SecBERT"}[tag] + " (3 seeds pooled)")
    ax.set_xlabel("Probability of the top-1 label (bins with at least 15 sentences)"); ax.set_ylabel("Share of correct top-1 labels"); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.legend(fontsize=8); ax.grid(True, lw=0.4, color="#cccccc")
    save(fig, FIGURES, "fig13_reliability")
    return dict(claims="G7.ece.roberta, G7.ece.secbert", source="results/reliability_bins.csv", alt="Reliability diagram: observed accuracy against predicted probability for RoBERTa and SecBERT; both curves lie below the diagonal, so the classifiers are over-confident.")


def fig14_shap():
    recs = {}
    for l in open(SHAP_DIR / "shap_v2_roberta_pw_s42.jsonl", encoding="utf-8"):
        if l.strip():
            r = json.loads(l); recs[r["row"]] = r
    rule = [("correct, one gold label", lambda r: len(set(r["gold_labels"])) == 1 and r["top1_correct"]), ("correct, several gold labels", lambda r: len(set(r["gold_labels"])) >= 2 and r["top1_correct"]), ("wrong", lambda r: not r["top1_correct"])]
    ids = [min(k for k, r in recs.items() if f(r)) for _, f in rule]
    fig, axs = plt.subplots(1, 3, figsize=(7.4, 4.6))
    for ax, rid, (lab, _) in zip(axs, ids, rule):
        r = recs[rid]; v = np.array(r["shap_values"]); w = [u.strip() for u in r["units"]]; keep = np.arange(len(v)) if len(v) <= 14 else np.sort(np.argsort(-np.abs(v))[:14]); y = np.arange(len(keep))[::-1]
        ax.barh(y, v[keep], color=[OI["blue"] if x >= 0 else OI["vermillion"] for x in v[keep]], edgecolor="black", lw=0.4); ax.axvline(0, color="black", lw=0.7)
        ax.set_yticks(y); ax.set_yticklabels([x[:16] for x in np.array(w)[keep]], fontsize=7.5); ax.tick_params(axis="x", labelsize=7.5)
        ax.set_title(f"test id {rid}: {lab}\ngold {', '.join(sorted(set(r['gold_labels'])))}\npredicted {r['pred_label']} (p = {r['pred_prob']:.2f})", fontsize=7.5, loc="left")
    axs[1].set_xlabel("SHAP value: contribution of the word to the logit of the predicted technique (RoBERTa, seed 42)")
    save(fig, FIGURES, "fig14_shap_examples")
    return dict(claims="E1", source="Exp_3_0_shap/shap_v2_roberta_pw_s42.jsonl; rule: lowest test id that is (a) correct with one gold label, (b) correct with several, (c) wrong; at most 14 words by |SHAP| shown", alt="Three panels of word attributions for test sentences chosen by a fixed rule; blue bars push towards the predicted technique, red bars against it. Explains the RoBERTa classifier only; the fusion version is not available yet (TODO-COLAB).")


def fig15_faithfulness():
    d = R("faithfulness_curves.csv"); fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.0), sharey=True)
    for ax, k, lab in ((axs[0], "del", "Words masked (most important first)"), (axs[1], "ins", "Words revealed (most important first)")):
        ax.plot(d.k, d[f"{k}_shap"], marker="o", color=OI["blue"], lw=1.4, ms=4, label="SHAP order"); ax.plot(d.k, d[f"{k}_random"], marker="s", color=OI["grey"], lw=1.4, ms=4, ls="--", label="random order (mean of 5)")
        ax.set_xlabel(lab); ax.grid(True, lw=0.4, color="#cccccc"); ax.set_ylim(0, 1)
    axs[0].set_ylabel("Mean probability of the predicted technique"); axs[0].legend(fontsize=8, loc="upper right")
    axs[1].text(0.98, 0.04, f"n = {int(d.n.iloc[0])} sentences at k = 0", transform=axs[1].transAxes, ha="right", fontsize=7.5)
    save(fig, FIGURES, "fig15_faithfulness_curves")
    return dict(claims="E5.del_auc, E5.ins_auc, E5.comp_prob, E5.suff_prob, E5.n", source="results/faithfulness_curves.csv", alt="Two line charts. Deletion: the probability of the predicted technique falls much faster when words are masked in SHAP order than in random order. Insertion: it rises much faster when words are revealed in SHAP order.")


def fig16_latency():
    e = R("efficiency.csv"); s = R("systems.csv").set_index("system"); ps = R("per_seed.csv")
    acc = {"TF-IDF + SVM": s.loc["TF-IDF + SVM", "P@1"], "RoBERTa": ps[ps.system == "RoBERTa"]["P@1"].mean(), "SecBERT": ps[ps.system == "SecBERT"]["P@1"].mean(), "Matcher (bge-base)": ps[ps.system == "Matcher ft20"]["P@1"].mean()}
    fig, ax = plt.subplots(figsize=(5.4, 3.4)); cols = [OI["grey"], OI["sky"], OI["green"], OI["orange"]]
    for (_, r), c in zip(e.iterrows(), cols):
        if pd.notna(r.median_ms): ax.scatter(r.median_ms, acc[r.system], s=70, color=c, edgecolor="black", zorder=3); ax.annotate(f"{r.system}\n{r.parameters / 1e6:.0f} M parameters", (r.median_ms, acc[r.system]), xytext=(6, -4), textcoords="offset points", fontsize=7.5)
    tot = e.median_ms.sum() + 2 * e[e.system.isin(["RoBERTa", "SecBERT"])].median_ms.sum() + 2 * e[e.system.str.startswith("Matcher")].median_ms.sum()
    ax.scatter(tot, s.loc["Fusion (3,1,1,1)", "P@1"], s=90, marker="*", color=OI["blue"], edgecolor="black", zorder=3); ax.annotate("Fusion, 3 seeds per neural model\n(sum of component latencies)", (tot, s.loc["Fusion (3,1,1,1)", "P@1"]), xytext=(-8, -22), textcoords="offset points", fontsize=7.5, ha="right")
    ax.set_xscale("log"); ax.set_xlabel("Median CPU time per sentence, ms (log scale; batch size 1)"); ax.set_ylabel("P@1 on the test set (single-seed mean)"); ax.grid(True, lw=0.4, color="#cccccc"); ax.set_ylim(0.72, 0.82)
    save(fig, FIGURES, "fig16_latency_accuracy")
    return dict(claims="G10.ms.*, G10.params.*, B13a", source="results/efficiency.csv, results/hardware.json, results/per_seed.csv", alt="Scatter of accuracy against CPU latency: the SVM is fastest at similar accuracy to the transformers; the fusion is most accurate and slowest. The matcher is timed with the public base checkpoint because its fine-tuned weights were not saved.")


def fig17_timeline():
    d = pd.read_csv(RESULTS / "process_timeline.csv", parse_dates=["first_timestamp", "last_timestamp"]).sort_values("first_timestamp").reset_index(drop=True)
    tracks = list(dict.fromkeys(d.track)); pal = [OI["grey"], OI["sky"], OI["orange"], OI["blue"], OI["green"], OI["purple"], OI["vermillion"], OI["black"]]; col = dict(zip(tracks, pal))
    fig, ax = plt.subplots(figsize=(7.4, 4.6)); y = np.arange(len(d))[::-1]
    for yi, (_, r) in zip(y, d.iterrows()):
        ax.plot([r.first_timestamp, r.last_timestamp], [yi, yi], color=col[r.track], lw=5, solid_capstyle="butt"); ax.plot(r.first_timestamp, yi, "o", color=col[r.track], ms=5)
    ax.set_yticks(y); ax.set_yticklabels([e[:62] for e in d.event], fontsize=7.5); ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%d %b")); ax.grid(True, axis="x", lw=0.4, color="#cccccc")
    ax.set_xlabel("Date of the files that record each step (reconstructed from file timestamps, 2026)")
    ax.legend(handles=[plt.Line2D([0], [0], color=col[t], lw=5, label=t) for t in tracks], fontsize=7.5, ncol=4, loc="upper center", bbox_to_anchor=(0.3, 1.13))
    save(fig, FIGURES, "fig17_process_timeline")
    return dict(claims="-", source="results/process_timeline.csv (scripts/build_timeline.py)", alt="Timeline of the work from late September to mid-November 2026 in tracks: data, classifiers, matcher, fusion, explainability, human study, audit and showcase; each bar spans the timestamps of the files that record the step.")


def fig18_status():
    st = yaml.safe_load((SHOWCASE / "STATUS.yaml").read_text(encoding="utf-8"))["items"]; d = pd.DataFrame(st)
    states = ["DONE", "PARTIAL", "NEGATIVE-RESULT", "TODO-COLAB", "TODO-AUTHOR", "FUTURE-WORK", "NOT-FOUND"]; cmap = dict(zip(states, [OI["green"], OI["yellow"], OI["vermillion"], OI["sky"], OI["orange"], OI["purple"], OI["grey"]]))
    areas = list(dict.fromkeys(d.area)); P = pd.crosstab(d.area, d.state).reindex(index=areas, columns=[s for s in states if s in set(d.state)], fill_value=0)
    fig, ax = plt.subplots(figsize=(7.2, 3.6)); left = np.zeros(len(P)); y = np.arange(len(P))[::-1]
    for s in P.columns:
        ax.barh(y, P[s], left=left, color=cmap[s], edgecolor="black", lw=0.5, label=s.replace("-", " ").lower())
        for yi, v, l in zip(y, P[s], left):
            if v: ax.text(l + v / 2, yi, str(int(v)), ha="center", va="center", fontsize=8)
        left += P[s].to_numpy()
    ax.set_yticks(y); ax.set_yticklabels(P.index); ax.set_xlabel("Items on the status board (STATUS.yaml)"); ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True)); ax.legend(fontsize=7.5, ncol=4, loc="upper center", bbox_to_anchor=(0.45, 1.2))
    save(fig, FIGURES, "fig18_status_board")
    return dict(claims="-", source="STATUS.yaml", alt="Stacked bars per work area counting status-board items by state: done, partial, negative result, to do on Colab, to do by the author, not found.")


def fig19_human():
    a = pd.read_csv(SHAP_DIR / "rater_agreement_v2_roberta_pw_s42.csv"); rc = sorted([c for c in a.columns if c.startswith("rating_")], key=lambda c: (a[c] == 2).mean())
    ct = pd.crosstab(a[rc[0]], a[rc[1]]).reindex(index=[0, 1, 2], columns=[0, 1, 2], fill_value=0); N = _numbers()
    fig, (ax, b) = plt.subplots(1, 2, figsize=(7.2, 3.1), gridspec_kw={"width_ratios": [1, 1.25]})
    im = ax.imshow(ct.to_numpy(), cmap="cividis", origin="lower")
    for i in range(3):
        for j in range(3): ax.text(j, i, int(ct.iat[i, j]), ha="center", va="center", color="white" if ct.iat[i, j] < ct.to_numpy().max() / 2 else "black", fontsize=10)
    ax.set_xticks(range(3)); ax.set_yticks(range(3)); ax.set_xlabel("Rater B rating"); ax.set_ylabel("Rater A rating"); ax.spines[:].set_visible(False)
    keys = [("D1", "Krippendorff alpha\n(nominal)"), ("D2", "Krippendorff alpha\n(ordinal)"), ("D3", "Fleiss kappa"), ("D4", "Cohen kappa"), ("D4.lin", "Cohen kappa\n(linear weights)")]
    v = [float(N[k]["value"]) for k, _ in keys]; y = np.arange(len(keys))[::-1]
    b.barh(y, v, color=OI["grey"], edgecolor="black", lw=0.5); b.axvline(0, color="black", lw=0.8); b.axvline(0.667, color=OI["vermillion"], ls="--", lw=1); b.text(0.667, len(keys) - 0.45, "0.667: lowest value usually\naccepted for tentative conclusions", fontsize=7, color=OI["vermillion"], ha="center")
    b.set_yticks(y); b.set_yticklabels([l for _, l in keys], fontsize=8); b.set_xlim(-0.2, 1.0); b.set_xlabel("Agreement between the two complete raters (100 sentences)")
    for yi, x in zip(y, v): b.text(max(x, 0) + 0.02, yi, f"{x:+.3f}", va="center", fontsize=8)
    save(fig, FIGURES, "fig19_human_agreement")
    return dict(claims="D1, D2, D3, D4, D4.lin, D5", source="Exp_3_0_shap/rater_agreement_v2_roberta_pw_s42.csv; _evidence_pack/07_agreement.csv", alt="Left: 3 by 3 table of the two raters' ratings (0, 1, 2) for 100 sentences; most mass is where rater A gave 1 or 2 and rater B gave 2. Right: agreement coefficients, all near zero and far below the 0.667 reference line.")


ALL = [fig01_architecture, fig02_protocol, fig03_er, fig04_data, fig05_systems, fig06_support, fig07_forest, fig08_weights, fig09_ablation, fig10_fixed_broken, fig11_tactics,
       fig12_confusions, fig13_reliability, fig14_shap, fig15_faithfulness, fig16_latency, fig17_timeline, fig18_status, fig19_human]
TITLES = {"fig01": "Architecture of the four components and the fusion", "fig02": "Protocol and leakage guard", "fig03": "Data model (ER diagram)", "fig04": "Split sizes and label long tail",
          "fig05": "All systems with confidence intervals", "fig06": "P@1 by train-support bucket", "fig07": "Forest plot of paired differences", "fig08": "Weight sensitivity", "fig09": "Component ablation",
          "fig10": "Sentences fixed and broken by the fusion", "fig11": "P@1 by tactic", "fig12": "Most frequent confusions of the fusion", "fig13": "Reliability diagram", "fig14": "SHAP examples (rule-selected)",
          "fig15": "Faithfulness curves", "fig16": "Latency versus accuracy", "fig17": "Process timeline", "fig18": "Status board", "fig19": "Human-study agreement"}


def make_all():
    setup(); rows = []
    for f in ALL:
        meta = f(); name = f.__name__; files = sorted(p.name for p in FIGURES.glob(name.split("_")[0] + "_*")); stem = files[0].rsplit(".", 1)[0]
        rows.append((stem, TITLES[name.split("_")[0]], meta))
    L = ["# FIGURES", "", "Every figure is produced by `src/ttpmap/viz/figures.py` (run `python scripts/make_figures.py`) from the listed source, as 300 dpi PNG and SVG, "
         "serif font, colour-blind-safe palette, no title inside the image. Claim ids refer to `thesis_numbers.json`.", "",
         "| file (.png, .svg) | content | claim ids | source | function | alt text |", "|---|---|---|---|---|---|"]
    for (stem, title, m), f in zip(rows, ALL): L.append(f"| {stem} | {title} | {m['claims']} | {m['source']} | `{f.__name__}` | {m['alt']} |")
    L += ["", "Colab-dependent content: fig14 shows the RoBERTa explanations only. A full-fusion version needs the outputs of notebooks 04 and 06 (TODO-COLAB); no placeholder image is shipped for it."]
    (FIGURES / "FIGURES.md").write_text("\n".join(L), encoding="utf-8")
    return rows
