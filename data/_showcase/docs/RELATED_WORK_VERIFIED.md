# RELATED WORK: verification log

Checked by web search on 2026-11-14 (access date for every URL below). The thesis draft is not in the project folder, so the list covers
(a) references named in project files and in the number ledger of the draft, and (b) the closest TTP-mapping papers found.
Status: **VERIFIED** = authors, title, venue/year and a working URL were confirmed by a search result; **PARTLY** = the paper is confirmed but
a number the draft attributes to it was not found; **UNVERIFIED** = not confirmed. Nothing here is filled in from memory.
Numbers the draft takes from these papers are literature values: they are not in `thesis_numbers.json` and must carry a citation.

## A. Core references

| # | Reference | Venue, year | URL / DOI | Status | Supports in the thesis | Note |
|---|---|---|---|---|---|---|
| 1 | T. Nguyen, N. Šrndić, A. Neth. *Noise Contrastive Estimation-based Matching Framework for Low-Resource Security Attack Pattern Recognition* | Findings of EACL 2024 (ACL Anthology listing; arXiv says "accepted at EACL 2024") | https://arxiv.org/abs/2401.10337 ; https://virtual2024.eacl.org/paper_98.html | VERIFIED | published baseline (P@1, MRR@3 on TRAM), dataset statistics, split ratios | Table values read from the arXiv PDF: `_evidence_pack/08_baseline.md`. The exact Anthology page URL was not retrieved. arXiv v4 was revised in July 2025: check which version the thesis cites |
| 2 | B. Strom, A. Applebaum, D. Miller, K. Nickels, A. Pennington, C. Thomas. *MITRE ATT&CK: Design and Philosophy* | MITRE technical report, July 2018; revised March 2020 | https://www.mitre.org/news-insights/publication/mitre-attck-design-and-philosophy | VERIFIED | ATT&CK background | - |
| 3 | S. Lundberg, S.-I. Lee. *A Unified Approach to Interpreting Model Predictions* | NIPS 2017 (Advances in Neural Information Processing Systems 30) | https://arxiv.org/abs/1705.07874 ; https://papers.nips.cc/paper/7062-a | VERIFIED | SHAP | - |
| 4 | J. DeYoung, S. Jain, N. F. Rajani, E. Lehman, C. Xiong, R. Socher, B. C. Wallace. *ERASER: A Benchmark to Evaluate Rationalized NLP Models* | ACL 2020, pp. 4443-4458 | https://aclanthology.org/2020.acl-main.408/ ; DOI 10.18653/v1/2020.acl-main.408 | VERIFIED | comprehensiveness and sufficiency | - |
| 5 | J. Devlin, M.-W. Chang, K. Lee, K. Toutanova. *BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding* | NAACL-HLT 2019, pp. 4171-4186 | https://aclanthology.org/N19-1423/ | VERIFIED | transformer encoders | - |
| 6 | Y. Liu et al. *RoBERTa: A Robustly Optimized BERT Pretraining Approach* | arXiv preprint, July 2019 (no conference venue on the arXiv record) | https://arxiv.org/abs/1907.11692 | VERIFIED | RoBERTa-base | cite as arXiv preprint |
| 7 | S. Xiao, Z. Liu, P. Zhang, N. Muennighoff, D. Lian, J.-Y. Nie. *C-Pack: Packed Resources For General Chinese Embeddings* | SIGIR 2024 | https://arxiv.org/abs/2309.07597 ; DOI 10.1145/3626772.3657878 | VERIFIED | bge embedding models | the title changed between arXiv versions; the BGE English models are described in this paper |
| 8 | `jackaduma/SecBERT` model | GitHub model release, MIT licence | https://github.com/jackaduma/SecBERT | VERIFIED | SecBERT checkpoint | repository exists, licence MIT, not archived (GitHub API, 15 Nov 2026); no peer-reviewed paper, cite as software |
| 9 | TRAM (Threat Report ATT&CK Mapper), Center for Threat-Informed Defense | software and data repository, Apache-2.0, active | https://github.com/center-for-threat-informed-defense/tram | VERIFIED | dataset origin | licence Apache-2.0, not archived, last push 2025-05-06 (GitHub API, 15 Nov 2026). The split files are attributed to DOI 10.57967/hf/1811 = Hugging Face `tumeteor/Security-TTP-Mapping` (created 2024-01-22), whose card licence field is `cc` with no variant |

