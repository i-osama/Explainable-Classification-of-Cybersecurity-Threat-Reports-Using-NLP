"""Q1 wave 2 Task 5 / prereg 20 (EXPLORATORY, descriptive): label-noise candidates on TEST.
Candidate = fusion top-1 not in the gold labels AND matcher, SVM, RoBERTa and SecBERT top-1 all equal the fusion top-1.
Writes results/label_noise_candidates.csv (no sentence text), results/label_noise_summary.csv and, for the author only,
human_study/materials_local/label_noise_review.xlsx (with sentence text; not in the upload zip). Run: python scripts/run_label_noise.py"""
import sys
from collections import Counter
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ttpmap import RESULTS
from ttpmap.data import build_space, load_split, load_tactics
from ttpmap.fusion import components, fuse
from ttpmap.metrics import rank_topk
from ttpmap.selective import margin

S = build_space(); Y = S.Y["test"]; LAB = np.array(S.labels)
Z = components(S, "test", "avg"); SYS = {"fusion": fuse(Z, (3, 1, 1, 1)), **{k: Z[k] for k in ("matcher", "svm", "roberta", "secbert")}}
TOP = {k: rank_topk(v, 1)[:, 0] for k, v in SYS.items()}
tech = load_tactics().set_index("id"); ttac = tech["tactics"].to_dict(); tname = tech["name"].to_dict()


def rel(g, p):  # same relation rules as scripts/run_analyses.py (results/parent_sub.csv), plus a same-tactic level
    if "." in g and p == g.split(".")[0]: return "predicted the parent"
    if "." in p and g == p.split(".")[0]: return "predicted a sub-technique"
    if g.split(".")[0] == p.split(".")[0]: return "sibling sub-technique"
    if set(ttac.get(g, [])) & set(ttac.get(p, [])): return "same tactic"
    return "other tactic"


ORDER = ("predicted the parent", "predicted a sub-technique", "sibling sub-technique", "same tactic", "other tactic")
wrong = ~Y[np.arange(len(Y)), TOP["fusion"]]
unanimous = np.all([TOP[k] == TOP["fusion"] for k in ("matcher", "svm", "roberta", "secbert")], axis=0)
cand = np.where(wrong & unanimous)[0]; fm = margin(SYS["fusion"])
rows = []
for i in cand:
    p = LAB[TOP["fusion"][i]]; gold = list(LAB[Y[i]]); rels = [rel(g, p) for g in gold]
    rows.append({"test_index": int(i), "gold": ";".join(gold), "consensus": p, "consensus_name": tname.get(p, "?"),
                 "relation": next(x for x in ORDER if x in rels), "fusion_margin": float(fm[i]), "consensus_train_support": int(S.train_count[TOP["fusion"][i]])})
C = pd.DataFrame(rows, columns=["test_index", "gold", "consensus", "consensus_name", "relation", "fusion_margin", "consensus_train_support"])
rc = Counter(C["relation"]) if len(C) else Counter()
summ = [{"metric": "test_sentences", "value": len(Y)}, {"metric": "fusion_top1_errors", "value": int(wrong.sum())},
        {"metric": "unanimous_wrong_candidates", "value": len(C)}, {"metric": "share_of_fusion_errors", "value": len(C) / max(1, int(wrong.sum()))},
        {"metric": "share_of_test", "value": len(C) / len(Y)}, {"metric": "all_five_agree_any_label", "value": int(unanimous.sum())}]
summ += [{"metric": f"relation: {x}", "value": int(rc.get(x, 0))} for x in ORDER]
C.to_csv(RESULTS / "label_noise_candidates.csv", index=False); pd.DataFrame(summ).to_csv(RESULTS / "label_noise_summary.csv", index=False)

te = load_split("test").reset_index(drop=True)
sheet = C.assign(sentence=[te.loc[i, "text"] for i in C["test_index"]],
                 gold_names=[";".join(tname.get(g, "?") for g in s.split(";")) for s in C["gold"]],
                 verdict_gold_correct="", verdict_consensus_correct="", both_acceptable="", note="")
out = ROOT / "human_study" / "materials_local"; out.mkdir(parents=True, exist_ok=True)
xl = out / "label_noise_review.xlsx"
if xl.exists():  # never overwrite a sheet the author may have filled in (CLAUDE.md working rule)
    from datetime import datetime
    xl = out / f"label_noise_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    print(f"existing review sheet kept; new sheet written to {xl.name}")
sheet.to_excel(xl, index=False)
print(pd.DataFrame(summ).to_csv(index=False)); print(C.drop(columns=["consensus_name"]).head(12).round(3).to_csv(index=False))
