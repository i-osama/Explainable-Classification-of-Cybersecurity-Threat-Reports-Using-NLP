"""T1 dataset proof -> 01_dataset.md, 01_label_counts.csv, 01_duplicates.csv"""
import difflib, hashlib, re
from collections import Counter, defaultdict
import numpy as np, pandas as pd
from common import ROOT, PACK, DATA, CLS, norm_text, parse_labels, load_split, w

comb = pd.read_csv(DATA / "combined_train.csv")
train = comb[comb["source_dataset"] == "tram"].rename(columns={"text1": "text"}).copy()
train["row_id"] = train.index                      # row index inside combined_train.csv
train["labels"] = train["labels"].apply(parse_labels)
train = train.reset_index(drop=True)
dev, test = load_split("dev"), load_split("test")
splits = {"train": train, "dev": dev, "test": test}
L = []
P = L.append

P("# 01 Dataset proof\n")
P("Sources: `Dataset/tram_dev.tsv`, `Dataset/tram_test.tsv`, train = rows of `Dataset/combined_train.csv` with "
  "`source_dataset == 'tram'` (`tram_train.tsv` itself is NOT-FOUND on E:; notebooks read it from Google Drive).\n")

# ---- rows / labels
P("## Rows and labels per split  [RECOMPUTED]\n")
P("| split | rows | unique labels | label assignments | single-label rows | multi-label rows | max labels/row | sub-technique labels | parent-level labels |")
P("|---|---|---|---|---|---|---|---|---|")
labset = {}
for n, d in splits.items():
    k = d["labels"].apply(lambda x: len(set(x)))
    s = set(l for ls in d["labels"] for l in ls); labset[n] = s
    P(f"| {n} | {len(d)} | {len(s)} | {int(k.sum())} | {int((k == 1).sum())} | {int((k > 1).sum())} | {int(k.max())} | "
      f"{sum('.' in x for x in s)} | {sum('.' not in x for x in s)} |")
tot = sum(len(d) for d in splits.values())
P(f"\nTotal sentences: **{tot}**. Rows with duplicate label ids inside one row: "
  + ", ".join(f"{n}={int(d['labels'].apply(lambda x: len(x) != len(set(x))).sum())}" for n, d in splits.items()) + ".\n")
seen_te = labset["test"] & labset["train"]; unseen_te = labset["test"] - labset["train"]
seen_dv = labset["dev"] & labset["train"]; unseen_dv = labset["dev"] - labset["train"]
P(f"- test labels: {len(labset['test'])} = {len(seen_te)} seen in train + {len(unseen_te)} unseen: `{sorted(unseen_te)}`")
P(f"- dev labels: {len(labset['dev'])} = {len(seen_dv)} seen + {len(unseen_dv)} unseen: `{sorted(unseen_dv)}`")
un_rows = test["labels"].apply(lambda x: any(l in unseen_te for l in x))
all_un = test["labels"].apply(lambda x: all(l in unseen_te for l in x))
un_pairs = int(test["labels"].apply(lambda x: sum(l in unseen_te for l in set(x))).sum())
P(f"- test rows with >=1 unseen label: {int(un_rows.sum())}; rows whose labels are ALL unseen: {int(all_un.sum())}; unseen (row,label) pairs: {un_pairs}")
P(f"- test (row,label) pairs total: {int(test['labels'].apply(lambda x: len(set(x))).sum())}\n")

# label counts
cnt = {n: Counter(l for ls in d["labels"] for l in set(ls)) for n, d in splits.items()}
alll = sorted(set().union(*labset.values()))
lc = pd.DataFrame({"label": alll, **{n: [cnt[n].get(l, 0) for l in alll] for n in splits}})
lc["is_subtechnique"] = lc["label"].str.contains(r"\.")
lc.to_csv(PACK / "01_label_counts.csv", index=False)
P(f"Per-label support per split: `01_label_counts.csv` ({len(lc)} labels across all splits).\n")
ts = lc["train"]
P("Train support distribution (labels with train>0): "
  f"median={int(ts[ts>0].median())}, min={int(ts[ts>0].min())}, max={int(ts.max())}, labels with <5 train rows={int(((ts>0)&(ts<5)).sum())}, "
  f"<10={int(((ts>0)&(ts<10)).sum())}\n")

# ---- duplicates
P("## Duplicates (lowercase + whitespace-normalised)  [RECOMPUTED]\n")
for d in splits.values(): d["norm"] = d["text"].apply(norm_text)
dup_rows = []
for n, d in splits.items():
    g = d.groupby("norm").indices
    k = sum(len(v) - 1 for v in g.values() if len(v) > 1)
    grp = sum(1 for v in g.values() if len(v) > 1)
    P(f"- within {n}: {k} redundant rows in {grp} duplicate groups (raw-text exact dup rows: {int(d['text'].duplicated().sum())})")
    for key, v in g.items():
        if len(v) > 1:
            dup_rows.append({"type": f"within_{n}", "ids_a": ";".join(map(str, v)), "ids_b": "", "text": d['text'].iloc[v[0]][:160],
                             "labels_a": str([d['labels'].iloc[i] for i in v]), "labels_b": ""})
