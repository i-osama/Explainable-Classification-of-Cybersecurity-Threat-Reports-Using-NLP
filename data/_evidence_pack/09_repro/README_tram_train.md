# tram_train.tsv

`tram_train.tsv` is **not on E:** (the notebooks read it from Google Drive) and is **not copied into this pack**: no license
text for the TRAM data exists anywhere in the project folder (searched for LICENSE files and the words "license"/"licence"
in all notebooks), so redistribution rights are NOT-FOUND.

How to obtain it:

1. Rebuild locally (verified): `python make_tram_train.py` extracts the 3,468 rows with `source_dataset == 'tram'` from
   `Dataset/combined_train.csv`. Check: 3,468 rows, 180 labels, 0 duplicate texts, and the SVM refit on it reproduces the
   notebook's numbers exactly (micro-F1 0.6961, P@1 0.7421; `03_results.md`).
2. Upstream sources named in the project and in the baseline paper (commit hashes NOT-FOUND):
   - `https://github.com/tumeteor/mitre-ttp-mapping` (the description file was downloaded from its `datasets/` folder, Exp_2.1 CELL 1;
     the exact path of the TRAM split files in that repository was not verified)
   - original annotations: `https://github.com/CTID/TRAM` (named in the baseline paper, footnote 4)

Pre-deduplication size of the original train file: NOT-FOUND (notebooks drop duplicate texts and assert 3,468).
