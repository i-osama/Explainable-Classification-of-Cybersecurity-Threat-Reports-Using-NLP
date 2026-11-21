"""T5: error and rarity analysis -> 05_*.csv, 05_errors.md, fig_rarity.png, fig_fusion_delta.png
Systems (fixed before looking at results): SVM; RoBERTa 3-seed prob-average; SecBERT 3-seed prob-average;
matcher 3-seed ensemble; fusion (3,1,1,1) seed-averaged; plus classifiers-only as a reference column."""
import json
from collections import Counter, defaultdict
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common import PACK, SHAPD, SEEDS, p_at_1, mrr_at_k, rank_topk, f1_per_label, w
from systems import build, components, fuse, rank_full, to_full

S = build(); L = S.L; Y = S.Yte; n = len(Y); LAB = np.array(S.LABELS)
Z = components(S, "test", "avg"); Zd = components(S, "dev", "avg")
def cls_avg(tag, sp="test"): return np.mean([to_full(S.cls_raw[tag, s][sp], S.cls_cols[tag, s], L, -1e9) for s in SEEDS], axis=0)
SYS = {"SVM": rank_full(S.svm_raw["test"], S.seen_idx, L), "RoBERTa": cls_avg("roberta"), "SecBERT": cls_avg("secbert"),
       "Matcher": Z["matcher"], "Fusion": fuse(Z, (3, 1, 1, 1)), "Classifiers-only": fuse(Z, (0, 1, 1, 1))}
SYS_DEV = {"SVM": rank_full(S.svm_raw["dev"], S.seen_idx, L), "RoBERTa": cls_avg("roberta", "dev"), "SecBERT": cls_avg("secbert", "dev"),
           "Matcher": Zd["matcher"], "Fusion": fuse(Zd, (3, 1, 1, 1)), "Classifiers-only": fuse(Zd, (0, 1, 1, 1))}
MAIN = ["SVM", "RoBERTa", "SecBERT", "Matcher", "Fusion"]
H = {k: p_at_1(v, Y) for k, v in SYS.items()}
TOP = {k: rank_topk(v, 1)[:, 0] for k, v in SYS.items()}
M = ["# 05 Error and rarity analysis\n",
     "Systems: SVM (refit), RoBERTa and SecBERT (3-seed probability average), Matcher (3-seed score average), Fusion (3,1,1,1) seed-averaged, "
     "Classifiers-only (reference). All on the 725 test sentences. [RECOMPUTED]\n"]

# ---------- 1. rarity buckets ----------
tc = S.train_count
rarest = np.where(Y, tc[None, :], 10**9).min(1)
BUCK = [("unseen (0)", 0, 0), ("1-4", 1, 4), ("5-9", 5, 9), ("10-19", 10, 19), ("20-49", 20, 49), ("50+", 50, 10**8)]
def bmask(v, lo, hi): return (v >= lo) & (v <= hi)
rows = []
for name, lo, hi in BUCK:
    m = bmask(rarest, lo, hi); lm = bmask(tc, lo, hi) & (Y.sum(0) > 0)        # test labels in this support bucket
    r = {"bucket(train support of rarest gold label)": name, "n_sentences": int(m.sum()), "n_test_labels": int(lm.sum())}
    for k in MAIN + ["Classifiers-only"]:
        r[f"P@1_{k}"] = H[k][m].mean() if m.any() else np.nan
        P1 = np.zeros_like(Y); P1[np.arange(n), TOP[k]] = True
        f = f1_per_label(P1, Y)
        r[f"top1_labelF1_{k}"] = f[lm].mean() if lm.any() else np.nan       # macro over labels of this bucket, top-1 as the prediction
    rows.append(r)
rar = pd.DataFrame(rows); rar.to_csv(PACK / "05_rarity_buckets.csv", index=False)
M += ["## 1. P@1 by train support of the sentence's rarest gold label\n",
      "Bucket rule fixed in the task brief: unseen, 1-4, 5-9, 10-19, 20-49, 50+. F1 column in the CSV = macro label-F1 over the test labels whose own train support falls in the bucket, using each system's top-1 label as its prediction (the matcher and the fusion have no threshold).\n",
      "| bucket | n sent. | " + " | ".join(MAIN) + " | Cls-only |", "|---|---|" + "---|" * (len(MAIN) + 1)]
