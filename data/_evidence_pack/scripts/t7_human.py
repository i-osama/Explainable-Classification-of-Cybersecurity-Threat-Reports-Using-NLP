"""T7: human-study evidence -> 07_human.md, 07_agreement.csv. Raters are referred to by role only."""
import hashlib, json
import numpy as np, pandas as pd
import krippendorff
from sklearn.metrics import cohen_kappa_score
from statsmodels.stats.inter_rater import fleiss_kappa, aggregate_raters
from common import PACK, SHAPD, w

files = sorted(SHAPD.glob("hand_check_v2_roberta_pw_s42*.xlsx"))
def sha8(p): return hashlib.sha256(p.read_bytes()).hexdigest()[:8]
sheets = {}
for p in files:
    df = pd.read_excel(p, sheet_name="rating")
    sheets[sha8(p)] = df
# role assignment by content, not by name: A = author's sheet is the one with 49 twos (documented in Exp_3_3 output), C = sheet with <100 ratings
order = sorted(sheets, key=lambda k: (-sheets[k]["rating"].notna().sum(), -(sheets[k]["rating"] == 2).sum()))
full = [k for k in order if sheets[k]["rating"].notna().sum() == 100]
part = [k for k in order if sheets[k]["rating"].notna().sum() < 100]
A = min(full, key=lambda k: (sheets[k]["rating"] == 2).sum()); B = [k for k in full if k != A][0]; C = part[0]
role = {A: "Rater A", B: "Rater B", C: "Rater C"}
exp = [int(r) for r in np.random.RandomState(42).permutation(725)[:100]]
M = ["# 07 Human-study evidence\n", "Rating files: 3 workbooks `Exp_3_0_shap/hand_check_v2_roberta_pw_s42*.xlsx` (sheet `rating`). Raters are identified here only by "
     "role and by the first 8 hex digits of the file SHA-256 (full hashes in `00_hashes.csv`). No names or personal data are reproduced.\n",
     "## Design  [VERIFIED: Exp_3_2_hand_check CELL 0-2]\n",
     "- unit rated: one test sentence with the 3 highest positive SHAP words marked `[[word]]`, plus predicted technique id, name, status, first sentence of its description. Gold labels hidden (`SHOW_GOLD = False`).",
     "- question: do the marked words make sense as evidence for the predicted technique?",
     "- scale (ordinal, 3 levels): **2 = makes sense, 1 = partly, 0 = does not make sense**.",
     "- sampling: first 100 rows of `numpy.random.RandomState(42).permutation(725)`: a fixed random sample of the test set, no hand selection; same order as the SHAP run.",
     "- explained model: roberta_pw_s42; technique names from MITRE `attack-stix-data` master (cache `attack_technique_names.json`), not pinned to v12.\n",
     "## Raters  [RECOMPUTED from the workbooks]\n", "| role | file sha256[:8] | rows in sheet | rows rated | 2 | 1 | 0 | mean | rows match fixed sample |", "|---|---|---|---|---|---|---|---|---|"]
for k in (A, B, C):
    df = sheets[k]; r = df["rating"].dropna().astype(int)
    M.append(f"| {role[k]} | {k} | {len(df)} | {len(r)} | {(r == 2).sum()} | {(r == 1).sum()} | {(r == 0).sum()} | {r.mean():.2f} | {list(df['row'].astype(int)) == exp} |")
M += ["\nRoles: Rater A's sheet is the project author's own sheet according to the notebook output order (Exp_3_3 CELL output 'raters: ... (A), ... (B)'); "
      "the profession/expertise of Raters B and C is NOT-FOUND in any file. Rater C's rated rows: "
      f"`{sheets[C].loc[sheets[C]['rating'].notna(), 'row'].astype(int).tolist()}` (sheet positions {sheets[C].index[sheets[C]['rating'].notna()].tolist()}).\n"]

a = sheets[A]["rating"].astype(int).to_numpy(); b = sheets[B]["rating"].astype(int).to_numpy()
c = sheets[C]["rating"].to_numpy(dtype=float)
agree_csv = pd.read_csv(SHAPD / "rater_agreement_v2_roberta_pw_s42.csv")
rc = [x for x in agree_csv.columns if x.startswith("rating_")]
csv_ok = sorted([tuple(agree_csv[rc[0]].astype(int)), tuple(agree_csv[rc[1]].astype(int))]) == sorted([tuple(a), tuple(b)])

