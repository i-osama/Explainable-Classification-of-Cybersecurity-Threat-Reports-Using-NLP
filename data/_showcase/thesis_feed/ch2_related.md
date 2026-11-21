# Chapter 2: Related work: numbers, tables, figures, caveats

Every number below comes from `thesis_numbers.json` (do not retype; quote the id). Status meanings: RECOMPUTED = recomputed from saved predictions by a showcase script; VERIFIED = read from a file or code; NOTES-ONLY = a copied constant; TODO-COLAB = not yet run; NOT-FOUND = searched, absent.

## Numbers

| id | value | 95% CI | definition | source file | status |
|---|---|---|---|---|---|
| `F1` | 0.770 |  | Published baseline P@1 (Nguyen et al., TRAM, 'Asymmetric'). constant typed into the notebooks from the paper; confirmed against arXiv:2401.10337 Table 2 (not a project file); not re-run | `run_match_1/final_results_table.csv; _evidence_pack/08_baseline.md` | NOTES-ONLY |
| `F2` | 0.864 |  | Published baseline MRR@3. as F1 | `run_match_1/final_results_table.csv; _evidence_pack/08_baseline.md` | NOTES-ONLY |

## Numbers from other papers (not in thesis_numbers.json; cite each)

| number in draft | source paper | status (docs/RELATED_WORK_VERIFIED.md) |
|---|---|---|
| P@1 .770, MRR@3 .864 (TRAM, "Asymmetric") | Nguyen et al., arXiv:2401.10337, Table 2 | VERIFIED from the PDF |
| P@1 .674 (XR-LINEAR on TRAM) | same, Table 2 | VERIFIED from the PDF |
| 1.16 labels and 23 tokens per TRAM text | same, Table 1 | VERIFIED from the PDF |
| about 24 h training on one V100 | same, Limitations | VERIFIED from the PDF |
| 39,296 samples; F1 92.42% | TTPXHunter, arXiv:2403.03267 | VERIFIED (abstract) |
| "193 TTPs" for TTPXHunter | TTPXHunter, full text Fig. 9 | VERIFIED (full text, 15 Nov 2026) |
| 6,612 descriptions; 8.9 s per query | Kumarasinghe et al., AsiaCCS 2024 | VERIFIED (full text, 15 Nov 2026) |
| P@1 57.83% | Kumarasinghe et al., AsiaCCS 2024 | NOT FOUND in the full text: drop it or give its source |
| F1 24.8 of the TRAM model on AnnoCTR | Lange et al., LREC-COLING 2024 | VERIFIED (full text: "TRAM baseline 24.8") |
| 2,066 sentences, 37 techniques (TRAM-Clean) | Cheng et al., CTI2TTP, arXiv 2605.25836 | VERIFIED (full text, 15 Nov 2026) |
| 14 tactics, 193 techniques, 401 sub-techniques (ATT&CK v12) | draft cites ATT&CK | CONFLICT: Nguyen et al. state 196 techniques and 411 sub-techniques for v12.0 |
| best micro-F1 0.22 of seven open LLMs (8B-236B) on complex CTI reports; 2,076 sentences, 114 techniques | Ryan et al., arXiv 2606.18166 (2026) | VERIFIED (abstract); other data than TRAM: do not compare numbers directly |
| 29 methods on 90 reports of 3 campaigns; max F1 78.6% (SolarWinds), 54.9% (XZ Utils) | Haque et al., arXiv 2604.07470 (2026) | VERIFIED (abstract) |
| 150 reports mapped to ATT&CK version 19.1; 269 techniques | Das et al., arXiv 2607.23312 (2026) | VERIFIED (abstract and full text) |

Recent work (2026) to discuss: open-weights LLMs are weak at multi-label technique classification on complex reports (Ryan et al.), which matches our local LLM baseline (`L1`, prereg 17); campaign-level extraction differs from sentence-level TRAM evaluation (Haque et al.); current datasets already use ATT&CK v19.1 while TRAM is v12.1 (Das et al.; our drift check `AD1`).


## Caveats to state

- Numbers taken from other papers are not in thesis_numbers.json. Each needs a citation; one is not found in its paper (57.83%) and one count conflicts (ATT&CK v12), see `docs/RELATED_WORK_VERIFIED.md`.
- The published baseline (0.770, 0.864) was not re-run; split and training mode are not verified to match ours.