for _, r in rar.iterrows():
    M.append(f"| {r.iloc[0]} | {r.n_sentences} | " + " | ".join(f"{r[f'P@1_{k}']:.3f}" for k in MAIN + ["Classifiers-only"]) + " |")

# ---------- 2. per tactic ----------
stix = json.load(open(PACK / "external" / "enterprise-attack-12.1.json", encoding="utf-8"))
tact, tname = {}, {}
for o in stix["objects"]:
    if o.get("type") != "attack-pattern": continue
    ext = [x for x in o.get("external_references", []) if x.get("source_name") == "mitre-attack"]
    if not ext: continue
    tid = ext[0]["external_id"].upper()
    if tid in tact and (o.get("revoked") or o.get("x_mitre_deprecated")): continue
    tact[tid] = sorted(p["phase_name"] for p in o.get("kill_chain_phases", []) if p.get("kill_chain_name") == "mitre-attack")
    tname[tid] = o["name"]
old = json.load(open(SHAPD / "attack_technique_names.json"))["techniques"]
def nm(t): return tname.get(t) or old.get(t, {}).get("name", "?")
test_labels = LAB[Y.sum(0) > 0]
no_tactic = [t for t in test_labels if not tact.get(t)]
rows = []
alltac = sorted({x for t in test_labels for x in tact.get(t, [])})
for ta in alltac:
    cols = np.array([ta in tact.get(t, []) for t in LAB])
    m = (Y & cols[None, :]).any(1)
    r = {"tactic": ta, "n_sentences": int(m.sum()), "n_test_labels": int((cols & (Y.sum(0) > 0)).sum())}
    for k in MAIN: r[f"P@1_{k}"] = H[k][m].mean()
    rows.append(r)
tac = pd.DataFrame(rows).sort_values("n_sentences", ascending=False); tac.to_csv(PACK / "05_per_tactic.csv", index=False)
M += ["\n## 2. Per-tactic P@1\n", "Tactics from ATT&CK Enterprise v12.1 STIX (`external/enterprise-attack-12.1.json`, downloaded from github.com/mitre-attack/attack-stix-data; "
      "not part of the original project files). A sentence is counted under every tactic of every gold label, so rows overlap. "
      f"Test labels without a tactic in v12.1 (revoked/deprecated): {no_tactic or 'none'}.\n",
      "| tactic | n | " + " | ".join(MAIN) + " |", "|---|---|" + "---|" * len(MAIN)]
for _, r in tac.iterrows():
    M.append(f"| {r.tactic} | {r.n_sentences} | " + " | ".join(f"{r[f'P@1_{k}']:.3f}" for k in MAIN) + " |")

# ---------- 3. confusions ----------
def rel(g, p):
    if p == g: return "same"
    if "." in g and p == g.split(".")[0]: return "pred is PARENT of gold"
    if "." in p and g == p.split(".")[0]: return "pred is SUB-TECHNIQUE of gold"
    if g.split(".")[0] == p.split(".")[0]: return "siblings (same parent)"
    return "unrelated technique family"
conf_rows, rel_rows = [], []
for k in MAIN:
    c = Counter(); rc = Counter()
    for i in np.where(H[k] == 0)[0]:
        p = LAB[TOP[k][i]]; golds = LAB[Y[i]]
        for g_ in golds: c[(g_, p)] += 1
        rels = [rel(g_, p) for g_ in golds]
        pr = ["pred is PARENT of gold", "pred is SUB-TECHNIQUE of gold", "siblings (same parent)", "unrelated technique family"]
        rc[next(x for x in pr if x in rels)] += 1                     # closest relation to any gold label
    for (g_, p), v in c.most_common(20):
        conf_rows.append({"system": k, "gold": g_, "gold_name": nm(g_), "predicted": p, "predicted_name": nm(p), "count": v,
                          "relation": rel(g_, p), "gold_train_support": int(tc[S.lab2i[g_]]), "pred_train_support": int(tc[S.lab2i[p]])})
    tot = int((H[k] == 0).sum())
    for x, v in rc.items(): rel_rows.append({"system": k, "relation": x, "errors": v, "share_of_errors": v / tot, "total_errors": tot})
