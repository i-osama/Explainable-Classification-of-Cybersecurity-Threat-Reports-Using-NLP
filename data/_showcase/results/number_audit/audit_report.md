# Number audit of the draft (from the pasted ledger; the .docx is not on this PC)

- registry numbers loaded: 582
- distinct strict tokens checked: 153
- audit_numbers.py status: registered 137, UNREGISTERED 16
- stricter check (value / display / CI of a claim): LITERATURE 11, NOT SUPPORTED 8, SETTING 6, SUPPORTED 128

## UNREGISTERED (as audit_numbers.py would report)

- [p197] `193` ...the Enterprise matrix contains 14 tactics, 193 techniques and 401 sub-techniques... -> LITERATURE: ATT&CK v12 matrix size (14 tactics / 193 techniques / 401 sub-techniques): from the cited ATT&CK source, not from a project file. Not to be confused with the 193 distinct labels of the dataset
- [p197] `401` ...the Enterprise matrix contains 14 tactics, 193 techniques and 401 sub-techniques... -> LITERATURE: as above; the baseline paper's background section says 196 techniques and 411 sub-techniques for v12.0 (_evidence_pack/08_baseline.md): check the source cited for 193 / 401
- [p272] `1.16` ...one or more technique identifiers, 1.16 on average... -> LITERATURE: baseline paper Table 1 (TRAM: 1.16 labels, 23 tokens); confirmed from arXiv:2401.10337, see _evidence_pack/08_baseline.md
- [p311] `24.8` ...Annotation errors reported; low F1 (24.8) on external data... -> LITERATURE: related-work table; no project file; reference must be verified (docs/RELATED_WORK_VERIFIED.md)
- [p313] `39,296` ...fine-tuned on an augmented sentence-TTP set of 39,296 samples (193 TTPs)... -> LITERATURE: related-work table; reference must be verified
- [p314] `92.42%` ...High F1 (92.42%) on its augmented data; STIX export... -> LITERATURE: related-work table; reference must be verified
- [p322] `6,612` ...Multi-stage ranking; benchmark of 6,612 descriptions... -> LITERATURE: related-work table; reference must be verified
- [p323] `57.83%` ...P@1 57.83% on its own data; slow (about 8.9 s per query)... -> LITERATURE: related-work table; reference must be verified
- [p323] `8.9` ...slow (about 8.9 s per query)... -> LITERATURE: related-work table; reference must be verified
- [p331] `37` ...Cleaned set covers only 37 techniques; document-level, LLM-based... -> LITERATURE: related-work table; reference must be verified
- [p334] `0.674` ...extreme-classification baselines reach a P@1 of 0.674 on the same data... -> LITERATURE: baseline paper Table 2, XR-LINEAR on TRAM: P@1 .674; confirmed from arXiv:2401.10337 (_evidence_pack/08_baseline.md)
- [p502] `2.5` ...the 95% interval is formed by the 2.5th and 97.5th percentiles... -> SETTING: percentile of the 95% interval
- [p502] `97.5` ...the 95% interval is formed by the 2.5th and 97.5th percentiles... -> SETTING: percentile of the 95% interval
- [p676] `0.037` ...fusion minus matcher ensemble MRR@3 0.019 (0.003 to 0.037 [confirm])... -> NOT SUPPORTED: number differs. C2 MRR@3 interval is [+0.003, +0.036]
- [p676] `+0.020` ...RoBERTa minus SVM +0.002 in MRR@3 (-0.018 to +0.020)... -> NOT SUPPORTED: number differs. C3 MRR@3 is +0.002 [-0.018, +0.022]
- [p692] `+0.020` ...RoBERTa minus SecBERT MRR@3 +0.003 [-0.015, +0.020]... -> NOT SUPPORTED: number differs. C4 MRR@3 interval is [-0.016, +0.019]

## NOT SUPPORTED or LOOSE under the stricter check

- [p192] `-0.015` ...RoBERTa and the SVM is +0.014 with a 95% interval of -0.015 to +0.040... -> NOT SUPPORTED: number differs. The draft says 10,000 resamples; at 10,000 the C3 interval is [-0.014, +0.041]. -0.015 / +0.040 is the 1,000-resample notebook-setting interval (_evidence_pack/04_bootstrap.csv)
- [p192] `+0.040` ...RoBERTa and the SVM is +0.014 with a 95% interval of -0.015 to +0.040... -> NOT SUPPORTED: number differs. See the row above: C3 at 10,000 resamples is [-0.014, +0.041]
- [p676] `0.037` ...fusion minus matcher ensemble MRR@3 0.019 (0.003 to 0.037 [confirm])... -> NOT SUPPORTED: number differs. C2 MRR@3 interval is [+0.003, +0.036]
- [p676] `+0.020` ...RoBERTa minus SVM +0.002 in MRR@3 (-0.018 to +0.020)... -> NOT SUPPORTED: number differs. C3 MRR@3 is +0.002 [-0.018, +0.022]
- [p676] `-0.022` ...RoBERTa minus SecBERT is +0.001 (-0.022 to +0.025) [P@1]... -> NOT SUPPORTED: number differs. C4 at 10,000 resamples is [-0.023, +0.025]; -0.022 is the 1,000-resample value
- [p676] `+0.003` ...RoBERTa minus SecBERT ... and +0.003 (-0.015 to +0.020) [MRR@3]... -> NOT SUPPORTED: number differs. C4 MRR@3 is +0.002 [-0.016, +0.019]
- [p676] `-0.015` ...RoBERTa minus SecBERT MRR@3 +0.003 (-0.015 to +0.020)... -> NOT SUPPORTED: number differs. C4 MRR@3 interval is [-0.016, +0.019]
- [p692] `+0.020` ...RoBERTa minus SecBERT MRR@3 +0.003 [-0.015, +0.020]... -> NOT SUPPORTED: number differs. C4 MRR@3 interval is [-0.016, +0.019]

## Not caught by a number scan (integers below 10 are ignored by the script)

- [p604, table] "2 test and 1 development sentence found": exact duplicates are 1 test and 0 dev; near-duplicates add 1 test and 3 dev rows (A6). '2 test' is right only as exact + near; '1 development' is supported by neither count.
