"""E7: number audit of the newest thesis .docx in E:\\Osamas Paper\\thesis\\ (read-only), then AUDIT_TODO.md.
For every UNREGISTERED number: the nearest thesis_numbers.json key of the same kind, and the likely cause.
No .docx present -> dry run on the ledger the author pasted (results/number_audit/ledger_from_author_paste.csv), labelled as such.
Usage: python scripts/audit_loop.py        (re-run whenever a new draft is saved into thesis\\)"""
import json, subprocess, sys
from decimal import Decimal
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_numbers as A

SHOW = Path(__file__).resolve().parents[1]; ROOT = SHOW.parent; OUT = SHOW / "results" / "number_audit"; OUT.mkdir(parents=True, exist_ok=True)
docs = sorted((ROOT / "thesis").glob("*.docx"), key=lambda p: p.stat().st_mtime) if (ROOT / "thesis").exists() else []
docs += sorted(ROOT.glob("Thesis_Draft*.docx"), key=lambda p: p.stat().st_mtime)    # 15 Nov: the author keeps drafts in the project root
docs += sorted(SHOW.glob("Thesis_Draft*.docx"), key=lambda p: p.stat().st_mtime)    # 16 Nov: v2.3 (mechanical fixes, scripts/make_draft_v23.py) lives in _showcase
docs = sorted([d for d in docs if not d.name.startswith("~$")], key=lambda p: p.stat().st_mtime)
if docs:
    doc = docs[-1]
    OUT = SHOW / "results" / f"number_audit_{doc.stem.lower().replace('thesis_draft_', '').replace('.', '_')}"  # one folder per draft: the ledger dry run is never overwritten
    OUT.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([sys.executable, "-X", "utf8", str(SHOW / "scripts" / "audit_numbers.py"), str(doc), "--registry", str(SHOW / "thesis_numbers.json"), "--out", str(OUT), "--no-fail"],
                       capture_output=True, text=True, encoding="utf-8")
    led = pd.read_csv(OUT / "audit_ledger.csv"); bad = led[led.status == "UNREGISTERED"].copy(); basis = f"`{doc.relative_to(ROOT).as_posix()}` (modified {pd.Timestamp(doc.stat().st_mtime, unit='s', tz='UTC').tz_convert('Asia/Dhaka'):%Y-%m-%d %H:%M} Dhaka)"
    words = json.loads((OUT / "words.json").read_text()) if (OUT / "words.json").exists() else {}
    ph = pd.read_csv(OUT / "placeholders.csv") if (OUT / "placeholders.csv").exists() else pd.DataFrame()
else:
    a = pd.read_csv(OUT / "audit_rows.csv"); bad = a[a.script_status == "UNREGISTERED"].rename(columns={"para": "para"}).copy()
    bad["kind"] = [A.kind_of(*A.parse_token(t)[:3]) for t in bad.token]; basis = "DRY RUN: no .docx in `thesis\\`; ledger of draft v2 pasted by the author"; words = {}; ph = pd.DataFrame()

J = json.loads((SHOW / "thesis_numbers.json").read_text(encoding="utf-8"))
cand = []                                                   # (id, number, decimals) from value, display and CI of each claim
for c in J["claims"]:
    acc = []; A.flatten([c["value"], c["display"], c["ci"]], acc)
    for v in acc: cand.append((c["id"], v))
boot = pd.read_csv(ROOT / "_evidence_pack" / "04_bootstrap.csv")
nb1000 = {round(abs(float(x)), 3) for x in pd.concat([boot.ci95_lo_nb1000, boot.ci95_hi_nb1000])}
LIT = {"193", "401", "15", "13", "1.16", "23", "24.8", "39,296", "92.42%", "24", "6,612", "57.83%", "8.9", "37", "0.674", "2,066", "0.770", "0.864"}
def nearest(tok, kind):
    val, pct, dec, d = A.parse_token(tok); v = val / 100 if pct else val
    pool = [(i, x) for i, x in cand if (kind in ("decimal", "percent") and x != x.to_integral_value() and abs(x) <= 1) or (kind.startswith("int") and x == x.to_integral_value())] or cand
    i, x = min(pool, key=lambda t: abs(abs(t[1]) - v))
    return i, x, abs(abs(x) - v), d + (2 if pct else 0)
