# Model card: bge bi-encoder matcher

| | |
|---|---|
| Role | retrieval component: ranks all 733 technique descriptions, so it can output techniques unseen in training |
| Architecture | `BAAI/bge-base-en-v1.5`, shared encoder for sentences and descriptions, [CLS] pooling, cosine |
| Training data | TRAM train, 3,468 sentences, 180 labels |
| Settings | InfoNCE-style loss with 64 random negatives, scale 30, batch 16, lr 2e-5, up to 20 epochs, patience 4 (`Exp_2.1` CELL 3, 7) |
| Selection | epoch on dev MRR@3 |
| Seeds | 42, 43, 44 |
| Test results | zero-shot P@1 0.228; fine-tuned 0.756 +/- 0.015; 3-seed ensemble 0.777 [0.746, 0.807] |
| By label frequency | P@1 0.200 unseen, 0.559 for 1-4, 0.862 for 50+: the best component on rare labels |
| Efficiency | 109,482,240 parameters; 47.6 ms per sentence (CPU, median), timed with the public base checkpoint |
| Artefacts | **score files only; the fine-tuned weights were never saved** (notebook 04 retrains with saving) |
| Limitations | cannot be re-run, explained or timed exactly until retrained |
| Not for | operational use without analyst review; techniques absent from or rare in the training data |