pd.DataFrame(conf_rows).to_csv(PACK / "05_top20_confusions.csv", index=False)
relp = pd.DataFrame(rel_rows); relp.to_csv(PACK / "05_parent_sub_confusions.csv", index=False)
M += ["\n## 3. Top confusions (Fusion; all systems in `05_top20_confusions.csv`)\n",
      "Counting rule: every wrong top-1 sentence contributes one (gold, predicted) pair per gold label.\n",
      "| gold | predicted | n | relation |", "|---|---|---|---|"]
for r in [x for x in conf_rows if x["system"] == "Fusion"][:20]:
    M.append(f"| {r['gold']} {r['gold_name']} | {r['predicted']} {r['predicted_name']} | {r['count']} | {r['relation']} |")
M += ["\n## 4. Parent vs sub-technique confusions (share of each system's top-1 errors)\n",
      "| system | errors | pred is parent | pred is sub-technique | siblings | unrelated family |", "|---|---|---|---|---|---|"]
for k in MAIN:
    d = relp[relp.system == k].set_index("relation")["errors"].to_dict(); t = int((H[k] == 0).sum())
    M.append(f"| {k} | {t} | {d.get('pred is PARENT of gold', 0)} | {d.get('pred is SUB-TECHNIQUE of gold', 0)} | {d.get('siblings (same parent)', 0)} | {d.get('unrelated technique family', 0)} |")
# technique-level P@1 (parent match counts as correct)
par = np.array([l.split(".")[0] for l in LAB])
M.append("\nTechnique-level P@1 (prediction and gold reduced to the parent technique): " +
         ", ".join(f"{k} {np.mean([par[TOP[k][i]] in set(par[Y[i]]) for i in range(n)]):.3f}" for k in MAIN) + ".")

# ---------- 5. fixed vs broken ----------
dev_p1 = {k: p_at_1(v, S.Ydev).mean() for k, v in SYS_DEV.items()}
singles = ["SVM", "RoBERTa", "SecBERT", "Matcher"]
best = max(singles, key=lambda k: dev_p1[k])
M += ["\n## 5. Sentences fixed vs broken by the fusion\n",
      f"Reference = best single system chosen by **DEV** P@1 (not test): {', '.join(f'{k} {dev_p1[k]:.3f}' for k in singles)} -> **{best}** "
      f"(test P@1 {H[best].mean():.3f}). Examples = the 10 lowest test sentence ids in each group (rule fixed before looking).\n"]
fb_rows = []
for ref in [best, "Classifiers-only"]:
    fixed = np.where((H["Fusion"] == 1) & (H[ref] == 0))[0]; broken = np.where((H["Fusion"] == 0) & (H[ref] == 1))[0]
    M.append(f"- vs {ref}: fixed {len(fixed)}, broken {len(broken)}, net {len(fixed) - len(broken):+d} ({(len(fixed) - len(broken)) / n:+.4f} P@1); "
             f"both right {int(((H['Fusion'] == 1) & (H[ref] == 1)).sum())}, both wrong {int(((H['Fusion'] == 0) & (H[ref] == 0)).sum())}")
    for kind, ids in (("fixed", fixed), ("broken", broken)):
        for i in ids:
            fb_rows.append({"reference": ref, "kind": kind, "test_id": int(i), "gold": ";".join(LAB[Y[i]]), "ref_pred": LAB[TOP[ref][i]],
                            "fusion_pred": LAB[TOP["Fusion"][i]], "rarest_gold_train_support": int(rarest[i]), "n_gold": int(Y[i].sum()),
                            "text": S.test["text"].iloc[i][:300]})
