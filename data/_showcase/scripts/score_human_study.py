"""Human study v2 (docs/HUMAN_STUDY_PROTOCOL.md, fixed 2026-11-14): validate the returned sheets and run the pre-registered analysis.

    python scripts/score_human_study.py            # reads human_study/key_PRIVATE.csv + human_study/returned/rating_sheet_R*.csv
    python scripts/score_human_study.py --selftest # synthetic raters in a temporary folder; writes nothing into results/

Section 5 (validation): every key item id exactly once per sheet, rating an integer 1-5; missing or invalid cells are reported, never imputed
or dropped silently; a rater with more than 10% missing cells is excluded from the agreement statistics only.
Section 6 (analysis): primary = mean(REAL) - mean(CONTROL) of the per-item mean rating, percentile bootstrap over items (10,000 resamples,
seed 20261114), plus the same per rater; the claim "explanations are rated above random words" needs lower bound > 0 AND difference >= 1.0.
Secondary on REAL items: Krippendorff alpha (ordinal, nominal) with bootstrap interval, Fleiss kappa, pairwise Cohen kappa (unweighted, linear),
exact agreement, per-rater mean and bias. Descriptive: REAL mean by whether the prediction was correct.
Outputs: results/human_study_v2_summary.json, results/human_study_v2_raters.csv, results/human_study_v2_items.csv (ids and means, no text)."""
import argparse, json, re, sys, tempfile
from itertools import combinations
from pathlib import Path
import numpy as np, pandas as pd

SHOW = Path(__file__).resolve().parents[1]; H = SHOW / "human_study"; RES = SHOW / "results"
BOOT_N, SEED = 10_000, 20261114


def load(key_path, returned):
    key = pd.read_csv(key_path); files = sorted(Path(returned).glob("rating_sheet_R*.csv"))
    sheets, issues = {}, []
    for f in files:
        rc = re.search(r"(R\d+)", f.stem).group(1); df = pd.read_csv(f, encoding="utf-8-sig", dtype=str)
        miss_cols = [c for c in ("item_id", "rating_1_to_5") if c not in df.columns]
        if miss_cols: issues.append(f"{rc}: missing columns {miss_cols}"); continue
        ids = df["item_id"].str.strip()
        for d in sorted(set(ids[ids.duplicated()])): issues.append(f"{rc}: item {d} appears more than once")
        for x in sorted(set(ids) - set(key.item_id)): issues.append(f"{rc}: unknown item {x}")
        for x in sorted(set(key.item_id) - set(ids)): issues.append(f"{rc}: item {x} missing")
        r = pd.to_numeric(df["rating_1_to_5"].str.strip(), errors="coerce")
        bad = df.loc[r.notna() & ~r.isin([1, 2, 3, 4, 5]), "item_id"].tolist() + df.loc[r.isna() & df["rating_1_to_5"].notna() & (df["rating_1_to_5"].str.strip() != ""), "item_id"].tolist()
        for x in bad: issues.append(f"{rc}: item {x} has an invalid rating {df.loc[df.item_id == x, 'rating_1_to_5'].iloc[0]!r} (counted as missing)")
        r = r.where(r.isin([1, 2, 3, 4, 5]))
        sheets[rc] = pd.Series(r.values, index=ids).groupby(level=0).first().reindex(key.item_id)
    M = pd.DataFrame(sheets).T if sheets else pd.DataFrame(columns=key.item_id)        # raters x items, NaN = missing
    return key, M, issues


def boot_diff(real, ctrl, rng, n=BOOT_N):
    real, ctrl = real[~np.isnan(real)], ctrl[~np.isnan(ctrl)]
    d = real.mean() - ctrl.mean()
    b = rng.choice(real, (n, len(real))).mean(1) - rng.choice(ctrl, (n, len(ctrl))).mean(1)
    return float(d), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def fleiss(Mi):
    """Fleiss kappa over items rated by every rater (rows = raters)."""
    X = Mi.dropna(axis=1).T.values.astype(int)
    if X.shape[0] < 2 or X.shape[1] < 2: return float("nan"), int(X.shape[0])
    from statsmodels.stats.inter_rater import fleiss_kappa
    t = np.stack([(X == k).sum(1) for k in range(1, 6)], 1); return float(fleiss_kappa(t)), int(X.shape[0])