WL = {l.split("#")[0].strip() for l in (SHOW / "configs" / "number_whitelist.txt").read_text(encoding="utf-8").splitlines() if l.split("#")[0].strip()}
def cause(tok, kind, diff, d):
    val = A.parse_token(tok)[0]
    if tok.lstrip("+-") in WL: return "setting on configs/number_whitelist.txt: no claim needed"
    if tok.lstrip("+-−–") in LIT: return "literature value: cite the paper (not a project number; see docs/RELATED_WORK_VERIFIED.md)"
    if kind == "decimal" and round(float(val), 3) in nb1000: return "interval from the 1,000-resample notebook setting; the thesis states 10,000 resamples"
    if diff <= Decimal("1.5") * Decimal(10) ** -d: return "rounding or last-digit difference: use the registry value"
    if kind.startswith("int") and val <= 512: return "setting or count not in the registry: add to configs/number_whitelist.txt if it is a setting, else add a claim"
    return "no close registry value: different definition, outdated number, or typo"
rows = []
for _, r in bad.iterrows():
    i, x, diff, d = nearest(r.token, r.kind); cz = cause(r.token, r.kind, diff, d)
    if not cz.startswith(("rounding", "no close")): i, x, diff = "-", "-", "-"                      # a nearest key is only meaningful for project numbers
    rows.append({"para": r.para, "token": r.token, "kind": r.kind, "nearest_key": i, "nearest_value": str(x), "difference": str(diff), "likely_cause": cz, "context": str(r.context)[:110]})
pd.DataFrame(rows).to_csv(OUT / "audit_todo.csv", index=False)
L = ["# AUDIT_TODO", "", f"Basis: {basis}. Generated by `scripts/audit_loop.py`; re-run after each new draft.", "",
     f"UNREGISTERED numbers: {len(rows)}. For each: the nearest registry key of the same kind and the likely cause. The thesis is never edited by this script.", ""]
if words: L += [f"Word counts (audit_numbers.py): {json.dumps(words)}", ""]
if len(ph): L += [f"Highlighted placeholders still in the draft: {len(ph)} (list: `{OUT.relative_to(SHOW).as_posix()}/placeholders.csv`)", ""]
L += ["| para | number | kind | nearest key | nearest value | likely cause | context |", "|---|---|---|---|---|---|---|"]
L += [f"| {r['para']} | `{r['token']}` | {r['kind']} | `{r['nearest_key']}` | {r['nearest_value']} | {r['likely_cause']} | {r['context'].replace('|', '/')} |" for r in rows]
L += ["", "The nearest key is a heuristic (closest value of the same kind); it can name a neighbouring claim. ", "Numbers that ARE registered can still be the wrong number in the right place (the match ignores which claim a number belongs to). "
      "The stricter claim-by-claim check for draft v2 is in `thesis_feed/DIFFERENCES.md`."]
if docs:                                                   # interval check: catches wrong bounds that equal some other registered number
    import check_intervals as CHK
    iv = CHK.check([p for p in A.assign_regions(A.load_paragraphs(str(doc))) if p["region"] != "refs"], J["claims"])
    pd.DataFrame(iv, columns=["para", "point", "lo", "hi", "status", "ids", "registry", "context"]).to_csv(OUT / "intervals.csv", index=False)
    dif = [r for r in iv if r["status"] == "DIFFERS"]
    L += ["", f"## Confidence intervals that differ from the registry ({len(dif)} of {len(iv)} intervals; `scripts/check_intervals.py`)", "",
          "The value-by-value audit above cannot see these: a wrong bound often equals some other registered number.", "",
          "| para | draft | registry claim (nearest first) | registry interval |", "|---|---|---|---|"]
    L += [f"| {r['para']} | {r['point']} [{r['lo']}, {r['hi']}] | `{r['ids']}` | {r['registry']} |" for r in dif]
    other = [r for r in iv if r["status"] in ("NO CLAIM", "POINT OUTSIDE")]
    if other:
        L += ["", f"Also check by hand ({len(other)}): NO CLAIM = no registered interval is close (stale or literature number?); "
              "POINT OUTSIDE = the point is not inside the brackets (not an interval, or a typo).", "",
              "| para | draft | status | context |", "|---|---|---|---|"]
        L += [f"| {r['para']} | {r['point']} [{r['lo']}, {r['hi']}] | {r['status']} | {r['context'].replace('|', '/')} |" for r in other]
(SHOW / "AUDIT_TODO.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print(f"audit basis: {basis} | UNREGISTERED: {len(rows)} | causes: " + json.dumps(pd.Series([r['likely_cause'].split(':')[0] for r in rows]).value_counts().to_dict()))
