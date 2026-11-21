# Thesis Draft v2.5: changes (17 Nov 2026)

Built from `Thesis_Draft_v2.4.docx` by a guarded build script (every edit asserts its anchor). Fields (TOC, List of Figures, List of Tables, caption numbers) were updated in Microsoft Word. v2.4 is unchanged.

Files: `Thesis_Draft_v2.5.docx` and `Thesis_Draft_v2.5.pdf` (69 pages).

## Checks run on v2.5

| Check | Result |
|---|---|
| OOXML schema validation (docx skill `validate.py`) | PASSED |
| Placeholders `[...]` and yellow highlights | 0 and 0 (v2.4 had 13) |
| Number audit (`scripts/audit_numbers.py` against `thesis_numbers.json`) | 11 unregistered tokens: the 10 of v2.4 (numbers quoted from cited papers, checked in `docs/RELATED_WORK_VERIFIED.md`) plus the Student ID |
| Interval check (`scripts/check_intervals.py`) | 20 intervals: 18 OK, 2 seed lists |
| Length | body text 11,418 words without tables (limit 8,000-12,000); Chapters 1-6 on pages 1-44 (limit 40-45) |
| Field errors in the PDF ("Error!") | none |
| Metadata | creator and last-modified-by `KDU`; no personal names or paths in any XML part or in the PDF metadata |

## Changes

1. All tracked changes of v2.4 were accepted (47 deletions, 46 insertions), so the copy is clean.
2. Identity, from the author's plan of 17 Nov: name Hashim Osama Bin (cover, approval page, declaration, abstract), Student ID 2317191, advisor Dr. Grace C. Kennedy (approval page and acknowledgement; Dr. Khadak Singh Bhandari moved to the committee), date November 19, 2026. The template's red colour was removed from the five names. The cover spacing was tightened so that the date stays on page 1.
3. Section 2.3: new paragraph "Recent work based on large language models" with 8 references verified on 15 Nov (TechniqueRAG, a WWW '25 study, You and Park, SynthCTI, Ryan et al., Haque et al., CTI-HAL, SMAH-CTI). Objective 1 in Section 6.2 no longer says that the review must be extended.
4. Section 3.4.4: the reason for keeping (3, 1, 1, 1) is stated: it won the first complete development search, and switching to the winner of the finer grid, whose test scores had been printed, would be a test-informed choice. The two settings differ by 0.004 in test P@1 (`B14.test3111` 0.800, `B14.test4111` 0.804).
5. Section 3.7: the dataset-text placeholder became a statement of the automated check (QA gate "no dataset text beyond short excerpts": PASS). The AI-use placeholder became a declaration of the tools used (Claude for code, number re-checks and wording; qwen2.5:7b for the optional explanations of the prototype).
6. New Section 4.4.7 "Explainer Prototype": replay and live modes, live full fusion with the retrained seed-42 matcher, checks `APP1.verify_ok` 16 of 16, `APP4.tests_passed` 29 (0 failed), grounding `APP3.*` 23 of 100, 31 and 42 of the 77 failures. It states that no usability study was done. Section 6.1 has one sentence that points to it.
7. Five new body figures, all from the registry-built figure set: 3.2 data splits and label long tail, 4.2 data model, 5.3 P@1 by support bucket for five systems, 5.4 SHAP examples (replaces the figure placeholder), 5.5 rater cross-tabulation and agreement (adds the registered weighted kappa `D4.lin` 0.133).
8. Citations added for standard methods that were used without a source: TF-IDF [26], McNemar [35], Holm [36], Cohen's kappa [37].
9. Appendix B: the written guideline prepared for the repeated rating study (question, 1-5 scale, rules, materials, consent), marked as not used at submission.
10. Appendix C: the code is "available from the author on request" (no public repository exists).
11. New Appendix D "Additional Figures" (D.1-D.7: weight sensitivity, ablation, fixed and broken sentences, P@1 by tactic, top confusions, reliability diagram, deletion and insertion curves).
12. New Appendix E "Guide to the Formulas": what each of the nine formulas computes, where it comes from and why this form is used.
13. References [26]-[37] added (12 entries).
14. List of Figures style: Latin words no longer break in the middle of a word (the template's Normal style allows that for Korean text).

## What only the author can confirm before submission

1. Read and sign the declaration. Check that the AI-use statement in Section 3.7 matches the university's required wording and is true.
2. Title: the registered title of proposal v0.1.4 is not on this computer, so v2.5 keeps the current title. If the registered title differs, change it on the cover, the approval page and the abstract.
3. Raters of the first study: v2.5 keeps the v2.4 wording ("project colleagues who took part voluntarily"). Confirm this.
4. The claude.ai build of 17 Nov (formula explanations in the body, Objective 6, dedication page) is not merged into v2.5. v2.5 has the formula guide in Appendix E instead, which keeps the body inside the length limit.
5. References [26]-[37] are appended at the end of the list, not strictly in order of first citation. Ask the supervisor whether strict IEEE order is required.
6. After any text edit in Word: right-click the Table of Contents, choose Update Field, then Update entire table. Do the same for the List of Figures and the List of Tables.
7. After saving in Word, set File > Info > Properties > "Last Modified By" if it shows a name that should not appear.