def analyse(key, M, issues):
    rng = np.random.default_rng(SEED); out = {"protocol": "docs/HUMAN_STUDY_PROTOCOL.md (fixed 2026-11-14)", "issues": issues, "n_raters": int(len(M))}
    real_ids = key.item_id[key.condition == "real"].tolist(); ctrl_ids = key.item_id[key.condition == "control"].tolist()
    miss = M.isna().mean(1) if len(M) else pd.Series(dtype=float)
    out["missing_share"] = {r: float(v) for r, v in miss.items()}
    agree = [r for r in M.index if miss[r] <= 0.10]; out["excluded_from_agreement"] = [r for r in M.index if r not in agree]
    out["meets_min_raters"] = bool(len(M) >= 3)
    if len(M) == 0: out["status"] = "NO SHEETS RETURNED"; return out, pd.DataFrame(), pd.DataFrame()
    item_mean = M.mean(0)
    d, lo, hi = boot_diff(item_mean[real_ids].values, item_mean[ctrl_ids].values, rng)
    out["primary"] = {"diff_real_minus_control": d, "ci": [lo, hi], "mean_real": float(item_mean[real_ids].mean()), "mean_control": float(item_mean[ctrl_ids].mean()),
                      "rule_met": bool(lo > 0 and d >= 1.0), "rule": "lower bound > 0 and difference >= 1.0 scale point"}
    rows = []
    for r in M.index:
        dr, lr, hr = boot_diff(M.loc[r, real_ids].values.astype(float), M.loc[r, ctrl_ids].values.astype(float), rng)
        rows.append({"rater": r, "missing_share": float(miss[r]), "mean_real": float(np.nanmean(M.loc[r, real_ids].values.astype(float))),
                     "diff_real_minus_control": dr, "ci_lo": lr, "ci_hi": hr})
    raters = pd.DataFrame(rows)
    A = M.loc[agree, real_ids].astype(float)
    sec = {"n_raters_used": len(agree)}
    if len(agree) >= 2:
        import krippendorff
        from sklearn.metrics import cohen_kappa_score
        data = A.values
        sec["alpha_ordinal"] = float(krippendorff.alpha(reliability_data=data, level_of_measurement="ordinal"))
        sec["alpha_nominal"] = float(krippendorff.alpha(reliability_data=data, level_of_measurement="nominal"))
        bs = []
        for _ in range(2_000):                         # alpha is slow; 2,000 item resamples for its interval (stated in the summary)
            cols = rng.integers(0, data.shape[1], data.shape[1]); s = data[:, cols]
            if np.isfinite(s).sum() > 1 and len(np.unique(s[np.isfinite(s)])) > 1:
                bs.append(krippendorff.alpha(reliability_data=s, level_of_measurement="ordinal"))
        sec["alpha_ordinal_ci"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]; sec["alpha_ci_resamples"] = len(bs)
        a = sec["alpha_ordinal"]; sec["alpha_band"] = "adequate" if a >= 0.80 else "tentative" if a >= 0.667 else "below 0.667: ratings are not pooled into a plausibility score"
        sec["fleiss_kappa"], sec["fleiss_items_complete"] = fleiss(A)
        pw = []
        for r1, r2 in combinations(agree, 2):
            m = A.loc[r1].notna() & A.loc[r2].notna(); x, y = A.loc[r1][m].astype(int), A.loc[r2][m].astype(int)
            pw.append({"pair": f"{r1}-{r2}", "n": int(m.sum()), "cohen": float(cohen_kappa_score(x, y, labels=[1, 2, 3, 4, 5])),
                       "cohen_linear": float(cohen_kappa_score(x, y, labels=[1, 2, 3, 4, 5], weights="linear")), "exact": float((x == y).mean())})
        sec["pairwise"] = pw
        full = A.dropna(axis=1); sec["exact_all_raters"] = float((full.nunique(0) == 1).mean()) if full.shape[1] else float("nan")
        gm = float(np.nanmean(A.values)); sec["per_rater"] = {r: {"mean": float(np.nanmean(A.loc[r])), "bias": float(np.nanmean(A.loc[r]) - gm)} for r in agree}
    out["secondary"] = sec
    k = key.set_index("item_id"); rc = [i for i in real_ids if str(k.loc[i, "top1_correct"]) == "True"]; rw = [i for i in real_ids if str(k.loc[i, "top1_correct"]) != "True"]
    out["descriptive"] = {"mean_real_prediction_correct": float(item_mean[rc].mean()) if rc else None, "n_correct": len(rc),
                          "mean_real_prediction_wrong": float(item_mean[rw].mean()) if rw else None, "n_wrong": len(rw)}
    out["status"] = "OK" if out["meets_min_raters"] and not issues else "OK WITH ISSUES" if out["meets_min_raters"] else "FEWER THAN 3 RATERS (protocol minimum)"
    items = pd.DataFrame({"item_id": item_mean.index, "condition": k.loc[item_mean.index, "condition"].values, "mean_rating": item_mean.values,
                          "n_ratings": M.notna().sum(0).values})
    return out, raters, items


