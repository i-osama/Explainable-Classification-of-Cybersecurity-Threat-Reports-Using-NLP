"""Run the local LLM explanation over a FIXED set of stored-SHAP rows and report how often GROUNDING RULE v1 passes.

    python grounding_report.py [N]        # default N = 100: the first N rows with stored SHAP, in row order, no picking

Report all N rows, failures included. A pass rate says the quoted words come from SHAP and nothing else.
Needs Ollama running with qwen2.5:7b (prereg 17 measured 5.8-16 s per sentence on the thesis PC).
"""
import csv
import os
import sys
import time

import core
import explain


def run(R, n=100, url="http://localhost:11434", ask=explain.ask_ollama, out="grounding_report.csv"):
    rows = sorted(R.shap)[:n]
    recs = []
    for i in rows:
        rec, units = R.shap[i], ["".join(p) for p in core.split_units(R.texts[i])]
        t0 = time.time()
        e = explain.explain(R.texts[i], rec["label"], R.name(rec["label"]), R.desc.get(rec["label"], ""), units, rec["values"], True, url, ask=ask)
        recs.append({"row": i, "source": e["source"], "grounded": e["grounded"], "reason": e["reason"], "seconds": round(time.time() - t0, 1),
                     "text": e["text"], "rejected": e.get("rejected", "")})
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(recs[0]))
        w.writeheader()
        w.writerows(recs)
    ok = sum(r["grounded"] is True for r in recs)
    unavailable = sum(str(r["reason"]).startswith("LLM unavailable") for r in recs)
    return {"n": len(recs), "passed": ok, "failed": sum(r["grounded"] is False for r in recs), "llm_unavailable": unavailable}


if __name__ == "__main__":
    R = core.load_replay(os.environ.get("TTPMAP_ROOT", r"E:\Osamas Paper"))
    print(run(R, int(sys.argv[1]) if len(sys.argv) > 1 else 100))
