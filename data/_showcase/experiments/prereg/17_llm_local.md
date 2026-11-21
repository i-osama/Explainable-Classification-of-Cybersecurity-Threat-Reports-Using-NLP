# Pre-registration 17_llm_local: Q1 plan Task 7: LLM baseline with open weights (local Ollama)

| field | content |
|---|---|
| Hypothesis | H: an open-weights 7B LLM (closed-set or retrieve-then-rank) does not reach the matcher ensemble's test P@1. |
| Split | DEV pilot: first 50 dev sentences, parse rate only, no prompt change allowed afterwards; TEST once per variant |
| Metric | P@1 (primary), MRR@3, R@5, parse rate; ranking = the LLM's ordered ids first, then the remaining candidates in retriever order (closed-set: then by SVM score) |
| Comparison | Model qwen2.5:7b (Ollama digest 845dbda0ea48, Q4_K_M), options temperature 0, seed 0, num_predict 64, num_ctx 8192. Variants: closed = 180 training labels (id: name); rr_zero = top-20 candidates from zero-shot bge; rr_matcher = top-20 candidates from the fine-tuned matcher ensemble. Candidate descriptions cut to 40 words. Prompt templates fixed in src/ttpmap/llm.py: CLOSED_TEMPLATE sha256 f0bf94b9ce5c18b2e170f06636568c38bfcf1d65831ee915c0e3584a5219cd9f; RR_TEMPLATE sha256 42c0c897c7305baaeb3e22c68bbe3819f3519da75ce85295c32213451e25439f. |
| Seeds | n/a |
| Dev-only tuning | none (prompts fixed before any output was seen) |
| Decision rule | Family = each variant vs matcher ensemble and vs fusion (3,1,1,1) (6 tests, Holm). H supported if no variant beats the matcher ensemble with Holm p < 0.05. |
| What counts as failure / prior exposure | No test request has been sent before sealing. A 7B local model is a lower bound on LLM performance; notebook 10 keeps the protocol for an API model. |

Split discipline: anything tuned is tuned on DEV only. The test split is evaluated once per configuration listed here. Uncertainty: paired/percentile bootstrap over test sentences, 10,000 resamples, numpy default_rng(20261114). Systems (fixed): SVM (refit, deterministic); RoBERTa and SecBERT = mean probability of seeds 42-44; matcher = mean score of seeds 42-44; fusion = z-score sum with weights (3,1,1,1) in the order matcher, SVM, RoBERTa, SecBERT.
