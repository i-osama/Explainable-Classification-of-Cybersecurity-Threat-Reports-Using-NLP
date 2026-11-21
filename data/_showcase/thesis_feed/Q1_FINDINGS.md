# Q1 upgrade findings (15 Nov 2026), all pre-registered in `../experiments/prereg/` (14-21) unless marked EXPLORATORY or POST-HOC

## Q2 Robustness and shortcut test (prereg 14), TEST, change in P@1 vs clean input [95% paired CI]
| system | clean P@1 | mask_groups | mask_software | mask_iocs | typo_5pct | lower_nopunct |
|---|---|---|---|---|---|---|
| TF-IDF + SVM | 0.742 | +0.000 [0.000, 0.000] | -0.008 [-0.015, -0.003] | -0.001 [-0.011, 0.007] | -0.008 [-0.018, 0.001] | +0.000 [0.000, 0.000] |
| RoBERTa ens. | 0.756 | +0.003 [0.000, 0.007] | -0.008 [-0.015, -0.003] | -0.010 [-0.018, -0.003] | -0.012 [-0.023, -0.001] | -0.030 [-0.052, -0.010] |
| SecBERT ens. | 0.754 | -0.003 [-0.007, 0.000] | -0.010 [-0.018, -0.003] | -0.010 [-0.019, 0.000] | -0.014 [-0.026, -0.001] | -0.015 [-0.029, -0.001] |
| bge zero-shot | 0.228 | -0.001 [-0.004, 0.000] | +0.001 [-0.003, 0.007] | +0.000 [-0.008, 0.007] | -0.004 [-0.014, 0.006] | +0.012 [-0.004, 0.029] |
| classifiers-only ens. | 0.774 | -0.001 [-0.004, 0.000] | -0.007 [-0.015, 0.001] | -0.010 [-0.019, -0.001] | -0.006 [-0.017, 0.006] | -0.004 [-0.019, 0.011] |

- No measurable dependence on threat-group names: masking them changes the classifiers-only ensemble by -0.001 (Holm p 1.000). Only 33 test sentences name a group (on those: 0.788 vs 0.758 (n = 33)), so only a large dependence could have been detected.
- The ensemble meets the pre-registered robustness rule for all five perturbations (Holm p: groups 1.000, software 0.719, IOCs 0.327, typos 1.000, lower-case 1.000).
- Single models are less robust: RoBERTa loses -0.030 [-0.052, -0.010] when text is lower-cased without punctuation (a cased model).
- On the sentences that contain IOCs the ensemble drops 0.667 vs 0.569 (n = 72): IOC strings carry signal for these sentences.
- Software masking also removes legitimate evidence (tool names such as cmd.exe are often the technique), so it is an upper bound on name reliance. Fusion with the fine-tuned matcher: TODO-COLAB (weights not saved).

## Q3 Learned (stacked) fusion (prereg 15): negative result
Logistic regression over 7 features per (sentence, label), fitted on dev (C = 0.01 by 5-fold dev CV).
Test P@1 0.789 [0.759, 0.819] vs 0.803 for (3,1,1,1): delta -0.014 [-0.026, -0.001], Holm p 0.052. Success rule met: False.
Unseen-label R@5 falls to 0.20 (fusion 0.50). The simple dev-tuned weighted sum is not beaten by a learned combiner on 604 dev sentences.

## Q4 Objective (b), TF-IDF + SVM part (prereg 16)
| training set | rows | labels | test P@1 | 95% CI | MRR@3 | unseen R@5 |
|---|---|---|---|---|---|---|
| (a) TRAM train | 3,468 | 180 | 0.742 | [0.710, 0.774] | 0.814 | 0 |
| (b) siblings only | 10,680 | 464 | 0.549 | [0.513, 0.585] | 0.607 | 0.50 |
| (c) TRAM + siblings | 14,135 | 476 | 0.665 | [0.630, 0.699] | 0.758 | 0.50 |

Siblings removed as duplicates of TRAM dev/test: exact 0, near 317. Adding siblings lowers SVM P@1: (c) minus (a) -0.077 [-0.116, -0.040], Holm p 0.000; (b) minus (a) -0.193 [-0.236, -0.150].
EXPLORATORY (not a pre-registered test, read on test): with the (c) SVM inside the fusion, P@1 is 0.817. This is a hypothesis for a new split or a dev-only confirmation, not a result.
The transformer part of objective (b) is notebook 08 (TODO-COLAB).