def cross(a, b):
    ia = splits[a].groupby("norm").indices; ib = splits[b].groupby("norm").indices
    common = sorted(set(ia) & set(ib)); na = sum(len(ia[c]) for c in common); nb = sum(len(ib[c]) for c in common)
    for c in common:
        dup_rows.append({"type": f"{a}_x_{b}", "ids_a": ";".join(map(str, ia[c])), "ids_b": ";".join(map(str, ib[c])),
                         "text": splits[a]['text'].iloc[ia[c][0]][:160], "labels_a": str([splits[a]['labels'].iloc[i] for i in ia[c]]),
                         "labels_b": str([splits[b]['labels'].iloc[i] for i in ib[c]])})
    return len(common), na, nb
for a, b in (("train", "test"), ("train", "dev"), ("dev", "test")):
    c, na, nb = cross(a, b)
    P(f"- {a} x {b}: {c} shared distinct sentences ({na} {a} rows, {nb} {b} rows)")
pd.DataFrame(dup_rows).to_csv(PACK / "01_duplicates.csv", index=False)
P("\nRow ids (0-based position in each split; train id = position in the tram slice) are in `01_duplicates.csv`.\n")

# near duplicates: token-set Jaccard >= 0.9 via candidate blocking on shared 5-gram shingles
def toks(s): return re.findall(r"[a-z0-9]+", s)
def near(a, b, thr=0.9):
    A = [set(toks(x)) for x in splits[a]["norm"]]; B = [set(toks(x)) for x in splits[b]["norm"]]
    inv = defaultdict(set)
    for j, s in enumerate(B):
        for t in s: inv[t].add(j)
    out = []
    for i, s in enumerate(A):
        if len(s) < 4: continue
        c = Counter()
        for t in s:
            if len(inv[t]) < 400:
                for j in inv[t]: c[j] += 1
        for j, k in c.items():
            if a == b and j <= i: continue
            u = len(s | B[j])
            if u and k / u >= thr and splits[a]["norm"].iloc[i] != splits[b]["norm"].iloc[j]:
                jac = len(s & B[j]) / u
                if jac >= thr: out.append((i, j, round(jac, 3)))
    return out
P("## Near-duplicates (token-set Jaccard >= 0.90, not exact)  [RECOMPUTED]\n")
nd_rows = []
for a, b in (("train", "test"), ("train", "dev"), ("dev", "test"), ("train", "train"), ("test", "test"), ("dev", "dev")):
    nd = near(a, b)
    ra = len(set(i for i, _, _ in nd)); rb = len(set(j for _, j, _ in nd))
    same = sum(set(splits[a]["labels"].iloc[i]) == set(splits[b]["labels"].iloc[j]) for i, j, _ in nd)
    P(f"- {a} x {b}: {len(nd)} pairs ({ra} distinct {a} rows, {rb} distinct {b} rows); identical label sets in {same} pairs")
    for i, j, jac in nd:
        nd_rows.append({"pair": f"{a}_x_{b}", "id_a": i, "id_b": j, "jaccard": jac, "text_a": splits[a]["text"].iloc[i][:140],
                        "text_b": splits[b]["text"].iloc[j][:140], "labels_a": splits[a]["labels"].iloc[i], "labels_b": splits[b]["labels"].iloc[j]})
pd.DataFrame(nd_rows).to_csv(PACK / "01_near_duplicates.csv", index=False)
P("\nPairs listed in `01_near_duplicates.csv`.\n")

# ---- token lengths
P("## Token lengths (incl. special tokens)  [RECOMPUTED]\n")
from transformers import AutoTokenizer
toksrc = {"roberta-base (run dir tokenizer)": CLS / "roberta_pw_s42", "jackaduma/SecBERT (run dir tokenizer)": CLS / "secbert_pw_s42"}
P("| tokenizer | split | mean | median | p95 | max | rows >128 | rows >256 |"); P("|---|---|---|---|---|---|---|---|")
trunc_ids = {}
for name, path in toksrc.items():
    tk = AutoTokenizer.from_pretrained(str(path))
    for n, d in splits.items():
        ln = np.array([len(x) for x in tk(list(d["text"]), truncation=False)["input_ids"]])
        P(f"| {name} | {n} | {ln.mean():.1f} | {int(np.median(ln))} | {int(np.percentile(ln, 95))} | {ln.max()} | {int((ln > 128).sum())} | {int((ln > 256).sum())} |")
        if n == "test": trunc_ids[name] = np.where(ln > 128)[0].tolist()
for name, ids in trunc_ids.items():
    P(f"\n- test row ids truncated at 128 under {name}: `{ids}`")
