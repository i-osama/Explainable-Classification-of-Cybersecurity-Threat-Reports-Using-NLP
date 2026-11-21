"""E5: validate returned rating sheets against the protocol schema (docs/HUMAN_STUDY_PROTOCOL.md, section 5).
Input: human_study/returned/rating_sheet_R<k>.csv (one per rater), human_study/returned/raters.csv, human_study/key_PRIVATE.csv.
Nothing is dropped or imputed; every problem is reported. Writes results/human_study_validation.json (no sentence text).
Exit code 1 if any sheet fails a hard check. Usage: python scripts/validate_returned.py"""
import json, sys
from pathlib import Path
import pandas as pd

SHOW = Path(__file__).resolve().parents[1]; H = SHOW / "human_study"; RET = H / "returned"
REQ = ["no", "item_id", "predicted_technique", "rating_1_to_5", "note"]
key = pd.read_csv(H / "key_PRIVATE.csv"); ids = set(key.item_id)
sheets = sorted(RET.glob("rating_sheet_R*.csv")); report = {"n_items_in_key": len(ids), "sheets": [], "raters_file": None}; hard_fail = False
if not sheets: print("no returned sheets in", RET); sys.exit(1)
for p in sheets:
    r = {"file": p.name, "problems": []}
    try:
        d = pd.read_csv(p, encoding="utf-8-sig", dtype=str)
    except Exception as e:
        r["problems"].append(f"cannot read: {type(e).__name__}"); hard_fail = True; report["sheets"].append(r); continue
    miss_cols = [c for c in REQ if c not in d.columns]
    if miss_cols: r["problems"].append(f"missing columns {miss_cols}"); hard_fail = True; report["sheets"].append(r); continue
    got = d.item_id.dropna().tolist(); dup = sorted({x for x in got if got.count(x) > 1}); unknown = sorted(set(got) - ids); absent = sorted(ids - set(got))
    raw = d.rating_1_to_5.fillna("").str.strip(); num = pd.to_numeric(raw, errors="coerce")
    empty = raw.eq(""); invalid = ~empty & ~(num.isin([1, 2, 3, 4, 5]) & (num == num.round()))
    r.update(rows=len(d), duplicated_ids=dup, unknown_ids=unknown, missing_ids=absent, empty_ratings=int(empty.sum()), invalid_ratings=int(invalid.sum()),
             invalid_examples=raw[invalid].head(5).tolist(), share_missing=round(float(empty.sum()) / max(len(ids), 1), 3),
             rating_counts={str(k): int(v) for k, v in num[~invalid & ~empty].astype(int).value_counts().sort_index().items()})
    if dup or unknown or absent or invalid.any(): hard_fail = True; r["problems"].append("ids or ratings do not match the schema")
    if r["share_missing"] > 0.10: r["problems"].append("more than 10% missing: report separately, exclude from agreement only (protocol 5)")
    report["sheets"].append(r)
rp = RET / "raters.csv"
if rp.exists():
    rt = pd.read_csv(rp); need = ["rater_code", "role", "years_in_security", "threat_intel_experience_yes_no", "attack_framework_familiarity_1_to_5", "minutes_spent"]
    report["raters_file"] = {"rows": len(rt), "missing_columns": [c for c in need if c not in rt.columns], "empty_cells": int(rt.reindex(columns=need).isna().sum().sum()),
                             "codes_without_sheet": sorted(set(rt.get("rater_code", pd.Series(dtype=str)).astype(str)) - {p.stem.split("_")[-1] for p in sheets})}
else:
    report["raters_file"] = "missing: human_study/returned/raters.csv"
(SHOW / "results" / "human_study_validation.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
for s in report["sheets"]:
    print(f"{s['file']}: rows {s.get('rows')} | missing ids {len(s.get('missing_ids', []))} | unknown {len(s.get('unknown_ids', []))} | duplicates {len(s.get('duplicated_ids', []))} | "
          f"empty ratings {s.get('empty_ratings')} | invalid {s.get('invalid_ratings')} | {'; '.join(s['problems']) or 'OK'}")
print("raters file:", report["raters_file"]); print("VALIDATION:", "FAIL" if hard_fail else "PASS")
sys.exit(1 if hard_fail else 0)
