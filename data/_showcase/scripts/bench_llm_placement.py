"""Hardware placement benchmark for the local LLM baseline (CPU only vs N layers on the GTX 960). DEV prompts only, never test.
Same model, prompts and pre-registered options as prereg 17; only num_gpu varies. Output ids must match the automatic placement.
Writes results/llm_raw/bench_placement.csv. Run with the runner stopped: python scripts/bench_llm_placement.py 0 9 12 14 16"""
import subprocess, sys, time
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap import RESULTS, SEEDS, EVIDENCE, llm
from ttpmap.data import build_space, load_descriptions
import json

S = build_space(); D = load_descriptions(); LAB = S.labels; ALLOWED = set(LAB)
stix = json.load(open(EVIDENCE / "external" / "enterprise-attack-12.1.json", encoding="utf-8"))["objects"]
NAME = {r["external_id"]: o["name"] for o in stix if o["type"] == "attack-pattern" for r in o.get("external_references", []) if r.get("source_name") == "mitre-attack"}
R = np.mean([S.matcher_raw[s]["dev"] for s in SEEDS], axis=0)
P = [llm.rr_prompt(S.dev["text"].iloc[i], [(LAB[j], NAME.get(LAB[j], ""), llm.short_desc(D.description[j])) for j in np.argsort(-R[i])[:llm.N_CANDIDATES]]) for i in range(3)]
def vram():
    try: return int(subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"], capture_output=True, text=True).stdout.split()[0])
    except Exception: return -1
rows = []
for ng in [int(x) for x in sys.argv[1:]] or [0, 9, 12, 14, 16]:
    t = time.time()
    try:
        llm.generate("qwen2.5:7b", P[0], extra={"num_gpu": ng})        # warm-up = model (re)load with this placement
    except Exception as e:
        rows.append({"num_gpu": ng, "error": str(e)[:120]}); print(ng, "ERROR", e); continue
    load_s = time.time() - t; mem = vram(); pe, pd_, ge, gd, ids = 0, 0, 0, 0, []
    for p in P:
        r = llm.generate("qwen2.5:7b", p, extra={"num_gpu": ng})
        pe += r["prompt_eval_count"]; pd_ += r["prompt_eval_duration"] / 1e9; ge += r["eval_count"]; gd += r["eval_duration"] / 1e9
        ids.append(",".join(llm.parse_ids(r["response"], ALLOWED)))
    rows.append({"num_gpu": ng, "load_s": round(load_s, 1), "vram_mib": mem, "prompt_tok_s": round(pe / pd_, 1), "gen_tok_s": round(ge / gd, 1),
                 "s_per_request": round((pd_ + gd) / len(P), 2), "ids": " | ".join(ids)})
    print(rows[-1], flush=True)
df = pd.DataFrame(rows); df.to_csv(RESULTS / "llm_raw" / "bench_placement.csv", index=False); print(df.to_string(index=False))