res = []
def add(name, val, note=""): res.append({"statistic": name, "value": val, "note": note})
ab = np.vstack([a, b]).astype(float)
abc = np.vstack([a, b, c]).astype(float)
add("Krippendorff alpha nominal (A,B; 100 rows)", krippendorff.alpha(ab, level_of_measurement="nominal"))
add("Krippendorff alpha ordinal (A,B; 100 rows)", krippendorff.alpha(ab, level_of_measurement="ordinal"))
add("Krippendorff alpha nominal (A,B,C; C has 3 rows)", krippendorff.alpha(abc, level_of_measurement="nominal"))
add("Krippendorff alpha ordinal (A,B,C; C has 3 rows)", krippendorff.alpha(abc, level_of_measurement="ordinal"))
tab, _ = aggregate_raters(np.vstack([a, b]).T)
add("Fleiss kappa (A,B; 100 rows)", fleiss_kappa(tab, method="fleiss"))
add("Cohen kappa unweighted (A,B)", cohen_kappa_score(a, b, labels=[0, 1, 2]))
add("Cohen kappa linear-weighted (A,B)", cohen_kappa_score(a, b, labels=[0, 1, 2], weights="linear"))
add("Cohen kappa quadratic-weighted (A,B)", cohen_kappa_score(a, b, labels=[0, 1, 2], weights="quadratic"))
add("Percent agreement exact (A,B)", float((a == b).mean()), f"{int((a == b).sum())} of 100")
add("Percent agreement within 1 point (A,B)", float((np.abs(a - b) <= 1).mean()))
add("Cohen kappa binary '2 vs not' (A,B)", cohen_kappa_score(a == 2, b == 2))
add("Cohen kappa binary '0 vs not' (A,B)", cohen_kappa_score(a == 0, b == 0))
m = ~np.isnan(c)
for nm, x in (("A", a), ("B", b)):
    add(f"Percent agreement ({nm},C) on C's {int(m.sum())} rows", float((x[m] == c[m]).mean()), f"{nm}={x[m].tolist()} C={c[m].astype(int).tolist()}; kappa undefined/meaningless at n=3 (C constant)")
# bootstrap CI for unweighted kappa and nominal alpha
rng = np.random.RandomState(42); ks, als = [], []
for _ in range(2000):
    i = rng.randint(0, 100, 100)
    try: ks.append(cohen_kappa_score(a[i], b[i], labels=[0, 1, 2]))
    except Exception: pass
    try: als.append(krippendorff.alpha(ab[:, i], level_of_measurement="nominal"))
    except Exception: pass
add("Cohen kappa unweighted 95% CI (2000 resamples, RandomState(42))", f"[{np.nanpercentile(ks, 2.5):.3f}, {np.nanpercentile(ks, 97.5):.3f}]")
add("Krippendorff alpha nominal 95% CI (same resamples)", f"[{np.nanpercentile(als, 2.5):.3f}, {np.nanpercentile(als, 97.5):.3f}]")
pd.DataFrame(res).to_csv(PACK / "07_agreement.csv", index=False)
ct = pd.crosstab(pd.Series(a, name="Rater A"), pd.Series(b, name="Rater B")).reindex(index=[0, 1, 2], columns=[0, 1, 2], fill_value=0)
M += ["## Agreement  [RECOMPUTED]\n", "| statistic | value | note |", "|---|---|---|"]
for r in res: M.append(f"| {r['statistic']} | {r['value'] if isinstance(r['value'], str) else f'{r[chr(118)+chr(97)+chr(108)+chr(117)+chr(101)]:.3f}'} | {r['note']} |")
M += ["\nContingency table (rows Rater A, columns Rater B):\n", "| A \\ B | 0 | 1 | 2 |", "|---|---|---|---|"] + [f"| {i} | {ct.loc[i, 0]} | {ct.loc[i, 1]} | {ct.loc[i, 2]} |" for i in (0, 1, 2)]
M.append(f"\nMerged file `rater_agreement_v2_roberta_pw_s42.csv` equals the two full workbooks: {csv_ok}; it has no Rater C column.\n")
v = {r["statistic"]: r["value"] for r in res}
def st(claim, val): return "MATCH" if abs(claim - val) <= 0.001 else f"**MISMATCH** (file {val:+.3f})"
M += ["## Claims D1-D5\n", "| ID | claim | recomputed | status |", "|---|---|---|---|",
      f"| D1 | Krippendorff alpha nominal -0.057 | {v['Krippendorff alpha nominal (A,B; 100 rows)']:+.3f} | {st(-0.057, v['Krippendorff alpha nominal (A,B; 100 rows)'])} |",
      f"| D2 | Krippendorff alpha ordinal 0.031 | {v['Krippendorff alpha ordinal (A,B; 100 rows)']:+.3f} | {st(0.031, v['Krippendorff alpha ordinal (A,B; 100 rows)'])} |",
      f"| D3 | Fleiss kappa -0.062 | {v['Fleiss kappa (A,B; 100 rows)']:+.3f} | {st(-0.062, v['Fleiss kappa (A,B; 100 rows)'])} |",
      f"| D4 | Cohen kappa 0.062 | unweighted {v['Cohen kappa unweighted (A,B)']:+.3f}; linear {v['Cohen kappa linear-weighted (A,B)']:+.3f}; quadratic {v['Cohen kappa quadratic-weighted (A,B)']:+.3f} | {st(0.062, v['Cohen kappa unweighted (A,B)'])} |",
      f"| D5 | third rater rated only 3 rows | {int(m.sum())} rated of {len(c)} | {'MATCH' if m.sum() == 3 else '**MISMATCH**'} |",
      "\nReading: agreement between the two full raters is at chance level; the human study cannot support a plausibility claim. "
      "The marginals differ strongly (Rater A gives '2' to 49%, Rater B to 83%), which is what drives kappa to ~0 despite 49% raw agreement."]
w(PACK / "07_human.md", "\n".join(M)); print("\n".join(M))
