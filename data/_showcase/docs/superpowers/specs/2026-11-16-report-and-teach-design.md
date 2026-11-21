# Report mode and Teach mode for the explainer (short design, 16 Nov 2026)

**Why:** the teacher may bring new text ("find the techniques in this") or new labelled data ("train it on this"). Today the app only takes one sentence of up to 40 words, and it cannot learn.

**Chosen approach (approved):** both features below; the SVM is the only part retrained live.
- Rejected: retraining RoBERTa, SecBERT or the matcher live. That needs a GPU and hours; in the viva it is explained instead.

## Report mode ("Report: many sentences")
- **Input:** pasted text, or an uploaded `.txt`, `.md` or `.csv` file. A CSV uses the column `text`, `text1` or `sentence`, else its first column.
- **Splitting:**
  - Text is split at `.`, `!` and `?` followed by a space, and at line breaks.
  - Pieces under 3 words are dropped.
  - At most 300 sentences.
- **Scoring:** every sentence is scored in one batch with the full fusion (3,1,1,1) seed 42. Without the retrained matcher, the classifier-only fusion is used.
  - The calibration is the same as in live mode.
  - No SHAP in this pass (about 0.15 s per sentence).
- **Table:** number, sentence, top-1 technique and name, confidence tier, conformal set size.
- **Download:** a CSV of the results.
- **Explain one sentence:** a select box plus a button runs SHAP on that sentence (≤ 40 words) and shows the normal panels.

## Teach mode ("Teach: add labelled sentences")
- **Input:**
  - Text lines in the form `T1486: sentence`. Several IDs are allowed: `T1059, T1105: sentence`.
  - Or a CSV with a text column and a `labels` column. The labels are a list literal or IDs separated by commas or semicolons.
  - IDs must be in the app's label space (733 IDs, ATT&CK v12.1). Unknown IDs are rejected and listed.
- **Retrain:** the TF-IDF + LinearSVC is refit with the same settings as `load_replay`, on train + the new sentences. The seen-label set may grow.
  - The dev-only calibration is refitted for both live systems.
  - The other components stay frozen.
  - Everything lives in the browser session only: nothing is written to disk, and replay and thesis numbers never change.
- **Before vs after:** a probe sentence shows the SVM top-3 before and after (instant, no torch).
- **Banner:** Live and Report modes then use the new SVM, with the banner "Using the SVM retrained with N added sentences: not evaluated on test, not a thesis number". An **Undo** button returns to the thesis model.

## Anti-goals
- A retrained model's score is shown as a thesis result.
- Replay changes.
- A malformed line crashes the app (it must report the line instead).
