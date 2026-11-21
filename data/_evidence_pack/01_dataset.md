# 01 Dataset proof

Sources: `Dataset/tram_dev.tsv`, `Dataset/tram_test.tsv`, train = rows of `Dataset/combined_train.csv` with `source_dataset == 'tram'` (`tram_train.tsv` itself is NOT-FOUND on E:; notebooks read it from Google Drive).

## Rows and labels per split  [RECOMPUTED]

| split | rows | unique labels | label assignments | single-label rows | multi-label rows | max labels/row | sub-technique labels | parent-level labels |
|---|---|---|---|---|---|---|---|---|
| train | 3468 | 180 | 4001 | 3056 | 412 | 9 | 74 | 106 |
| dev | 604 | 123 | 701 | 542 | 62 | 7 | 45 | 78 |
| test | 725 | 127 | 851 | 635 | 90 | 6 | 47 | 80 |

Total sentences: **4797**. Rows with duplicate label ids inside one row: train=11, dev=2, test=1.

- test labels: 127 = 117 seen in train + 10 unseen: `['T1011', 'T1134.005', 'T1218.002', 'T1485', 'T1547.005', 'T1548.001', 'T1548.003', 'T1552.004', 'T1556.002', 'T1574.010']`
- dev labels: 123 = 119 seen + 4 unseen: `['T1055.011', 'T1216', 'T1547.005', 'T1569.001']`
- test rows with >=1 unseen label: 10; rows whose labels are ALL unseen: 10; unseen (row,label) pairs: 10
- test (row,label) pairs total: 851

Per-label support per split: `01_label_counts.csv` (193 labels across all splits).

Train support distribution (labels with train>0): median=7, min=1, max=170, labels with <5 train rows=79, <10=100

## Duplicates (lowercase + whitespace-normalised)  [RECOMPUTED]

- within train: 1 redundant rows in 1 duplicate groups (raw-text exact dup rows: 0)
- within dev: 0 redundant rows in 0 duplicate groups (raw-text exact dup rows: 0)
- within test: 0 redundant rows in 0 duplicate groups (raw-text exact dup rows: 0)
- train x test: 1 shared distinct sentences (1 train rows, 1 test rows)
- train x dev: 0 shared distinct sentences (0 train rows, 0 dev rows)
- dev x test: 0 shared distinct sentences (0 dev rows, 0 test rows)

Row ids (0-based position in each split; train id = position in the tram slice) are in `01_duplicates.csv`.

## Near-duplicates (token-set Jaccard >= 0.90, not exact)  [RECOMPUTED]

- train x test: 1 pairs (1 distinct train rows, 1 distinct test rows); identical label sets in 1 pairs
- train x dev: 4 pairs (4 distinct train rows, 3 distinct dev rows); identical label sets in 3 pairs
- dev x test: 1 pairs (1 distinct dev rows, 1 distinct test rows); identical label sets in 1 pairs
- train x train: 0 pairs (0 distinct train rows, 0 distinct train rows); identical label sets in 0 pairs
- test x test: 0 pairs (0 distinct test rows, 0 distinct test rows); identical label sets in 0 pairs
- dev x dev: 0 pairs (0 distinct dev rows, 0 distinct dev rows); identical label sets in 0 pairs

Pairs listed in `01_near_duplicates.csv`.

## Token lengths (incl. special tokens)  [RECOMPUTED]

| tokenizer | split | mean | median | p95 | max | rows >128 | rows >256 |
|---|---|---|---|---|---|---|---|
| roberta-base (run dir tokenizer) | train | 36.0 | 22 | 105 | 1173 | 126 | 36 |
| roberta-base (run dir tokenizer) | dev | 37.4 | 23 | 117 | 787 | 27 | 7 |
| roberta-base (run dir tokenizer) | test | 35.4 | 22 | 112 | 335 | 34 | 4 |
| jackaduma/SecBERT (run dir tokenizer) | train | 31.4 | 20 | 92 | 865 | 95 | 21 |
| jackaduma/SecBERT (run dir tokenizer) | dev | 32.5 | 20 | 99 | 523 | 22 | 5 |
| jackaduma/SecBERT (run dir tokenizer) | test | 31.5 | 20 | 95 | 298 | 24 | 3 |

