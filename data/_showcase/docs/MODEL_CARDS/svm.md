# Model card: TF-IDF + linear SVM

| | |
|---|---|
| Role | classical baseline and fusion component |
| Architecture | word 1-2 gram TF-IDF (sublinear tf), one-vs-rest LinearSVC |
| Training data | TRAM train, 3,468 sentences, 180 labels |
| Settings | C = 1.0, no class weights, random_state 42 (`Exp_1_4` CELL 6) |
| Selection | global decision threshold -0.45 on dev micro-F1; arg-max fallback |
| Seeds | deterministic |
| Test results | micro-F1 0.696; macro-F1 0.543 (seen test labels) / 0.500 (all test labels); P@1 0.742 [0.710, 0.774] |
| By label frequency | P@1 0.000 unseen, 0.206 for 1-4 training sentences, 0.875 for 50+ |
| Efficiency | 7,774,740 weights; 17.9 ms per sentence (CPU, median) |
| Artefacts | no saved scores; refit is deterministic and reproduces the notebook output |
| Limitations | cannot output a label unseen in training |
| Not for | operational use without analyst review; techniques absent from or rare in the training data |
