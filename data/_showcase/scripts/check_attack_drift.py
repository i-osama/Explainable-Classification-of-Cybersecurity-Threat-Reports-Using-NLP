"""Q1 wave 2 Task 6 / prereg 21 (descriptive): ATT&CK version drift of the label space.
Compares the 737 ids of Dataset/ttp-desc-mappings.csv (= ATT&CK v12.1, results/attack_version.csv) with the current
Enterprise ATT&CK bundle from mitre-attack/attack-stix-data (downloaded once to E:/Osamas Paper/_downloads/attack_latest/).
Writes results/attack_drift.csv (summary) and results/attack_drift_ids.csv (per id). Run: python scripts/check_attack_drift.py [bundle.json]"""
import difflib, hashlib, json, re, sys
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ttpmap import RESULTS, DATA, EVIDENCE
from ttpmap.data import build_space
from ttpmap.drift import status_table, _ext

URL = "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/enterprise-attack/enterprise-attack.json"
P = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / "_downloads" / "attack_latest" / "enterprise-attack.json"
raw = P.read_bytes(); B = json.loads(raw); sha = hashlib.sha256(raw).hexdigest()
coll = next(o for o in B["objects"] if o["type"] == "x-mitre-collection")
new = status_table(B["objects"]).set_index("id")
old = status_table(json.load(open(EVIDENCE / "external" / "enterprise-attack-12.1.json", encoding="utf-8"))["objects"]).set_index("id")


def norm(s):  # same normalisation as scripts/check_attack_version.py
    s = re.sub(r"\(Citation:[^)]*\)", " ", str(s)); s = re.sub(r"\bCitation:\s*[^.]*", " ", s); s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)
    return re.sub(r"[^a-z0-9]+", " ", re.sub(r"</?code>", "", s).lower()).strip()


desc_new = {}  # active objects only, so a deprecated duplicate never replaces the active description
for o in B["objects"]:
    if o.get("type") == "attack-pattern" and not o.get("revoked") and not o.get("x_mitre_deprecated"):
        e = _ext(o)
        if e: desc_new[e] = o.get("description", "")
d = pd.read_csv(DATA / "ttp-desc-mappings.csv", sep="\t"); d["id"] = d["ttp"].str.upper().str.strip()
ids = []
for t, txt in zip(d["id"], d["description"]):
    st = new["status"].get(t, "missing"); fin = new["final_id"].get(t) if t in new.index else None
    # same argument order and autojunk=False as scripts/check_attack_version.py (D28)
    sim = difflib.SequenceMatcher(None, norm(desc_new[t]), norm(txt), autojunk=False).ratio() if st == "active" and t in desc_new else np.nan
    ids.append({"id": t, "status_v12.1": old["status"].get(t, "missing"), "status_latest": st, "final_id_latest": fin,
                "final_status_latest": new["final_status"].get(t) if t in new.index else None, "desc_similarity": sim})
I = pd.DataFrame(ids).set_index("id")

S = build_space(); LAB = np.array(S.labels); stat = np.array([I["status_latest"].get(l, "missing") for l in LAB])
nonact = stat != "active"; was_nonact = np.array([I["status_v12.1"].get(l, "missing") != "active" for l in LAB]); after = nonact & ~was_nonact
rows = {"bundle_url": URL, "bundle_sha256": sha, "latest_version": coll.get("x_mitre_version"), "latest_modified": coll.get("modified"), "label_ids": len(I)}
for s in ("active", "deprecated", "revoked", "missing"):
    rows[f"ids_{s}"] = int((I["status_latest"] == s).sum())
rows["ids_nonactive_already_in_v12.1"] = int(((I["status_latest"] != "active") & (I["status_v12.1"] != "active")).sum())
rows["ids_became_nonactive_after_v12.1"] = int(((I["status_latest"] != "active") & (I["status_v12.1"] == "active")).sum())
for sp in ("train", "test"):
    Y = S.Y[sp]; rows[f"{sp}_label_occurrences"] = int(Y.sum()); rows[f"{sp}_occurrences_nonactive"] = int(Y[:, nonact].sum())
    rows[f"{sp}_sentences_any_nonactive"] = int(Y[:, nonact].any(1).sum()); rows[f"{sp}_sentences"] = int(len(Y))
    rows[f"{sp}_sentences_nonactive_already_v12.1"] = int(Y[:, nonact & was_nonact].any(1).sum())
    rows[f"{sp}_sentences_nonactive_after_v12.1"] = int(Y[:, after].any(1).sum())
rows["test_share_sentences_any_nonactive"] = rows["test_sentences_any_nonactive"] / rows["test_sentences"]
rows["latest_active_ids"] = int((new["status"] == "active").sum())
rows["latest_active_ids_absent_from_label_space"] = int(len(set(new.index[new["status"] == "active"]) - set(I.index)))
rows["desc_similarity_median_active"] = float(I["desc_similarity"].median()); rows["desc_similarity_lt_0.80"] = int((I["desc_similarity"] < 0.80).sum())
rows["revoked_without_replacement"] = int(((I["status_latest"] == "revoked") & I["final_id_latest"].isna()).sum())
rows["revoked_to_nonactive_target"] = int(((I["status_latest"] == "revoked") & I["final_id_latest"].notna() & (I["final_status_latest"] != "active")).sum())
pd.DataFrame([rows]).to_csv(RESULTS / "attack_drift.csv", index=False); I.reset_index().to_csv(RESULTS / "attack_drift_ids.csv", index=False)
for k, v in rows.items():
    print(f"{k}: {v}")