fb = pd.DataFrame(fb_rows); fb.to_csv(PACK / "05_fixed_broken_all.csv", index=False)
ex = fb[fb.reference == best].sort_values("test_id").groupby("kind").head(10).sort_values(["kind", "test_id"])
ex.to_csv(PACK / "05_fixed_broken_examples.csv", index=False)
for kind in ("fixed", "broken"):
    M += [f"\n**{kind} (vs {best}), 10 lowest ids:**\n", "| id | gold | " + best + " pred | fusion pred | sentence |", "|---|---|---|---|---|"]
    for _, r in ex[ex.kind == kind].iterrows():
        M.append(f"| {r.test_id} | {r.gold} | {r.ref_pred} | {r.fusion_pred} | {r.text[:110].replace('|', '/')} |")
fbb = []
for name, lo, hi in BUCK:
    m = bmask(rarest, lo, hi)
    for ref in [best, "Classifiers-only"]:
        fbb.append({"bucket": name, "reference": ref, "n": int(m.sum()), "fixed": int(((H["Fusion"] == 1) & (H[ref] == 0) & m).sum()),
                    "broken": int(((H["Fusion"] == 0) & (H[ref] == 1) & m).sum())})
fbb = pd.DataFrame(fbb); fbb.to_csv(PACK / "05_fixed_broken_by_bucket.csv", index=False)

# ---------- 6. truncation, multi-label ----------
tr = pd.read_csv(PACK / "01_truncated_test_ids.csv")
tids = tr[tr.tokenizer.str.startswith("roberta")]["test_id"].to_numpy()
tm = np.zeros(n, bool); tm[tids] = True
multi = Y.sum(1) > 1
rows = []
for nme, m in (("truncated >128 RoBERTa tokens", tm), ("not truncated", ~tm), ("multi-label", multi), ("single-label", ~multi)):
    r = {"subset": nme, "n": int(m.sum())}
    for k in MAIN: r[f"P@1_{k}"] = H[k][m].mean(); r[f"MRR@3_{k}"] = mrr_at_k(SYS[k], Y)[m].mean()
    rows.append(r)
sub = pd.DataFrame(rows); sub.to_csv(PACK / "05_truncation_multilabel.csv", index=False)
M += ["\n## 6. Truncated sentences and multi-label sentences (P@1)\n", "| subset | n | " + " | ".join(MAIN) + " |", "|---|---|" + "---|" * len(MAIN)]
for _, r in sub.iterrows(): M.append(f"| {r.subset} | {r.n} | " + " | ".join(f"{r[f'P@1_{k}']:.3f}" for k in MAIN) + " |")
M.append("\nNote: with n=34 the 95% half-width of a P@1 value is about +/-0.15; multi-label rows are easier for P@1 by construction (more gold labels to hit).")

# ---------- 7. ECE ----------
def ece(conf, corr, bins=10):
    e = 0.0; edges = np.linspace(0, 1, bins + 1)
    for a, b in zip(edges[:-1], edges[1:]):
        m = (conf > a) & (conf <= b) if a > 0 else (conf >= a) & (conf <= b)
        if m.any(): e += m.mean() * abs(corr[m].mean() - conf[m].mean())
    return e
rows = []
for tag in ("roberta", "secbert"):
    for s in SEEDS:
        P = S.cls_raw[tag, s]["test"]; top = P.argmax(1); conf = P[np.arange(n), top]
        corr = S.Yte[:, S.cls_cols[tag, s]][np.arange(n), top].astype(float)
        rows.append({"model": tag, "seed": s, "ECE_top1_10bins": ece(conf, corr), "mean_conf": conf.mean(), "accuracy(P@1)": corr.mean()})
ec = pd.DataFrame(rows); ec.to_csv(PACK / "05_ece.csv", index=False)
M += ["\n## 7. Calibration (optional)\n", "ECE, 10 equal-width bins, confidence = sigmoid probability of the top-1 label, correctness = top-1 is gold. "
      "Only the transformer classifiers output probabilities.\n", "| model | seed | ECE | mean confidence | P@1 |", "|---|---|---|---|---|"]