## B. Closest TTP-mapping and CTI-classification work

| # | Reference | Venue, year | URL / DOI | Status | Draft statement to check | Finding |
|---|---|---|---|---|---|---|
| 10 | N. Rani, B. Saha, V. Maurya, S. K. Shukla. *TTPXHunter: Actionable Threat Intelligence Extraction as TTPs from Finished Cyber Threat Reports* | Digital Threats: Research and Practice 5(4), 2024 | https://arxiv.org/abs/2403.03267 | VERIFIED | "augmented sentence-TTP set of 39,296 samples (193 TTPs)", "F1 92.42%" | 39,296 samples and 92.42% F1 in the abstract; "193" TTP classes confirmed in the full text checked 15 Nov 2026 (arXiv HTML): Fig. 9 "Sentence-TTP Dataset Data Distribution over 193-TTP Class". Author list from dblp key RaniSMS24 |
| 11 | U. Kumarasinghe et al. *Semantic Ranking for Automated Adversarial Technique Annotation in Security Text* | ACM AsiaCCS 2024, pp. 49-62 | https://arxiv.org/abs/2403.17068 ; DOI 10.1145/3634737.3645000 | PARTLY | "benchmark of 6,612 descriptions", "P@1 57.83%", "about 8.9 s per query" | full text checked 15 Nov 2026 (arXiv HTML): 6,612 unique threat-behaviour descriptions (combined dataset) and 8.9 s per query confirmed; top-3 recall 81% among 193 top-level techniques confirmed. **57.83% not found**: drop it or give its source |
| 12 | L. Lange et al. *AnnoCTR: A Dataset for Detecting and Linking Entities, Tactics, and Techniques in Cyber Threat Reports* | LREC-COLING 2024 | https://arxiv.org/abs/2404.07765 | VERIFIED | "TRAM model reaches an F1 of 24.8 on technique detection in AnnoCTR" | full text checked 15 Nov 2026 (arXiv HTML): "TRAM baseline 24.8" (technique linking, results table). Authors from the arXiv API: L. Lange, M. Müller, G. Haratinezhad Torbati, D. Milchevski, P. Grau, S. Pujari, A. Friedrich |
| 13 | Y. Cheng, C. Li, R. S. P. Basuki, Q. Cui, W. Ding, P. Gao. *CTI2TTP: Evidence-Grounded TTP Extraction from Cyber Threat Intelligence via Diverge-then-Converge Verification* | arXiv preprint 2605.25836 (v2), 2026 | https://arxiv.org/abs/2605.25836 | VERIFIED | cleaned TRAM benchmark (TRAM-Clean) and document-level extraction; supports our note on TRAM label noise | title and authors from the arXiv API; full text checked 15 Nov 2026 (arXiv HTML): "2,066 sentences with 665 technique labels across 37 unique techniques" (TRAM-Clean). The old entry name "TRAM-Clean / TTPrint" was not the title |
| 14 | G. Husari, E. Al-Shaer, M. Ahmed, B. Chu, X. Niu. *TTPDrill: Automatic and Accurate Extraction of Threat Actions from Unstructured Text of CTI Sources* | ACSAC 2017 | DOI 10.1145/3134600.3134646 | PARTLY | early ontology/BM25 approach | title, venue, DOI confirmed; only the first author's name was confirmed by the search |
| 15 | V. Legoy, M. Caselli, C. Seifert, A. Peter. *Automated Retrieval of ATT&CK Tactics and Techniques for Cyber Threat Reports* (rcATT) | arXiv preprint, April 2020 | https://arxiv.org/abs/2004.14322 | VERIFIED | classical ML baseline family | - |
| 16 | W. You, Y. Park. *Cyber-Attack Technique Classification Using Two-Stage Trained Large Language Models* | arXiv preprint 2411.18755, 2024 | https://arxiv.org/abs/2411.18755 | VERIFIED | LLM approach on TRAM-style data | verified 15 Nov 2026 against the arXiv API record; no venue on the record |
| 17 | Á. Ruiz-Ródenas, J. Pujante Sáez, D. García-Algora, M. Rodríguez Béjar, J. Blasco, J. L. Hernández-Ramos. *SynthCTI: LLM-Driven Synthetic CTI Generation to enhance MITRE Technique Mapping* | arXiv preprint 2507.16852, 2025 | https://arxiv.org/abs/2507.16852 | VERIFIED | synthetic data for rare techniques (relevant to our tail result) | verified 15 Nov 2026 against the arXiv API record; no venue on the record |
| 18 | S. Della Penna, R. Natella, V. Orbinato, L. Parracino, L. Pianese. *CTI-HAL: A Human-Annotated Dataset for Cyber Threat Intelligence Analysis* | WACCO 2025 workshop, co-located with IEEE EuroS&P 2025 | https://arxiv.org/abs/2504.05866 | VERIFIED | newer human-annotated dataset | verified 15 Nov 2026 against the arXiv API record (comment field gives the venue) |

