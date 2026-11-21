"""Number audit of the thesis draft WITHOUT the .docx (the file is not on this PC).
Input: results/number_audit/ledger_from_author_paste.csv = the distinct strict tokens (decimal, percent, integer >= 10,
not on the allow-list) of the ledger that the author pasted on 2026-11-14, one row per distinct meaning, transcribed by hand.
Matching uses the functions of scripts/audit_numbers.py (the author's script), so the result equals what
`audit_numbers.py Thesis.docx --registry thesis_numbers.json` would report for these tokens.
Extra, stricter step: for each token find the claim ids whose value / display / CI support it.
Outputs: results/number_audit/audit_rows.csv, audit_report.md.  Run audit_numbers.py on the real .docx when it is available."""
import csv, json, sys
from decimal import Decimal
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_numbers as A

SHOW = Path(__file__).resolve().parents[1]; OUT = SHOW / "results" / "number_audit"
J = json.loads((SHOW / "thesis_numbers.json").read_text(encoding="utf-8"))
registry = []; A.flatten(J, registry); registry = sorted(set(registry))
per_claim = {}
for c in J["claims"]:
    acc = []; A.flatten([c["value"], c["display"], c["ci"]], acc); per_claim[c["id"]] = acc
# Reviewer notes for tokens that no project result can support. Category is a judgement from the quoted context.
NOTE = {
 ("10", 7): ("FRONT MATTER", "a date, not a result"),
 ("193", 197): ("LITERATURE", "ATT&CK v12 matrix size (14 tactics / 193 techniques / 401 sub-techniques): from the cited ATT&CK source, not from a project file. Not to be confused with the 193 distinct labels of the dataset"),
 ("401", 197): ("LITERATURE", "as above; the baseline paper's background section says 196 techniques and 411 sub-techniques for v12.0 (_evidence_pack/08_baseline.md): check the source cited for 193 / 401"),
 ("15", 199): ("LITERATURE", "current ATT&CK website; cited source"), ("13", 231): ("LITERATURE", "ATT&CK version number in a citation"),
 ("1.16", 272): ("LITERATURE", "baseline paper Table 1 (TRAM: 1.16 labels, 23 tokens); confirmed from arXiv:2401.10337, see _evidence_pack/08_baseline.md"),
 ("23", 272): ("LITERATURE", "baseline paper Table 1; see _evidence_pack/08_baseline.md"),
 ("24.8", 311): ("LITERATURE", "related-work table; no project file; reference must be verified (docs/RELATED_WORK_VERIFIED.md)"),
 ("39,296", 313): ("LITERATURE", "related-work table; reference must be verified"), ("92.42%", 314): ("LITERATURE", "related-work table; reference must be verified"),
 ("24", 319): ("LITERATURE", "baseline paper, Limitations: 'on average, it requires 24 hours for training' on one V100; see _evidence_pack/08_baseline.md"),
 ("6,612", 322): ("LITERATURE", "related-work table; reference must be verified"), ("57.83%", 323): ("LITERATURE", "related-work table; reference must be verified"),
 ("8.9", 323): ("LITERATURE", "related-work table; reference must be verified"), ("37", 331): ("LITERATURE", "related-work table; reference must be verified"),
 ("0.674", 334): ("LITERATURE", "baseline paper Table 2, XR-LINEAR on TRAM: P@1 .674; confirmed from arXiv:2401.10337 (_evidence_pack/08_baseline.md)"),
 ("256", 395): ("SETTING", "matcher ablation ft20L256: label_max_len_train=256 (Exp_2.1 CELL 16)"),
 ("15", 427): ("SETTING", "epochs of the earlier configuration (folder runs_tram_1.1_epoch_15)"),
 ("2.5", 502): ("SETTING", "percentile of the 95% interval"), ("97.5", 502): ("SETTING", "percentile of the 95% interval"),
 ("0.03", 790): ("DERIVED", "rounded gain: C1 +0.029 and C2 +0.026"), ("0.002", 817): ("DERIVED", "0.779 - 0.777 (B11 - B10c)"), ("0.005", 817): ("DERIVED", "0.779 - 0.774 (B11 - B9)"),
 ("0.04", 859): ("DERIVED", "macro-F1 117 vs 127 labels: 0.563 - 0.519 = 0.044 and 0.543 - 0.500 = 0.043 (B4, B5)"),
 ("10,000", 502): ("SETTING", "bootstrap resamples: configs/analysis.yaml; seed = numpy default_rng(20261114)"),
 ("100", 528): ("SETTING", "sample size of the rating sheet: first 100 of RandomState(42).permutation(725) (Exp_3_2_hand_check CELL 0)"),
 ("49", 741): ("SETTING", "bucket boundary"), ("50", 741): ("SETTING", "bucket boundary"), ("19", 755): ("SETTING", "bucket boundary"),
}
# Known draft-vs-file differences that a pure number match cannot see (the token exists somewhere in the registry, but not for this claim).
OVERRIDE = {
 ("-0.015", 192): "NOT SUPPORTED: number differs. The draft says 10,000 resamples; at 10,000 the C3 interval is {C3ci}. -0.015 / +0.040 is the 1,000-resample notebook-setting interval (_evidence_pack/04_bootstrap.csv)",
 ("+0.040", 192): "NOT SUPPORTED: number differs. See the row above: C3 at 10,000 resamples is {C3ci}",
 ("-0.022", 676): "NOT SUPPORTED: number differs. C4 at 10,000 resamples is {C4ci}; -0.022 is the 1,000-resample value",
 ("0.037", 676): "NOT SUPPORTED: number differs. C2 MRR@3 interval is {C2mci}",
 ("+0.020", 676): "NOT SUPPORTED: number differs. C3 MRR@3 is {C3m} {C3mci}",
 ("+0.003", 676): "NOT SUPPORTED: number differs. C4 MRR@3 is {C4m} {C4mci}",
 ("-0.015", 676): "NOT SUPPORTED: number differs. C4 MRR@3 interval is {C4mci}",
 ("+0.020", 692): "NOT SUPPORTED: number differs. C4 MRR@3 interval is {C4mci}",
 ("0.001", 192): "SUPPORTED by C2 (lower bound at 10,000 resamples); upper bound 0.051 confirmed: C2 = {C2ci}",
}
N = {c["id"]: c for c in J["claims"]}
def cif(k): return f"[{N[k]['ci'][0]:+.3f}, {N[k]['ci'][1]:+.3f}]"
fmt = {"C3ci": cif("C3"), "C4ci": cif("C4"), "C2ci": cif("C2"), "C2mci": cif("C2.mrr"), "C3mci": cif("C3.mrr"), "C4mci": cif("C4.mrr"), "C3m": N["C3.mrr"]["display"], "C4m": N["C4.mrr"]["display"]}
rows = []
for r in csv.DictReader(open(OUT / "ledger_from_author_paste.csv", encoding="utf-8")):
    tok = r["token"]; para = int(r["para"]); val, pct, dec, d = A.parse_token(tok)
    reg = A.matches(val, pct, dec, d, registry)
    keys = [k for k, acc in per_claim.items() if acc and A.matches(val, pct, dec, d, acc)]
    key = (tok, para)
    if key in OVERRIDE: verdict = OVERRIDE[key].format(**fmt); status = "NOT SUPPORTED" if verdict.startswith("NOT") else "SUPPORTED"
    elif keys: verdict = "SUPPORTED by " + ", ".join(keys[:6]) + (" ..." if len(keys) > 6 else ""); status = "SUPPORTED"
    elif key in NOTE: verdict = f"{NOTE[key][0]}: {NOTE[key][1]}"; status = NOTE[key][0]
    elif reg: verdict = "REGISTERED only loosely (the number occurs in a definition or note, not as a claim value): check by hand"; status = "LOOSE"
    else: verdict = "NOT SUPPORTED: missing from thesis_numbers.json"; status = "NOT SUPPORTED"
    rows.append({"token": tok, "para": para, "context": r["context"], "script_status": "registered" if reg else "UNREGISTERED", "status": status, "supporting_key_or_reason": verdict})