## Q5 Minimum detectable effect (power 0.8, n = 725, Holm alpha of each comparison)
| comparison | observed delta P@1 | MDE |
|---|---|---|
| fusion vs classifiers-only (C1) | +0.029 | 0.025 |
| fusion vs matcher ensemble (C2) | +0.026 | 0.044 |
| RoBERTa vs SVM (C3) | +0.014 | 0.048 |
| RoBERTa vs SecBERT (C4) | +0.001 | 0.036 |

A null result here means "no difference larger than about the MDE", never "equal".

## Q6 LLM baseline, open weights (prereg 17), qwen2.5:7b on this PC
| variant | P@1 | 95% CI | MRR@3 | R@5 | parse rate | minus matcher ens. | Holm p | minus fusion | Holm p |
|---|---|---|---|---|---|---|---|---|---|
| closed | 0.257 | [0.225, 0.288] | 0.335 | 0.839 | 1.000 | -0.520 [-0.559, -0.480] | 0.000 | -0.546 [-0.583, -0.508] | 0.000 |
| rr_matcher | 0.597 | [0.563, 0.633] | 0.680 | 0.860 | 1.000 | -0.179 [-0.215, -0.143] | 0.000 | -0.206 [-0.244, -0.166] | 0.000 |
| rr_zero | 0.328 | [0.295, 0.363] | 0.409 | 0.498 | 1.000 | -0.448 [-0.488, -0.408] | 0.000 | -0.474 [-0.514, -0.433] | 0.000 |

No variant beats the matcher ensemble, so the pre-registered hypothesis holds (D26). Letting the LLM re-rank the matcher's top 20 changes P@1 by -0.179 [-0.215, -0.143] against the matcher alone. A 7B local model is a lower bound on LLM performance; an API model (notebook 10) is not run.


## Q11 Conformal prediction sets (prereg 18): calibrated on dev, TEST once, alpha 0.10, score rule
| system | coverage of all gold labels | 95% CI (Wilson) | mean set size (labels) | 95% CI |
|---|---|---|---|---|
| Fusion (3,1,1,1) | 0.894 | [0.869, 0.914] | 2.80 | [2.703, 2.903] |
| Matcher (3-seed ens.) | 0.909 | [0.886, 0.928] | 7.69 | [7.506, 7.869] |
| TF-IDF + SVM | 0.917 | [0.895, 0.935] | 5.00 | [4.801, 5.201] |
| RoBERTa ens. | 0.917 | [0.895, 0.935] | 558.84 | [558.528, 559.167] |
| SecBERT ens. | 0.917 | [0.895, 0.935] | 558.30 | [558.019, 558.579] |

