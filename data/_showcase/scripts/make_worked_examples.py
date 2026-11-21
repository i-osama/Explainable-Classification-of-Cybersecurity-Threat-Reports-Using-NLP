"""E5: two worked examples for raters, from TRAIN sentences (never test). Local file only (contains dataset text).
Selection rule (fixed before running): walk TRAIN in numpy RandomState(42).permutation order; keep sentences with exactly one gold label,
8-16 words, and roberta_pw_s42 top-1 = gold with probability >= 0.9. Example A = 1st kept sentence with its 3 highest positive SHAP words
(a REAL item). Example B = 2nd kept sentence with 3 words drawn at random (RandomState(7)) outside its top-5 SHAP words (a CONTROL item).
SHAP: same method as the stored run (whitespace words, <mask>, permutation, 40 permutations, seed 42). Inference only, CPU."""
import json, re, sys
from pathlib import Path
import numpy as np, torch, shap
from transformers import AutoTokenizer, AutoModelForSequenceClassification
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap import CLS_DIR, SHOWCASE
from ttpmap.data import load_split, load_descriptions

torch.set_grad_enabled(False)
d = CLS_DIR / "roberta_pw_s42"; tok = AutoTokenizer.from_pretrained(str(d)); model = AutoModelForSequenceClassification.from_pretrained(str(d)).float().eval()
classes = [str(c).upper() for c in np.load(d / "mlb_classes.npy", allow_pickle=True)]
def logits(tx):
    enc = tok([str(t) for t in tx], truncation=True, max_length=128, padding=True, return_tensors="pt"); return model(**enc).logits.numpy()
tr = load_split("train"); UNIT = re.compile(r"(\s*)(\S+)(\s*)"); kept = []
for i in np.random.RandomState(42).permutation(len(tr)):
    t, ls = tr.text.iloc[i], tr.labels.iloc[i]
    if len(ls) != 1 or not 8 <= len(t.split()) <= 16: continue
    lg = logits([t])[0]; k = int(lg.argmax())
    if classes[k] == ls[0] and 1 / (1 + np.exp(-lg[k])) >= 0.9: kept.append((int(i), t, k))
    if len(kept) == 2: break
desc = dict(zip(load_descriptions().ttp, load_descriptions().description))
out = []
for n, (i, t, k) in enumerate(kept):
    parts = [m.groups() for m in UNIT.finditer(t)]; nw = len(parts)
    f = lambda M: logits(["".join(l + (w if kp else tok.mask_token) + r for (l, w, r), kp in zip(parts, row)) for row in (np.asarray(M) > 0.5)])[:, k]
    sv = shap.Explainer(f, shap.maskers.Independent(np.zeros((1, nw))), algorithm="permutation", seed=42)(np.ones((1, nw)), max_evals=40 * (2 * nw + 1), batch_size=64, silent=True)[0].values
    order = np.argsort(-sv, kind="stable")
    idx = order[:3].tolist() if n == 0 else np.random.RandomState(7).choice([j for j in range(nw) if j not in set(order[:5].tolist())], 3, replace=False).tolist()
    marked = "".join(l + (f"[[{w}]]" if j in idx else w) + r for j, (l, w, r) in enumerate(parts))
    out.append({"example": "A (real explanation)" if n == 0 else "B (random words, like a control item)", "train_row": i, "technique": classes[k], "description": desc.get(classes[k], "")[:300],
                "marked": marked, "shap_top5": [parts[j][1] for j in order[:5]]})
p = SHOWCASE / "human_study" / "materials_local"; p.mkdir(parents=True, exist_ok=True)
(p / "worked_examples_raw.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
for e in out: print(e["example"], "| row", e["train_row"], "|", e["technique"], "|", e["marked"], "| top5:", e["shap_top5"])
