"""Bring the measured checks of the explainer app (thesis objective c, folder ..\\ttp_app) into results/ as text-free CSVs.

    python scripts/ingest_app_checks.py

1. results/app_verify.csv: re-runs ttp_app/verify_artifacts.checks() (the app's loader recomputes P@1, conformal and triage
   numbers from the saved scores and compares them with results/selective.csv, conformal.csv, explained_vs_fusion.csv).
2. results/app_live_timing.csv: from ttp_app/live_timing.json (live mode wall-clock seconds, measured on this PC).
3. results/app_grounding.csv: counts only from ttp_app/grounding_report.csv (grounding rule v1 pass / fail / unavailable);
   the explanation texts stay in ttp_app/ because they quote test sentences.
Each part is skipped with a note if its input is missing; existing result files of other scripts are never touched.
"""
import json, os, re, sys
from pathlib import Path
import pandas as pd

SHOW = Path(__file__).resolve().parents[1]; ROOT = SHOW.parent; RES = SHOW / "results"
APP = Path(os.environ.get("TTPMAP_APP", ROOT / "ttp_app"))
if not (APP / "core.py").exists():
    print(f"app folder not found: {APP} (set TTPMAP_APP); app checks not ingested, existing results/app_*.csv kept")
    sys.exit(0)
sys.path.insert(0, str(APP))
import core, verify_artifacts  # noqa: E402  (the app's own modules)

R = core.load_replay(ROOT)
rows = verify_artifacts.checks(R, RES)
v = pd.DataFrame(rows, columns=["check", "app", "thesis", "ok"])
v.to_csv(RES / "app_verify.csv", index=False)
print(f"app_verify.csv: {int(v.ok.sum())}/{len(v)} match")

import subprocess  # app test suite: counts only
r = subprocess.run([sys.executable, "-X", "utf8", "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=APP, capture_output=True, text=True, encoding="utf-8", errors="ignore")
last = (r.stdout.strip().splitlines() or [""])[-1]
cnt = {k: int(n) for n, k in re.findall(r"(\d+) (passed|failed|error|errors|skipped)", last)}
pd.DataFrame([{"passed": cnt.get("passed", 0), "failed": cnt.get("failed", 0) + cnt.get("error", 0) + cnt.get("errors", 0), "skipped": cnt.get("skipped", 0),
               "runner": "pytest -q in ttp_app", "summary": last}]).to_csv(RES / "app_tests.csv", index=False)
print(f"app_tests.csv: {last}")

lt = APP / "live_timing.json"
if lt.exists():
    d = json.loads(lt.read_text(encoding="utf-8"))
    t = pd.DataFrame([{k: r.get(k) for k in ("sentence", "words", "n_perm", "wall_s", "shap_s", "additivity_error", "set_size", "tier", "error")}
                      | {f"ms_{k}": x for k, x in r.get("ms_batch1", {}).items()} for r in d["rows"]])
    t["measured"], t["how"] = d["measured"], d["how"]
    t.to_csv(RES / "app_live_timing.csv", index=False)
    print(f"app_live_timing.csv: {len(t)} rows")
else:
    print("live_timing.json missing: live timing not ingested")

gr = APP / "grounding_report.csv"
if gr.exists():
    g = pd.read_csv(gr)
    cause = lambda r: ("passed" if str(r).strip() == "ok" else "LLM unavailable" if str(r).startswith("LLM unavailable")
                       else re.sub(r":.*$", "", str(r).replace("LLM text rejected: ", "")))
    s = {"n": len(g), "passed": int((g.grounded.astype(str) == "True").sum()), "failed": int((g.grounded.astype(str) == "False").sum()),
         "llm_unavailable": int(g.reason.astype(str).str.startswith("LLM unavailable").sum()),
         "seconds_median": float(g.seconds.median()), "seconds_mean": float(g.seconds.mean()), "rows": f"first {len(g)} rows with stored SHAP, row order",
         "rule": "grounding rule v1 (ttp_app/explain.py)", "model": "qwen2.5:7b, temperature 0, seed 0"}
    answered = s["n"] - s["llm_unavailable"]
    s["pass_rate"] = s["passed"] / answered if answered else float("nan")  # no LLM answer at all: no rate, not 0%
    out = pd.DataFrame([s])
    for c, n in g.reason.map(cause).value_counts().items():
        out[f"cause: {c}"] = int(n)
    out.to_csv(RES / "app_grounding.csv", index=False)
    print(f"app_grounding.csv: {s['passed']}/{s['n']} passed, {s['failed']} failed, {s['llm_unavailable']} unavailable")
    # POST-HOC description of the v1 failures (rule unchanged): which kinds of quoted words broke it. Input for a v2 proposal only.
    import explain
    kinds_all = []
    for _, r in g[g.grounded.astype(str) == "False"].iterrows():
        i = int(r.row); lab = R.shap[i]["label"]
        units = ["".join(p) for p in core.split_units(R.texts[i])]
        allowed = {explain.norm(w) for w, _ in explain.top_words(units, R.shap[i]["values"])}
        sent, name = {explain.norm(u) for u in units}, {explain.norm(w) for w in R.name(lab).split()}
        quotes, kinds = explain._QUOTE.findall(str(r.rejected)), set()
        for w in (w for q in quotes for w in q.split()):
            n = explain.norm(w)
            if n and n not in allowed:
                kinds.add("technique id/name" if n in name else "sentence word outside top-5" if n in sent else "word not in sentence")
        if not quotes: kinds.add("no quotes")
        if any(t != lab for t in explain._TID.findall(str(r.rejected))): kinds.add("other technique id")
        kinds_all.append(" + ".join(sorted(kinds)))
    pc = pd.Series(kinds_all).value_counts().rename_axis("violations").reset_index(name="rows")
    pc.to_csv(RES / "app_grounding_causes_posthoc.csv", index=False)
    print(f"app_grounding_causes_posthoc.csv: only the explained technique's own id/name: {int(pc.loc[pc.violations == 'technique id/name', 'rows'].sum())} rows")
else:
    print("grounding_report.csv missing: grounding not ingested")