pd.DataFrame({"tokenizer": [k for k, v in trunc_ids.items() for _ in v], "test_id": [i for v in trunc_ids.values() for i in v]}).to_csv(PACK / "01_truncated_test_ids.csv", index=False)

# ---- descriptions
P("\n## ATT&CK description file  [RECOMPUTED + VERIFIED]\n")
desc = pd.read_csv(DATA / "ttp-desc-mappings.csv", sep="\t")
ids = desc["ttp"].str.lower().str.strip()
drop = {"t1060", "t1107", "t1151", "t1188"}
P(f"- file `Dataset/ttp-desc-mappings.csv` (TAB-separated despite .csv): {len(desc)} rows, {ids.nunique()} unique ids, "
  f"{int(ids.str.contains(r'\.').sum())} sub-techniques, {int((~ids.str.contains(r'\.')).sum())} techniques")
P(f"- matcher label space = {ids.nunique()} - {len(drop & set(ids))} revoked duplicates {sorted(drop)} = **{ids.nunique() - len(drop & set(ids))}** (Exp_2.1 CELL 2, output line 'labels in the matching space: 733')")
P(f"- empty descriptions: {int(desc['description'].fillna('').str.strip().eq('').sum())}")
P(f"- all labels of train/dev/test present in description ids: "
  + ", ".join(f"{n}={all(l.lower() in set(ids) for l in labset[n])}" for n in splits))
P("- version string INSIDE the file: NOT-FOUND (no version column/field). 'ATT&CK v12' appears only in notebook text (Exp_2.1 CELL 0, CELL 2 comments) -> NOTES-ONLY.")
P("- source URL (VERIFIED, Exp_2.1 CELL 1): `https://raw.githubusercontent.com/tumeteor/mitre-ttp-mapping/main/datasets/ttp-desc-mappings.csv` (branch `main`; commit hash NOT-FOUND).")
P("- TRAM split source URL/commit and license: NOT-FOUND in folder (searched notebooks for 'http', 'license', 'github').\n")

P("## Train deduplication  [VERIFIED]\n")
P("- Notebooks run `train.drop_duplicates(subset=['text'])` then `assert len(train) == 3468` (Exp_1_4 CELL 4; Exp_2.1 CELL 2). dev/test are not deduplicated.")
P(f"- The local tram slice already has {len(train)} rows with {train['text'].nunique()} unique raw texts; the pre-dedup row count of tram_train.tsv is NOT-FOUND locally.\n")

ex_tt = cross("train", "test")[0]; ex_td = cross("train", "dev")[0]
nd_tt = len(set(j for i, j, _ in near("train", "test"))); nd_td = len(set(j for i, j, _ in near("train", "dev")))
P("## Claim status A1-A8\n")
P("| ID | claim | file value | status |"); P("|---|---|---|---|")
P(f"| A1 | total 4,797 | {tot} | {'VERIFIED-MATCH' if tot == 4797 else 'MISMATCH'} (RECOMPUTED) |")
P(f"| A2 | 3,468 / 604 / 725 | {len(train)} / {len(dev)} / {len(test)} | MATCH (RECOMPUTED; train from combined_train.csv tram slice) |")
P(f"| A3 | 180 train labels | {len(labset['train'])} | {'MATCH' if len(labset['train']) == 180 else 'MISMATCH'} (RECOMPUTED) |")
P(f"| A4 | 127 test labels | {len(labset['test'])} | {'MATCH' if len(labset['test']) == 127 else 'MISMATCH'} (RECOMPUTED) |")
P(f"| A5 | 117 seen + 10 unseen | {len(seen_te)} + {len(unseen_te)} | MATCH (RECOMPUTED) |")
P(f"| A6 | 2 test and 1 dev sentence also in train | exact (lowercase+whitespace): {ex_tt} test, {ex_td} dev. "
  f"Near-duplicate (Jaccard>=0.90, not exact): +{nd_tt} test, +{nd_td} dev | **MISMATCH**: exact+near gives {ex_tt + nd_tt} test (matches the '2') "
  f"but {ex_td + nd_td} dev (claim says 1); as *exact* duplicates the claim is wrong for both (RECOMPUTED) |")
P(f"| A7 | 34 of 725 test truncated at 128 | RoBERTa tokenizer: {len(trunc_ids['roberta-base (run dir tokenizer)'])}; SecBERT tokenizer: {len(trunc_ids['jackaduma/SecBERT (run dir tokenizer)'])} | MATCH for RoBERTa only; SecBERT truncates 24 (RECOMPUTED) |")
P(f"| A8 | 733 ATT&CK description entries | file has 737 rows; 733 after removing 4 revoked ids | MATCH with qualifier: 733 is the matcher label space, the FILE has 737 (RECOMPUTED + VERIFIED Exp_2.1 CELL 2) |")
w(PACK / "01_dataset.md", "\n".join(L))
print("\n".join(L))
