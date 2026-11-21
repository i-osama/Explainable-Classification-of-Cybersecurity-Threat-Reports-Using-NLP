# Rater kit: send and collect (author checklist)

Protocol: `docs/HUMAN_STUDY_PROTOCOL.md` (fixed 2026-11-14, before any sheet was sent). Raters: R1, R2, R3 (codes only; keep the name-to-code list off this PC's project folder).

## Before sending
- [ ] Ask the supervisor whether ethics approval is needed (protocol section 8).
- [ ] Open one zip and read `worked_examples.md`. The two ratings (5 and 1) were drafted from the anchors; change them if you disagree, then edit
      `human_study/materials_local/worked_examples_DRAFT-FOR-AUTHOR.md` and rerun `python scripts/make_rater_kit.py`.
      Example 2 uses T1064 Scripting, which later ATT&CK releases deprecate; keep it (the label comes from the dataset) or regenerate it with `scripts/make_worked_examples.py`.
- [ ] Each rater must work in cyber security and be able to read ATT&CK technique descriptions (protocol section 2).

## Send (one e-mail per rater, no other rater in copy)
Attach `rater_R<k>.zip`. Suggested text: "Please read READ_FIRST_instructions.md and worked_examples.md, then rate the 80 rows of rating_sheet_R<k>.csv
(about 45-60 minutes). Fill in your row of raters.csv. Send both files back without renaming them. Participation is voluntary; only your role and ratings are stored."

## When a sheet comes back
- [ ] Save it unchanged as `human_study/returned/rating_sheet_R<k>.csv` (same name as sent).
- [ ] Copy the rater's row into `human_study/returned/raters.csv` (start from `raters_TEMPLATE.csv`).
- [ ] Run `python scripts/score_human_study.py`. It lists every missing or invalid cell (never imputed) and needs at least 3 raters.
- [ ] Then run `finish_q1.ps1` so the result enters `thesis_numbers.json` (ids `T8.*`).

Returned-sheet schema read by the scorer: `item_id`, `rating_1_to_5` (whole number 1-5), `note`; all other columns are ignored. A rater with more than
10% empty ratings is excluded from the agreement statistics only. Kill-switch Tue 18 Nov 2026 18:00: if fewer than 3 sheets are back, the study is reported as not completed.