def report(out):
    print(f"status: {out['status']} | raters: {out['n_raters']} | issues: {len(out['issues'])}")
    for i in out["issues"][:15]: print("  -", i)
    if "primary" in out:
        p = out["primary"]; print(f"primary: REAL - CONTROL = {p['diff_real_minus_control']:+.2f} [{p['ci'][0]:+.2f}, {p['ci'][1]:+.2f}] -> rule met: {p['rule_met']}")
        s = out["secondary"]
        if "alpha_ordinal" in s: print(f"secondary: alpha ordinal {s['alpha_ordinal']:.3f} {[round(x, 3) for x in s['alpha_ordinal_ci']]} ({s['alpha_band']}); Fleiss {s['fleiss_kappa']:.3f}")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true"); ap.add_argument("--returned", default=str(H / "returned")); a = ap.parse_args()
    if a.selftest:
        key = pd.read_csv(H / "key_PRIVATE.csv"); rng = np.random.default_rng(1)
        with tempfile.TemporaryDirectory() as t:
            q = np.where(key.condition == "real", 3.8, 2.0) + rng.normal(0, 0.9, len(key))
            for r in (1, 2, 3):
                v = np.clip(np.rint(q + rng.normal(0, 0.4) + rng.normal(0, 0.6, len(key))), 1, 5).astype(int)
                pd.DataFrame({"item_id": key.item_id, "rating_1_to_5": v, "note": ""}).sample(frac=1, random_state=r).to_csv(Path(t) / f"rating_sheet_R{r}.csv", index=False)
            out, _, _ = analyse(*load(H / "key_PRIVATE.csv", t)); print("SELFTEST (synthetic raters, true gap 1.8; nothing written):"); report(out)
        return
    key, M, issues = load(H / "key_PRIVATE.csv", a.returned)
    out, raters, items = analyse(key, M, issues); report(out)
    if out["n_raters"] == 0: print("nothing returned yet: put the filled sheets into human_study/returned/ (see human_study/TO_SEND/RETURN_CHECKLIST.md)"); return
    if (Path(a.returned) / "raters.csv").exists(): out["rater_background"] = pd.read_csv(Path(a.returned) / "raters.csv").drop(columns=[], errors="ignore").to_dict("records")
    (RES / "human_study_v2_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    raters.to_csv(RES / "human_study_v2_raters.csv", index=False); items.to_csv(RES / "human_study_v2_items.csv", index=False)
    print("written: results/human_study_v2_summary.json, human_study_v2_raters.csv, human_study_v2_items.csv")


if __name__ == "__main__":
    main()
