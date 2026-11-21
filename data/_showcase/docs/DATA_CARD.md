# Data card

| | |
|---|---|
| Name | TRAM sentence-level ATT&CK technique annotations, in the split distributed with the repository of Nguyen et al. |
| Unit | one sentence (or short passage) of a cyber-threat-intelligence report with one or more ATT&CK technique or sub-technique ids |
| Sizes | 4,797 sentences: 3,468 / 604 / 725 (train / dev / test). Train after exact-text de-duplication |
| Labels | 180 in train, 127 in test (117 + 10 seen + unseen); 90 test sentences carry more than one label; 851 gold (sentence, label) pairs in test |
| Long tail | median 7 training sentences per label; 79 labels have fewer than 5 |
| Overlap | exact 1 / 0; near-duplicate +1 / +3 |
| Length | 34 (RoBERTa tokenizer); 24 (SecBERT tokenizer) test sentences exceed 128 tokens |
| Label descriptions | `ttp-desc-mappings.csv` (tab-separated): 737 in the file; 733 used |
| Sibling data | `combined_train.csv`: 14,465 rows from three sources (8,487 procedure, 3,468 tram, 2,510 derived_procedure), 478 labels; used only as the source of the TRAM train rows |
| Source | description file: `github.com/tumeteor/mitre-ttp-mapping` (URL in `Exp_2.1` CELL 1); original annotations: `github.com/center-for-threat-informed-defense/tram` |
| Licence | No licence file in the project. The Hugging Face dataset card lists "cc" without a variant (DOI 10.57967/hf/1811), as reported by the author; variant [FILL]. Because the variant is unknown, this showcase ships no sentence text: only ids, SHA-256 hashes, lengths, labels and derived metrics (`results/tables/sentences.parquet`) |
| ATT&CK version | "version 12" according to notebook comments and the baseline paper; **no version string inside any data file** |
| Known issues | annotation noise is reported in the literature; one normalised test sentence also occurs in train; `tram_train.tsv` itself is not in the folder and is rebuilt from `combined_train.csv` |

## Obtaining the data

1. TRAM dev and test: the files `tram_dev.tsv`, `tram_test.tsv` of the baseline repository. 2. Train: `python ../_evidence_pack/09_repro/make_tram_train.py`.
3. Check: `python scripts/check_hashes.py` compares the files with the recorded hashes.

## Intended and unintended use

Research on mapping CTI text to ATT&CK. Not validated for operational triage: accuracy on rare techniques is low and labels are noisy.
