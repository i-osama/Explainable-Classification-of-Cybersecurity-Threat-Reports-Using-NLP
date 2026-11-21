"""Retrain the bge matcher on CPU WITH saved weights (the original Exp_2.1 `train_matcher` saved only scores).
Faithful port of Exp_2.1 CELL 3 + CELL 7 settings: BAAI/bge-base-en-v1.5, CLS pooling, L2 norm, scale 30, 64 random
negatives from all 733 labels, batch 16, lr 2e-5, AdamW wd 0.01, linear warmup 10%, clip 1.0, max 20 epochs,
patience 4, epoch selected by DEV MRR@3, text 128 tokens, descriptions 128 (train) / 256 (eval).
Differences from the Colab run (unavoidable): CPU fp32 instead of GPU AMP fp16; train rows come from
combined_train.csv[tram] (row order may differ from tram_train.tsv), so scores are NOT bit-identical to run_match_1.
Resumable: a checkpoint is written after every epoch.  Output: _evidence_pack/matcher_retrain/ft20_s<seed>/
usage: python x3_train_matcher_cpu.py --seed 42 [--bench 3]
"""
import argparse, json, math, os, random, time
import numpy as np, pandas as pd, torch, torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel, get_linear_schedule_with_warmup
from common import PACK, DATA, p_at_1, mrr_at_k, rank_topk
from systems import build

ap = argparse.ArgumentParser(); ap.add_argument("--seed", type=int, default=42); ap.add_argument("--bench", type=int, default=0)
A = ap.parse_args()
BASE = "BAAI/bge-base-en-v1.5"
EPOCHS, PATIENCE, BS, LR, N_NEG, SCALE, T_LEN, L_TRAIN, L_EVAL = 20, 4, 16, 2e-5, 64, 30.0, 128, 128, 256
OUT = PACK / "matcher_retrain" / f"ft20_s{A.seed}"; OUT.mkdir(parents=True, exist_ok=True)
S = build(); L = S.L
desc = pd.read_csv(DATA / "ttp-desc-mappings.csv", sep="\t")
desc["ttp"] = desc["ttp"].str.lower().str.strip()
desc["description"] = (desc["description"].fillna("").str.replace(r"\s+", " ", regex=True).str.replace(r"\bcitation:\s*", "", regex=True).str.strip())
desc = desc.drop_duplicates("ttp"); desc = desc[~desc["ttp"].isin({"t1060", "t1107", "t1151", "t1188"})].reset_index(drop=True)
assert [t.upper() for t in desc["ttp"]] == S.LABELS
LABEL_TEXTS = np.array(desc["description"].tolist(), dtype=object)
texts = S.train["text"].tolist(); N = len(texts); Ytr = S.Ytr
pos_lists = [np.where(Ytr[i])[0] for i in range(N)]; pool = np.arange(L)

random.seed(A.seed); np.random.seed(A.seed); torch.manual_seed(A.seed)
rng = np.random.default_rng(A.seed)
tok = AutoTokenizer.from_pretrained(BASE); enc_model = AutoModel.from_pretrained(BASE).float()


def emb(tx, max_len):
    e = tok(list(tx), padding=True, truncation=True, max_length=max_len, return_tensors="pt")
    return F.normalize(enc_model(**e).last_hidden_state[:, 0].float(), dim=-1)


@torch.no_grad()
def embed_all(tx, max_len, bs=64):
    enc_model.eval(); out = []
    for i in range(0, len(tx), bs): out.append(emb(tx[i:i + bs], max_len))
    return torch.cat(out).numpy()


def run_eval():
    le = embed_all(LABEL_TEXTS.tolist(), L_EVAL)
    Sd = embed_all(S.dev["text"].tolist(), T_LEN) @ le.T; St = embed_all(S.test["text"].tolist(), T_LEN) @ le.T
    def met(Sc, Y):
        top5 = rank_topk(Sc, 5); un = Y & ~S.SEEN[None, :]
        it = np.zeros(Y.shape, bool); it[np.arange(len(Y))[:, None], top5] = True
        return {"P@1": float(p_at_1(Sc, Y).mean()), "MRR@3": float(mrr_at_k(Sc, Y).mean()), "R@5": float((it & Y).sum() / Y.sum()),
                "unseen_R@5": float((it & un).sum() / max(un.sum(), 1))}
    return Sd, St, met(Sd, S.Ydev), met(St, S.Yte)


