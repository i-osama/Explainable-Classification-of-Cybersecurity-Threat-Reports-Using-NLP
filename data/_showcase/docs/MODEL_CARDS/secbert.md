# Model card: SecBERT classifier

| | |
|---|---|
| Role | domain-specific neural classifier and fusion component |
| Architecture | `jackaduma/SecBERT` with a multi-label classification head |
| Training data | TRAM train, 3,468 sentences, 180 labels |
| Settings | as RoBERTa |
| Selection | as RoBERTa |
| Seeds | 42, 43, 44 |
| Test results | micro-F1 0.703 +/- 0.001; macro-F1 0.543 / 0.500; P@1 single-seed mean 0.743 +/- 0.004, 3-seed average 0.754 [0.723, 0.786]; ECE 0.138 +/- 0.012 |
| By label frequency | P@1 0.000 unseen, 0.176 for 1-4, 0.867 for 50+ |
| Efficiency | 83,589,300 parameters; 22.7 ms per sentence (CPU, median, one seed) |
| Artefacts | probabilities and weights saved for all seeds |
| Limitations | no measurable advantage over RoBERTa (+0.001 [-0.023, 0.025]) |
| Not for | operational use without analyst review; techniques absent from or rare in the training data |