## E. Recent work on LLM and retrieval-based technique mapping (added 15 Nov 2026; for the Q1 related-work section)

| # | Reference | Venue, year | URL / DOI | Status | Supports in the thesis | Note |
|---|---|---|---|---|---|---|
| 19 | A. Lekssays, U. Shukla, H. T. Sencar, M. R. Parvez. *TechniqueRAG: Retrieval Augmented Generation for Adversarial Technique Annotation in Cyber Threat Intelligence Text* | Findings of ACL 2025 | https://arxiv.org/abs/2505.11988 ; https://aclanthology.org/2025.findings-acl.1076/ | VERIFIED | closest design to our matcher plus LLM re-ranking (prereg 17 variant rr_matcher) | arXiv API and ACL Anthology BibTeX |
| 20 | H. C. Nguyen, S. Tariq, M. B. Chhetri, B. Q. Vo. *Towards Effective Identification of Attack Techniques in Cyber Threat Intelligence Reports using Large Language Models* | The Web Conference 2025 (WWW '25), short paper | https://arxiv.org/abs/2505.03147 ; DOI 10.1145/3701716.3715469 | VERIFIED | LLM baselines vs TRAM; data rebalancing with LLM-generated data | verified 15 Nov 2026 against the arXiv API record (comment and DOI fields) |
| 21 | F. Morbiato, M. Keller, P. Nair, L. Romano. *Hierarchical Retrieval Augmented Generation for Adversarial Technique Annotation in Cyber Threat Intelligence Text* | arXiv preprint 2604.14166, 2026 | https://arxiv.org/abs/2604.14166 | VERIFIED | tactic-technique hierarchy in retrieval (future work for the matcher) | verified 15 Nov 2026 against the arXiv API record; no venue on the record |
| 22 | N. O. Jaffal, R. Jarrar, M. Alkhanafseh, D. Mohaisen. *SMAH-CTI: A Unified Sentence-Level Benchmark for Multi-Task Cyber Threat Intelligence Extraction* | Findings of EMNLP 2026 | https://aclanthology.org/2026.findings-emnlp.1180/ | VERIFIED | newer sentence-level benchmark (external-validity threat: one dataset) | ACL Anthology BibTeX |

Search note: a vendor blog reports that the TRAM LLM found the right technique in 88 of 100 cases; it is not peer reviewed and its test conditions are not stated. Do not cite it as a result.

## F. 2026 refresh (added 15 Nov 2026, Q1 wave 2; title, authors, date and abstract checked against the arXiv API record)

| # | Reference | Venue, year | URL / DOI | Status | Supports in the thesis | Note |
|---|---|---|---|---|---|---|
| 23 | A. Ryan, S. S. Noor, M. Erfan, S. Mitra, S. Mittal, M. R. Rahman. *Evaluating Open-Source LLMs for Multi-Label ATT&CK Technique Classification on CTI Reports* | arXiv preprint 2606.18166, 2026 | https://arxiv.org/abs/2606.18166 | VERIFIED | context for the local LLM baseline (prereg 17): open-weights LLMs are weak at multi-label technique classification | abstract: 2,076 annotated sentences from 83 reports, 114 techniques, kappa 0.68; seven open LLMs (8B to 236B); best micro-F1 0.22; size correlates with F1; prompt strategy and temperature gave no significant gain. Different data (complex reports, negatives included): do not compare its numbers with ours directly |
| 24 | M. N. Haque, S. Hamer, B. Wroblewski, M. R. Rahman, L. Williams. *Beyond Single Reports: Evaluating Automated ATT&CK Technique Extraction in Multi-Report Campaign Settings* | arXiv preprint 2604.07470, 2026 | https://arxiv.org/abs/2604.07470 | VERIFIED | external validity: sentence-level TRAM results do not transfer to campaign-level extraction; confusions between semantically similar techniques | abstract: 29 methods (NER, encoder, decoder LLM) on 90 reports of 3 campaigns; aggregation improves F1 by about 26%; max F1 78.6% (SolarWinds), 54.9% (XZ Utils); up to 33.3% of errors are between similar techniques sharing tactics |
| 25 | D. Das, A. Banik, M. S. Islam, M. R. Rahman. *A Structured Cyber Threat Intelligence Dataset Using STIX 2.1 Entities and MITRE ATT&CK Mappings* | arXiv preprint 2607.23312, 2026 (6 pages) | https://arxiv.org/abs/2607.23312 | VERIFIED | ATT&CK version drift (wave 2, prereg 21): current datasets map to ATT&CK v19.1, ours is v12.1; LLMs as annotation-consistency checkers (wave 2, prereg 20) | abstract: 150 reports, 269 techniques and sub-techniques; local LLM judges help find annotation inconsistencies but expert validation remains essential. Full text (arXiv HTML v1): attack patterns "were manually mapped to ATT&CK version 19.1 enterprise techniques and sub-techniques" |

Method references for wave 2 (checked 15 Nov 2026):

| method | reference | DOI / URL | status |
|---|---|---|---|
| split conformal prediction | A. N. Angelopoulos, S. Bates, A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification, arXiv 2107.07511 (also Foundations and Trends in ML) | https://arxiv.org/abs/2107.07511 | VERIFIED (arXiv record) |
| multi-label conformal sets with limited false positives | A. Fisch, T. Schuster, T. Jaakkola, R. Barzilay, Conformal Prediction Sets with Limited False Positives, ICML 2022 | https://arxiv.org/abs/2202.07650 | VERIFIED (arXiv record; venue from icml.cc) |
| conformal multi-label text classification | V. Örnbratt, J. Hallberg Szabadváry, Conformal LLM Multi-label Text Classification with Binary Relevance Approach, COPA 2025, PMLR 266, 214-229 | https://proceedings.mlr.press/v266/ornbratt25a.html | VERIFIED (PMLR page metadata) |
| selective classification, risk-coverage | Y. Geifman, R. El-Yaniv, Selective Classification for Deep Neural Networks, NeurIPS 2017 | https://arxiv.org/abs/1705.08500 | VERIFIED (arXiv record) |
| confident learning (label noise) | C. G. Northcutt, L. Jiang, I. L. Chuang, Confident Learning: Estimating Uncertainty in Dataset Labels, JAIR 2021 | https://arxiv.org/abs/1911.00068 | VERIFIED (arXiv journal-ref) |
| reporting standard | S. Kapoor et al. (19 authors), REFORMS: Consensus-based Recommendations for Machine-learning-based Science, Science Advances 10(18), 2024 | 10.1126/sciadv.adk3452 ; preprint https://arxiv.org/abs/2308.07832 | VERIFIED (Crossref) |

## C. Statements in the draft that conflict or need a source

| Draft statement | Problem | Action |
|---|---|---|
| "the Enterprise matrix contains 14 tactics, 193 techniques and 401 sub-techniques" (version 12) | Reference 1 says of version 12.0: "14 tactics, 196 techniques, 411 sub-techniques". Our description file has 737 entries (333 techniques and 404 sub-techniques by id pattern, including revoked ids). Three different counts | cite the official ATT&CK v12 release notes for the count actually used, or state the count of the data file and say what it contains |
| "193 TTPs" attributed to TTPXHunter | confirmed in the full text (Fig. 9, 193-TTP classes; reference 10); 193 is also the number of TRAM labels in reference 1 | keep with citation to reference 10 |
| baseline training time "about 24 h on one V100" | confirmed in reference 1, Limitations | keep with citation |
| P@1 of 0.674 for extreme-classification baselines "on the same data" | confirmed: XR-LINEAR on TRAM, reference 1 Table 2 | keep with citation |
| average of 1.16 labels and 23 tokens per TRAM text | confirmed: reference 1 Table 1 | keep with citation |

## D. Standard methods (checked 15 Nov 2026 against Crossref, the arXiv API or the publisher page)

| method | reference | DOI / URL | status |
|---|---|---|---|
| McNemar's test | Q. McNemar, Note on the Sampling Error of the Difference Between Correlated Proportions or Percentages, Psychometrika, 1947 | 10.1007/BF02295996 | VERIFIED |
| Holm's step-down procedure | S. Holm, A simple sequentially rejective multiple test procedure, Scandinavian Journal of Statistics, 1979 | no DOI in Crossref; JSTOR record | UNVERIFIED: confirm volume and pages on JSTOR |
| bootstrap, percentile interval | B. Efron, R. J. Tibshirani, An Introduction to the Bootstrap, Chapman & Hall/CRC | 10.1201/9780429246593 (Crossref year 1994 for this edition) | VERIFIED |
| Cohen's kappa | J. Cohen, A Coefficient of Agreement for Nominal Scales, Educational and Psychological Measurement, 1960 | 10.1177/001316446002000104 | VERIFIED |
| Fleiss' kappa | J. L. Fleiss, Measuring nominal scale agreement among many raters, Psychological Bulletin, 1971 | 10.1037/h0031619 | VERIFIED |
| Krippendorff's alpha | A. F. Hayes, K. Krippendorff, Answering the Call for a Standard Reliability Measure for Coding Data, Communication Methods and Measures 1, 77-89, 2007 | 10.1080/19312450709336664 | VERIFIED |
| expected calibration error | C. Guo, G. Pleiss, Y. Sun, K. Q. Weinberger, On Calibration of Modern Neural Networks, ICML 2017 | https://arxiv.org/abs/1706.04599 | VERIFIED |
| AdamW | I. Loshchilov, F. Hutter, Decoupled Weight Decay Regularization, ICLR 2019 | https://arxiv.org/abs/1711.05101 | VERIFIED |
| scikit-learn | F. Pedregosa et al., Scikit-learn: Machine Learning in Python, JMLR 12, 2825-2830, 2011 | https://www.jmlr.org/papers/v12/pedregosa11a.html | VERIFIED |
| linear SVM | C. Cortes, V. Vapnik, Support-vector networks, Machine Learning 20, 273-297, 1995 | 10.1007/BF00994018 | VERIFIED |
| TF-IDF weighting | G. Salton, C. Buckley, Term-weighting approaches in automatic text retrieval, Information Processing & Management 24, 513-523, 1988 | 10.1016/0306-4573(88)90021-0 | VERIFIED |

## Sources

- https://arxiv.org/abs/2401.10337 , https://virtual2024.eacl.org/paper_98.html
- https://arxiv.org/abs/2403.03267 , https://dblp.uni-trier.de/rec/journals/dtrap/RaniSMS24.html
- https://arxiv.org/abs/2403.17068 , https://github.com/qcri/Text2TTP
- https://arxiv.org/abs/2404.07765
- https://arxiv.org/abs/2605.25836 , https://arxiv.org/abs/2411.18755 , https://arxiv.org/abs/2507.16852 , https://arxiv.org/abs/2504.05866
- https://arxiv.org/abs/1705.07874 , https://papers.nips.cc/paper/7062-a
- https://aclanthology.org/2020.acl-main.408/
- https://arxiv.org/abs/2309.07597
- https://arxiv.org/abs/1907.11692 , https://aclanthology.org/N19-1423/
- https://www.mitre.org/news-insights/publication/mitre-attck-design-and-philosophy
- https://arxiv.org/abs/2004.14322 , https://acsac.org/2017/program-files/s297.html
- https://export.arxiv.org/api/query (records for 2605.25836, 2411.18755, 2507.16852, 2504.05866, 2505.11988, 2505.03147, 2604.14166) , https://aclanthology.org/2025.findings-acl.1076.bib , https://aclanthology.org/2026.findings-emnlp.1180.bib
- https://huggingface.co/api/datasets/tumeteor/Security-TTP-Mapping , https://api.github.com/repos/center-for-threat-informed-defense/tram , https://api.github.com/repos/jackaduma/SecBERT
- https://api.crossref.org/works (McNemar, Cohen, Fleiss, Efron-Tibshirani, Hayes-Krippendorff, Cortes-Vapnik, Salton-Buckley) , https://www.jmlr.org/papers/v12/pedregosa11a.html , https://export.arxiv.org/api/query?id_list=1706.04599,1711.05101
- https://export.arxiv.org/api/query?id_list=2606.18166,2604.07470,2607.23312,2107.07511,2202.07650,1705.08500,1911.00068,2308.07832 , https://api.crossref.org/works/10.1126/sciadv.adk3452 , https://proceedings.mlr.press/v266/ornbratt25a.html , https://reforms.cs.princeton.edu/

## G. Design science and usability evaluation (verified 15 Nov 2026 via the Crossref API)

Used to frame the thesis as design science research (artefact + evaluation) and for the usability study kit of the explainer app.

| reference | status | checked against | URL |
|---|---|---|---|
| Hevner, A. R., March, S. T., Park, J., & Ram, S. (2004). Design science in information systems research. MIS Quarterly, 28(1), 75-106. | VERIFIED | Crossref: authors, year, title, journal, volume, issue, pages | https://doi.org/10.2307/25148625 |
| Peffers, K., Tuunanen, T., Rothenberger, M. A., & Chatterjee, S. (2007). A design science research methodology for information systems research. Journal of Management Information Systems, 24(3), 45-77. | VERIFIED | Crossref: authors, year, title, journal, volume, issue, pages | https://doi.org/10.2753/MIS0742-1222240302 |
| Brooke, J. (1996). SUS: A "quick and dirty" usability scale. In Usability Evaluation in Industry (pp. 207-212 of the Taylor & Francis e-book; print pages not checked). | PARTLY | Crossref: title, book, year, e-book pages; the author field is empty in Crossref (author not checked here) | https://doi.org/10.1201/9781498710411-35 |
| Bangor, A., Kortum, P. T., & Miller, J. T. (2008). An empirical evaluation of the System Usability Scale. International Journal of Human-Computer Interaction, 24(6), 574-594. | VERIFIED | Crossref: authors, year, title, journal, volume, issue, pages | https://doi.org/10.1080/10447310802205776 |
