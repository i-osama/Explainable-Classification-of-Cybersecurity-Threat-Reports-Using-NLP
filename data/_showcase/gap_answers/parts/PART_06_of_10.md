THESIS GAP ANSWERS - PART 6/10 - 2026-11-21
=== G20 | NOT-RUN ===
FACTS:
returned repeat-study sheets: none. _showcase\human_study\returned\ holds only raters_TEMPLATE.csv (14 Nov 18:04, empty rows R1-R2...)
sent kits: _showcase\human_study\TO_SEND\rater_R1.zip, rater_R2.zip, rater_R3.zip (16 Nov 01:19); each = rating_sheet_Rn.csv, READ_FIRST_instructions.md, worked_examples.md, raters.csv
no returned copy anywhere in E:\Osamas Paper or Downloads (search rating_sheet*)
instruction sheet: _showcase\docs\RATER_INSTRUCTIONS.md = READ_FIRST_instructions.md in each zip (sha256 aeee52ee5ad02a9a identical); full text in APPENDIX G20 at the end of this file
SOURCE: directory listing of _showcase\human_study\{returned,TO_SEND}; search for rating_sheet* in E:\Osamas Paper and %USERPROFILE%\Downloads; sha256 of RATER_INSTRUCTIONS.md and the zip members
EVIDENCE: returned\ holds 1 file: raters_TEMPLATE.csv (14 Nov 18:04)
CAVEAT: scale 1-5 (not the 0-2 scale of study 1); some rows mark random words (controls). Agreement statistics: NOT-RUN (no data).

=== G21 | NEEDS-AUTHOR ===
FACTS:
.git roots: one, E:\Osamas Paper\.git; `git remote -v`: origin -> github.com/<personal account, withheld>/ttp-thesis-showcase.git (fetch, push); local main is 17 commits ahead of origin/main
the remote URL and the commit author are the PC user's personal identity: do not use this URL in the thesis
publishable manifest: _showcase\gap_answers\publish_manifest.csv (376 tracked files; 373 kept, 10.48 MB; columns file, bytes, excluded_flag, review_note)
excluded (G03): _evidence_pack/05_errors.md, _evidence_pack/06_shap.md, _showcase/tests/test_fusion_stats_schema.py
excluded (G04 rater data): none tracked (07_human.md and 07_agreement.csv hold only aggregates, roles and hash prefixes)
review by eye: _evidence_pack/fig_shap_ex1-3.png, _showcase/figures/fig14_shap_examples.png/.svg (may show sentence words)
SOURCE: git remote -v; git ls-files; git ls-tree origin/main
EVIDENCE: `git status -sb` -> "## main...origin/main [ahead 17]"
CAVEAT: no commit or push made; the 2 G03 files are already on origin/main, so leaving them out of a new copy does not remove them from the existing remote.
QUESTIONS: Repository URL for Appendix C, or confirm a new public repository will be created (under whose account) and from which folder?

=== G22 | NEEDS-AUTHOR ===
FACTS: supervisor's additional references: NOT-FOUND (no .bib/.ris, reference list, note, mail or message file; only the open item _showcase\CHANGELOG_v2.4.md:76 "p337: additional references recommended by the supervisor")
v4 sentence: paragraph 942 (Achievement and Objectives) "...it should be extended with the supervisor's additional references."
SOURCE: _showcase\CHANGELOG_v2.4.md:76; Thesis_Final-v4.docx p942; search of E:\Osamas Paper and %USERPROFILE%\Downloads for .bib, .ris and reference-list files
EVIDENCE: CHANGELOG_v2.4.md:76 "- p337: additional references recommended by the supervisor."
CAVEAT: none.
QUESTIONS: Paste the supervisor's additional references, or confirm there are none (then the sentence is deleted)?

