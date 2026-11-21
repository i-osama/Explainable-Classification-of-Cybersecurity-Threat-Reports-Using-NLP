# Usability study of the explainer app (artefact evaluation, design science)

Goal: show that the artefact can be used by its intended users, as the evaluation step of design science research (Hevner et al. 2004; Peffers et al. 2007). This is a small formative study, not a statistical test.

## Who and how many
- 3 to 5 participants with some security or IT background (classmates, lab members). Not the author.
- About 20 minutes each, one at a time, on the thesis PC.
- No names in any file: use P1, P2, ... Ask the supervisor whether the university needs ethics approval for a short anonymous usability test, before you start.

## Consent (read aloud, tick in the sheet)
"This is a test of a software tool, not of you. It takes about 20 minutes. I will note whether each task worked and how long it took, and you will fill in a 10-question form. Nothing that identifies you is recorded. You can stop at any time."

## Setup
1. Double-click `run_app.bat`; wait for the browser page (about 10 s).
2. Keep "Synthetic demo data" off, mode "Replay", alpha 0.10, LLM toggle off.

## Tasks (give one at a time; note success yes/no, seconds, comments)
| # | task given to the participant | success when |
|---|---|---|
| T1 | Open sentence 1. Which technique does the tool rank first, and does it match the gold label? | names T1082 and says it matches |
| T2 | Find a sentence where the tool is wrong (tick the filter in the sidebar). Is the correct technique inside the conformal set? | uses the filter; reads the set |
| T3 | Open sentence 84. What does the warning say about the predicted technique? | says it is no longer active in ATT&CK |
| T4 | Open sentence 2. Do the highlighted words explain the tool's first-ranked technique? | notices the caution message (they do not) |
| T5 | Open "What this tool does not show" at the bottom. Name one limit. | names any listed limit |

## SUS form (Brooke 1996): answer 1 = strongly disagree ... 5 = strongly agree
1. I think that I would like to use this system frequently.
2. I found the system unnecessarily complex.
3. I thought the system was easy to use.
4. I think that I would need the support of a technical person to be able to use this system.
5. I found the various functions in this system were well integrated.
6. I thought there was too much inconsistency in this system.
7. I would imagine that most people would learn to use this system very quickly.
8. I found the system very cumbersome to use.
9. I felt very confident using the system.
10. I needed to learn a lot of things before I could get going with this system.

Two open questions after the form: "What was most useful?" and "What was confusing?"

## Scoring and reporting
1. Copy `sus_responses_TEMPLATE.csv` to `sus_responses.csv` and type the answers (keep the template).
2. Run `python usability/score_sus.py usability/sus_responses.csv`.
3. Report per participant: task success (5 tasks), seconds per task, SUS score; then the mean SUS and the range. With 3-5 people this is descriptive: write "mean SUS X (range A-B, n = N)", compare it with published SUS benchmarks (Bangor et al. 2008) in words, and do not claim significance.
4. Put the open answers in a short table (most useful / confusing) and say what you would change.

References (verified, `../_showcase/docs/RELATED_WORK_VERIFIED.md` section G): Hevner et al. 2004; Peffers et al. 2007; Brooke 1996 (PARTLY: author not checked); Bangor et al. 2008.
