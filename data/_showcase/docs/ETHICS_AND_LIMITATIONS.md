# Ethics and limitations

## Dual use
The system reads defensive threat reports and names the attack techniques they describe. It produces no exploit, payload or procedure; ATT&CK itself is public.
The realistic misuse is indirect: automated labelling could help an adversary index public reporting about their own tooling. That information is already public and the risk is judged low.

## Risks of use
- **Over-trust.** P@1 is 0.803: about one top prediction in five is wrong, and on rare techniques most are (P@1 0.294 for labels with 1-4 training sentences, 0.000 for unseen ones). Output is a suggestion for an analyst, never a decision.
- **Over-confidence.** The classifiers' top-1 probability averages 0.913 for RoBERTa while its accuracy is lower (ECE 0.172 +/- 0.007); probabilities must not be shown as certainty.
- **Explanations can mislead.** They are faithful to one RoBERTa model, not to the fused system (different top-1 label on 108 of 725 (14.9%) sentences), and human agreement on their plausibility is at chance in the only study run (alpha -0.057).
- **Label noise and coverage.** TRAM covers 180 of the ATT&CK techniques in training; a sentence about any other technique cannot be labelled correctly by three of the four components.

## Data and privacy
The data are sentences from published threat reports. No personal data were collected for training. Human raters are recorded by role only; rating sheets stay out of the repository.
The dataset licence is not documented in the project, so no sentence text is redistributed here.

## Limitations of the study
One dataset and one split; three seeds; a baseline taken from its paper; an inconclusive human study; no robustness test under paraphrase or adversarial edits;
efficiency measured on one desktop CPU. `docs/THREATS_TO_VALIDITY.md` treats these in detail.

## AI assistance
See the section "AI assistance" in `README.md`.
