# Differences between the draft and the files

Basis: the number ledger of **draft v2** pasted by the author on 14 Nov 2026 (`../results/number_audit/ledger_from_author_paste.csv`). Draft v2.2 is not on this PC.
Re-run `scripts/audit_numbers.py` on v2.2 (E7) to confirm which of these are already fixed.

## A The 8 numbers that differ from the files

| para | draft value | file value | why |
|---|---|---|---|
| 192 | `-0.015` | see reason | NOT SUPPORTED: number differs. The draft says 10,000 resamples; at 10,000 the C3 interval is [-0.014, +0.041]. -0.015 / +0.040 is the 1,000-resample notebook-setting interval (_evidence_pack/04_bootstrap.csv) (RoBERTa and the SVM is +0.014 with a 95% interval of -0.015 to +0.040) |
| 192 | `+0.040` | see reason | NOT SUPPORTED: number differs. See the row above: C3 at 10,000 resamples is [-0.014, +0.041] (RoBERTa and the SVM is +0.014 with a 95% interval of -0.015 to +0.040) |
| 676 | `0.037` | see reason | NOT SUPPORTED: number differs. C2 MRR@3 interval is [+0.003, +0.036] (fusion minus matcher ensemble MRR@3 0.019 (0.003 to 0.037 [confirm])) |
| 676 | `+0.020` | see reason | NOT SUPPORTED: number differs. C3 MRR@3 is +0.002 [-0.018, +0.022] (RoBERTa minus SVM +0.002 in MRR@3 (-0.018 to +0.020)) |
| 676 | `-0.022` | see reason | NOT SUPPORTED: number differs. C4 at 10,000 resamples is [-0.023, +0.025]; -0.022 is the 1,000-resample value (RoBERTa minus SecBERT is +0.001 (-0.022 to +0.025) [P@1]) |
| 676 | `+0.003` | see reason | NOT SUPPORTED: number differs. C4 MRR@3 is +0.002 [-0.016, +0.019] (RoBERTa minus SecBERT ... and +0.003 (-0.015 to +0.020) [MRR@3]) |
| 676 | `-0.015` | see reason | NOT SUPPORTED: number differs. C4 MRR@3 interval is [-0.016, +0.019] (RoBERTa minus SecBERT MRR@3 +0.003 (-0.015 to +0.020)) |
| 692 | `+0.020` | see reason | NOT SUPPORTED: number differs. C4 MRR@3 interval is [-0.016, +0.019] (RoBERTa minus SecBERT MRR@3 +0.003 [-0.015, +0.020]) |

Common cause: the draft quotes intervals from the notebook setting (1,000 resamples, seed 0) while saying 10,000 resamples. File values at 10,000 resamples:
C3 +0.014 [-0.014, 0.041]; C4 +0.001 [-0.023, 0.025]; MRR@3 deltas: C2 +0.019 [0.003, 0.036], C3 +0.002 [-0.018, 0.022], C4 +0.002 [-0.016, 0.019].

## B Other contradictions and open marks found in draft v2

| para | draft says | files say | action |
|---|---|---|---|
| 604 (table) | "2 test and 1 development sentence found" | exact 1 / 0; near-duplicate +1 / +3 | replace with exact and near counts |
| 192, 859 | headline 0.803 | the plan says the headline is seed-paired 0.796 +/- 0.006 | pick one definition; see FUSION_DEFINITIONS.md |
| 817 | equal weights 0.779 is "0.002 to 0.005 above the controls (0.774 and 0.777)" | 0.779 uses matcher seed 42 only (`B11`); with the same seed-averaged matcher as the controls it is 0.782 | use 0.782 for the comparison, or say it is not like-for-like |
| 192, 676, 790, 854, 865 | fusion vs matcher ensemble "+0.026 (interval 0.001 to 0.051), p = 0.048", called borderline | after Holm over 8 tests: p = 0.190 | say it does not survive correction |
| 197 | ATT&CK v12: 14 tactics, 193 techniques, 401 sub-techniques | Nguyen et al. (v12.0): 196 techniques, 411 sub-techniques; our description file has 737 entries | cite the source of the count used |
| 313 | TTPXHunter "193 TTPs" | not found in the paper's abstract | check or drop |
| 322, 323, 333, 335 | 6,612; 57.83%; 8.9 s; 24.8; 2,066; 37 | not found by web search | check each in its paper |
| 852 | SHAP "on a sample of 100 sentences" | stored SHAP covers 725 sentences; the deletion test and rating sheet use the first 100 | separate the two |
| 848 | RoBERTa threshold 0.85 "[extended-grid analysis pending]" | done: thresholds 0.93 / 0.83 / 0.88, test micro-F1 change -0.0006 | fill |
| 697, 870 | "[optional: re-evaluate at 256 tokens]" | done at inference: RoBERTa 19 vs 17 of 34 | fill, and say training at 256 was not tested |
| 741 | "[confirm the reference system for 0.0]" | classifiers-only ensemble (0.00); fusion 0.50 | fill |
| 767 | "[confirm ... three-seed ensemble or seed 42]"; 5-19 bucket values missing | matcher = 3-seed ensemble; 5-19: fusion 0.667, matcher 0.646 (n = 96) | fill |
| 502 | "[confirm the seed]" | numpy default_rng(20261114), 10,000 resamples | fill |
| 584, 769 | "[confirm ... sampling rule ... 93 ... 10.19 definition]" | `THESIS_PLACEHOLDERS.md` section 7 | fill |
| 929 (appendix) | "[export requirements.txt]", "[copy tram_train.tsv]" | `requirements.txt` exists; tram_train.tsv is rebuilt by `_evidence_pack/09_repro/make_tram_train.py` (not shipped: licence) | fill |
| 931 (appendix) | "[confirm sampling procedure]" | first 100 of RandomState(42).permutation(725) | fill |