- H1 (0.90 inside the CI of the fusion's coverage): True. H2 (fusion sets smaller than every component, Wilcoxon, Holm over 4): True; fusion minus matcher -4.88 [-5.068, -4.706] labels.
- An analyst gets about 2.80 candidate techniques per sentence for 90% coverage of all gold labels; a fixed top-k list needs 5.00 for the same guarantee.
- The classifier rows are large because the z-scored components put the 553 labels outside a classifier's space at z = 0 (D27). POST-HOC, not pre-registered, with raw scores: RoBERTa 6.15, SecBERT 5.58, SVM 5.35 labels. The fusion's sets stay the smallest.
- The guarantee is marginal, not per label: unseen labels are covered 0.00 by the fusion and 0.70 by the matcher; labels with 1-4 training sentences 0.74 vs 0.85.

## Q12 Abstention for analyst triage (prereg 19): confidence = top-1 minus top-2 score, thresholds on dev
| system | AURC (lower is better) | E-AURC | selective P@1, dev target 0.5 | 95% CI | test coverage |
|---|---|---|---|---|---|
| Fusion (3,1,1,1) | 0.0715 | 0.0505 | 0.964 | [0.942, 0.982] | 0.455 |
| Matcher (3-seed ens.) | 0.0834 | 0.0562 | 0.946 | [0.923, 0.969] | 0.486 |
| TF-IDF + SVM | 0.1045 | 0.0678 | 0.909 | [0.876, 0.940] | 0.457 |
| RoBERTa ens. | 0.0881 | 0.0554 | 0.959 | [0.936, 0.980] | 0.476 |
| SecBERT ens. | 0.1112 | 0.0780 | 0.903 | [0.871, 0.933] | 0.470 |

- Fusion minus component AURC: matcher -0.0119 [-0.024, -0.001] (Holm p 0.040), SVM -0.0330 (Holm p 0.000), RoBERTa -0.0166 (Holm p 0.001), SecBERT -0.0396 (Holm p 0.000). All four meet the pre-registered rule; against the matcher the margin is small.
- Reading for practice: the fusion answers the most confident 0.455 of sentences at P@1 0.964 and passes the rest to an analyst; at coverage 0.914 its P@1 is 0.827.
- This does not overturn C2: on P@1 itself the fusion does not beat the matcher ensemble after Holm.

## Q13 Label-noise candidates (prereg 20, EXPLORATORY)
37 of 143 fusion top-1 errors (0.259) are sentences where the fusion and all four components agree on the same wrong label. The consensus label is a sibling sub-technique in 1, shares a tactic in 19 and shares no tactic in 17 cases.
These are candidates for a human check (`human_study/materials_local/label_noise_review.xlsx`, author only), not label errors: a bias shared by all models produces the same pattern. Report no label-noise rate before the check.

## Q14 ATT&CK version drift (prereg 21, descriptive)
Against v20.1 (collection modified 2026-11-05): of the 737 label ids, 581 are active, 12 deprecated and 144 revoked. 143 were already non-active in v12.1 (the description file keeps revoked ids); 13 became non-active later.
39 test sentences (0.054) carry such a label: 24 already in v12.1 (a TRAM data-quality issue) and 15 since then (T1562 Impair Defenses was split into new techniques). 125 active techniques of the current release are outside the label space and cannot be predicted.
Median description similarity to the current text 0.938 (84 ids below 0.80). State results as valid for ATT&CK Enterprise v12.1.

## Q15 Reporting standard and Q16 related work
REFORMS checklist, 32 items with evidence and open holes: `docs/REFORMS_CHECKLIST.md`. Related work refreshed with three 2026 papers: `docs/RELATED_WORK_VERIFIED.md` section F and `ch2_related.md`.


## Q17 Explainer application (thesis objective c, folder `ttp_app`), checked on the thesis PC on 15 Nov 2026
- Replay of the 725 test sentences from the saved scores reproduces the registered numbers: 16 of 16 checks match (P@1, conformal tau, coverage and set size at alpha 0.10 and 0.20, triage coverage and selective P@1 at three targets, stored SHAP count, `E4`). The first run matched 15 of 16: the app's triage threshold interpolated between dev margins instead of using the prereg-19 order statistic. Fixed with a test (D29).
- Live mode (classifier-only fusion SVM + RoBERTa s42 + SecBERT s42, NOT the reported system) on CPU, one run per setting on invented sentences, seconds for scoring plus permutation SHAP: 7 words 2.4 (10 permutations) / 8.4 (40); 26 words 17.4 / 67.0; 54 words 76.9 / 300.3. Largest SHAP additivity error 5.7e-07.
- Written explanations from local qwen2.5:7b pass grounding rule v1 (every quoted word is a top-5 positive-SHAP word; no other technique id) in 23 of 100 (23%) of the first 100 test rows with stored SHAP (0 rows had no LLM answer; median 7.5 s per row). POST-HOC, rule unchanged: 31 of the failures quote only the explained technique's own id or name; 42 quote a word that is not in the sentence. A rule v2 that also accepts the explained technique's id and name is proposed in `ttp_app/README.md`; it needs a fresh row set before any v2 number is reported. A pass shows only that the quoted words come from SHAP; it does not show that an explanation is correct or useful (no human study; the first plausibility study is at chance, `D1`, `D2`).
- The screen warns when the explained model (RoBERTa seed 42) and the fusion disagree on top-1 (test sentences: 108 of 725 (14.9%)), when a label is rare or not active in the latest ATT&CK release, and on known confusions; names follow ATT&CK v12.1.
- AI assistance: the application was written with Claude (claude.ai) and checked and corrected with Claude Code; the thesis must disclose this under the university's AI-use rules (`ttp_app/README.md`, section "AI assistance").
