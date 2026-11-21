"""Q1 plan Task 5 / prereg 16: objective (b), TF-IDF + SVM part. Train on (a) TRAM, (b) siblings only, (c) TRAM + siblings; test on TRAM test once each.
Siblings = combined_train.csv rows with source_dataset procedure / derived_procedure, de-duplicated against TRAM dev + test (exact and near).
Writes results/cross_dataset_svm.csv and results/cross_dataset_family.csv. Run: python scripts/run_cross_dataset_svm.py"""
import sys
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap import RESULTS, DATA
from ttpmap.data import build_space, dedup_against, _labels
from ttpmap.fusion import components, fuse, rank_space, to_full, zrow
from ttpmap.metrics import hit_at_1, rr_at_k, recall_at_k_micro, rank_topk
from ttpmap.stats import bootstrap_ci, paired_bootstrap, mcnemar_exact, holm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC

S = build_space(); Y = S.Y["test"]; n, L = Y.shape; li = S.lab2i; un = Y & ~S.seen[None, :]
cb = pd.read_csv(DATA / "combined_train.csv").rename(columns={"text1": "text"})
sib = cb[cb.source_dataset != "tram"].drop_duplicates(subset=["text"]).copy(); sib["labels"] = sib["labels"].apply(_labels)
sib_k, removed = dedup_against(sib, pd.concat([S.dev, S.test])["text"].tolist())
TR = {"a": S.train[["text", "labels"]], "b": sib_k[["text", "labels"]], "c": pd.concat([S.train[["text", "labels"]], sib_k[["text", "labels"]]]).drop_duplicates(subset=["text"])}

rows, H, SC = [], {}, {}
for k, df in TR.items():
    lab = df["labels"].apply(lambda ys: [y for y in ys if y in li]); dropped = int((lab.str.len() == 0).sum()); df = df[lab.str.len() > 0]; lab = lab[lab.str.len() > 0]
    Yt = np.zeros((len(df), L), bool)
    for i, ys in enumerate(lab):
        Yt[i, [li[y] for y in ys]] = True
    seen = np.where(Yt.any(0))[0]
    vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True).fit(df["text"])
    svm = OneVsRestClassifier(LinearSVC(C=1.0, random_state=42)).fit(vec.transform(df["text"]), Yt[:, seen].astype(int))
    raw = svm.decision_function(vec.transform(S.test["text"])); Sc = rank_space(raw, seen, L); SC[k] = (raw, seen)
    H[k] = hit_at_1(Sc, Y); c = bootstrap_ci(H[k]); it = np.zeros(Y.shape, bool); it[np.arange(n)[:, None], rank_topk(Sc, 5)] = True
    Z = components(S, "test", "avg"); Z["svm"] = zrow(to_full(raw, seen, L))
    rows.append({"train_set": k, "P@1": c["mean"], "P@1_lo": c["lo"], "P@1_hi": c["hi"], "MRR@3": float(rr_at_k(Sc, Y).mean()), "R@5_micro": recall_at_k_micro(Sc, Y, 5),
                 "unseen_R@5": float((it & un).sum() / un.sum()), "train_rows": len(df), "train_labels": len(seen), "rows_without_space_label": dropped,
                 "test_labels_covered": int((Y.any(0) & Yt.any(0)).sum()), "removed_exact": removed["exact"] if k != "a" else 0, "removed_near": removed["near"] if k != "a" else 0,
                 "fusion_3111_with_this_svm_P@1": float(hit_at_1(fuse(Z, (3, 1, 1, 1)), Y).mean())})
assert abs(rows[0]["P@1"] - 0.7420689655172413) < 1e-9, rows[0]["P@1"]                  # (a) must reproduce B6
fam = []
for a, b in (("c", "a"), ("b", "a")):
    pb = paired_bootstrap(H[a], H[b]); mc = mcnemar_exact(H[a], H[b])
    fam.append({"A": a, "B": b, "delta_P@1": pb["delta"], "ci_lo": pb["lo"], "ci_hi": pb["hi"], "p_mcnemar": mc["p"], "mcnemar_b": mc["b"], "mcnemar_c": mc["c"]})
for f, p in zip(fam, holm([f["p_mcnemar"] for f in fam])): f["p_holm"] = p; f["family_size"] = len(fam)
pd.DataFrame(rows).to_csv(RESULTS / "cross_dataset_svm.csv", index=False); pd.DataFrame(fam).to_csv(RESULTS / "cross_dataset_family.csv", index=False)
print(pd.DataFrame(rows).round(4).to_string(index=False)); print(pd.DataFrame(fam).round(4).to_string(index=False))
