"""Q1 plan Task 7 / prereg 17: open-weights LLM baseline on local Ollama (qwen2.5:7b). Resumable.
  python scripts/run_llm_baseline.py --split dev --n 50        dev pilot (parse rate only)
  python scripts/run_llm_baseline.py --split test              all variants, all 725 test sentences (hours; safe to restart)
  python scripts/run_llm_baseline.py --score                   results/llm_baseline.csv + results/llm_family.csv from the jsonl files
Raw replies are kept (first 300 characters) in results/llm_raw/<variant>_<split>.jsonl; they are not shipped in the upload package."""
import argparse, json, sys, time
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap import RESULTS, SEEDS, EVIDENCE, llm, zeroshot
from ttpmap.data import build_space, load_descriptions
from ttpmap.fusion import components, fuse, rank_space
from ttpmap.metrics import hit_at_1, rr_at_k, recall_at_k_micro
from ttpmap.stats import bootstrap_ci, paired_bootstrap, mcnemar_exact, holm

MODEL, DIGEST = "qwen2.5:7b", "845dbda0ea48"
VARIANTS = ("closed", "rr_matcher", "rr_zero")
RAW = RESULTS / "llm_raw"; RAW.mkdir(parents=True, exist_ok=True)
ap = argparse.ArgumentParser(); ap.add_argument("--split", default="test"); ap.add_argument("--n", type=int, default=0)
ap.add_argument("--variants", default=",".join(VARIANTS)); ap.add_argument("--score", action="store_true"); a = ap.parse_args()

S = build_space(); D = load_descriptions(); LAB = S.labels; ALLOWED = set(LAB)
stix = json.load(open(EVIDENCE / "external" / "enterprise-attack-12.1.json", encoding="utf-8"))["objects"]
NAME = {r["external_id"]: o["name"] for o in stix if o["type"] == "attack-pattern" for r in o.get("external_references", []) if r.get("source_name") == "mitre-attack"}
NAME = {l: NAME.get(l, llm.short_desc(D.description[i], 6)) for i, l in enumerate(LAB)}
CATALOG = [(LAB[j], NAME[LAB[j]]) for j in S.seen_idx]


def retriever(variant, split):
    if variant == "rr_matcher":
        return np.mean([S.matcher_raw[s][split] for s in SEEDS], axis=0)
    if split == "test":
        return S.matcher_zero_test
    f = RAW / "zeroshot_dev_scores.npy"
    if not f.exists():
        np.save(f, zeroshot.scores(S.dev["text"].tolist(), D["description"].tolist()))
    return np.load(f)


def prompt(variant, text, R_row):
    if variant == "closed":
        return llm.closed_prompt(text, CATALOG), None
    top = np.argsort(-R_row)[:llm.N_CANDIDATES]
    return llm.rr_prompt(text, [(LAB[j], NAME[LAB[j]], llm.short_desc(D.description[j])) for j in top]), top


def read_rows(f):
    """jsonl rows by sentence index; a half-written last line (process killed mid-write) is skipped and redone."""
    out = {}
    for l in f.read_text(encoding="utf-8").splitlines():
        try: r = json.loads(l); out[r["i"]] = r
        except (ValueError, KeyError): continue
    return out


def run(split, n):
    df = getattr(S, split); idx = range(len(df) if not n else min(n, len(df)))
    for v in a.variants.split(","):
        R = None if v == "closed" else retriever(v, split)
        f = RAW / f"{v}_{split}.jsonl"; done = set()
        if f.exists():
            done = set(read_rows(f))
        t0 = time.time(); k = 0
        with open(f, "a", encoding="utf-8") as fh:
            for i in idx:
                if i in done: continue
                p, _ = prompt(v, df["text"].iloc[i], None if R is None else R[i])
                t = time.time(); r = llm.generate(MODEL, p)
                ids = llm.parse_ids(r.get("response", ""), ALLOWED)
                fh.write(json.dumps({"variant": v, "split": split, "i": i, "ids": ids, "raw": r.get("response", "")[:300], "prompt_tokens": r.get("prompt_eval_count"),
                                     "seconds": round(time.time() - t, 2), "model": MODEL, "digest": DIGEST, "num_gpu": llm.placement().get("num_gpu", "auto")}) + "\n"); fh.flush(); k += 1
                if k % 25 == 0: print(f"{v} {split}: {len(done) + k} done, {(time.time() - t0) / k:.1f} s/sentence", flush=True)
        print(f"{v} {split}: finished ({len(done) + k} rows)", flush=True)