for _, r in ec.iterrows(): M.append(f"| {r.model} | {r.seed} | {r.ECE_top1_10bins:.3f} | {r.mean_conf:.3f} | {r['accuracy(P@1)']:.3f} |")
M.append("\n" + "; ".join(f"{t}: ECE {ec[ec.model == t].ECE_top1_10bins.mean():.3f} +/- {ec[ec.model == t].ECE_top1_10bins.std(ddof=1):.3f}" for t in ("roberta", "secbert")))

# ---------- figures ----------
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"], "font.size": 10,
                     "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white"})
COL = {"SVM": "#999999", "RoBERTa": "#56B4E9", "SecBERT": "#009E73", "Matcher": "#E69F00", "Fusion": "#0072B2"}
HATCH = {"SVM": "", "RoBERTa": "//", "SecBERT": "..", "Matcher": "\\\\", "Fusion": ""}
fig, ax = plt.subplots(figsize=(7.2, 3.8))
x = np.arange(len(BUCK)); bw = 0.16
for j, k in enumerate(MAIN):
    ax.bar(x + (j - 2) * bw, rar[f"P@1_{k}"].to_numpy(), bw, color=COL[k], hatch=HATCH[k], edgecolor="black", linewidth=0.5, label=k)
ax.set_xticks(x); ax.set_xticklabels([f"{b[0]}\n(n = {v})" for b, v in zip(BUCK, rar.n_sentences)])
ax.set_xlabel("Training sentences for the rarest gold label of the test sentence"); ax.set_ylabel("P@1 (test)")
ax.set_ylim(0, 1.0); ax.yaxis.grid(True, linewidth=0.4, color="#cccccc"); ax.set_axisbelow(True)
ax.spines[["top", "right"]].set_visible(False); ax.legend(ncol=5, frameon=False, loc="upper left", bbox_to_anchor=(0, 1.12), fontsize=9, columnspacing=1.0, handlelength=1.4)
fig.tight_layout(); fig.savefig(PACK / "fig_rarity.png", dpi=300); plt.close(fig)

fig, ax = plt.subplots(figsize=(7.2, 3.6))
d = fbb[fbb.reference == best].reset_index(drop=True); d2 = fbb[fbb.reference == "Classifiers-only"].reset_index(drop=True)
bw = 0.38
for off, dd, lab_, c1, h in ((-bw / 2, d, f"vs. {best.lower()} ensemble", "#0072B2", ""), (bw / 2, d2, "vs. classifiers-only ensemble", "#E69F00", "//")):
    ax.bar(x + off, dd.fixed, bw, color=c1, hatch=h, edgecolor="black", linewidth=0.5, label=f"fixed / broken {lab_}")
    ax.bar(x + off, -dd.broken, bw, color="white", hatch=h, edgecolor=c1, linewidth=0.9)
    for xi, f_, b_ in zip(x + off, dd.fixed, dd.broken):
        ax.text(xi, f_ + 0.4, str(f_), ha="center", va="bottom", fontsize=8); ax.text(xi, -b_ - 0.4, str(b_), ha="center", va="top", fontsize=8)
ax.axhline(0, color="black", linewidth=0.8)
ax.set_xticks(x); ax.set_xticklabels([f"{b[0]}\n(n = {v})" for b, v in zip(BUCK, rar.n_sentences)])
ax.set_xlabel("Training sentences for the rarest gold label of the test sentence")
ax.set_ylabel("Test sentences\n(up: fixed by fusion, down: broken)")
lim = max(d.fixed.max(), d2.fixed.max(), d.broken.max(), d2.broken.max()) + 5; ax.set_ylim(-lim, lim)
ax.set_yticks(ax.get_yticks()); ax.set_yticklabels([str(int(abs(t))) for t in ax.get_yticks()])
ax.spines[["top", "right"]].set_visible(False); ax.legend(frameon=False, fontsize=9, loc="upper left")
fig.tight_layout(); fig.savefig(PACK / "fig_fusion_delta.png", dpi=300); plt.close(fig)

w(PACK / "05_errors.md", "\n".join(M)); print("\n".join(M))