- test row ids truncated at 128 under roberta-base (run dir tokenizer): `[472, 489, 492, 537, 550, 580, 610, 630, 636, 665, 666, 669, 673, 678, 682, 683, 684, 687, 690, 693, 697, 698, 699, 702, 706, 707, 711, 712, 713, 714, 717, 718, 721, 722]`

- test row ids truncated at 128 under jackaduma/SecBERT (run dir tokenizer): `[472, 489, 492, 550, 610, 636, 666, 669, 673, 678, 683, 684, 687, 693, 697, 702, 706, 707, 711, 713, 714, 717, 718, 721]`

## ATT&CK description file  [RECOMPUTED + VERIFIED]

- file `Dataset/ttp-desc-mappings.csv` (TAB-separated despite .csv): 737 rows, 737 unique ids, 404 sub-techniques, 333 techniques
- matcher label space = 737 - 4 revoked duplicates ['t1060', 't1107', 't1151', 't1188'] = **733** (Exp_2.1 CELL 2, output line 'labels in the matching space: 733')
- empty descriptions: 0
- all labels of train/dev/test present in description ids: train=True, dev=True, test=True
- version string INSIDE the file: NOT-FOUND (no version column/field). 'ATT&CK v12' appears only in notebook text (Exp_2.1 CELL 0, CELL 2 comments) -> NOTES-ONLY.
- source URL (VERIFIED, Exp_2.1 CELL 1): `https://raw.githubusercontent.com/tumeteor/mitre-ttp-mapping/main/datasets/ttp-desc-mappings.csv` (branch `main`; commit hash NOT-FOUND).
- TRAM split source URL/commit and license: NOT-FOUND in folder (searched notebooks for 'http', 'license', 'github').

## Train deduplication  [VERIFIED]

- Notebooks run `train.drop_duplicates(subset=['text'])` then `assert len(train) == 3468` (Exp_1_4 CELL 4; Exp_2.1 CELL 2). dev/test are not deduplicated.
- The local tram slice already has 3468 rows with 3468 unique raw texts; the pre-dedup row count of tram_train.tsv is NOT-FOUND locally.

## Claim status A1-A8

| ID | claim | file value | status |
|---|---|---|---|
| A1 | total 4,797 | 4797 | VERIFIED-MATCH (RECOMPUTED) |
| A2 | 3,468 / 604 / 725 | 3468 / 604 / 725 | MATCH (RECOMPUTED; train from combined_train.csv tram slice) |
| A3 | 180 train labels | 180 | MATCH (RECOMPUTED) |
| A4 | 127 test labels | 127 | MATCH (RECOMPUTED) |
| A5 | 117 seen + 10 unseen | 117 + 10 | MATCH (RECOMPUTED) |
| A6 | 2 test and 1 dev sentence also in train | exact (lowercase+whitespace): 1 test, 0 dev. Near-duplicate (Jaccard>=0.90, not exact): +1 test, +3 dev | **MISMATCH**: exact+near gives 2 test (matches the '2') but 3 dev (claim says 1); as *exact* duplicates the claim is wrong for both (RECOMPUTED) |
| A7 | 34 of 725 test truncated at 128 | RoBERTa tokenizer: 34; SecBERT tokenizer: 24 | MATCH for RoBERTa only; SecBERT truncates 24 (RECOMPUTED) |
| A8 | 733 ATT&CK description entries | file has 737 rows; 733 after removing 4 revoked ids | MATCH with qualifier: 733 is the matcher label space, the FILE has 737 (RECOMPUTED + VERIFIED Exp_2.1 CELL 2) |