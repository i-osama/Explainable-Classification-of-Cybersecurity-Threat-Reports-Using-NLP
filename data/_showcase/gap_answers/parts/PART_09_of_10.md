THESIS GAP ANSWERS - PART 9/10 - 2026-11-21
=== APPENDIX G20: full text of _showcase\docs\RATER_INSTRUCTIONS.md (= READ_FIRST_instructions.md) ===
# Instructions for raters (one page)

Thank you for helping. This takes about 45 to 60 minutes. You can stop and continue later.

## What you see

Each row of your sheet shows:
- a sentence from a cyber-threat report;
- a MITRE ATT&CK technique that a computer model predicted for this sentence, with its name and the first sentence of its official description;
- three words in the sentence marked like this: [[word]].

## Your task

For each row, answer one question:

> If you had to justify the predicted technique to a colleague using only the marked words, how well would they serve as evidence?

Write a whole number from 1 to 5 in the column `rating_1_to_5`.

| rating | meaning |
|---|---|
| 5 | All three marked words are direct evidence for the technique. They name the action, tool or object that defines it. |
| 4 | Two marked words are direct evidence. The third is neutral. |
| 3 | One marked word is direct evidence, or the words are only loosely related to the technique. |
| 2 | The marked words are general security words that would fit many techniques. |
| 1 | The marked words are filler (such as "a", "the", "to", names) or point to a different technique. |

## Rules

- Rate the marked words as evidence for the **predicted** technique, even if you think the prediction is wrong. If you think it is wrong, write that in the `note` column.
- Judge only the marked words. Other words in the sentence do not count.
- Some rows mark words chosen at random. This is on purpose. Rate them the same way.
- Work alone. Do not discuss rows with other raters until everyone has sent their sheet.
- Do not change the order of rows, the `item_id` column or any column except `rating_1_to_5` and `note`.
- If a row is unclear, still give your best rating and explain in `note`. Leave a rating empty only if you cannot judge at all.

## Two worked examples

Your sheet comes with a page of two worked examples (one rated 5, one rated 1). Read it before you start.

## When you are done

Save the file as CSV with the same name and send it back. Also fill in one row of the short background form (`raters.csv`): your role, years in security,
whether you work with threat intelligence, how familiar you are with ATT&CK (1 to 5), and how many minutes the rating took.
We store only your role and your answers. We do not store your name. You may withdraw your sheet at any time.
