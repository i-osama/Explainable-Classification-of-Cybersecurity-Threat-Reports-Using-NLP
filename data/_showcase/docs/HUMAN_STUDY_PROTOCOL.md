# HUMAN STUDY PROTOCOL (study 2: plausibility of word-level explanations)

Status: **protocol and materials only. No ratings have been collected under this protocol.** Fixed on 2026-11-14, before any sheet is sent.
The first study (two complete raters, three-point scale, no controls) ended at chance agreement and is reported as a negative result
(`_evidence_pack/07_human.md`). This protocol addresses its four weaknesses: too few raters, no stated rater background, a coarse scale
without written anchors, and no control items that would show whether raters can tell a real explanation from a random one.

## 1 Question

Do the three words that the explanation method marks as most influential read, to a security analyst, as evidence for the predicted technique,
more so than three randomly chosen words of the same sentence?

## 2 Raters

- At least **3** raters; each completes the whole sheet alone and does not see other raters' sheets or this protocol's item key.
- Required background: working or studying in cyber security, able to read ATT&CK technique descriptions. Recorded per rater in
  `human_study/returned/raters.csv` (template `raters_TEMPLATE.csv`): role, years in security, threat-intelligence experience (yes/no),
  self-rated ATT&CK familiarity (1-5), minutes spent. **Roles only, no names.**
- The thesis author may act as a rater only if the supervisor allows it; if so, the analysis is reported with and without that rater.

## 3 Items

| | count | content |
|---|---|---|
| REAL | 60 | test sentence with the 3 words of highest positive SHAP value marked `[[word]]` |
| CONTROL | 20 | test sentence with 3 words marked at random among the words that are not in its top 5 by SHAP value |

- Sentences: the eligible rows at positions 100 and later of `numpy.random.RandomState(42).permutation(725)`, in that order; none was used in study 1.
  Eligible = at least 8 words, at least 3 words with positive SHAP value, at most 128 model tokens. No hand selection.
- Explained model: the RoBERTa classifier `roberta_pw_s42` (the model for which SHAP values exist for every test sentence). The sheet states this.
  If full-fusion SHAP values exist by the time sheets are generated, a separate sheet is generated for them and analysed separately.
- Shown per item: predicted technique id and name, first sentence of its ATT&CK description, the sentence with marked words.
  Not shown: gold labels, whether the prediction is correct, SHAP values, whether the item is REAL or CONTROL.
- Order: independently shuffled per rater (seed = base seed + rater number). Item ids are opaque.
- Generator: `scripts/make_rating_sheet.py --raters N` writes `human_study/sheets/rating_sheet_R<k>.csv` and `human_study/key_PRIVATE.csv`.
  The sheets carry dataset sentences and the key carries the conditions; both stay out of the repository and the zip.

## 4 Scale (ordinal, 1 to 5)

Question printed at the top of the sheet: *"If you had to justify the predicted technique to a colleague using only the marked words, how well would they serve as evidence?"*

| rating | anchor |
|---|---|
| 5 | All three marked words are direct evidence for the technique (they name the action, tool or object that defines it). |
| 4 | Two marked words are direct evidence; the third is neutral. |
| 3 | One marked word is direct evidence, or the words are only loosely related to the technique. |
| 2 | The marked words are generic security vocabulary that would fit many techniques. |
| 1 | The marked words are filler (articles, prepositions, names) or point to a different technique. |

Raters rate the words as evidence for the *predicted* technique, even when they believe the prediction is wrong; they may say so in the note column.
Two worked examples (one rated 5, one rated 1), built from **training** sentences so that no test item is revealed, are given with the sheet.

## 5 Returned data and validation

- One CSV per rater in `human_study/returned/`: columns `item_id`, `rating_1_to_5`, `note`. Schema check: every item id of the key present exactly once;
  rating an integer 1-5. Missing or invalid cells are **reported, never imputed or dropped silently**.
- A rater with more than 10% missing cells is reported separately and excluded from agreement statistics only (stated in the report).

## 6 Analysis (fixed in advance; nothing else is reported as a finding)

Primary outcome: **REAL vs CONTROL.** For each item, the mean rating over raters. Statistic: mean(REAL) minus mean(CONTROL) with a percentile
bootstrap 95% interval over items (10,000 resamples, seed 20261114), plus the same difference per rater.

- *Explanations are rated above random words* only if the interval excludes 0 **and** the difference is at least 1.0 scale point.
- Otherwise the study reports that raters did not separate real explanations from random words.

Secondary outcome: **agreement** on the REAL items. Krippendorff alpha (ordinal; nominal for comparison) with bootstrap interval, Fleiss kappa,
pairwise Cohen kappa (unweighted and linearly weighted), exact agreement, per-rater mean and each rater's bias (mean minus grand mean).

- alpha (ordinal) at or above 0.80: agreement adequate; between 0.667 and 0.80: tentative; below 0.667: **ratings are not pooled into a plausibility
  score**, and only the primary outcome and the per-rater results are reported.

Descriptive only: mean rating of REAL items split by whether the prediction was correct (the raters do not see this).

Not done: no rater removal after seeing results; no re-anchoring of the scale; no additional items; no significance hunting over subgroups.

## 7 Power reasoning (simulation, assumptions stated, not data)

`python scripts/make_rating_sheet.py --power` writes `results/human_power_simulation.csv`. Assumptions: item quality on the 1-5 scale normally
distributed with standard deviation 0.9 around a condition mean; each rating = quality + rater bias (sd 0.4) + rater noise, rounded and clipped;
3, 4 or 5 raters; rater noise sd 0.6, 1.0 or 1.4; three true gaps between REAL and CONTROL.

What the simulation shows for the chosen design (60 REAL + 20 CONTROL):

- The primary rule (interval excludes 0 and difference at least 1.0) is met in at least four of five simulated studies when the true gap is large,
  for every number of raters and every noise level, and almost never when the true gap is small or absent. The design can therefore detect a clear
  difference and does not manufacture one.
- alpha at or above 0.667 is reached in about half of the simulated studies only when rater noise is low, and practically never at medium or high
  noise, whatever the number of raters. Adding raters does not raise alpha; clearer anchors and rater training do.
  This is why agreement is the secondary outcome and why the anchors and the two worked examples are part of the materials.

## 8 Ethics

Raters are adult volunteers; they are told the purpose, that participation is voluntary, that only their role and ratings are stored, and that they can
withdraw their sheet. No personal data beyond the role table is collected. Whether institutional ethics approval is required is a question for the supervisor.

## 9 Threats specific to this study

- The explained model is one component (RoBERTa, one seed), not the fused system; its top-1 label differs from the fusion's on a measurable share of test sentences.
- Plausibility to a reader is not faithfulness to the model; faithfulness is measured separately (`results/faithfulness_summary.csv`).
- Technique names and descriptions shown to raters come from the ATT&CK description file of the project, not from a version-pinned ATT&CK release.
- Twenty control items give a wide interval for the control mean; the primary rule compensates by requiring a full scale point.
