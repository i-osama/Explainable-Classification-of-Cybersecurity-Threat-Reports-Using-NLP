# E3 report: three draft numbers to decide (report only, the thesis is not edited)

Basis: `Thesis_Draft_v2.3.docx` (paragraph numbers as in `scripts/audit_numbers.py`). Values from `thesis_numbers.json` and `docs/RELATED_WORK_VERIFIED.md`.

## (a) "23 tokens"

Three places, all cited to [8], the TRAM dataset paper:

| para | section | sentence |
|---|---|---|
| 272 | The ATT&CK Knowledge Base and the TRAM Dataset | "…sentences are short, with an average of 23 tokens [8]." |
| 370 | Data and Label Space | "The dataset paper reports 4,797 texts with an average length of 23 tokens, 193 technique and sub-technique labels and 1.16 labels per text, annotated against ATT&CK version 12 [8]." |
| 814 | Why the Transformers Do Not Clearly Beat the SVM | "First, sentences are short, about 23 tokens on average [8], …" |

Source check: `docs/RELATED_WORK_VERIFIED.md` line 75 confirms 23 tokens and 1.16 labels in reference 1, Table 1. So "23 tokens" is correct **as the paper's own figure** and needs no change while it stays cited.

Our own recount of the same 4,797 sentences (the paper does not state its tokeniser; none of these gives 23):

| counting method | mean per sentence | registry |
|---|---|---|
| whitespace-separated words | 21.0 | `A2.words_mean` |
| `\w+` words | 22.5 | note on `A2.words_mean` |
| RoBERTa sub-word tokens | 34.1 | note on `A2.words_mean` |

Option if the author wants an own number: "about 21 words (whitespace) per sentence in our copy (`A2.words_mean`); the dataset paper reports 23 tokens [8]".

## (b) "57.83%"

| para | section | text |
|---|---|---|
| 323 | Review of Related Work / Existing Solutions (table row, Kumarasinghe et al., AsiaCCS 2024) | "P@1 57.83% on its own data; slow (about 8.9 s per query)" |

Search: `_showcase` (results, notes, thesis feed, docs), all notebooks under `Experiments/`, and `_evidence_pack`. The only hits are audit and verification files that flag this number; it does not come from any project result.
Full-text check (`docs/RELATED_WORK_VERIFIED.md`, reference 11, arXiv 2403.17068, checked 15 Nov 2026): 6,612 descriptions and 8.9 s per query are confirmed; **57.83% is not found in the paper**.
Decision for the author: drop "P@1 57.83%" (keep "about 8.9 s per query", which is confirmed), or give the page/table where 57.83% appears.

## (c) Deletion test: 10.19 / 93 of 93 versus 10.13 / 644 of 645

Both appear in the same paragraph, 769 (Explanation Faithfulness):

1. "…reduced the predicted technique's logit by **10.19** logits more than removing random tokens, and the effect had the expected direction for **93 of 93** evaluated sentences [confirm the definition of the 10.19 difference and the eligibility rule behind 93]."
2. "Repeated on all 645 eligible test sentences, the deletion test gives **10.13** logits with the expected direction in **644 of 645**."

No other occurrence of 10.19, 93/93, 93 of 93, 10.13, 644 of 645 or 644/645 in the draft.

Both pairs are correct and registered:

| id | value | meaning | source |
|---|---|---|---|
| `E2` | 10.19 | mean of (drop top-3 minus mean drop random-3), mask variant, logits of the top-1 label; **100-sentence sample**, 93 eligible (100 − 3 too short − 4 truncated) | `_evidence_pack/06_shap.md` line 18; `02_settings.md` line 115 (12.656 − 2.466 = 10.189, CI [9.317, 11.041]) |
| `E3` | 93 / 93 | of those 93, sentences whose top-3 drop exceeds the mean random drop | same |
| `E2.all` | 10.13 | the same test on **all 645 eligible test sentences** (CPU re-run), CI [9.785, 10.502] | `_evidence_pack/06_shap.md` line 28 |
| `E2.all` text | 644 / 645 | direction as expected in 644 of 645 | same |

The bracketed note can be answered from these lines: the definition is the `E2` row below, and eligibility is as stated in `_evidence_pack/06_shap.md` line 18: a sentence is skipped if it is short or has fewer than 3 positive SHAP words, or if it was truncated (100 sampled − 3 skipped − 4 truncated = 93). Suggested mechanical resolution for the author: keep the 645-sentence result as the main figure and give 10.19 / 93 of 93 as the original 100-sentence sample, then delete the bracketed note.
