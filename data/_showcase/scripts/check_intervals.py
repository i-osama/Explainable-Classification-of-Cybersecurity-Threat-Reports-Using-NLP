"""Check every confidence interval written in a thesis draft against the registry (thesis_numbers.json).

    python scripts/check_intervals.py <draft.docx> [--out results/number_audit_<draft>]

audit_numbers.py matches single numbers against ANY registry value, so a wrong interval bound that happens to equal some other
registered number passes (draft v2.2: -0.015, -0.022 and +0.003 did). This script reads "x [lo, hi]", "x (lo to hi)" and
"x ... interval of/from lo to hi", finds the registry claims whose value rounds to x, and compares lo and hi at the draft's precision.
Status: OK (a claim matches all three), DIFFERS (a claim matches x but not the bounds, or a claim is close overall), NO CLAIM (no claim
with an interval is close), POINT OUTSIDE (x is not inside [lo, hi]: not an interval, or mistyped bounds). Rounding is half up.
"""
import argparse, json, re, sys
from pathlib import Path

from decimal import Decimal, ROUND_HALF_UP

N = r"[+\-−–]?\d+\.\d+"
OPEN = r"(?:[\[\(]\s*(?:95\s*%\s*)?(?:CI|confidence interval)?\s*:?|interval (?:of|from) )"   # "(", "[", "(95% CI:", "interval of"
SEP = r"(?:,|;|to|–|−|-)"
IV = re.compile(rf"(?P<point>{N})(?P<mid>(?:(?!\d\.\d)[^\[\(\]\);]){{0,40}}?){OPEN}\s*(?P<lo>{N})\s*{SEP}\s*(?P<hi>{N})")


def _f(s):
    return float(s.replace("−", "-").replace("–", "-"))


def _d(s):
    return len(s.split(".")[1])


def _eq(x, s):
    """Registry value x written at the draft's precision, rounding half up (as authors do), equals the draft string s."""
    q = Decimal(1).scaleb(-_d(s))
    return Decimal(repr(float(x))).quantize(q, rounding=ROUND_HALF_UP) == Decimal(repr(_f(s))).quantize(q, rounding=ROUND_HALF_UP)


def find(text):
    """All intervals in one paragraph, as dicts with the raw strings point, lo, hi and the character position."""
    return [{"point": m["point"], "lo": m["lo"], "hi": m["hi"], "pos": m.start(), "list": bool(SEEDLIST.match(text, m.end()))} for m in IV.finditer(text)]


SEEDLIST = re.compile(rf"\s*(?:,|and)\s*{N}")      # a third number follows: "(0.790, 0.796, 0.803)" lists seed values, it is not an interval


def check(paras, claims):
    """DIFFERS lists the nearest claims first (|point| + |lo| + |hi| distance): claims whose value rounds to the point, plus any claim
    within 15 units of the last decimal in total, so a draft whose point estimate is also off still finds its claim."""
    cl = [c for c in claims if c.get("ci") and isinstance(c.get("value"), (int, float))]
    rows = []
    for p in paras:
        for g in find(p["text"]):
            P, L, H, d = _f(g["point"]), _f(g["lo"]), _f(g["hi"]), _d(g["point"])
            if g.get("list"):
                rows.append({"para": p["idx"], "point": g["point"], "lo": g["lo"], "hi": g["hi"], "status": "SEED LIST", "ids": "", "registry": "",
                             "context": p["text"][max(0, g["pos"] - 50): g["pos"] + 60]})
                continue
            if not min(L, H) <= P <= max(L, H):  # either not an interval (e.g. "a gap of 0.006 [0.790, 0.796]") or mistyped bounds: the author decides
                rows.append({"para": p["idx"], "point": g["point"], "lo": g["lo"], "hi": g["hi"], "status": "POINT OUTSIDE", "ids": "", "registry": "",
                             "context": p["text"][max(0, g["pos"] - 50): g["pos"] + 60]})
                continue
            dist = lambda c: abs(c["value"] - P) + abs(c["ci"][0] - L) + abs(c["ci"][1] - H)
            cand = [c for c in cl if _eq(c["value"], g["point"])]
            ok = [c for c in cand if _eq(c["ci"][0], g["lo"]) and _eq(c["ci"][1], g["hi"])]
            near = [c for c in cl if dist(c) < 15 * 10 ** -d and c not in cand]
            use = ok or sorted(cand + near, key=dist)
            rows.append({"para": p["idx"], "point": g["point"], "lo": g["lo"], "hi": g["hi"],
                         "status": "OK" if ok else "DIFFERS" if use else "NO CLAIM", "ids": ", ".join(c["id"] for c in use[:4]),
                         "registry": f"[{use[0]['ci'][0]:+.{d}f}, {use[0]['ci'][1]:+.{d}f}]" if use else "",
                         "context": p["text"][max(0, g["pos"] - 50): g["pos"] + 60]})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("docx"); ap.add_argument("--registry", default=str(Path(__file__).resolve().parents[1] / "thesis_numbers.json")); ap.add_argument("--out")
    a = ap.parse_args()
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import audit_numbers as A
    paras = [p for p in A.assign_regions(A.load_paragraphs(a.docx)) if p["region"] != "refs"]
    rows = check(paras, json.loads(Path(a.registry).read_text(encoding="utf-8"))["claims"])
    if a.out:
        import csv
        Path(a.out).mkdir(parents=True, exist_ok=True)
        with open(Path(a.out) / "intervals.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["para", "point", "lo", "hi", "status", "ids", "registry", "context"]); w.writeheader(); w.writerows(rows)
    from collections import Counter
    print("intervals:", len(rows), dict(Counter(r["status"] for r in rows)))
    for r in rows:
        if r["status"] == "DIFFERS":
            print(f"  p{r['para']}: {r['point']} [{r['lo']}, {r['hi']}] -> registry {r['ids']} {r['registry']}")
    return rows


if __name__ == "__main__":
    main()
