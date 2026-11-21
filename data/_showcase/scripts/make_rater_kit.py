"""Prompt E5: human_study/TO_SEND/ = one zip per rater (rater codes only, no names) + RETURN_CHECKLIST.md for the author.
Each zip: rating_sheet_R<k>.csv (own shuffled order), READ_FIRST_instructions.md (docs/RATER_INSTRUCTIONS.md), worked_examples.md (two TRAINING
sentences, from human_study/materials_local/worked_examples_DRAFT-FOR-AUTHOR.md without the author notes), raters.csv (one background row).
Checks before writing: every sheet holds the 80 key items once, 60 REAL + 20 CONTROL in the key, orders differ between raters, the sheet columns are
the ones scripts/score_human_study.py reads. The zips carry dataset sentences: local only (*.zip is git-ignored; never in the claude.ai zip).
Usage: python scripts/make_rater_kit.py"""
import re, sys, zipfile
from pathlib import Path
import pandas as pd

SHOW = Path(__file__).resolve().parents[1]; H = SHOW / "human_study"; OUT = H / "TO_SEND"
key = pd.read_csv(H / "key_PRIVATE.csv"); sheets = sorted((H / "sheets").glob("rating_sheet_R*.csv"))
assert key.condition.value_counts().to_dict() == {"real": 60, "control": 20} and key.item_id.is_unique
orders = []
for s in sheets:
    df = pd.read_csv(s, encoding="utf-8-sig")
    assert {"item_id", "rating_1_to_5", "note"} <= set(df.columns), s.name
    assert len(df) == 80 and set(df.item_id) == set(key.item_id) and df.item_id.is_unique, s.name
    assert df.rating_1_to_5.isna().all(), f"{s.name}: ratings already filled"
    assert not {"condition", "top1_correct", "gold", "shap"} & {c.lower() for c in df.columns}, f"{s.name}: sheet reveals the key"
    orders.append(tuple(df.item_id))
assert len(sheets) >= 3 and len(set(orders)) == len(orders), "need at least 3 sheets in different orders"
we = (H / "materials_local" / "worked_examples_DRAFT-FOR-AUTHOR.md").read_text(encoding="utf-8")
body = we.split("## Example 1", 1)[1].split("Author check:", 1)[0]
we_out = ("# Two worked examples\n\nBoth sentences come from the training part of the dataset, so they are not on your sheet. Marked words look like [[this]].\n\n## Example 1"
          + body.replace("Draft rating:", "Rating:").replace("Draft reason:", "Why:").replace(" (marked words from the explanation)", "").replace(" (marked words chosen at random)", "")).rstrip() + "\n"
assert "Draft" not in we_out and "Author" not in we_out
instr = (SHOW / "docs" / "RATER_INSTRUCTIONS.md").read_text(encoding="utf-8")
head = "rater_code,role,years_in_security,threat_intel_experience_yes_no,attack_framework_familiarity_1_to_5,minutes_spent\n"
OUT.mkdir(parents=True, exist_ok=True)
for s in sheets:
    rc = re.search(r"(R\d+)", s.stem).group(1); z = OUT / f"rater_{rc}.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(s, s.name); zf.writestr("READ_FIRST_instructions.md", instr); zf.writestr("worked_examples.md", we_out); zf.writestr("raters.csv", head + f"{rc},,,,,\n")
    print(f"{z.relative_to(SHOW)}: {z.stat().st_size / 1e3:.0f} KB")
codes = [re.search(r"(R\d+)", s.stem).group(1) for s in sheets]
(OUT / "RETURN_CHECKLIST.md").write_text(f"""# Rater kit: send and collect (author checklist)

Protocol: `docs/HUMAN_STUDY_PROTOCOL.md` (fixed 2026-11-14, before any sheet was sent). Raters: {', '.join(codes)} (codes only; keep the name-to-code list off this PC's project folder).

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
""", encoding="utf-8")
print("TO_SEND/RETURN_CHECKLIST.md written")
