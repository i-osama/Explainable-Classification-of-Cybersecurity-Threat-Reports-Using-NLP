# CHANGELOG v2.3

`Thesis_Draft_v2.3.docx` = `Thesis_Draft_v2.2.docx` with 13 confidence intervals changed from the old 1,000-resample values to the 10,000-resample values in `thesis_numbers.json` (paired percentile bootstrap, seed 20261114). Only digits changed; no prose, layout or other number was touched. Rows marked `point:` correct a point estimate that came from the same stale source (registry value 0.0016 shown as +0.002). Generated and checked by `scripts/make_draft_v23.py` (the paragraph texts of v2.2 and v2.3 differ in exactly these places).

| # | para | section | table row | context (v2.2) | old | new | claim id | claim |
|---|---|---|---|---|---|---|---|---|
| 1 | 192 |  |  | …etween RoBERTa and the SVM is +0.014 with a 95% interval of −0.015 to +0.040. Fine-tuning raises… | −0.015 to +0.040 | −0.014 to +0.041 | `C3` | RoBERTa minus SVM, delta P@1 |
| 2 | 676 | Statistical Comparison of Systems |  | ….001 to 0.051 [confirm upper bound]) and by 0.019 in MRR@3 (0.003 to 0.037 [confirm]). With 10… | 0.003 to 0.037 | 0.003 to 0.036 | `C2.mrr` | Fusion minus matcher ensemble, delta MRR@3 |
| 3 | 676 | Statistical Comparison of Systems |  | … is clear. In contrast, RoBERTa minus SVM is +0.014 in P@1 (−0.015 to +0.040) and +0.002 in MRR@… | −0.015 to +0.040 | −0.014 to +0.041 | `C3` | RoBERTa minus SVM, delta P@1 |
| 4 | 676 | Statistical Comparison of Systems |  | …VM is +0.014 in P@1 (−0.014 to +0.041) and +0.002 in MRR@3 (−0.018 to +0.020), and RoBERTa minus… | −0.018 to +0.020 | −0.018 to +0.022 | `C3.mrr` | RoBERTa minus SVM, delta MRR@3 |
| 5 | 676 | Statistical Comparison of Systems |  | …@3 (−0.018 to +0.022), and RoBERTa minus SecBERT is +0.001 (−0.022 to +0.025) and +0.003 (−0.015… | −0.022 to +0.025 | −0.023 to +0.025 | `C4` | RoBERTa minus SecBERT, delta P@1 |
| 6 | 676 | Statistical Comparison of Systems |  | …ERTa minus SecBERT is +0.001 (−0.023 to +0.025) and +0.003 (−0.015 to +0.020). These intervals i… | −0.015 to +0.020 | −0.016 to +0.019 | `C4.mrr` | RoBERTa minus SecBERT, delta MRR@3 |
| 7 | 686 | Statistical Comparison of Systems | Fusion − matcher 3-seed ensemble | …+0.019 [+0.003, +0.037]… | [+0.003, +0.037] | [+0.003, +0.036] | `C2.mrr` | Fusion minus matcher ensemble, delta MRR@3 |
| 8 | 688 | Statistical Comparison of Systems | RoBERTa − SVM (seed-averaged) | …+0.014 [−0.015, +0.040]… | [−0.015, +0.040] | [−0.014, +0.041] | `C3` | RoBERTa minus SVM, delta P@1 |
| 9 | 689 | Statistical Comparison of Systems | RoBERTa − SVM (seed-averaged) | …+0.002 [−0.018, +0.020]… | [−0.018, +0.020] | [−0.018, +0.022] | `C3.mrr` | RoBERTa minus SVM, delta MRR@3 |
| 10 | 691 | Statistical Comparison of Systems | RoBERTa − SecBERT (seed-averaged) | …+0.001 [−0.022, +0.025]… | [−0.022, +0.025] | [−0.023, +0.025] | `C4` | RoBERTa minus SecBERT, delta P@1 |
| 11 | 692 | Statistical Comparison of Systems | RoBERTa − SecBERT (seed-averaged) | …+0.003 [−0.015, +0.020]… | [−0.015, +0.020] | [−0.016, +0.019] | `C4.mrr` | RoBERTa minus SecBERT, delta MRR@3 |
| 12 | 790 | Answers to the Research Questions |  | …between RoBERTa and the SVM is +0.014 with an interval from −0.015 to +0.040, and the micro-F1 v… | −0.015 to +0.040 | −0.014 to +0.041 | `C3` | RoBERTa minus SVM, delta P@1 |
| 13 | 798 | Answers to the Research Questions | Transformers are tied with the SVM | …ΔP@1 +0.014 [−0.015, +0.040]… | [−0.015, +0.040] | [−0.014, +0.041] | `C3` | RoBERTa minus SVM, delta P@1 |
| 14 | 676 | Statistical Comparison of Systems |  | … and RoBERTa minus SecBERT is +0.001 (−0.023 to +0.025) and +0.003 (−0.016 to +0.019). These i… | +0.003 (−0.016 | +0.002 (−0.016 | `point:C4.mrr` | RoBERTa minus SecBERT, delta MRR@3 |
| 15 | 692 | Statistical Comparison of Systems | RoBERTa − SecBERT (seed-averaged) | …+0.003 [−0.016, +0.019]… | +0.003 [−0.016 | +0.002 [−0.016 | `point:C4.mrr` | RoBERTa minus SecBERT, delta MRR@3 |

Characters changed per paragraph: {192: 2, 676: 9, 686: 1, 688: 2, 689: 1, 691: 1, 692: 4, 790: 2, 798: 2}. Paragraph numbers follow `scripts/audit_numbers.py` (body order, table cells included).
