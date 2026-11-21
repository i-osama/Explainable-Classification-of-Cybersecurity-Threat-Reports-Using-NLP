"""SHA-256 manifest of every input the analyses read and every output the showcase ships.
    python scripts/check_hashes.py --record   (re)write results/hashes.json
    python scripts/check_hashes.py            verify; exit 1 on any mismatch or missing file
Inputs that are absent in a clone without the data (licence unknown) are reported as ABSENT, not as failures, with --allow-absent."""
import hashlib, json, sys
from pathlib import Path
SHOW = Path(__file__).resolve().parents[1]; ROOT = SHOW.parent; MAN = SHOW / "results" / "hashes.json"

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def inputs():
    pats = ["Dataset/tram_dev.tsv", "Dataset/tram_test.tsv", "Dataset/combined_train.csv", "Dataset/ttp-desc-mappings.csv",
            "Exp_1_4_run_tram_2_epoc_30/*_pw_s4[234]/*_probs.npy", "Exp_1_4_run_tram_2_epoc_30/*_pw_s4[234]/*_labels.npy", "Exp_1_4_run_tram_2_epoc_30/*_pw_s4[234]/metrics.json",
            "Exp_1_4_run_tram_2_epoc_30/*_pw_s4[234]/mlb_classes.npy", "run_match_1/ft20_s4[234]/*_scores.npy", "run_match_1/zeroshot/test_scores.npy", "run_match_1/final_results_table.csv",
            "Exp_3_0_shap/shap_v2_roberta_pw_s42.jsonl", "Exp_3_0_shap/deletion_test_v2_roberta_pw_s42.csv", "_evidence_pack/06_deletion_test_725.csv",
            "_evidence_pack/07_agreement.csv", "_evidence_pack/01_truncated_test_ids.csv", "_evidence_pack/EVIDENCE_REPORT.md"]
    return sorted({p for pat in pats for p in ROOT.glob(pat)})

def outputs():
    fs = [p for d in ("results", "figures", "report") for p in (SHOW / d).rglob("*") if p.is_file() and p.name not in ("hashes.json", "qa_gates.json", "test_report.json") and not p.name.startswith("_")
          and not ({"smoke_logs", "smoke_runs", "llm_raw"} & set(p.parts))]   # run logs carry timings; llm_raw is a live, local-only, resumable run
    return sorted(fs + [SHOW / "thesis_numbers.json"])

def rel(p): return str(p.relative_to(ROOT)).replace("\\", "/")

if "--record" in sys.argv:
    m = {"inputs": {rel(p): sha(p) for p in inputs()}, "outputs": {rel(p): sha(p) for p in outputs()}}
    MAN.write_text(json.dumps(m, indent=1), encoding="utf-8"); print(f"recorded {len(m['inputs'])} inputs, {len(m['outputs'])} outputs -> {rel(MAN)}"); sys.exit(0)
m = json.loads(MAN.read_text(encoding="utf-8")); bad, absent = [], []
for kind in ("inputs", "outputs"):
    for f, h in m[kind].items():
        p = ROOT / f
        if not p.exists(): (absent if kind == "inputs" else bad).append(f"{f} (missing)")
        elif sha(p) != h: bad.append(f"{f} (changed)")
print(f"hash check: {len(m['inputs'])} inputs, {len(m['outputs'])} outputs | mismatches: {len(bad)} | absent inputs: {len(absent)}")
for b in bad[:15]: print("  BAD", b)
for a in absent[:5]: print("  ABSENT", a)
fail = bool(bad) or (bool(absent) and "--allow-absent" not in sys.argv)
print("HASHES: " + ("FAIL" if fail else "PASS")); sys.exit(1 if fail else 0)
