| system | removed | n_removed | removed_test_ids | n | P@1 | MRR@3 |
|---|---|---|---|---|---|---|
| TF-IDF + SVM | none | 0 | nan | 725 | 0.7421 | 0.8138 |
| TF-IDF + SVM | exact | 1 | 59 | 724 | 0.7417 | 0.8135 |
| TF-IDF + SVM | exact+near | 2 | 59;124 | 723 | 0.7414 | 0.8133 |
| RoBERTa (3-seed avg) | none | 0 | nan | 725 | 0.7559 | 0.8159 |
| RoBERTa (3-seed avg) | exact | 1 | 59 | 724 | 0.7555 | 0.8156 |
| RoBERTa (3-seed avg) | exact+near | 2 | 59;124 | 723 | 0.7552 | 0.8154 |
| SecBERT (3-seed avg) | none | 0 | nan | 725 | 0.7545 | 0.8143 |
| SecBERT (3-seed avg) | exact | 1 | 59 | 724 | 0.7541 | 0.814 |
| SecBERT (3-seed avg) | exact+near | 2 | 59;124 | 723 | 0.7538 | 0.8137 |
| Matcher (3-seed ens.) | none | 0 | nan | 725 | 0.7766 | 0.8366 |
| Matcher (3-seed ens.) | exact | 1 | 59 | 724 | 0.7762 | 0.8363 |
| Matcher (3-seed ens.) | exact+near | 2 | 59;124 | 723 | 0.7759 | 0.8361 |
| Fusion (3,1,1,1) | none | 0 | nan | 725 | 0.8028 | 0.8556 |
| Fusion (3,1,1,1) | exact | 1 | 59 | 724 | 0.8025 | 0.8554 |
| Fusion (3,1,1,1) | exact+near | 2 | 59;124 | 723 | 0.8022 | 0.8552 |
| Classifiers-only ens. | none | 0 | nan | 725 | 0.7738 | 0.8366 |
| Classifiers-only ens. | exact | 1 | 59 | 724 | 0.7735 | 0.8363 |
| Classifiers-only ens. | exact+near | 2 | 59;124 | 723 | 0.7732 | 0.8361 |
