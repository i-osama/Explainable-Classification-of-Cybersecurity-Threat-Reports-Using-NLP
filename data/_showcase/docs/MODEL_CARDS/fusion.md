# Model card: Late fusion (3,1,1,1)

| | |
|---|---|
| Role | the reported system |
| Architecture | weighted sum of per-sentence z-scores: matcher 3, SVM 1, RoBERTa 1, SecBERT 1 |
| Training data | TRAM train, 3,468 sentences, 180 labels |
| Settings | weights from the dev winner of the coarse grid: (3,1,1,1) = dev winner of the 255-setting grid; the 1,711-setting grid selects (4,1,1,1) |
| Selection | dev MRR@3, tie-break dev P@1; guarded against test ids in code |
| Seeds | three definitions: seed-averaged, seed-paired, matcher seed varied |
| Test results | P@1 0.803 [0.774, 0.832] (seed-averaged), 0.796 +/- 0.006 (seed-paired), 0.800 +/- 0.001 (notebook); MRR@3 0.856; vs classifiers-only +0.029 (Holm p 0.000); vs matcher ensemble +0.026 (Holm p 0.190) |
| By label frequency | P@1 0.000 unseen, 0.294 for 1-4, 0.897 for 50+: worse than the matcher on rare labels, better on frequent ones |
| Efficiency | sum of the components; about ten transformer passes per sentence in the seed-averaged form |
| Artefacts | recomputed from saved scores by `scripts/verify_claims.py` |
| Limitations | gain over the matcher ensemble is not robust; no gain on rare or unseen techniques; explanations exist for one component only |
| Not for | operational use without analyst review; techniques absent from or rare in the training data |