def scores_of(v, split):
    rows = read_rows(RAW / f"{v}_{split}.jsonl")
    n = len(getattr(S, split)); assert set(rows) == set(range(n)), f"{v}: {len(rows)} of {n} sentences scored"
    base = rank_space(S.svm_raw[split], S.seen_idx, S.L) if v == "closed" else retriever(v, split)
    Sc = np.argsort(np.argsort(base, axis=1), axis=1).astype(float)          # retriever / SVM order as the tail, 0 .. L-1
    li = S.lab2i
    for i, r in rows.items():
        for rank, t in enumerate(r["ids"]): Sc[i, li[t]] = 10_000 - rank   # LLM answers first, in its order
    parse = np.mean([len(r["ids"]) > 0 for r in rows.values()]); secs = np.mean([r["seconds"] for r in rows.values()])
    return Sc, parse, secs


if not a.score:
    run(a.split, a.n)
    if a.split == "dev":                                                     # pilot report: parse rate only (dev number, never used to change prompts)
        for v in a.variants.split(","):
            rr = list(read_rows(RAW / f"{v}_dev.jsonl").values())
            print(f"PILOT {v}: n={len(rr)} parse rate {np.mean([len(r['ids']) > 0 for r in rr]):.2f}, {np.mean([r['seconds'] for r in rr]):.1f} s/sentence")
    sys.exit(0)

Y = S.Y["test"]; Z = components(S, "test", "avg")
REF = {"Matcher (3-seed ens.)": Z["matcher"], "Fusion (3,1,1,1)": fuse(Z, (3, 1, 1, 1))}
rows, fam = [], []
for v in VARIANTS:
    Sc, parse, secs = scores_of(v, "test"); h = hit_at_1(Sc, Y); c = bootstrap_ci(h); m = bootstrap_ci(rr_at_k(Sc, Y))
    rows.append({"variant": v, "P@1": c["mean"], "P@1_lo": c["lo"], "P@1_hi": c["hi"], "MRR@3": m["mean"], "MRR@3_lo": m["lo"], "MRR@3_hi": m["hi"],
                 "R@5_micro": recall_at_k_micro(Sc, Y, 5), "parse_rate": parse, "seconds_per_sentence": secs, "model": MODEL, "digest": DIGEST, "n": len(Y)})
    for ref, R_ in REF.items():
        hb = hit_at_1(R_, Y); pb = paired_bootstrap(h, hb); mc = mcnemar_exact(h, hb)
        fam.append({"A": f"LLM {v}", "B": ref, "delta_P@1": pb["delta"], "ci_lo": pb["lo"], "ci_hi": pb["hi"], "p_mcnemar": mc["p"], "mcnemar_b": mc["b"], "mcnemar_c": mc["c"]})
ph = holm([r["p_mcnemar"] for r in fam])
for r, p in zip(fam, ph): r["p_holm"] = p; r["family_size"] = len(fam)
pd.DataFrame(rows).to_csv(RESULTS / "llm_baseline.csv", index=False); pd.DataFrame(fam).to_csv(RESULTS / "llm_family.csv", index=False)
print(pd.DataFrame(rows)[["variant", "P@1", "MRR@3", "R@5_micro", "parse_rate", "seconds_per_sentence"]].round(3).to_string(index=False))
print(pd.DataFrame(fam)[["A", "B", "delta_P@1", "ci_lo", "ci_hi", "p_holm"]].round(3).to_string(index=False))
