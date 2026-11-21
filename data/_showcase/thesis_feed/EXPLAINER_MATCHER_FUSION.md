# Matcher and Fusion Explained Simply

Nov 15, 2026 · @Osama · corrected version (every number checked against `thesis_numbers.json`; ids in backticks)

This page explains the thesis in plain language: what we built, how the matcher and the fusion work, and why the fusion is the most accurate system overall, but not the winner on rare techniques.

## The big picture and what we did

Cyber-security reports contain sentences like "the attacker copied passwords from memory". MITRE ATT&CK is a large catalogue of attacker behaviour, called **techniques**, and each has an ID such as T1055. The thesis builds a program that reads a sentence and guesses which technique ID(s) it describes. One sentence can have more than one correct answer.

The data is **TRAM**: 3,468 sentences to learn from, 604 to tune settings on, and 725 for the final exam (`A2`). The program picks from **733 possible techniques** (`A8.space`). The catalogue file has 737 entries (`A8.file`), but 4 are revoked IDs whose descriptions duplicate an active ID, so they were dropped.

**What we did**

1. Built the normal models (baselines): TF-IDF + SVM, RoBERTa and SecBERT. They learn from examples, like a student memorising past exam questions. RoBERTa and SecBERT were trained with 3 random starts (seeds 42, 43, 44).
2. Built the matcher.
3. Built the fusion.
4. Checked our own work: how much a score moves by chance (about ±0.03, `B13a.halfwidth`), paired bootstrap tests with Holm correction, accuracy on rare labels, and two attempts to fix rare labels (longer descriptions, a support-aware weighting rule). Neither helped (see "Honest limits").
5. Wrote it down: the experiment record, a results dashboard and the progress document.

**Still to do:** SHAP of the full fusion (needs the matcher retrained with saved weights on Colab; SHAP of one RoBERTa seed is done), the Qwen explanations, the demo and the paper.

## How we measure, and normal models vs. the matcher

- **P@1:** how often the model's top guess is right.
- **MRR@3:** like P@1, but with partial credit if the right answer is 2nd or 3rd.
- **R@5:** the share of correct (sentence, technique) pairs that appear somewhere in the top 5.

**Normal models** learn "sentences like this get label X". They are strong on common labels, but they can only pick labels they saw in training, and they are weak on labels with few examples.

**The matcher** works differently. It reads the **description** of every technique, like a dictionary entry. It turns the sentence and each description into a list of numbers that captures the meaning (one shared `BAAI/bge-base-en-v1.5` encoder), then ranks the descriptions by how close their numbers are to the sentence. Because it reads descriptions, it can in principle guess labels it never saw in training.

It was trained by showing a sentence, its correct technique and 64 random wrong techniques to push away (`M1.n_neg`). Its scores on the test set:

- Before training (zero-shot): P@1 0.228 (`B10a`).
- Trained with an 8-epoch budget, seed 42 only: P@1 0.731 (`M1.ft8.p1`). This run was superseded.
- Trained with a 20-epoch budget and early stopping (patience 4, `M1.ft20.budget`), seeds 42, 43, 44: P@1 0.756 ± 0.015 as a mean of the single seeds (`B10b`).
- The 3 seeds' scores averaged into one ensemble: P@1 0.777 (`B10c`). This ensemble is the matcher used everywhere below.
- On rare labels (rarest correct label has 1-4 training sentences, 34 test sentences, `G4.n.1_4`): matcher 0.559, against 0.294 for RoBERTa, 0.176 for SecBERT and 0.206 for the SVM (`G4.*.1_4`).

It is not perfect on unseen labels. Its R@5 on the 10 never-seen labels is 0.60 (`G6.unseen_r5_matcher`), and it varied a lot between seeds: 0.600 ± 0.100 (`M1.ft20.unseen_r5_seeds`).

## How the fusion works

Think of a panel of 4 judges: the matcher, SVM, RoBERTa and SecBERT. Each gives a score to all 733 techniques. For each sentence:

1. **Put scores on one scale.** Each judge's scores are turned into z-scores for that sentence: how many standard deviations a technique sits above that judge's average. No judge can shout louder just by using bigger numbers. A classifier gives a neutral 0 to techniques it never saw in training.
2. **Add with weights.** Matcher × 3, SVM × 1, RoBERTa × 1, SecBERT × 1.
3. **Rank** the techniques by the weighted total.

The weights were chosen using the dev set only. The 725-sentence test set was then used once.

> **How the weights (3,1,1,1) were chosen**
>
> - We tried every combination of whole-number weights from 0 to 3 for each judge: 255 settings (`B14.coarse_n`).
> - For each one we measured the fused ranking on the **dev set** (604 sentences), using MRR@3.
> - (3,1,1,1) came out on top of that grid, both with one matcher seed and with the averaged matcher (`B14`, `B14.avg_coarse`). The test set was not used to choose it.
> - It is the winner of this grid, not the best possible setting: a wider grid of 1,711 settings picks (4,1,1,1) with matcher seed 42 and (8,3,2,2) with the averaged matcher (`B14`, `B14.avg_wide`). The differences on test are small.

