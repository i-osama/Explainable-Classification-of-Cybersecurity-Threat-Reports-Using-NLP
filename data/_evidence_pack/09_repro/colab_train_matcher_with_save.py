"""NOT RUN. Colab (T4 GPU) cell that retrains the bge matcher exactly as Exp_2.1 CELL 7 but ALSO saves the weights,
which the original `train_matcher` never did. Needed for: full-fusion SHAP, 256-token re-evaluation, any later inference.

How to use: open Exp_2.1_matcher_.ipynb, run CELL 1-3 unchanged, then run this cell.
It writes to a NEW folder (run_match_2_saved) and never touches run_match_1.
Estimated runtime: about 20-30 min per seed on a T4 (the notebook's own estimate, CELL 0 table; seed 43 log shows 18 epochs).
On this PC's CPU (12 threads, no usable GPU) the same run was not attempted; expect many hours per seed.

Expected check: test P@1 close to run_match_1 (s42 0.756, s43 0.771, s44 0.741). GPU nondeterminism means the
scores will not be bit-identical, so report the retrained matcher's own numbers next to any SHAP result.
"""
OUT2 = "/content/drive/MyDrive/KDU/Thesis/run_match_2_saved"
os.makedirs(OUT2, exist_ok=True)

_orig_load = Matcher.load_state_dict
def train_and_save(seed):
    out = f"{OUT2}/ft20_s{seed}"
    if os.path.exists(f"{out}/matcher_state.pt"):
        print("skip", out); return
    holder = {}
    def spy(self, state, *a, **k):                      # train_matcher calls model.load_state_dict(best_state) once, at the end
        holder["state"] = {k_: v.clone() for k_, v in state.items()}
        return _orig_load(self, state, *a, **k)
    Matcher.load_state_dict = spy
    try:
        train_matcher(BASE_MODEL, out, seed=seed, epochs=20, patience=4, batch_size=16, lr=2e-5, n_neg=64, scale=30.0)
    finally:
        Matcher.load_state_dict = _orig_load
    torch.save(holder["state"], f"{out}/matcher_state.pt")      # keys start with "enc."
    print("saved", f"{out}/matcher_state.pt")

for sd in (42, 43, 44):
    train_and_save(sd)

# Then, on the PC (after copying run_match_2_saved\ft20_s42 next to the project):
#   python x1_fusion_shap.py --n 100 --seed 42 --matcher-dir "E:\Osamas Paper\run_match_2_saved\ft20_s42"
#   python x2_fusion_shap_summary.py --file 11_fusion_shap_full.jsonl
