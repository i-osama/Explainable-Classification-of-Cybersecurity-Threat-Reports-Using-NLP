"""Which ATT&CK release does Dataset/ttp-desc-mappings.csv come from? (no version string is stored in any data file)
Compares the technique-id set and the description texts with the Enterprise ATT&CK v12.1 STIX bundle in _evidence_pack/external/.
Texts are compared after removing citations, markdown links, <code> tags and punctuation (difflib ratio).
Writes results/attack_version.csv. Run: python scripts/check_attack_version.py"""
import difflib, json, re, sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap import RESULTS, EVIDENCE, DATA

b = json.load(open(EVIDENCE / "external" / "enterprise-attack-12.1.json", encoding="utf-8"))
ver = next(o.get("x_mitre_version") for o in b["objects"] if o["type"] == "x-mitre-collection")
st = {r["external_id"].lower(): o.get("description", "") for o in b["objects"] if o["type"] == "attack-pattern"
      for r in o.get("external_references", []) if r.get("source_name") == "mitre-attack"}
def norm(s):
    s = re.sub(r"\(Citation:[^)]*\)", " ", str(s)); s = re.sub(r"\bCitation:\s*[^.]*", " ", s); s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)
    return re.sub(r"[^a-z0-9]+", " ", re.sub(r"</?code>", "", s).lower()).strip()
d = pd.read_csv(DATA / "ttp-desc-mappings.csv", sep="\t"); d["ttp"] = d["ttp"].str.lower().str.strip()
# autojunk=False: with the default, characters in more than 1% of a 200+ character string count as junk, which
# deflates character-level ratios and makes them depend on argument order (code review, 15 Nov 2026; DECISIONS D28).
sim = pd.Series([difflib.SequenceMatcher(None, norm(st.get(t, "")), norm(x), autojunk=False).ratio() for t, x in zip(d.ttp, d.description)])
row = {"stix_version": ver, "file_ids": len(d), "stix_ids": len(st), "id_set_equal": set(d.ttp) == set(st), "ids_only_in_file": len(set(d.ttp) - set(st)),
       "ids_only_in_stix": len(set(st) - set(d.ttp)), "text_similarity_median": float(sim.median()), "text_sim_ge_0.95": int((sim >= 0.95).sum()),
       "text_sim_ge_0.99": int((sim >= 0.99).sum()), "text_sim_lt_0.80": int((sim < 0.80).sum())}
pd.DataFrame([row]).to_csv(RESULTS / "attack_version.csv", index=False); print(row)
