"""Invigilator check: (1) ledger counts from the evidence report, (2) headline numbers recomputed from saved
predictions and compared with thesis_numbers.json within 0.001, (3) every ledger claim present with a status.
Usage: python scripts/verify_claims.py      Exit code 0 only if everything matches."""
import json, re, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap import EVIDENCE, SHOWCASE, SEEDS
from ttpmap.data import build_space
from ttpmap.fusion import components, fuse, rank_space, to_full
from ttpmap.metrics import hit_at_1, rr_at_k

TOL = 0.001; ok = True
N = json.loads((SHOWCASE / "thesis_numbers.json").read_text(encoding="utf-8")); by = {c["id"]: c for c in N["claims"]}

# 1 ledger counts, parsed from the evidence report (not typed here)
rows = [l.split("|") for l in (EVIDENCE / "EVIDENCE_REPORT.md").read_text(encoding="utf-8").splitlines() if re.match(r"^\| [A-F]\d+[a-c]? \|", l)]
def cat(s):
    s = s.strip()
    if s.startswith("MISMATCH"): return "MISMATCH"
    if s.startswith("NOTES-ONLY"): return "NOTES-ONLY"
    return "MATCH-WITH-CAVEAT" if any(k in s for k in ("MISLABELLED", "qualifier", "only", "borderline", "not like-for-like", "NOT-FOUND", "no notebook")) else "MATCH"
cnt = {}
for r in rows: cnt[cat(r[5])] = cnt.get(cat(r[5]), 0) + 1
print(f"[1] evidence ledger: {len(rows)} claims -> " + ", ".join(f"{k} {v}" for k, v in sorted(cnt.items())))
miss = [r[1].strip() for r in rows if r[1].strip() not in by]
print(f"    ledger ids missing from thesis_numbers.json: {miss or 'none'}"); ok &= not miss

# 2 recompute headline numbers from saved predictions
S = build_space(); Y = S.Y["test"]; Z = components(S, "test", "avg")
def avg(tag): return np.mean([to_full(S.cls_raw[tag, s]["test"], S.cls_cols[tag, s], S.L, -1e9) for s in SEEDS], axis=0)
re_ = {"B13a": hit_at_1(fuse(Z, (3, 1, 1, 1)), Y).mean(), "B13b": rr_at_k(fuse(Z, (3, 1, 1, 1)), Y).mean(), "B9": hit_at_1(fuse(Z, (0, 1, 1, 1)), Y).mean(),
       "B10c": hit_at_1(Z["matcher"], Y).mean(), "B6": hit_at_1(rank_space(S.svm_raw["test"], S.seen_idx, S.L), Y).mean(), "B10a": hit_at_1(S.matcher_zero_test, Y).mean(),
       "B7": hit_at_1(avg("roberta"), Y).mean(), "B8": hit_at_1(avg("secbert"), Y).mean(),
       "B12a": np.mean([hit_at_1(fuse(components(S, "test", "paired", s), (3, 1, 1, 1)), Y).mean() for s in SEEDS]),
       "B12nb": np.mean([hit_at_1(fuse(components(S, "test", "nb_seed", s), (3, 1, 1, 1)), Y).mean() for s in SEEDS]),
       "B10b": np.mean([hit_at_1(S.matcher_raw[s]["test"], Y).mean() for s in SEEDS]),
       "C1": hit_at_1(fuse(Z, (3, 1, 1, 1)), Y).mean() - hit_at_1(fuse(Z, (0, 1, 1, 1)), Y).mean(), "C2": hit_at_1(fuse(Z, (3, 1, 1, 1)), Y).mean() - hit_at_1(Z["matcher"], Y).mean()}
print("[2] recomputed from saved predictions vs thesis_numbers.json (tolerance 0.001)")
for k, v in re_.items():
    j = by[k]["value"]; good = abs(v - j) <= TOL; ok &= good
    print(f"    {'OK  ' if good else 'DIFF'} {k:6s} recomputed {v:.4f}  json {j:.4f}  {by[k]['label'][:60]}")

# 3 statuses
st = {}
for c in N["claims"]: st[c["status"]] = st.get(c["status"], 0) + 1
bad = [c["id"] for c in N["claims"] if (c["value"] is None) != (c["status"] in ("NOT-FOUND", "TODO-COLAB"))]
print(f"[3] thesis_numbers.json: {len(N['claims'])} entries -> " + ", ".join(f"{k} {v}" for k, v in sorted(st.items())) + f"; value/status inconsistencies: {bad or 'none'}")
ok &= not bad
print("VERIFY: " + ("PASS" if ok else "FAIL")); sys.exit(0 if ok else 1)