**Worked example (the scores are invented to show the idea).** Sentence: "The malware runs a PowerShell command to download a second file." The correct answer is T1059.001.

<!-- illustrative -->
| Technique | Matcher | SVM | RoBERTa | SecBERT | Total, equal weights | Total, matcher × 3 |
|---|---|---|---|---|---|---|
| T1059.001 PowerShell (correct) | 5.0 | 4.0 | 4.5 | 4.0 | 17.5 | **27.5** |
| T1059.003 Windows Command Shell | 2.0 | 5.5 | 5.0 | 5.2 | **17.7** | 21.7 |
| T1105 Ingress Tool Transfer | 1.5 | 2.0 | 3.0 | 2.5 | 9.0 | 12.0 |
<!-- /illustrative -->

The three classifiers lean toward the wrong technique, because they learned that command-line sentences often belong there. The matcher read the descriptions and prefers the right one. With equal weights the wrong answer wins by a hair; with the matcher counted three times the correct answer wins clearly.

**Why fusion helps.** The classifiers learned from the same data, so they make similar mistakes. The matcher works from the descriptions, so its mistakes differ. When errors differ, adding the scores cancels some of them.

## Why the fusion is better overall

The fusion is the most accurate system overall on the test set: P@1 0.803, MRR@3 0.856, R@5 0.917 (`B13a`, `B13b`, `B13c`).

Every row below is one system scored once on the 725 test sentences. Rows with seeds use the ensemble of seeds 42-44 (scores averaged before ranking); the SVM is deterministic and has no seeds.

| System | P@1 | MRR@3 | R@5 |
|---|---|---|---|
| TF-IDF + SVM | 0.742 | 0.814 | 0.888 |
| RoBERTa (3-seed ensemble) | 0.756 | 0.816 | 0.865 |
| SecBERT (3-seed ensemble) | 0.754 | 0.814 | 0.868 |
| Matcher (3-seed ensemble) | 0.777 | 0.837 | 0.875 |
| Classifiers-only ensemble | 0.774 | 0.837 | 0.901 |
| **Fusion (3,1,1,1)** | **0.803** | **0.856** | **0.917** |

Ids: `B6`, `B7`, `B8`, `B10c`, `B9`, `B13a` with their `.mrr3` and `.r5` entries.

The matcher adds something real: the fusion beats the classifiers-only mix by +0.029 P@1, with a 95% interval of +0.017 to +0.043 (`C1`). This survives Holm correction over the 8 comparisons, so it is not luck.

## Honest limits of the fusion

- **Over the matcher alone the gain is not established.** It is +0.026 P@1, interval +0.001 to +0.051, and the Holm-corrected p-value is 0.190 (`C2`, `C2.holm`). Do not write "the fusion beats the matcher".
- Part of the gain is just averaging many models. Averaging the matcher's 3 seeds alone lifted it from 0.756 to 0.777 (`B10b`, `B10c`).
- **It is not better on rare or unseen techniques.** On rare labels (1-4 training sentences, 34 test sentences) the fusion gets 0.294 and the matcher 0.559 (`G4.fusion.1_4`, `G4.matcher.1_4`). On the 10 never-seen labels the fusion gets P@1 0.000 and the matcher 0.200 (`G4.*.unseen`). The fusion still has 0.50 of the unseen pairs in its top 5, against 0.60 for the matcher (`G6`). These groups are small, so the intervals are wide.
- **The two fixes for rare labels did not work.** Longer descriptions (256 tokens): matcher 0.774 and fusion 0.800, against 0.777 and 0.803 (`M1.L256.p1`, `M1.L256.fusion.p1`). The pre-registered support-aware fusion failed its success rule (Holm p 0.453, `G9.fam1.holm`).
- **Against the paper:** our P@1 is 0.803 and theirs is 0.770; our MRR@3 is 0.856 and theirs is 0.864. Their system was not re-run under our protocol, and we have not verified that their split and training mode match ours. So the comparison is side by side, not controlled. Say "competitive with", not "better than".
- It is more complicated and much harder to explain with SHAP, which is why SHAP currently explains one RoBERTa seed. That model's top-1 answer differs from the fusion's on 108 of the 725 test sentences (`E4`), so those explanations do not explain the fusion.

In short: the fusion is the most accurate system overall on this test set. It is not the winner on rare techniques, and its lead over the matcher alone is not statistically supported.

## Method lines (for the systems table)

- **Matcher:** bi-encoder retrieval (`BAAI/bge-base-en-v1.5`): zero-shot; fine-tuned with an 8-epoch budget (seed 42 only, superseded); fine-tuned with a 20-epoch budget and early stopping, patience 4 (seeds 42, 43, 44). The headline results use the 3-seed score ensemble.
- **Fusion:** weighted sum of per-sentence z-scored scores from the matcher, SVM, RoBERTa and SecBERT. Weights (3,1,1,1) were chosen by dev MRR@3 from a 0-3 grid (255 settings).
