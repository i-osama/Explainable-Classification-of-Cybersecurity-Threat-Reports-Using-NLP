# 06 Explainability evidence

## Stored SHAP output  [VERIFIED from file]

- file `Exp_3_0_shap/shap_v2_roberta_pw_s42.jsonl`: 725 records, 725 distinct test rows, all with identical method block: `{'unit': 'whitespace-delimited word', 'masking': 'word replaced by <mask>, surrounding whitespace kept', 'algorithm': 'permutation', 'n_perm': 40, 'shap_seed': 42, 'output': 'logit of the top-1 predicted label', 'max_length': 128}`
- all records share one method: True; rows cover all 725 test ids: True
- stored order equals `RandomState(42).permutation(725)`: True
- top-1 correct: 549 of 725; truncated (>128 tokens): 34; max additivity error |sum(shap)+base-logit|: 2.0e-05
- words per sentence: mean 21.3, median 15, max 141
- older files (not used in the thesis numbers): `shap_roberta_pw_s42.jsonl` (20 rows, token-level, no method block), `shap_v1_roberta_pw_s42.jsonl` (100 rows, n_perm=10).

## Method  [VERIFIED: Exp_3_0b CELL 2, Exp_3_1_deletion_test CELL 0/2/3]

- explained model: `Exp_1_4_run_tram_2_epoc_30/roberta_pw_s42` (RoBERTa-base, pos_weight, seed 42). It was the designated SHAP model before any test result existed (Exp_1_4 CELL 10 comment: 'RoBERTa + class weights first (this is the model SHAP needs)'), i.e. not picked by test score.
- explainer: `shap.Explainer(f, shap.maskers.Independent(zeros(1,n)), algorithm='permutation', seed=42)`, shap 0.54.1; features = whitespace-delimited words; a hidden word is replaced by `<mask>` (whitespace kept); `max_evals = 40*(2n+1)` = 40 permutations; output explained = raw logit of the model's top-1 label.
- sample: ALL 725 test sentences (the first 100 of the fixed permutation were computed first and are the ones used for the deletion test and the human sheet).
- deletion test: for each sentence hide the K=3 words with the highest positive SHAP value and measure drop = logit(original) - logit(edited) of the top-1 label; compare with the mean drop over 20 random 3-word subsets (RandomState(42+row)). Two variants: *mask* (`<mask>` token) and *remove* (word deleted). Sentences need >= 6 words and >= 3 positive SHAP words; truncated sentences reported separately. CI: 1,000 bootstrap resamples of sentences, RandomState(42), percentile.
- **10.19** = mean over 93 sentences of (drop top-3) - (mean drop random-3), *mask* variant, in logit units. **93/93** = number of those sentences where the top-3 drop exceeds the mean random drop. 93 = 100 sampled - 3 skipped (short / <3 positive words) - 4 truncated.

## Deletion test numbers

| source | variant | n | mean drop top-3 | mean drop random-3 | difference | 95% CI | top-3 larger |
|---|---|---|---|---|---|---|---|
| saved CSV (100 sampled rows) [RECOMPUTED from file] | mask | 93 | 12.656 | 2.466 | 10.189 | [9.317, 11.041] | 93 / 93 |
| saved CSV (100 sampled rows) [RECOMPUTED from file] | remove | 93 | 12.768 | 2.643 | 10.125 | [9.229, 11.004] | 93 / 93 |
| CPU re-run, same 100 rows [RECOMPUTED with checkpoint] | mask | 93 | 12.656 | 2.466 | 10.189 | [9.317, 11.041] | 93 / 93 |
| CPU re-run, same 100 rows [RECOMPUTED with checkpoint] | remove | 93 | 12.768 | 2.643 | 10.125 | [9.229, 11.004] | 93 / 93 |
| CPU re-run, ALL 725 rows [RECOMPUTED, new] | mask | 645 | 12.722 | 2.590 | 10.132 | [9.785, 10.502] | 644 / 645 |
| CPU re-run, ALL 725 rows [RECOMPUTED, new] | remove | 645 | 12.795 | 2.701 | 10.094 | [9.747, 10.446] | 642 / 645 |
|   ALL rows, top-1 correct only | mask | 489 | 13.525 | 2.784 | 10.741 | [10.342, 11.130] | 488 / 489 |
|   ALL rows, top-1 correct only | remove | 489 | 13.615 | 2.863 | 10.752 | [10.382, 11.151] | 487 / 489 |
|   ALL rows, top-1 wrong only | mask | 156 | 10.206 | 1.984 | 8.222 | [7.595, 8.835] | 156 / 156 |
|   ALL rows, top-1 wrong only | remove | 156 | 10.226 | 2.195 | 8.031 | [7.421, 8.591] | 155 / 156 |

Saved CSV: 100 rows, used 97, skipped 3, used-and-truncated 4.
CPU re-run vs stored: max |stored logit - recomputed logit| over 725 rows = 4.20e-05; top-1 label differs in 0 rows; max |drop_top_mask saved - CPU| on the 100 rows = 3.72e-05.
All-725 run: used 679, skipped 46, used-and-truncated 34 (excluded from the table).

Claims: E1 SHAP permutation / 40 permutations / roberta_pw_s42 -> VERIFIED. E2 10.19 -> RECOMPUTED 10.189 (mask). E3 93/93 -> RECOMPUTED.

Caveats to state in the thesis: (1) the *mask* variant uses the same perturbation as SHAP, so it tests internal consistency; the *remove* variant is the more independent check. (2) The explained model is ONE seed of ONE component (RoBERTa); it is not the fusion system that gives the headline P@1. (3) The number is on the top-1 logit, so it says nothing about whether the prediction is right.

## Example figures

Rule (written before looking at any attribution): among the 725 test sentences, take the LOWEST test sentence id that is (ex1) single-label gold and top-1 correct; (ex2) multi-label gold (>=2 distinct labels) and top-1 correct; (ex3) top-1 wrong. Model: roberta_pw_s42. Long sentences: the 20 words with the largest |SHAP| are drawn, in sentence order (all words if <= 25).

| figure | test id | gold | predicted | prob | correct | words | sum(SHAP)+base = logit |
|---|---|---|---|---|---|---|---|
| fig_shap_ex1.png | 0 | T1082 | T1082 (System Information Discovery) | 1.000 | True | 14 | 10.355 = 10.355 |
|  | sentence | can collect system information, including computer name, system manufacturer, IsDebuggerPresent state, and execution path. |  |  |  |  |  |
| fig_shap_ex2.png | 3 | T1547.001, T1547.009 | T1547.009 (Shortcut Modification) | 0.997 | True | 10 | 5.955 = 5.955 |
|  | sentence | achieves persistence by creating a shortcut in the Startup folder. |  |  |  |  |  |
| fig_shap_ex3.png | 1 | T1018, T1069 | T1005 (Data from Local System) | 0.453 | False | 23 | -0.188 = -0.188 |
|  | sentence | FIN6 conducted internal reconnaissance with a Windows batch file leveraging Adfind to query Active Directory, then 7-zip to compress the results for exfiltration |  |  |  |  |  |