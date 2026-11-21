# Model card: RoBERTa-base classifier

| | |
|---|---|
| Role | neural classifier, fusion component, and the model explained with SHAP (seed 42) |
| Architecture | `roberta-base` with a multi-label classification head over the train labels |
| Training data | TRAM train, 3,468 sentences, 180 labels |
| Settings | max length 128, batch 16, lr 2e-5 (encoder) / 1e-3 (head), up to 30 epochs, patience 5, BCE with positive weight capped at 20 (`Exp_1_4` CELL 8) |
| Selection | epoch and threshold on dev micro-F1 |
| Seeds | 42, 43, 44 |
| Test results | micro-F1 0.705 +/- 0.011; macro-F1 0.563 / 0.519; P@1 single-seed mean 0.752 +/- 0.007, 3-seed average 0.756 [0.724, 0.786]; ECE 0.172 +/- 0.007 |
| By label frequency | P@1 0.000 unseen, 0.294 for 1-4, 0.859 for 50+ |
| Efficiency | 124,784,052 parameters; 46.7 ms per sentence (CPU, median, one seed) |
| Artefacts | probabilities and weights saved for all seeds |
| Limitations | not better than the SVM with statistical support (+0.014 [-0.014, 0.041]); over-confident; dev threshold at the edge of the original grid |
| Not for | operational use without analyst review; techniques absent from or rare in the training data |
