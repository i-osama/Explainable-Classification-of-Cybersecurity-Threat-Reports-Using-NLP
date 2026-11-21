# 08 Baseline comparability (Nguyen et al.)

## What is in the folder

- Paper PDF or notes: **NOT-FOUND** (searched all of `E:\Osamas Paper` for `*.pdf`, and notebooks for "Nguyen", "Asymmetric", "EACL").
- The baseline numbers appear only as hard-coded constants in notebooks -> **NOTES-ONLY** inside the project:
  - `Exp_2.1_matcher_` CELL 6 and CELL 12: `"Paper: Asymmetric NCE (reference)"`, P@1 .770, R@1 .658, MRR@3 .864, tech_P@1 .903; comment "Nguyen et al., EACL Findings 2024".
  - `Exp_1_4_tram_30ep_3seeds` CELL 18: Asymmetric NCE .770 / .658 and XR-Linear .674 / .626.
- Their code or predictions: **NOT-FOUND** in the folder. Only two of their data files are present: `Dataset/ttp-desc-mappings.csv`
  (downloaded from `github.com/tumeteor/mitre-ttp-mapping`, Exp_2.1 CELL 1) and, by its three `source_dataset` values
  (`procedure`, `derived_procedure`, `tram`), `Dataset/combined_train.csv`.

## Outside check (not a project file)

To avoid leaving F1/F2 as NOTES-ONLY, the arXiv PDF **arXiv:2401.10337** ("Noise Contrastive Estimation-based Matching Framework for
Low-Resource Security Attack Pattern Recognition", Tu Nguyen, Nedim Šrndić, Alexander Neth, Huawei R&D Munich) was fetched on 2026-11-14 and
its text scraped. Status tag used below: **WEB** = read from that PDF, not from the project folder. Page numbers could not be extracted
(no PDF library installed); table and section numbers are given instead. Venue string ("EACL Findings" vs main) was NOT confirmed from the PDF.

| item | quote / value from the paper | where |
|---|---|---|
| TRAM, model "Asymmetric" | P@1 **.770**, R@1 **.658**, F1@3 .555, MRR@3 **.864** | Table 2, TRAM columns |
| TRAM, "@-balanced" | P@1 .765, R@1 .646, F1@3 .546, MRR@3 .856 | Table 2 |
| TRAM, InfoNCE | .697 / .577 / .516 / .799 | Table 2 |
| TRAM, XR-LINEAR | .674 / .626 / .445 / .757 | Table 2 |
| TRAM, NAPKINXC | .662 / .614 / .453 / .754 | Table 2 |
| TRAM technique-level, Asymmetric | P@1 **.903**, R@1 .789, F1@3 .726, MRR@3 .938 | Table 3 ("resolve sub-techniques to their super-techniques") |
| TRAM size | "TRAM 4797 [texts] 193 [S+T] 132 [techniques] 1.16 [avg labels] 23 [avg tokens]" | Table 1 |
| TRAM source | "CTID TRAM: github.com/CTID/TRAM" | footnote 4 |
| split | "each was stratified-shuffled and split into training, validation and test sets with ratios of 72.5%, 12.5% and 15%, respectively. The test sets remained fixed for reporting purposes." | Sec. 5.3 |
| training modes | "two modes were considered: separate and combined. In the former, the datasets are kept distinct, while in the latter, they were merged according to their respective splits." | Sec. 5.3 |
| encoder | "We use the common security LM SecBERT for the transformer-based models" | Sec. 5.3 |
| ATT&CK version | "The version 12.0 comprises 14 tactics, 196 techniques, 411 sub-techniques" | Appendix (background) |
| P@k | "the micro precision of the top-k is defined as: P@k = 1/k Σ_{i=1..k} 1_{y+}(l_i)" | App. D.1 |
| R@k | "R@k = 1/|Q| Σ_{i=1..k} 1_{y+}(l_i), whereas |Q| is the number of positive labels in the sample" | App. D.1 |
| MRR@k | "RR is the inverse rank of the first relevant item in the top-k ranked list ... MRR@k = 1/S Σ_{i=1..S} 1/rank_i, whereas S is the number of samples" | App. D.1 |
| data release | "The datasets are publicly shared at github.com/[...]TTP-Mapping" | footnote 5 |

## Claims

| ID | claim | value | status |
|---|---|---|---|
| F1 | Nguyen et al. P@1 0.770 | .770 (TRAM, Asymmetric, Table 2) | NOTES-ONLY in the project; **confirmed WEB** |
| F2 | Nguyen et al. MRR@3 0.864 | .864 (same row) | NOTES-ONLY in the project; **confirmed WEB** |

## Comparability

| field | ours | theirs | verdict |
|---|---|---|---|
| test set | 725 sentences, `Dataset/tram_test.tsv` | 15% stratified split of 4,797 TRAM texts (15% = 720; our 725 = 15.1%); total 4,797 and 193 S+T labels equal ours (`01_dataset.md`) | **UNKNOWN (probably same)**: sizes agree and our files come from their repository, but no hash or row-level comparison with their released split was possible (their split files are not in the folder) |
| ATT&CK version | "v12" stated only in notebook text; description file has no version field | v12.0 (stated) | **SAME by statement, not verified from data** |
| label set | 193 labels over all splits; exact-ID match; ranking over 733 descriptions (737 minus 4 revoked) | 193 S+T for TRAM; size of their ranking label space not extracted | **SAME for the TRAM label inventory (193); candidate set UNKNOWN** |
| metric definitions | P@1 = share of sentences whose top-1 is gold; MRR@3 = mean 1/rank of first gold in top 3, 0 if none (`scripts/common.py`) | P@1 and MRR@k as quoted above | **SAME for P@1 and MRR@3** (the paper does not say what a sentence with no hit in the top k contributes; 0 is the only sensible reading). **DIFFERENT for R@1**: the paper's formula is per-sample (hits/|Q|), the notebooks' "paper-style R@1" is hits / all gold labels (Exp_1_4 CELL 18), so our R@1 must not be compared with their .658 |
| training data | TRAM train only (3,468) | "separate" or "combined" (Procedures+ merged in); which mode produced Table 2 was not extracted; Table 4 (head/tail) says "All are trained in combined mode" | **UNKNOWN, possibly DIFFERENT**: if Table 2 is combined mode the baseline saw about 4x more training text |
| technique-level number | our tech_P@1 0.808 (fusion) | .903 | **NOT COMPARABLE as coded**: notebook itself flags it ("not comparable to our tech_P@1") |

Consequence for the thesis: "fusion P@1 0.803 vs. 0.770, MRR@3 0.856 vs. 0.864" may be reported as a side-by-side with the published figure,
but not as a controlled comparison. The baseline was not re-run on this machine; its code is not in the folder.