with open(OUT / "audit_rows.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
cnt = {}
for r in rows: cnt[r["status"]] = cnt.get(r["status"], 0) + 1
unreg = [r for r in rows if r["script_status"] == "UNREGISTERED"]
L = ["# Number audit of the draft (from the pasted ledger; the .docx is not on this PC)", "",
     f"- registry numbers loaded: {len(registry)}", f"- distinct strict tokens checked: {len(rows)}",
     f"- audit_numbers.py status: registered {len(rows) - len(unreg)}, UNREGISTERED {len(unreg)}",
     "- stricter check (value / display / CI of a claim): " + ", ".join(f"{k} {v}" for k, v in sorted(cnt.items())), "",
     "## UNREGISTERED (as audit_numbers.py would report)", ""]
L += [f"- [p{r['para']}] `{r['token']}` ...{r['context']}... -> {r['supporting_key_or_reason']}" for r in unreg]
L += ["", "## NOT SUPPORTED or LOOSE under the stricter check", ""]
L += [f"- [p{r['para']}] `{r['token']}` ...{r['context']}... -> {r['supporting_key_or_reason']}" for r in rows if r["status"] in ("NOT SUPPORTED", "LOOSE")]
L += ["", "## Not caught by a number scan (integers below 10 are ignored by the script)", "",
      f"- [p604, table] \"2 test and 1 development sentence found\": exact duplicates are {N['A6.exact_test']['display']} test and {N['A6.exact_dev']['display']} dev; "
      f"near-duplicates add {N['A6.near_test']['display']} test and {N['A6.near_dev']['display']} dev rows (A6). '2 test' is right only as exact + near; '1 development' is supported by neither count."]
(OUT / "audit_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L[:7])); print(f"UNREGISTERED: {len(unreg)}; NOT SUPPORTED/LOOSE: {sum(r['status'] in ('NOT SUPPORTED', 'LOOSE') for r in rows)}")
