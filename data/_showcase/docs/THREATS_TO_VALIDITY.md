# Threats to validity

## Internal (is the measured effect real?)
| threat | evidence | mitigation / status |
|---|---|---|
| tuning on test | selection code takes dev only and raises on test ids; the leakage test passes | controlled. Residual: test scores of the ten best wide-grid settings were printed in the original notebook before weights were fixed; the kept setting has the lower test score (0.800 vs 0.804) |
| the test set was looked at repeatedly during development | notebooks print test metrics at many steps | cannot be undone; new analyses are pre-registered and the family of tests is Holm-corrected |
| train-test overlap | exact 1 / 0; near-duplicate +1 / +3 | removing the overlap changes P@1 by at most 0.0007 |
| threshold grid too narrow | RoBERTa thresholds 0.85 / 0.85 / 0.85 at the grid edge | extended grid changes test micro-F1 by -0.0006 on average |
| implementation differences between systems | one metric implementation, unit-tested; stored metrics reproduce | controlled |
| matcher weights lost | score files only | fusion cannot be re-run on new text or explained until notebook 04 is run |

## Construct (do the measures mean what is claimed?)
| threat | status |
|---|---|
| P@1 and MRR@3 against noisy single annotations treat a plausible alternative technique as an error | open; the confusion table shows semantically close pairs |
| F1 as computed in the notebooks ignores the 10 unseen test labels | three variants reported; micro-F1 drops by 0.0043 when they count |
| "explainable" is measured as faithfulness to one component | stated; fusion-level explanation is open work |
| plausibility judged by two raters on a three-point scale | agreement at chance (alpha -0.057); a five-point protocol with controls is written, not run |
| per-sample vs micro definitions of recall differ between this work and the baseline paper | R@1 is not compared; notebook 09 implements the paper's definitions |

## External (does it generalise?)
| threat | status |
|---|---|
| one dataset, short sentences, 180 of several hundred techniques | open; objective (b) on the sibling datasets is scripted (notebook 08), not run |
| one ATT&CK version, not pinned inside the data | open |
| comparison with the published baseline is not on verified-identical data or training mode | open; reported as side by side |
| latency measured on one desktop CPU | descriptive only (`results/hardware.json`) |

## Conclusion (are the statistics sound?)
| threat | status |
|---|---|
| three seeds give a weak estimate of seed variance | mean and sd reported; seeds 45-46 scripted, not run |
| the bootstrap resamples sentences, not seeds or training data | stated with every interval |
| multiplicity | Holm over a family of 8 fixed in advance; only fusion vs classifiers-only and the matcher and RoBERTa ablations stay supported |
| borderline result reported as a gain | fusion vs matcher ensemble: +0.026 [0.001, 0.051], Holm p 0.190: reported as not robust |
| small buckets | unseen (n = 10) and 1-4 (n = 34) have wide intervals; shown with intervals, not interpreted beyond direction |