=== X1 | VERIFIED ===
FACTS:
P@1 / MRR@3 (_showcase\src\ttpmap\metrics.py):
:20-22 `def rank_topk(scores, k): return np.argsort(-scores, axis=1, kind="stable")[:, :k]`  (ties: lower label index first)
:25-28 `def hit_at_1(scores, Y): top = rank_topk(scores, 1)[:, 0]; return Y[np.arange(len(Y)), top].astype(float)`  (hit if top-1 is any gold label)
:36-40 `def rr_at_k(scores, Y, k=3): hits = np.take_along_axis(Y, rank_topk(scores, k), axis=1); first = hits.argmax(1) + 1; return np.where(hits.any(1), 1.0 / first, 0.0)`  (k = 3; 0 if no gold in top 3; multi-label: first gold counts)
z-score and fusion (fusion.py):
:33-36 `def zrow(F): m = np.nanmean(F, axis=1, keepdims=True); s = np.nanstd(F, axis=1, keepdims=True) + 1e-9; return np.nan_to_num((F - m) / s, nan=0.0)`  (per sentence, over the labels the model knows; unknown labels -> 0)
:52 `Z = {"svm": zrow(to_full(S.svm_raw[split], S.seen_idx, L))}`
:57 classifiers avg `zrow(np.mean([to_full(S.cls_raw[tag, s][split], ...) for s in SEEDS], axis=0))`  (seed averaging = mean probability, then z)
:58 matcher `zrow(np.mean([S.matcher_raw[s][split] for s in SEEDS], axis=0)) if mode == "avg" else zrow(S.matcher_raw[seed][split])`
:20 `ORDER = ("matcher", "svm", "roberta", "secbert")`; :62-63 `def fuse(Z, w): return sum(wi * Z[n] for wi, n in zip(w, ORDER))`
bootstrap / McNemar (stats.py):
:9-10 `BOOT_N = 10_000`, `BOOT_SEED = 20261114`
:24-30 `d = a - b; rng = np.random.default_rng(seed); bs = d[rng.integers(0, len(d), (n_boot, len(d)))].mean(1)`; CI = quantiles 0.025 / 0.975 (paired, unit = sentence); p_boot = 2*min(P(bs<=0), P(bs>=0))
:33-38 `b_ = (a & ~b).sum(); c_ = (~a & b).sum(); p = binomtest(b_, b_ + c_, 0.5).pvalue`  (exact two-sided McNemar)
SOURCE: _showcase\src\ttpmap\metrics.py:20-40; fusion.py:20-63; stats.py:9-38
EVIDENCE: the raw code lines are quoted in FACTS
CAVEAT: Exp_2.1 nb used np.argsort default (not stable) and 1,000 resamples default_rng(0); P@1 values are identical (registry), CIs differ slightly.

=== X2 | VERIFIED ===
FACTS: shap 0.54.1; `shap.Explainer(f, shap.maskers.Independent(np.zeros((1, n))), algorithm="permutation", seed=42)` (permutation explainer); max_evals = 40 * (2n + 1) = 40 permutations; background = all-zeros mask vector = every word replaced by <mask>; f = logit of the top-1 label of roberta_pw_s42 (Exp_1_4_run_tram_2_epoc_30\roberta_pw_s42, fine-tuned from roberta-base); unit = whitespace-delimited word, surrounding whitespace kept; max_length 128; output Exp_3_0_shap\shap_v2_roberta_pw_s42.jsonl
SOURCE: Exp_3_0b_shap_all_725.ipynb CELL 0 L2, CELL 1, CELL 2 L8-13, L87-102
EVIDENCE: method block in every record: {'unit': 'whitespace-delimited word', 'masking': 'word replaced by <mask>, surrounding whitespace kept', 'algorithm': 'permutation', 'n_perm': 40, 'shap_seed': 42, 'output': 'logit of the top-1 predicted label', 'max_length': 128}
CAVEAT: explains RoBERTa s42 only; SHAP of the fused score = G15 / Z1.