steps_per_epoch = math.ceil(N / BS)
opt = torch.optim.AdamW(enc_model.parameters(), lr=LR, weight_decay=0.01)
sched = get_linear_schedule_with_warmup(opt, int(0.1 * steps_per_epoch * EPOCHS), steps_per_epoch * EPOCHS)
state = {"epoch": 0, "best": -1.0, "best_ep": 0, "bad": 0, "hist": []}
ck = OUT / "ckpt_last.pt"
if ck.exists() and not A.bench:
    c = torch.load(ck, map_location="cpu", weights_only=False)
    enc_model.load_state_dict(c["model"]); opt.load_state_dict(c["opt"]); sched.load_state_dict(c["sched"])
    rng.bit_generator.state = c["rng"]; torch.set_rng_state(c["torch_rng"]); state = c["state"]
    print(f"resumed after epoch {state['epoch']}", flush=True)
print(f"[{BASE}] seed={A.seed} threads={torch.get_num_threads()} steps/epoch={steps_per_epoch}", flush=True)

done = False
for ep in range(state["epoch"] + 1, EPOCHS + 1):
    if state["bad"] >= PATIENCE: break
    enc_model.train(); perm = rng.permutation(N); tot = 0.0; t0 = time.time()
    for bi, b in enumerate(range(0, N, BS)):
        idx = perm[b:b + BS]
        gold_u = np.unique(np.concatenate([pos_lists[i] for i in idx]))
        cand = np.setdiff1d(pool, gold_u)
        negs = rng.choice(cand, size=min(N_NEG, len(cand)), replace=False)
        U = np.concatenate([gold_u, negs])
        et = emb([texts[i] for i in idx], T_LEN); eu = emb(LABEL_TEXTS[U].tolist(), L_TRAIN)
        Sc = (et @ eu.T) * SCALE
        pos = torch.tensor(Ytr[idx][:, U])
        neg_lse = torch.logsumexp(Sc.masked_fill(pos, -1e4), dim=1)
        rows = pos.nonzero()[:, 0]
        loss = F.softplus(neg_lse[rows] - Sc[pos]).mean()
        opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(enc_model.parameters(), 1.0)
        opt.step(); sched.step(); tot += loss.item() * len(idx)
        if A.bench and bi + 1 >= A.bench:
            dt = (time.time() - t0) / A.bench
            print(f"BENCH {dt:.1f} s/step -> {dt * steps_per_epoch / 60:.0f} min/epoch (+ eval)", flush=True); raise SystemExit
        if (bi + 1) % 20 == 0: print(f"  ep {ep} step {bi + 1}/{steps_per_epoch} loss {loss.item():.3f} {time.time() - t0:.0f}s", flush=True)
    Sd, St, md, mt = run_eval()
    state["hist"].append({"epoch": ep, "train_loss": tot / N, **{f"dev_{k}": v for k, v in md.items()}, "minutes": (time.time() - t0) / 60})
    print(f"epoch {ep:2d}: train_loss={tot / N:.4f} dev P@1={md['P@1']:.4f} MRR@3={md['MRR@3']:.4f} R@5={md['R@5']:.4f} | {(time.time() - t0) / 60:.0f} min", flush=True)
    if md["MRR@3"] > state["best"]:
        state.update(best=md["MRR@3"], best_ep=ep, bad=0)
        torch.save({"enc." + k: v for k, v in enc_model.state_dict().items()}, OUT / "matcher_state.pt")
        np.save(OUT / "dev_scores.npy", Sd); np.save(OUT / "test_scores.npy", St)
        json.dump({"model_name": BASE, "seed": A.seed, "best_epoch": ep, "dev": md, "test": mt, "history": state["hist"], "finished": False,
                   "config": dict(epochs=EPOCHS, patience=PATIENCE, batch_size=BS, lr=LR, n_neg=N_NEG, scale=SCALE, text_max_len=T_LEN,
                                  label_max_len_train=L_TRAIN, pooling="cls", neg_pool="all", device="cpu", precision="fp32")},
                  open(OUT / "metrics.json", "w"), indent=2)
        print(f"  new best (epoch {ep}); TEST P@1={mt['P@1']:.4f} MRR@3={mt['MRR@3']:.4f}; weights saved", flush=True)
    else:
        state["bad"] += 1
    state["epoch"] = ep
    torch.save({"model": enc_model.state_dict(), "opt": opt.state_dict(), "sched": sched.state_dict(), "rng": rng.bit_generator.state,
                "torch_rng": torch.get_rng_state(), "state": state}, ck)
    if state["bad"] >= PATIENCE:
        print(f"early stop (no dev improvement for {PATIENCE} epochs)", flush=True); break
m = json.load(open(OUT / "metrics.json")); m["finished"] = True; m["history"] = state["hist"]
json.dump(m, open(OUT / "metrics.json", "w"), indent=2)
print(f"FINISHED best epoch {m['best_epoch']} TEST {m['test']}", flush=True)
